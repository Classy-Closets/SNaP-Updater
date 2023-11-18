from os import path
import math
import time

import bpy
from bpy.types import Operator
from bpy.props import (
    StringProperty,
    EnumProperty,
    BoolProperty)

from snap import sn_types, sn_unit, sn_utils
from . import data_closet_splitters
from ..ops.drop_closet import PlaceClosetInsert
from .. import closet_props
from ..common import common_parts
from ..common import common_prompts
from ..common import common_lists


active_operator = None


def get_active_operator(context):
    global active_operator

    if active_operator:
        return active_operator


class Doors(sn_types.Assembly):

    type_assembly = "INSERT"
    id_prompt = "sn_closets.door_prompts"
    drop_id = "sn_closets.insert_doors_drop"
    placement_type = "EXTERIOR"
    show_in_library = True
    category_name = "Products - Basic"
    mirror_y = False

    door_type = ""  # {Base, Tall, Upper, Sink, Suspended}
    striker_depth = sn_unit.inch(3.4)
    striker_thickness = sn_unit.inch(0.75)
    shelf_thickness_ppt_obj = None

    shelves = []

    calculator = None
    calculator_name = "Opening Heights Calculator"
    calculator_obj_name = "Shelf Stack Calc Distance Obj"

    def __init__(self, obj_bp=None):
        super().__init__(obj_bp=obj_bp)
        self.shelves = []
        self.get_shelves()
        self.calculator = self.get_calculator(self.calculator_name)

    def get_shelves(self):
        for child in self.obj_bp.children:
            if child.get("IS_STACK_SHELF"):
                shelf = sn_types.Assembly(child)
                self.shelves.append(shelf)

    def add_common_doors_prompts(self):
        props = bpy.context.scene.sn_closets
        defaults = props.closet_defaults

        common_prompts.add_thickness_prompts(self)
        common_prompts.add_front_overlay_prompts(self)
        common_prompts.add_pull_prompts(self)
        common_prompts.add_door_prompts(self)
        common_prompts.add_door_pull_prompts(self)
        common_prompts.add_door_lock_prompts(self)

        if defaults.use_plant_on_top and self.door_type == 'Upper':
            door_height = sn_unit.millimeter(1184)
        else:
            door_height = sn_unit.millimeter(621.284)

        ppt_obj_shelves = self.add_prompt_obj("Shelves")
        self.add_prompt("Doors Backing Gap", 'DISTANCE', 0, prompt_obj=ppt_obj_shelves)
        glass_thickness = self.add_prompt("Glass Thickness", 'DISTANCE', sn_unit.inch(0.75), prompt_obj=ppt_obj_shelves)

        self.add_prompt("Fill Opening", 'CHECKBOX', False)
        self.add_prompt("Insert Height", 'DISTANCE', door_height)
        self.add_prompt("Offset For Plant On Top", 'CHECKBOX', defaults.use_plant_on_top)
        self.add_prompt("Add Striker", 'CHECKBOX', False)
        self.add_prompt("Striker Depth", 'DISTANCE', self.striker_depth)
        self.add_prompt("Striker Thickness", 'DISTANCE', self.striker_thickness)
        self.add_prompt("Use Mirror", 'CHECKBOX', False)

        self.add_prompt("Top KD", 'CHECKBOX', True)
        self.add_prompt("Bottom KD", 'CHECKBOX', True)
        self.add_prompt("Use Bottom KD Setback", 'CHECKBOX', False)
        self.add_prompt("Pard Has Top KD", 'CHECKBOX', False)
        self.add_prompt("Pard Has Bottom KD", 'CHECKBOX', False)
        self.add_prompt("Placed In Invalid Opening", 'CHECKBOX', False)

        self.add_prompt("Left Filler Amount", 'DISTANCE', 0)
        self.add_prompt("Right Filler Amount", 'DISTANCE', 0)
        self.add_prompt("Has Blind Left Corner", 'CHECKBOX', False)
        self.add_prompt("Has Blind Right Corner", 'CHECKBOX', False)
        self.add_prompt("Left Blind Corner Depth", 'DISTANCE', 0)
        self.add_prompt("Right Blind Corner Depth", 'DISTANCE', 0)

        self.add_prompt("Is Melamine Door", 'CHECKBOX', True)
        self.add_prompt("Has Center Rail", 'CHECKBOX', False)
        self.add_prompt("Center Rail Distance From Center", 'DISTANCE', 0)

        self.add_prompt("Full Overlay", 'CHECKBOX', False)
        self.add_prompt("Door Height Exceeded", 'CHECKBOX', False)

        # Shelves
        self.add_prompt("Shelf Thickness", 'DISTANCE', sn_unit.inch(0.75))
        self.add_prompt('Individual Shelf Setbacks', 'CHECKBOX', False)
        self.add_prompt("Adj Shelf Setback", 'DISTANCE', sn_unit.inch(0.25))
        self.add_prompt("Evenly Space Shelves", 'CHECKBOX', True)
        self.add_prompt("Thick Adjustable Shelves", 'CHECKBOX', defaults.thick_adjustable_shelves)
        self.add_prompt("Glass Shelves", 'CHECKBOX', False)
        self.add_prompt("Add Shelves", 'CHECKBOX', 0)
        self.add_prompt("Shelf Quantity", 'QUANTITY', 3)
        self.add_prompt("Shelf Backing Setback", 'DISTANCE', 0)
        self.add_prompt("Glass Shelf Thickness", 'COMBOBOX', 0, ['1/4"', '3/8"', '1/2"'])

        self.add_prompt("Left Large Hinge", 'CHECKBOX', False)
        self.add_prompt("Right Large Hinge", 'CHECKBOX', False)

        ST = self.get_prompt("Glass Shelf Thickness").get_var("ST")
        glass_thickness.set_formula('IF(ST==0,INCH(0.25),IF(ST==1,INCH(0.375),INCH(0.5)))', [ST])

        front_thickness = self.get_prompt('Front Thickness')
        front_thickness.set_value(sn_unit.inch(0.75))

    def set_door_drivers(self, assembly):
        Height = self.obj_z.snap.get_var('location.z', 'Height')
        Door_Gap = self.get_prompt("Door to Cabinet Gap").get_var('Door_Gap')
        Top_Thickness = self.get_prompt("Top Thickness").get_var('Top_Thickness')
        Bottom_Thickness = self.get_prompt("Bottom Thickness").get_var('Bottom_Thickness')
        Top_Overlay = self.get_prompt("Top Overlay").get_var('Top_Overlay')
        Bottom_Overlay = self.get_prompt("Bottom Overlay").get_var('Bottom_Overlay')
        # TODO: create issue - prompts "Extend Top Amount", "Extend Bottom Amount" do not exist
        # eta = self.get_prompt("Extend Top Amount").get_var('eta')
        # eba = self.get_prompt("Extend Bottom Amount").get_var('eba')
        Front_Thickness = self.get_prompt("Front Thickness").get_var('Front_Thickness')
        Insert_Height = self.get_prompt("Insert Height").get_var('Insert_Height')
        Fill_Opening = self.get_prompt("Fill Opening").get_var('Fill_Opening')
        Door_Type = self.get_prompt("Door Type").get_var('Door_Type')

        assembly.loc_y('-Door_Gap', [Door_Gap, Front_Thickness])
        assembly.loc_z(
            'IF(Door_Type==2,IF(Fill_Opening,0,Height-Insert_Height)-Bottom_Overlay,-Bottom_Overlay)',
            [Fill_Opening, Door_Type, Height, Insert_Height, Bottom_Thickness, Bottom_Overlay])
        assembly.rot_y(value=math.radians(-90))
        assembly.dim_x('IF(Fill_Opening,Height,Insert_Height)+Top_Overlay+Bottom_Overlay',
                       [Fill_Opening, Insert_Height, Height, Top_Overlay, Bottom_Overlay, Top_Thickness])
        assembly.dim_z('Front_Thickness', [Front_Thickness])

    def set_pull_drivers(self, assembly):
        self.set_door_drivers(assembly)

        Height = self.obj_z.snap.get_var('location.z', 'Height')
        Pull_Length = assembly.get_prompt("Pull Length").get_var('Pull_Length')
        Pull_From_Edge = self.get_prompt("Pull From Edge").get_var('Pull_From_Edge')
        Base_Pull_Location = self.get_prompt("Base Pull Location").get_var('Base_Pull_Location')
        Tall_Pull_Location = self.get_prompt("Tall Pull Location").get_var('Tall_Pull_Location')
        Upper_Pull_Location = self.get_prompt("Upper Pull Location").get_var('Upper_Pull_Location')

        World_Z = self.obj_bp.snap.get_var('matrix_world[2][3]', 'World_Z')

        Insert_Height = self.get_prompt("Insert Height").get_var('Insert_Height')
        Fill_Opening = self.get_prompt("Fill Opening").get_var('Fill_Opening')
        Door_Type = self.get_prompt("Door Type").get_var('Door_Type')

        pull_loc_x = assembly.get_prompt("Pull X Location")
        pull_loc_x.set_formula('Pull_From_Edge', [Pull_From_Edge])
        pull_loc_z = assembly.get_prompt("Pull Z Location")
        pull_loc_z.set_formula(
            'IF(Door_Type==0,Base_Pull_Location+(Pull_Length/2),'
            'IF(Door_Type==1,IF(Fill_Opening,Height,Insert_Height)-Tall_Pull_Location+(Pull_Length/2)+World_Z,'
            'IF(Fill_Opening,Height,Insert_Height)-Upper_Pull_Location-(Pull_Length/2)))',
            [Door_Type, Base_Pull_Location, Pull_Length, Fill_Opening, Insert_Height, Upper_Pull_Location,
             Tall_Pull_Location, World_Z, Height])

    def add_calculator(self, amt):
        Height = self.obj_z.snap.get_var('location.z', 'Height')
        Insert_Height = self.get_prompt("Insert Height").get_var('Insert_Height')
        Thickness = self.get_prompt('Shelf Thickness').get_var("Thickness")
        Fill_Opening = self.get_prompt("Fill Opening").get_var('Fill_Opening')

        calc_distance_obj = self.add_empty(self.calculator_obj_name)
        calc_distance_obj.empty_display_size = .001

        for coll in calc_distance_obj.users_collection:
            coll.objects.unlink(calc_distance_obj)

        for coll in self.obj_bp.users_collection:
            coll.objects.link(calc_distance_obj)

        self.calculator = self.obj_prompts.snap.add_calculator(self.calculator_name, calc_distance_obj)

        self.calculator.set_total_distance(
            "IF(Fill_Opening,Height,Insert_Height)-Thickness*{}".format(str(amt - 1)),
            [Height, Insert_Height, Fill_Opening, Thickness])

    def add_calculator_prompts(self, amt):
        self.calculator.prompts.clear()
        for i in range(1, amt + 1):
            calc_prompt = self.calculator.add_calculator_prompt("Opening " + str(i) + " Height")
            calc_prompt.equal = True

    def add_shelves(self, glass=False, amt=3):
        self.shelves = []
        Width = self.obj_x.snap.get_var('location.x', 'Width')
        Depth = self.obj_y.snap.get_var('location.y', 'Depth')
        Height = self.obj_z.snap.get_var('location.z', 'Height')
        Thickness = self.get_prompt("Shelf Thickness").get_var('Thickness')
        Shelf_Backing_Setback = self.get_prompt("Shelf Backing Setback").get_var('Shelf_Backing_Setback')
        Individual_Shelf_Setbacks = self.get_prompt("Individual Shelf Setbacks").get_var()
        Door_Type = self.get_prompt("Door Type").get_var()
        Insert_Height = self.get_prompt("Insert Height").get_var()
        Glass_Thickness = self.get_prompt("Glass Thickness").get_var('Glass_Thickness')

        TAS = self.get_prompt("Thick Adjustable Shelves").get_var('TAS')

        previous_shelf = None

        if not self.calculator:
            self.add_calculator(amt)

        self.add_calculator_prompts(amt)

        for i in range(1, amt):
            ppt_shelf_setback = self.get_prompt("Shelf " + str(i) + " Setback")
            if not ppt_shelf_setback:
                self.add_prompt("Shelf " + str(i) + " Setback", 'DISTANCE', sn_unit.inch(0.25))
            Shelf_Setback = self.get_prompt("Shelf " + str(i) + " Setback").get_var("Shelf_Setback")
            height_prompt = eval("self.calculator.get_calculator_prompt('Opening {} Height')".format(str(i)))
            opening_height = eval("height_prompt.get_var(self.calculator.name, 'opening_{}_height')".format(str(i)))

            if not glass:
                shelf = common_parts.add_shelf(self)
                IBEKD = shelf.get_prompt('Is Bottom Exposed KD').get_var('IBEKD')
                shelf.dim_z('IF(AND(TAS,IBEKD==False), INCH(1),Thickness)', [Thickness, TAS, IBEKD])
            else:
                shelf = common_parts.add_glass_shelf(self)
                shelf.dim_z('Glass_Thickness', [Glass_Thickness])

            shelf.obj_bp["IS_STACK_SHELF"] = True
            shelf.obj_bp.name = "Stack Shelf"
            self.shelves.append(shelf)
            if not glass:
                IBEKD = shelf.get_prompt('Is Bottom Exposed KD').get_var('IBEKD')
            Is_Locked_Shelf = shelf.get_prompt('Is Locked Shelf').get_var('Is_Locked_Shelf')
            Locked_Shelf_Setback = shelf.get_prompt('Locked Shelf Setback').get_var('Locked_Shelf_Setback')
            Adj_Shelf_Setback = shelf.get_prompt('Adj Shelf Setback').get_var('Adj_Shelf_Setback')
            Adj_Shelf_Clip_Gap = shelf.get_prompt('Adj Shelf Clip Gap').get_var('Adj_Shelf_Clip_Gap')
            Shelf_Setback_All = self.get_prompt("Adj Shelf Setback").get_var('Shelf_Setback_All')

            shelf.loc_x('IF(Is_Locked_Shelf,0,Adj_Shelf_Clip_Gap)', [Is_Locked_Shelf, Adj_Shelf_Clip_Gap])
            shelf.loc_y('Depth-Shelf_Backing_Setback', [Depth, Shelf_Backing_Setback])

            if previous_shelf:
                if i != amt:  # Not last Shelf
                    Previous_Z_Loc = previous_shelf.obj_bp.snap.get_var("location.z", "Previous_Z_Loc")
                    shelf.loc_z(
                        'Previous_Z_Loc-opening_{}_height-Thickness'.format(str(i)),
                        [Previous_Z_Loc, opening_height, Thickness])
            else:
                shelf.loc_z(
                    'IF(Door_Type==2,Height-opening_{}_height,Insert_Height-opening_{}_height)'.format(str(i), str(i)),
                    [Height, opening_height, Door_Type, Insert_Height])

            shelf.dim_x(
                'Width-IF(Is_Locked_Shelf,0,Adj_Shelf_Clip_Gap*2)',
                [Width, Is_Locked_Shelf, Adj_Shelf_Clip_Gap])
            shelf.dim_y(
                '-Depth+IF(Is_Locked_Shelf,Locked_Shelf_Setback,Adj_Shelf_Setback)+Shelf_Backing_Setback',
                [Depth, Locked_Shelf_Setback, Is_Locked_Shelf, Adj_Shelf_Setback, Shelf_Backing_Setback])
            if not glass:
                shelf.dim_z('IF(AND(TAS,IBEKD==False), INCH(1),Thickness) *-1', [Thickness, TAS, IBEKD])
            shelf.get_prompt("Adj Shelf Setback").set_formula(
                'IF(Individual_Shelf_Setbacks,Shelf_Setback,Shelf_Setback_All)',
                [Shelf_Setback, Shelf_Setback_All, Individual_Shelf_Setbacks])

            previous_shelf = shelf

        for shelf in self.shelves:
            sn_utils.update_obj_driver_expressions(shelf.obj_bp)

        self.update_collections()

    def add_glass_shelves(self):
        Width = self.obj_x.snap.get_var('location.x', 'Width')
        Height = self.obj_z.snap.get_var('location.z', 'Height')
        Depth = self.obj_y.snap.get_var('location.y', 'Depth')
        Shelf_Qty = self.get_prompt("Shelf Qty").get_var('Shelf_Qty')
        Glass_Thickness = self.get_prompt("Glass Thickness").get_var('Glass_Thickness')
        Insert_Height = self.get_prompt("Insert Height").get_var('Insert_Height')
        Fill_Opening = self.get_prompt("Fill Opening").get_var('Fill_Opening')
        Door_Type = self.get_prompt("Door Type").get_var('Door_Type')
        Glass_Shelves = self.get_prompt("Glass Shelves").get_var('Glass_Shelves')

        glass_shelf = common_parts.add_glass_shelf(self)
        glass_shelf.draw_as_hidden_line()
        glass_shelf.loc_x(value=0)
        glass_shelf.loc_y('Depth',[Depth])
        glass_shelf.loc_z('IF(Fill_Opening,((Height-(Glass_Thickness*Shelf_Qty))/(Shelf_Qty+1)),IF(Door_Type==2,Height-Insert_Height,0)+((Insert_Height-(Glass_Thickness*Shelf_Qty))/(Shelf_Qty+1)))',
                        [Fill_Opening,Height,Glass_Thickness,Shelf_Qty,Insert_Height,Door_Type])
        glass_shelf.dim_x('Width',[Width])
        glass_shelf.dim_y('-Depth+.00635',[Depth])
        glass_shelf.dim_z('Glass_Thickness',[Glass_Thickness])

        hide = glass_shelf.get_prompt('Hide')
        hide.set_formula('IF(Glass_Shelves==False,True,IF(Shelf_Qty==0,True,False))',[Shelf_Qty,Glass_Shelves])
        z_qty = glass_shelf.get_prompt('Z Quantity')
        z_qty.set_formula('Shelf_Qty', [Shelf_Qty])

        z_offset = glass_shelf.get_prompt('Z Offset')
        z_offset.set_formula('IF(Fill_Opening,((Height-(Glass_Thickness*Shelf_Qty))/(Shelf_Qty+1))+Glass_Thickness,((Insert_Height-(Glass_Thickness*Shelf_Qty))/(Shelf_Qty+1))+Glass_Thickness)',
                         [Fill_Opening,Height,Glass_Thickness,Shelf_Qty,Insert_Height])

    def update(self):
        super().update()

        self.obj_bp["IS_BP_DOOR_INSERT"] = True
        self.obj_bp.snap.export_as_subassembly = True

        props = self.obj_bp.sn_closets
        props.is_door_insert_bp = True  # TODO: remove

        self.set_prompts()

    def draw(self):
        self.create_assembly()
        self.add_common_doors_prompts()

        Width = self.obj_x.snap.get_var('location.x', 'Width')
        Depth = self.obj_y.snap.get_var('location.y', 'Depth')
        Height = self.obj_z.snap.get_var('location.z', 'Height')
        LO = self.get_prompt("Left Overlay").get_var('LO')
        RO = self.get_prompt("Right Overlay").get_var('RO')
        Vertical_Gap = self.get_prompt("Vertical Gap").get_var('Vertical_Gap')
        Rotation = self.get_prompt("Door Rotation").get_var('Rotation')
        Open = self.get_prompt("Open").get_var('Open')
        double_door = self.get_prompt("Force Double Doors").get_var('double_door')
        DD = self.get_prompt("Force Double Doors").get_var('DD')
        left_swing = self.get_prompt("Use Left Swing").get_var('left_swing')
        ST = self.get_prompt("Shelf Thickness").get_var( 'ST')
        Insert_Height = self.get_prompt("Insert Height").get_var('Insert_Height')
        Fill_Opening = self.get_prompt("Fill Opening").get_var('Fill_Opening')
        DDAS = self.get_prompt("Double Door Auto Switch").get_var( 'DDAS')
        No_Pulls = self.get_prompt("No Pulls").get_var('No_Pulls')
        Lock_Door = self.get_prompt("Lock Door").get_var('Lock_Door')
        Lock_to_Panel = self.get_prompt("Lock to Panel").get_var('Lock_to_Panel')
        dt = self.get_prompt("Division Thickness").get_var('dt')
        ddl_offset = self.get_prompt("Double Door Lock Offset").get_var('ddl_offset')
        Front_Thickness = self.get_prompt("Front Thickness").get_var('Front_Thickness')
        Door_Gap = self.get_prompt("Door to Cabinet Gap").get_var('Door_Gap')
        Door_Type = self.get_prompt("Door Type").get_var('Door_Type')
        Offset_For_Plant_On_Top = self.get_prompt("Offset For Plant On Top").get_var('Offset_For_Plant_On_Top')
        Add_Striker = self.get_prompt("Add Striker").get_var('Add_Striker')
        Striker_Depth = self.get_prompt("Striker Depth").get_var('Striker_Depth')
        Striker_Thickness = self.get_prompt("Striker Thickness").get_var('Striker_Thickness')
        Glass_Shelves = self.get_prompt("Glass Shelves").get_var('Glass_Shelves')
        Shelf_Backing_Setback = self.get_prompt("Shelf Backing Setback").get_var('Shelf_Backing_Setback')
        Use_Bottom_KD_Setback = self.get_prompt("Use Bottom KD Setback").get_var()

        FO = self.get_prompt("Full Overlay").get_var('FO')
        DDHOD = self.get_prompt("Double Door Half Overlay Difference").get_var('DDHOD')
        DDFOD = self.get_prompt("Double Door Full Overlay Difference").get_var('DDFOD')
        SDFOD = self.get_prompt("Single Door Full Overlay Difference").get_var('SDFOD')

        Top_KD = self.get_prompt("Top KD").get_var('Top_KD')
        Bottom_KD = self.get_prompt("Bottom KD").get_var('Bottom_KD')
        Pard_Has_Top_KD = self.get_prompt("Pard Has Top KD").get_var('Pard_Has_Top_KD')
        Pard_Has_Bottom_KD = self.get_prompt("Pard Has Bottom KD").get_var('Pard_Has_Bottom_KD')
        Placed_In_Invalid_Opening = self.get_prompt("Placed In Invalid Opening").get_var('Placed_In_Invalid_Opening')
        Full_Overlay = self.get_prompt("Full Overlay").get_var('Full_Overlay')
        DDHOD = self.get_prompt("Double Door Half Overlay Difference").get_var('DDHOD')
        DDFOD = self.get_prompt("Double Door Full Overlay Difference").get_var('DDFOD')
        SDFOD = self.get_prompt("Single Door Full Overlay Difference").get_var('SDFOD')

        LF = self.get_prompt("Left Filler Amount").get_var('LF')
        RF = self.get_prompt("Right Filler Amount").get_var('RF')

        BLC = self.get_prompt("Has Blind Left Corner").get_var('BLC')
        BRC = self.get_prompt("Has Blind Right Corner").get_var('BRC')
        LD = self.get_prompt("Left Blind Corner Depth").get_var('LD')
        RD = self.get_prompt("Right Blind Corner Depth").get_var('RD')

        TAS = self.get_prompt("Thick Adjustable Shelves").get_var('TAS')

        Left_Large_Hinge = self.get_prompt("Left Large Hinge").get_var('Left_Large_Hinge')
        Right_Large_Hinge = self.get_prompt("Right Large Hinge").get_var('Right_Large_Hinge')

        door_backing_gap = self.get_prompt('Doors Backing Gap')
        door_backing_gap.set_formula('Insert_Height+ST*2', [Insert_Height, ST])  

        sq = self.get_prompt("Shelf Quantity").get_var('sq')

        # STRIKER
        striker = common_parts.add_door_striker(self)
        striker.loc_y('Striker_Depth', [Striker_Depth])
        striker.loc_z('Height+Striker_Thickness', [Height, Striker_Thickness])
        striker.rot_x(value=math.radians(180))
        striker.dim_x('Width', [Width])
        striker.dim_y('Striker_Depth', [Striker_Depth])
        striker.dim_z('ST', [ST])
        hide = striker.get_prompt('Hide')
        hide.set_formula('IF(Add_Striker,False,True)',[Add_Striker])

        # TODO: glass shelves
        # self.add_glass_shelves()

        left_door = common_parts.add_door(self)
        left_door.set_name("Left Door")
        self.set_door_drivers(left_door)
        left_door.loc_x('IF(BLC,LD-ST/4-INCH(0.375)-LF,IF(FO,-LO*2,-LO))', [LO, FO, BLC, BLC, ST, LD, Width, LF])
        left_door.rot_z('radians(90)-Open*Rotation', [Open, Rotation])
        left_door.dim_y(
            'IF(OR(BLC,BRC),IF(OR(DD,Width-IF(BLC,LD-LF,RD-RF)+ST>DDAS),(Width-IF(BLC,LD-LF,RD-RF)+ST)/2,(Width-IF(BLC,LD-LF,RD-RF)+ST)+ST/6),IF(OR(DD,Width>DDAS),IF(FO,(Width+(ST*2)-DDFOD)/2,(Width+LO+RO)/2-DDHOD),IF(FO,Width+(ST*2)-SDFOD,Width+LO+RO)))*-1',
            [DDHOD, DDFOD, SDFOD, DD, DDAS, Width, LO, RO, Vertical_Gap, FO, ST, BLC, BRC, LD, RD, LF, RF])
        hide = left_door.get_prompt('Hide')
        hide.set_formula(
            'IF(OR(BLC,BRC),IF(OR(double_door,Width-IF(BLC,LD-LF,RD-RF)+ST>DDAS,left_swing),False,True),IF(OR(double_door,Width>DDAS,left_swing),False,True))', 
            [double_door, DDAS, left_swing, Width, BLC, BRC, LD, RD, ST, LF, RF])
        door_type = left_door.get_prompt('Door Type')
        door_type.set_formula('Door_Type', [Door_Type])
        door_swing = left_door.get_prompt('Door Swing')
        door_swing.set_value(0)
        no_pulls = left_door.get_prompt('No Pulls')
        no_pulls.set_formula('No_Pulls', [No_Pulls])
        cat_num = left_door.get_prompt('CatNum')
        cat_num.set_formula('IF(OR(double_door,Width>DDAS),51,52)', [double_door, Width, DDAS])
        large_hinge = left_door.get_prompt('Large Hinge')
        large_hinge.set_formula('IF(BLC,False,Left_Large_Hinge)', [Left_Large_Hinge, BLC])

        left_pull = common_parts.add_door_pull(self)
        self.set_pull_drivers(left_pull)
        left_pull.loc_x('IF(BLC,LD-ST/4-INCH(0.375)-LF,-LO)',[LO,BLC,Width,LD,ST,BRC,RD,double_door,DDAS, LF])
        left_pull.rot_z('IF(BLC,radians(90)-Open*Rotation,radians(90)-Open*Rotation)', [Open, Rotation, BLC])
        left_pull.dim_y(
            'IF(OR(BLC,BRC),IF(OR(double_door,Width-IF(BLC,LD-LF,RD-RF)+ST>DDAS),((Width-IF(BLC,LD-LF,RD-RF))/2),(Width-(IF(BLC,LD-LF,RD-RF)))),IF(OR(double_door,Width>DDAS),(Width+LO+RO-Vertical_Gap)/2,(Width+LO+RO)))*-1',
            [double_door, DDAS, Width, LO, RO, Vertical_Gap, ST, BLC, BRC, LD, RD, LF, RF])
        hide = left_pull.get_prompt('Hide')
        hide.set_formula(
            'IF(No_Pulls,True,IF(OR(BLC,BRC),IF(OR(double_door,Width-IF(BLC,LD-LF,RD-RF)+ST>DDAS,left_swing),False,True),IF(OR(double_door,Width>DDAS,left_swing),False,True)))', 
            [No_Pulls, double_door, DDAS, left_swing, Width, BLC, BRC, LD, RD, ST, LF, RF])

        right_door = common_parts.add_door(self)
        right_door.set_name("Right Door")
        self.set_door_drivers(right_door)
        right_door.loc_x('IF(BRC,Width-RD+ST/4+INCH(0.375)+RF,IF(FO, Width+(RO*2), Width+RO))',[Width,RO,FO,BLC,BRC,RD,ST, RF])
        right_door.rot_z('radians(90)+Open*Rotation', [Open, Rotation])
        right_door.dim_y('IF(OR(BLC,BRC),IF(OR(DD,Width-IF(BLC,LD-LF,RD-RF)+ST>DDAS),(Width-IF(BLC,LD-LF,RD-RF)+ST)/2,(Width-IF(BLC,LD-LF,RD-RF)+ST)+ST/6),IF(OR(DD,Width>DDAS), IF(FO,(Width+(ST*2)-DDFOD)/2,(Width+LO+RO)/2-DDHOD) ,IF(FO,Width+(ST*2)-SDFOD,Width+LO+RO)))',[DDHOD,DDFOD,SDFOD,DD,DDAS,Width,LO,RO,Vertical_Gap,FO,ST,BLC,BRC,LD,RD,LF,RF])
        hide = right_door.get_prompt('Hide')
        hide.set_formula(
            'IF(OR(BLC,BRC),IF(OR(double_door,Width-IF(BLC,LD-LF,RD-RF)+ST>DDAS),False,IF(left_swing,True,False)),IF(OR(double_door,Width>DDAS),False,IF(left_swing,True,False)))', 
            [double_door,DDAS,Width,BLC,BRC,LD,RD,ST,left_swing,LF,RF])
        door_type = right_door.get_prompt('Door Type')
        door_type.set_formula('Door_Type',[Door_Type])
        door_swing = right_door.get_prompt('Door Swing')
        door_swing.set_value(1)
        no_pulls = right_door.get_prompt('No Pulls')
        no_pulls.set_formula('No_Pulls', [No_Pulls])
        cat_num = right_door.get_prompt('CatNum')
        cat_num.set_formula('IF(OR(double_door,Width>DDAS),51,52)', [double_door, Width, DDAS])
        large_hinge = right_door.get_prompt('Large Hinge')
        large_hinge.set_formula('IF(BRC,False,Right_Large_Hinge)', [Right_Large_Hinge, BRC])

        right_pull = common_parts.add_door_pull(self)
        self.set_pull_drivers(right_pull)
        right_pull.loc_x('IF(BRC,Width-RD+ST/4+INCH(0.375)+RF,Width+RO)',[RO,BLC,Width,RD,ST,BRC,double_door,DDAS,RF])
        right_pull.rot_z('radians(90)+Open*Rotation', [Open, Rotation])
        right_pull.dim_y(
            'IF(OR(BLC,BRC),IF(OR(double_door,Width-IF(BLC,LD-LF,RD-RF)+ST>DDAS),((Width-IF(BLC,LD-LF,RD-RF))/2),(Width-IF(BLC,LD-LF,RD-RF))),IF(OR(double_door,Width>DDAS),(Width+LO+RO-Vertical_Gap)/2,(Width+LO+RO)))',
            [double_door, DDAS, Width, LO, RO, Vertical_Gap, ST, BLC, BRC, LD, RD, LF, RF])
        hide = right_pull.get_prompt('Hide')
        hide.set_formula('IF(No_Pulls,True,IF(OR(BLC,BRC),IF(OR(double_door,Width-IF(BLC,LD-LF,RD-RF)+ST>DDAS,left_swing==False),False,True),IF(OR(double_door,Width>DDAS,left_swing==False),False,True)))', 
                          [No_Pulls, double_door, DDAS, left_swing, Width, BLC, BRC, LD, RD, ST, LF, RF])
        
        #BOTTOM KD SHELF
        bottom_shelf = common_parts.add_shelf(self)
        IBEKD = bottom_shelf.get_prompt('Is Bottom Exposed KD').get_var('IBEKD')
        bottom_shelf.loc_x('Width',[Width])
        bottom_shelf.loc_y(
            'Depth-IF(Use_Bottom_KD_Setback,Shelf_Backing_Setback,0)',
            [Depth, Shelf_Backing_Setback, Use_Bottom_KD_Setback])
        bottom_shelf.loc_z('IF(Fill_Opening, 0, IF(Door_Type==2,Height-Insert_Height,0))', 
                    [Door_Type,Insert_Height,Height,ST,Fill_Opening])
        bottom_shelf.rot_z(value=math.radians(180))
        bottom_shelf.dim_x('Width',[Width])
        bottom_shelf.dim_y(
            'Depth-IF(Use_Bottom_KD_Setback,Shelf_Backing_Setback,0)',
            [Depth, Shelf_Backing_Setback, Use_Bottom_KD_Setback])
        # bottom_shelf.dim_z('IF(AND(TAS,IBEKD==False), INCH(1),ST) *-1', [ST, TAS, IBEKD])
        bottom_shelf.dim_z('-ST', [ST, TAS, IBEKD])
        hide = bottom_shelf.get_prompt('Hide')
        hide.set_formula(
            "IF(Placed_In_Invalid_Opening,IF(Door_Type!=2,True,IF(Bottom_KD, False, True)),IF(OR(AND(Pard_Has_Bottom_KD,Door_Type!=2),AND(Pard_Has_Bottom_KD,Fill_Opening)), True, IF(Bottom_KD, False, True)))", 
            [Bottom_KD,Pard_Has_Bottom_KD,Door_Type,Fill_Opening,Placed_In_Invalid_Opening])
        is_locked_shelf = bottom_shelf.get_prompt('Is Locked Shelf')
        is_locked_shelf.set_value(True)
        bottom_shelf.get_prompt("Is Forced Locked Shelf").set_value(value=True)

        #TOP KD SHELF
        top_shelf = common_parts.add_shelf(self)
        IBEKD = top_shelf.get_prompt('Is Bottom Exposed KD').get_var('IBEKD')
        top_shelf.loc_x('Width',[Width])
        top_shelf.loc_y('Depth',[Depth])
        top_shelf.loc_z('IF(Fill_Opening, Height + ST,IF(Door_Type==2,Height + ST,Insert_Height + ST))',
                    [Door_Type,Insert_Height,Height,ST, Fill_Opening])
        top_shelf.rot_z(value=math.radians(180))
        top_shelf.dim_x('Width',[Width])
        top_shelf.dim_y('Depth-Shelf_Backing_Setback',[Depth,Shelf_Backing_Setback])
        # top_shelf.dim_z('IF(AND(TAS,IBEKD==False), INCH(1),ST) *-1', [ST, TAS, IBEKD])
        top_shelf.dim_z('-ST', [ST, TAS, IBEKD])
        hide = top_shelf.get_prompt('Hide')
        hide.set_formula("IF(Placed_In_Invalid_Opening,IF(Door_Type==2,True,IF(Top_KD, False, True)),IF(OR(AND(Pard_Has_Top_KD,Door_Type==2),AND(Pard_Has_Top_KD,Fill_Opening)), True, IF(Top_KD, False, True)))", [Top_KD, Pard_Has_Top_KD,Door_Type,Fill_Opening,Placed_In_Invalid_Opening])
        is_locked_shelf = top_shelf.get_prompt('Is Locked Shelf')
        is_locked_shelf.set_value(True)
        top_shelf.get_prompt("Is Forced Locked Shelf").set_value(value=True)
        
        opening = common_parts.add_opening(self)
        opening.loc_z('IF(Fill_Opening,0,IF(Door_Type==2,0,Insert_Height+ST))', [Door_Type, Insert_Height, ST, Fill_Opening])
        opening.dim_x('Width', [Width])
        opening.dim_y('Depth', [Depth])
        opening.dim_z('IF(Fill_Opening,Insert_Height,Height-Insert_Height-ST)', [Fill_Opening, Height, Insert_Height, ST])

        # LOCK
        door_lock = common_parts.add_lock(self)
        wall_bp = sn_utils.get_wall_bp(door_lock.obj_bp)
        if wall_bp:
            wall_coll = bpy.data.collections[wall_bp.snap.name_object]
            scene_coll = bpy.context.scene.collection
            sn_utils.add_assembly_to_collection(door_lock, wall_coll)
            sn_utils.remove_assembly_from_collection(door_lock, scene_coll)      

        door_lock.loc_x('IF(OR(double_door,Width>DDAS),Width/2+ddl_offset,IF(left_swing,Width+IF(Lock_to_Panel,dt,-dt),IF(Lock_to_Panel,-dt,dt)))',
                        [Lock_to_Panel,left_swing,Width,double_door,dt,DDAS,ddl_offset])
        door_lock.loc_y('IF(OR(double_door,Width>DDAS),-Front_Thickness-Door_Gap,IF(Lock_to_Panel,Front_Thickness,-Front_Thickness-Door_Gap))',
                        [Lock_to_Panel,Door_Gap,Front_Thickness,dt,DDAS,double_door,Width])
        door_lock.rot_y('IF(OR(double_door,Width>DDAS),radians(90),IF(AND(left_swing,Lock_to_Panel==False),radians(180),0))',
                        [left_swing,double_door,Width,Lock_to_Panel,DDAS])
        door_lock.rot_z('IF(OR(double_door,Width>DDAS),0,IF(Lock_to_Panel==False,0,IF(left_swing,radians(90),radians(-90))))',
                        [Lock_to_Panel,left_swing,double_door,DDAS,Width])
        base_lock_z_location_formula = "IF(Fill_Opening,Height,Insert_Height)-INCH(1.5)"
        tall_lock_z_location_formula = "IF(Fill_Opening,Height/2,Insert_Height/2)-INCH(1.5)"
        upper_lock_z_location_formula = "IF(Fill_Opening,0,Height-Insert_Height)+INCH(1.5)"
        door_lock.loc_z('IF(Door_Type==0,' + base_lock_z_location_formula + ',IF(Door_Type==1,' + tall_lock_z_location_formula + ',' + upper_lock_z_location_formula + '))',
                        [Door_Type,Fill_Opening,Insert_Height,Height])
        hide = door_lock.get_prompt('Hide')
        hide.set_formula('IF(Lock_Door==True,IF(Open>0,IF(Lock_to_Panel,False,True),False),True)',  [Lock_Door, Open, Lock_to_Panel])
        door_lock.material('Chrome')        
        
        self.update()

    def update_collections(self):
        wall_bp = sn_utils.get_wall_bp(self.obj_bp)
        floor = sn_utils.get_floor_parent(self.obj_bp)

        for i, shelf in enumerate(self.shelves):
            if wall_bp:
                wall_coll = bpy.data.collections[wall_bp.snap.name_object]
                self.asssign_to_collection(shelf.obj_bp, wall_coll)

            if floor:
                floor_coll = bpy.data.collections[floor.snap.name_object]
                self.asssign_to_collection(shelf.obj_bp, floor_coll)

    def asssign_to_collection(self, obj_bp, collection):
        scene_coll = bpy.context.scene.collection
        sn_utils.add_assembly_to_collection(obj_bp, collection)
        sn_utils.remove_assembly_from_collection(obj_bp, scene_coll)


def update_door_type(self, context):
    """Door Type - Base, Tall, Upper"""
    op = get_active_operator(context)
    if op:
        if op.initialized:
            ppt_door_type = op.assembly.get_prompt("Door Type")

            if ppt_door_type:
                ppt_door_type.set_value(int(op.door_type))


def update_use_shelves(self, context):
    """Add/remove shelves"""
    op = get_active_operator(context)
    if op:
        if op.initialized:
            add_shelves = op.assembly.get_prompt("Add Shelves")
            if add_shelves:
                add_shelves.set_value(op.use_shelves)
            op.run_calculators(op.assembly.obj_bp)


def update_shelf_quantity(self, context):
    """Update shelf quantity"""
    op = get_active_operator(context)
    if op:
        if op.initialized:
            shelf_quantity = op.assembly.get_prompt("Shelf Quantity")
            if shelf_quantity:
                shelf_quantity.set_value(int(self.shelf_quantity))


# TODO: Glass shelf thickness
def update_shelf_glass_thickness(self, context):
    """Glass shelf thickness"""
    op = get_active_operator(context)
    if op:
        if op.initialized:
            ppt_glass_thickness = op.assembly.get_prompt("Glass Shelf Thickness")
            if ppt_glass_thickness:
                ppt_glass_thickness.set_value(int(self.glass_thickness))


def update_kd_shelves(self, context):
    """Glass shelf thickness"""
    op = get_active_operator(context)
    if op:
        if op.initialized:
            ppt_glass_thickness = self.assembly.get_prompt("Glass Shelf Thickness")
            if ppt_glass_thickness:
                ppt_glass_thickness.set_value(int(self.glass_thickness))


def update_user_glass_shelves(self, context):
    """Toggles shelf material between glass and melamine"""
    op = get_active_operator(context)
    if op:
        if op.initialized:
            bpy.ops.snap.update_scene_from_pointers()


class PROMPTS_Door_Prompts(sn_types.Prompts_Interface):
    bl_idname = "sn_closets.door_prompts"
    bl_label = "Door Prompt"
    bl_description = "This shows all of the available door options"
    bl_options = {'UNDO'}

    object_name: StringProperty(name="Object Name")

    tabs: EnumProperty(
        name="Tabs",
        items=[
            ('DOOR', 'Door Options', 'Options for the door'),
            ('SHELVES', 'Shelf Options', 'Options for the shelves')],
        default='DOOR')

    door_type: EnumProperty(
        name="Door Type",
        items=[
            ('0', 'Base', 'Base'),
            ('1', 'Tall', 'Tall'),
            ('2', 'Upper', 'Upper')],
        default='2',
        update=update_door_type)

    use_glass_shelves: BoolProperty(name="Use Glass Shelves", default=False, update=update_user_glass_shelves)

    def update_fill_opening(self, context):
        op = get_active_operator(context)
        if op:
            if op.initialized:
                if not op.fill_opening:
                    # Set back to default
                    insert_height = op.assembly.get_prompt("Insert Height")
                    insert_height.distance_value = sn_unit.millimeter(621.284)
                    op.door_opening_height = str(621.284)

                fill_opening = op.assembly.get_prompt("Fill Opening")
                fill_opening.set_value(op.fill_opening)
                op.check_door_size(context)
                op.update_door_opening_height(context)
                op.run_calculators(op.assembly.obj_bp)

    fill_opening: BoolProperty(name="Fill Opening", default=False, update=update_fill_opening)

    glass_thickness: EnumProperty(
        name="Glass Thickness",
        items=[
            ('0', '1/4"', '1/4"'),
            ('1', '3/8"', '3/8"')],
        default='0',
        update=update_shelf_glass_thickness)

    glass_thickness_prompt = None
    shelf_thickness_prompt = None

    assembly = None
    part = None

    shelf_quantity: EnumProperty(
        name="Shelf Quantity",
        items=[(str(i), str(i), str(i)) for i in range(1, 16)],
        default='3',
        update=update_shelf_quantity
    )

    plant_on_top_opening_height: EnumProperty(name="Height", items=common_lists.PLANT_ON_TOP_OPENING_HEIGHTS)

    def update_door_opening_height(self, context):
        op = get_active_operator(context)
        if op:
            if op.initialized:
                fill_opening = op.assembly.get_prompt("Fill Opening")
                insert_height = op.assembly.get_prompt("Insert Height")
                offset_for_plant_on_top = op.assembly.get_prompt("Offset For Plant On Top")
                ppt_door_type = op.assembly.get_prompt("Door Type")

                if ppt_door_type:
                    ppt_door_type.set_value(int(op.door_type))
                    door_type_name = ppt_door_type.combobox_items[ppt_door_type.get_value()].name

                if insert_height:
                    if door_type_name == 'Upper' and offset_for_plant_on_top.get_value():
                        insert_height.distance_value = sn_unit.inch(float(op.plant_on_top_opening_height) / 25.4)
                    else:
                        if fill_opening:
                            if fill_opening.get_value():
                                insert_height.distance_value = op.assembly.obj_z.location.z
                            else:
                                insert_height.distance_value = sn_unit.inch(float(op.door_opening_height) / 25.4)
                        else:
                            insert_height.distance_value = sn_unit.inch(float(op.door_opening_height) / 25.4)

                op.check_door_size(context)
                op.run_calculators(op.assembly.obj_bp)

    door_opening_height: EnumProperty(
        name="Height",
        items=common_lists.OPENING_HEIGHTS,
        update=update_door_opening_height)

    use_shelves: BoolProperty(name="Use Shelves", default=False, update=update_use_shelves)
    door_height_exceeded: BoolProperty(name="Door Height Exceeded", default=False)

    shelf_quantity_prompt = None
    door_type_prompt = None
    cur_shelf_height = None

    def update_striker(self, context):
        """Disable top KD shelf if door striker is being used"""
        op = get_active_operator(context)

        if op:
            if op.initialized:
                add_striker_ppt = op.assembly.get_prompt("Add Striker")
                top_kd_ppt = op.assembly.get_prompt("Top KD")
                add_striker_ppt.set_value(op.add_striker)

                if add_striker_ppt:
                    if add_striker_ppt.get_value():
                        top_kd_ppt.set_value(False)
                    else:
                        top_kd_ppt.set_value(True)

                op.update_kd_shelves()

    add_striker: BoolProperty(name="Add Striker", default=False, update=update_striker)
    door_style = ""

    initialized = False

    @classmethod
    def poll(cls, context):
        return True

    def delete_shelves(self):
        for assembly in self.assembly.shelves:
            sn_utils.delete_object_and_children(assembly.obj_bp)
        self.assembly.shelves.clear()

    def add_shelves(self):
        if self.use_glass_shelves:
            self.assembly.add_shelves(glass=True, amt=int(self.shelf_quantity))
        else:
            self.assembly.add_shelves(amt=int(self.shelf_quantity))

        self.assembly.update()

        self.calculators = []
        heights_calc = self.assembly.get_calculator('Opening Heights Calculator')
        if heights_calc:
            self.calculators.append(heights_calc)
        self.run_calculators(self.assembly.obj_bp)

        bpy.ops.object.select_all(action='DESELECT')

    def update_shelves(self, context):
        shelf_amt_changed = len(self.assembly.shelves) != int(self.shelf_quantity) - 1
        shelf_type_changed = False

        if self.assembly.shelves:
            shelf_bp = self.assembly.shelves[0].obj_bp
            shelf_is_glass = shelf_bp.get("IS_GLASS_SHELF")

            if not shelf_is_glass and self.use_glass_shelves:
                shelf_type_changed = True
            elif shelf_is_glass and not self.use_glass_shelves:
                shelf_type_changed = True

        if self.use_shelves:
            if not self.assembly.shelves:
                self.add_shelves()
            else:
                if shelf_amt_changed or shelf_type_changed:
                    self.delete_shelves()
                    self.add_shelves()
        else:
            if self.assembly.shelves:
                self.delete_shelves()

        context.view_layer.objects.active = self.assembly.obj_bp

    def update_kd_shelves(self):
        fill_opening = self.assembly.get_prompt("Fill Opening").get_value()
        top_pard_KD = self.assembly.get_prompt("Pard Has Top KD")
        top_KD = self.assembly.get_prompt("Top KD")
        bottom_pard_KD = self.assembly.get_prompt("Pard Has Bottom KD")
        bottom_KD = self.assembly.get_prompt("Bottom KD")

        kd_prompts = [
            top_pard_KD,
            bottom_pard_KD,
            top_KD,
            bottom_KD
        ]

        closet_obj = None
        closet_assembly = None

        ppt_door_type = self.assembly.get_prompt("Door Type")
        temp_door_type_num = 0

        if ppt_door_type:
            temp_door_type_num = ppt_door_type.get_value()
            door_type_name = ppt_door_type.combobox_items[ppt_door_type.get_value()].name

        closet_obj = sn_utils.get_closet_bp(self.assembly.obj_bp)
        if "IS_BP_CLOSET" in closet_obj:
            closet_assembly = sn_types.Assembly(closet_obj)

        if all(kd_prompts):
            if closet_assembly:
                opening_name = self.assembly.obj_bp.sn_closets.opening_name
                if closet_assembly.get_prompt("Remove Top Shelf " + opening_name):
                    does_opening_have_top_KD = closet_assembly.get_prompt("Remove Top Shelf " + opening_name)
                    does_opening_have_bottom_KD = closet_assembly.get_prompt("Remove Bottom Hanging Shelf " + opening_name)

                    if fill_opening:
                        if top_KD.get_value():
                            does_opening_have_top_KD.set_value(True)
                            top_pard_KD.set_value(True)
                        else:
                            does_opening_have_top_KD.set_value(False)
                            top_pard_KD.set_value(False)

                        if bottom_KD.get_value():
                            does_opening_have_bottom_KD.set_value(True)
                            bottom_pard_KD.set_value(True)
                        else:
                            does_opening_have_bottom_KD.set_value(False)
                            bottom_pard_KD.set_value(False)
                    else:
                        if door_type_name == 'Upper':
                            if top_KD.get_value():
                                does_opening_have_top_KD.set_value(True)
                                top_pard_KD.set_value(True)
                            else:
                                does_opening_have_top_KD.set_value(False)
                                top_pard_KD.set_value(False)
                        elif temp_door_type_num == 2:
                            does_opening_have_top_KD.set_value(False)
                            top_pard_KD.set_value(False)
                        else:
                            if bottom_KD.get_value():
                                does_opening_have_bottom_KD.set_value(True)
                                bottom_pard_KD.set_value(True)
                            else:
                                does_opening_have_bottom_KD.set_value(False)
                                bottom_pard_KD.set_value(False)
            else:
                placed_in_invalid_opening = self.assembly.get_prompt("Placed In Invalid Opening")
                placed_in_invalid_opening.set_value(True)

                if fill_opening:
                    top_KD.set_value(False)
                    bottom_KD.set_value(False)
                elif door_type_name == 'Upper':
                    top_KD.set_value(False)
                else:
                    bottom_KD.set_value(False)

    def set_prompts_from_properties(self):
        ''' This should be called in the check function to set the prompts
            to the same values as the class properties
        '''

        self.update_kd_shelves()

        for child in self.assembly.obj_bp.children:
            if 'IS_DOOR' in child:
                if not child.visible_get:
                    door_assembly = sn_types.Assembly(child)
                    door_style = door_assembly.get_prompt("Door Style")
                    is_melamine_door = self.assembly.get_prompt("Is Melamine Door")
                    has_center_rail = self.assembly.get_prompt("Has Center Rail")
                    prompts = [door_style, is_melamine_door, has_center_rail]

                    if all(prompts):
                        if door_style.get_value() == "Slab Door" or "Traviso" in (door_style.get_value()):
                            is_melamine_door.set_value(True)
                            has_center_rail.set_value(False)
                        else:
                            is_melamine_door.set_value(False)

    def set_properties_from_prompts(self):
        insert_height = self.assembly.get_prompt("Insert Height")
        door_type = self.assembly.get_prompt("Door Type")
        offset_for_plant_on_top = self.assembly.get_prompt("Offset For Plant On Top")
        self.glass_thickness_prompt = self.assembly.get_prompt("Glass Shelf Thickness")
        add_shelves = self.assembly.get_prompt("Add Shelves")
        shelf_quantity = self.assembly.get_prompt("Shelf Quantity")

        if add_shelves and shelf_quantity:
            self.use_shelves = add_shelves.get_value()
            self.shelf_quantity = str(shelf_quantity.get_value())

        if door_type:
            self.door_type_prompt = door_type
            self.door_type = str(self.door_type_prompt.combobox_index)
            door_type_name = self.door_type_prompt.combobox_items[self.door_type_prompt.get_value()].name

        if self.glass_thickness_prompt:
            self.glass_thickness = str(self.glass_thickness_prompt.combobox_index)

        if insert_height:
            value = round(insert_height.distance_value * 1000, 3)
            if door_type_name == 'Upper' and offset_for_plant_on_top.get_value():
                for index, height in enumerate(common_lists.PLANT_ON_TOP_OPENING_HEIGHTS):
                    if not value >= float(height[0]):
                        self.plant_on_top_opening_height = common_lists.PLANT_ON_TOP_OPENING_HEIGHTS[index - 1][0]
                        break
            else:
                for index, height in enumerate(common_lists.OPENING_HEIGHTS):
                    if not value >= float(height[0]):
                        self.door_opening_height = common_lists.OPENING_HEIGHTS[index - 1][0]
                        break

    def closest_hole_amt(self, opening_heights, height):
        return opening_heights[min(range(len(opening_heights)), key=lambda i: abs(opening_heights[i] - height))]

    def update_opening_heights(self):
        for i in range(1, int(self.shelf_quantity) + 1):
            opening_height = self.assembly.get_prompt("Opening " + str(i) + " Height")
            if opening_height:
                if not opening_height.equal:
                    op_heights = [float(height[0]) for height in data_closet_splitters.get_opening_heights()]
                    height = opening_height.get_value()
                    closest_hole_amt = self.closest_hole_amt(op_heights, sn_unit.meter_to_millimeter(height))
                    opening_height.set_value(sn_unit.millimeter(closest_hole_amt))

    def check_door_size(self, context):
        # Check Traviso door size is not too large

        for obj in self.assembly.obj_bp.children:
            if obj.get("IS_DOOR"):
                door_assy = sn_types.Assembly(obj)
                door_style = door_assy.get_prompt("Door Style")

                if door_style and ("Traviso" in (door_style.get_value())):
                    constraint = [c for c in door_assy.obj_x.constraints if c.type == 'LIMIT_LOCATION']

                    if constraint:
                        constraint = constraint[0]
                        context.view_layer.update()
                        self.door_height_exceeded = door_assy.obj_x.location.x > constraint.max_x
                        height_exceeded_ppt = self.assembly.get_prompt("Door Height Exceeded")

                        if not height_exceeded_ppt:
                            height_exceeded_ppt = self.assembly.add_prompt("Door Height Exceeded", 'CHECKBOX', False)

                        height_exceeded_ppt.set_value(self.door_height_exceeded)

                        if self.door_height_exceeded:
                            self.assembly.get_prompt("Fill Opening").set_value(False)
                            self.assembly.get_prompt("Insert Height").set_value(sn_unit.millimeter(1485.392))
                            for index, height in enumerate(common_lists.OPENING_HEIGHTS):
                                if not 1485.392 >= float(height[0]):
                                    self.door_opening_height = common_lists.OPENING_HEIGHTS[index - 1][0]
                                    break

    def check(self, context):
        start_time = time.perf_counter()

        # self.check_door_size(context)
        # self.update_top_kd_shelf()
        self.set_prompts_from_properties()
        self.update_shelves(context)
        self.update_opening_heights()
        # self.run_calculators(self.assembly.obj_bp)
        # self.run_calculators(self.assembly.obj_bp)

        # TODO: Do mirrored doors need to be fixed?
        # self.assign_mirror_material(self.assembly.obj_bp)
        # closet_props.update_render_materials(self, context)
        # bpy.ops.snap.update_scene_from_pointers()

        self.assembly.obj_bp.location = self.assembly.obj_bp.location  # Redraw Viewport

        print("{} : Check Time --- {} seconds ---".format(
            self.bl_idname,
            round(time.perf_counter() - start_time, 8)))

        return True

    # TODO: Do mirrored doors need to be fixed?
    # def assign_mirror_material(self, obj):
        # use_mirror = self.assembly.get_prompt("Use Mirror")

        # if use_mirror.get_value():
        #     if obj.snap.type_mesh == 'BUYOUT':
        #         for mat_slot in obj.snap.material_slots:
        #             if "Glass" in mat_slot.name:
        #                 mat_slot.pointer_name = 'Mirror'
        # else:
        #     if obj.snap.type_mesh == 'BUYOUT':
        #         for mat_slot in obj.snap.material_slots:
        #             if "Glass" in mat_slot.name:
        #                 mat_slot.pointer_name = 'Glass'

        # for child in obj.children:
        #     self.assign_mirror_material(child)

    def execute(self, context):
        self.tabs = 'DOOR'
        return {'FINISHED'}

    def reset_variables(self):
        self.active_operator = None
        self.assembly = None
        self.part = None
        self.door_type_prompt = None
        self.initialized = False
        self.calculators = []
        self.door_height_exceeded = False
        global active_operator
        active_operator = self

    def invoke(self, context, event):
        start_time = time.perf_counter()
        self.reset_variables()
        obj = context.object
        obj_bp = self.get_insert().obj_bp
        self.assembly = Doors(obj_bp)
        obj_assembly_bp = sn_utils.get_assembly_bp(obj)
        self.part = sn_types.Assembly(obj_assembly_bp)
        self.set_properties_from_prompts()

        closet_obj = None
        closet_assembly = None
        heights_calc = self.assembly.get_calculator('Opening Heights Calculator')
        add_striker_ppt = self.assembly.get_prompt("Add Striker")
        fill_opening = self.assembly.get_prompt("Fill Opening").get_value()
        top_pard_KD = self.assembly.get_prompt("Pard Has Top KD")
        top_KD = self.assembly.get_prompt("Top KD")
        bottom_pard_KD = self.assembly.get_prompt("Pard Has Bottom KD")
        bottom_KD = self.assembly.get_prompt("Bottom KD")

        if not obj_bp.get("SNAP_VERSION"):
            print("Found old lib data!")
            return bpy.ops.sn_closets.door_prompts_214('INVOKE_DEFAULT')

        if heights_calc:
            self.calculators.append(heights_calc)

        if add_striker_ppt:
            self.add_striker = add_striker_ppt.get_value()

        if self.assembly.shelves:
            shelf_bp = self.assembly.shelves[0].obj_bp
            shelf_is_glass = shelf_bp.get("IS_GLASS_SHELF")
            if shelf_is_glass:
                self.use_glass_shelves = True
            else:
                self.use_glass_shelves = False

        self.fill_opening = fill_opening

        door_type_name = self.door_type_prompt.combobox_items[self.door_type_prompt.get_value()].name
        closet_obj = sn_utils.get_closet_bp(self.assembly.obj_bp)

        if "IS_BP_CLOSET" in closet_obj:
            closet_assembly = sn_types.Assembly(closet_obj)

        placed_in_invalid_opening = self.assembly.get_prompt("Placed In Invalid Opening")

        if closet_assembly:
            Blind_Corner_Left = closet_assembly.get_prompt("Blind Corner Left")
            Blind_Corner_Right = closet_assembly.get_prompt("Blind Corner Right")
            Blind_Left_Depth = closet_assembly.get_prompt("Blind Left Depth")
            Blind_Right_Depth = closet_assembly.get_prompt("Blind Right Depth")
            Has_Blind_Left_Corner = self.assembly.get_prompt("Has Blind Left Corner")
            Has_Blind_Right_Corner = self.assembly.get_prompt("Has Blind Right Corner")
            Left_Blind_Corner_Depth = self.assembly.get_prompt("Left Blind Corner Depth")
            Right_Blind_Corner_Depth = self.assembly.get_prompt("Right Blind Corner Depth")

            kd_prompts = [
                top_pard_KD,
                bottom_pard_KD,
                top_KD,
                bottom_KD]

            bcp_prompts = [
                Blind_Corner_Left,
                Blind_Corner_Right,
                Blind_Left_Depth,
                Blind_Right_Depth,
                Has_Blind_Left_Corner,
                Has_Blind_Right_Corner,
                Left_Blind_Corner_Depth,
                Right_Blind_Corner_Depth]

            if all(kd_prompts):
                opening_name = self.assembly.obj_bp.sn_closets.opening_name
                remove_top_shelf_ppt = closet_assembly.get_prompt("Remove Top Shelf " + opening_name)
                remove_bottom_shelf_ppt = closet_assembly.get_prompt("Remove Bottom Hanging Shelf " + opening_name)

                if remove_top_shelf_ppt:
                    does_opening_have_top_KD = remove_top_shelf_ppt.get_value()
                    does_opening_have_bottom_KD = remove_bottom_shelf_ppt.get_value()

                    if fill_opening:
                        top_pard_KD.set_value(does_opening_have_top_KD)
                        top_KD.set_value(does_opening_have_top_KD)
                        bottom_pard_KD.set_value(does_opening_have_bottom_KD)
                        bottom_KD.set_value(does_opening_have_bottom_KD)
                    else:
                        if door_type_name == 'Upper':
                            top_pard_KD.set_value(does_opening_have_top_KD)
                            top_KD.set_value(does_opening_have_top_KD)
                        else:
                            bottom_pard_KD.set_value(does_opening_have_bottom_KD)
                            bottom_KD.set_value(does_opening_have_bottom_KD)

            if closet_assembly.get_prompt("Opening 1 Height"):
                opening_quantity = 0
                for i in range(1, 10):
                    parent_assy = sn_types.Assembly(self.assembly.obj_bp.parent)
                    opening_height_ppt = parent_assy.get_prompt("Opening " + str(i) + " Height")

                    if opening_height_ppt is None:
                        opening_quantity = i - 1
                        break

                if all(bcp_prompts):
                    if opening_quantity == 1:
                        if Blind_Corner_Left:
                            Has_Blind_Right_Corner.set_value(False)

                        elif Blind_Corner_Right:
                            Has_Blind_Right_Corner.set_value(True)
                            Has_Blind_Left_Corner.set_value(False)

                        else:
                            Has_Blind_Right_Corner.set_value(False)
                            Has_Blind_Left_Corner.set_value(False)

                    elif opening_name == '1':
                        if Blind_Corner_Left:
                            Has_Blind_Left_Corner.set_value(True)
                        else:
                            Has_Blind_Left_Corner.set_value(False)

                    elif opening_name == str(opening_quantity):
                        if Blind_Corner_Right:
                            Has_Blind_Right_Corner.set_value(True)
                        else:
                            Has_Blind_Right_Corner.set_value(False)

                    else:
                        Has_Blind_Left_Corner.set_value(False)
                        Has_Blind_Right_Corner.set_value(False)
                    Left_Blind_Corner_Depth.set_value(Blind_Left_Depth.get_value())
                    Right_Blind_Corner_Depth.set_value(Blind_Right_Depth.get_value())

        else:
            placed_in_invalid_opening.set_value(True)
            Has_Blind_Left_Corner = self.assembly.get_prompt("Has Blind Left Corner")
            Has_Blind_Right_Corner = self.assembly.get_prompt("Has Blind Right Corner")
            Left_Blind_Corner_Depth = self.assembly.get_prompt("Left Blind Corner Depth")
            Right_Blind_Corner_Depth = self.assembly.get_prompt("Right Blind Corner Depth")

            if fill_opening:
                top_KD.set_value(False)
                bottom_KD.set_value(False)
            elif door_type_name == 'Upper':
                top_KD.set_value(False)
            else:
                bottom_KD.set_value(False)

            Has_Blind_Left_Corner.set_value(False)
            Has_Blind_Right_Corner.set_value(False)

        for child in self.assembly.obj_bp.children:
            if 'IS_DOOR' in child:
                if not child.visible_get():
                    door_assembly = sn_types.Assembly(child)
                    door_style = door_assembly.get_prompt("Door Style")

                    if door_style:
                        self.door_style = door_style.get_value()

                    is_melamine_door = self.assembly.get_prompt("Is Melamine Door")
                    has_center_rail = self.assembly.get_prompt("Has Center Rail")
                    prompts = [door_style, is_melamine_door, has_center_rail]

                    if all(prompts):
                        if door_style.get_value() == "Slab Door" or "Traviso" in door_style.get_value():
                            is_melamine_door.set_value(True)
                            has_center_rail.set_value(False)
                        else:
                            is_melamine_door.set_value(False)

        self.initialized = True

        print("{} {}: Check Time --- {} seconds ---".format(
            self.bl_idname, "invoke",
            round(time.perf_counter() - start_time, 8)))

        return super().invoke(context, event, width=375)

    # TODO: Do mirrored doors need to be fixed?
    # def is_glass_door(self):
    #     if self.part:
    #         if "Glass" in self.part.obj_bp.snap.comment:
    #             return True
    #         else:
    #             return False
    #     else:
    #         return False

    def get_number_of_equal_heights(self):
        calculator = self.assembly.get_calculator('Opening Heights Calculator')
        shelf_qty = self.assembly.get_prompt("Shelf Quantity").get_value()
        number_of_equal_heights = 0

        for i in range(1, shelf_qty + 1):
            height = eval("calculator.get_calculator_prompt('Opening {} Height')".format(str(i)))

            if height:
                number_of_equal_heights += 1 if height.equal else 0
            else:
                break

        return number_of_equal_heights

    def draw_height_row(self, layout, height, i):
        opening_heights = data_closet_splitters.get_opening_heights()
        row = layout.row()
        row.label(text="Opening " + str(i+1) + ":")
        if not height.equal:
            row.prop(height, 'equal', text="")
        else:
            if self.get_number_of_equal_heights() != 1:
                row.prop(height, 'equal', text="")
            else:
                row.label(text="", icon='BLANK1')
        if height.equal:
            row.label(text=str(round(sn_unit.meter_to_active_unit(height.distance_value), 2)) + '"')
        else:
            label = ""
            for opening_height in opening_heights:
                if float(opening_height[0]) == round(sn_unit.meter_to_millimeter(height.distance_value), 1):
                    label = opening_height[1]
            row.menu("SNAP_MT_Opening_{}_Heights".format(str(i+1)), text=label)        

    def draw_opening_heights(self, layout):
        calculator = self.assembly.get_calculator('Opening Heights Calculator')
        idv_shelf_setbacks = self.assembly.get_prompt("Individual Shelf Setbacks")
        
        col = layout.column(align=True)
        box = col.box()
        box.label(text="Opening Heights:")

        for i, shelf in enumerate(self.assembly.shelves):
            height = eval("calculator.get_calculator_prompt('Opening {} Height')".format(str(i+1)))
            setback = self.assembly.get_prompt("Shelf " + str(i+1) + " Setback")
            is_locked_shelf = self.assembly.shelves[i].get_prompt("Is Locked Shelf")

            if height:
                self.draw_height_row(box, height, i)

            if setback and idv_shelf_setbacks and is_locked_shelf:
                if idv_shelf_setbacks.get_value() and not is_locked_shelf.get_value():
                    row = box.row()
                    row.label(text="Shelf " + str(i+1) + " Setback")
                    row.prop(setback, 'distance_value', text="")

            if i == len(self.assembly.shelves) - 1:
                height = eval("calculator.get_calculator_prompt('Opening {} Height')".format(str(i+2)))
                if height:
                    self.draw_height_row(box, height, i+1)

    def draw(self, context):
        super().draw(context)
        layout = self.layout

        if self.assembly.obj_bp:
            if self.assembly.obj_bp.name in context.scene.objects:
                props = bpy.context.scene.sn_closets
                door_type = self.assembly.get_prompt("Door Type")
                open_prompt = self.assembly.get_prompt("Open")
                pull_type = self.assembly.get_prompt('Pull Location')
                use_left_swing = self.assembly.get_prompt('Use Left Swing')
                force_double_door = self.assembly.get_prompt('Force Double Doors')
                force_double_door = self.assembly.get_prompt('Force Double Doors')
                lock_door = self.assembly.get_prompt('Lock Door')
                lock_to_panel = self.assembly.get_prompt('Lock to Panel')
                insert_height = self.assembly.get_prompt("Insert Height")
                no_pulls = self.assembly.get_prompt("No Pulls")
                shelf_qty = self.assembly.get_prompt("Shelf Qty")
                offset_for_plant_on_top = self.assembly.get_prompt("Offset For Plant On Top")
                # add_striker = self.assembly.get_prompt("Add Striker")
                # TODO: Do mirrored doors need to be fixed?
                # use_mirror = self.assembly.get_prompt("Use Mirror")
                glass_shelves = self.assembly.get_prompt("Glass Shelves")
                full_overlay = self.assembly.get_prompt("Full Overlay")
                top_KD = self.assembly.get_prompt("Top KD")
                bottom_KD = self.assembly.get_prompt("Bottom KD")
                placed_in_invalid_opening = self.assembly.get_prompt("Placed In Invalid Opening")
                is_melamine_door = self.assembly.get_prompt("Is Melamine Door")
                has_center_rail = self.assembly.get_prompt("Has Center Rail")
                center_rail_distance_from_center = self.assembly.get_prompt("Center Rail Distance From Center")
                shelf_quantity = self.assembly.get_prompt("Shelf Quantity")
                add_shelves = self.assembly.get_prompt("Add Shelves")
                has_blind_left_corner = self.assembly.get_prompt("Has Blind Left Corner")                
                has_blind_right_corner = self.assembly.get_prompt("Has Blind Right Corner")
                left_large_hinge = self.assembly.get_prompt("Left Large Hinge")
                right_large_hinge = self.assembly.get_prompt("Right Large Hinge")

                door_type_name = door_type.combobox_items[door_type.get_value()].name

                box = layout.box()
                row = box.row()
                if add_shelves:
                    row.prop(self,'tabs',expand=True)

                if self.tabs == 'DOOR':
                    box.label(text="Opening Options:")
                    # box.prop(add_striker, "checkbox_value", text=add_striker.name)
                    box.prop(self, "add_striker", text="Add Striker")
                    row = box.row()
                    row.label(text="Fill Opening")
                    row.prop(self, 'fill_opening', text="")

                    if not self.fill_opening:
                        row = box.row()
                        if props.closet_defaults.use_32mm_system:
                            row.label(text="Opening Height:")
                            row = box.row()
                            if door_type_name == 'Upper' and offset_for_plant_on_top.get_value():
                                row.prop(self, 'plant_on_top_opening_height', text="")
                            else:
                                row.prop(self, 'door_opening_height', text="")
                        else:
                            insert_height.draw_prompt(row)
                            row.prop(insert_height, "distance_value", text=insert_height.name)

                    if self.door_height_exceeded:
                        box = box.box()
                        row = box.row()
                        row.label(text="Traviso door style not permitted in sizes above 47H!", icon='ERROR')

                    row = box.row()
                    if shelf_qty:
                        row.prop(shelf_qty, "quantity_value", text=shelf_qty.name)

                    box = layout.box()
                    box.label(text="Door Options:")
                    if door_type:
                        row = box.row()
                        row.prop(self, "door_type", expand=True)
                        row = box.row()

                        if door_type_name == 'Base':
                            pull_location = self.assembly.get_prompt('Base Pull Location')
                            row.label(text=pull_location.name)
                            row.prop(pull_location, "distance_value", text="")
                        if door_type_name == 'Tall':
                            pull_location = self.assembly.get_prompt('Tall Pull Location')
                            row.label(text=pull_location.name)
                            row.prop(pull_location, "distance_value", text="")
                        if door_type_name == 'Upper':
                            pull_location = self.assembly.get_prompt('Upper Pull Location')
                            row.label(text=pull_location.name)
                            row.prop(pull_location, "distance_value", text="")              

                    row = box.row()
                    row.label(text="Open Door")
                    row.prop(open_prompt, 'factor_value', slider=True, text="")

                    if has_center_rail and is_melamine_door and center_rail_distance_from_center:
                        if not is_melamine_door.get_value():
                            row = box.row()
                            row.label(text="Center Rail")
                            row.prop(has_center_rail, 'checkbox_value', text="")
                            if has_center_rail.get_value():
                                row = box.row()
                                row.label(text="Distance From Center")
                                row.prop(center_rail_distance_from_center, 'distance_value', text="")

                    if top_KD and bottom_KD:
                        if placed_in_invalid_opening and placed_in_invalid_opening.get_value() == False:
                            row = box.row()
                            row.label(text="Top KD")
                            row.prop(top_KD, 'checkbox_value', text="")
                            row = box.row()
                            row.label(text="Bottom KD")
                            row.prop(bottom_KD, 'checkbox_value', text="")
                        else:
                            if not self.fill_opening:
                                if door_type_name == 'Upper':
                                    row = box.row()
                                    row.label(text="Top KD")
                                    row.prop(top_KD, 'checkbox_value', text="")
                                    row = box.row()
                                    row.label(text="Bottom KD")
                                    row.prop(bottom_KD, 'checkbox_value', text="")
                                else:
                                    row = box.row()
                                    row.label(text="Top KD")
                                    row.prop(top_KD, 'checkbox_value', text="")

                        row = box.row()
                        row.label(text="Force Double Door")
                        row.prop(force_double_door, 'checkbox_value', text="")
                        row = box.row()
                        row.label(text="Left Swing")
                        row.prop(use_left_swing, 'checkbox_value', text="")
                        row = box.row()
                        row.label(text="No Pulls")
                        row.prop(no_pulls, 'checkbox_value', text="")
                        row = box.row()
                        row.label(text="Lock Door")
                        row.prop(lock_door, 'checkbox_value', text="")

                        locked_door = lock_door.get_value()
                        not_force_double_door = force_double_door.get_value() == False
                        less_than_24_inches = self.assembly.obj_x.location.x < sn_unit.inch(24)

                        if locked_door and not_force_double_door and less_than_24_inches:
                            row = box.row()
                            row.label(text="Lock to Panel")
                            row.prop(lock_to_panel, 'checkbox_value', text="")

                        if full_overlay:
                            row = box.row()
                            row.label(text="Full Overlay")
                            row.prop(full_overlay,'checkbox_value',text="")

                        # TODO: Do mirrored doors need to be fixed?
                        # if self.is_glass_door():
                        #     row = box.row()
                        #     use_mirror.draw_prompt(row)

                    prompts = [force_double_door, has_blind_left_corner, has_blind_right_corner, left_large_hinge, right_large_hinge, use_left_swing]
                    if all(prompts):
                        if force_double_door.get_value():
                            hinge_box = box.box()
                            hinge_box.label(text="Hinge Options:")
                            if not has_blind_left_corner.get_value():
                                row = hinge_box.row()
                                row.label(text="165 Hinge Left")
                                row.prop(left_large_hinge, 'checkbox_value', text="")
                            if not has_blind_right_corner.get_value():
                                row = hinge_box.row()
                                row.label(text="165 Hinge Right")
                                row.prop(right_large_hinge, 'checkbox_value', text="")
                        else:
                            if not has_blind_left_corner.get_value() and use_left_swing.get_value():
                                hinge_box = box.box()
                                hinge_box.label(text="Hinge Options:")
                                row = hinge_box.row()
                                row.label(text="165 Hinge Left")
                                row.prop(left_large_hinge, 'checkbox_value', text="")
                            if not has_blind_right_corner.get_value() and not use_left_swing.get_value():
                                hinge_box = box.box()
                                hinge_box.label(text="Hinge Options:")
                                row = hinge_box.row()
                                row.label(text="165 Hinge Right")
                                row.prop(right_large_hinge, 'checkbox_value', text="")

                elif self.tabs == 'SHELVES':
                    adj_shelf_setback = self.assembly.get_prompt("Adj Shelf Setback")
                    shelf_quantity = self.assembly.get_prompt("Shelf Quantity")
                    idv_shelf_setbacks = self.assembly.get_prompt("Individual Shelf Setbacks")

                    row = box.row()
                    row.label(text="Add Shelves")
                    row.prop(self, 'use_shelves', text="")
                    if add_shelves:
                        if add_shelves.get_value():
                            if shelf_quantity:
                                col = box.column(align=True)
                                row = col.row()
                                row.label(text="Qty:")
                                row.prop(self, "shelf_quantity", expand=True)
                                col.separator()

                            if adj_shelf_setback:
                                col = box.column(align=True)
                                row = col.row()
                                adj_shelf_setback.draw(row, allow_edit=False)

                            if idv_shelf_setbacks:
                                col = box.column(align=True)
                                row = col.row()
                                idv_shelf_setbacks.draw(row, allow_edit=False)

                            if glass_shelves:
                                row = box.row()
                                row.label(text="Glass Shelves: ")
                                row.prop(self, "use_glass_shelves", text="")

                                if self.use_glass_shelves and self.glass_thickness_prompt:
                                    row = box.row()
                                    row.label(text="Glass Shelf Thickness: ")
                                    row.prop(self, "glass_thickness", expand=True)

                            self.draw_opening_heights(box)


class OPS_Doors_Drop(Operator, PlaceClosetInsert):
    bl_idname = "sn_closets.insert_doors_drop"
    bl_label = "Custom drag and drop for doors insert"
    adjacent_cant_be_deeper = True

    def execute(self, context):
        return super().execute(context)    

    def confirm_placement(self, context):
        super().confirm_placement(context)

        self.set_backing_top_gap(self.insert.obj_bp, self.selected_opening)
        context.view_layer.objects.active = self.insert.obj_bp
        closet_obj = None
        closet_assembly = None
        opening_width = None

        closet_obj = sn_utils.get_closet_bp(self.insert.obj_bp)
        if "IS_BP_CLOSET" in closet_obj:
            closet_assembly = sn_types.Assembly(closet_obj)

        if closet_assembly:
            width = closet_assembly.get_prompt("Opening " + self.insert.obj_bp.sn_closets.opening_name + " Width")
            if(width):
                opening_width = width.distance_value

            if(closet_assembly.get_prompt("Remove Top Shelf " + self.insert.obj_bp.sn_closets.opening_name)):
                self.insert.get_prompt("Pard Has Top KD").set_value(closet_assembly.get_prompt("Remove Top Shelf " + self.insert.obj_bp.sn_closets.opening_name).get_value())
                self.insert.get_prompt("Pard Has Bottom KD").set_value(closet_assembly.get_prompt("Remove Bottom Hanging Shelf " + self.insert.obj_bp.sn_closets.opening_name).get_value())
                if(self.insert.get_prompt("Pard Has Top KD").get_value() is False and self.insert.get_prompt("Door Type").get_value() == 2):
                    self.insert.get_prompt("Pard Has Top KD").set_value(True)
                    closet_assembly.get_prompt("Remove Top Shelf " + self.insert.obj_bp.sn_closets.opening_name).set_value(True)
            if(closet_assembly.get_prompt("Opening 1 Height")):
                opening_quantity = 0
                left_depth = 0
                right_depth = 0
                if(closet_assembly.get_prompt("Blind Corner Left Depth") and closet_assembly.get_prompt("Blind Corner Right Depth")):
                    left_depth = closet_assembly.get_prompt("Blind Corner Left Depth").get_value()
                    right_depth = closet_assembly.get_prompt("Blind Corner Right Depth").get_value()
                    for i in range(1, 10):
                        if(closet_assembly.get_prompt("Opening " + str(i) + " Height") is None):
                            opening_quantity = (i - 1)
                            break
                    if(opening_quantity == 1):
                        if(closet_assembly.get_prompt("Blind Corner Left").get_value()):
                            self.insert.get_prompt("Has Blind Left Corner").set_value(True)
                            self.insert.get_prompt("Use Left Swing").set_value(True)
                            opening_width = opening_width - left_depth + sn_unit.inch(0.75)
                        if(closet_assembly.get_prompt("Blind Corner Right").get_value()):
                            self.insert.get_prompt("Has Blind Right Corner").set_value(True)
                            opening_width = opening_width - right_depth + sn_unit.inch(0.75)
                    elif(self.insert.obj_bp.sn_closets.opening_name == '1'):
                        if(closet_assembly.get_prompt("Blind Corner Left").get_value()):
                            self.insert.get_prompt("Has Blind Left Corner").set_value(True)
                            self.insert.get_prompt("Use Left Swing").set_value(True)
                            opening_width = opening_width - left_depth + sn_unit.inch(0.75)
                    elif(self.insert.obj_bp.sn_closets.opening_name == str(opening_quantity)):
                        if(closet_assembly.get_prompt("Blind Corner Right").get_value()):
                            self.insert.get_prompt("Has Blind Right Corner").set_value(True)
                            opening_width = opening_width - right_depth + sn_unit.inch(0.75)
                    else:
                        self.insert.get_prompt("Has Blind Left Corner").set_value(False)
                        self.insert.get_prompt("Has Blind Right Corner").set_value(False)

                    self.insert.get_prompt("Left Blind Corner Depth").set_value(left_depth)
                    self.insert.get_prompt("Right Blind Corner Depth").set_value(right_depth)

                closet_left_filler = closet_assembly.get_prompt("Left Side Wall Filler")
                insert_left_filler = self.insert.get_prompt("Left Filler Amount")
                closet_right_filler = closet_assembly.get_prompt("Right Side Wall Filler")
                insert_right_filler = self.insert.get_prompt("Right Filler Amount")
                prompts = [closet_left_filler, insert_left_filler, closet_right_filler, insert_right_filler]
                if all(prompts):
                    CLF = closet_left_filler.get_var('CLF')
                    insert_left_filler.set_formula("CLF", [CLF])
                    CRF = closet_right_filler.get_var('CRF')
                    insert_right_filler.set_formula("CRF", [CRF])

            if(opening_width and opening_width >= sn_unit.inch(21)): 
                force_double_door = self.insert.get_prompt("Force Double Doors")
                if(force_double_door):
                    force_double_door.set_value(True)
        else:
            placed_in_invalid_opening = self.insert.get_prompt("Placed In Invalid Opening")
            placed_in_invalid_opening.set_value(True)
            self.insert.get_prompt("Has Blind Left Corner").set_value(False)
            self.insert.get_prompt("Has Blind Right Corner").set_value(False)
            self.insert.get_prompt("Left Blind Corner Depth").set_value(0)
            self.insert.get_prompt("Right Blind Corner Depth").set_value(0)

        self.selected_opening.obj_bp.snap.interior_open = False

        # TOP LEVEL PRODUCT RECAL
        sn_utils.run_calculators(sn_utils.get_closet_bp(self.insert.obj_bp))
        sn_utils.run_calculators(sn_utils.get_closet_bp(self.insert.obj_bp))

    def set_backing_top_gap(self, insert_bp, selected_opening):
        opening_name = selected_opening.obj_bp.sn_closets.opening_name
        carcass_bp = sn_utils.get_closet_bp(insert_bp)
        doors_assembly = sn_types.Assembly(insert_bp)
        Doors_Backing_Gap = doors_assembly.get_prompt('Doors Backing Gap').get_var()

        if "IS_BP_ISLAND" in carcass_bp:
            return

        for child in carcass_bp.children:
            if child.sn_closets.is_back_bp:
                if child.sn_closets.opening_name == opening_name:
                    back_assembly = sn_types.Assembly(child)
                    top_insert_backing = back_assembly.get_prompt('Top Insert Backing')
                    top_ppt = back_assembly.get_prompt("Top Section Backing")
                    center_ppt = back_assembly.get_prompt("Center Section Backing")
                    bottom_ppt = back_assembly.get_prompt("Bottom Section Backing")
                    single_back_ppt = back_assembly.get_prompt("Single Back")
                    use_center = center_ppt.get_value()
                    use_single_back = single_back_ppt.get_value()

                    if top_insert_backing:
                        top_insert_backing.set_formula('Doors_Backing_Gap', [Doors_Backing_Gap])

                    if use_single_back:
                        top_ppt.set_value(use_center)
                        center_ppt.set_value(use_center)
                        bottom_ppt.set_value(use_center)
                        single_back_ppt.set_value(use_single_back)


bpy.utils.register_class(PROMPTS_Door_Prompts)
bpy.utils.register_class(OPS_Doors_Drop)
