from os import path
import math

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, EnumProperty

from snap import sn_types, sn_unit, sn_utils
from ..ops.drop_closet import PlaceClosetInsert
from .. import closet_props
from ..common import common_prompts
from ..common import common_parts

WIRE_HAMPER_HEIGHTS = [
    ('557.276', '18H-22.52"', '18H-22.52"'),
    ('589.280', '19H-23.78"', '19H-23.78"'),
    ('621.284', '20H-25.04"', '20H-25.04"'),
    ('653.288', '21H-26.30"', '21H-26.30"'),
    ('685.292', '22H-27.56"', '22H-27.56"')
]

NYLON_HAMPER_HEIGHTS = [
    ('621.284', '20H-25.04"', '20H-25.04"'),
    ('653.288', '21H-26.30"', '21H-26.30"'),
    ('685.292', '22H-27.56"', '22H-27.56"')
]

WIRE_BASKET_HEIGHT = 19.0

class Hamper(sn_types.Assembly):

    type_assembly = "INSERT"
    id_prompt = "sn_closets.hampers_prompts"
    drop_id = "sn_closets.insert_hamper_drop"
    placement_type = "SPLITTER"
    show_in_library = True
    category_name = "Products - Basic"    
    mirror_y = False
    
    upper_interior = None
    upper_exterior = None
    overlay_ppt_obj = None

    def update(self):
        super().update()
        self.obj_bp.snap.export_as_subassembly = True
        props = self.obj_bp.sn_closets
        self.obj_bp["IS_BP_HAMPER"] = True
        props.is_hamper_insert_bp = True        

    def draw(self):
        self.create_assembly()
        common_prompts.add_thickness_prompts(self)
        self.overlay_ppt_obj = common_prompts.add_front_overlay_prompts(self)
        common_prompts.add_pull_prompts(self)
        common_prompts.add_drawer_pull_prompts(self)

        self.add_prompt("Tilt Out Hamper", 'CHECKBOX', True)
        self.add_prompt("Hamper Type", 'COMBOBOX', 0, ['Wire', 'Hafele Nylon'])
        self.add_prompt("Add Cloth Bag", 'CHECKBOX', False)
        self.add_prompt("Wire Basket Color", 'COMBOBOX', 0, ['Chrome', 'White'])
        self.add_prompt("Remove Bottom Shelf", 'CHECKBOX', False)
        self.add_prompt("Remove Top Shelf", 'CHECKBOX', True)
        self.add_prompt("Wire Hamper Height", 'DISTANCE', sn_unit.millimeter(589.280))
        self.add_prompt("Nylon Hamper Height", 'DISTANCE', sn_unit.millimeter(621.284))
        self.add_prompt("Hamper Backing Gap", 'DISTANCE', 0, prompt_obj=self.add_prompt_obj("Backing_Gap"))
        self.add_prompt("Cleat Location", 'COMBOBOX', 0, ["Above", "Below", "None"])  # columns=3
        self.add_prompt("Cleat Height", 'DISTANCE', sn_unit.inch(3.64))
        self.add_prompt("Shelf Backing Setback", 'DISTANCE', 0)
        self.add_prompt("Full Overlay", 'CHECKBOX', False)

        Width = self.obj_x.snap.get_var('location.x', 'Width')
        Height = self.obj_z.snap.get_var('location.z', 'Height')
        Depth = self.obj_y.snap.get_var('location.y', 'Depth')
        Left_Overlay = self.get_prompt("Left Overlay").get_var('Left_Overlay')
        Right_Overlay = self.get_prompt("Right Overlay").get_var('Right_Overlay')
        Top_Overlay = self.get_prompt("Top Overlay").get_var('Top_Overlay')
        Bottom_Overlay = self.get_prompt("Bottom Overlay").get_var('Bottom_Overlay')
        Door_to_Cabinet_Gap = self.get_prompt("Door to Cabinet Gap").get_var('Door_to_Cabinet_Gap')
        Front_Thickness = self.get_prompt("Front Thickness").get_var('Front_Thickness')
        Center_Pulls_on_Drawers = self.get_prompt("Center Pulls on Drawers").get_var('Center_Pulls_on_Drawers')
        Drawer_Pull_From_Top = self.get_prompt("Drawer Pull From Top").get_var('Drawer_Pull_From_Top')
        Open = self.get_prompt("Open").get_var('Open')
        Inset_Front = self.overlay_ppt_obj.snap.get_prompt("Inset Front").get_var('Inset_Front')
        Tilt_Out_Hamper = self.get_prompt("Tilt Out Hamper").get_var('Tilt_Out_Hamper')
        Shelf_Thickness = self.get_prompt("Shelf Thickness").get_var('Shelf_Thickness')
        Remove_Bottom_Shelf = self.get_prompt("Remove Bottom Shelf").get_var('Remove_Bottom_Shelf')
        Remove_Top_Shelf = self.get_prompt("Remove Top Shelf").get_var('Remove_Top_Shelf')
        WHH = self.get_prompt("Wire Hamper Height").get_var('WHH')
        NHH = self.get_prompt("Nylon Hamper Height").get_var('NHH')
        Hamper_Type = self.get_prompt("Hamper Type").get_var('Hamper_Type')
        Cleat_Location = self.get_prompt("Cleat Location").get_var('Cleat_Location')
        Cleat_Height = self.get_prompt("Cleat Height").get_var('Cleat_Height')
        Shelf_Backing_Setback = self.get_prompt("Shelf Backing Setback").get_var('Shelf_Backing_Setback')
        Full_Overlay = self.get_prompt("Full Overlay").get_var('Full_Overlay')
        SDFOD = self.get_prompt("Single Door Full Overlay Difference").get_var('SDFOD')
        Wire_Basket_Color = self.get_prompt("Wire Basket Color").get_var('Wire_Basket_Color')

        self.get_prompt('Hamper Backing Gap').set_formula('IF(Hamper_Type==0,WHH,NHH)+(Shelf_Thickness*2)', [Hamper_Type, WHH, NHH, Shelf_Thickness])

        #PULL OUT WIDTH ERROR DIM
        # dim_x = sn_types.Dimension()
        # dim_x.parent(self.obj_bp)
        # dim_x.start_z(value = 0)
        # dim_x.start_x(value = 0)
        # dim_x.end_x('Width',[Width])
        # dim_x.anchor.cabinetlib.glfontx = sn_unit.inch(20)
        # dim_x.hide('IF(Width<INCH(17.99),False,True)',[Width])
        # dim_x.set_color(value = 3)
        # dim_x.set_label('Hamper Min Width (18")',new_line=True)
        
        #DEPTH ERROR DIM
        # dim_y = sn_types.Dimension()
        # dim_y.parent(self.obj_bp)
        # dim_y.start_z(value=sn_unit.inch(10))
        # dim_y.start_x('Width/2',[Width])
        # dim_y.end_y('Depth',[Depth])
        # dim_y.anchor.cabinetlib.glfontx = sn_unit.inch(20)
        # dim_y.hide('IF(fabs(Depth)<INCH(15.99),False,True)',[Depth])
        # dim_y.set_color(value = 3)
        # dim_y.set_label('Hamper Min Depth (16")',new_line=True)

        front = common_parts.add_hamper_front(self)
        front.loc_x('IF(Full_Overlay,-Left_Overlay*2,-Left_Overlay)',[Left_Overlay,Full_Overlay])
        front.loc_y('IF(Inset_Front,Front_Thickness,-Door_to_Cabinet_Gap)-IF(Tilt_Out_Hamper,0,Depth*Open)',[Door_to_Cabinet_Gap,Inset_Front,Front_Thickness,Tilt_Out_Hamper,Depth,Open])
        front.loc_z('-Bottom_Overlay',[Bottom_Overlay])
        front.rot_y('IF(Tilt_Out_Hamper,radians(-90)-(Open*.325),radians(-90))',[Tilt_Out_Hamper,Open])
        front.rot_z(value=math.radians(90))
        front.dim_x('IF(Hamper_Type==0,WHH,NHH)+Top_Overlay+Bottom_Overlay', [Hamper_Type, WHH, NHH, Top_Overlay, Bottom_Overlay])
        front.dim_y('IF(Full_Overlay,(Width+(Shelf_Thickness*2)-SDFOD),(Width+Left_Overlay+Right_Overlay))*-1',[Width,Left_Overlay,Right_Overlay,Full_Overlay,SDFOD,Shelf_Thickness])
        front.dim_z('Front_Thickness',[Front_Thickness])

        pull = common_parts.add_drawer_pull(self)
        pull.set_name("Hamper Drawer Pull")
        pull.loc_x('-Left_Overlay',[Left_Overlay])
        pull.loc_y('IF(Inset_Front,Front_Thickness,-Door_to_Cabinet_Gap)-IF(Tilt_Out_Hamper,0,Depth*Open)',[Door_to_Cabinet_Gap,Inset_Front,Front_Thickness,Tilt_Out_Hamper,Depth,Open])
        pull.loc_z('-Bottom_Overlay',[Bottom_Overlay])
        pull.rot_x('IF(Tilt_Out_Hamper,radians(90)+(Open*.325),radians(90))',[Tilt_Out_Hamper,Open])
        pull.dim_x('Width+Left_Overlay+Right_Overlay',[Width,Left_Overlay,Right_Overlay])
        pull.dim_y('IF(Hamper_Type==0,WHH,NHH)+Top_Overlay+Bottom_Overlay', [Hamper_Type, WHH, NHH, Top_Overlay, Bottom_Overlay])
        pull.dim_z('Front_Thickness',[Front_Thickness])
        pull.get_prompt("Pull X Location").set_formula('IF(Center_Pulls_on_Drawers,IF(Hamper_Type==0,WHH,NHH)/2,Drawer_Pull_From_Top)', [Center_Pulls_on_Drawers, Hamper_Type, WHH, NHH, Drawer_Pull_From_Top])
        pull.get_prompt("Pull Z Location").set_formula('(Width/2)+Right_Overlay',[Width,Right_Overlay])

        # Wire Basket
        basket_1 = common_parts.add_wire_hamper(self)
        basket_1.loc_x('IF(Width<=INCH(23.99),Width-INCH(18),Width-INCH(24))/2', [Width])
        basket_1.loc_y('-IF(Tilt_Out_Hamper,0,Depth*Open)', [Tilt_Out_Hamper, Depth, Open])
        basket_1.rot_x('IF(Tilt_Out_Hamper,Open*.325,0)', [Open, Tilt_Out_Hamper])
        basket_1.dim_x('IF(Width<=INCH(23.99),INCH(18),INCH(24))', [Width])
        basket_1.dim_y('IF(Depth<=INCH(15.99),INCH(14),INCH(16))', [Depth])
        basket_1.dim_z(value=sn_unit.inch(WIRE_BASKET_HEIGHT))
        basket_1.get_prompt('Hide').set_formula('IF(Hamper_Type==0,False,True)', [Hamper_Type])
        basket_1.get_prompt("Wire Basket Color").set_formula("Wire_Basket_Color", [Wire_Basket_Color])

        # Hafele Nylon
        basket_2 = common_parts.add_single_canvas_hamper(self)
        basket_2.loc_x('(Width-IF(Width<INCH(24),INCH(18),IF(Width<INCH(29.9999),INCH(24),INCH(30))))/2', [Width])
        basket_2.loc_y('-IF(Tilt_Out_Hamper,0,Depth*Open)', [Tilt_Out_Hamper, Depth, Open])
        basket_2.rot_x('IF(Tilt_Out_Hamper,Open*.325,0)', [Open, Tilt_Out_Hamper])
        basket_2.dim_x("IF(Width<INCH(24),INCH(18),IF(Width<INCH(29.9999),INCH(24),INCH(15)))", [Width])
        basket_2.dim_y(value=sn_unit.inch(12.0625))
        basket_2.dim_z(value=sn_unit.millimeter(621.284))
        basket_2.get_prompt('Hide').set_formula(
            'IF(AND(Height>=INCH(25),Width>=INCH(17.999),Hamper_Type==1),False,True)',
            [Hamper_Type, Width, Height])

        # Double Nylon
        basket_3 = common_parts.add_single_canvas_hamper(self)
        basket_3.loc_x('Width/2', [Width])
        basket_3.loc_y('-IF(Tilt_Out_Hamper,0,Depth*Open)', [Tilt_Out_Hamper, Depth, Open])
        basket_3.rot_x('IF(Tilt_Out_Hamper,Open*.325,0)', [Open, Tilt_Out_Hamper])
        basket_3.dim_x("INCH(15)", [Width])
        basket_3.dim_y(value=sn_unit.inch(12.0625))
        basket_3.dim_z(value=sn_unit.millimeter(621.284))
        basket_3.get_prompt('Hide').set_formula(
            'IF(AND(Width>INCH(29.99999),Hamper_Type==1),False,True)',
            [Hamper_Type, Width, Height])

        # basket_3 = common_parts.add_double_canvas_hamper(self)
        # basket_3.loc_x('(Width-INCH(24.0))/2',[Width])
        # basket_3.loc_y('-IF(Tilt_Out_Hamper,0,Depth*Open)',[Tilt_Out_Hamper,Depth,Open])
        # basket_3.rot_x('IF(Tilt_Out_Hamper,Open*.325,0)',[Open,Tilt_Out_Hamper])
        # basket_3.dim_x(value = sn_unit.inch(24.0))
        # basket_3.dim_y(value = sn_unit.inch(12.0625))
        # basket_3.dim_z(value = sn_unit.inch(WIRE_BASKET_HEIGHT))
        # basket_3.get_prompt('Hide').set_formula('IF(AND(Width>=INCH(24.0),Hamper_Type==1),False,True)',[Hamper_Type,Width])     

        cleat = common_parts.add_cleat(self)
        cleat.set_name("Bottom Cleat")
        cleat.loc_y('Depth',[Depth])
        cleat.loc_z('IF(Hamper_Type==0,WHH,NHH)+IF(Cleat_Location==0,Shelf_Thickness,0)', [Hamper_Type, WHH, NHH, Cleat_Location, Shelf_Thickness])
        cleat.rot_x(value=math.radians(-90))
        cleat.dim_x('Width',[Width])
        cleat.dim_y('IF(Cleat_Location==0,-Cleat_Height,Cleat_Height)', [Cleat_Height, Cleat_Location])
        cleat.dim_z('-Shelf_Thickness',[Shelf_Thickness])
        cleat.get_prompt("Hide").set_formula("IF(Cleat_Location==2,True,False)", [Cleat_Location])
        cleat.get_prompt('Use Cleat Cover').set_formula('IF(Cleat_Location==0,True,False)', [Cleat_Location])  

        top_shelf = common_parts.add_shelf(self)
        top_shelf.loc_y('Depth-Shelf_Backing_Setback',[Depth,Shelf_Backing_Setback])
        top_shelf.loc_z('IF(Hamper_Type==0,WHH,NHH)+Shelf_Thickness', [Hamper_Type, WHH, NHH, Shelf_Thickness])
        top_shelf.dim_x('Width',[Width])
        top_shelf.dim_y('-Depth+Shelf_Backing_Setback',[Depth,Shelf_Backing_Setback])
        top_shelf.dim_z('-Shelf_Thickness',[Shelf_Thickness])
        top_shelf.get_prompt('Hide').set_formula('IF(Remove_Top_Shelf,False,True)',[Remove_Top_Shelf])
        top_shelf.get_prompt('Is Locked Shelf').set_value(value=True)
        top_shelf.get_prompt("Is Forced Locked Shelf").set_value(value=True)
        
        bottom_shelf = common_parts.add_shelf(self)
        bottom_shelf.loc_y('Depth-Shelf_Backing_Setback',[Depth,Shelf_Backing_Setback])
        bottom_shelf.loc_z('0',[Shelf_Thickness])
        bottom_shelf.dim_x('Width',[Width])
        bottom_shelf.dim_y('-Depth+Shelf_Backing_Setback',[Depth,Shelf_Backing_Setback])
        bottom_shelf.dim_z('-Shelf_Thickness',[Shelf_Thickness])
        bottom_shelf.get_prompt('Hide').set_formula('IF(Remove_Bottom_Shelf,True,False)',[Remove_Bottom_Shelf])
        bottom_shelf.get_prompt('Is Locked Shelf').set_value(value=True)
        bottom_shelf.get_prompt("Is Forced Locked Shelf").set_value(value=True)
        
        opening = common_parts.add_opening(self)
        opening.loc_z('IF(Hamper_Type==0,WHH,NHH)+Shelf_Thickness', [Hamper_Type, WHH, NHH, Shelf_Thickness])
        opening.dim_x('Width',[Width])
        opening.dim_y('Depth',[Depth])
        opening.dim_z('Height-IF(Hamper_Type==0,WHH,NHH)-Shelf_Thickness', [Height, Hamper_Type, WHH, NHH, Shelf_Thickness])            
        
        if self.upper_exterior:
            opening.obj_bp.snap.exterior_open = False
            
            self.upper_exterior.draw()
            self.upper_exterior.obj_bp.parent = self.obj_bp
            self.upper_exterior.loc_z('IF(Hamper_Type==0,WHH,NHH)+Shelf_Thickness', [Hamper_Type, WHH, NHH, Shelf_Thickness])
            self.upper_exterior.dim_x('Width',[Width])
            self.upper_exterior.dim_y('Depth',[Depth])
            self.upper_exterior.dim_z('Height-IF(Hamper_Type==0,WHH,NHH)-Shelf_Thickness', [Height, Hamper_Type, WHH, NHH, Shelf_Thickness])
        
        if self.upper_interior:
            opening.obj_bp.snap.interior_open = False
            
            self.upper_interior.draw()
            self.upper_interior.obj_bp.parent = self.obj_bp
            self.upper_interior.loc_z('IF(Hamper_Type==0,WHH,NHH)+Shelf_Thickness', [Hamper_Type, WHH, NHH, Shelf_Thickness])
            self.upper_interior.dim_x('Width',[Width])
            self.upper_interior.dim_y('Depth',[Depth])
            self.upper_interior.dim_z('Height-IF(Hamper_Type==0,WHH,NHH)-Shelf_Thickness', [Height, WHH, NHH, Hamper_Type, Shelf_Thickness])

        self.update()               


class PROMPTS_Hamper_Prompts(sn_types.Prompts_Interface):
    bl_idname = "sn_closets.hampers_prompts"
    bl_label = "Hamper Options"
    bl_description = "This shows all of the available hamper options"
    bl_options = {'UNDO'}

    object_name: StringProperty(name="Object Name")
    wire_hamper_height: EnumProperty(name="Wire Hamper Face Height", items=WIRE_HAMPER_HEIGHTS, default='589.280')
    nylon_hamper_height: EnumProperty(name="Nylon Face Height", items=NYLON_HAMPER_HEIGHTS)

    hamper_type: EnumProperty(
        name="Hamper Type",
        items=[
            ('0', 'Wire', 'Wire'),
            ('1', 'Hafele Nylon', 'Hafele Nylon')],
        default='0')

    cleat_location: EnumProperty(
        name="Cleat Location",
        items=[
            ('0', 'Above', 'Above'),
            ('1', 'Below', 'Below'),
            ('2', 'None', 'None')],
        default='0')

    wire_basket_color: EnumProperty(
        name="Wire Basket Color",
        items=[
            ('0', 'Chrome', 'Chrome'),
            ('1', 'White', 'White')],
        default='0')

    assembly = None
    wire_hamper_height_prompt = None
    nylon_hamper_height_prompt = None
    hamper_type_prompt = None
    cleat_loc_prompt = None
    wire_basket_color_prompt = None
    basket_width = 0
    basket_depth = 0

    def get_basket_dimensions(self, hamper_type):
        if hamper_type == 0:
            # Wire Basket
            if self.assembly.obj_x.location.x <= sn_unit.inch(23.99):
                self.basket_width = 18
            else:
                self.basket_width = 24

            if self.assembly.obj_y.location.y <= sn_unit.inch(15.99):
                self.basket_depth = 14
            else:
                self.basket_depth = 16
        else:
            # Nylon Basket
            if self.assembly.obj_x.location.x <= sn_unit.inch(23.99):
                self.basket_width = 18
            elif self.assembly.obj_x.location.x <= sn_unit.inch(29.99):
                self.basket_width = 24
            else:
                self.basket_width = 30

            self.basket_depth = 16

    def execute(self, context):
        return {'FINISHED'}

    def check(self, context):
        props = bpy.context.scene.sn_closets

        if self.wire_hamper_height_prompt and props.closet_defaults.use_32mm_system:
            self.wire_hamper_height_prompt.set_value(sn_unit.inch(float(self.wire_hamper_height) / 25.4))

        if self.nylon_hamper_height_prompt and props.closet_defaults.use_32mm_system:
            self.nylon_hamper_height_prompt.set_value(sn_unit.inch(float(self.nylon_hamper_height) / 25.4))

        if self.hamper_type_prompt:
            self.hamper_type_prompt.set_value(int(self.hamper_type))
            self.get_basket_dimensions(int(self.hamper_type))

        if self.wire_basket_color_prompt:
            self.wire_basket_color_prompt.set_value(int(self.wire_basket_color))

        if self.cleat_loc_prompt:
            self.cleat_loc_prompt.set_value(int(self.cleat_location))

        if int(self.hamper_type) == 1:
            if self.assembly.obj_y.location.y <= sn_unit.inch(15.99):
                self.hamper_type = "0"
                self.hamper_type_prompt.set_value(0)
                self.hamper_depth = 14

        sn_utils.run_calculators(self.assembly.obj_bp)
        sn_utils.run_calculators(self.assembly.obj_bp.parent)  # Recalc top level assembly for backing that relies on this insert height
        self.assembly.obj_bp.location = self.assembly.obj_bp.location  # Redraw Viewport
        closet_props.update_render_materials(self, context)
        return True

    def set_properties_from_prompts(self):
        props = bpy.context.scene.sn_closets
        self.wire_hamper_height_prompt = self.assembly.get_prompt("Wire Hamper Height")
        self.nylon_hamper_height_prompt = self.assembly.get_prompt("Nylon Hamper Height")
        self.hamper_type_prompt = self.assembly.get_prompt('Hamper Type')
        self.cleat_loc_prompt = self.assembly.get_prompt('Cleat Location')
        self.wire_basket_color_prompt = self.assembly.get_prompt("Wire Basket Color")

        if self.wire_hamper_height_prompt and props.closet_defaults.use_32mm_system:
            value = round(self.wire_hamper_height_prompt.get_value() * 1000, 3)

            for index, t_height in enumerate(WIRE_HAMPER_HEIGHTS):
                if not value >= float(t_height[0]):
                    self.hamper_height = WIRE_HAMPER_HEIGHTS[index - 1][0]
                    break

        if self.nylon_hamper_height_prompt and props.closet_defaults.use_32mm_system:
            value = round(self.nylon_hamper_height_prompt.get_value() * 1000, 3)

            for index, t_height in enumerate(NYLON_HAMPER_HEIGHTS):
                if not value >= float(t_height[0]):
                    self.hamper_height = NYLON_HAMPER_HEIGHTS[index - 1][0]
                    break

        if self.hamper_type_prompt:
            self.hamper_type = str(self.hamper_type_prompt.combobox_index)
            self.get_basket_dimensions(self.hamper_type_prompt.combobox_index)

        if self.wire_basket_color_prompt:
            self.wire_basket_color = str(self.wire_basket_color_prompt.combobox_index)

        if self.cleat_loc_prompt:
            self.cleat_location = str(self.cleat_loc_prompt.combobox_index)

        if int(self.hamper_type) == 1:
            if self.assembly.obj_y.location.y <= sn_unit.inch(15.99):
                self.hamper_type = "0"
                self.hamper_type_prompt.set_value(0)
                self.hamper_depth = 14

    def invoke(self, context, event):
        self.assembly = self.get_insert()
        self.set_properties_from_prompts()
        return super().invoke(context, event, width=300)

    def draw(self, context):
        super().draw(context)
        props = bpy.context.scene.sn_closets
        layout = self.layout
        if self.assembly.obj_bp:
            if self.assembly.obj_bp.name in context.scene.objects:
                open_drawer = self.assembly.get_prompt('Open')
                # tilt_out_hamper = self.assembly.get_prompt('Tilt Out Hamper')
                # hamper_type = self.assembly.get_prompt('Hamper Type')
                cleat_loc = self.assembly.get_prompt("Cleat Location")
                full_overlay = self.assembly.get_prompt("Full Overlay")
                # wire_hamper_height = self.assembly.get_prompt("Wire Hamper Height")
                # nylon_hamper_height = self.assembly.get_prompt("Nylon Hamper Height")
                wire_basket_color = self.assembly.get_prompt("Wire Basket Color")
                add_cloth_bag = self.assembly.get_prompt("Add Cloth Bag")

                box = layout.box()

                dimension_box = box.box()
                dimension_box.label(text="Basket Dimensions")
                row = dimension_box.row()
                row.label(text="Width")
                row.label(text=str(self.basket_width) + '"')
                row = dimension_box.row()
                row.label(text="Depth")
                row.label(text=str(self.basket_depth) + '"')

                row = box.row()
                row.label(text="Open")
                row.prop(open_drawer, 'factor_value', text="")

                row = box.row()
                split = row.split(factor=0.5)
                split.label(text=self.hamper_type_prompt.name)
                if self.assembly.obj_y.location.y >= sn_unit.inch(15.999):
                    split.prop(self, "hamper_type", text="")
                else:
                    split.label(text="Wire")

                if int(self.hamper_type) == 0:
                    row = box.row()
                    if wire_basket_color:
                        split = row.split(factor=0.5)
                        split.label(text=self.wire_basket_color_prompt.name)
                        split.prop(self, 'wire_basket_color', text="")

                if add_cloth_bag:
                    if int(self.hamper_type) == 0:
                        row = box.row()
                        split = row.split(factor=0.5)
                        split.label(text=add_cloth_bag.name)
                        split.prop(add_cloth_bag, 'checkbox_value', text="")

                row = box.row()
                if props.closet_defaults.use_32mm_system:
                    split = row.split(factor=0.5)
                    split.label(text="Hamper Face Height")
                    if int(self.hamper_type) == 0:
                        split.prop(self, 'wire_hamper_height', text="")
                    else:
                        split.prop(self, 'nylon_hamper_height', text="")

                row = box.row()
                if cleat_loc:
                    split = row.split(factor=0.5)
                    split.label(text="Cleat Location")
                    split.prop(self, "cleat_location", expand=True)

                # row = box.row()
                # if tilt_out_hamper:
                #     split = row.split(factor=0.5)
                #     split.label(text=tilt_out_hamper.name)
                #     row.prop(tilt_out_hamper, "checkbox_value", text="")

                row = box.row()
                if(full_overlay):
                    split = row.split(factor=0.5)
                    split.label(text=full_overlay.name)
                    row.prop(full_overlay, "checkbox_value", text="")


class OPS_Hamper_Drop(Operator, PlaceClosetInsert):
    bl_idname = "sn_closets.insert_hamper_drop"
    bl_label = "Custom drag and drop for hamper insert"
    adjacent_cant_be_deeper = True

    def show_openings(self):
        # Clear  to avoid old/duplicate openings
        self.openings.clear()
        insert_type = self.insert.obj_bp.snap.placement_type
        insert_op_num = self.insert.obj_bp.sn_closets.opening_name

        for obj in bpy.context.scene.objects:
            # Check to avoid opening that is part of the dropped insert
            if sn_utils.get_parent_assembly_bp(obj) == self.insert.obj_bp:
                continue

            opening = None

            opening_width = 0
            opening_depth = 0
            if obj.parent:
                if obj.parent.get("IS_BP_CLOSET"):
                    closet_assembly = sn_types.Assembly(obj.parent)
                    opening_width_ppt = closet_assembly.get_prompt("Opening " + str(obj.sn_closets.opening_name) + " Width")
                    if opening_width_ppt:
                        opening_width = round(sn_unit.meter_to_inch(opening_width_ppt.get_value()), 2)
                    opening_depth_ppt = closet_assembly.get_prompt("Opening " + str(obj.sn_closets.opening_name) + " Depth")
                    if opening_depth_ppt:
                        opening_depth = round(sn_unit.meter_to_inch(opening_depth_ppt.get_value()), 2)
            if obj.snap.type_group == 'OPENING' and opening_width >= 18 and opening_depth >= 14:

                wall = sn_types.Wall(obj_bp=sn_utils.get_wall_bp(obj))

                # Ensure opening status is set correctly
                product_bp = sn_utils.get_closet_bp(obj)
                if product_bp:
                    op_num = obj.sn_closets.opening_name
                    op_inserts = [o for o in product_bp.children if o.snap.type_group == 'INSERT' and o.sn_closets.opening_name == op_num]
                    if not op_inserts:
                        obj.snap.interior_open = True
                        obj.snap.exterior_open = True

                wall_hidden = False
                collections = bpy.data.collections
                wall_bp = sn_utils.get_wall_bp(obj)
                if wall_bp:
                    wall_name = wall_bp.snap.name_object
                    if wall_name in collections:
                        wall_coll = collections[wall_name]
                        wall_hidden = wall_coll.hide_viewport
                if wall and sn_utils.get_wall_bp(obj) and wall_hidden:
                    continue
                if insert_type in ('INTERIOR', 'SPLITTER'):
                    opening = sn_types.Assembly(obj) if obj.snap.interior_open else None
                if insert_type == 'EXTERIOR':
                    opening = sn_types.Assembly(obj) if obj.snap.exterior_open else None
                if opening:
                    cage = opening.get_cage()
                    cage.display_type = 'WIRE'
                    cage.hide_select = False
                    cage.hide_viewport = False
                    self.openings.append(cage)

    def modal(self, context, event):
        self.run_asset_calculators()
        bpy.ops.object.select_all(action='DESELECT')
        context.area.tag_redraw()
        self.reset_selection()

        if len(self.openings) == 0:
            bpy.ops.snap.message_box(
                'INVOKE_DEFAULT', message='There are no openings that are at least \n 18" wide and 14" deep in this scene.')
            context.area.header_text_set(None)
            return self.cancel_drop(context)

        self.selected_point, self.selected_obj, _ = sn_utils.get_selection_point(
            context,
            event,
            objects=self.include_objects,
            exclude_objects=self.exclude_objects)

        self.position_asset(context)

        if self.adjacent_cant_be_deeper and self.is_between_deeper():
            bpy.context.preferences.themes[0].view_3d.object_active = (1, 0, 0)
            bpy.context.preferences.themes[0].view_3d.object_selected = (1, 0, 0)

        elif self.adjacent_cant_be_deeper:
            bpy.context.preferences.themes[0].view_3d.object_active = (0.14902, 1, 0.6)
            bpy.context.preferences.themes[0].view_3d.object_selected = (0.14902, 1, 0.6)

        if self.event_is_place_first_point(event) and self.selected_opening:
            bpy.context.preferences.themes[0].view_3d.object_active = self.object_selected_original_color
            bpy.context.preferences.themes[0].view_3d.object_selected = self.active_object_original_color

            if self.adjacent_cant_be_deeper and self.is_between_deeper():
                bpy.ops.snap.message_box(
                    'INVOKE_DEFAULT',
                    message="This assembly cannot be placed here because it can only \n "
                            "be placed in openings with equal left and right partition depths.")
                return self.cancel_drop(context)
            self.confirm_placement(context)
            return self.finish(context)

        if self.event_is_cancel_command(event):
            bpy.context.preferences.themes[0].view_3d.object_active = self.object_selected_original_color
            bpy.context.preferences.themes[0].view_3d.object_selected = self.active_object_original_color
            return self.cancel_drop(context)

        if self.event_is_pass_through(event):
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}

    def execute(self, context):
        return super().execute(context)

    def confirm_placement(self, context):
        super().confirm_placement(context)
        self.set_backing_bottom_gap(self.insert.obj_bp, self.selected_opening)
        self.set_bottom_KD(self.insert.obj_bp, self.selected_opening)
        self.set_hamper_type(self.insert.obj_bp, self.selected_opening)
        bpy.context.view_layer.objects.active = self.insert.obj_bp
        # THIS NEEDS TO BE RUN TWICE TO AVOID RECAL ERRORS
        sn_utils.run_calculators(self.insert.obj_bp)
        sn_utils.run_calculators(self.insert.obj_bp)
        # TOP LEVEL PRODUCT RECAL
        sn_utils.run_calculators(sn_utils.get_closet_bp(self.insert.obj_bp))
        sn_utils.run_calculators(sn_utils.get_closet_bp(self.insert.obj_bp))
        # bpy.context.window.cursor_set('DEFAULT')

    def set_backing_bottom_gap(self, insert_bp, selected_opening):
        opening_name = selected_opening.obj_bp.sn_closets.opening_name
        carcass_bp = sn_utils.get_closet_bp(insert_bp)
        hamper_assembly = sn_types.Assembly(insert_bp)
        Hamper_Backing_Gap = hamper_assembly.get_prompt('Hamper Backing Gap').get_var()

        cleat_location = hamper_assembly.get_prompt("Cleat Location")
        has_counter_top = False
        for child in carcass_bp.children:
            if "IS_BP_COUNTERTOP" in child:
                has_counter_top = True
        if has_counter_top or "IS_BP_ISLAND" in carcass_bp:
            cleat_location.set_value(1)  # Setting Cleat Location to Below
            return

        for child in carcass_bp.children:
            if child.sn_closets.is_back_bp:
                if child.sn_closets.opening_name == opening_name:
                    back_assembly = sn_types.Assembly(child)
                    bottom_insert_backing = back_assembly.get_prompt('Bottom Insert Backing')
                    top_ppt = back_assembly.get_prompt("Top Section Backing")
                    center_ppt = back_assembly.get_prompt("Center Section Backing")
                    bottom_ppt = back_assembly.get_prompt("Bottom Section Backing")
                    single_back_ppt = back_assembly.get_prompt("Single Back")
                    use_center = center_ppt.get_value()
                    use_single_back = single_back_ppt.get_value()

                    if bottom_insert_backing:
                        bottom_insert_backing.set_formula('Hamper_Backing_Gap', [Hamper_Backing_Gap])

                    if use_single_back:
                        top_ppt.set_value(use_center)
                        center_ppt.set_value(use_center)
                        bottom_ppt.set_value(use_center)
                        single_back_ppt.set_value(use_single_back)

    def set_bottom_KD(self, insert_bp, selected_opening):
        opening_name = selected_opening.obj_bp.sn_closets.opening_name
        carcass_bp = sn_utils.get_closet_bp(insert_bp)
        drawer_assembly = sn_types.Assembly(insert_bp)
        carcass_assembly = sn_types.Assembly(carcass_bp)
        ppt_floor_mounted = carcass_assembly.get_prompt("Opening " + str(opening_name) + " Floor Mounted")
        ppt_remove_bottom_shelf = carcass_assembly.get_prompt('Remove Bottom Hanging Shelf ' + str(opening_name))

        if ppt_floor_mounted and ppt_remove_bottom_shelf:
            if ppt_floor_mounted.get_value() or ppt_remove_bottom_shelf.get_value():
                drawer_assembly.get_prompt("Remove Bottom Shelf").set_value(True)

    def set_hamper_type(self, insert_bp, selected_opening):
        opening_name = selected_opening.obj_bp.sn_closets.opening_name
        carcass_bp = sn_utils.get_closet_bp(insert_bp)
        hamper_assembly = sn_types.Assembly(insert_bp)
        carcass_assembly = sn_types.Assembly(carcass_bp)
        opening_width_ppt = carcass_assembly.get_prompt("Opening " + str(opening_name) + " Width")
        opening_depth_ppt = carcass_assembly.get_prompt("Opening " + str(opening_name) + " Depth")
        hamper_type = hamper_assembly.get_prompt("Hamper Type")
        prompts = (opening_width_ppt, opening_depth_ppt, hamper_type)
        if all(prompts):
            if opening_depth_ppt.get_value() >= sn_unit.inch(15.999) and opening_width_ppt.get_value() >= sn_unit.inch(29.999):
                hamper_type.set_value(1)


bpy.utils.register_class(PROMPTS_Hamper_Prompts)
bpy.utils.register_class(OPS_Hamper_Drop)
