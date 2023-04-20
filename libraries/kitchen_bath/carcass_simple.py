from os import path
import math

import bpy

from snap import sn_props, sn_types, sn_unit, sn_utils
from . import cabinet_properties
from . import common_parts
from snap.libraries.closets import closet_paths
from snap import sn_paths


PART_WITH_FRONT_EDGEBANDING = path.join(closet_paths.get_closet_assemblies_path(), "Part with Edgebanding.blend")
PART_WITH_FRONT_AND_BOTTOM_EDGEBANDING = path.join(closet_paths.get_closet_assemblies_path(), "Part with Edgebanding.blend")
PART_WITH_NO_EDGEBANDING = path.join(closet_paths.get_closet_assemblies_path(), "Part with Edgebanding.blend")
NOTCHED_SIDE = path.join(sn_paths.KITCHEN_BATH_ASSEMBLIES, "Notched Side.blend")
LEG_LEVELERS = path.join(sn_paths.KITCHEN_BATH_ASSEMBLIES, "Leg Levelers.blend")
CHAMFERED_PART = path.join(sn_paths.KITCHEN_BATH_ASSEMBLIES,"Chamfered Part.blend")
CORNER_NOTCH_PART = path.join(sn_paths.KITCHEN_BATH_ASSEMBLIES,"Corner Notch Part.blend")
ISLAND_FRONT_ROW = 0
ISLAND_BACK_ROW = 1
ISLAND_BASE_CARCASS = 0
ISLAND_APPLIANCE_CARCASS = 1
ISLAND_SINK_CARCASS = 2


def add_side_height_dimension(original_part):
    part = original_part

    part_children = part.obj_bp.children
    for child in part_children:
        for subchild in child.children:
            if subchild.get("SIDE_HEIGHT_LABEL"):
                # print("PREV_add_side_height_dimensions - part.obj_bp.child=",child, "subchild=",subchild)
                sn_utils.delete_object_and_children(subchild)
                part = sn_types.Assembly(child)

    Part_Height = part.obj_x.snap.get_var('location.x','Part_Height')

    dim = sn_types.Dimension()
    dim.anchor["SIDE_HEIGHT_LABEL"] = True
    dim.anchor["IS_KB_LABEL"] = True
    dim.parent(part.obj_bp)
    
    dim.anchor.rotation_euler.y = math.radians(-90)
    if hasattr(part, "mirror_z") and part.mirror_z:
        dim.start_x('part/2',[part])
    else:
        dim.start_x('Part_Height/2',[Part_Height])
    dim.start_y(value=sn_unit.inch(-1.5))
    dim.start_z(value=sn_unit.inch(-1.5))
    dim.set_label("")

def create_dimensions(part):
    add_side_height_dimension(part)
    update_dimensions(part)

def update_dimensions(part):
    dimensions = []
    
    toe_kick_ppt = part.get_prompt('Toe Kick Height')
    toe_kick_height = 0
    if toe_kick_ppt:
        toe_kick_height = toe_kick_ppt.get_value()

    for child in part.obj_bp.children:
        for nchild in child.children:
            if 'SIDE_HEIGHT_LABEL' in nchild:
                dimensions.append(nchild)

    for anchor in dimensions:
        assembly = sn_types.Assembly(anchor.parent)
        abs_x_loc = math.fabs(sn_unit.meter_to_inch(assembly.obj_x.location.x - toe_kick_height))
        dim_x_label = str(round(abs_x_loc, 2)) + '\"'
        anchor.snap.opengl_dim.gl_label = dim_x_label

# ---------ASSEMBLY INSTRUCTIONS
def add_part(assembly, path):
    part_bp = assembly.add_assembly_from_file(path)
    part = sn_types.Assembly(part_bp)
    part.obj_bp.sn_closets.is_panel_bp = True
    return part  
    
class Standard_Carcass(sn_types.Assembly):

    type_assembly = "INSERT"
    id_prompt = cabinet_properties.LIBRARY_NAME_SPACE + ".frameless_cabinet_prompts"
    library_name = "Carcasses"
    placement_type = ""

    carcass_type = ""  # {Base, Tall, Upper, Sink, Suspended}
    carcass_shape = 'RECTANGLE'
    open_name = ""

    remove_top = False  # Used to remove top for face frame sink cabinets
    remove_bottom = False  # Used to remove bottom for appliance cabinets

    def create_dimensions(self):
        create_dimensions(self) # Call module level function to create/recreate door dim labels

    def update_dimensions(self):
        update_dimensions(self)  # Call module level function to find and update door dim labels

    def update(self):
        super().update()
        self.obj_bp["IS_BP_CARCASS"] = True
        self.obj_bp["STANDARD_CARCASS"] = True
        self.obj_bp["PROFILE_SHAPE_RECTANGLE"] = True
        self.obj_bp["CARCASS_TYPE"] = self.carcass_type

    def add_common_carcass_prompts(self):
        props = cabinet_properties.get_scene_props().carcass_defaults

        self.add_prompt("Left Fin End", 'CHECKBOX', False)
        self.add_prompt("Right Fin End", 'CHECKBOX', False)
        self.add_prompt("Left End Condition", 'COMBOBOX', 0, ['MP', 'EP'])
        self.add_prompt("Right End Condition", 'COMBOBOX', 0, ['MP', 'EP'])
        self.add_prompt("Left Side Wall Filler", 'DISTANCE', 0.0)
        self.add_prompt("Right Side Wall Filler", 'DISTANCE', 0.0)
        self.add_prompt("Use Nailers", 'CHECKBOX', props.use_nailers)
        self.add_prompt("Nailer Width", 'DISTANCE', props.nailer_width)
        self.add_prompt("Center Nailer Switch", 'DISTANCE', props.center_nailer_switch)
        self.add_prompt("Use Thick Back", 'CHECKBOX', props.use_thick_back)
        self.add_prompt("Remove Back", 'CHECKBOX', props.remove_back)
        self.add_prompt("Remove Bottom", 'CHECKBOX', False)

        if self.carcass_type in {'Base', 'Suspended'} and not props.use_full_tops:
            self.add_prompt("Stretcher Width", 'DISTANCE', props.stretcher_width)

        self.add_prompt("Left Side Thickness", 'DISTANCE', sn_unit.inch(.75))
        self.add_prompt("Right Side Thickness", 'DISTANCE', sn_unit.inch(.75))
        self.add_prompt("Top Thickness", 'DISTANCE', sn_unit.inch(.75))
        self.add_prompt("Bottom Thickness", 'DISTANCE', sn_unit.inch(.75))
        self.add_prompt("Back Thickness", 'DISTANCE', sn_unit.inch(.75))
        self.add_prompt("Thick Back Thickness", 'DISTANCE', sn_unit.inch(.75))
        self.add_prompt("Filler Thickness", 'DISTANCE', sn_unit.inch(.75))
        self.add_prompt("Nailer Thickness", 'DISTANCE', sn_unit.inch(.75))
        self.add_prompt("Edgebanding Thickness", 'DISTANCE', sn_unit.inch(.02))

        # Create separate prompts obj for insets
        ppt_obj_insets = self.add_prompt_obj("Backing_Config")
        self.add_prompt("Back Inset", 'DISTANCE', sn_unit.inch(0), prompt_obj=ppt_obj_insets)
        self.add_prompt("Top Inset", 'DISTANCE', sn_unit.inch(0), prompt_obj=ppt_obj_insets)
        self.add_prompt("Bottom Inset", 'DISTANCE', sn_unit.inch(0), prompt_obj=ppt_obj_insets)

    # Updated
    def add_base_assembly_prompts(self):
        props = cabinet_properties.get_scene_props().carcass_defaults
        toe_kick_height = 0
        if self.carcass_type == 'Appliance':
            # self.add_prompt("Toe Kick Height",'DISTANCE', 0)
            self.add_prompt("Toe Kick Height",'DISTANCE', props.toe_kick_height)
        else:
            self.add_prompt("Toe Kick Height",'DISTANCE', props.toe_kick_height)
        self.add_prompt("Toe Kick Setback",'DISTANCE', props.toe_kick_setback)
        self.add_prompt("Toe Kick Thickness", 'DISTANCE', sn_unit.inch(.75))
        self.add_prompt("Left Toe Kick Filler", 'DISTANCE', 0.0)
        self.add_prompt("Right Toe Kick Filler", 'DISTANCE', 0.0)

    def add_valance_prompts(self,add_bottom_valance):
        props = cabinet_properties.get_scene_props().carcass_defaults
        self.add_prompt("Valance Height Top",'DISTANCE',props.valance_height_top)
        self.add_prompt("Door Valance Top",'CHECKBOX',props.door_valance_top)
        if add_bottom_valance:
            self.add_prompt("Valance Height Bottom",'DISTANCE',props.valance_height_bottom)
            self.add_prompt("Door Valance Bottom",'CHECKBOX',props.door_valance_bottom)
        self.add_prompt("Left Side Full Height",'CHECKBOX',False)
        self.add_prompt("Right Side Full Height",'CHECKBOX',False)
        self.add_prompt("Valance Each Unit",'CHECKBOX',props.valance_each_unit)
        self.add_prompt("Valance Thickness",'DISTANCE',sn_unit.inch(.75))
    
    def add_sink_prompts(self):
        props = cabinet_properties.get_scene_props().carcass_defaults
        self.add_prompt("Sub Front Height",'DISTANCE', props.sub_front_height)
        self.add_prompt("Sub Front Thickness",'DISTANCE',sn_unit.inch(.75))
    
    def add_appliance_prompts(self):
        props = cabinet_properties.get_scene_props().carcass_defaults
        self.add_prompt("Remove Left Side", 'CHECKBOX', False)
        self.add_prompt("Remove Right Side", 'CHECKBOX', False)

    def add_prompt_formulas(self):
        tt = self.get_prompt("Top Thickness").get_var('tt')
        bt = self.get_prompt("Bottom Thickness").get_var('bt')
        use_nailers = self.get_prompt("Use Nailers").get_var('use_nailers')
        nt = self.get_prompt("Nailer Thickness").get_var('nt')
        bkt = self.get_prompt("Back Thickness").get_var('bkt')
        tbkt = self.get_prompt("Thick Back Thickness").get_var('tbkt')
        use_thick_back = self.get_prompt("Use Thick Back").get_var('use_thick_back')
        remove_back = self.get_prompt("Remove Back").get_var('remove_back')
        Remove_Bottom = self.get_prompt('Remove Bottom').get_var('Remove_Bottom')
        if self.carcass_type in {'Base','Sink','Tall'}:
            kick_height = self.get_prompt("Toe Kick Height").get_var('kick_height')
        if self.carcass_type in {'Upper','Tall'}:
            vht = self.get_prompt("Valance Height Top").get_var('vht')
        if self.carcass_type == 'Upper':
            vhb = self.get_prompt("Valance Height Bottom").get_var('vhb')

        # Used to calculate the exterior opening for doors
        if self.carcass_type == 'Base':
            self.get_prompt('Top Inset').set_formula('tt',[tt])
            self.get_prompt('Bottom Inset').set_formula('kick_height+bt',[kick_height,bt])

        if self.carcass_type == 'Sink':
            Sub_Front_Height = self.get_prompt("Sub Front Height").get_var()
            self.get_prompt('Top Inset').set_formula('Sub_Front_Height',[Sub_Front_Height])
            self.get_prompt('Bottom Inset').set_formula('kick_height+bt',[kick_height,bt])

        if self.carcass_type == 'Tall':
            self.get_prompt('Top Inset').set_formula('vht+tt',[vht,tt])
            self.get_prompt('Bottom Inset').set_formula('kick_height+bt',[kick_height,bt])

        if self.carcass_type == 'Upper':
            self.get_prompt('Top Inset').set_formula('vht+tt',[vht,tt])
            self.get_prompt('Bottom Inset').set_formula('IF(Remove_Bottom,0,vhb+bt)',[vhb,bt,Remove_Bottom])

        if self.carcass_type == 'Suspended':
            self.get_prompt('Top Inset').set_formula('tt',[tt])
            self.get_prompt('Bottom Inset').set_formula('IF(Remove_Bottom,0,bt)',[bt,Remove_Bottom])

        self.get_prompt('Back Inset').set_formula('IF(use_nailers,nt,0)+IF(remove_back,0,IF(use_thick_back,tbkt,bkt))',[use_nailers,nt,bkt,tbkt,use_thick_back,remove_back])

        # region TODO XML Export

        # sgi = self.get_var('cabinetlib.spec_group_index','sgi')
        # lfe = self.get_var("Left Fin End",'lfe')
        # rfe = self.get_var("Right Fin End",'rfe')
        # Side_Pointer_Name = 'Cabinet_Unfinished_Side' + self.open_name
        # FE_Pointer_Name = 'Cabinet_Finished_Side' + self.open_name
        # Top_Pointer_Name = 'Cabinet_Top' + self.open_name
        # Bottom_Pointer_Name = 'Cabinet_Bottom' + self.open_name
        # Back_Pointer_Name = 'Cabinet_Back' + self.open_name
        # Thick_Back_Pointer_Name = 'Cabinet_Thick_Back' + self.open_name
        # Edgebanding_Pointer_Name = 'Cabinet_Body_Edges' + self.open_name

        # self.prompt('Left Side Thickness','IF(lfe,THICKNESS(sgi,"' + FE_Pointer_Name +'"),THICKNESS(sgi,"' + Side_Pointer_Name +'"))',[lfe,sgi])
        # self.prompt('Right Side Thickness','IF(rfe,THICKNESS(sgi,"' + FE_Pointer_Name +'"),THICKNESS(sgi,"' + Side_Pointer_Name +'"))',[rfe,sgi])
        # if self.carcass_type == "Sink" or self.remove_top:
        #     self.prompt('Top Thickness',value = 0)
        # else:
        #     self.prompt('Top Thickness','THICKNESS(sgi,"' + Top_Pointer_Name +'")',[sgi])
        # self.prompt('Bottom Thickness','THICKNESS(sgi,"' + Bottom_Pointer_Name +'")',[sgi])
        # if self.carcass_type in {'Base','Sink','Tall'}:
        #     self.prompt('Toe Kick Thickness','THICKNESS(sgi,"Cabinet_Toe_Kick")',[sgi])
        # if self.carcass_type == 'Sink':
        #     self.prompt('Sub Front Thickness','THICKNESS(sgi,"Cabinet_Sink_Sub_Front")',[sgi])
        # self.prompt('Back Thickness','IF(remove_back,0,IF(use_thick_back,THICKNESS(sgi,"' + Thick_Back_Pointer_Name +'"),THICKNESS(sgi,"' + Back_Pointer_Name +'")))',[sgi,use_thick_back,remove_back])
        # self.prompt('Thick Back Thickness','THICKNESS(sgi,"Cabinet_Thick_Back' + self.open_name +'")',[sgi])
        # self.prompt('Filler Thickness','THICKNESS(sgi,"Cabinet_Filler")',[sgi])
        # self.prompt('Nailer Thickness','THICKNESS(sgi,"Cabinet_Nailer")',[sgi])
        # if self.carcass_type in {'Tall','Upper'}:
        #     self.prompt('Valance Thickness','THICKNESS(sgi,"Cabinet_Valance")',[sgi])
        # self.prompt('Edgebanding Thickness','EDGE_THICKNESS(sgi,"' + Edgebanding_Pointer_Name + '")',[sgi])
        # endregion

    def add_base_sides(self):
        Width = self.obj_x.snap.get_var('location.x', 'Width')
        Height = self.obj_z.snap.get_var('location.z', 'Height')
        Depth = self.obj_y.snap.get_var('location.y', 'Depth')

        Toe_Kick_Height = self.get_prompt('Toe Kick Height').get_var()
        Left_Fin_End = self.get_prompt('Left Fin End').get_var()
        Right_Fin_End = self.get_prompt('Right Fin End').get_var()
        Left_Side_Thickness = self.get_prompt('Left Side Thickness').get_var()
        Right_Side_Thickness = self.get_prompt('Right Side Thickness').get_var()

        left_side = common_parts.add_panel(self)
        left_side.obj_bp["IS_BP_PANEL"] = True

        right_depth = left_side.get_prompt("Right Depth")
        right_depth.set_formula('fabs(Depth)', [Depth])

        left_side.add_prompt("Is Cutpart", 'CHECKBOX', True)
        left_side.loc_z('Toe_Kick_Height', [Toe_Kick_Height])
        left_side.dim_x('Height-Toe_Kick_Height', [Height, Toe_Kick_Height])
        left_side.rot_y(value=math.radians(-90))
        left_side.dim_y('Depth', [Depth])
        left_side.dim_z('-Left_Side_Thickness', [Left_Side_Thickness])
        left_side.get_prompt('Hide').set_formula('IF(Left_Fin_End,True,False)',[Left_Fin_End])
        add_side_height_dimension(left_side)

        right_side = common_parts.add_panel(self)
        right_side.obj_bp["IS_BP_PANEL"] = True
        
        left_depth = right_side.get_prompt("Left Depth")
        left_depth.set_formula('fabs(Depth)', [Depth])

        right_side.add_prompt("Is Cutpart",'CHECKBOX',True)
        right_side.loc_x('Width',[Width])
        right_side.loc_z('Toe_Kick_Height',[Toe_Kick_Height])
        right_side.dim_x('Height-Toe_Kick_Height', [Height, Toe_Kick_Height])
        right_side.rot_y(value=math.radians(-90))
        right_side.dim_y('Depth',[Depth])
        right_side.dim_z('Right_Side_Thickness',[Right_Side_Thickness])
        right_side.get_prompt('Hide').set_formula('IF(Right_Fin_End,True,False)',[Right_Fin_End])

    def add_appliance_sides(self):
        Width = self.obj_x.snap.get_var('location.x', 'Width')
        Height = self.obj_z.snap.get_var('location.z', 'Height')
        Depth = self.obj_y.snap.get_var('location.y', 'Depth')

        # Toe_Kick_Height = self.get_prompt('Toe Kick Height').get_var()
        Left_Fin_End = self.get_prompt('Left Fin End').get_var()
        Right_Fin_End = self.get_prompt('Right Fin End').get_var()
        Remove_Left_Side = self.get_prompt('Remove Left Side').get_var()
        Remove_Right_Side = self.get_prompt('Remove Right Side').get_var()
        Left_Side_Thickness = self.get_prompt('Left Side Thickness').get_var()
        Right_Side_Thickness = self.get_prompt('Right Side Thickness').get_var()

        left_side = common_parts.add_panel(self)
        left_side.obj_bp["IS_BP_PANEL"] = True

        right_depth = left_side.get_prompt("Right Depth")
        right_depth.set_formula('fabs(Depth)', [Depth])

        left_side.add_prompt("Is Cutpart", 'CHECKBOX', True)
        left_side.dim_x('Height', [Height])
        left_side.rot_y(value=math.radians(-90))
        left_side.dim_y('Depth', [Depth])
        left_side.dim_z('-Left_Side_Thickness', [Left_Side_Thickness])
        left_side.get_prompt('Hide').set_formula('IF(Remove_Left_Side,True,False)',[Remove_Left_Side])
        add_side_height_dimension(left_side)
  
        right_side = common_parts.add_panel(self)
        right_side.obj_bp["IS_BP_PANEL"] = True
        left_depth = right_side.get_prompt("Left Depth")
        left_depth.set_formula('fabs(Depth)', [Depth])

        right_side.add_prompt("Is Cutpart",'CHECKBOX',True)
        right_side.loc_x('Width',[Width])
        right_side.dim_x('Height', [Height])
        right_side.rot_y(value=math.radians(-90))
        right_side.dim_y('Depth',[Depth])
        right_side.dim_z('Right_Side_Thickness',[Right_Side_Thickness])
        right_side.get_prompt('Hide').set_formula('IF(Remove_Right_Side,True,False)',[Remove_Right_Side])

    def add_tall_sides(self):
        Width = self.obj_x.snap.get_var('location.x', 'Width')
        Height = self.obj_z.snap.get_var('location.z', 'Height')
        Depth = self.obj_y.snap.get_var('location.y', 'Depth')
        Toe_Kick_Height = self.get_prompt('Toe Kick Height').get_var()
        Left_Fin_End = self.get_prompt('Left Fin End').get_var()
        Right_Fin_End = self.get_prompt('Right Fin End').get_var()
        Left_Side_Thickness = self.get_prompt('Left Side Thickness').get_var()
        Right_Side_Thickness = self.get_prompt('Right Side Thickness').get_var()
        Left_Side_Full_Height = self.get_prompt('Left Side Full Height').get_var()
        Right_Side_Full_Height = self.get_prompt('Right Side Full Height').get_var()
        Top_Inset = self.get_prompt('Top Inset').get_var()
        Top_Thickness = self.get_prompt('Top Thickness').get_var()

        left_side = common_parts.add_panel(self)
        right_depth = left_side.get_prompt("Right Depth")
        right_depth.set_formula('fabs(Depth)', [Depth])
        left_side.loc_z('Toe_Kick_Height',[Toe_Kick_Height])
        left_side.dim_x('Height-Toe_Kick_Height+IF(Left_Side_Full_Height,0,-Top_Inset+Top_Thickness)',[Left_Side_Full_Height,Height,Toe_Kick_Height,Top_Thickness,Top_Inset])
        left_side.rot_y(value=math.radians(-90))
        left_side.dim_y('Depth',[Depth])
        left_side.dim_z('-Left_Side_Thickness',[Left_Side_Thickness])
        left_side.get_prompt('Hide').set_formula('IF(Left_Fin_End,True,False)',[Left_Fin_End])
        add_side_height_dimension(left_side)

        right_side = common_parts.add_panel(self)
        left_depth = right_side.get_prompt("Left Depth")
        left_depth.set_formula('fabs(Depth)', [Depth])
        right_side.loc_x('Width',[Width])
        right_side.loc_z('Toe_Kick_Height',[Toe_Kick_Height])
        right_side.dim_x('Height-Toe_Kick_Height+IF(Right_Side_Full_Height,0,-Top_Inset+Top_Thickness)',[Right_Side_Full_Height,Top_Thickness,Top_Inset,Height,Toe_Kick_Height])
        right_side.rot_y(value=math.radians(-90))
        right_side.dim_y('Depth',[Depth])
        right_side.dim_z('Right_Side_Thickness',[Right_Side_Thickness])
        right_side.get_prompt('Hide').set_formula('IF(Right_Fin_End,True,False)',[Right_Fin_End])

    def add_upper_sides(self):
        Width = self.obj_x.snap.get_var('location.x', 'Width')
        Height = self.obj_z.snap.get_var('location.z', 'Height')
        Depth = self.obj_y.snap.get_var('location.y', 'Depth')
        Left_Fin_End = self.get_prompt('Left Fin End').get_var()
        Right_Fin_End = self.get_prompt('Right Fin End').get_var()
        Left_Side_Thickness = self.get_prompt('Left Side Thickness').get_var()
        Right_Side_Thickness = self.get_prompt('Right Side Thickness').get_var()
        Left_Side_Full_Height = self.get_prompt('Left Side Full Height').get_var()
        Right_Side_Full_Height = self.get_prompt('Right Side Full Height').get_var()
        Valance_Height_Top = self.get_prompt('Valance Height Top').get_var()
        Valance_Height_Bottom = self.get_prompt('Valance Height Bottom').get_var()

        left_side = common_parts.add_panel(self)
        right_depth = left_side.get_prompt("Right Depth")
        right_depth.set_formula('fabs(Depth)', [Depth])
        left_side.loc_z('IF(Left_Side_Full_Height,0,-Valance_Height_Top)',[Left_Side_Full_Height,Valance_Height_Top])
        left_side.rot_y(value=math.radians(-90))
        left_side.dim_x('Height+IF(Left_Side_Full_Height,0,Valance_Height_Top+Valance_Height_Bottom)',[Height,Valance_Height_Bottom,Valance_Height_Top,Left_Side_Full_Height])
        left_side.dim_y('Depth',[Depth])
        left_side.dim_z('-Left_Side_Thickness',[Left_Side_Thickness])
        left_side.get_prompt('Hide').set_formula('IF(Left_Fin_End,True,False)',[Left_Fin_End])
        add_side_height_dimension(left_side)
        
        right_side = common_parts.add_panel(self)
        left_depth = right_side.get_prompt("Left Depth")
        left_depth.set_formula('fabs(Depth)', [Depth])
        right_side.loc_x('Width',[Width])
        right_side.loc_z('IF(Right_Side_Full_Height,0,-Valance_Height_Top)',[Right_Side_Full_Height,Valance_Height_Top])
        right_side.rot_y(value=math.radians(-90))
        right_side.dim_x('Height+IF(Right_Side_Full_Height,0,Valance_Height_Top+Valance_Height_Bottom)',[Height,Right_Side_Full_Height,Valance_Height_Top,Valance_Height_Bottom])
        right_side.dim_y('Depth',[Depth])
        right_side.dim_z('Right_Side_Thickness',[Right_Side_Thickness])
        right_side.get_prompt('Hide').set_formula('IF(Right_Fin_End,True,False)',[Right_Fin_End])

    def add_suspended_sides(self):
        Width = self.obj_x.snap.get_var('location.x', 'Width')
        Height = self.obj_z.snap.get_var('location.z', 'Height')
        Depth = self.obj_y.snap.get_var('location.y', 'Depth')
        Left_Fin_End = self.get_prompt('Left Fin End').get_var()
        Right_Fin_End = self.get_prompt('Right Fin End').get_var()
        Left_Side_Thickness = self.get_prompt('Left Side Thickness').get_var()
        Right_Side_Thickness = self.get_prompt('Right Side Thickness').get_var()

        left_side = common_parts.add_panel(self)
        right_depth = left_side.get_prompt("Right Depth")
        right_depth.set_formula('fabs(Depth)', [Depth])
        left_side.rot_y(value=math.radians(-90))
        left_side.dim_x('Height',[Height])
        left_side.dim_y('Depth',[Depth])
        left_side.dim_z('-Left_Side_Thickness',[Left_Side_Thickness])
        left_side.get_prompt('Hide').set_formula('IF(Left_Fin_End,True,False)',[Left_Fin_End])
        add_side_height_dimension(left_side)
        
        right_side = common_parts.add_panel(self)
        left_depth = right_side.get_prompt("Left Depth")
        left_depth.set_formula('fabs(Depth)', [Depth])
        right_side.loc_x('Width',[Width])
        right_side.rot_y(value=math.radians(-90))
        right_side.dim_x('Height',[Height])
        right_side.dim_y('Depth',[Depth])
        right_side.dim_z('Right_Side_Thickness',[Right_Side_Thickness])
        right_side.get_prompt('Hide').set_formula('IF(Right_Fin_End,True,False)',[Right_Fin_End])

    def add_fillers(self):
        width = self.obj_x.snap.get_var('location.x', 'width')
        height = self.obj_z.snap.get_var('location.z', 'height')
        depth = self.obj_y.snap.get_var('location.y', 'depth')        

        l_filler = self.get_prompt("Left Side Wall Filler").get_var('l_filler')
        r_filler = self.get_prompt("Right Side Wall Filler").get_var('r_filler')
        ft = self.get_prompt("Filler Thickness").get_var('ft')
        if self.carcass_type in {'Base','Sink','Tall'}:
            kick_height = self.get_prompt("Toe Kick Height").get_var('kick_height')
            
        left_filler = common_parts.add_filler(self)
        left_filler.set_name("Left Filler")
        left_filler.loc_y('depth',[depth])
        left_filler.loc_z('height',[height])
        left_filler.rot_x(value=math.radians(90))
        left_filler.rot_y(value=math.radians(90))
        left_filler.rot_z(value=math.radians(180))
        left_filler.dim_y('l_filler',[l_filler])
        left_filler.dim_z('ft',[ft])
        left_filler.get_prompt('Hide').set_formula('IF(l_filler>0,False,True)',[l_filler])
        
        right_filler = common_parts.add_filler(self)
        right_filler.set_name("Right Filler")
        right_filler.loc_x('width',[width])
        right_filler.loc_y('depth',[depth])
        right_filler.loc_z('height',[height])
        right_filler.rot_x(value=math.radians(90))
        right_filler.rot_y(value=math.radians(90))
        right_filler.dim_y('r_filler',[r_filler])
        right_filler.dim_z('-ft',[ft])
        right_filler.get_prompt('Hide').set_formula('IF(r_filler>0,False,True)',[r_filler])
        
        if self.carcass_type in {'Base','Sink','Tall'}:
            left_filler.dim_x('height-kick_height',[height,kick_height])
            right_filler.dim_x('height-kick_height',[height,kick_height])
            
        if self.carcass_type in {'Upper','Suspended'}:
            left_filler.dim_x('height',[height])
            right_filler.dim_x('height',[height])
            
    def add_full_top(self):
        Width = self.obj_x.snap.get_var('location.x', 'Width')
        Height = self.obj_z.snap.get_var('location.z', 'Height')
        Depth = self.obj_y.snap.get_var('location.y', 'Depth')

        Top_Thickness = self.get_prompt('Top Thickness').get_var()
        Left_Side_Thickness = self.get_prompt('Left Side Thickness').get_var()
        Right_Side_Thickness = self.get_prompt('Right Side Thickness').get_var()
        Top_Inset = self.get_prompt('Top Inset').get_var()
        
        if self.carcass_type == "Appliance":
            Remove_Left_Side = self.get_prompt('Remove Left Side').get_var()   
            Remove_Right_Side = self.get_prompt('Remove Right Side').get_var()

        top = common_parts.add_kd_shelf(self)
        if self.carcass_type != "Appliance":
            top.dim_x('Width-(Left_Side_Thickness+Right_Side_Thickness)',[Width,Left_Side_Thickness,Right_Side_Thickness])
            top.loc_x('Left_Side_Thickness',[Left_Side_Thickness])
        else:
            top.dim_x('Width-IF(Remove_Left_Side,0,Left_Side_Thickness)-IF(Remove_Right_Side,0,Right_Side_Thickness)',
                            [Width,Remove_Left_Side,Left_Side_Thickness,Remove_Right_Side,Right_Side_Thickness])
            top.loc_x('IF(Remove_Left_Side,0,Left_Side_Thickness)',[Remove_Left_Side,Left_Side_Thickness])
        top.dim_y('Depth',[Depth])
        top.dim_z('-Top_Thickness',[Top_Thickness])

        if self.carcass_type == "Upper":
            top.loc_z('IF(Height>0,2*Height-Top_Inset+Top_Thickness,-Top_Inset+Top_Thickness)',[Height,Top_Inset,Top_Thickness])
        else: 
            top.loc_z('IF(Height>0,Height-Top_Inset+Top_Thickness,-Top_Inset+Top_Thickness)',[Height,Top_Inset,Top_Thickness])

    def add_sink_top(self):
        Width = self.obj_x.snap.get_var('location.x', 'Width')
        Height = self.obj_z.snap.get_var('location.z', 'Height')
        Depth = self.obj_y.snap.get_var('location.y', 'Depth')
        Left_Side_Thickness = self.get_prompt('Left Side Thickness').get_var()
        Right_Side_Thickness = self.get_prompt('Right Side Thickness').get_var()
        Sub_Front_Height = self.get_prompt('Sub Front Height').get_var()
        Sub_Front_Thickness = self.get_prompt('Sub Front Thickness').get_var()
        
        front_s = add_part(self, PART_WITH_FRONT_EDGEBANDING)
        front_s.set_name(self.carcass_type + " Front Stretcher")
        front_s.dim_x('Width-(Left_Side_Thickness+Right_Side_Thickness)',[Width,Left_Side_Thickness,Right_Side_Thickness])
        front_s.dim_y('-Sub_Front_Height',[Sub_Front_Height])
        front_s.dim_z('-Sub_Front_Thickness',[Sub_Front_Thickness])
        front_s.loc_x('Left_Side_Thickness',[Left_Side_Thickness])
        front_s.loc_y('Depth',[Depth])
        front_s.loc_z('IF(Height>0,Height,0)',[Height])
        front_s.rot_x(value=math.radians(90))
        
    def add_bottom(self):
        Width = self.obj_x.snap.get_var('location.x', 'Width')
        Height = self.obj_z.snap.get_var('location.z', 'Height')
        Depth = self.obj_y.snap.get_var('location.y', 'Depth')

        Left_Side_Thickness = self.get_prompt('Left Side Thickness').get_var()
        Right_Side_Thickness = self.get_prompt('Right Side Thickness').get_var()
        Bottom_Thickness = self.get_prompt('Bottom Thickness').get_var()
        Remove_Bottom = self.get_prompt('Remove Bottom').get_var()
                
        bottom = common_parts.add_kd_shelf(self)
        # bottom.set_name(self.carcass_type + " Bottom")
        bottom.loc_x('Left_Side_Thickness',[Left_Side_Thickness])
        bottom.dim_x('Width-(Left_Side_Thickness+Right_Side_Thickness)',[Width,Left_Side_Thickness,Right_Side_Thickness])
        bottom.dim_y('Depth',[Depth])
        bottom.dim_z('Bottom_Thickness',[Bottom_Thickness])

        bottom.get_prompt('Hide').set_formula('Remove_Bottom',[Remove_Bottom])
        
        if self.carcass_type in {'Upper','Suspended'}:
            Bottom_Inset = self.get_prompt('Bottom Inset').get_var()
            bottom.loc_z('Height+Bottom_Inset-Bottom_Thickness',[Height,Bottom_Inset,Bottom_Thickness])
            
        if self.carcass_type in {'Base','Tall','Sink'}:
            Toe_Kick_Height = self.get_prompt('Toe Kick Height').get_var()
            bottom.loc_z('Toe_Kick_Height',[Toe_Kick_Height])
            
    def add_toe_kick(self):
        Width = self.obj_x.snap.get_var('location.x', 'Width')
        Depth = self.obj_y.snap.get_var('location.y', 'Depth')

        Toe_Kick_Height = self.get_prompt('Toe Kick Height').get_var()
        Toe_Kick_Setback = self.get_prompt('Toe Kick Setback').get_var()
        Left_Toe_Kick_Filler = self.get_prompt('Left Toe Kick Filler').get_var()
        Right_Toe_Kick_Filler = self.get_prompt('Right Toe Kick Filler').get_var()
        Left_Side_Thickness = self.get_prompt('Left Side Thickness').get_var()
        Right_Side_Thickness = self.get_prompt('Right Side Thickness').get_var()
        Remove_Bottom = self.get_prompt('Remove Bottom').get_var()
        
        kick = add_part(self, PART_WITH_FRONT_EDGEBANDING)
        kick.set_name("Toe Kick")

        kick.dim_x('Width+Left_Toe_Kick_Filler+Right_Toe_Kick_Filler',[Width,Left_Toe_Kick_Filler,Right_Toe_Kick_Filler])
        kick.dim_y('Toe_Kick_Height',[Toe_Kick_Height])
        kick.dim_z(value=sn_unit.inch(-0.75))

        kick.loc_x('-Left_Toe_Kick_Filler',[Left_Toe_Kick_Filler])
        kick.loc_y('Depth+Toe_Kick_Setback',[Depth,Toe_Kick_Setback])
        kick.rot_x(value=math.radians(90))
        kick.get_prompt('Hide').set_formula('Remove_Bottom', [Remove_Bottom])
    
    def add_leg_levelers(self):
        Width = self.obj_x.snap.get_var('location.x', 'Width')
        Depth = self.obj_y.snap.get_var('location.y', 'Depth')
        Toe_Kick_Height = self.get_prompt('Toe Kick Height').get_var()
        Toe_Kick_Setback = self.get_prompt('Toe Kick Setback').get_var()
        Left_Side_Thickness = self.get_prompt('Left Side Thickness').get_var()
        Right_Side_Thickness = self.get_prompt('Right Side Thickness').get_var()

        legs = add_part(self, LEG_LEVELERS)
        legs.set_name("Leg Levelers")
        legs.loc_x('Left_Side_Thickness',[Left_Side_Thickness])
        legs.dim_x('Width-(Left_Side_Thickness+Right_Side_Thickness)',[Width,Left_Side_Thickness,Right_Side_Thickness])
        legs.dim_y('Depth+Toe_Kick_Setback',[Depth,Toe_Kick_Setback])
        legs.dim_z('Toe_Kick_Height',[Toe_Kick_Height])
    
    def add_back(self):
        Width = self.obj_x.snap.get_var('location.x', 'Width')
        Height = self.obj_z.snap.get_var('location.z', 'Height')

        Left_Side_Thickness = self.get_prompt('Left Side Thickness').get_var()
        Right_Side_Thickness = self.get_prompt('Right Side Thickness').get_var()
        Top_Inset = self.get_prompt('Top Inset').get_var()
        Bottom_Inset = self.get_prompt('Bottom Inset').get_var()
        Back_Thickness = self.get_prompt('Back Thickness').get_var()
        Bottom_Thickness = self.get_prompt('Bottom Thickness').get_var()
        Top_Thickness = self.get_prompt('Top Thickness').get_var()
        Remove_Back = self.get_prompt('Remove Back').get_var()
        Remove_Bottom = self.get_prompt('Remove Bottom').get_var()
        if self.carcass_type in {'Base','Appliance','Tall','Sink'}:
            Toe_Kick_Height = self.get_prompt('Toe Kick Height').get_var()
        if self.carcass_type == "Appliance":
            Remove_Left_Side = self.get_prompt('Remove Left Side').get_var()   
            Remove_Right_Side = self.get_prompt('Remove Right Side').get_var()
        
        back = common_parts.add_back(self)
        # back.set_name(self.carcass_type + " Back")

        if self.carcass_type != 'Appliance':
            back.loc_x('Left_Side_Thickness',[Left_Side_Thickness])
        else:
            back.loc_x('IF(Remove_Left_Side,0,Left_Side_Thickness)',[Remove_Left_Side,Left_Side_Thickness])
        back.rot_y(value=math.radians(-90))
        back.rot_z(value=math.radians(-90))
        
        if self.carcass_type in {'Base','Sink'}:
            back.dim_x('fabs(Height)-IF(Remove_Bottom,0,Toe_Kick_Height+Bottom_Thickness)-Top_Thickness',[Height,Toe_Kick_Height,Bottom_Thickness,Remove_Bottom,Top_Thickness])
        elif self.carcass_type in {'Appliance'}:
            back.dim_x('fabs(Height)-Top_Thickness',[Height,Top_Thickness])
        elif self.carcass_type == 'Tall':
            back.dim_x('fabs(Height)-IF(Remove_Bottom,0,Toe_Kick_Height+Bottom_Thickness)-Top_Inset',[Height,Top_Inset,Toe_Kick_Height,Bottom_Thickness,Remove_Bottom])
        elif self.carcass_type in {'Upper','Suspended'}:
            back.dim_x('fabs(Height)-(Top_Inset+Bottom_Inset)',[Height,Top_Inset,Bottom_Inset])

        if self.carcass_type != 'Appliance':    
            back.dim_y('Width-(Left_Side_Thickness+Right_Side_Thickness)',[Width,Left_Side_Thickness,Right_Side_Thickness])
        else:
            back.dim_y('Width-IF(Remove_Left_Side,0,Left_Side_Thickness)-IF(Remove_Right_Side,0,Right_Side_Thickness)',
                            [Width,Remove_Left_Side,Left_Side_Thickness,Remove_Right_Side,Right_Side_Thickness])
        back.dim_z('-Back_Thickness',[Back_Thickness])
        back.get_prompt('Hide').set_formula('IF(Remove_Back,True,False)',[Remove_Back])
        
        if self.carcass_type in {'Base','Tall','Sink'}:
            back.loc_z('IF(Remove_Bottom,0,Toe_Kick_Height+Bottom_Thickness)',[Remove_Bottom,Toe_Kick_Height,Bottom_Thickness])
    
        if self.carcass_type in {'Upper','Suspended'}:
            back.loc_z('Height+Bottom_Inset',[Height,Bottom_Inset])
    
    def add_valances(self):
        Width = self.obj_x.snap.get_var('location.x', 'Width')
        Depth = self.obj_y.snap.get_var('location.y', 'Depth')
        Height = self.obj_z.snap.get_var('location.z', 'Height')
        Left_Side_Thickness = self.get_prompt('Left Side Thickness').get_var()
        Right_Side_Thickness = self.get_prompt('Right Side Thickness').get_var()
        Top_Inset = self.get_prompt('Top Inset').get_var()
        Top_Thickness = self.get_prompt('Top Thickness').get_var()
        Left_Fin_End = self.get_prompt('Left Fin End').get_var()
        Right_Fin_End = self.get_prompt('Right Fin End').get_var()
        Left_Side_Full_Height = self.get_prompt('Left Side Full Height').get_var()
        Right_Side_Full_Height = self.get_prompt('Right Side Full Height').get_var()
        Valance_Thickness = self.get_prompt("Valance Thickness").get_var()
        Valance_Each_Unit = self.get_prompt("Valance Each Unit").get_var()
        Valance_Height_Top = self.get_prompt("Valance Height Top").get_var()
        Valance_Height_Bottom = self.get_prompt("Valance Height Bottom").get_var()
        
        top_val = add_part(self, PART_WITH_FRONT_EDGEBANDING)
        top_val.set_name("Top Valance")
        top_val.loc_x('IF(OR(Left_Fin_End,Left_Side_Full_Height),Left_Side_Thickness,0)',[Left_Fin_End,Left_Side_Full_Height,Left_Side_Thickness])
        top_val.loc_y('Depth',[Depth])
        top_val.loc_z('IF(Height>0,Height-Top_Inset+Top_Thickness,-Top_Inset+Top_Thickness)',[Height,Top_Thickness,Top_Inset])
        top_val.rot_x(value=math.radians(90))
        top_val.dim_x('Width-(IF(OR(Left_Fin_End,Left_Side_Full_Height),Left_Side_Thickness,0)+IF(OR(Right_Fin_End,Right_Side_Full_Height),Right_Side_Thickness,0))',[Width,Right_Fin_End,Left_Fin_End,Left_Side_Full_Height,Left_Side_Thickness,Right_Side_Full_Height,Right_Side_Thickness])
        top_val.dim_y('Valance_Height_Top',[Valance_Height_Top])
        top_val.dim_z('-Valance_Thickness',[Valance_Thickness])
        top_val.get_prompt('Hide').set_formula('IF(AND(Valance_Each_Unit,Valance_Height_Top>0),False,True)',[Valance_Each_Unit,Valance_Height_Top])
        
        if self.carcass_type == 'Upper':
            bottom_val = add_part(self, PART_WITH_FRONT_EDGEBANDING)
            bottom_val.set_name("Bottom Valance")
            bottom_val.loc_x('IF(OR(Left_Fin_End,Left_Side_Full_Height),Left_Side_Thickness,0)',[Left_Fin_End,Left_Side_Full_Height,Left_Side_Thickness])
            bottom_val.loc_y('Depth',[Depth])
            bottom_val.loc_z('Height+Valance_Height_Bottom',[Height,Valance_Height_Bottom])
            bottom_val.rot_x(value=math.radians(90))
            bottom_val.dim_x('Width-(IF(OR(Left_Fin_End,Left_Side_Full_Height),Left_Side_Thickness,0)+IF(OR(Right_Fin_End,Right_Side_Full_Height),Right_Side_Thickness,0))',[Width,Right_Fin_End,Left_Fin_End,Left_Side_Full_Height,Left_Side_Thickness,Right_Side_Full_Height,Right_Side_Thickness])
            bottom_val.dim_y('-Valance_Height_Bottom',[Valance_Height_Bottom])
            bottom_val.dim_z('-Valance_Thickness',[Valance_Thickness])
            bottom_val.get_prompt('Hide').set_formula('IF(AND(Valance_Each_Unit,Valance_Height_Bottom>0),False,True)',[Valance_Each_Unit,Valance_Height_Bottom])
            
    def draw(self):
        props = cabinet_properties.get_scene_props().carcass_defaults
        self.create_assembly()

        self.add_common_carcass_prompts()
        if self.carcass_type == "Base":
            self.add_base_assembly_prompts()
            if not self.remove_top:
                self.add_full_top()
            self.add_back()
            self.add_bottom()
            self.add_base_sides()
            if props.use_leg_levelers:
                self.add_leg_levelers()

        if self.carcass_type == "Appliance":
            self.add_base_assembly_prompts()
            self.add_appliance_prompts()
            self.add_appliance_sides()
            if props.use_leg_levelers:
                self.add_leg_levelers()

        if self.carcass_type == "Tall":
            self.add_base_assembly_prompts()
            self.add_full_top()
            self.add_back()
            self.add_bottom()
            self.add_valance_prompts(add_bottom_valance=False)
            self.add_tall_sides()
            if props.use_leg_levelers:
                self.add_leg_levelers()
            
        if self.carcass_type == "Upper":
            self.flip_z = True
            self.add_full_top()
            self.add_back()
            self.add_bottom()
            self.add_valance_prompts(add_bottom_valance=True)
            self.add_valances()
            self.add_upper_sides()
            
        if self.carcass_type == "Sink":
            self.add_base_assembly_prompts()
            self.add_sink_prompts()
            self.add_sink_top()
            self.add_back()
            self.add_bottom()
            self.add_base_sides()
            if props.use_leg_levelers:
                self.add_leg_levelers()
                
        if self.carcass_type == "Suspended":
            self.flip_z = True
            self.add_suspended_sides()
            if not self.remove_top:
                self.add_full_top()
            self.add_back()
            self.add_bottom()

        self.add_fillers()

        self.add_prompt_formulas()
        
        self.update()
   
class Inside_Corner_Carcass(sn_types.Assembly):
    type_assembly = "INSERT"
    id_prompt = cabinet_properties.LIBRARY_NAME_SPACE + ".frameless_cabinet_prompts"
    library_name = "Carcasses"
    placement_type = ""
    
    carcass_type = "" # {Base, Tall, Upper}
    open_name = ""
    
    carcass_shape = "" # {Notched, Diagonal}
    left_right_depth = sn_unit.inch(23)

    def create_dimensions(self):
        create_dimensionss(self) # Call module level function to create/recreate door dim labels

    def update_dimensions(self):
        update_dimensions(self)  # Call module level function to find and update door dim labels

    def update(self):
        super().update()
        self.obj_bp["IS_BP_CARCASS"] = True   
        self.obj_bp["INSIDE_CORNER_CARCASS"] = True 
        self.obj_bp["CARCASS_TYPE"] = self.carcass_type

        if self.carcass_shape.upper() == 'NOTCHED':
            self.obj_bp["PROFILE_SHAPE_NOTCHED"] = True
        elif self.carcass_shape.upper() == 'DIAGONAL':
            self.obj_bp["PROFILE_SHAPE_DIAGONAL"] = True
        else:
            self.obj_bp["PROFILE_SHAPE_RECTANGLE"] = True
    
    def add_common_carcass_prompts(self):
        props = cabinet_properties.get_scene_props().size_defaults
        if self.carcass_type == 'Upper':
            self.left_right_depth = props.upper_cabinet_depth
        else:
            self.left_right_depth = props.base_cabinet_depth

        self.add_prompt("Left Fin End", 'CHECKBOX', False)
        self.add_prompt("Right Fin End", 'CHECKBOX', False)
        self.add_prompt("Left End Condition", 'COMBOBOX', 0, ['MP', 'EP'])
        self.add_prompt("Right End Condition", 'COMBOBOX', 0, ['MP', 'EP'])
        self.add_prompt("Left Side Wall Filler", 'DISTANCE', 0.0)
        self.add_prompt("Right Side Wall Filler", 'DISTANCE', 0.0)
        
        self.add_prompt("Cabinet Depth Left", 'DISTANCE', self.left_right_depth)
        self.add_prompt("Cabinet Depth Right", 'DISTANCE', self.left_right_depth)
        
        self.add_prompt("Left Side Thickness", 'DISTANCE', sn_unit.inch(.75))
        self.add_prompt("Right Side Thickness", 'DISTANCE', sn_unit.inch(.75))
        self.add_prompt("Top Thickness", 'DISTANCE', sn_unit.inch(.75))
        self.add_prompt("Bottom Thickness", 'DISTANCE', sn_unit.inch(.75))
        self.add_prompt("Back Thickness", 'DISTANCE', sn_unit.inch(.75))
        self.add_prompt("Thick Back Thickness", 'DISTANCE', sn_unit.inch(.75))
        self.add_prompt("Filler Thickness", 'DISTANCE', sn_unit.inch(.75))
        self.add_prompt("Nailer Thickness", 'DISTANCE', sn_unit.inch(.75))
        self.add_prompt("Edgebanding Thickness", 'DISTANCE', sn_unit.inch(.02))

        ppt_obj_insets = self.add_prompt_obj("Backing_Config")
        self.add_prompt("Back Inset", 'DISTANCE', sn_unit.inch(0), prompt_obj=ppt_obj_insets)
        self.add_prompt("Top Inset", 'DISTANCE', sn_unit.inch(0), prompt_obj=ppt_obj_insets)
        self.add_prompt("Bottom Inset", 'DISTANCE', sn_unit.inch(0), prompt_obj=ppt_obj_insets)
        
    def add_base_assembly_prompts(self):
        props = cabinet_properties.get_scene_props().carcass_defaults
        self.add_prompt("Toe Kick Height", 'DISTANCE', props.toe_kick_height)
        self.add_prompt("Toe Kick Setback", 'DISTANCE', props.toe_kick_setback)
        self.add_prompt("Toe Kick Thickness", 'DISTANCE', sn_unit.inch(.75))
        self.add_prompt("Left Toe Kick Filler", 'DISTANCE', 0.0)
        self.add_prompt("Right Toe Kick Filler", 'DISTANCE', 0.0)

    def add_valance_prompts(self,add_bottom_valance):
        props = cabinet_properties.get_scene_props().carcass_defaults
        self.add_prompt("Valance Height Top", 'DISTANCE', props.valance_height_top)
        self.add_prompt("Door Valance Top", 'CHECKBOX', props.door_valance_top)
        if add_bottom_valance:
            self.add_prompt("Valance Height Bottom", 'DISTANCE', props.valance_height_bottom)
            self.add_prompt("Door Valance Bottom", 'CHECKBOX', props.door_valance_bottom)
        self.add_prompt("Left Side Full Height", 'CHECKBOX', False)
        self.add_prompt("Right Side Full Height", 'CHECKBOX', False)
        self.add_prompt("Valance Each Unit", 'CHECKBOX', props.valance_each_unit)
        self.add_prompt("Valance Thickness", 'DISTANCE', sn_unit.inch(.75))
    
    def add_prompt_formuls(self):
        # sgi = self.get_var('cabinetlib.spec_group_index','sgi')
        tt = self.get_prompt("Top Thickness").get_var('tt')
        bt = self.get_prompt("Bottom Thickness").get_var('bt')
        bkt = self.get_prompt("Back Thickness").get_var('bkt')
        lfe = self.get_prompt("Left Fin End").get_var('lfe')
        rfe = self.get_prompt("Right Fin End").get_var('rfe')
        if self.carcass_type in {'Base','Sink','Tall'}:
            kick_height = self.get_prompt("Toe Kick Height").get_var('kick_height')
        if self.carcass_type in {'Upper','Tall'}:
            vht = self.get_prompt("Valance Height Top").get_var('vht')
        if self.carcass_type == 'Upper':
            vhb = self.get_prompt("Valance Height Bottom").get_var('vhb')
            
        Side_Pointer_Name = 'Cabinet_Unfinished_Side' + self.open_name
        FE_Pointer_Name = 'Cabinet_Finished_Side' + self.open_name
        Top_Pointer_Name = 'Cabinet_Top' + self.open_name
        Bottom_Pointer_Name = 'Cabinet_Bottom' + self.open_name
        Thick_Back_Pointer_Name = 'Cabinet_Thick_Back' + self.open_name
        Edgebanding_Pointer_Name = 'Cabinet_Body_Edges' + self.open_name            
            
        # self.get_prompt('Left Side Thickness').set_formula('IF(lfe,THICKNESS(sgi,"' + FE_Pointer_Name +'"),THICKNESS(sgi,"' + Side_Pointer_Name +'"))',[lfe,sgi])
        # self.get_prompt('Right Side Thickness').set_formula('IF(rfe,THICKNESS(sgi,"' + FE_Pointer_Name +'"),THICKNESS(sgi,"' + Side_Pointer_Name +'"))',[rfe,sgi])
        # self.get_prompt('Top Thickness').set_formula('THICKNESS(sgi,"' + Top_Pointer_Name +'")',[sgi])
        # self.get_prompt('Bottom Thickness').set_formula('THICKNESS(sgi,"' + Bottom_Pointer_Name +'")',[sgi])
        # if self.carcass_type in {'Base','Sink','Tall'}:
        #     self.get_prompt('Toe Kick Thickness').set_formula('THICKNESS(sgi,"Cabinet_Toe_Kick")',[sgi])
        # if self.carcass_type == 'Sink':
        #     self.get_prompt('Sub Front Thickness').set_formula('THICKNESS(sgi,"Sink_Sub_Front")',[sgi])
        # self.get_prompt('Back Thickness').set_formula('THICKNESS(sgi,"' + Thick_Back_Pointer_Name +'")',[sgi])
        # self.get_prompt('Thick Back Thickness').set_formula('THICKNESS(sgi,"Cabinet_Thick_Back' + self.open_name +'")',[sgi])
        # self.get_prompt('Filler Thickness').set_formula('THICKNESS(sgi,"Cabinet_Filler")',[sgi])
        # self.get_prompt('Nailer Thickness').set_formula('THICKNESS(sgi,"Cabinet_Nailer")',[sgi])
        # if self.carcass_type in {'Tall','Upper'}:
        #     self.get_prompt('Valance Thickness').set_formuula('THICKNESS(sgi,"Cabinet_Valance")',[sgi])
        # self.get_prompt('Edgebanding Thickness').set_formula('EDGE_THICKNESS(sgi,"' + Edgebanding_Pointer_Name + '")',[sgi])
        
        if self.carcass_type == 'Base':
            self.get_prompt('Top Inset').set_formula('tt',[tt])
            self.get_prompt('Bottom Inset').set_formula('kick_height+bt',[kick_height,bt])
        if self.carcass_type == 'Sink':
            self.get_prompt('Top Inset').set_formula(value = sn_unit.inch(.75))
            self.get_prompt('Bottom Inset').set_formula('kick_height+bt',[kick_height,bt])
        if self.carcass_type == 'Tall':
            self.get_prompt('Top Inset').set_formula('vht+tt',[vht,tt])
            self.get_prompt('Bottom Inset').set_formula('kick_height+bt',[kick_height,bt])
        if self.carcass_type == 'Upper':
            self.get_prompt('Top Inset').set_formula('vht+tt',[vht,tt])
            self.get_prompt('Bottom Inset').set_formula('vhb+bt',[vhb,bt])
        if self.carcass_type == 'Suspended':
            self.get_prompt('Top Inset').set_formula('tt',[tt])
            self.get_prompt('Bottom Inset').set_formula('bt',[bt])
        
        self.get_prompt('Back Inset').set_formula('bkt',[bkt])
    
    def add_sides(self):
        props = cabinet_properties.get_scene_props().carcass_defaults
        width = self.obj_x.snap.get_var('location.x','width')
        height = self.obj_z.snap.get_var('location.z','height')
        depth = self.obj_y.snap.get_var('location.y','depth')
        if self.carcass_type in {'Base','Tall'}:
            Toe_Kick_Height = self.get_prompt('Toe Kick Height').get_var()
            Toe_Kick_Setback = self.get_prompt('Toe Kick Setback').get_var()
            Toe_Kick_Thickness = self.get_prompt('Toe Kick Thickness').get_var()
        Left_Side_Thickness = self.get_prompt('Left Side Thickness').get_var()
        Right_Side_Thickness = self.get_prompt('Right Side Thickness').get_var()
        Cabinet_Depth_Left = self.get_prompt("Cabinet Depth Left").get_var()
        Cabinet_Depth_Right = self.get_prompt("Cabinet Depth Right").get_var()
    
        if self.carcass_type in {"Base","Tall","Sink"}:
            left_side = add_part(self, PART_WITH_FRONT_EDGEBANDING)
            left_side.set_name(self.carcass_type + " Left Side")
            left_side.rot_y(value=math.radians(-90))
            left_side.loc_y('depth',[depth])
            left_side.loc_z('Toe_Kick_Height', [Toe_Kick_Height])
            left_side.dim_x('height-Toe_Kick_Height', [height, Toe_Kick_Height])
            left_side.dim_y('-Cabinet_Depth_Left', [Cabinet_Depth_Left])
            left_side.dim_z('-Left_Side_Thickness', [Left_Side_Thickness])
            left_side.rot_z(value=math.radians(90))
            add_side_height_dimension(left_side)
        
            right_side = add_part(self, PART_WITH_FRONT_EDGEBANDING)
            right_side.set_name(self.carcass_type + " Right Side")
            right_side.loc_x('width',[width])
            right_side.loc_z('Toe_Kick_Height', [Toe_Kick_Height])
            right_side.rot_y(value=math.radians(-90))
            right_side.dim_x('height-Toe_Kick_Height', [height, Toe_Kick_Height])
            right_side.dim_y('-Cabinet_Depth_Right', [Cabinet_Depth_Right])
            right_side.dim_z('Right_Side_Thickness', [Right_Side_Thickness])

        if self.carcass_type in {"Upper","Suspended"}:
            left_side = add_part(self, PART_WITH_FRONT_AND_BOTTOM_EDGEBANDING)
            left_side.set_name(self.carcass_type + " Left Side")
            left_side.rot_y(value=math.radians(-90))
            left_side.loc_y('depth',[depth])
            left_side.dim_x('height',[height])
            left_side.dim_y('-Cabinet_Depth_Left',[Cabinet_Depth_Left])
            left_side.dim_z('-Left_Side_Thickness',[Left_Side_Thickness])
            left_side.rot_z(value=math.radians(90))
            add_side_height_dimension(left_side)
        
            right_side = add_part(self, PART_WITH_FRONT_AND_BOTTOM_EDGEBANDING)
            right_side.set_name(self.carcass_type + " Right Side")
            right_side.loc_x('width',[width])
            right_side.rot_y(value=math.radians(-90))
            right_side.dim_x('height',[height])
            right_side.dim_y('-Cabinet_Depth_Right',[Cabinet_Depth_Right])
            right_side.dim_z('Right_Side_Thickness',[Right_Side_Thickness])

    def add_fillers(self):
        Width = self.obj_x.snap.get_var('location.x','Width')
        Depth = self.obj_y.snap.get_var('location.y','Depth')
        Height = self.obj_z.snap.get_var('location.z','Height')
        Left_Side_Wall_Filler = self.get_prompt("Left Side Wall Filler").get_var()
        Right_Side_Wall_Filler = self.get_prompt("Right Side Wall Filler").get_var()
        Filler_Thickness = self.get_prompt("Filler Thickness").get_var()
        Cabinet_Depth_Left = self.get_prompt("Cabinet Depth Left").get_var()
        Cabinet_Depth_Right = self.get_prompt("Cabinet Depth Right").get_var()
        
        if self.carcass_type in {'Base','Sink','Tall'}:
            Toe_Kick_Height = self.get_prompt("Toe Kick Height").get_var()
            
        left_filler = add_part(self, PART_WITH_NO_EDGEBANDING)
        left_filler.set_name("Left Filler")
        left_filler.loc_x('Cabinet_Depth_Left',[Cabinet_Depth_Left])
        left_filler.loc_y('Depth',[Depth])
        left_filler.loc_z('Height',[Height])
        left_filler.rot_x(value=math.radians(90))
        left_filler.rot_y(value=math.radians(90))
        left_filler.rot_z(value=math.radians(-90))
        left_filler.dim_y('Left_Side_Wall_Filler',[Left_Side_Wall_Filler])
        left_filler.dim_z('Filler_Thickness',[Filler_Thickness])
        left_filler.get_prompt('Hide').set_formula('IF(Left_Side_Wall_Filler>0,False,True)',[Left_Side_Wall_Filler])
        # left_filler.cutpart('Cabinet_Filler')
        
        right_filler = add_part(self, PART_WITH_NO_EDGEBANDING)
        right_filler.set_name("Right Filler")
        right_filler.loc_x('Width',[Width])
        right_filler.loc_y('-Cabinet_Depth_Right',[Cabinet_Depth_Right])
        right_filler.loc_z('Height',[Height])
        right_filler.rot_x(value=math.radians(90))
        right_filler.rot_y(value=math.radians(90))
        right_filler.dim_y('Right_Side_Wall_Filler',[Right_Side_Wall_Filler])
        right_filler.dim_z('-Filler_Thickness',[Filler_Thickness])
        right_filler.get_prompt('Hide').set_formula('IF(Right_Side_Wall_Filler>0,False,True)',[Right_Side_Wall_Filler])
        # right_filler.cutpart('Cabinet_Filler')
        
        if self.carcass_type in {'Base','Sink','Tall'}:
            left_filler.dim_x('Height-Toe_Kick_Height',[Height,Toe_Kick_Height])
            right_filler.dim_x('Height-Toe_Kick_Height',[Height,Toe_Kick_Height])
            
        if self.carcass_type in {'Upper','Suspended'}:
            left_filler.dim_x('Height',[Height])
            right_filler.dim_x('Height',[Height])
            
    def add_full_top(self):
        Width = self.obj_x.snap.get_var('location.x','Width')
        Depth = self.obj_y.snap.get_var('location.y','Depth')
        Height = self.obj_z.snap.get_var('location.z','Height')
        Top_Thickness = self.get_prompt('Top Thickness').get_var()
        Left_Side_Thickness = self.get_prompt('Left Side Thickness').get_var()
        Right_Side_Thickness = self.get_prompt('Right Side Thickness').get_var()
        Cabinet_Depth_Left = self.get_prompt("Cabinet Depth Left").get_var()
        Cabinet_Depth_Right = self.get_prompt("Cabinet Depth Right").get_var()
        
        if self.carcass_shape == 'Diagonal':
            top = add_part(self, CHAMFERED_PART)
        if self.carcass_shape == 'Notched':
            top = add_part(self, CORNER_NOTCH_PART)
        
        top.set_name(self.carcass_type + " Top")
        top.dim_x('Width-Right_Side_Thickness',[Width,Right_Side_Thickness])
        top.dim_y('Depth+Left_Side_Thickness',[Depth,Left_Side_Thickness])
        top.dim_z('-Top_Thickness',[Top_Thickness])
        top.loc_z('IF(Height>0,Height,0)',[Height])
        # top.cutpart("Cabinet_Top"+self.open_name)
        top.get_prompt('Left Depth').set_formula('Cabinet_Depth_Left',[Cabinet_Depth_Left])
        top.get_prompt('Right Depth').set_formula('Cabinet_Depth_Right',[Cabinet_Depth_Right])
        # top.edgebanding('Cabinet_Body_Edges', l1 = True)
        
    def add_bottom(self):
        Width = self.obj_x.snap.get_var('location.x','Width')
        Depth = self.obj_y.snap.get_var('location.y','Depth')
        Height = self.obj_z.snap.get_var('location.z','Height')
        Left_Side_Thickness = self.get_prompt('Left Side Thickness').get_var()
        Right_Side_Thickness = self.get_prompt('Right Side Thickness').get_var()
        Bottom_Thickness = self.get_prompt('Bottom Thickness').get_var()
        Cabinet_Depth_Left = self.get_prompt("Cabinet Depth Left").get_var()
        Cabinet_Depth_Right = self.get_prompt("Cabinet Depth Right").get_var()
        
        if self.carcass_shape == 'Diagonal':
            bottom = add_part(self, CHAMFERED_PART)
        if self.carcass_shape == 'Notched':
            bottom = add_part(self, CORNER_NOTCH_PART)
            
        bottom.set_name(self.carcass_type + " Bottom")
        bottom.dim_x('Width-Right_Side_Thickness',[Width,Right_Side_Thickness])
        bottom.dim_y('Depth+Left_Side_Thickness',[Depth,Left_Side_Thickness])
        bottom.dim_z('Bottom_Thickness',[Bottom_Thickness])
        bottom.get_prompt('Left Depth').set_formula('Cabinet_Depth_Left',[Cabinet_Depth_Left])
        bottom.get_prompt('Right Depth').set_formula('Cabinet_Depth_Right',[Cabinet_Depth_Right])
        # bottom.cutpart("Cabinet_Bottom"+self.open_name)
        # bottom.edgebanding('Cabinet_Body_Edges', l1 = True)
        
        if self.carcass_type in {'Upper','Suspended'}:
            bottom.loc_z('Height',[Height])
            
        if self.carcass_type in {'Base','Tall','Sink'}:
            Toe_Kick_Height = self.get_prompt('Toe Kick Height').get_var()
            bottom.loc_z('Toe_Kick_Height',[Toe_Kick_Height])

    def add_backs(self):
        Width = self.obj_x.snap.get_var('location.x','Width')
        Depth = self.obj_y.snap.get_var('location.y','Depth')
        Height = self.obj_z.snap.get_var('location.z','Height')
        Right_Side_Thickness = self.get_prompt('Right Side Thickness').get_var()
        Top_Inset = self.get_prompt('Top Inset').get_var()
        Bottom_Inset = self.get_prompt('Bottom Inset').get_var()
        Back_Thickness = self.get_prompt('Back Thickness').get_var()

        r_back = common_parts.add_back(self)
        r_back.set_name(self.carcass_type + " Back")
        r_back.loc_x('Back_Thickness',[Back_Thickness])
        r_back.loc_z('IF(Height>0,Bottom_Inset,Height+Bottom_Inset)',[Bottom_Inset,Height])
        r_back.rot_y(value=math.radians(-90))
        r_back.rot_z(value=math.radians(-90))
        r_back.dim_x('fabs(Height)-(Top_Inset+Bottom_Inset)',[Height,Top_Inset,Bottom_Inset])
        r_back.dim_y('Width-(Back_Thickness+Right_Side_Thickness)',[Width,Back_Thickness,Right_Side_Thickness])
        r_back.dim_z('-Back_Thickness',[Back_Thickness])
        # r_back.cutpart("Cabinet_Thick_Back" + self.open_name)
        
        l_back = common_parts.add_back(self)
        l_back.set_name(self.carcass_type + " Back")
        l_back.loc_z('IF(Height>0,Bottom_Inset,Height+Bottom_Inset)',[Bottom_Inset,Height])
        l_back.rot_y(value=math.radians(-90))
        l_back.rot_z(value=math.radians(180))
        l_back.dim_x('fabs(Height)-(Top_Inset+Bottom_Inset)',[Height,Top_Inset,Bottom_Inset])
        l_back.dim_y('fabs(Depth)-Right_Side_Thickness',[Depth,Right_Side_Thickness])
        l_back.dim_z('Back_Thickness',[Back_Thickness])
        # l_back.cutpart("Cabinet_Thick_Back" + self.open_name)
        
    def add_valances(self):
        pass
    
    def add_toe_kick(self):
        props = cabinet_properties.get_scene_props().carcass_defaults
        self.add_prompt("Toe Kick Height", 'DISTANCE', props.toe_kick_height)
        self.add_prompt("Toe Kick Setback", 'DISTANCE', props.toe_kick_setback)

        Width = self.obj_x.snap.get_var('location.x', 'Width')
        Depth = self.obj_y.snap.get_var('location.y', 'Depth')
        Left_Depth = self.get_prompt('Cabinet Depth Left').get_var('Left_Depth')
        Right_Depth = self.get_prompt('Cabinet Depth Right').get_var('Right_Depth')
        Toe_Kick_Setback = self.get_prompt('Toe Kick Setback').get_var('Toe_Kick_Setback')
        Toe_Kick_Height = self.get_prompt('Toe Kick Height').get_var('Toe_Kick_Height')
        LPT = self.get_prompt('Left Side Thickness').get_var("LPT")
        RPT = self.get_prompt('Right Side Thickness').get_var("RPT")

        tk_path = path.join(closet_paths.get_library_path(), "/Products - Basic/Toe Kick.png")
        wm_props = bpy.context.window_manager.snap

        left_tk = wm_props.get_asset(tk_path)
        left_tk.draw()
        left_tk.obj_bp.parent = self.obj_bp
        left_tk.obj_bp["ID_PROMPT"] = left_tk.id_prompt
        left_tk.obj_bp.snap.comment_2 = "1034"
        left_tk.loc_y('Depth', [Depth])
        left_tk.rot_z(value=math.radians(90))
        left_tk.dim_x('-Depth+INCH(0.75)/2', [Depth])
        left_tk.dim_y('-Left_Depth+Toe_Kick_Setback', [Left_Depth, Toe_Kick_Setback])
        left_tk.get_prompt('Toe Kick Height').set_formula('Toe_Kick_Height', [Toe_Kick_Height])
        left_depth_amount = left_tk.get_prompt("Extend Depth Amount").get_var("left_depth_amount")

        right_tk = wm_props.get_asset(tk_path)
        right_tk.draw()
        right_tk.obj_bp.parent = self.obj_bp
        right_tk.obj_bp.snap.comment_2 = "1034"
        right_tk.loc_x(
            'Left_Depth-Toe_Kick_Setback-INCH(0.75)/2+left_depth_amount',
            [Left_Depth, Toe_Kick_Setback, left_depth_amount])
        right_tk.dim_x(
            'Width-Left_Depth+Toe_Kick_Setback+INCH(0.75)/2-left_depth_amount',
            [Width, Left_Depth, Toe_Kick_Setback, left_depth_amount])
        right_tk.dim_y('-Right_Depth+Toe_Kick_Setback', [Right_Depth, Toe_Kick_Setback])
        right_tk.get_prompt('Toe Kick Height').set_formula('Toe_Kick_Height', [Toe_Kick_Height])

        if self.carcass_shape == 'Diagonal':
            angle_kick = common_parts.add_toe_kick(self)
            angle_kick.set_name("Angle Kick")
            angle_kick.loc_x(
                'Left_Depth-Toe_Kick_Setback-INCH(0.75)+.00635',
                [Left_Depth, Toe_Kick_Setback])
            angle_kick.loc_y('Depth+3*INCH(0.75)/2-.00635', [Depth])
            angle_kick.rot_x(value=math.radians(90))
            angle_kick.rot_z(
                '-atan((Depth+Right_Depth-Toe_Kick_Setback)'
                '/(Width-Left_Depth+Toe_Kick_Setback))',
                [Width, Depth, Right_Depth, Left_Depth, Toe_Kick_Setback])
            angle_kick.dim_x(
                'sqrt((Width-Left_Depth+Toe_Kick_Setback-INCH(0.75))**2'
                '+(Depth+Right_Depth-Toe_Kick_Setback)**2)',
                [Width, Depth, Left_Depth, Right_Depth,
                Toe_Kick_Setback])
            angle_kick.dim_y('Toe_Kick_Height', [Toe_Kick_Height])
            angle_kick.dim_z('INCH(0.75)')

    def draw(self):
        self.create_assembly()
        self.add_common_carcass_prompts()
        
        if self.carcass_type in {"Base","Tall"}:
            self.add_base_assembly_prompts()
        if self.carcass_type == "Base":
            self.add_toe_kick()
        if self.carcass_type == "Tall":
            self.add_valance_prompts(add_bottom_valance=False)
        elif self.carcass_type == "Upper":
            self.add_valance_prompts(add_bottom_valance=True)

        self.add_prompt_formuls()
        self.add_sides()
        self.add_full_top()
        self.add_bottom()
        self.add_backs()
        self.add_fillers()

        self.update()

class Island_Carcass(sn_types.Assembly):

    type_assembly = "INSERT"
    id_prompt = cabinet_properties.LIBRARY_NAME_SPACE + ".frameless_cabinet_prompts"
    library_name = "Carcasses"
    placement_type = ""

    carcass_type = ""  # {Base, Sink, Appliance?}
    carcass_shape = 'RECTANGLE'
    open_name = ""

    opening_qty = 1
    double_sided = False

    front_calculator = None
    front_calculator_name = "Front Row Widths Calculator"
    front_calculator_obj_name = "Front Row Widths Distance Obj"   
    back_calculator = None
    back_calculator_name = "Back Row Widths Calculator"
    back_calculator_obj_name = "Back Row Widths Distance Obj" 

    opening_1_width = 0
    opening_2_width = 0
    opening_3_width = 0
    opening_4_width = 0
    opening_5_width = 0
    opening_6_width = 0
    opening_7_width = 0
    opening_8_width = 0

    def create_dimensions(self):
        create_dimensions(self) # Call module level function to create/recreate door dim labels

    def update_dimensions(self):
        update_dimensions(self)  # Call module level function to find and update door dim labels

    def add_calculator(self, amt):
        Width = self.obj_x.snap.get_var('location.x', 'Width')
        Left_Side_Thickness = self.get_prompt('Left Side Thickness').get_var()
        Right_Side_Thickness = self.get_prompt('Right Side Thickness').get_var()

        calc_distance_obj = self.add_empty(self.front_calculator_obj_name)
        calc_distance_obj.empty_display_size = .001
        self.front_calculator = self.obj_prompts.snap.add_calculator(self.front_calculator_name, calc_distance_obj)
        self.front_calculator.set_total_distance("Width-(Left_Side_Thickness-Right_Side_Thickness)*{}".format(str(amt - 1)), [Width, Left_Side_Thickness, Right_Side_Thickness])

        if self.double_sided:
            calc_distance_obj = self.add_empty(self.back_calculator_obj_name)
            calc_distance_obj.empty_display_size = .001
            self.back_calculator = self.obj_prompts.snap.add_calculator(self.back_calculator_name, calc_distance_obj)
            self.back_calculator.set_total_distance("Width-(Left_Side_Thickness-Right_Side_Thickness)*{}".format(str(amt - 1)), [Width, Left_Side_Thickness, Right_Side_Thickness])

    def add_calculator_prompts(self, amt):
        self.front_calculator.prompts.clear()
        if self.double_sided:
            self.back_calculator.prompts.clear()

        cols = int(self.opening_qty / 2) if self.double_sided else self.opening_qty
        for col in range(0, cols):
            for row in range (0,2):
                if row == ISLAND_FRONT_ROW or (self.double_sided and row == ISLAND_BACK_ROW):
                    opening_nbr = str(col+1) if row == ISLAND_FRONT_ROW else str(cols+col+1)
                    if row == ISLAND_FRONT_ROW:
                        prompt = self.front_calculator.add_calculator_prompt("Opening " + str(opening_nbr) + " Width")
                    else:
                        prompt = self.back_calculator.add_calculator_prompt("Opening " + str(opening_nbr) + " Width")
                    size = eval("self.opening_" + str(opening_nbr) + "_width")
                    if size > 0:
                        prompt.set_value(size)
                        prompt.equal = False

    def get_calculator_widths(self, row, part_nbr):
        opening_width = 0
        loc_x_exp = ""
        loc_x_vars = []

        if int(row) == ISLAND_FRONT_ROW:
            calculator = self.get_calculator('Front Row Widths Calculator')
            start_col = 1
        else:
            calculator = self.get_calculator('Back Row Widths Calculator')
            opening_qty = len(calculator.prompts)*2
            start_col = int(opening_qty / 2 + 1)
        
        width_prompt = calculator.get_calculator_prompt('Opening {} Width'.format(part_nbr))
        opening_width = width_prompt.get_var(calculator.name, 'Opening_{}_Width'.format(part_nbr))

        for col in range(start_col, int(part_nbr)):
            loc_x_exp += "Opening_{}_Width".format(col)
            if col != int(part_nbr) - 1: 
                loc_x_exp += "+"
            temp_prompt = eval("calculator.get_calculator_prompt('Opening {} Width')".format(str(col)))
            temp_width = eval("temp_prompt.get_var(calculator.name, 'Opening_{}_Width')".format(str(col)))  
            loc_x_vars.append(temp_width)
       
        return loc_x_exp, loc_x_vars, opening_width

    def update(self):
        super().update()
        self.obj_bp["IS_BP_CARCASS"] = True
        self.obj_bp["ISLAND_CARCASS"] = True
        self.obj_bp["PROFILE_SHAPE_RECTANGLE"] = True 
        self.obj_bp["CARCASS_TYPE"] = 'Island'
        if self.double_sided:
            self.obj_bp["DOUBLE_SIDED"] = True

    def add_common_carcass_prompts(self):
        props = cabinet_properties.get_scene_props().carcass_defaults
        size_props = cabinet_properties.get_scene_props().size_defaults
        self.add_prompt("Double Sided", 'CHECKBOX', self.double_sided)
        self.add_prompt("Chase Depth", 'DISTANCE', size_props.island_chase_depth)
        self.add_prompt("Chase Cap Thickness", 'DISTANCE', sn_unit.inch(.75))
        for i in range(1, self.opening_qty + 1):
            self.add_prompt("Carcass Subtype " + str(i), 'COMBOBOX', 0)

        self.add_prompt("Opening Width", 'DISTANCE', size_props.island_cabinet_width)
        self.add_prompt("Front Row Depth", 'DISTANCE', size_props.island_cabinet_depth)
        self.add_prompt("Back Row Depth", 'DISTANCE', size_props.island_cabinet_depth)

        self.add_prompt("Left Fin End", 'CHECKBOX', False)
        self.add_prompt("Right Fin End", 'CHECKBOX', False)
        self.add_prompt("Left Side Wall Filler", 'DISTANCE', 0.0)
        self.add_prompt("Right Side Wall Filler", 'DISTANCE', 0.0)
        self.add_prompt("Use Nailers", 'CHECKBOX', props.use_nailers)
        self.add_prompt("Nailer Width", 'DISTANCE', props.nailer_width)
        self.add_prompt("Center Nailer Switch", 'DISTANCE', props.center_nailer_switch)
        self.add_prompt("Use Thick Back", 'CHECKBOX', props.use_thick_back)
        self.add_prompt("Remove Back", 'CHECKBOX', props.remove_back)
        self.add_prompt("Remove Bottom", 'CHECKBOX', False)

        if self.carcass_type in {'Base'} and not props.use_full_tops:
            self.add_prompt("Stretcher Width", 'DISTANCE', props.stretcher_width)

        self.add_prompt("Left Side Thickness", 'DISTANCE', sn_unit.inch(.75))
        self.add_prompt("Right Side Thickness", 'DISTANCE', sn_unit.inch(.75))
        self.add_prompt("Top Thickness", 'DISTANCE', sn_unit.inch(.75))
        self.add_prompt("Bottom Thickness", 'DISTANCE', sn_unit.inch(.75))
        self.add_prompt("Back Thickness", 'DISTANCE', sn_unit.inch(.75))
        self.add_prompt("Thick Back Thickness", 'DISTANCE', sn_unit.inch(.75))
        self.add_prompt("Filler Thickness", 'DISTANCE', sn_unit.inch(.75))
        self.add_prompt("Nailer Thickness", 'DISTANCE', sn_unit.inch(.75))
        self.add_prompt("Edgebanding Thickness", 'DISTANCE', sn_unit.inch(.02))

        # Create separate prompts obj for insets
        ppt_obj_insets = self.add_prompt_obj("Backing_Config")
        self.add_prompt("Back Inset", 'DISTANCE', sn_unit.inch(0), prompt_obj=ppt_obj_insets)
        self.add_prompt("Top Inset", 'DISTANCE', sn_unit.inch(0), prompt_obj=ppt_obj_insets)
        self.add_prompt("Bottom Inset", 'DISTANCE', sn_unit.inch(0), prompt_obj=ppt_obj_insets)

    def add_base_assembly_prompts(self):
        props = cabinet_properties.get_scene_props().carcass_defaults
        self.add_prompt("Toe Kick Height",'DISTANCE', props.toe_kick_height)
        self.add_prompt("Toe Kick Setback",'DISTANCE', props.toe_kick_setback)
        self.add_prompt("Toe Kick Thickness", 'DISTANCE', sn_unit.inch(.75))

    def add_sink_prompts(self):
        props = cabinet_properties.get_scene_props().carcass_defaults
        self.add_prompt("Sub Front Height",'DISTANCE', props.sub_front_height)
        self.add_prompt("Sub Front Thickness",'DISTANCE',sn_unit.inch(.75))
    
    def add_appliance_prompts(self):
        props = cabinet_properties.get_scene_props().carcass_defaults
        for i in range(1, self.opening_qty + 1):
            self.add_prompt("Remove Left Side " + str(i), 'CHECKBOX', False)
            self.add_prompt("Remove Right Side " + str(i), 'CHECKBOX', False)

    def add_prompt_formulas(self):
        tt = self.get_prompt("Top Thickness").get_var('tt')
        bt = self.get_prompt("Bottom Thickness").get_var('bt')
        use_nailers = self.get_prompt("Use Nailers").get_var('use_nailers')
        nt = self.get_prompt("Nailer Thickness").get_var('nt')
        bkt = self.get_prompt("Back Thickness").get_var('bkt')
        tbkt = self.get_prompt("Thick Back Thickness").get_var('tbkt')
        use_thick_back = self.get_prompt("Use Thick Back").get_var('use_thick_back')
        remove_back = self.get_prompt("Remove Back").get_var('remove_back')
        Remove_Bottom = self.get_prompt('Remove Bottom').get_var('Remove_Bottom')
        kick_height = self.get_prompt("Toe Kick Height").get_var('kick_height')

        # Used to calculate the exterior opening for doors
        self.get_prompt('Top Inset').set_formula('tt',[tt])
        self.get_prompt('Bottom Inset').set_formula('kick_height+bt',[kick_height,bt])

        self.get_prompt('Back Inset').set_formula('IF(use_nailers,nt,0)+IF(remove_back,0,IF(use_thick_back,tbkt,bkt))',[use_nailers,nt,bkt,tbkt,use_thick_back,remove_back])

    def add_base_sides(self):
        Height = self.obj_z.snap.get_var('location.z', 'Height')
        Front_Row_Depth = self.get_prompt('Front Row Depth').get_var()
        Back_Row_Depth = self.get_prompt('Back Row Depth').get_var()
        Chase_Depth = self.get_prompt('Chase Depth').get_var()

        Double_Sided = self.get_prompt('Double Sided').get_var()
        Toe_Kick_Height = self.get_prompt('Toe Kick Height').get_var()
        Left_Side_Thickness = self.get_prompt('Left Side Thickness').get_var()
        Right_Side_Thickness = self.get_prompt('Right Side Thickness').get_var()

        cols = int(self.opening_qty / 2) if self.double_sided else self.opening_qty

        for col in range(0, cols):
            for row in range (0,2):
                if row == ISLAND_FRONT_ROW or (self.double_sided and row == ISLAND_BACK_ROW):
                    part_nbr = str(col+1) if row == ISLAND_FRONT_ROW else str(cols+col+1)
                    Carcass_Subtype = self.get_prompt("Carcass Subtype " + part_nbr).get_var("Carcass_Subtype")
                    loc_x_exp, loc_x_vars, opening_width = self.get_calculator_widths(row, part_nbr)

                    left_side = common_parts.add_panel(self)
                    left_side.obj_bp["IS_BP_PANEL"] = True
                    part_label = "Base Left Side " + part_nbr if row == ISLAND_FRONT_ROW else "Base Right Side " + part_nbr
                    left_side.set_name(part_label)
                    left_side.add_prompt("Is Cutpart",'CHECKBOX',True)

                    if row == ISLAND_FRONT_ROW:
                        left_side.loc_x(loc_x_exp,loc_x_vars)
                    elif row == ISLAND_BACK_ROW:
                        loc_x_vars.append(Left_Side_Thickness)
                        left_side.loc_x(loc_x_exp + '+Left_Side_Thickness', loc_x_vars)
                        left_side.rot_z(value=math.radians(180))
                    if self.double_sided:
                        if row == ISLAND_FRONT_ROW:
                            left_side.loc_y('-Back_Row_Depth-Chase_Depth',[Back_Row_Depth,Chase_Depth])
                            left_side.dim_y('-Front_Row_Depth',[Front_Row_Depth])
                        elif row == ISLAND_BACK_ROW:
                            left_side.loc_y('-Back_Row_Depth',[Back_Row_Depth])
                            left_side.dim_y('-Back_Row_Depth',[Back_Row_Depth])
                    else:
                        left_side.dim_y('-Front_Row_Depth',[Front_Row_Depth])

                    left_side.loc_z('Toe_Kick_Height',[Toe_Kick_Height])
                    left_side.dim_x('Height-Toe_Kick_Height',[Height,Toe_Kick_Height])
                    left_side.rot_y(value=math.radians(-90))
                    left_side.dim_z('-Left_Side_Thickness',[Left_Side_Thickness])
                    left_side.get_prompt('Hide').set_formula('IF(Carcass_Subtype==' + str(ISLAND_APPLIANCE_CARCASS) + ',True,False)', [Carcass_Subtype])

                    add_side_height_dimension(left_side)
                    
                    right_side = common_parts.add_panel(self)
                    right_side.obj_bp["IS_BP_PANEL"] = True
                    part_label = "Base Right Side " + part_nbr if row == ISLAND_FRONT_ROW else "Base Left Side " + part_nbr
                    right_side.set_name(part_label)
                    right_side.add_prompt("Is Cutpart",'CHECKBOX',True)

                    if row == ISLAND_FRONT_ROW:
                        loc_x_vars.append(opening_width)
                        right_side.loc_x(loc_x_exp + '+Opening_' + part_nbr + '_Width',loc_x_vars)
                    else:
                        loc_x_vars.extend([opening_width, Right_Side_Thickness])
                        right_side.loc_x(loc_x_exp + '-Right_Side_Thickness+Opening_' + part_nbr + '_Width', loc_x_vars)
                        right_side.rot_z(value=math.radians(180))
                    if self.double_sided:
                        if row == ISLAND_FRONT_ROW:
                            right_side.loc_y('-Back_Row_Depth-Chase_Depth',[Back_Row_Depth,Chase_Depth])
                            right_side.dim_y('-Front_Row_Depth',[Front_Row_Depth])
                        elif row == ISLAND_BACK_ROW:
                            right_side.loc_y('-Back_Row_Depth',[Back_Row_Depth])
                            right_side.dim_y('-Back_Row_Depth',[Back_Row_Depth])
                    else:
                        right_side.dim_y('-Front_Row_Depth',[Front_Row_Depth])
                    right_side.loc_z('Toe_Kick_Height',[Toe_Kick_Height])
                    right_side.dim_x('Height-Toe_Kick_Height',[Height,Toe_Kick_Height])
                    right_side.rot_y(value=math.radians(-90))
                    right_side.dim_z('Right_Side_Thickness',[Right_Side_Thickness])
                    right_side.get_prompt('Hide').set_formula('IF(Carcass_Subtype==' + str(ISLAND_APPLIANCE_CARCASS) + ',True,False)', [Carcass_Subtype])

    def add_appliance_sides(self):
        Height = self.obj_z.snap.get_var('location.z', 'Height')
        Front_Row_Depth = self.get_prompt('Front Row Depth').get_var()
        Back_Row_Depth = self.get_prompt('Back Row Depth').get_var()
        Chase_Depth = self.get_prompt('Chase Depth').get_var()

        Double_Sided = self.get_prompt('Double Sided').get_var()
        Left_Side_Thickness = self.get_prompt('Left Side Thickness').get_var()
        Right_Side_Thickness = self.get_prompt('Right Side Thickness').get_var()

        cols = int(self.opening_qty / 2) if self.double_sided else self.opening_qty

        for col in range(0, cols):
            for row in range (0,2):
                if row == ISLAND_FRONT_ROW or (self.double_sided and row == ISLAND_BACK_ROW):
                    part_nbr = str(col+1) if row == ISLAND_FRONT_ROW else str(cols+col+1)
                    Carcass_Subtype = self.get_prompt("Carcass Subtype " + part_nbr).get_var("Carcass_Subtype")
                    Remove_Left_Side = self.get_prompt("Remove Left Side " + part_nbr).get_var("Remove_Left_Side")
                    Remove_Right_Side = self.get_prompt("Remove Right Side " + part_nbr).get_var("Remove_Right_Side")
                    loc_x_exp, loc_x_vars, opening_width = self.get_calculator_widths(row, part_nbr)

                    left_side = common_parts.add_panel(self)
                    left_side.obj_bp["IS_BP_PANEL"] = True
                    part_label = "Appliance Left Side " + part_nbr if row == ISLAND_FRONT_ROW else "Appliance Right Side " + part_nbr
                    left_side.set_name(part_label)
                    left_side.add_prompt("Is Cutpart",'CHECKBOX',True)
                    
                    if row == ISLAND_FRONT_ROW:
                        left_side.loc_x(loc_x_exp,loc_x_vars)
                    elif row == ISLAND_BACK_ROW:
                        loc_x_vars.append(Left_Side_Thickness)
                        left_side.loc_x(loc_x_exp + "+Left_Side_Thickness", loc_x_vars)
                        left_side.rot_z(value=math.radians(180))
                    if self.double_sided:
                        if row == ISLAND_FRONT_ROW:
                            left_side.loc_y('-Back_Row_Depth-Chase_Depth',[Back_Row_Depth,Chase_Depth])
                            left_side.dim_y('-Front_Row_Depth',[Front_Row_Depth])
                        elif row == ISLAND_BACK_ROW:
                            left_side.loc_y('-Back_Row_Depth',[Back_Row_Depth])
                            left_side.dim_y('-Back_Row_Depth',[Back_Row_Depth])
                    else:
                        left_side.dim_y('-Front_Row_Depth',[Front_Row_Depth])

                    left_side.dim_x('Height', [Height])
                    left_side.rot_y(value=math.radians(-90))
                    left_side.dim_z('-Left_Side_Thickness', [Left_Side_Thickness])
                    
                    removal_prompt = "Remove_Left_Side" if row == ISLAND_FRONT_ROW else "Remove_Right_Side"
                    left_side.get_prompt('Hide').set_formula(
                        'IF(Carcass_Subtype==' + str(ISLAND_APPLIANCE_CARCASS) + ',IF(' + removal_prompt + ',True,False),True)', [Carcass_Subtype,Remove_Left_Side,Remove_Right_Side])
                    
                    # add_side_height_dimension(left_side)
            
                    right_side = common_parts.add_panel(self)
                    right_side.obj_bp["IS_BP_PANEL"] = True
                    part_label = "Appliance Right Side " + part_nbr if row == ISLAND_FRONT_ROW else "Appliance Left Side " + part_nbr
                    right_side.set_name(part_label)
                    right_side.add_prompt("Is Cutpart",'CHECKBOX',True)

                    if row == ISLAND_FRONT_ROW:
                        loc_x_vars.append(opening_width)
                        right_side.loc_x(loc_x_exp + "+Opening_" + part_nbr + "_Width",loc_x_vars)
                    else:
                        loc_x_vars.extend([opening_width, Right_Side_Thickness])
                        right_side.loc_x(loc_x_exp + "-Right_Side_Thickness+Opening_" + part_nbr + "_Width", loc_x_vars)
                        right_side.rot_z(value=math.radians(180))
                    if self.double_sided:
                        if row == ISLAND_FRONT_ROW:
                            right_side.loc_y('-Back_Row_Depth-Chase_Depth',[Back_Row_Depth,Chase_Depth])
                            right_side.dim_y('-Front_Row_Depth',[Front_Row_Depth])
                        elif row == ISLAND_BACK_ROW:
                            right_side.loc_y('-Back_Row_Depth',[Back_Row_Depth])
                            right_side.dim_y('-Back_Row_Depth',[Back_Row_Depth])
                    else:
                        right_side.dim_y('-Front_Row_Depth',[Front_Row_Depth])

                    right_side.dim_x('Height', [Height])
                    right_side.rot_y(value=math.radians(-90))
                    right_side.dim_z('Right_Side_Thickness',[Right_Side_Thickness])
                    
                    removal_prompt = "Remove_Right_Side" if row == ISLAND_FRONT_ROW else "Remove_Left_Side"
                    right_side.get_prompt('Hide').set_formula(
                        'IF(Carcass_Subtype==' + str(ISLAND_APPLIANCE_CARCASS) + ',IF(' + removal_prompt + ',True,False),True)', [Carcass_Subtype,Remove_Left_Side,Remove_Right_Side])

    def add_chase_caps(self):
        Height = self.obj_z.snap.get_var('location.z', 'Height')
        Width = self.obj_x.snap.get_var('location.x', 'Width')
        Front_Row_Depth = self.get_prompt('Front Row Depth').get_var()
        Back_Row_Depth = self.get_prompt('Back Row Depth').get_var()
        Chase_Depth = self.get_prompt('Chase Depth').get_var() 

        Chase_Cap_Thickness = self.get_prompt("Chase Cap Thickness").get_var()
        Toe_Kick_Height = self.get_prompt('Toe Kick Height').get_var()

        left_chase_cap = add_part(self, PART_WITH_FRONT_EDGEBANDING)
        left_chase_cap.set_name("Left Chase Cap")
        left_chase_cap.dim_x('Height',[Height])
        left_chase_cap.dim_y('-Chase_Depth',[Chase_Depth])
        left_chase_cap.dim_z('-Chase_Cap_Thickness', [Chase_Cap_Thickness])
        left_chase_cap.loc_y('-Back_Row_Depth',[Back_Row_Depth])
        left_chase_cap.rot_y(value=math.radians(-90))
        left_chase_cap.get_prompt('Hide').set_formula('IF(Chase_Depth>0,False,True)', [Chase_Depth])

        right_chase_cap = add_part(self, PART_WITH_FRONT_EDGEBANDING)
        right_chase_cap.set_name("Right Chase Cap")
        right_chase_cap.dim_x('Height',[Height])
        right_chase_cap.dim_y('-Chase_Depth',[Chase_Depth])
        right_chase_cap.dim_z('-Chase_Cap_Thickness', [Chase_Cap_Thickness])
        right_chase_cap.loc_x('Width-Chase_Cap_Thickness',[Width, Chase_Cap_Thickness])
        right_chase_cap.loc_y('-Back_Row_Depth',[Back_Row_Depth])
        right_chase_cap.rot_y(value=math.radians(-90))
        right_chase_cap.get_prompt('Hide').set_formula('IF(Chase_Depth>0,False,True)', [Chase_Depth])

    def add_backing_cap(self):
        Height = self.obj_z.snap.get_var('location.z', 'Height')
        Width = self.obj_x.snap.get_var('location.x', 'Width')

        Chase_Cap_Thickness = self.get_prompt("Chase Cap Thickness").get_var()
        Toe_Kick_Height = self.get_prompt('Toe Kick Height').get_var()

        backing_cap = add_part(self, PART_WITH_FRONT_EDGEBANDING)
        backing_cap.set_name("Backing Cap")
        backing_cap.dim_x('Height',[Height])
        backing_cap.dim_y('-Chase_Cap_Thickness',[Chase_Cap_Thickness])
        backing_cap.dim_z('-Width', [Width])

        backing_cap.loc_y('Chase_Cap_Thickness',[Chase_Cap_Thickness])
        backing_cap.rot_y(value=math.radians(-90))
    
    def add_full_top(self):
        Height = self.obj_z.snap.get_var('location.z', 'Height')
        Front_Row_Depth = self.get_prompt('Front Row Depth').get_var()
        Back_Row_Depth = self.get_prompt('Back Row Depth').get_var()
        Chase_Depth = self.get_prompt('Chase Depth').get_var()
        
        Double_Sided = self.get_prompt('Double Sided').get_var()
        Top_Thickness = self.get_prompt('Top Thickness').get_var()
        Left_Side_Thickness = self.get_prompt('Left Side Thickness').get_var()
        Right_Side_Thickness = self.get_prompt('Right Side Thickness').get_var()
        Top_Inset = self.get_prompt('Top Inset').get_var()
        
        cols = int(self.opening_qty / 2) if self.double_sided else self.opening_qty

        for col in range(0, cols):
            for row in range (0,2):
                if row == ISLAND_FRONT_ROW or (self.double_sided and row == ISLAND_BACK_ROW):
                    part_nbr = str(col+1) if row == ISLAND_FRONT_ROW else str(cols+col+1)
                    Carcass_Subtype = self.get_prompt("Carcass Subtype " + part_nbr).get_var("Carcass_Subtype")
                    loc_x_exp, loc_x_vars, opening_width = self.get_calculator_widths(row, part_nbr)

                    top = common_parts.add_kd_shelf(self)
                    top.set_name(self.carcass_type + " Top " + part_nbr)
                    
                    top.dim_z('-Top_Thickness',[Top_Thickness])
                    loc_x_vars.extend([opening_width,Left_Side_Thickness,Right_Side_Thickness])
                    if row == ISLAND_FRONT_ROW:
                        loc_x_vars.append(Left_Side_Thickness)
                        top.loc_x(loc_x_exp + '+Left_Side_Thickness', loc_x_vars)
                        top.dim_x('Opening_' + part_nbr + '_Width-(Left_Side_Thickness+Right_Side_Thickness)',loc_x_vars)
                        top.dim_y('-Front_Row_Depth',[Front_Row_Depth])
                    elif row == ISLAND_BACK_ROW:
                        loc_x_vars.extend([opening_width, Left_Side_Thickness])
                        top.loc_x(loc_x_exp + '-Left_Side_Thickness+Opening_' + part_nbr + '_Width', loc_x_vars)
                        top.dim_x('Opening_' + part_nbr + '_Width-(Left_Side_Thickness+Right_Side_Thickness)',loc_x_vars)
                        top.dim_y('-Back_Row_Depth',[Back_Row_Depth])
                        top.rot_z(value=math.radians(180))

                    if self.double_sided:
                        if row == ISLAND_FRONT_ROW:
                            top.loc_y('-Back_Row_Depth-Chase_Depth',[Back_Row_Depth,Chase_Depth])
                        elif row == ISLAND_BACK_ROW:
                            top.loc_y('-Back_Row_Depth',[Back_Row_Depth])
                    top.loc_z('IF(Height>0,Height-Top_Inset+Top_Thickness,-Top_Inset+Top_Thickness)',[Height,Top_Inset,Top_Thickness])
                  
                    top.get_prompt('Hide').set_formula('IF(Carcass_Subtype==' + str(ISLAND_BASE_CARCASS) + ',False,True)', [Carcass_Subtype])

    def add_sink_top(self):
        Height = self.obj_z.snap.get_var('location.z', 'Height')
        Front_Row_Depth = self.get_prompt('Front Row Depth').get_var()
        Back_Row_Depth = self.get_prompt('Back Row Depth').get_var()
        Chase_Depth = self.get_prompt('Chase Depth').get_var()

        Double_Sided = self.get_prompt('Double Sided').get_var()
        Left_Side_Thickness = self.get_prompt('Left Side Thickness').get_var()
        Right_Side_Thickness = self.get_prompt('Right Side Thickness').get_var()
        Sub_Front_Height = self.get_prompt('Sub Front Height').get_var()
        Sub_Front_Thickness = self.get_prompt('Sub Front Thickness').get_var()
        
        cols = int(self.opening_qty / 2) if self.double_sided else self.opening_qty

        for col in range(0, cols):
            for row in range (0,2):
                if row == ISLAND_FRONT_ROW or (self.double_sided and row == ISLAND_BACK_ROW):
                    part_nbr = str(col+1) if row == ISLAND_FRONT_ROW else str(cols+col+1)
                    Carcass_Subtype = self.get_prompt("Carcass Subtype " + part_nbr).get_var("Carcass_Subtype")
                    loc_x_exp, loc_x_vars, opening_width = self.get_calculator_widths(row, part_nbr)
                    
                    front_s = add_part(self, PART_WITH_FRONT_EDGEBANDING)
                    front_s.set_name(self.carcass_type + " Front Stretcher " + part_nbr)
                    
                    front_s.dim_y('-Sub_Front_Height',[Sub_Front_Height])
                    front_s.dim_z('-Sub_Front_Thickness',[Sub_Front_Thickness])

                    loc_x_vars.extend([opening_width, Left_Side_Thickness, Right_Side_Thickness])    
                    if row == ISLAND_FRONT_ROW:
                        front_s.loc_x(loc_x_exp + '+Left_Side_Thickness', loc_x_vars)
                        front_s.dim_x('Opening_' + part_nbr + '_Width-Left_Side_Thickness-Right_Side_Thickness',loc_x_vars)
                    elif row == ISLAND_BACK_ROW:
                        front_s.loc_x(loc_x_exp + '+Left_Side_Thickness', loc_x_vars)
                        front_s.dim_x('-Opening_' + part_nbr + '_Width+Left_Side_Thickness+Right_Side_Thickness',loc_x_vars)
                        front_s.rot_z(value=math.radians(180))

                    if self.double_sided and row == ISLAND_FRONT_ROW:
                        front_s.loc_y('-Front_Row_Depth-Back_Row_Depth-Chase_Depth',[Front_Row_Depth,Back_Row_Depth,Chase_Depth])
                    elif row == ISLAND_FRONT_ROW:
                        front_s.loc_y('-Front_Row_Depth',[Front_Row_Depth])
                    
                    front_s.loc_z('IF(Height>0,Height,0)',[Height])
                    front_s.rot_x(value=math.radians(90))

                    front_s.get_prompt('Hide').set_formula('IF(Carcass_Subtype==' + str(ISLAND_SINK_CARCASS) + ',False,True)', [Carcass_Subtype])

    def add_bottom(self):
        Height = self.obj_z.snap.get_var('location.z', 'Height')
        Front_Row_Depth = self.get_prompt('Front Row Depth').get_var()
        Back_Row_Depth = self.get_prompt('Back Row Depth').get_var()
        Chase_Depth = self.get_prompt('Chase Depth').get_var()
        
        Double_Sided = self.get_prompt('Double Sided').get_var()
        Left_Side_Thickness = self.get_prompt('Left Side Thickness').get_var()
        Right_Side_Thickness = self.get_prompt('Right Side Thickness').get_var()
        Bottom_Thickness = self.get_prompt('Bottom Thickness').get_var()
        Remove_Bottom = self.get_prompt('Remove Bottom').get_var()

        cols = int(self.opening_qty / 2) if self.double_sided else self.opening_qty

        for col in range(0, cols):
            for row in range (0,2):
                if row == ISLAND_FRONT_ROW or (self.double_sided and row == ISLAND_BACK_ROW):
                    part_nbr = str(col+1) if row == ISLAND_FRONT_ROW else str(cols+col+1)
                    Carcass_Subtype = self.get_prompt("Carcass Subtype " + part_nbr).get_var("Carcass_Subtype")
                    loc_x_exp, loc_x_vars, opening_width = self.get_calculator_widths(row, part_nbr)

                    bottom = common_parts.add_kd_shelf(self)
                    bottom.set_name(self.carcass_type + " Bottom " + part_nbr)

                    loc_x_vars.extend([opening_width, Left_Side_Thickness, Right_Side_Thickness])
                    if row == ISLAND_FRONT_ROW:
                        bottom.loc_x(loc_x_exp + '+Left_Side_Thickness', loc_x_vars)
                        bottom.dim_x('Opening_' + part_nbr + '_Width-Left_Side_Thickness-Right_Side_Thickness',loc_x_vars)
                    elif row == ISLAND_BACK_ROW:
                        bottom.loc_x(loc_x_exp + '+Left_Side_Thickness', loc_x_vars)
                        bottom.dim_x('-Opening_' + part_nbr + '_Width+Left_Side_Thickness+Right_Side_Thickness',loc_x_vars)
                        bottom.rot_z(value=math.radians(180))

                    if row == ISLAND_FRONT_ROW:
                        bottom.dim_y('-Front_Row_Depth',[Front_Row_Depth])
                    else:
                        bottom.dim_y('-Back_Row_Depth',[Back_Row_Depth])
                    bottom.dim_z('Bottom_Thickness',[Bottom_Thickness])

                    if self.double_sided:
                        if row == ISLAND_FRONT_ROW:
                            bottom.loc_y('-Back_Row_Depth-Chase_Depth',[Back_Row_Depth,Chase_Depth])
                            bottom.dim_y('-Front_Row_Depth',[Front_Row_Depth])
                        elif row == ISLAND_BACK_ROW:
                            bottom.loc_y('-Back_Row_Depth',[Back_Row_Depth])
                            bottom.dim_y('-Back_Row_Depth',[Back_Row_Depth])
  
                    Toe_Kick_Height = self.get_prompt('Toe Kick Height').get_var()
                    bottom.loc_z('Toe_Kick_Height',[Toe_Kick_Height])
                    
                    bottom.get_prompt('Hide').set_formula('IF(Carcass_Subtype!=' + str(ISLAND_APPLIANCE_CARCASS) + ',False,True)', [Carcass_Subtype])
            
    def get_row_opening_nbrs(self, row_nbr):
        if row_nbr == ISLAND_FRONT_ROW:
            start_nbr = 1
            if self.double_sided:
                end_nbr = int(self.opening_qty/2)
            else:
                end_nbr = int(self.opening_qty)
        elif row_nbr == ISLAND_BACK_ROW:
            start_nbr = int(self.opening_qty/2)+1
            end_nbr = int(self.opening_qty)
    
        return start_nbr, end_nbr

    def create_toe_kick(self, row_nbr, start_nbr, end_nbr):
        props = cabinet_properties.get_scene_props().carcass_defaults
        self.add_prompt("Toe Kick Height", 'DISTANCE', props.toe_kick_height)
        self.add_prompt("Toe Kick Setback", 'DISTANCE', props.toe_kick_setback)

        Width = self.obj_x.snap.get_var('location.x', 'Width')
        Front_Row_Depth = self.get_prompt('Front Row Depth').get_var()
        Back_Row_Depth = self.get_prompt('Back Row Depth').get_var()
        Chase_Depth = self.get_prompt('Chase Depth').get_var()

        Toe_Kick_Setback = self.get_prompt('Toe Kick Setback').get_var('Toe_Kick_Setback')
        Toe_Kick_Height = self.get_prompt('Toe Kick Height').get_var('Toe_Kick_Height')
        Left_Side_Thickness = self.get_prompt('Left Side Thickness').get_var()
        Right_Side_Thickness = self.get_prompt('Right Side Thickness').get_var()
    
        tk_path = path.join(closet_paths.get_library_path(), "/Products - Basic/Toe Kick.png")
        wm_props = bpy.context.window_manager.snap
        
        if row_nbr == ISLAND_FRONT_ROW:
            calculator = self.get_calculator('Front Row Widths Calculator')
        else:
            calculator = self.get_calculator('Back Row Widths Calculator')

        Carcass_Subtype_1 = self.get_prompt("Carcass Subtype " + str(start_nbr)).get_var("Carcass_Subtype_1")
        loc_x_exp, loc_x_vars, opening_width_1 = self.get_calculator_widths(row_nbr, start_nbr)

        if end_nbr > start_nbr:
            Carcass_Subtype_2 = self.get_prompt("Carcass Subtype " + str(end_nbr)).get_var("Carcass_Subtype_2")
            width_prompt = calculator.get_calculator_prompt('Opening {} Width'.format(str(end_nbr)))
            opening_width_2 = width_prompt.get_var(calculator.name, 'Opening_{}_Width'.format(str(end_nbr)))

        
        toe_kick = wm_props.get_asset(tk_path)
        toe_kick.draw()
        toe_kick.obj_bp.parent = self.obj_bp
        # toe_kick.obj_bp["ID_PROMPT"] = toe_kick.id_prompt
        toe_kick.obj_bp.snap.comment_2 = "1034"

        if start_nbr != end_nbr:
            loc_x_vars.extend([opening_width_1,opening_width_2,Left_Side_Thickness,Right_Side_Thickness,Carcass_Subtype_1,Carcass_Subtype_2])
            if row_nbr == ISLAND_FRONT_ROW:
                if self.double_sided:
                    toe_kick.loc_y('-Back_Row_Depth-Chase_Depth',[Back_Row_Depth,Chase_Depth])
                toe_kick.dim_y('-Front_Row_Depth+Toe_Kick_Setback', [Front_Row_Depth,Toe_Kick_Setback])
                toe_kick.loc_x(loc_x_exp + '-INCH(0.75)/2'
                                            '+IF(Carcass_Subtype_1==' + str(ISLAND_APPLIANCE_CARCASS) + ',Opening_' + str(start_nbr) +'_Width,0)', loc_x_vars)
                toe_kick.dim_x('IF(Carcass_Subtype_1!=' + str(ISLAND_APPLIANCE_CARCASS) + ',Opening_' + str(start_nbr) +'_Width,0)'
                                '+IF(Carcass_Subtype_2!=' + str(ISLAND_APPLIANCE_CARCASS) + ',Opening_' + str(end_nbr) +'_Width,0)'
                                '+Left_Side_Thickness',loc_x_vars)
            elif row_nbr == ISLAND_BACK_ROW:
                toe_kick.loc_y('-Back_Row_Depth',[Back_Row_Depth])
                toe_kick.dim_y('-Back_Row_Depth+Toe_Kick_Setback', [Back_Row_Depth,Toe_Kick_Setback])
                toe_kick.loc_x(loc_x_exp + 
                                '+IF(Carcass_Subtype_2!=' + str(ISLAND_APPLIANCE_CARCASS) + ',Opening_' + str(end_nbr) +'_Width+Opening_' + str(start_nbr) + '_Width,'
                                    'IF(Carcass_Subtype_1!=' + str(ISLAND_APPLIANCE_CARCASS) + ',Opening_' + str(start_nbr) +'_Width,0))'
                                '+INCH(0.75)/2',loc_x_vars)
                toe_kick.dim_x('IF(Carcass_Subtype_1!=' + str(ISLAND_APPLIANCE_CARCASS) + ',Opening_' + str(start_nbr) +'_Width,0)'
                                '+IF(Carcass_Subtype_2!=' + str(ISLAND_APPLIANCE_CARCASS) + ',Opening_' + str(end_nbr) +'_Width,0)'
                                '+Left_Side_Thickness',loc_x_vars)
                toe_kick.rot_z(value=math.radians(180))    

            toe_kick.get_prompt("Hide").set_formula('IF(Carcass_Subtype_1==' + str(ISLAND_APPLIANCE_CARCASS) + 
                                                            ' and Carcass_Subtype_2==' + str(ISLAND_APPLIANCE_CARCASS) + ',True,False)',
                                                     [Carcass_Subtype_1,Carcass_Subtype_2])
        else:
            loc_x_vars.extend([opening_width_1,Left_Side_Thickness,Carcass_Subtype_1])
            if row_nbr == ISLAND_FRONT_ROW:
                if self.double_sided:
                    toe_kick.loc_y('-Back_Row_Depth-Chase_Depth',[Back_Row_Depth,Chase_Depth])
                toe_kick.dim_y('-Front_Row_Depth+Toe_Kick_Setback', [Front_Row_Depth,Toe_Kick_Setback])
                toe_kick.loc_x(loc_x_exp + '-INCH(0.75)/2'
                                            '+IF(Carcass_Subtype_1==' + str(ISLAND_APPLIANCE_CARCASS) + ',Opening_' + str(start_nbr) +'_Width,0)', loc_x_vars)
                toe_kick.dim_x('IF(Carcass_Subtype_1!=' + str(ISLAND_APPLIANCE_CARCASS) + ',Opening_' + str(start_nbr) +'_Width,0)'
                                '+Left_Side_Thickness',loc_x_vars)
            elif row_nbr == ISLAND_BACK_ROW:
                toe_kick.loc_y('-Back_Row_Depth',[Back_Row_Depth])
                toe_kick.dim_y('-Back_Row_Depth+Toe_Kick_Setback', [Back_Row_Depth,Toe_Kick_Setback])
                toe_kick.loc_x(loc_x_exp + 
                                '+IF(Carcass_Subtype_1!=' + str(ISLAND_APPLIANCE_CARCASS) + ',Opening_' + str(start_nbr) +'_Width,0)'
                                '+INCH(0.75)/2',loc_x_vars)
                toe_kick.dim_x('IF(Carcass_Subtype_1!=' + str(ISLAND_APPLIANCE_CARCASS) + ',Opening_' + str(start_nbr) +'_Width,0)'
                                '+Left_Side_Thickness',loc_x_vars)
                toe_kick.rot_z(value=math.radians(180))   

            toe_kick.get_prompt('Hide').set_formula('IF(Carcass_Subtype_1==' + str(ISLAND_APPLIANCE_CARCASS) + ',True,False)', [Carcass_Subtype_1])

        toe_kick.get_prompt('Toe Kick Height').set_formula('Toe_Kick_Height', [Toe_Kick_Height])
  

    def add_toe_kick(self):
        row_start_nbr, row_end_nbr = self.get_row_opening_nbrs(ISLAND_FRONT_ROW)

        tk_start_nbr = 1
        tk_end_nbr = row_start_nbr + 1 if row_start_nbr < row_end_nbr else row_start_nbr
        self.create_toe_kick(ISLAND_FRONT_ROW, tk_start_nbr, tk_end_nbr)

        if tk_end_nbr < row_end_nbr:
            tk_start_nbr = tk_end_nbr + 1
            tk_end_nbr = tk_start_nbr + 1 if tk_start_nbr < row_end_nbr else tk_start_nbr
            self.create_toe_kick(ISLAND_FRONT_ROW, tk_start_nbr, tk_end_nbr)

        if self.double_sided:
            row_start_nbr, row_end_nbr = self.get_row_opening_nbrs(ISLAND_BACK_ROW)

            tk_start_nbr = row_start_nbr
            tk_end_nbr = row_start_nbr + 1 if row_start_nbr < row_end_nbr else row_start_nbr
            self.create_toe_kick(ISLAND_BACK_ROW, tk_start_nbr, tk_end_nbr)

            if tk_end_nbr < row_end_nbr:
                tk_start_nbr = tk_end_nbr + 1
                tk_end_nbr = tk_start_nbr + 1 if tk_start_nbr < row_end_nbr else tk_start_nbr
                self.create_toe_kick(ISLAND_BACK_ROW, tk_start_nbr, tk_end_nbr)

    def add_leg_levelers(self):
        Width = self.get_prompt('Opening Width').get_var('Width')
        Depth = self.obj_y.snap.get_var('location.y', 'Depth')

        Toe_Kick_Height = self.get_prompt('Toe Kick Height').get_var()
        Toe_Kick_Setback = self.get_prompt('Toe Kick Setback').get_var()
        Left_Side_Thickness = self.get_prompt('Left Side Thickness').get_var()
        Right_Side_Thickness = self.get_prompt('Right Side Thickness').get_var()

        cols = int(self.opening_qty / 2) if self.double_sided else self.opening_qty

        for col in range(0, cols):
            for row in range (0,2):
                if row == ISLAND_FRONT_ROW or (self.double_sided and row == ISLAND_BACK_ROW):
                    legs = add_part(self, LEG_LEVELERS)
                    part_nbr = str(col+1) if row == ISLAND_FRONT_ROW else str(cols+col+1)
                    legs.set_name("Leg Levelers " + part_nbr)
                    # legs.loc_x('Left_Side_Thickness',[Left_Side_Thickness])
                    legs.loc_x('Left_Side_Thickness+Width*' + str(col),[Left_Side_Thickness,Width])
                    legs.dim_x('Width-(Left_Side_Thickness+Right_Side_Thickness)',[Width,Left_Side_Thickness,Right_Side_Thickness])
                    legs.dim_y('Depth+Toe_Kick_Setback',[Depth,Toe_Kick_Setback])
                    legs.dim_z('Toe_Kick_Height',[Toe_Kick_Height])
    
    def add_back(self):
        Height = self.obj_z.snap.get_var('location.z', 'Height')
        Front_Row_Depth = self.get_prompt('Front Row Depth').get_var()
        Back_Row_Depth = self.get_prompt('Back Row Depth').get_var()
        Chase_Depth = self.get_prompt('Chase Depth').get_var()

        Double_Sided = self.get_prompt('Double Sided').get_var()
        Left_Side_Thickness = self.get_prompt('Left Side Thickness').get_var()
        Right_Side_Thickness = self.get_prompt('Right Side Thickness').get_var()
        Top_Inset = self.get_prompt('Top Inset').get_var()
        Bottom_Inset = self.get_prompt('Bottom Inset').get_var()
        Back_Thickness = self.get_prompt('Back Thickness').get_var()
        Bottom_Thickness = self.get_prompt('Bottom Thickness').get_var()
        Top_Thickness = self.get_prompt('Top Thickness').get_var()
        Remove_Back = self.get_prompt('Remove Back').get_var()
        Remove_Bottom = self.get_prompt('Remove Bottom').get_var()
        Toe_Kick_Height = self.get_prompt('Toe Kick Height').get_var()
        
        cols = int(self.opening_qty / 2) if self.double_sided else self.opening_qty

        for col in range(0, cols):
            for row in range (0,2):
                if row == ISLAND_FRONT_ROW or (self.double_sided and row == ISLAND_BACK_ROW): 
                    part_nbr = str(col+1) if row == ISLAND_FRONT_ROW else str(cols+col+1)
                    Carcass_Subtype = self.get_prompt("Carcass Subtype " + part_nbr).get_var("Carcass_Subtype")
                    Remove_Left_Side = self.get_prompt("Remove Left Side " + part_nbr).get_var("Remove_Left_Side")
                    Remove_Right_Side = self.get_prompt("Remove Right Side " + part_nbr).get_var("Remove_Right_Side")
                    loc_x_exp, loc_x_vars, opening_width = self.get_calculator_widths(row, part_nbr)

                    back = common_parts.add_back(self)
                    back.set_name(self.carcass_type + " Back " + part_nbr)

                    back.rot_y(value=math.radians(-90))
                    
                    loc_x_vars.extend([opening_width, Left_Side_Thickness, Right_Side_Thickness, Carcass_Subtype, Remove_Left_Side, Remove_Right_Side])
                    if row == ISLAND_FRONT_ROW:
                        back.loc_x(loc_x_exp + '+Left_Side_Thickness', loc_x_vars)
                        back.dim_y('Opening_' + part_nbr + '_Width-Left_Side_Thickness-Right_Side_Thickness',loc_x_vars)
                       
                        back.rot_z(value=math.radians(-90))
                    elif row == ISLAND_BACK_ROW:
                        back.loc_x(loc_x_exp + '+Left_Side_Thickness', loc_x_vars)
                        back.dim_y('-Opening_' + part_nbr + '_Width+Left_Side_Thickness+Right_Side_Thickness',loc_x_vars)

                        back.rot_z(value=math.radians(90))
                    
                    back.dim_x('fabs(Height)-Top_Thickness-Bottom_Thickness-IF(Carcass_Subtype!=' + str(ISLAND_APPLIANCE_CARCASS) + ',Toe_Kick_Height,0)',
                               [Height,Top_Thickness,Toe_Kick_Height,Bottom_Thickness,Remove_Bottom,Carcass_Subtype])
                    back.dim_z('-Back_Thickness',[Back_Thickness])
                    
                    if self.double_sided:
                        if row == ISLAND_FRONT_ROW:
                            back.loc_y('-Back_Row_Depth-Chase_Depth',[Back_Row_Depth,Chase_Depth])
                        elif row == ISLAND_BACK_ROW:
                            back.loc_y('-Back_Row_Depth',[Back_Row_Depth])
                    back.loc_z('IF(Remove_Bottom,0,Toe_Kick_Height+Bottom_Thickness)',[Remove_Bottom,Toe_Kick_Height,Bottom_Thickness])

                    back.get_prompt('Hide').set_formula('IF(Carcass_Subtype!=' + str(ISLAND_APPLIANCE_CARCASS) + ',False,True)', [Carcass_Subtype])
        
    def draw(self):
        props = cabinet_properties.get_scene_props().carcass_defaults
        self.create_assembly()
        
        self.add_common_carcass_prompts()
        self.add_base_assembly_prompts()
        self.add_appliance_prompts()
        self.add_sink_prompts()

        self.add_calculator(self.opening_qty)
        self.add_calculator_prompts(self.opening_qty) 

        self.add_base_sides()
        self.add_appliance_sides()
        
        self.add_full_top()
        self.add_sink_top()
                
        if self.double_sided:
            self.add_chase_caps()
        else:
            self.add_backing_cap()

        self.add_back()
        self.add_bottom()
        
        self.add_toe_kick()

        self.add_prompt_formulas()

        self.update()

#---------Standard Carcasses
        
class INSERT_Base_Carcass(Standard_Carcass):
    
    def __init__(self):
        self.category_name = "Carcasses"
        self.assembly_name = "Base Carcass"
        self.carcass_type = "Base"
        self.width = sn_unit.inch(18)
        self.height = sn_unit.inch(34)
        self.depth = sn_unit.inch(23)

class INSERT_Tall_Carcass(Standard_Carcass):
    
    def __init__(self):
        self.category_name = "Carcasses"
        self.assembly_name = "Tall Carcass"
        self.carcass_type = "Tall"
        self.width = sn_unit.inch(18)
        self.height = sn_unit.inch(84)
        self.depth = sn_unit.inch(23)

class INSERT_Upper_Carcass(Standard_Carcass):
    
    def __init__(self):
        self.category_name = "Carcasses"
        self.assembly_name = "Upper Carcass"
        self.carcass_type = "Upper"
        self.width = sn_unit.inch(18)
        self.height = sn_unit.inch(34)
        self.depth = sn_unit.inch(12)
               
class INSERT_Sink_Carcass(Standard_Carcass):
    
    def __init__(self):
        self.category_name = "Carcasses"
        self.assembly_name = "Sink Carcass"
        self.carcass_type = "Sink"
        self.width = sn_unit.inch(18)
        self.height = sn_unit.inch(34)
        self.depth = sn_unit.inch(23)
                
class INSERT_Suspended_Carcass(Standard_Carcass):
    
    def __init__(self):
        self.category_name = "Carcasses"
        self.assembly_name = "Suspended Carcass"
        self.carcass_type = "Suspended"
        self.width = sn_unit.inch(18)
        self.height = sn_unit.inch(6)
        self.depth = sn_unit.inch(23)

class INSERT_Appliance_Carcass(Standard_Carcass):
    
    def __init__(self):
        self.category_name = "Carcasses"
        self.assembly_name = "Appliance Carcass"
        self.carcass_type = "Appliance"
        self.width = sn_unit.inch(24)
        self.height = sn_unit.inch(34.5)
        self.depth = sn_unit.inch(24)

#---------Inside Corner Carcasses

class INSERT_Base_Inside_Corner_Notched_Carcass(Inside_Corner_Carcass):
    
    def __init__(self):
        self.category_name = "Carcasses"
        self.assembly_name = "Base Inside Corner Notched Carcass"
        self.carcass_type = "Base"
        self.carcass_shape = "Notched"
        self.width = sn_unit.inch(36)
        self.height = sn_unit.inch(34)
        self.depth = sn_unit.inch(36)
        self.left_right_depth = sn_unit.inch(23)
        
class INSERT_Upper_Inside_Corner_Notched_Carcass(Inside_Corner_Carcass):
    
    def __init__(self):
        self.category_name = "Carcasses"
        self.assembly_name = "Upper Inside Corner Notched Carcass"
        self.carcass_type = "Upper"
        self.carcass_shape = "Notched"
        self.width = sn_unit.inch(12)
        self.height = sn_unit.inch(34)
        self.depth = sn_unit.inch(12)
        self.left_right_depth = sn_unit.inch(12)

class INSERT_Base_Inside_Corner_Diagonal_Carcass(Inside_Corner_Carcass):
    
    def __init__(self):
        self.category_name = "Carcasses"
        self.assembly_name = "Base Inside Corner Diagonal Carcass"
        self.carcass_type = "Base"
        self.carcass_shape = "Diagonal"
        self.width = sn_unit.inch(36)
        self.height = sn_unit.inch(34)
        self.depth = sn_unit.inch(36)
        self.left_right_depth = sn_unit.inch(23)
        
class INSERT_Upper_Inside_Corner_Diagonal_Carcass(Inside_Corner_Carcass):
    
    def __init__(self):
        self.category_name = "Carcasses"
        self.assembly_name = "Upper Inside Corner Diagonal Carcass"
        self.carcass_type = "Upper"
        self.carcass_shape = "Diagonal"
        self.width = sn_unit.inch(12)
        self.height = sn_unit.inch(34)
        self.depth = sn_unit.inch(12)
        self.left_right_depth = sn_unit.inch(12)

#---------Island Carcasses

class INSERT_Island_Carcass(Island_Carcass):
    
    def __init__(self):
        self.category_name = "Carcasses"
        self.assembly_name = "Island Carcass"
        self.carcass_type = "Base"
        self.width = sn_unit.inch(18)
        self.height = sn_unit.inch(34)
        self.depth = sn_unit.inch(23)