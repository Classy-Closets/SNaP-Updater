import math
from snap.sn_unit import inch

import bpy
from bpy.props import StringProperty, FloatProperty, EnumProperty

from snap import sn_types, sn_unit, sn_utils
from os import path
from .. import closet_props
from ..common import common_parts
from ..common import common_prompts
from ..common import common_lists
from . import data_base_assembly


def update_closet_height(self,context):
    ''' EVENT changes height for all closet openings
    '''
    obj_product_bp = sn_utils.get_bp(context.active_object,'PRODUCT')
    product = sn_types.Assembly(obj_product_bp)
    product.run_all_calculators()
    product.obj_z.location.z = sn_unit.millimeter(float(self.height))
    product.run_all_calculators()


class Closet_Island_Carcass(sn_types.Assembly):

    type_assembly = "PRODUCT"
    id_prompt = "sn_closets.island_openings"
    plan_draw_id = "sn_closets.draw_plan"
    show_in_library = True
    category_name = ""

    countertop = None
    opening_qty = 4
    calculator = None
    is_double_sided = False

    def __init__(self, obj_bp=None):
        super().__init__(obj_bp=obj_bp)

        defaults = bpy.context.scene.sn_closets.closet_defaults
        self.width = (sn_unit.inch(24.75) * self.opening_qty) + sn_unit.inch(0.75)
        self.height = sn_unit.millimeter(float(defaults.island_panel_height))
        if self.is_double_sided:
            self.depth = defaults.panel_depth * 2
        else:
            self.depth = defaults.panel_depth

        if obj_bp:
            self.get_assemblies()

    def get_assemblies(self):
        for child in self.obj_bp.children:
            if "IS_BP_COUNTERTOP" in child and child["IS_BP_COUNTERTOP"]:
                self.countertop = sn_types.Assembly(child)

    def add_to_wall_collection(self, obj_bp):
        wall_bp = sn_utils.get_wall_bp(self.obj_bp)
        if wall_bp:
            wall_coll = bpy.data.collections[wall_bp.snap.name_object]
            scene_coll = bpy.context.scene.collection
            sn_utils.add_assembly_to_collection(obj_bp, wall_coll)
            sn_utils.remove_assembly_from_collection(obj_bp, scene_coll)

    def add_opening_prompts(self):
        for i in range(1, self.opening_qty + 1):
            calc_prompt = self.calculator.add_calculator_prompt("Opening " + str(i) + " Width")
            calc_prompt.equal = True            
            self.add_prompt("Opening " + str(i) + " Depth", 'DISTANCE', self.depth)            
        
    def add_island_prompts(self):
        props = bpy.context.scene.sn_closets.closet_defaults
        
        self.add_prompt("Left Against Wall", 'CHECKBOX', False)
        self.add_prompt("Right Against Wall", 'CHECKBOX', False)
        self.add_prompt("Back Against Wall", 'CHECKBOX', False)
        self.add_prompt("Exposed Back", 'CHECKBOX', True)
        self.add_prompt("No Countertop", 'CHECKBOX', False)
        self.add_prompt("Add TK Skin", 'CHECKBOX', False)
        self.add_prompt("TK Skin Thickness", 'DISTANCE', sn_unit.inch(0.25))
        self.add_prompt("Add Capping Base", 'CHECKBOX', False)
        self.add_prompt("Material Max Width", 'DISTANCE', sn_unit.inch(48))

        if self.is_double_sided:
            self.add_prompt("Depth 1", 'DISTANCE', props.panel_depth)
            self.add_prompt("Depth 2", 'DISTANCE', props.panel_depth)
            
            Depth_1 = self.get_prompt('Depth 1').get_var()
            Depth_2 = self.get_prompt('Depth 2').get_var()
            Back_Thickness = self.get_prompt('Back Thickness').get_var()
            Panel_Thickness = self.get_prompt('Panel Thickness').get_var()
            
            self.dim_y('(Depth_1+Depth_2+Panel_Thickness)*-1',[Depth_1,Depth_2,Panel_Thickness])
            
    def add_sides(self):
        props = bpy.context.scene.sn_closets   
        Toe_Kick_Height = self.get_prompt('Toe Kick Height').get_var('Toe_Kick_Height')
        Product_Height = self.obj_z.snap.get_var('location.z','Product_Height')
        Product_Width = self.obj_x.snap.get_var('location.x','Product_Width')
        Product_Depth = self.obj_y.snap.get_var('location.y','Product_Depth')
        Left_Side_Thickness = self.get_prompt('Left Side Thickness').get_var()
        Right_Side_Thickness = self.get_prompt('Right Side Thickness').get_var()
        #Add_Backing = self.get_prompt('Add Backing').get_var()
        Back_Thickness = self.get_prompt('Back Thickness').get_var()
        Panel_Thickness = self.get_prompt('Panel Thickness').get_var()
        Max_Width = self.get_prompt('Material Max Width').get_var("Max_Width")

        left_side = common_parts.add_panel(self, island_panel=True)
        left_side.obj_bp['PARTITION_NUMBER'] = 0
        left_side.dim_x('IF(abs(Product_Depth)>Max_Width,-Product_Depth,Product_Height)', [Product_Height, Product_Depth, Max_Width])
        left_side.dim_y('IF(abs(Product_Depth)>Max_Width,Product_Height,Product_Depth)', [Product_Depth, Product_Height, Max_Width])
        left_side.dim_z('-Left_Side_Thickness', [Left_Side_Thickness])
        left_side.loc_z('Toe_Kick_Height',[Toe_Kick_Height])

        left_side.rot_x("IF(abs(Product_Depth)>Max_Width,radians(90),0)", [Product_Depth, Max_Width])
        left_side.rot_y("IF(abs(Product_Depth)>Max_Width,0,radians(-90))", [Product_Depth, Max_Width])
        left_side.rot_z("IF(abs(Product_Depth)>Max_Width,radians(-90),0)", [Product_Depth, Max_Width])

        right_side = common_parts.add_panel(self, island_panel=True)
        right_side.obj_bp['PARTITION_NUMBER'] = self.opening_qty
        right_side.dim_x('IF(abs(Product_Depth)>Max_Width,-Product_Depth,Product_Height)', [Product_Height, Product_Depth, Max_Width])
        right_side.dim_y('IF(abs(Product_Depth)>Max_Width,Product_Height,Product_Depth)', [Product_Depth, Product_Height, Max_Width])
        right_side.dim_z('Right_Side_Thickness', [Right_Side_Thickness])
        right_side.loc_x('Product_Width',[Product_Width])
        right_side.loc_z('Toe_Kick_Height',[Toe_Kick_Height])

        right_side.rot_x("IF(abs(Product_Depth)>Max_Width,radians(90),0)", [Product_Depth, Max_Width])
        right_side.rot_y("IF(abs(Product_Depth)>Max_Width,0,radians(-90))", [Product_Depth, Max_Width])
        right_side.rot_z("IF(abs(Product_Depth)>Max_Width,radians(-90),0)", [Product_Depth, Max_Width])

    def add_panel(self,index,previous_panel):
        PH = self.obj_z.snap.get_var('location.z', 'PH')
        PD = self.obj_y.snap.get_var('location.y', 'PD')
        width_prompt = eval("self.calculator.get_calculator_prompt('Opening {} Width')".format(str(index - 1)))
        Width = eval("width_prompt.get_var(self.calculator.name, 'Width')".format(str(index)))
        Max_Width = self.get_prompt('Material Max Width').get_var("Max_Width")
        Panel_Thickness = self.get_prompt('Panel Thickness').get_var()
        Toe_Kick_Height = self.get_prompt('Toe Kick Height').get_var()

        panel = common_parts.add_panel(self, island_panel=True)
        panel.set_material_pointers("Closet_Part_Edges", "TopBottomEdge")

        if previous_panel:
            Prev_Panel_X = previous_panel.obj_bp.snap.get_var("location.x", 'Prev_Panel_X')
            Left_Side_Thickness = self.get_prompt('Left Side Thickness').get_var()
            panel.loc_x('Prev_Panel_X+Panel_Thickness+Width', [Prev_Panel_X, Panel_Thickness, Width])
        else:
            Left_Side_Thickness = self.get_prompt('Left Side Thickness').get_var()
            panel.loc_x('Left_Side_Thickness+Width+Panel_Thickness', [Left_Side_Thickness, Width, Panel_Thickness])

        panel.loc_z('Toe_Kick_Height', [Toe_Kick_Height])
        panel.rot_x("IF(abs(PD)>Max_Width,radians(90),0)", [PD, Max_Width])
        panel.rot_y("IF(abs(PD)>Max_Width,0,radians(-90))", [PD, Max_Width])
        panel.rot_z("IF(abs(PD)>Max_Width,radians(-90),0)", [PD, Max_Width])
        panel.dim_x('IF(abs(PD)>Max_Width,-PD,PH)', [PH, PD, Max_Width])
        panel.dim_y('IF(abs(PD)>Max_Width,PH,PD)', [PD, PH, Max_Width])
        panel.dim_z('Panel_Thickness', [Panel_Thickness])

        return panel

    def add_shelf(self,i,panel,is_top=False,is_rear=False):
        Product_Height = self.obj_z.snap.get_var('location.z','Product_Height')
        Product_Depth = self.obj_y.snap.get_var('location.y','Product_Depth')
        width_prompt = eval("self.calculator.get_calculator_prompt('Opening {} Width')".format(str(i)))
        Width = eval("width_prompt.get_var(self.calculator.name, 'Width')".format(str(i)))        
        # Depth_1 = self.get_prompt('Depth 1').get_var()
        # Depth_2 = self.get_prompt('Depth 2').get_var()
        Shelf_Thickness = self.get_prompt('Shelf Thickness').get_var()
        Toe_Kick_Height = self.get_prompt('Toe Kick Height').get_var()

        shelf = common_parts.add_shelf(self)
        shelf.get_prompt("Is Locked Shelf").set_value(value=True)
        shelf.get_prompt("Is Forced Locked Shelf").set_value(value=True)
        if panel:
            X_Loc = panel.obj_bp.snap.get_var('location.x','X_Loc')
            shelf.loc_x('X_Loc', [X_Loc])
        else:
            X_Loc = self.get_prompt('Left Side Thickness').get_var('X_Loc')
            shelf.loc_x('X_Loc', [X_Loc])
        
        shelf.dim_y("Product_Depth",[Product_Depth])
        
        if is_top:
            shelf.loc_z('Product_Height+Toe_Kick_Height',[Product_Height,Toe_Kick_Height])
            shelf.dim_z('-Shelf_Thickness',[Shelf_Thickness])
            shelf.obj_bp["IS_BP_TOP_KD_SHELF"] = True
        else:
            shelf.loc_z('Toe_Kick_Height',[Toe_Kick_Height])
            shelf.dim_z('Shelf_Thickness',[Shelf_Thickness])

        shelf.dim_x('Width',[Width])
        
        if is_top:
            shelf.get_prompt("Drill On Top").set_value(value=True)
        else:
            shelf.get_prompt("Drill On Top").set_value(value=False)
    
    def add_toe_kick(self,i,panel,is_rear=False):
        Product_Depth = self.obj_y.snap.get_var('location.y','Product_Depth')
        width_prompt = eval("self.calculator.get_calculator_prompt('Opening {} Width')".format(str(i)))
        Width = eval("width_prompt.get_var(self.calculator.name, 'Width')".format(str(i)))
        Toe_Kick_Height = self.get_var('Toe Kick Height')
        Toe_Kick_Setback = self.get_var('Toe Kick Setback')
        Shelf_Thickness = self.get_var('Shelf Thickness')
        Toe_Kick_Thickness = self.get_var('Toe Kick Thickness')

        if panel:
            X_Loc = panel.obj_bp.snap.get_var('location.x','X_Loc')
        else:
            X_Loc = self.get_var('Left Side Thickness','X_Loc')
        
        kick = common_parts.add_toe_kick(self)
        kick.dim_x("Width",[Width])
        kick.dim_y('-Toe_Kick_Height',[Toe_Kick_Height,Shelf_Thickness])
        kick.loc_x('X_Loc',[X_Loc])
        if is_rear:
            kick.loc_y('-Toe_Kick_Setback',[Product_Depth,Toe_Kick_Setback])
            kick.dim_z('-Toe_Kick_Thickness',[Toe_Kick_Thickness])
        else:
            kick.loc_y('Product_Depth+Toe_Kick_Setback',[Product_Depth,Toe_Kick_Setback])
            kick.dim_z('Toe_Kick_Thickness',[Toe_Kick_Thickness])
        kick.rot_x(value=math.radians(-90))
        
    def add_closet_opening(self,i,panel,is_rear=False):
        props = bpy.context.scene.sn_closets.closet_defaults
        
        Product_Height = self.obj_z.snap.get_var('location.z','Product_Height')
        Product_Depth = self.obj_y.snap.get_var('location.y','Product_Depth')
        width_prompt = eval("self.calculator.get_calculator_prompt('Opening {} Width')".format(str(i)))
        Width = eval("width_prompt.get_var(self.calculator.name, 'Width')".format(str(i)))        
        Shelf_Thickness = self.get_prompt('Shelf Thickness').get_var()
        Toe_Kick_Height = self.get_prompt('Toe Kick Height').get_var()
        
        opening = common_parts.add_section_opening(self)
        opening.obj_bp.sn_closets.opening_name = str(i)
        
        if panel:
            X_Loc = panel.obj_bp.snap.get_var('location.x','X_Loc')
        else:
            X_Loc = self.get_prompt('Left Side Thickness').get_var('X_Loc')

        opening.loc_z('Toe_Kick_Height+Shelf_Thickness',[Toe_Kick_Height,Shelf_Thickness])
        if is_rear:
            opening.loc_x('X_Loc+Width',[X_Loc,Width])
            opening.rot_z(value=math.radians(180))
            if self.is_double_sided:
                Depth_1 = self.get_prompt('Depth 1').get_var()
                opening.dim_y("Depth_1",[Depth_1])
        else:
            opening.loc_x('X_Loc',[X_Loc])
            opening.loc_y('Product_Depth',[Product_Depth])
            if self.is_double_sided:
                Depth_2 = self.get_prompt('Depth 2').get_var()
                opening.dim_y("Depth_2",[Depth_2])
            else:
                opening.dim_y("fabs(Product_Depth)",[Product_Depth])
        opening.dim_x('Width',[Width])
        
        if props.use_plant_on_top:
            opening.dim_z('Product_Height-Shelf_Thickness',[Product_Height,Shelf_Thickness])
        else:
            opening.dim_z('Product_Height-(Shelf_Thickness*2)',[Product_Height,Shelf_Thickness])
        
    def add_inside_dimension(self,i,panel):
        width_prompt = eval("self.calculator.get_calculator_prompt('Opening {} Width')".format(str(i)))
        Width = eval("width_prompt.get_var(self.calculator.name, 'Width')".format(str(i)))
        Left_Side_Wall_Filler = self.get_var('Left Side Wall Filler')
        
        if panel:
            X_Loc = panel.obj_bp.snap.get_var('location.x','X_Loc')
        else:
            X_Loc = self.get_var('Left Side Thickness','X_Loc')
            
        dim = sn_types.Dimension()
        dim.parent(self.obj_bp)
        dim.start_z(value = sn_unit.inch(-4))
        dim.start_y(value = sn_unit.inch(4))
        if panel:
            dim.start_x('X_Loc',[X_Loc])
        else:
            dim.start_x('X_Loc+Left_Side_Wall_Filler',[X_Loc,Left_Side_Wall_Filler])
        dim.end_x('Width',[Width])
        dim.set_color('IF(Width>INCH(42),3,0)',[Width])

    def add_thick_back(self):
        Product_Height = self.obj_z.snap.get_var('location.z','Product_Height')
        Product_Width = self.obj_x.snap.get_var('location.x','Product_Width')
        Toe_Kick_Height = self.get_prompt('Toe Kick Height').get_var()
        Panel_Thickness = self.get_prompt('Panel Thickness').get_var()
        Max_Width = self.get_prompt('Material Max Width').get_var("Max_Width")

        backing = common_parts.add_back(self)
        backing.obj_bp["IS_BP_CAPPING_BACK"] = True
        backing.loc_z('Toe_Kick_Height',[Toe_Kick_Height])

        backing.rot_x("IF(Product_Width>Max_Width,radians(90),0)", [Product_Width, Max_Width])
        backing.rot_y("IF(Product_Width>Max_Width,0,radians(-90))", [Product_Width, Max_Width])
        backing.rot_z("IF(Product_Width>Max_Width,0,radians(-90))", [Product_Width, Max_Width])

        backing.dim_x("IF(Product_Width>Max_Width,Product_Width,Product_Height)",
                      [Product_Height, Product_Width, Max_Width])
        backing.dim_y('IF(Product_Width>Max_Width,Product_Height,Product_Width)',
                      [Product_Width, Product_Height, Max_Width])
        backing.dim_z('IF(Product_Width>Max_Width,-Panel_Thickness,Panel_Thickness)',
                      [Product_Width, Max_Width, Panel_Thickness])

    def add_double_sided_back(self,i,panel):
        width_prompt = eval("self.calculator.get_calculator_prompt('Opening {} Width')".format(str(i)))
        Width = eval("width_prompt.get_var(self.calculator.name, 'Width')".format(str(i)))
        Product_Height = self.obj_z.snap.get_var('location.z','Product_Height')
        Product_Width = self.obj_x.snap.get_var('location.x','Product_Width')
        Back_Thickness = self.get_prompt('Back Thickness').get_var()
        Depth_1 = self.get_prompt('Depth 1').get_var()
        Toe_Kick_Height = self.get_prompt('Toe Kick Height').get_var()
        Panel_Thickness = self.get_prompt('Panel Thickness').get_var()
        Max_Width = self.get_prompt('Material Max Width').get_var("Max_Width")
        
        if panel:
            X_Loc = panel.obj_bp.snap.get_var('location.x','X_Loc')
        else:
            X_Loc = self.get_prompt('Left Side Thickness').get_var('X_Loc')
            
        backing = common_parts.add_back(self)
        backing.loc_x('IF(Width>Max_Width,X_Loc,X_Loc+Width)',[X_Loc, Width, Max_Width])
        backing.loc_y('-Depth_1',[Depth_1])
        backing.loc_z('Toe_Kick_Height + Panel_Thickness',[Toe_Kick_Height,Panel_Thickness])
        backing.rot_x(value=math.radians(90))
        backing.rot_y("IF(Width>Max_Width,0,radians(-90))", [Width, Max_Width])

        backing.dim_x("IF(Width>Max_Width,Width,Product_Height-(Panel_Thickness*2))", [Product_Height, Panel_Thickness, Width, Max_Width])
        backing.dim_y('IF(Width>Max_Width,Product_Height-(Panel_Thickness*2),Width)', [Product_Height, Panel_Thickness, Width, Max_Width])

        backing.dim_z('Panel_Thickness',[Panel_Thickness])
        
    def set_child_properties(self, obj):
        obj["ID_PROMPT"] = self.obj_bp["ID_PROMPT"]
        for child in obj.children:
            if child.type == 'MESH':
                child["ID_PROMPT"] = self.obj_bp["ID_PROMPT"]
            if child.children:
                self.set_child_properties(child)

    def add_countertop(self):
        dim_x = self.obj_x.snap.get_var('location.x', 'dim_x')
        dim_z = self.obj_z.snap.get_var('location.z', 'dim_z')
        dim_y = self.obj_y.snap.get_var('location.y', 'dim_y')

        countertop_type_ppt = self.get_prompt('Countertop Type')
        countertop_type = countertop_type_ppt.get_combobox_str()
        Countertop_Type = countertop_type_ppt.get_var()
        no_countertop = self.get_prompt('No Countertop').get_value()
        ct_type_tag = "COUNTERTOP_{}".format(countertop_type.upper())
        if countertop_type == "Standard Quartz":
            ct_type_tag = "COUNTERTOP_QUARTZ"

        if self.countertop:
            if no_countertop:
                sn_utils.delete_object_and_children(self.countertop.obj_bp)
                self.countertop = None
                return
            elif ct_type_tag in self.countertop.obj_bp:
                return
            else:
                sn_utils.delete_object_and_children(self.countertop.obj_bp)
                self.countertop = None

        Front_Overhang = self.get_prompt("Front Overhang").get_var()
        Back_Overhang = self.get_prompt("Back Overhang").get_var()
        Left_Overhang = self.get_prompt("Left Overhang").get_var()
        Right_Overhang = self.get_prompt("Right Overhang").get_var()

        Left_Against_Wall = self.get_prompt('Left Against Wall').get_var()
        Right_Against_Wall = self.get_prompt('Right Against Wall').get_var()
        Exposed_Back = self.get_prompt('Exposed Back').get_var()
        Toe_Kick_Height = self.get_prompt('Toe Kick Height').get_var()

        if countertop_type == 'Melamine':
            self.countertop = common_parts.add_cc_countertop(self)
            constraint = self.countertop.obj_x.constraints.new(type='LIMIT_LOCATION')
            constraint.use_max_x = True
            constraint.max_x = sn_unit.inch(96)
            constraint.owner_space = 'LOCAL'
            constraint = self.countertop.obj_y.constraints.new(type='LIMIT_LOCATION')
            constraint.use_min_y = True
            constraint.min_y = sn_unit.inch(-48)
            constraint.owner_space = 'LOCAL'
        if countertop_type in ('HPL', 'Custom'):
            self.countertop = common_parts.add_hpl_top(self)
            self.countertop.dim_z("IF(Countertop_Type==1,INCH(0.75),INCH(1.5))", [Countertop_Type])
        if countertop_type == 'Granite':
            self.countertop = common_parts.add_granite_countertop(self)
        if countertop_type == 'Quartz':
            self.countertop = common_parts.add_quartz_countertop(self)
        if countertop_type == 'Standard Quartz':
            self.countertop = common_parts.add_quartz_countertop(self)
        if countertop_type == 'Wood':
            self.countertop = common_parts.add_wood_countertop(self)

        self.countertop.set_name("{} Countertop".format(countertop_type))
        self.countertop.obj_bp.sn_closets.is_countertop_bp = True
        self.countertop.obj_bp["IS_BP_COUNTERTOP"] = True

        if "ID_PROMPT" in self.obj_bp:
            self.set_child_properties(self.countertop.obj_bp)
        
        self.countertop.loc_x('IF(Left_Against_Wall,0,-Left_Overhang)', [Left_Against_Wall, Left_Overhang])
        self.countertop.loc_y('Back_Overhang', [Back_Overhang])
        self.countertop.loc_z('dim_z+Toe_Kick_Height', [dim_z, Toe_Kick_Height])

        self.countertop.dim_x(
            'dim_x+IF(Left_Against_Wall,0,Left_Overhang)+IF(Right_Against_Wall,0,Right_Overhang)',
            [dim_x, Left_Against_Wall, Right_Against_Wall, Left_Overhang, Right_Overhang])
        self.countertop.dim_y('dim_y-Front_Overhang-Back_Overhang', [dim_y, Front_Overhang, Back_Overhang])

        if countertop_type in ("Melamine", "HPL"):
            self.countertop.get_prompt("Exposed Left").set_formula("IF(Left_Against_Wall,False,True)", [Left_Against_Wall])
            self.countertop.get_prompt("Exposed Right").set_formula("IF(Right_Against_Wall,False,True)", [Right_Against_Wall])
            self.countertop.get_prompt("Exposed Back").set_formula("Exposed_Back", [Exposed_Back])

            for child in self.countertop.obj_bp.children:
                if child.snap.type_mesh == 'CUTPART':
                    for mat_slot in child.snap.material_slots:
                        mat_slot.pointer_name = "Closet_Part_Edges"

        self.add_to_wall_collection(self.countertop.obj_bp)

        return self.countertop

    def add_base_assembly(self):
        self.add_prompt("Cleat Width", 'DISTANCE', sn_unit.inch(2.5))
        Width = self.obj_x.snap.get_var('location.x', 'Width')
        Depth = self.obj_y.snap.get_var('location.y', 'Depth')
        Height = self.get_prompt('Toe Kick Height').get_var("Height")
        Cleat_Width = self.get_prompt('Cleat Width').get_var()
        Toe_Kick_Thickness = self.get_prompt('Toe Kick Thickness').get_var()
        Toe_Kick_Setback = self.get_prompt('Toe Kick Setback').get_var()
        # Extend_Left_Amount = self.get_prompt('Extend Left Amount').get_var()
        # Extend_Right_Amount = self.get_prompt('Extend Right Amount').get_var()
        # Extend_Depth_Amount = self.get_prompt('Extend Depth Amount').get_var()
        Add_TK_Skin = self.get_prompt('Add TK Skin').get_var()
        TK_Skin_Thickness = self.get_prompt('TK Skin Thickness').get_var()
        LAW = self.get_prompt('Left Against Wall').get_var('LAW')
        RAW = self.get_prompt('Right Against Wall').get_var('RAW')
        Back_Against_Wall = self.get_prompt('Back Against Wall').get_var()
        Add_Capping_Base = self.get_prompt('Add Capping Base').get_var()
        
        toe_kick_front = common_parts.add_toe_kick(self)
        toe_kick_front.set_name("Toe Kick Front")
        toe_kick_front.obj_bp.snap.comment_2 = "1034"
        false_exp =\
            "Width-(Toe_Kick_Thickness*3)"+\
            "-IF(Add_TK_Skin,IF(LAW,0,TK_Skin_Thickness)+IF(RAW,0,TK_Skin_Thickness),0)"+\
            "+IF(Add_Capping_Base,Toe_Kick_Thickness,0)"
        toe_kick_front.dim_x(
            "IF(Width>INCH(98.25),INCH(96),"+false_exp+")",
            [Width, Toe_Kick_Thickness, LAW, RAW, Add_TK_Skin, TK_Skin_Thickness, Add_Capping_Base])
        toe_kick_front.dim_y('-Height',[Height])
        toe_kick_front.dim_z('Toe_Kick_Thickness',[Toe_Kick_Thickness])
        toe_kick_front.loc_x(
            "(Toe_Kick_Thickness*1.5)"
            "+IF(Add_TK_Skin,IF(LAW,0,TK_Skin_Thickness),0)"
            "-IF(Add_Capping_Base,Toe_Kick_Thickness*0.5,0)",
            [Toe_Kick_Thickness, Add_TK_Skin, LAW, TK_Skin_Thickness, Add_Capping_Base])
        toe_kick_front.loc_y('Depth+IF(Add_Capping_Base,0,Toe_Kick_Setback)',[Depth,Toe_Kick_Setback, Add_Capping_Base])
        toe_kick_front.rot_x(value=math.radians(-90))
        
        toe_kick_back = common_parts.add_toe_kick(self)
        toe_kick_back.set_name("Toe Kick Back")
        if(self.is_double_sided):
            toe_kick_back.loc_y('IF(Add_Capping_Base,0,-Toe_Kick_Setback)',[Toe_Kick_Setback, Add_Capping_Base])
        else:
            toe_kick_back.loc_y('Toe_Kick_Thickness-IF(Add_TK_Skin,TK_Skin_Thickness,0)',[Toe_Kick_Thickness, Add_TK_Skin, TK_Skin_Thickness, Add_Capping_Base])
        
        toe_kick_back.obj_bp.snap.comment_2 = "1034"
        toe_kick_back.dim_x(
            "IF(Width>INCH(98.25),INCH(96),"+false_exp+")",
            [Width, Toe_Kick_Thickness, LAW, RAW, Add_TK_Skin, TK_Skin_Thickness, Add_Capping_Base])
        toe_kick_back.dim_y('-Height', [Height])
        toe_kick_back.dim_z('-Toe_Kick_Thickness',[Toe_Kick_Thickness])
        toe_kick_back.loc_x(
            '(Toe_Kick_Thickness*1.5)'
            '+IF(Add_TK_Skin,IF(LAW,0,TK_Skin_Thickness),0)'
            '-IF(Add_Capping_Base,Toe_Kick_Thickness*0.5,0)',
            [Toe_Kick_Thickness, Add_TK_Skin, LAW, TK_Skin_Thickness, Add_Capping_Base])
        toe_kick_back.rot_x(value=math.radians(-90))
      
        # Left end cap
        left_toe_kick = common_parts.add_toe_kick_end_cap(self)
        if self.is_double_sided:
            left_toe_kick.dim_y('-Depth-IF(Add_Capping_Base,0,(Toe_Kick_Setback*2))',[Depth,Toe_Kick_Setback, Add_Capping_Base])
            left_toe_kick.loc_y('Depth+IF(Add_Capping_Base,0,Toe_Kick_Setback)',[Depth, Toe_Kick_Setback, Add_Capping_Base])
        else:
            left_toe_kick.dim_y(
                '-Depth-IF(Add_Capping_Base,0,Toe_Kick_Setback)+Toe_Kick_Thickness-IF(Add_TK_Skin,TK_Skin_Thickness,0)',
                [Depth, Toe_Kick_Setback, Toe_Kick_Thickness, Add_TK_Skin, TK_Skin_Thickness, Add_Capping_Base])
            left_toe_kick.loc_y('Depth+IF(Add_Capping_Base,0,Toe_Kick_Setback)',[Depth, Toe_Kick_Setback, TK_Skin_Thickness, Add_Capping_Base])

        left_toe_kick.dim_x('-Height',[Height])
        left_toe_kick.dim_z('Toe_Kick_Thickness',[Toe_Kick_Thickness])
        left_toe_kick.loc_x(
            '(Toe_Kick_Thickness/2)'
            '+IF(Add_TK_Skin,IF(LAW,0,TK_Skin_Thickness),0)'
            '-IF(Add_Capping_Base,Toe_Kick_Thickness/2,0)',
            [Toe_Kick_Thickness, Add_TK_Skin, TK_Skin_Thickness, LAW, Add_Capping_Base])
        left_toe_kick.rot_y(value=math.radians(90))
        
        # Right end cap
        right_toe_kick = common_parts.add_toe_kick_end_cap(self)
        if self.is_double_sided:
            right_toe_kick.loc_y('Depth+IF(Add_Capping_Base,0,Toe_Kick_Setback)',[Depth, Toe_Kick_Setback, Add_Capping_Base])
            right_toe_kick.dim_y('-Depth-IF(Add_Capping_Base,0,(Toe_Kick_Setback*2))',[Depth,Toe_Kick_Setback,Toe_Kick_Thickness, Add_Capping_Base])
        else:
            right_toe_kick.loc_y('Depth+IF(Add_Capping_Base,0,Toe_Kick_Setback)',[Depth, Toe_Kick_Setback, Add_Capping_Base])
            right_toe_kick.dim_y(
                '-Depth-IF(Add_Capping_Base,0,Toe_Kick_Setback)+Toe_Kick_Thickness-IF(Add_TK_Skin,TK_Skin_Thickness,0)',
                [Depth, Toe_Kick_Setback, Toe_Kick_Thickness, Add_TK_Skin, TK_Skin_Thickness, Add_Capping_Base])

        right_toe_kick.dim_x('Height',[Height])
        right_toe_kick.dim_z('Toe_Kick_Thickness',[Toe_Kick_Thickness])
        right_toe_kick.loc_x('IF(Width>INCH(98.25),'
            'INCH(98.25)-(Toe_Kick_Thickness/2)-IF(Add_TK_Skin,IF(RAW,0,TK_Skin_Thickness),0),'
            'Width-(Toe_Kick_Thickness/2)-IF(Add_TK_Skin,IF(RAW,0,TK_Skin_Thickness),0))'
            '+IF(Add_Capping_Base,Toe_Kick_Thickness/2,0)',
            [Width, Toe_Kick_Thickness, Add_TK_Skin, RAW, TK_Skin_Thickness, Add_Capping_Base])
        right_toe_kick.rot_x(value=math.radians(90))
        right_toe_kick.rot_y(value=math.radians(-90))
        right_toe_kick.rot_z(value=math.radians(-90))
        
        toe_kick_stringer = common_parts.add_toe_kick_stringer(self)
        false_exp =\
            "Width-(Toe_Kick_Thickness*3)"+\
            "-IF(Add_TK_Skin,IF(LAW,0,TK_Skin_Thickness),0)"+\
            "-IF(Add_TK_Skin,IF(RAW,0,TK_Skin_Thickness),0)"+\
            "+IF(Add_Capping_Base,Toe_Kick_Thickness,0)"
        toe_kick_stringer.dim_x(
            "IF(Width>INCH(98.25),INCH(96),"+false_exp+")",
            [Width, Toe_Kick_Thickness, LAW, RAW, Add_TK_Skin, TK_Skin_Thickness, Add_Capping_Base])
        toe_kick_stringer.dim_y('Cleat_Width',[Cleat_Width])
        toe_kick_stringer.dim_z('Toe_Kick_Thickness',[Toe_Kick_Thickness])
        toe_kick_stringer.loc_x(
            '(Toe_Kick_Thickness*1.5)+IF(Add_TK_Skin,IF(LAW,0,TK_Skin_Thickness),0)-IF(Add_Capping_Base,Toe_Kick_Thickness*0.5,0)',
            [Toe_Kick_Thickness, Add_TK_Skin, LAW, TK_Skin_Thickness, Add_Capping_Base])
        toe_kick_stringer.loc_y('Depth+Toe_Kick_Thickness+IF(Add_Capping_Base,0,Toe_Kick_Setback)',[Depth,Toe_Kick_Thickness,Toe_Kick_Setback, Add_Capping_Base])
        toe_kick_stringer.loc_z('Height-Toe_Kick_Thickness',[Height,Toe_Kick_Thickness])

        toe_kick_stringer = common_parts.add_toe_kick_stringer(self)
        if self.is_double_sided:
            toe_kick_stringer.loc_y('-IF(Add_Capping_Base,0,Toe_Kick_Setback)-Toe_Kick_Thickness', [Toe_Kick_Setback, Toe_Kick_Thickness, Add_Capping_Base])
        else:
            toe_kick_stringer.loc_y('IF(Add_TK_Skin,-TK_Skin_Thickness,0)', [Add_TK_Skin, TK_Skin_Thickness])
        false_exp =\
            "Width-(Toe_Kick_Thickness*3)"+\
            "-IF(Add_TK_Skin,IF(LAW,0,TK_Skin_Thickness),0)"+\
            "-IF(Add_TK_Skin,IF(RAW,0,TK_Skin_Thickness),0)"+\
            "+IF(Add_Capping_Base,Toe_Kick_Thickness,0)"
        toe_kick_stringer.dim_x(
            "IF(Width>INCH(98.25),INCH(96),"+false_exp+")",
            [Width, Toe_Kick_Thickness, LAW, RAW, Add_TK_Skin, TK_Skin_Thickness, Add_Capping_Base])
        toe_kick_stringer.dim_y('-Cleat_Width', [Cleat_Width])
        toe_kick_stringer.dim_z('Toe_Kick_Thickness',[Toe_Kick_Thickness])
        toe_kick_stringer.loc_x(
            '(Toe_Kick_Thickness*1.5)+IF(Add_TK_Skin,IF(LAW,0,TK_Skin_Thickness),0)-IF(Add_Capping_Base,Toe_Kick_Thickness*0.5,0)',
            [Toe_Kick_Thickness, Add_TK_Skin, LAW, TK_Skin_Thickness, Add_Capping_Base])

        front_tk_skin = common_parts.add_toe_kick_skin(self)
        front_tk_skin.dim_x('IF(Width>INCH(98.25),'
            'INCH(98.25)-(Toe_Kick_Thickness),'
            'Width-(Toe_Kick_Thickness))',
            [Width, Toe_Kick_Thickness, TK_Skin_Thickness, RAW, LAW])
        front_tk_skin.dim_y('-Height',[Height])
        front_tk_skin.dim_z('TK_Skin_Thickness',[TK_Skin_Thickness])
        front_tk_skin.loc_x('(Toe_Kick_Thickness*1.5)-Toe_Kick_Thickness',[Toe_Kick_Thickness,TK_Skin_Thickness,LAW])
        front_tk_skin.loc_y('Depth+Toe_Kick_Setback-TK_Skin_Thickness',[Depth,Toe_Kick_Setback,TK_Skin_Thickness])
        front_tk_skin.rot_x(value=math.radians(-90))
        front_tk_skin.get_prompt("Hide").set_formula('IF(Add_TK_Skin,False,True)',[Add_TK_Skin])

        back_tk_skin = common_parts.add_toe_kick_skin(self)
        back_tk_skin.dim_x('IF(Width>INCH(98.25),'
            'INCH(98.25)-(Toe_Kick_Thickness)-IF(LAW,TK_Skin_Thickness,0)-IF(RAW,TK_Skin_Thickness,0),'
            'Width-(Toe_Kick_Thickness)-IF(LAW,TK_Skin_Thickness,0)-IF(RAW,TK_Skin_Thickness,0))',
            [Width, Toe_Kick_Thickness, TK_Skin_Thickness, LAW, RAW])
        back_tk_skin.dim_y('-Height', [Height])
        back_tk_skin.dim_z('-TK_Skin_Thickness',[TK_Skin_Thickness])
        back_tk_skin.loc_x(
            '(Toe_Kick_Thickness*1.5)-Toe_Kick_Thickness+IF(LAW,TK_Skin_Thickness,0)',
            [Toe_Kick_Thickness, TK_Skin_Thickness, LAW])

        if self.is_double_sided:
            back_tk_skin.loc_y('-Toe_Kick_Setback+TK_Skin_Thickness', [Toe_Kick_Setback, TK_Skin_Thickness])
        else:
            back_tk_skin.loc_y('IF(Add_TK_Skin,Toe_Kick_Thickness,0)', [Add_TK_Skin, Toe_Kick_Thickness])

        back_tk_skin.rot_x(value=math.radians(-90))
        back_tk_skin.get_prompt("Hide").set_formula('IF(Add_TK_Skin,False,True)',[Add_TK_Skin]) 
        
        left_tk_skin = common_parts.add_toe_kick_skin(self)
        if(self.is_double_sided):
            left_tk_skin.dim_x('-Depth-(Toe_Kick_Setback*2)',[Depth,Toe_Kick_Setback])
            left_tk_skin.loc_y('-Toe_Kick_Setback',[Toe_Kick_Setback])
        else:
            left_tk_skin.dim_x('-Depth-Toe_Kick_Setback+Toe_Kick_Thickness',[Depth,Toe_Kick_Setback,Toe_Kick_Thickness])
            left_tk_skin.loc_y('Toe_Kick_Thickness',[Toe_Kick_Thickness])

        left_tk_skin.dim_y('-Height',[Height])
        left_tk_skin.dim_z('TK_Skin_Thickness',[TK_Skin_Thickness])
        left_tk_skin.loc_x('(Toe_Kick_Thickness/2)',[Toe_Kick_Thickness,TK_Skin_Thickness])
        left_tk_skin.rot_x(value=math.radians(-90))
        left_tk_skin.rot_z(value=math.radians(-90))  
        left_tk_skin.get_prompt("Hide").set_formula(
            'IF(LAW,True,IF(Add_TK_Skin,False,True))',
            [Add_TK_Skin, LAW])

        right_tk_skin = common_parts.add_toe_kick_skin(self)
        if(self.is_double_sided):
            right_tk_skin.dim_x('-Depth-(Toe_Kick_Setback*2)',[Depth,Toe_Kick_Setback])
            right_tk_skin.loc_y('-Toe_Kick_Setback',[Toe_Kick_Setback])
        else:
            right_tk_skin.dim_x('-Depth-Toe_Kick_Setback+Toe_Kick_Thickness',[Depth,Toe_Kick_Setback,Toe_Kick_Thickness])
            right_tk_skin.loc_y('Toe_Kick_Thickness',[Toe_Kick_Thickness])

        right_tk_skin.dim_y('Height',[Height])
        right_tk_skin.dim_z('TK_Skin_Thickness',[TK_Skin_Thickness])
        right_tk_skin.loc_x('IF(Width>INCH(98.25),'
            'INCH(98.25)-(Toe_Kick_Thickness/2),'
            'Width-(Toe_Kick_Thickness/2))',
            [Width,Toe_Kick_Thickness,TK_Skin_Thickness])
        right_tk_skin.rot_x(value=math.radians(90))
        right_tk_skin.rot_z(value=math.radians(-90))
        right_tk_skin.get_prompt("Hide").set_formula(
            'IF(RAW,True,IF(Add_TK_Skin,False,True))',
            [Add_TK_Skin, RAW])

        front_tk_capping_base = common_parts.add_toe_kick_capping_base(self)
        front_tk_capping_base.dim_x(
            'IF(Width>INCH(98.25),'
            'INCH(98.25)-(Toe_Kick_Thickness),'
            'Width+IF(LAW,0,Toe_Kick_Thickness)+IF(RAW,0,Toe_Kick_Thickness))',
            [Width,Toe_Kick_Thickness,TK_Skin_Thickness, LAW, RAW])
        front_tk_capping_base.dim_y('-Height-Toe_Kick_Thickness/3',[Height, Toe_Kick_Thickness])
        front_tk_capping_base.dim_z('Toe_Kick_Thickness',[Toe_Kick_Thickness])
        front_tk_capping_base.loc_x('IF(LAW,0,-Toe_Kick_Thickness)',[Toe_Kick_Thickness, LAW])
        front_tk_capping_base.loc_y('Depth-Toe_Kick_Thickness',[Depth, Toe_Kick_Thickness])
        front_tk_capping_base.rot_x(value=math.radians(-90))
        front_tk_capping_base.get_prompt("Hide").set_formula('IF(Add_Capping_Base,False,True)',[Add_Capping_Base])

        back_tk_capping_base = common_parts.add_toe_kick_capping_base(self)
        back_tk_capping_base.dim_x('IF(Width>INCH(98.25),'
            'INCH(98.25)-(Toe_Kick_Thickness),'
            'Width+IF(LAW,0,Toe_Kick_Thickness)+IF(RAW,0,Toe_Kick_Thickness))',
            [Width, Toe_Kick_Thickness, LAW, RAW])
        back_tk_capping_base.dim_y('-Height-Toe_Kick_Thickness/3', [Height, Toe_Kick_Thickness])
        back_tk_capping_base.dim_z('-Toe_Kick_Thickness',[Toe_Kick_Thickness])
        back_tk_capping_base.loc_x('IF(LAW,0,-Toe_Kick_Thickness)',[Toe_Kick_Thickness, LAW])

        if self.is_double_sided:
            back_tk_capping_base.loc_y('Toe_Kick_Thickness', [Toe_Kick_Thickness])
        else:
            back_tk_capping_base.loc_y('Toe_Kick_Thickness*2', [Toe_Kick_Thickness])

        back_tk_capping_base.rot_x(value=math.radians(-90))
        back_tk_capping_base.get_prompt("Hide").set_formula('IF(Add_Capping_Base,IF(Back_Against_Wall,True,False),True)',[Add_Capping_Base, Back_Against_Wall]) 
        
        left_tk_capping_base = common_parts.add_toe_kick_capping_base(self)
        if(self.is_double_sided):
            left_tk_capping_base.dim_x('-Depth+Toe_Kick_Thickness*2-IF(Back_Against_Wall,Toe_Kick_Thickness,0)',[Depth,Toe_Kick_Thickness, Back_Against_Wall])
            left_tk_capping_base.loc_y('Toe_Kick_Thickness-IF(Back_Against_Wall,Toe_Kick_Thickness,0)',[Toe_Kick_Thickness, Back_Against_Wall])
        else:
            left_tk_capping_base.dim_x('-Depth+Toe_Kick_Thickness*3-IF(Back_Against_Wall,Toe_Kick_Thickness,0)',[Depth,Toe_Kick_Thickness, Back_Against_Wall])
            left_tk_capping_base.loc_y('Toe_Kick_Thickness*2-IF(Back_Against_Wall,Toe_Kick_Thickness,0)',[Toe_Kick_Thickness, Back_Against_Wall])

        left_tk_capping_base.dim_y('-Height-Toe_Kick_Thickness/3',[Height, Toe_Kick_Thickness])
        left_tk_capping_base.dim_z('Toe_Kick_Thickness',[Toe_Kick_Thickness])
        left_tk_capping_base.loc_x('-Toe_Kick_Thickness',[Toe_Kick_Thickness])
        left_tk_capping_base.rot_x(value=math.radians(-90))
        left_tk_capping_base.rot_z(value=math.radians(-90))  
        left_tk_capping_base.get_prompt("Hide").set_formula('IF(Add_Capping_Base,IF(LAW,True,False),True)',[Add_Capping_Base, LAW])

        right_tk_capping_base = common_parts.add_toe_kick_capping_base(self)
        if(self.is_double_sided):
            right_tk_capping_base.dim_x('-Depth+Toe_Kick_Thickness*2-IF(Back_Against_Wall,Toe_Kick_Thickness,0)',[Depth,Toe_Kick_Thickness, Back_Against_Wall])
            right_tk_capping_base.loc_y('Toe_Kick_Thickness-IF(Back_Against_Wall,Toe_Kick_Thickness,0)',[Toe_Kick_Thickness, Back_Against_Wall])
        else:
            right_tk_capping_base.dim_x('-Depth+Toe_Kick_Thickness*3-IF(Back_Against_Wall,Toe_Kick_Thickness,0)',[Depth,Toe_Kick_Thickness,Back_Against_Wall])
            right_tk_capping_base.loc_y('Toe_Kick_Thickness*2-IF(Back_Against_Wall,Toe_Kick_Thickness,0)',[Toe_Kick_Thickness, Back_Against_Wall])

        right_tk_capping_base.dim_y('Height+Toe_Kick_Thickness/3',[Height, Toe_Kick_Thickness])
        right_tk_capping_base.dim_z('Toe_Kick_Thickness',[Toe_Kick_Thickness])
        right_tk_capping_base.loc_x('IF(Width>INCH(98.25),'
            'INCH(98.25),'
            'Width+Toe_Kick_Thickness)',
            [Width,Toe_Kick_Thickness])
        right_tk_capping_base.rot_x(value=math.radians(90))
        right_tk_capping_base.rot_z(value=math.radians(-90))
        right_tk_capping_base.get_prompt("Hide").set_formula('IF(Add_Capping_Base,IF(RAW,True,False),True)',[Add_Capping_Base, RAW])

    def add_opening_widths_calculator(self):
        calc_distance_obj = self.add_empty('Calc Distance Obj')
        calc_distance_obj.empty_display_size = .001

        self.calculator = self.obj_prompts.snap.add_calculator(
            "Opening Widths Calculator",
            calc_distance_obj)

    def set_calculator_distance(self):
        Product_Width = self.obj_x.snap.get_var('location.x', 'Product_Width')
        Panel_Thickness = self.get_prompt('Panel Thickness').get_var()
        self.calculator.set_total_distance(
            "Product_Width-Panel_Thickness*(" + str(self.opening_qty) +"+1)",
            [Product_Width, Panel_Thickness])
    
    def calculate_opening_widths(self):
        calculator = self.get_calculator('Opening Widths Calculator')
        if calculator:
            bpy.context.view_layer.update()
            calculator.calculate()        

    def update(self):
        self.obj_x.location.x = self.width
        self.obj_z.location.z = self.height
        self.obj_y.location.y = -self.depth

        self.obj_bp["IS_BP_CLOSET"] = True
        self.obj_bp["IS_BP_ISLAND"] = True
        self.obj_bp["ID_PROMPT"] = self.id_prompt 
        self.obj_y['IS_MIRROR'] = True
        self.obj_bp.snap.type_group = self.type_assembly
        self.set_prompts()

        self.calculate_opening_widths()
        super().update()

    def draw(self):
        defaults = bpy.context.scene.sn_closets.closet_defaults
        self.create_assembly()
        self.obj_bp['product_type'] = "Closet"
        product_props = self.obj_bp.sn_closets
        product_props.is_island = True
        
        if defaults.export_subassemblies:
            self.obj_bp.snap.export_product_subassemblies = True

        #ORDER OF PROMPTS ARE IMPORTANT
        self.add_opening_widths_calculator()
        self.add_opening_prompts()
        common_prompts.add_thickness_prompts(self) #MUST BE CALLED BEFORE add_island_prompts()
        self.set_calculator_distance()
        self.add_island_prompts()
        common_prompts.add_toe_kick_prompts(self,prompt_tab=1)
        common_prompts.add_countertop_prompts(self)         
        
        self.add_base_assembly()
        self.add_sides()
        self.add_countertop()
        if not self.is_double_sided:
            self.add_thick_back()
        panel = None
        self.add_shelf(1,panel,is_top=True)
        self.add_shelf(1,panel,is_top=False)
    
        # self.add_toe_kick(1,panel)
        self.add_closet_opening(1,panel)
        self.add_closet_opening(1,panel,is_rear=True)
        if self.is_double_sided:
            # self.add_toe_kick(1, panel, is_rear=True)
            self.add_double_sided_back(1, panel)
            #self.add_shelf(1,panel,is_top=True,is_rear=True)
            #self.add_shelf(1,panel,is_top=False,is_rear=True)                
        
        for i in range(2,self.opening_qty+1):
            panel = self.add_panel(i,panel)
            panel.obj_bp['PARTITION_NUMBER'] = (i - 1)
            self.add_shelf(i,panel,is_top=True)
            self.add_shelf(i,panel,is_top=False)
            # self.add_toe_kick(i,panel)
            self.add_closet_opening(i,panel)
            if self.is_double_sided:
                # self.add_toe_kick(i, panel, is_rear=True)
                self.add_double_sided_back(i, panel)
                self.add_closet_opening(i,panel,is_rear=True)
        
        self.update()
                

class PROMPTS_Opening_Starter(sn_types.Prompts_Interface):
    bl_idname = "sn_closets.island_openings"
    bl_label = "Island Prompts" 
    bl_options = {'UNDO'}
    
    object_name: StringProperty(name="Object Name")
    
    tabs: EnumProperty(name="Tabs",
                        items=[('OPENINGS','Opening Sizes','Show the Width x Height x Depth for each opening'),
                               ('CONSTRUCTION','Construction Options','Show Additional Construction Options')],
                        default = 'OPENINGS')
    
    current_location: FloatProperty(name="Current Location", default=0,subtype='DISTANCE')
    left_offset: FloatProperty(name="Left Offset", default=0,subtype='DISTANCE')
    right_offset: FloatProperty(name="Right Offset", default=0,subtype='DISTANCE')
    product_width: FloatProperty(name="Product Width", default=0,subtype='DISTANCE')    
    
    width: FloatProperty(name="Width", unit='LENGTH', precision=4)
    depth: FloatProperty(name="Depth", unit='LENGTH', precision=4)
    height: EnumProperty(name="Height",
                          items=common_lists.PANEL_HEIGHTS,
                          default = '2131',
                          update=update_closet_height)

    countertop_type_ppt = None
    prev_countertop_type = 0
    countertop_type: EnumProperty(
        name="Countertop Type",
        items=[
            ('0', 'Melamine', 'Melamine'),
            ('1', 'Custom', 'Custom'),
            ('2', 'Granite', 'Granite'),
            ('3', 'HPL', 'HPL'),
            ("4", "Quartz", "Quartz"),
            ("5", "Standard Quartz", "Standard Quartz"),
            ("6", "Wood", "Wood")],
        default='0')
    
    hpl_edge_type: EnumProperty(
        name="Countertop Edge Type",
        items=[
            ('0', 'Ora', 'Ora'),
            ('1', 'Futura', 'Futura'),
            ('2', 'Nova', 'Nova'),
            ('3', 'Tempo', 'Tempo'),
            ('4', 'Flat', 'Flat')],
        default='0')

    stone_edge_type: EnumProperty(
        name="Countertop Edge Type",
        items=[
            ('0', 'Miter', 'Miter'),
            ('1', 'STD Eased', 'STD Eased'),
            ('2', 'Bullnose', 'Bullnose'),
            ('3', 'Demi Bullnose', 'Demi Bullnose'),
            ('4', 'Crescent', 'Crescent'),
            ('5', 'Bevel', 'Bevel'),
            ('6', 'Euro', 'Euro'),
            ('7', 'Ogee', 'Ogee'),
            ('8', 'Ogee Bullnose', 'Ogee Bullnose'),
            ('9', 'Double Bevel', 'Double Bevel'),
            ('10', 'Chisel', 'Chisel'),
            ('11', 'Miter 4"', 'Miter 4"'),
            ('12', 'Miter 6"', 'Miter 6"'),
            ('13', 'Miter Waterfall', 'Miter Waterfall')],
        default='0')

    painted_edge_type: EnumProperty(
        name="Countertop Edge Type",
        items=[
            ('0', 'Solid Flat', 'Solid Flat'),
            ('1', 'Solid Round', 'Solid Round'),
            ('2', 'Solid Ogee', 'Solid Ogee'),
            ('3', 'Applied Flat', 'Applied Flat'),
            ('4', 'Applied Round', 'Applied Round'),
            ('5', 'Applied Ogee', 'Applied Ogee')],
        default='0')
    
    stained_edge_type: EnumProperty(
        name="Countertop Edge Type",
        items=[
            ('0', 'Dolce', 'Dolce'),
            ('1', 'Solid Flat Applied', 'Solid Flat Applied'),
            ('2', 'Solid Round Applied', 'Solid Round Applied'),
            ('3', 'Solid Ogee Applied', 'Solid Ogee Applied'),
            ('4', 'Alder Miter', 'Alder Miter')],
        default='0')
    
    hpl_edge_type_prompt = None
    stone_edge_type_prompt = None
    painted_edge_type_prompt = None
    stained_edge_type_prompt = None
    is_painted = False
    is_stained = False
    no_countertop = False
    
    product = None
    countertop = None
    inserts = []
    splitters = []

    def reset_variables(self):
        self.tabs = 'OPENINGS'
        self.product = None
        self.countertop = None
        self.splitters = []

    def update_placement(self, context):
        self.product.obj_x.location.x = self.width
        self.run_calculators(self.product.obj_bp)

    def get_part_mesh(self, obj_bp):
        for obj in obj_bp.children:
            if obj.type == 'MESH':
                return obj

    def update_edges(self):
        material_color = bpy.context.scene.closet_materials.materials.get_mat_color()

        for child in self.product.obj_bp.children:
            if 'IS_BP_PANEL' in child:
                assembly = sn_types.Assembly(child)
                assembly_width = assembly.obj_x.location.x
                panel_mesh = self.get_part_mesh(assembly.obj_bp)
                max_width_ppt = self.product.get_prompt('Material Max Width')
                mat_name = material_color.name

                if max_width_ppt:
                    if "S " in mat_name or "CL " in mat_name:
                        max_width = sn_unit.inch(80)
                    else:
                        max_width = sn_unit.inch(48)
                    if assembly_width > max_width:
                        mapping = 'UV'   
                    else:
                        mapping = 'BOX'
                    max_width_ppt.set_value(max_width)
                    panel_mesh.snap.material_mapping = mapping

    def update_countertop_type(self, context):
        mat_props = context.scene.closet_materials
        countertop_type = 0
        ct_type = mat_props.countertops.get_type()

        # COUNTERTOP_HPL is used for "Custom"
        countertops = (
            "COUNTERTOP_MELAMINE", "COUNTERTOP_HPL", "COUNTERTOP_GRANITE",
            "COUNTERTOP_HPL", "COUNTERTOP_QUARTZ", "COUNTERTOP_STANDARD_QUARTZ", "COUNTERTOP_WOOD")        

        if self.countertop_type_ppt:
            self.prev_countertop_type = self.countertop_type_ppt.get_value()
            self.countertop_type_ppt.set_value(int(self.countertop_type))
        
        no_countertop = self.product.get_prompt("No Countertop")
        if no_countertop:
            if self.no_countertop != no_countertop.get_value():
                self.countertop = self.product.add_countertop()
                self.product.update()
                self.no_countertop = no_countertop.get_value()

        if self.prev_countertop_type != int(self.countertop_type):
            self.countertop = self.product.add_countertop()
            self.product.update()
            countertop_type = self.countertop_type_ppt.get_value()

            # Set unique material status
            for child in self.product.obj_bp.children:
                if countertops[countertop_type] in child or (self.countertop_type == "5" and "COUNTERTOP_QUARTZ" in child):
                    use_unique = mat_props.ct_type_index != countertop_type
                    child.sn_closets.use_unique_material = use_unique
                    bpy.context.view_layer.objects.active = child
                    child.select_set(True)

                    # Toggle properties panel
                    if use_unique:
                        context_copy = context.copy()
                        for area in context.screen.areas:
                            if area.type == 'VIEW_3D':
                                context_copy['area'] = area
                                # Only toggle if not already open
                                for region in area.regions:
                                    if region.type == 'UI':
                                        if region.width == 1:
                                            bpy.ops.wm.context_toggle(context_copy,data_path="space_data.show_region_ui")      
        self.set_edge_type_prompts()      

    def check(self, context):
        self.update_edges()
        self.update_countertop_type(context)
        self.update_placement(context)
        self.run_calculators(self.product.obj_bp)
        closet_props.update_render_materials(self, context)

        toe_kick_height = self.product.get_prompt("Toe Kick Height").distance_value
        if toe_kick_height <= inch(3):
            self.product.get_prompt("Toe Kick Height").set_value(inch(3))
            bpy.ops.snap.log_window('INVOKE_DEFAULT',
                                    message="Minimum Toe Kick Height is 3\"",
                                    icon="ERROR")

        depth_1 = self.product.get_prompt("Depth 1")
        if not depth_1:
            self.product.obj_y.location.y = -self.depth

        return True

    def set_product_defaults(self):
        self.product.obj_bp.location.x = self.selected_location + self.left_offset
        self.product.obj_x.location.x = self.default_width - (self.left_offset + self.right_offset)
    
    def set_edge_type_prompts(self):
        if self.hpl_edge_type_prompt:
            self.hpl_edge_type_prompt.set_value(int(self.hpl_edge_type))
        if self.stone_edge_type_prompt:
            self.stone_edge_type_prompt.set_value(int(self.stone_edge_type))
        if self.painted_edge_type_prompt:
            self.painted_edge_type_prompt.set_value(int(self.painted_edge_type))
        if self.stained_edge_type_prompt:
            self.stained_edge_type_prompt.set_value(int(self.stained_edge_type))

    def execute(self, context):
        obj_list = []
        obj_list = sn_utils.get_child_objects(self.product.obj_bp, obj_list)
        for obj in obj_list:
            if obj.type == 'EMPTY':
                obj.hide_set(True)
        if self.product.obj_bp:
            if self.product.obj_bp.name in context.scene.objects:
                self.run_calculators(self.product.obj_bp)
        return {'FINISHED'}

    def set_default_heights(self):
        opening_height = round(sn_unit.meter_to_millimeter(self.product.obj_z.location.z),0)
        for index, height in enumerate(common_lists.PANEL_HEIGHTS):
            if not opening_height >= int(height[0]):
                exec('self.height = common_lists.PANEL_HEIGHTS[index - 1][0]')                                                                                                                                                                                                        
                break

    def get_assemblies(self, context):
        self.calculators = []
        opening_widths_calculator = self.product.get_calculator('Opening Widths Calculator')
        if opening_widths_calculator:
            self.calculators.append(opening_widths_calculator)

        for child in self.product.obj_bp.children:
            if "IS_BP_SPLITTER" in child and child["IS_BP_SPLITTER"]:
                assy = sn_types.Assembly(child)
                calculator = assy.get_calculator('Opening Heights Calculator')
                if assy:
                    self.splitters.append(assy)
                if calculator:
                    self.calculators.append(calculator)

    def invoke(self,context,event):
        self.reset_variables()
        bp = sn_utils.get_closet_bp(context.object)
        self.product = Closet_Island_Carcass(obj_bp=bp)
        self.get_assemblies(context)
        self.run_calculators(self.product.obj_bp)

        if self.product.obj_bp:
            self.width = math.fabs(self.product.obj_x.location.x)
            new_list = []
            self.inserts = sn_utils.get_insert_bp_list(self.product.obj_bp,new_list)
            self.depth = math.fabs(self.product.obj_y.location.y)
            self.set_default_heights()
            self.countertop_type_ppt = self.product.get_prompt("Countertop Type")

            if self.countertop_type_ppt:
                self.countertop_type = str(self.countertop_type_ppt.get_value())
            
            self.set_edge_type_enums()
            self.get_wood(context)

        return super().invoke(context, event, width=500)
    
    def set_edge_type_enums(self):
        self.hpl_edge_type_prompt = self.product.get_prompt("HPL Edge Type")
        self.stone_edge_type_prompt = self.product.get_prompt("Stone Edge Type")
        self.painted_edge_type_prompt = self.product.get_prompt("Painted Edge Type")
        self.stained_edge_type_prompt = self.product.get_prompt("Stained Edge Type")
        if self.hpl_edge_type_prompt:
            self.hpl_edge_type = str(self.hpl_edge_type_prompt.combobox_index)
        if self.stone_edge_type_prompt:
            self.stone_edge_type = str(self.stone_edge_type_prompt.combobox_index)
        if self.painted_edge_type_prompt:
            self.painted_edge_type = str(self.painted_edge_type_prompt.combobox_index)
        if self.stained_edge_type_prompt:
            self.stained_edge_type = str(self.stained_edge_type_prompt.combobox_index)
    
    def get_wood(self, context):
        for child in self.product.obj_bp.children:
            if "Wood Countertop" in child.name:
                if child.sn_closets.use_unique_material:
                    if child.sn_closets.wood_countertop_types == 'Wood Painted MDF':
                        self.is_painted = True
                        self.is_stained = False
                    elif child.sn_closets.wood_countertop_types == 'Wood Stained Veneer':
                        self.is_painted = False
                        self.is_stained = True
                    else:
                        self.is_painted = False
                        self.is_stained = False
                else:
                    ct_type = context.scene.closet_materials.countertops.get_type()
                    if ct_type.name == 'Wood':
                        ct_mfg = ct_type.get_mfg()
                        if ct_mfg.name == 'Wood Painted MDF':
                            self.is_painted = True
                            self.is_stained = False
                        elif ct_mfg.name == 'Wood Stained Veneer':
                            self.is_painted = False
                            self.is_stained = True
                        else:
                            self.is_painted = False
                            self.is_stained = False
                    else:
                        self.is_painted = False
                        self.is_stained = False

    def convert_to_height(self,number):
        for index, height in enumerate(common_lists.PANEL_HEIGHTS):
            if not number * 1000 >= float(height[0]):
                return common_lists.PANEL_HEIGHTS[index - 1][0]

    def draw_product_size(self,layout):
        row = layout.row()
        box = row.box()
        col = box.column(align=True)

        row1 = col.row(align=True)
        if self.object_has_driver(self.product.obj_x):
            row1.label(text='Width: ' + str(sn_unit.meter_to_active_unit(math.fabs(self.product.obj_x.location.x))))
        else:
            row1.label(text='Width:')
            row1.prop(self,'width',text="")
        
        row1 = col.row(align=True)
        if self.object_has_driver(self.product.obj_z):
            pass
        else:
            row1 = col.row(align=True)
            row1.prop(self,'height',text="Set Height")
        
    def object_has_driver(self,obj):
        if obj.animation_data:
            if len(obj.animation_data.drivers) > 0:
                return True
            
    def draw_common_prompts(self,layout):
        depth_1 = self.product.get_prompt("Depth 1")
        depth_2 = self.product.get_prompt("Depth 2")
        box = layout.box()
        col = box.column(align=True)        
        if depth_1 and depth_2:
            col.prop(depth_1, "distance_value", text=depth_1.name)
            col.prop(depth_2, "distance_value", text=depth_2.name)
        else:
            col.prop(self,'depth')
        
    def get_number_of_equal_widths(self):
        number_of_equal_widths = 0
        
        for i in range(1,9):
            width = self.product.get_prompt("Opening " + str(i) + " Width")
            if width:
                number_of_equal_widths += 1 if width.equal else 0
            else:
                break
            
        return number_of_equal_widths
        
    def draw_splitter_widths(self,layout):
        props = bpy.context.scene.sn_closets

        col = layout.column(align=True)
        box = col.box()
        row = box.row()
        row.label(text="Opening Name:")
        row.label(text="",icon='BLANK1')
        row.label(text="Width:")
        
        box = col.box()
        
        for i in range(1,9):
            width = self.product.get_prompt("Opening " + str(i) + " Width")

            if width:
                row = box.row()
                row.label(text= str(i) + ":")
                if width.equal == False:
                    row.prop(width,'equal',text="")
                else:
                    if self.get_number_of_equal_widths() != 1:
                        row.prop(width,'equal',text="")
                    else:
                        row.label(text="",icon='BLANK1')
                if width.equal:
                    row.label(text=str(round(sn_unit.meter_to_active_unit(width.distance_value), 3)) + '"')
                else:
                    row.prop(width,'distance_value',text="")   
            
    def draw_construction_options(self,layout):
        box = layout.box()
        
        toe_kick_height = self.product.get_prompt("Toe Kick Height")
        toe_kick_setback = self.product.get_prompt("Toe Kick Setback")
        left_against_wall = self.product.get_prompt("Left Against Wall")
        right_against_wall = self.product.get_prompt("Right Against Wall")
        back_against_wall = self.product.get_prompt("Back Against Wall")
        add_tk_skin = self.product.get_prompt("Add TK Skin")
        add_capping_base = self.product.get_prompt("Add Capping Base")

        HPL_Edge_Type = self.product.get_prompt("HPL Edge Type")
        Stone_Edge_Type = self.product.get_prompt("Stone Edge Type")
        Painted_Edge_Type = self.product.get_prompt("Painted Edge Type")
        Stained_Edge_Type = self.product.get_prompt("Stained Edge Type")
        
        col = box.column(align=True)
        row = col.row()
        row.label(text="Against Wall:")   
        row.prop(left_against_wall, "checkbox_value", text="Left")
        row.prop(right_against_wall, "checkbox_value", text="Right")
        row.prop(back_against_wall, "checkbox_value", text="Back")
        
        col = box.column(align=True)
        col.label(text="Base Options:")        
        # TOE KICK OPTIONS
        if toe_kick_height and toe_kick_setback:
            row = col.row()
            row.label(text="Toe Kick")
            row.prop(toe_kick_height, "distance_value", text="Height")
            row.prop(toe_kick_setback, "distance_value", text="Setback")

            if add_tk_skin and add_capping_base:
                if not add_capping_base.get_value():
                    row = col.row()
                    row.prop(add_tk_skin, "checkbox_value", text="Add Toe Kick Skin")
                if not add_tk_skin.get_value():
                    row = col.row()
                    row.prop(add_capping_base, "checkbox_value", text="Add Toe Kick Capping Base")
            elif add_tk_skin:
                row = col.row()
                row.prop(add_tk_skin, "checkbox_value", text="Add Toe Kick Skin")

        col = box.column(align=True)
        col.label(text="Countertop Options:")
        Front_Overhang = self.product.get_prompt("Front Overhang")
        Back_Overhang = self.product.get_prompt("Back Overhang")
        Left_Overhang = self.product.get_prompt("Left Overhang")
        Right_Overhang = self.product.get_prompt("Right Overhang")
        No_Countertop = self.product.get_prompt("No Countertop")

        # 2.3.1
        Deck_Overhang = self.product.get_prompt('Deck Overhang')
        Side_Deck_Overhang = self.product.get_prompt("Side Deck Overhang")

        if Deck_Overhang:
            row = col.row()
            row.prop(Deck_Overhang, "distance_value", text="Opening Overhang")
            row.prop(Side_Deck_Overhang, "distance_value", text="Side Overhang")

        row = col.row()
        row.prop(No_Countertop,"checkbox_value",text="No Countertop")

        if self.countertop_type_ppt and No_Countertop.get_value() == False:
            if Front_Overhang and Back_Overhang:
                row = col.row(align=True)
                row.prop(Front_Overhang, "distance_value", text="Front Overhang")
                row.prop(Back_Overhang, "distance_value", text="Back Overhang")
            if Left_Overhang and Right_Overhang:
                row = col.row(align=True)
                row.prop(Left_Overhang, "distance_value", text="Left Overhang")
                row.prop(Right_Overhang, "distance_value", text="Right Overhang")
            
            c_box = layout.box()
            c_box.label(text='Countertop Types')
            tab_col = c_box.column(align=True)
            row = tab_col.row(align=True)
            row.prop_enum(self,"countertop_type","0")
            row.prop_enum(self,"countertop_type","1")
            row.prop_enum(self,"countertop_type","2")
            row.prop_enum(self,"countertop_type","3")
            row = tab_col.row(align=True)
            row.prop_enum(self,"countertop_type","4")
            row.prop_enum(self,"countertop_type","5")
            row.prop_enum(self,"countertop_type","6")

            if self.countertop_type == '1' or self.countertop_type == '3':
                if HPL_Edge_Type:
                    row = c_box.row()
                    row.label(text=HPL_Edge_Type.name)
                    row = c_box.row()
                    row.prop(self, "hpl_edge_type", expand=False)
            if self.countertop_type == '2' or self.countertop_type == '4' or self.countertop_type == '5':
                if Stone_Edge_Type:
                    row = c_box.row()
                    row.label(text=Stone_Edge_Type.name)
                    row = c_box.row()
                    row.prop(self, "stone_edge_type", expand=False)

            if self.countertop_type == '6' and self.is_painted:
                if Painted_Edge_Type:
                    row = c_box.row()
                    row.label(text=Painted_Edge_Type.name)
                    row = c_box.row()
                    row.prop(self, "painted_edge_type", expand=False)
            if self.countertop_type == '6' and self.is_stained:
                if Stained_Edge_Type:
                    row = c_box.row()
                    row.label(text=Stained_Edge_Type.name)
                    row = c_box.row()
                    row.prop(self, "stained_edge_type", expand=False)

            # sn_utils.draw_enum(self, layout, 'countertop_type', 'Countertop Types', 7)

    def draw_product_placment(self,layout):
        box = layout.box()
        
        row = box.row(align=True)
        row.label(text='Location:')
        row.prop(self.product.obj_bp,'location',index=0,text="X")
        row.prop(self.product.obj_bp,'location',index=1,text="Y")
        
        row.label(text='Rotation:')
        row.prop(self.product.obj_bp,'rotation_euler',index=2,text="")
        
    def draw(self, context):
        super().draw(context)
        layout = self.layout
        if self.product.obj_bp:
            if self.product.obj_bp.name in context.scene.objects:
                left_against_wall = self.product.get_prompt("Left Against Wall")
                box = layout.box()
                box.label(text=self.product.obj_bp.snap.name_object,icon='LATTICE_DATA')
                
                split = box.split(factor=.5)
                self.draw_product_size(split)
                self.draw_common_prompts(split)
                row = box.row()
                if(left_against_wall):
                    row.prop(self,'tabs',expand=True)
                    if self.tabs == 'OPENINGS':
                        self.draw_splitter_widths(box)
                    elif self.tabs == 'CONSTRUCTION':
                        self.draw_construction_options(box)
                    else:
                        pass
                    self.draw_product_placment(box)        
                
bpy.utils.register_class(PROMPTS_Opening_Starter)
