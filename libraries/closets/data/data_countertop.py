import math

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, EnumProperty, FloatProperty

from snap import sn_types, sn_unit, sn_utils
from ..ops.drop_closet import PlaceClosetInsert
from .. import closet_props
from ..common import common_parts
from ..common import common_prompts


class Countertop_Insert(sn_types.Assembly):

    type_assembly = "INSERT"
    placement_type = "EXTERIOR"
    id_prompt = "sn_closets.counter_top"
    show_in_library = True
    category_name = "Products - Basic"

    def update(self):
        self.obj_x.location.x = self.width
        self.obj_y.location.y = -self.depth

        self.obj_bp["IS_BP_COUNTERTOP"] = True
        self.obj_bp["ID_PROMPT"] = self.id_prompt
        self.obj_y['IS_MIRROR'] = True
        self.obj_bp.snap.type_group = self.type_assembly
        super().update()

    def draw(self):
        self.create_assembly()
        self.obj_bp.snap.export_as_subassembly = True

        props = self.obj_bp.sn_closets
        props.is_counter_top_insert_bp = True

        self.add_prompt("Add Left Corner", 'CHECKBOX', False)
        self.add_prompt("Add Right Corner", 'CHECKBOX', False)
        self.add_prompt("Left Corner Width", 'DISTANCE', sn_unit.inch(24))
        self.add_prompt("Right Corner Width", 'DISTANCE', sn_unit.inch(24))
        self.add_prompt("Left Corner Depth", 'DISTANCE', sn_unit.inch(24))
        self.add_prompt("Right Corner Depth", 'DISTANCE', sn_unit.inch(24))
        self.add_prompt("Left Depth", 'DISTANCE', sn_unit.inch(12))
        self.add_prompt("Right Depth", 'DISTANCE', sn_unit.inch(12))
        self.add_prompt("Add Backsplash", 'CHECKBOX', False)
        self.add_prompt("Backsplash Height", 'DISTANCE', sn_unit.inch(4))
        self.add_prompt("Backsplash Thickness", 'DISTANCE', sn_unit.inch(0.75))
        self.add_prompt("Melamine Thickness", 'DISTANCE', sn_unit.inch(0.75))
        self.add_prompt("Extend To Left Panel", 'CHECKBOX', True)
        self.add_prompt("Extend To Right Panel", 'CHECKBOX', True)
        self.add_prompt("Extend Left Amount", 'DISTANCE', sn_unit.inch(0))
        self.add_prompt("Extend Right Amount", 'DISTANCE', sn_unit.inch(0))
        self.add_prompt("Exposed Left", 'CHECKBOX', False)
        self.add_prompt("Exposed Right", 'CHECKBOX', False)
        self.add_prompt("Exposed Back", 'CHECKBOX', False)
        self.add_prompt("Corner Shape", 'COMBOBOX', 0, ['Diagonal', 'L Shape'])

        # Necessary to keep countertop height relative to floor while allowing relative movement to partitions
        self.add_prompt("Tallest Pard Height", 'DISTANCE', 0)
        self.add_prompt("Relative Offset", 'DISTANCE', 0)
        self.add_prompt("Countertop Height", 'DISTANCE', 0)

        common_prompts.add_countertop_prompts(self)

        Product_Width = self.obj_x.snap.get_var('location.x', 'Product_Width')
        Product_Depth = self.obj_y.snap.get_var('location.y', 'Product_Depth')
        # Edge_Type = self.get_prompt('Edge Type').get_var()
        Deck_Thickness = self.get_prompt('Deck Thickness').get_var()
        Deck_Overhang = self.get_prompt('Deck Overhang').get_var()
        Countertop_Type = self.get_prompt('Countertop Type').get_var()
        Add_Left_Corner = self.get_prompt('Add Left Corner').get_var()
        Add_Right_Corner = self.get_prompt('Add Right Corner').get_var()
        Left_Corner_Width = self.get_prompt('Left Corner Width').get_var()
        Right_Corner_Width = self.get_prompt('Right Corner Width').get_var()
        Left_Corner_Depth = self.get_prompt('Left Corner Depth').get_var()
        Right_Corner_Depth = self.get_prompt('Right Corner Depth').get_var()
        Left_Depth = self.get_prompt('Left Depth').get_var()
        Right_Depth = self.get_prompt('Right Depth').get_var()
        Corner_Shape = self.get_prompt('Corner Shape').get_var()
        Add_Backsplash = self.get_prompt('Add Backsplash').get_var()
        B_Splash_Height = self.get_prompt('Backsplash Height').get_var('B_Splash_Height')
        B_Splash_Thickness = self.get_prompt('Backsplash Thickness').get_var('B_Splash_Thickness')
        Melamine_Thickness = self.get_prompt('Melamine Thickness').get_var()
        Extend_Left = self.get_prompt('Extend To Left Panel').get_var('Extend_Left')
        Extend_Right = self.get_prompt('Extend To Right Panel').get_var('Extend_Right')
        Extend_Left_Amount = self.get_prompt('Extend Left Amount').get_var()
        Extend_Right_Amount = self.get_prompt('Extend Right Amount').get_var()
        Exposed_Left = self.get_prompt('Exposed Left').get_var()
        Exposed_Right = self.get_prompt('Exposed Right').get_var()
        Exposed_Back = self.get_prompt('Exposed Back').get_var()

        self.dim_z('Deck_Thickness', [Deck_Thickness])

        melamine_deck = common_parts.add_cc_countertop(self)   
        constraint = melamine_deck.obj_x.constraints.new(type='LIMIT_LOCATION')
        constraint.use_max_x = True
        constraint.max_x = sn_unit.inch(96)
        constraint.owner_space = 'LOCAL'
        constraint = melamine_deck.obj_y.constraints.new(type='LIMIT_LOCATION')
        constraint.use_max_y = True
        constraint.max_y = sn_unit.inch(48)
        constraint.owner_space = 'LOCAL'     
        melamine_deck.set_name("Melamine Countertop")
        melamine_deck.loc_x('IF(Add_Left_Corner,0,IF(Extend_Left,0,Deck_Thickness/2)-Extend_Left_Amount)',[Extend_Left,Extend_Left_Amount,Deck_Thickness,Add_Left_Corner])
        melamine_deck.loc_y('Product_Depth',[Product_Depth])
        melamine_deck.dim_x('Product_Width-IF(Extend_Left,0,Deck_Thickness/2)-IF(Extend_Right,0,Deck_Thickness/2)+IF(Add_Left_Corner,0,Extend_Left_Amount)+IF(Add_Right_Corner,0,Extend_Right_Amount)',
                  [Product_Width,Extend_Left,Extend_Right,Deck_Thickness,Extend_Right_Amount,Extend_Left_Amount,Add_Left_Corner,Add_Right_Corner])
        melamine_deck.dim_y("-Product_Depth-Deck_Overhang",[Product_Depth,Deck_Overhang])
        melamine_deck.dim_z("Melamine_Thickness",[Melamine_Thickness])
        melamine_deck.get_prompt("Hide").set_formula("IF(Countertop_Type==0,False,True)",[Countertop_Type])
        melamine_deck.get_prompt('Exposed Left').set_formula('Exposed_Left',[Exposed_Left])
        melamine_deck.get_prompt('Exposed Right').set_formula('Exposed_Right',[Exposed_Right])
        melamine_deck.get_prompt('Exposed Back').set_formula('Exposed_Back',[Exposed_Back])

        granite_ctop = common_parts.add_granite_countertop(self)
        granite_ctop.set_name("Granite Countertop")
        granite_ctop.loc_x('IF(Add_Left_Corner,0,IF(Extend_Left,0,Deck_Thickness/2)-Extend_Left_Amount)',[Extend_Left,Extend_Left_Amount,Deck_Thickness,Add_Left_Corner])
        granite_ctop.loc_y('Product_Depth',[Product_Depth])
        granite_ctop.dim_x('Product_Width-IF(Extend_Left,0,Deck_Thickness/2)-IF(Extend_Right,0,Deck_Thickness/2)+IF(Add_Left_Corner,0,Extend_Left_Amount)+IF(Add_Right_Corner,0,Extend_Right_Amount)',
                  [Product_Width,Extend_Left,Extend_Right,Deck_Thickness,Extend_Right_Amount,Extend_Left_Amount,Add_Left_Corner,Add_Right_Corner])
        granite_ctop.dim_y("-Product_Depth-Deck_Overhang",[Product_Depth,Deck_Overhang])
        granite_ctop.dim_z(value=sn_unit.inch(1.5))
        granite_ctop.get_prompt("Hide").set_formula("IF(Countertop_Type==2,False,True)",[Countertop_Type])
        # granite_ctop.get_prompt('Edge Type').set_value(0)

        hpltop = common_parts.add_hpl_top(self)
        hpltop.set_name("HPL Countertop")
        hpltop.loc_x('IF(Add_Left_Corner,0,IF(Extend_Left,0,Deck_Thickness/2)-Extend_Left_Amount)',[Extend_Left,Extend_Left_Amount,Deck_Thickness,Add_Left_Corner])
        hpltop.loc_y('Product_Depth',[Product_Depth])
        hpltop.dim_x('Product_Width-IF(Extend_Left,0,Deck_Thickness/2)-IF(Extend_Right,0,Deck_Thickness/2)+IF(Add_Left_Corner,0,Extend_Left_Amount)+IF(Add_Right_Corner,0,Extend_Right_Amount)',
                  [Product_Width,Extend_Left,Extend_Right,Deck_Thickness,Extend_Right_Amount,Extend_Left_Amount,Add_Left_Corner,Add_Right_Corner])
        hpltop.dim_y("-Product_Depth-Deck_Overhang",[Product_Depth,Deck_Overhang])
        hpltop.dim_z("IF(Countertop_Type==1,INCH(0.75),INCH(1.5))", [Countertop_Type])
        hpltop.get_prompt("Hide").set_formula("IF(OR(Countertop_Type==1,Countertop_Type==3),False,True)",[Countertop_Type])

        quartz_ctop = common_parts.add_quartz_countertop(self)
        quartz_ctop.set_name("Quartz Countertop")
        quartz_ctop.loc_x(
            'IF(Add_Left_Corner,0,IF(Extend_Left,0,Deck_Thickness/2)-Extend_Left_Amount)',
            [Extend_Left, Extend_Left_Amount, Deck_Thickness, Add_Left_Corner])
        quartz_ctop.loc_y('Product_Depth', [Product_Depth])
        quartz_ctop.dim_x(
            "Product_Width"
            "-IF(Extend_Left,0,Deck_Thickness/2)"
            "-IF(Extend_Right,0,Deck_Thickness/2)"
            "+IF(Add_Left_Corner,0,Extend_Left_Amount)"
            "+IF(Add_Right_Corner,0,Extend_Right_Amount)",
            [Product_Width, Extend_Left, Extend_Right, Deck_Thickness, Extend_Right_Amount,
             Extend_Left_Amount, Add_Left_Corner, Add_Right_Corner])
        quartz_ctop.dim_y("-Product_Depth-Deck_Overhang", [Product_Depth, Deck_Overhang])
        quartz_ctop.dim_z(value=sn_unit.inch(1.5))
        quartz_ctop.get_prompt("Hide").set_formula("IF(OR(Countertop_Type==4,Countertop_Type==5),False,True)", [Countertop_Type])
        # quartz_ctop.get_prompt('Edge Type').set_value(0)

        wood_deck = common_parts.add_wood_countertop(self)
        wood_deck.set_name("Wood Countertop")
        wood_deck.loc_x(
            'IF(Add_Left_Corner,0,IF(Extend_Left,0,Deck_Thickness/2)-Extend_Left_Amount)',
            [Extend_Left, Extend_Left_Amount, Deck_Thickness, Add_Left_Corner])
        wood_deck.loc_y('Product_Depth',[Product_Depth])
        wood_deck.dim_x(
            "Product_Width"
            "-IF(Extend_Left,0,Deck_Thickness/2)"
            "-IF(Extend_Right,0,Deck_Thickness/2)"
            "+IF(Add_Left_Corner,0,Extend_Left_Amount)"
            "+IF(Add_Right_Corner,0,Extend_Right_Amount)",
            [Product_Width, Extend_Left, Extend_Right, Deck_Thickness, Extend_Right_Amount,
             Extend_Left_Amount, Add_Left_Corner, Add_Right_Corner])
        wood_deck.dim_y("-Product_Depth-Deck_Overhang", [Product_Depth, Deck_Overhang])
        wood_deck.dim_z(value=sn_unit.inch(1.25))
        wood_deck.get_prompt("Hide").set_formula("IF(Countertop_Type==6,False,True)", [Countertop_Type])

        b_splash = common_parts.add_back_splash(self)
        b_splash.set_name("Countertop Backsplash")

        b_splash.loc_x('IF(Add_Left_Corner,-Left_Corner_Width,0)-Extend_Left_Amount',[Add_Left_Corner,Left_Corner_Width,Extend_Left_Amount])
        b_splash.loc_y('Product_Depth',[Product_Depth])
        b_splash.loc_z('IF(Countertop_Type==0,INCH(0.75),INCH(1.5))', [Countertop_Type])
        b_splash.rot_x(value=math.radians(90))

        b_splash.dim_x(
            "Product_Width+IF(Add_Left_Corner,Left_Corner_Width,0)+IF(Add_Right_Corner,Right_Corner_Width,0)+Extend_Right_Amount+Extend_Left_Amount",
            [Product_Width,Add_Left_Corner,Left_Corner_Width,Add_Right_Corner,Right_Corner_Width,Extend_Right_Amount,Extend_Left_Amount]
        )

        b_splash.dim_y("B_Splash_Height",[B_Splash_Height])
        b_splash.dim_z("B_Splash_Thickness",[B_Splash_Thickness])
        b_splash.get_prompt("Hide").set_formula("IF(Add_Backsplash,False,True)",[Add_Backsplash])       

        l_corner_ctop = common_parts.add_cc_corner_countertop(self)      
        l_corner_ctop.set_name("Countertop")
        l_corner_ctop.loc_x('-Left_Corner_Width',[Left_Corner_Width])
        l_corner_ctop.loc_y('Product_Depth',[Product_Depth])
        l_corner_ctop.dim_x("Left_Corner_Width",[Left_Corner_Width])
        l_corner_ctop.dim_y("-Left_Corner_Depth",[Left_Corner_Depth])
        l_corner_ctop.dim_z('IF(Countertop_Type == 0,Melamine_Thickness,Deck_Thickness)',[Deck_Thickness,Melamine_Thickness,Countertop_Type])
        l_corner_ctop.get_prompt("Hide").set_formula("IF(Add_Left_Corner,False,True)",[Add_Left_Corner])       
        # l_corner_ctop.get_prompt('Edge Type').set_formula('IF(Countertop_Type==2,Edge_Type,1)',[Edge_Type,Countertop_Type])
        l_corner_ctop.get_prompt('Right Depth').set_formula('Product_Depth+Deck_Overhang',[Product_Depth,Deck_Overhang])
        l_corner_ctop.get_prompt('Left Depth').set_formula('Left_Depth',[Left_Depth])
        l_corner_ctop.get_prompt('Corner Shape').set_formula('Corner_Shape',[Corner_Shape])

        left_b_splash = common_parts.add_back_splash(self)
        left_b_splash.set_name("Left Countertop Backsplash")
        left_b_splash.loc_x('-Left_Corner_Width',[Left_Corner_Width])
        left_b_splash.loc_y('Product_Depth-B_Splash_Thickness',[Product_Depth,B_Splash_Thickness])
        left_b_splash.loc_z('IF(Countertop_Type==0,INCH(0.75),INCH(1.5))', [Countertop_Type])
        left_b_splash.rot_x(value=math.radians(90))
        left_b_splash.rot_z(value=math.radians(90))
        left_b_splash.dim_x("-Left_Corner_Depth+B_Splash_Thickness",[Left_Corner_Depth,B_Splash_Thickness])
        left_b_splash.dim_y("B_Splash_Height",[B_Splash_Height])
        left_b_splash.dim_z("B_Splash_Thickness",[B_Splash_Thickness]) 
        left_b_splash.get_prompt("Hide").set_formula("IF(AND(Add_Left_Corner,Add_Backsplash),False,True)",[Add_Left_Corner,Add_Backsplash])       

        r_corner_ctop = common_parts.add_cc_corner_countertop(self)
        r_corner_ctop.set_name("Countertop")
        r_corner_ctop.loc_x('Product_Width+Right_Corner_Width',[Product_Width,Right_Corner_Width])
        r_corner_ctop.loc_y('Product_Depth',[Product_Depth])
        r_corner_ctop.rot_z(value=math.radians(-90))
        r_corner_ctop.dim_x("Right_Corner_Depth",[Right_Corner_Depth])
        r_corner_ctop.dim_y("-Right_Corner_Width",[Right_Corner_Width])
        r_corner_ctop.dim_z('IF(Countertop_Type == 0,Melamine_Thickness,Deck_Thickness)',[Deck_Thickness,Melamine_Thickness,Countertop_Type])
        r_corner_ctop.get_prompt("Hide").set_formula("IF(Add_Right_Corner,False,True)",[Add_Right_Corner])
        # r_corner_ctop.get_prompt('Edge Type').set_formula('IF(Countertop_Type==2,Edge_Type,1)',[Edge_Type,Countertop_Type])
        r_corner_ctop.get_prompt('Left Depth').set_formula('Product_Depth+Deck_Overhang',[Product_Depth,Deck_Overhang])
        r_corner_ctop.get_prompt('Right Depth').set_formula('Right_Depth',[Right_Depth])
        r_corner_ctop.get_prompt('Corner Shape').set_formula('Corner_Shape',[Corner_Shape])

        right_b_splash = common_parts.add_back_splash(self)
        right_b_splash.set_name("Right Countertop Backsplash")
        right_b_splash.loc_x('Product_Width+Right_Corner_Width',[Product_Width,Right_Corner_Width])
        right_b_splash.loc_y('Product_Depth-B_Splash_Thickness',[Product_Depth,B_Splash_Thickness])
        right_b_splash.loc_z('IF(Countertop_Type==0,INCH(0.75),INCH(1.5))', [Countertop_Type])
        right_b_splash.rot_x(value=math.radians(90))
        right_b_splash.rot_z(value=math.radians(-90))
        right_b_splash.dim_x("Right_Corner_Depth-B_Splash_Thickness",[Right_Corner_Depth,B_Splash_Thickness])
        right_b_splash.dim_y("B_Splash_Height",[B_Splash_Height])
        right_b_splash.dim_z("B_Splash_Thickness",[B_Splash_Thickness]) 
        right_b_splash.get_prompt("Hide").set_formula("IF(AND(Add_Right_Corner,Add_Backsplash),False,True)",[Add_Right_Corner,Add_Backsplash])         

        self.update()


class PROMPTS_Counter_Top(sn_types.Prompts_Interface):
    bl_idname = "sn_closets.counter_top"
    bl_label = "Countertop Prompt" 
    bl_description = "This shows all of the available Countertop options"
    bl_options = {'UNDO'}
    
    object_name: StringProperty(name="Object Name")

    width: FloatProperty(name="Width",unit='LENGTH',precision=4)
    height: FloatProperty(name="Height",unit='LENGTH',precision=4)
    depth: FloatProperty(name="Depth",unit='LENGTH',precision=4)    

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

    assembly = None
    countertop_type_prompt = None
    edge_type_prompt = None

    prev_ex_left = 0
    prev_ex_right = 0
    prev_width = 0

    prev_front_overhang = 0
    prev_depth = 0
    hpl_edge_type_prompt = None
    stone_edge_type_prompt = None
    painted_edge_type_prompt = None
    stained_edge_type_prompt = None
    is_painted = False
    is_stained = False
        
    def check(self, context):
        mat_props = context.scene.closet_materials
        countertop_type = 0
        Add_Left_Corner = self.assembly.get_prompt("Add Left Corner")
        Add_Right_Corner = self.assembly.get_prompt("Add Right Corner")
        extend_left_amount = self.assembly.get_prompt("Extend Left Amount")
        extend_right_amount = self.assembly.get_prompt("Extend Right Amount")
        prompts = [Add_Left_Corner,Add_Right_Corner,extend_left_amount,extend_right_amount]

        # COUNTERTOP_HPL is used for "Custom"
        countertops = (
            "COUNTERTOP_MELAMINE", "COUNTERTOP_HPL", "COUNTERTOP_GRANITE",
            "COUNTERTOP_HPL", "COUNTERTOP_QUARTZ", "COUNTERTOP_STANDARD_QUARTZ", "COUNTERTOP_WOOD")

        if self.countertop_type_prompt:
            countertop_type = self.countertop_type_prompt.get_value()
            self.prev_countertop_type = countertop_type

        if self.prev_countertop_type != int(self.countertop_type):
            self.countertop_type_prompt.set_value(int(self.countertop_type))
            countertop_type = self.countertop_type_prompt.get_value()

        if int(self.countertop_type) == 0: 
            self.check_width()
            self.check_depth()

            # Set unique material status
            for child in self.assembly.obj_bp.children:
                if countertops[countertop_type] in child or (self.countertop_type == "5" and "COUNTERTOP_QUARTZ" in child):
                    use_unique = mat_props.ct_type_index != countertop_type
                    child.sn_closets.use_unique_material = use_unique
                    bpy.context.view_layer.objects.active = child

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
        
        if all(prompts):
            if(Add_Left_Corner.get_value()):
                extend_left_amount.set_value(sn_unit.inch(0)) 
            if(Add_Right_Corner.get_value()):   
                extend_right_amount.set_value(sn_unit.inch(0))
        self.assembly.obj_bp.location = self.assembly.obj_bp.location # Redraw Viewport
        closet_props.update_render_materials(self, context)   

        Tallest_Pard_Height = self.assembly.get_prompt("Tallest Pard Height")
        Relative_Offset = self.assembly.get_prompt("Relative Offset")
        Countertop_Height = self.assembly.get_prompt("Countertop Height")
        if Relative_Offset:
            Relative_Offset.set_value(Countertop_Height.get_value() - Tallest_Pard_Height.get_value())

        if Countertop_Height is not None:
            self.assembly.obj_bp.location.z = Countertop_Height.get_value()

        return True

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
        return {'FINISHED'}
        
    def invoke(self,context,event):
        self.assembly = self.get_insert()
        self.countertop_type_prompt = self.assembly.get_prompt("Countertop Type")
        self.countertop_type = str(self.countertop_type_prompt.combobox_index)
        self.set_previous_values()
        self.set_edge_type_enums()
        self.get_wood(context)
        wm = context.window_manager
        return super().invoke(context, event, width=475)
    
    def set_edge_type_enums(self):
        self.hpl_edge_type_prompt = self.assembly.get_prompt("HPL Edge Type")
        self.stone_edge_type_prompt = self.assembly.get_prompt("Stone Edge Type")
        self.painted_edge_type_prompt = self.assembly.get_prompt("Painted Edge Type")
        self.stained_edge_type_prompt = self.assembly.get_prompt("Stained Edge Type")
        if self.hpl_edge_type_prompt:
            self.hpl_edge_type = str(self.hpl_edge_type_prompt.combobox_index)
        if self.stone_edge_type_prompt:
            self.stone_edge_type = str(self.stone_edge_type_prompt.combobox_index)
        if self.painted_edge_type_prompt:
            self.painted_edge_type = str(self.painted_edge_type_prompt.combobox_index)
        if self.stained_edge_type_prompt:
            self.stained_edge_type = str(self.stained_edge_type_prompt.combobox_index)
    
    def get_wood(self, context):
        for child in self.assembly.obj_bp.children:
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

    def draw(self, context):
        super().draw(context)
        layout = self.layout
        if self.assembly.obj_bp:
            if self.assembly.obj_bp.name in context.scene.objects:
                Countertop_Type = self.assembly.get_prompt("Countertop Type")
                Countertop_Thickness = self.assembly.get_prompt("Countertop Thickness")
                HPL_Edge_Type = self.assembly.get_prompt("HPL Edge Type")
                Stone_Edge_Type = self.assembly.get_prompt("Stone Edge Type")
                Painted_Edge_Type = self.assembly.get_prompt("Painted Edge Type")
                Stained_Edge_Type = self.assembly.get_prompt("Stained Edge Type")
                HPL_Material_Name = self.assembly.get_prompt("HPL Material Name")
                HPL_Material_Number = self.assembly.get_prompt("HPL Material Number")
                Deck_Overhang = self.assembly.get_prompt("Deck Overhang")  
                Add_Left_Corner = self.assembly.get_prompt("Add Left Corner")
                Add_Right_Corner = self.assembly.get_prompt("Add Right Corner")
                Corner_Shape = self.assembly.get_prompt("Corner Shape")
                Add_Backsplash = self.assembly.get_prompt('Add Backsplash')
                B_Splash_Height = self.assembly.get_prompt('Backsplash Height')
                B_Splash_Thickness = self.assembly.get_prompt('Backsplash Thickness') 
                extend_left_amount = self.assembly.get_prompt("Extend Left Amount")
                extend_right_amount = self.assembly.get_prompt("Extend Right Amount")
                exposed_left = self.assembly.get_prompt("Exposed Left")
                exposed_right = self.assembly.get_prompt("Exposed Right")      
                exposed_back = self.assembly.get_prompt("Exposed Back")
                countertop_height = self.assembly.get_prompt('Countertop Height')
                
                box = layout.box()   
                row = box.row()

                if Deck_Overhang:
                    row = box.row()
                    row.prop(Deck_Overhang, "distance_value", text="Front Overhang:")

                if extend_left_amount and Add_Left_Corner.get_value() == False:                        
                    row = box.row()
                    row.prop(extend_left_amount, "distance_value", text="Left Overhang:")

                if extend_right_amount and Add_Right_Corner.get_value() == False:    
                    row = box.row()
                    row.prop(extend_right_amount, "distance_value", text="Right Overhang:")

                row = box.row()
                row.label(text="Exposed Ends:")
                row.prop(exposed_left, "checkbox_value", text="Left")
                row.prop(exposed_right, "checkbox_value", text="Right")      
                row.prop(exposed_back, "checkbox_value", text="Back")
           
                if countertop_height:
                    row = box.row()
                    row.label(text="Countertop Height:")
                    row.prop(countertop_height,'distance_value',index=2,text="")

                row = box.row()
                row.prop(Add_Backsplash, "checkbox_value", text=Add_Backsplash.name)

                if Add_Backsplash.get_value():
                    row = box.row()
                    row.prop(B_Splash_Height, "distance_value", text=B_Splash_Height.name)
                    row = box.row()
                    row.prop(B_Splash_Thickness, "distance_value", text=B_Splash_Thickness.name)
                
                row = box.row()
                row.label(text="Add Corner:")
                row.prop(Add_Left_Corner, "checkbox_value", text=Add_Left_Corner.name)
                row.prop(Add_Right_Corner, "checkbox_value", text=Add_Right_Corner.name)
                
                if Add_Left_Corner.get_value():
                    Left_Corner_Width = self.assembly.get_prompt("Left Corner Width")
                    Left_Corner_Depth = self.assembly.get_prompt("Left Corner Depth")
                    Left_Depth = self.assembly.get_prompt("Left Depth")
                    row = box.row()
                    row.label(text="Left Corner Size:")
                    row = box.row(align=True)
                    row.prop(Left_Corner_Width, "distance_value", text=Left_Corner_Width.name)
                    row.prop(Left_Corner_Depth, "distance_value", text=Left_Corner_Depth.name)
                    row.prop(Left_Depth, "distance_value", text=Left_Depth.name)
                
                if Add_Right_Corner.get_value():
                    Right_Corner_Width = self.assembly.get_prompt("Right Corner Width")
                    Right_Corner_Depth = self.assembly.get_prompt("Right Corner Depth")
                    Right_Depth = self.assembly.get_prompt("Right Depth")
                    row = box.row()
                    row.label(text="Right Corner Size:")
                    row = box.row(align=True)
                    row.prop(Right_Corner_Width, "distance_value", text=Right_Corner_Width.name)
                    row.prop(Right_Corner_Depth, "distance_value", text=Right_Corner_Depth.name)
                    row.prop(Right_Depth, "distance_value", text=Right_Depth.name)

                if Add_Left_Corner.get_value() or Add_Right_Corner.get_value():
                    row = box.row()
                    row.prop(Corner_Shape, "combobox_index", text=Corner_Shape.name)

                if Countertop_Type:
                    c_box = layout.box()
                    c_box.label(text=Countertop_Type.name)
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

    
    def check_width(self):
        extend_left_amount =\
            self.assembly.get_prompt("Extend Left Amount").get_value()
        extend_right_amount =\
            self.assembly.get_prompt("Extend Right Amount").get_value()
        width = self.assembly.obj_x.location.x
        total_width =\
            extend_left_amount + extend_right_amount + width
        prev_total_width =\
            self.prev_ex_left + self.prev_ex_right + self.width
        max_width = sn_unit.inch(96)
        is_width_augmented =\
            round(prev_total_width, 2) < round(max_width, 2)
        limit_reached =\
            round(total_width, 2) >= round(max_width, 2) and is_width_augmented
        if limit_reached:
            bpy.ops.snap.log_window("INVOKE_DEFAULT",
                                    message="Maximum Melamine Countertop width is 96\"",
                                    icon="ERROR")
            if self.prev_ex_left == extend_left_amount:
                self.assembly.get_prompt(
                    "Extend Right Amount").set_value(self.prev_ex_right)
            if self.prev_ex_right == extend_right_amount:
                self.assembly.get_prompt(
                    "Extend Left Amount").set_value(self.prev_ex_left)
        else:
            self.prev_ex_left = extend_left_amount
            self.prev_ex_right = extend_right_amount
        self.prev_width = width

    def check_depth(self):
        front_overhang_value =\
            self.assembly.get_prompt("Deck Overhang").get_value()
        depth = self.assembly.obj_y.location.y
        total_depth =\
            depth + front_overhang_value
        prev_total_depth =\
            self.prev_front_overhang + self.depth
        max_depth = sn_unit.inch(48)
        is_depth_augmented =\
            round(prev_total_depth, 2) < round(max_depth, 2)
        limit_reached =\
            round(total_depth, 2) >= round(max_depth, 2) and is_depth_augmented
        if limit_reached:
            bpy.ops.snap.log_window("INVOKE_DEFAULT",
                                    message="Maximum Melamine Countertop depth is 48\"",
                                    icon="ERROR")
            self.assembly.get_prompt(
                "Deck Overhang").set_value(self.prev_front_overhang)
        else:
            self.prev_front_overhang = front_overhang_value

        self.prev_depth = depth

    def set_previous_values(self):
        ex_left_amount_value =\
            self.assembly.get_prompt("Extend Left Amount").get_value()
        ex_right_amount_value =\
            self.assembly.get_prompt("Extend Right Amount").get_value()
        self.prev_ex_left = ex_left_amount_value
        self.prev_ex_right = ex_right_amount_value
        self.prev_width = self.assembly.obj_x.location.x

        front_overhang_value =\
            self.assembly.get_prompt("Deck Overhang").get_value()
        self.prev_front_overhang = front_overhang_value
        self.prev_depth = self.assembly.obj_y.location.y


class OPERATOR_Place_Countertop(Operator, PlaceClosetInsert):
    bl_idname = "sn_closets.place_countertop"
    bl_label = "Place Countertop"
    bl_description = "This places the countertop."
    bl_options = {'UNDO'}

    show_openings = False
    countertop = None
    selected_panel_1 = None
    selected_panel_2 = None
    objects = []
    panels = []
    max_shelf_length = 96.0
    max_shelf_depth = 48.0
    sel_product_bp = None
    panel_bps = []
    header_text = "Place Countertop - Select Partitions (Left to Right)   (Esc, Right Click) = Cancel Command  :  (Left Click) = Select Panel"
    
    # def __del__(self):
    #     bpy.context.area.header_text_set()

    def execute(self, context):
        self.countertop = self.asset
        self.objects = [obj for obj in context.visible_objects if obj.parent and obj.parent.sn_closets.is_panel_bp]
        return super().execute(context)

    def get_deepest_panel(self):
        depths = []
        for p in self.panels:
            depths.append(abs(p.obj_y.location.y))
        return max(depths)

    def get_closest_opening(self,x_loc):
        return lambda op : abs(op - x_loc)

    def get_panels(self):
        self.panel_bps.clear()

        for child in self.sel_product_bp.children:
            if 'IS_BP_PANEL' in child and 'PARTITION_NUMBER' in child:
                self.panel_bps.append(child)

        self.panel_bps.sort(key=lambda a: int(a['PARTITION_NUMBER']))

        for i,bp in enumerate(self.panel_bps):
            print(i,sn_unit.inch(bp.location.x))
            
    def is_first_panel(self, panel):
        if panel.obj_z.location.z < 0:
            return True
        else:
            return False

    def is_last_panel(self, panel):
        self.get_panels()
        last_panel_bp = self.panel_bps[-1]
        if panel.obj_bp is last_panel_bp:
            return True
        else:
            return False

    def get_inculded_panels(self,panel_1,panel_2):
        self.panels.clear()
        p1_x_loc = panel_1.obj_bp.location.x
        p2_x_loc = panel_2.obj_bp.location.x

        for child in self.sel_product_bp.children:
            if 'IS_BP_BLIND_CORNER_PANEL' in child:
                continue
            
            if 'IS_BP_PANEL' in child:
                if p1_x_loc <= child.location.x <= p2_x_loc:
                    self.panels.append(sn_types.Assembly(child))

    def place_on_hanging_section(self, product, P1_X_Loc, P2_X_Loc, Panel_Thickness):
        Left_Side_Wall_Filler = product.get_prompt('Left Side Wall Filler').get_var()
        Right_Side_Wall_Filler = product.get_prompt('Right Side Wall Filler').get_var()

        if self.is_first_panel(self.selected_panel_1):
            self.countertop.loc_x('P1_X_Loc-Left_Side_Wall_Filler', [P1_X_Loc, Left_Side_Wall_Filler])
            if self.is_last_panel(self.selected_panel_2):
                self.countertop.dim_x(
                    'P2_X_Loc-P1_X_Loc+Left_Side_Wall_Filler+Right_Side_Wall_Filler',
                    [P1_X_Loc, P2_X_Loc, Left_Side_Wall_Filler, Right_Side_Wall_Filler])
            else:
                self.countertop.dim_x(
                    'P2_X_Loc-P1_X_Loc+Left_Side_Wall_Filler',
                    [P1_X_Loc, P2_X_Loc, Left_Side_Wall_Filler])
        else:
            self.countertop.loc_x('P1_X_Loc-Panel_Thickness', [P1_X_Loc, Panel_Thickness])
            if self.is_last_panel(self.selected_panel_2):
                self.countertop.dim_x(
                    'P2_X_Loc-P1_X_Loc+Panel_Thickness+Right_Side_Wall_Filler',
                    [P1_X_Loc, P2_X_Loc, Panel_Thickness, Right_Side_Wall_Filler])
            else:
                self.countertop.dim_x(
                    'P2_X_Loc-P1_X_Loc+Panel_Thickness',
                    [P1_X_Loc, P2_X_Loc, Panel_Thickness])

    def place_insert(self, context, event):
        selected_point, selected_obj, _ = sn_utils.get_selection_point(context, event, objects=self.objects)
        bpy.ops.object.select_all(action='DESELECT')

        if selected_obj is not None:
            self.sel_product_bp = sn_utils.get_closet_bp(selected_obj)
            sel_assembly_bp = sn_utils.get_assembly_bp(selected_obj)
            product = sn_types.Assembly(self.sel_product_bp)

            if sel_assembly_bp and 'IS_BP_CLOSET' in self.sel_product_bp:
                if 'IS_BP_PANEL' in sel_assembly_bp:
                    selected_obj.select_set(True)
                    hover_panel = sn_types.Assembly(selected_obj.parent)
                    hp_x_loc = hover_panel.obj_bp.location.x

                    if not self.selected_panel_1:
                        if hover_panel.obj_bp.location.x == product.obj_x.location.x or abs(round(sn_unit.meter_to_inch(hover_panel.obj_y.location.y), 2)) > self.max_shelf_depth:
                            selected_obj.select_set(False)
                            return {'RUNNING_MODAL'}

                        self.countertop.obj_bp.parent = self.sel_product_bp
                        self.countertop.obj_bp.location = hover_panel.obj_bp.location

                        if hover_panel.obj_z.location.z > 0:
                            self.countertop.obj_bp.location.x = hp_x_loc - sn_unit.inch(0.75)

                        self.countertop.obj_bp.location.z += hover_panel.obj_x.location.x
                        self.countertop.obj_x.location.x = sn_unit.inch(18.0)
                        self.countertop.obj_bp.location.y = hover_panel.obj_y.location.y
                        self.countertop.obj_y.location.y = -hover_panel.obj_y.location.y

                    else:
                        self.get_inculded_panels(self.selected_panel_1, hover_panel)
                        sp1_x_loc = self.selected_panel_1.obj_bp.location.x
                        hp_x_loc = hover_panel.obj_bp.location.x
                        ct_length = hp_x_loc - sp1_x_loc
                        ct_depth = self.get_deepest_panel()
                        same_panel = self.selected_panel_1.obj_bp == hover_panel.obj_bp
                        same_product = self.selected_panel_1.obj_bp.parent == hover_panel.obj_bp.parent
                        hp_to_left = hp_x_loc < sp1_x_loc
                        hp_out_of_reach = round(sn_unit.meter_to_inch(ct_length), 2) > self.max_shelf_length
                        ct_too_deep = abs(round(sn_unit.meter_to_inch(hover_panel.obj_y.location.y), 2)) > self.max_shelf_depth

                        if same_panel or hp_to_left or not same_product or hp_out_of_reach or ct_too_deep:
                            selected_obj.select_set(False)
                            if same_product and hp_out_of_reach:
                                bpy.ops.snap.log_window("INVOKE_DEFAULT",
                                            message="Maximum Countertop width is 96\"",
                                            message2="You can add another Countertop",
                                            icon="ERROR")
                            if same_product and ct_too_deep:
                                bpy.ops.snap.log_window("INVOKE_DEFAULT",
                                            message="Maximum Countertop depth is 48\"",
                                            icon="ERROR")
                            return {'RUNNING_MODAL'}

                        if self.is_first_panel(self.selected_panel_1):
                            self.countertop.obj_x.location.x = ct_length
                        else:
                            if hp_x_loc < sp1_x_loc:
                                #Hover selection to left
                                pass
                            else:
                                self.countertop.obj_x.location.x = ct_length + sn_unit.inch(0.75)

                        self.countertop.obj_bp.location.y = ct_depth * -1
                        self.countertop.obj_y.location.y = ct_depth

                    if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
                        if not self.selected_panel_1:
                            self.selected_panel_1 = hover_panel
                            sn_utils.set_wireframe(self.countertop.obj_bp,False)
                            bpy.ops.object.select_all(action='DESELECT')
                            context.view_layer.objects.active = self.countertop.obj_bp

                            self.countertop.obj_bp.parent = self.sel_product_bp
                            p1_z_loc = self.selected_panel_1.obj_bp.location.z
                            p1_z_dim = self.selected_panel_1.obj_x.location.x

                            if self.selected_panel_1.obj_z.location.z < 0:
                                self.countertop.obj_bp.location.x = self.selected_panel_1.obj_bp.location.x
                            else:
                                self.countertop.obj_bp.location.x = self.selected_panel_1.obj_bp.location.x - sn_unit.inch(0.75)
                            self.countertop.obj_bp.location.z = p1_z_loc + p1_z_dim
                            self.countertop.obj_y.location.y = -self.selected_panel_1.obj_y.location.y

                            return {'RUNNING_MODAL'}

                        if not self.selected_panel_2:
                            self.selected_panel_2 = hover_panel
                            bpy.ops.object.select_all(action='DESELECT')
                            context.view_layer.objects.active = self.countertop.obj_bp
                            self.countertop.obj_bp.select_set(True)

                            if self.selected_panel_1.obj_bp == self.selected_panel_2.obj_bp:
                                self.cancel_drop(context,event)
                                return {'FINISHED'}

                            P1_X_Loc = self.selected_panel_1.obj_bp.snap.get_var('location.x', 'P1_X_Loc')
                            P2_X_Loc = self.selected_panel_2.obj_bp.snap.get_var('location.x', 'P2_X_Loc')
                            Panel_Thickness = product.get_prompt('Panel Thickness').get_var()

                            countertop_height_ppt = self.countertop.get_prompt("Countertop Height")
                            tallest_pard_ppt = self.countertop.get_prompt('Tallest Pard Height')
                            if countertop_height_ppt:
                                countertop_height_ppt.set_value(self.countertop.obj_bp.location.z)
                            if tallest_pard_ppt:
                                tallest_pard_ppt.set_value(self.countertop.obj_bp.location.z)

                            self.place_on_hanging_section(product, P1_X_Loc, P2_X_Loc, Panel_Thickness)

                            return self.finish(context)

        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        bpy.ops.object.select_all(action='DESELECT')
        context.area.tag_redraw()
        context.area.header_text_set(text=self.header_text)
        self.reset_selection()

        if not self.countertop:
            self.countertop = self.asset

        if self.event_is_cancel_command(event):
            context.area.header_text_set(None)
            return self.cancel_drop(context)

        if self.event_is_pass_through(event):
            return {'PASS_THROUGH'}

        return self.place_insert(context, event)    


bpy.utils.register_class(PROMPTS_Counter_Top)
bpy.utils.register_class(OPERATOR_Place_Countertop)
