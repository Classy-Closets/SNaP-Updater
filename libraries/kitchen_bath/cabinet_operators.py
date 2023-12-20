
import bpy
import math
from os import path
from snap import sn_types, sn_unit, sn_utils
from bpy.app.handlers import persistent
from . import cabinet_properties
from snap.libraries.closets.ops.drop_closet import PlaceClosetInsert


def get_carcass_insert(product):
    new_list = []
    inserts = sn_utils.get_insert_bp_list(product.obj_bp,new_list)
    for insert in inserts:
        if insert.get("IS_BP_CARCASS"):
            carcass = sn_types.Assembly(insert)
            return carcass
    # pass

def get_product_components(product):

    lbl_text = ""
    count_door = 0
    count_drawer = 0
    count_shelf = 0
    count_hood = 0
    count_false = 0
    components = sn_utils.get_assembly_bp_list(product.obj_bp, [])
    
    for component in components:
        if "IS_DOOR" in component:
            door = sn_types.Assembly(component)
            hide_ppt = door.get_prompt("Hide")
            if hide_ppt:
                if door.get_prompt("Hide").get_value() == False:
                    count_door += 1
        elif "IS_BP_DRAWER_FRONT" in component:
            if "IS_BP_FALSE_FRONT" in component:
                count_false += 1
            else:
                count_drawer += 1
        elif "IS_BP_SHELVES" in component:
            shelves = sn_types.Assembly(component)
            shelf_ppt = shelves.get_prompt("Shelf Qty")
            if shelf_ppt:
                count_shelf += shelves.get_prompt("Shelf Qty").get_value()
        elif "IS_BP_HOOD_BODY" in component:
            count_hood += 1

    if count_door > 1:
        lbl_text += str(count_door) + " Doors|"
    elif count_door == 1:
        lbl_text += "1 Door|"
    
    if count_drawer > 1:
        lbl_text += str(count_drawer) + " Drws|"
    elif count_drawer == 1:
        lbl_text += "1 Drw|"

    if count_shelf > 1:
        lbl_text += str(count_shelf) + " Shlvs|"
    elif count_shelf == 1:
        lbl_text += "1 Shelf|"

    if count_hood >= 1:
        lbl_text += str(count_hood) + " Hood|"

    if lbl_text.endswith("|"):
        lbl_text = lbl_text[:-1]

    return lbl_text

def get_product_profile_mesh(carcass_shape, name, size):
    x = size[0]
    y = size[1]
    z = size[2]
    l = size[3]
    r = -size[4]
    verts = []
    faces = {}

   
    if carcass_shape == 'DIAGONAL':
        verts = [(0.0, 0.0, 0.0),
             (0.0, y, 0.0),
             (l, y, 0.0),
             (x, r, 0.0),
             (x, 0.0, 0.0),
             (0.0, 0.0, z),
             (0.0, y, z),
             (l, y, z),
             (x, r, z),
             (x, 0.0, z),
             ]

        faces = [(0, 1, 2, 3, 4),
                 (5, 6, 7, 8, 9),
                 (0, 1, 6, 5),
                 (1, 2, 7, 6),
                 (2, 3, 8, 7),
                 (3, 4, 9, 8),
                 (4, 0, 9, 8),
                ]

    elif carcass_shape == 'NOTCHED':
        verts = [(0.0, 0.0, 0.0),
             (0.0, y, 0.0),
             (l, y, 0.0),
             (l, r, 0.0),
             (x, r, 0.0),
             (x, 0.0, 0.0),
            
             (0.0, 0.0, z),
             (0.0, y, z),
             (l, y, z),
             (l, r, z),
             (x, r, z),
             (x, 0.0, z),
             ]

        faces = [(0, 1, 2, 3, 4, 5),
                 (6, 7, 8, 9, 10, 11),
                 (0, 1, 7, 6),
                 (1, 2, 8, 7),
                 (2, 3, 9, 8),
                 (3, 4, 10, 9),
                 (4, 5, 11, 10),
                 (5, 0, 6, 11),
                ]
    else:
        verts = [(0.0, 0.0, 0.0),
             (0.0, y, 0.0),
             (x, y, 0.0),
             (x, 0.0, 0.0),
             (0.0, 0.0, z),
             (0.0, y, z),
             (x, y, z),
             (x, 0.0, z),
             ]

        faces = [(0, 1, 2, 3),
                (4, 7, 6, 5),
                (0, 4, 5, 1),
                (1, 5, 6, 2),
                (2, 6, 7, 3),
                (4, 0, 3, 7),
                ]


    return sn_utils.create_object_from_verts_and_faces(verts, faces, name)

def add_rectangle_molding(product,is_crown=True):
    carcass = get_carcass_insert(product)
    if carcass:
        width = product.obj_x.location.x
        depth = product.obj_y.location.y
        toe_kick_setback = carcass.get_prompt("Toe Kick Setback")
        left_fin_end = carcass.get_prompt("Left Fin End")
        right_fin_end = carcass.get_prompt("Right Fin End")
        left_end_condition = carcass.get_prompt("Left End Condition")
        if not left_end_condition:
            left_end_condition = carcass.add_prompt("Left End Condition", 'COMBOBOX', 0, ['MP', 'EP'])
        right_end_condition = carcass.get_prompt("Right End Condition")
        if not right_end_condition:
            right_end_condition = carcass.add_prompt("Right End Condition", 'COMBOBOX', 0, ['MP', 'EP'])

        setback = 0
        if toe_kick_setback and is_crown == False:
            setback = toe_kick_setback.get_value()

        points = []

        # LEFT
        if left_end_condition.get_value() == 1:  # End Panel
            points.append((0, 0, 0))
            points.append((0, depth + setback, 0))
        elif left_fin_end.get_value():
            points.append((0, 0, 0))
            points.append((0, depth + setback, 0))
        else:
            points.append((0, depth + setback, 0))

        # RIGHT
        if right_end_condition.get_value() == 1:  # End Panel
            points.append((width, depth + setback, 0))
            points.append((width, 0, 0))
        elif right_fin_end.get_value():
            points.append((width, depth + setback, 0))
            points.append((width, 0, 0))
        else:
            points.append((width, depth + setback, 0))

        return points

def add_inside_molding(product,is_crown=True,is_notched=True):
    carcass = get_carcass_insert(product)
    width = product.obj_x.location.x
    depth = product.obj_y.location.y
    toe_kick_setback = carcass.get_prompt("Toe Kick Setback")
    left_fin_end = carcass.get_prompt("Left Fin End")
    right_fin_end = carcass.get_prompt("Right Fin End")
    left_end_condition = carcass.get_prompt("Left End Condition")
    right_end_condition = carcass.get_prompt("Right End Condition")
    left_side_wall_filler = carcass.get_prompt("Left Side Wall Filler")
    right_side_wall_filler = carcass.get_prompt("Right Side Wall Filler")
    cabinet_depth_left = carcass.get_prompt("Cabinet Depth Left")
    cabinet_depth_right = carcass.get_prompt("Cabinet Depth Right")

    setback = 0
    if toe_kick_setback and is_crown == False:
        setback = toe_kick_setback.get_value()
    
    points = []
    
    #LEFT
    if left_side_wall_filler.get_value() > 0:
        points.append((cabinet_depth_left.get_value()-setback,depth-left_side_wall_filler.get_value(),0))
    elif left_end_condition.get_value() == 1:  # End Panel
        points.append((0,depth,0))
        points.append((cabinet_depth_left.get_value()-setback,depth,0))
    elif left_fin_end.get_value() == True:
        points.append((0,depth,0))
        points.append((cabinet_depth_left.get_value()-setback,depth,0))
    else:
        points.append((cabinet_depth_left.get_value()-setback,depth,0))
        
    #CENTER
    if is_notched:
        points.append((cabinet_depth_left.get_value()-setback,-cabinet_depth_right.get_value()+setback,0))
        
    #RIGHT
    if right_side_wall_filler.get_value() > 0:
        points.append((width + right_side_wall_filler.get_value(),-cabinet_depth_right.get_value()+setback,0))
    elif right_end_condition.get_value() == 1:  # End Panel
        points.append((width,-cabinet_depth_right.get_value()+setback,0))
        points.append((width,0,0))
    elif right_fin_end.get_value() == True:
        points.append((width,-cabinet_depth_right.get_value()+setback,0))
        points.append((width,0,0))
    else:
        points.append((width,-cabinet_depth_right.get_value()+setback,0))
    
    return points
  
def add_transition_molding(product,is_crown=True):
    carcass = get_carcass_insert(product)
    if carcass:
        width = product.obj_x.location.x
        toe_kick_setback = carcass.get_prompt("Toe Kick Setback")
        left_fin_end = carcass.get_prompt("Left Fin End")
        right_fin_end = carcass.get_prompt("Right Fin End")
        left_end_condition = carcass.get_prompt("Left End Condition")
        right_end_condition = carcass.get_prompt("Right End Condition")
        left_side_wall_filler = carcass.get_prompt("Left Side Wall Filler")
        right_side_wall_filler = carcass.get_prompt("Right Side Wall Filler")
        cabinet_depth_left = carcass.get_prompt("Cabinet Depth Left")
        cabinet_depth_right = carcass.get_prompt("Cabinet Depth Right")
        left_side_thickness = carcass.get_prompt("Left Side Thickness")
        right_side_thickness = carcass.get_prompt("Right Side Thickness")
        
        setback = 0
        if toe_kick_setback and is_crown == False:
            setback = toe_kick_setback.get_value()
        
        points = []
        
        #LEFT
        if left_side_wall_filler.get_value() > 0:
            points.append((-left_side_wall_filler.get_value(),-cabinet_depth_left.get_value()+setback,0))
            points.append((left_side_thickness.get_value(),-cabinet_depth_left.get_value()+setback,0))
        elif left_end_condition.get_value() == 1:  # End Panel
            points.append((0,0,0))
            points.append((0,-cabinet_depth_left.get_value()+setback,0))
            points.append((left_side_thickness.get_value(),-cabinet_depth_left.get_value()+setback,0))    
        elif left_fin_end.get_value() == True:
            points.append((0,0,0))
            points.append((0,-cabinet_depth_left.get_value()+setback,0))
            points.append((left_side_thickness.get_value(),-cabinet_depth_left.get_value()+setback,0))
        else:
            points.append((0,-cabinet_depth_left.get_value()+setback,0))
            points.append((left_side_thickness.get_value(),-cabinet_depth_left.get_value()+setback,0))
            
        #RIGHT
        if right_side_wall_filler.get_value() > 0:
            points.append((width - right_side_thickness.get_value() + right_side_wall_filler.get_value(),-cabinet_depth_right.get_value()+setback,0))
            points.append((width + right_side_wall_filler.get_value(),-cabinet_depth_right.get_value()+setback,0))
        elif right_end_condition.get_value() == 1:  # End Panel
            points.append((width - right_side_thickness.get_value() + right_side_wall_filler.get_value(),-cabinet_depth_right.get_value()+setback,0))
            points.append((width,-cabinet_depth_right.get_value()+setback,0))
            points.append((width,0,0))
        elif right_fin_end.get_value() == True:
            points.append((width - right_side_thickness.get_value() + right_side_wall_filler.get_value(),-cabinet_depth_right.get_value()+setback,0))
            points.append((width,-cabinet_depth_right.get_value()+setback,0))
            points.append((width,0,0))
        else:
            points.append((width - right_side_thickness.get_value() + right_side_wall_filler.get_value(),-cabinet_depth_right.get_value()+setback,0))
            points.append((width,-cabinet_depth_right.get_value()+setback,0))
        
        return points

class OPERATOR_Frameless_Standard_Draw_Plan(bpy.types.Operator):
    bl_idname = "sn_cabinets.draw_plan"
    bl_label = "Draw Cabinet Plan View"
    bl_description = "Creates the plan view for cabinets"
    
    object_name: bpy.props.StringProperty(name="Object Name",default="")
    scene_name: bpy.props.StringProperty(name="Scene Name",default="")

    product = None

    left_filler_amount = 0
    right_filler_amount = 0
    cabinet_depth_left = 0
    cabinet_depth_right = 0
    carcass_shape = "RECTANGLE"
    
    def get_prompts(self):
        inserts = sn_utils.get_insert_bp_list(self.product.obj_bp,[])
        carcass_shape = ""
        for insert in inserts:
            carcass = sn_types.Assembly(insert)

            if "PROFILE_SHAPE_NOTCHED" in carcass.obj_bp:
                carcass_shape = "NOTCHED"
            elif "PROFILE_SHAPE_DIAGONAL" in carcass.obj_bp:
                carcass_shape = "DIAGONAL"
            elif "PROFILE_SHAPE_RECTANGLE" in carcass.obj_bp:
                carcass_shape = "RECTANGLE"

            left_wall_filler = carcass.get_prompt("Left Side Wall Filler")
            right_wall_filler = carcass.get_prompt("Right Side Wall Filler")
            cabinet_depth_left = carcass.get_prompt("Cabinet Depth Left")
            cabinet_depth_right = carcass.get_prompt("Cabinet Depth Right")

            if carcass_shape != "":
                self.carcass_shape = carcass_shape

            if left_wall_filler:
                self.left_filler_amount = left_wall_filler.get_value()
            if right_wall_filler:
                self.right_filler_amount = right_wall_filler.get_value()
            if cabinet_depth_left:
                self.cabinet_depth_left = cabinet_depth_left.get_value()
            if cabinet_depth_right:
                self.cabinet_depth_right = cabinet_depth_right.get_value()

                
    def execute(self, context):
        obj_bp = bpy.data.objects[self.object_name]
        
        self.product = sn_types.Assembly(obj_bp)
        self.get_prompts()
        
        assembly_mesh = get_product_profile_mesh(self.carcass_shape, self.product.obj_bp.snap.name_object,
                                            (self.product.obj_x.location.x,
                                             self.product.obj_y.location.y,
                                            self.product.obj_z.location.z,
                                             self.cabinet_depth_left,
                                             self.cabinet_depth_right))

        assembly_mesh.matrix_world = self.product.obj_bp.matrix_world
        assembly_mesh.snap.type = 'CAGE'
        assembly_mesh['IS_BP_CABINET'] = True

        wall_bp = sn_utils.get_wall_bp(self.product.obj_bp)
        parent_rot = 0
        if wall_bp:
            parent_rot = wall_bp.rotation_euler.z
        
        dim_lbl = sn_types.Dimension()
        dim_lbl.parent(assembly_mesh)
        scene = bpy.context.scene
        scene.snap.opengl_dim.gl_font_size = 15.5

        dim_lbl.anchor.rotation_euler = (0, -parent_rot, 0)
        dim_lbl.anchor["IS_KB_LABEL"] = True
        dim_lbl.end_point["IS_KB_LABEL"] = True
        dim_lbl.start_x(value=assembly_mesh.dimensions.x/2)

        if wall_bp:
            assembly_above = self.product.get_adjacent_assembly(direction='ABOVE')
            if self.product.obj_bp.location.z > 1:  # if this is an upper...
                y_offset = 0.45
            elif not assembly_above:
                y_offset = 0.5
            else:
                y_offset = 0.73
        else:
            y_offset = 0.5
        dim_lbl.start_y(value=-assembly_mesh.dimensions.y*y_offset)
        dim_lbl.start_z(value=math.fabs(assembly_mesh.dimensions.z))

        product_label = get_product_components(self.product)
        dim_lbl.set_label(product_label)

        if self.scene_name:
            scene = bpy.data.scenes[self.scene_name]
            scene.collection.objects.link(assembly_mesh)
            context.scene.collection.objects.unlink(assembly_mesh)
            for child in assembly_mesh.children:
                scene.collection.objects.link(child)
                context.scene.collection.objects.unlink(child)
                if child.get('IS_VISDIM_A'):
                    for subchild in child.children:
                        scene.collection.objects.link(subchild)
                        context.scene.collection.objects.unlink(subchild)
            

        return {'FINISHED'}

#region Old OPERATOR_Cabinet_Update
# class OPERATOR_Cabinet_Update(bpy.types.Operator):
#     bl_idname = cabinet_properties.LIBRARY_NAME_SPACE + ".update"
#     bl_label = "Cabinet Update"
#     bl_description = "Update Cabinets after being drawn"
    
#     object_name: bpy.props.StringProperty(name="Object Name",default="")
    
#     product = None
    
#     def execute(self, context):
#         print("enetring Operator_Cabinet_Update...")
#         obj_bp = bpy.data.objects[self.object_name]
        
#         self.product = sn_types.Assembly(obj_bp)
        
#         carcass = get_carcass_insert(self.product)
    

#         props = cabinet_properties.get_scene_props()
#         if self.product.obj_bp.lm_cabinets.product_sub_type == 'Base':
#             self.product.obj_y.location.y = -props.size_defaults.base_cabinet_depth
#             self.product.obj_z.location.z = props.size_defaults.base_cabinet_height
            
#         if self.product.obj_bp.lm_cabinets.product_sub_type == 'Sink':
#             self.product.obj_y.location.y = -props.size_defaults.sink_cabinet_depth
#             self.product.obj_z.location.z = props.size_defaults.sink_cabinet_height
            
#         if self.product.obj_bp.lm_cabinets.product_sub_type == 'Tall':
#             self.product.obj_y.location.y = -props.size_defaults.tall_cabinet_depth
#             self.product.obj_z.location.z = props.size_defaults.tall_cabinet_height
        
#         if self.product.obj_bp.lm_cabinets.product_sub_type == 'Upper':
#             self.product.obj_y.location.y = -props.size_defaults.upper_cabinet_depth
#             self.product.obj_z.location.z = -props.size_defaults.upper_cabinet_height
            
#             self.product.obj_bp.location.z = props.size_defaults.height_above_floor
        
#         if self.product.obj_bp.lm_cabinets.product_sub_type == 'Suspended':
#             self.product.obj_y.location.y = -props.size_defaults.suspended_cabinet_depth
#             self.product.obj_z.location.z = -props.size_defaults.suspended_cabinet_height
            
#             self.product.obj_bp.location.z = props.size_defaults.base_cabinet_height
            
#         if carcass:
#             carcass_defaults = props.carcass_defaults
#             toe_kick_height = carcass.get_prompt("Toe Kick Height")
#             toe_kick_setback = carcass.get_prompt("Toe Kick Setback")
            
#             if toe_kick_height:
#                 toe_kick_height.set_value(carcass_defaults.toe_kick_height)

#             if toe_kick_setback:
#                 toe_kick_setback.set_value(carcass_defaults.toe_kick_setback)
                
#         sn_utils.run_calculators(self.product.obj_bp)
#         return {'FINISHED'}
#endregion Old OPERATOR_Cabinet_Update

class OPERATOR_Auto_Add_Molding(bpy.types.Operator):
    bl_idname = cabinet_properties.LIBRARY_NAME_SPACE + ".auto_add_molding"
    bl_label = "Add Molding" 
    bl_options = {'UNDO'}

    molding_type: bpy.props.StringProperty(name="Molding Type")

    crown_profile = None
    base_profile = None
    
    is_base = False
    is_crown = False
    is_light_rail = False
    
    tall_cabinet_switch = sn_unit.inch(60)
    
    def get_profile(self, context):
        props = cabinet_properties.get_scene_props()
        scene_coll = context.scene.collection
        molding_coll = scene_coll.children.get("Molding Profiles")

        if  not molding_coll:
            molding_coll = bpy.data.collections.new("Molding Profiles")
            scene_coll.children.link(molding_coll)

        if self.molding_type == 'Base':
            self.profile = molding_coll.objects.get(props.base_molding)

            if not self.profile:
                self.profile_exists = False
                self.profile = sn_utils.get_object(
                    path.join(path.dirname(__file__),
                    cabinet_properties.MOLDING_FOLDER_NAME,
                    cabinet_properties.BASE_MOLDING_FOLDER_NAME,
                    props.base_molding_category,
                    props.base_molding + ".blend"))
                molding_coll.objects.link(self.profile)

        elif self.molding_type == 'Light':
            self.profile = molding_coll.objects.get(props.light_rail_molding)

            if not self.profile:
                self.profile_exists = False
                self.profile = sn_utils.get_object(
                    path.join(path.dirname(__file__),
                    cabinet_properties.MOLDING_FOLDER_NAME,
                    cabinet_properties.LIGHT_MOLDING_FOLDER_NAME,
                    props.light_rail_molding_category,
                    props.light_rail_molding + ".blend"))
                molding_coll.objects.link(self.profile)

        else:
            profile_name = props.crown_molding + " Molding Profile"
            self.profile = molding_coll.objects.get(profile_name)

            if not self.profile:
                self.profile = sn_utils.get_object(
                    path.join(path.dirname(__file__),
                    cabinet_properties.MOLDING_FOLDER_NAME,
                    cabinet_properties.CROWN_MOLDING_FOLDER_NAME,
                    props.crown_molding_category,
                    props.crown_molding + ".blend"))
                self.profile.name = profile_name
                molding_coll.objects.link(self.profile)

        self.profile['IS_MOLDING_PROFILE'] = True

    def get_products(self):
        products = []
        for obj in bpy.context.scene.objects:
            if obj.get("IS_BP_CABINET"):
                product = sn_types.Assembly(obj)
                products.append(product)
        return products
        
    def create_extrusion(self, context, points, is_crown=True, is_light_rail=False, is_base=False, product=None):
        if self.profile is None:
            self.get_profile(context)
        
        bpy.ops.curve.primitive_bezier_curve_add(enter_editmode=False)
        obj_curve = bpy.context.active_object
        obj_curve.modifiers.new("Edge Split",type='EDGE_SPLIT')
        obj_props = cabinet_properties.get_object_props(obj_curve)

        if is_crown:
            obj_props.is_crown_molding = True
            name = context.scene.lm_cabinets.crown_molding
        elif is_light_rail:
            obj_props.is_light_rail_molding = True
            name = context.scene.lm_cabinets.light_rail_molding
            if "L01" in context.scene.lm_cabinets.light_rail_molding:
                name = "Light Rail"
        else:
            obj_props.is_base_molding = True
            name = context.scene.lm_cabinets.base_molding

        obj_curve.data.splines.clear()
        spline = obj_curve.data.splines.new('BEZIER')
        spline.bezier_points.add(count=len(points) - 1)
        obj_curve.data.bevel_object = self.profile
        obj_curve.data.bevel_mode = 'OBJECT'
        obj_curve.snap.type_mesh = 'SOLIDSTOCK'
        obj_curve.snap.solid_stock = self.profile.name
        obj_curve.snap.name_object = name
        obj_curve.name = name
        
        bpy.ops.sn_object.add_material_slot(object_name=obj_curve.name)
        bpy.ops.sn_material.sync_material_slots(object_name=obj_curve.name)

        if is_crown and "Flat Crown" in context.scene.lm_cabinets.crown_molding:
            obj_curve.snap.material_slots[0].pointer_name = "Closet_Part_Surfaces"
        elif is_light_rail and "L01" in context.scene.lm_cabinets.light_rail_molding:
            obj_curve.snap.material_slots[0].pointer_name = "Closet_Part_Surfaces"
        elif is_base and "BA23" in context.scene.lm_cabinets.base_molding:
            obj_curve.snap.material_slots[0].pointer_name = "Closet_Part_Surfaces"
        else:
            obj_curve.snap.material_slots[0].pointer_name = "Molding"
        
        obj_curve.location = (0,0,0)
        
        for i, point in enumerate(points):
            obj_curve.data.splines[0].bezier_points[i].co = point
        
        bpy.ops.object.editmode_toggle()
        bpy.ops.curve.select_all(action='SELECT')
        bpy.ops.curve.handle_type_set(type='VECTOR')
        bpy.ops.object.editmode_toggle()
        obj_curve.data.dimensions = '2D'
        obj_curve.data.use_fill_caps = True
        sn_utils.assign_materials_from_pointers(obj_curve)
        return obj_curve

    def get_curve_assy_objs(self, del_objs, curve_obj):
        assy_bp = sn_utils.get_assembly_bp(curve_obj)
        if assy_bp:
            for child in sn_utils.get_child_objects(assy_bp):
                del_objs.append(child)

    def clean_up_room(self, context):
        """ Removes all of the Dimensions and other objects
            That were added to the scene from this command
            We dont want multiple objects added on top of each other
            So we must clean up the scene before running this command 
        """
        objs = []
        for obj in context.visible_objects:
            molding_profile = 'IS_MOLDING_PROFILE' in obj
            if obj.type == "CURVE" and not molding_profile:
                obj_props = cabinet_properties.get_object_props(obj)
                if self.molding_type == 'Crown':
                    if obj_props.is_crown_molding == True:
                        self.get_curve_assy_objs(objs, obj)
                elif self.molding_type == 'Base':
                    if obj_props.is_base_molding == True:
                        self.get_curve_assy_objs(objs, obj)
                else:
                    if obj_props.is_light_rail_molding == True:
                        self.get_curve_assy_objs(objs, obj)

        sn_utils.delete_obj_list(objs)

    def set_curve_location(self, context, product, curve, is_crown):
        curve.parent = product.obj_bp
        if self.is_base:
            curve.location.z = 0
        elif self.is_crown:
            if product.obj_z.location.z < 0:
                curve.location.z = 0
            else:
                curve.location.z = product.obj_z.location.z
        else:
            curve.location.z = product.obj_z.location.z

        empty_assembly = sn_types.Assembly()
        empty_assembly.create_assembly()
        empty_assembly.set_name(curve.name)
        empty_assembly.obj_bp.snap.type_group = 'INSERT'
        empty_assembly.obj_bp["IS_KB_MOLDING"] = True
        empty_assembly.obj_bp["IS_KB_PART"] = True
        empty_assembly.add_prompt("Exposed Left", 'CHECKBOX', False)
        empty_assembly.add_prompt("Exposed Right", 'CHECKBOX', False)
        empty_assembly.add_prompt("Exposed Back", 'CHECKBOX', False)

        if self.is_crown:
            empty_assembly.obj_bp["IS_BP_CROWN_MOLDING"] = True
            if "Flat Crown" in context.scene.lm_cabinets.crown_molding:
                # empty_assembly.obj_bp["IS_BP_CROWN_MOLDING"] = True
                empty_assembly.obj_bp.snap.comment_2 = "1078"
                empty_assembly.obj_bp["IS_BP_FLAT_CROWN"] = True
                empty_assembly.obj_bp.sn_closets.flat_crown_bp = True
            
        if self.is_light_rail:
            empty_assembly.obj_bp["IS_BP_LIGHT_RAIL"] = True
            if "Light Rail" in curve.name:
                empty_assembly.obj_bp.snap.comment_2 = "1040"
                empty_assembly.set_name("Light Rail")
                empty_assembly.get_prompt("Exposed Left").set_value(value=True)
                empty_assembly.get_prompt("Exposed Right").set_value(value=True)
                empty_assembly.get_prompt("Exposed Back").set_value(value=True)
        if self.is_base:
            empty_assembly.obj_bp["IS_BP_BASE_MOLDING"] = True

        # curve.snap.type_mesh = 'CUTPART'
        # curve.snap.use_multiple_edgeband_pointers = True

        empty_assembly.obj_x.hide_set(True)
        empty_assembly.obj_y.hide_set(True)
        empty_assembly.obj_z.hide_set(True)
        empty_assembly.obj_bp.parent = product.obj_bp
        empty_assembly.obj_y.location.y = curve.dimensions[2]
        empty_assembly.obj_z.location.z = sn_unit.inch(0.75)
        
        curve.parent = empty_assembly.obj_bp
        
        wall_bp = sn_utils.get_wall_bp(empty_assembly.obj_bp)
        if wall_bp:
            wall_coll = bpy.data.collections[wall_bp.snap.name_object]
            scene_coll = bpy.context.scene.collection
            sn_utils.add_assembly_to_collection(empty_assembly.obj_bp, wall_coll, recursive=True)
            sn_utils.remove_assembly_from_collection(empty_assembly.obj_bp, scene_coll, recursive=True)
            if "Collection" in bpy.data.collections:
                default_coll = bpy.data.collections["Collection"]
                sn_utils.remove_assembly_from_collection(empty_assembly.obj_bp, default_coll, recursive=True)

    def execute(self, context):
        self.is_base = True if self.molding_type == 'Base' else False
        self.is_crown = True if self.molding_type == 'Crown' else False
        self.is_light_rail = True if self.molding_type == 'Light' else False

        self.clean_up_room(context)
        self.profile = None
        products = self.get_products()
        for product in products:
            shape = product.obj_bp.lm_cabinets.product_shape

            # Check for stacked upper cabinets and skip adding light rail
            if self.is_light_rail and product.obj_bp.lm_cabinets.product_sub_type == 'Upper':
                product_below = product.get_adjacent_assembly(direction='BELOW')

                # Skip adding light rail if cabinet below is within 6" of this cabinet
                if product_below:
                    space = sn_unit.inch(6)
                    product_below_z_loc = product_below.obj_bp.location.z
                    product_below_height = product_below.obj_z.location.z

                    if product_below.obj_bp.lm_cabinets.product_sub_type == 'Upper':
                        if product_below_z_loc > product.obj_bp.location.z - abs(product.obj_z.location.z) - space:
                            continue
                    else:
                        if product_below_z_loc + product_below_height > product.obj_bp.location.z + product.obj_z.location.z - space:
                            continue

            if (self.is_crown or self.is_light_rail) and product.obj_bp.lm_cabinets.product_sub_type == 'Base':
                continue  # DONT ADD CROWN OR LIGHT RAIL MOLDING TO BASE

            if (self.is_crown or self.is_light_rail) and product.obj_bp.lm_cabinets.product_sub_type == 'Sink':
                continue  # DONT ADD CROWN OR LIGHT RAIL MOLDING TO SINK

            if self.is_light_rail and product.obj_bp.lm_cabinets.product_sub_type == 'Tall':
                continue  # DONT ADD LIGHT RAIL MOLDING TO TALL

            if product.obj_bp.lm_cabinets.product_sub_type == 'Suspended':
                continue  # DONT ADD MOLDING TO SUSPENDED

            if self.is_base and product.obj_bp.lm_cabinets.product_sub_type == 'Upper':
                continue  # DONT ADD BASE MOLDING TO UPPER

            if shape == 'RECTANGLE':
                points = add_rectangle_molding(product, self.is_crown)
                if points:
                    curve = self.create_extrusion(
                        context, points, self.is_crown, self.is_light_rail, self.is_base, product)
                    self.set_curve_location(context, product, curve, self.is_crown)

            if shape == 'INSIDE_NOTCH':
                points = add_inside_molding(product, self.is_crown, True)
                if points:
                    curve = self.create_extrusion(
                        context, points, self.is_crown, self.is_light_rail, self.is_base, product)
                    self.set_curve_location(context, product, curve, self.is_crown)

            if shape == 'INSIDE_DIAGONAL':
                points = add_inside_molding(product, self.is_crown, False)
                if points:
                    curve = self.create_extrusion(
                        context, points, self.is_crown, self.is_light_rail, self.is_base, product)
                    self.set_curve_location(context, product, curve, self.is_crown)

            if shape == 'OUTSIDE_DIAGONAL':
                pass  # TODO

            if shape == 'OUTSIDE_RADIUS':
                pass  # TODO

            if shape == 'TRANSITION':
                points = add_transition_molding(product, self.is_crown)
                if points:
                    curve = self.create_extrusion(
                        context, points, self.is_crown, self.is_light_rail, self.is_base, product)

                    self.set_curve_location(context, product, curve, self.is_crown)

        
            if product.obj_bp.get("IS_BP_CABINET") and product.obj_bp.get("MATERIAL_POINTER_NAME"):  
                sn_utils.add_kb_insert_material_pointers(product.obj_bp)
                bpy.ops.closet_materials.poll_assign_materials()

        return {'FINISHED'}

class OPERATOR_Delete_Molding(bpy.types.Operator):
    bl_idname = cabinet_properties.LIBRARY_NAME_SPACE + ".delete_molding"
    bl_label = "Delete Molding" 
    bl_options = {'UNDO'}

    molding_type: bpy.props.StringProperty(name="Molding Type")

    def get_curve_assy_objs(self, del_objs, curve_obj):
        assy_bp = sn_utils.get_assembly_bp(curve_obj)
        if assy_bp:
            for child in sn_utils.get_child_objects(assy_bp):
                del_objs.append(child)

    def execute(self, context):
        is_crown = True if self.molding_type == 'Crown' else False
        objs = []

        for obj in context.visible_objects:
            obj_props = cabinet_properties.get_object_props(obj)

            if self.molding_type == 'Crown':
                if obj_props.is_crown_molding == True:
                    self.get_curve_assy_objs(objs, obj)
            elif self.molding_type == 'Base':
                if obj_props.is_base_molding == True:
                    self.get_curve_assy_objs(objs, obj)
            else:
                if obj_props.is_light_rail_molding == True:
                    self.get_curve_assy_objs(objs, obj)

        sn_utils.delete_obj_list(objs)
        return {'FINISHED'}
    
class OPERATOR_Update_Door_Selection(bpy.types.Operator):
    """ This will clear all the spec groups to save on file size.
    """
    bl_idname = cabinet_properties.LIBRARY_NAME_SPACE + ".update_door_selection"
    bl_label = "Update Door Selection"
    bl_description = "This will change the selected door with the active door"
    bl_options = {'UNDO'}
    
    cabinet_type: bpy.props.StringProperty(name = "Cabinet Type")
    
    #DOOR SELECTION
    current_selection = bpy.props.BoolProperty(name="Use Current Selection")
    base_doors = bpy.props.BoolProperty(name="Select all base doors")
    tall_doors = bpy.props.BoolProperty(name="Select all tall doors")
    upper_doors = bpy.props.BoolProperty(name="Select all upper doors")
    drawer_fronts = bpy.props.BoolProperty(name="Select all drawer doors")
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=sn_utils.get_prop_dialog_width(400))      
    
    def draw(self, context):
        box = self.layout.box()
        split = box.split()
        
        col = split.column()
        sub = col.column()
        sub.prop(self, 'current_selection', text="Current Selection")
        sub.prop(self, 'base_doors', text="Base Doors")
        sub.prop(self, 'upper_doors', text="Upper Doors")
        
        col = split.column()
        sub = col.column()
        sub.prop(self, 'tall_doors', text="Tall Doors")
        sub.prop(self, 'drawer_fronts', text="Drawer Fronts")
        sub.prop(self, 'place_at_scene_origin')
        
    def get_door_selection(self):
        door_bps = []
        
        if self.current_selection:
            for obj in bpy.context.selected_objects:
                if obj.type == 'MESH' or 'CURVE':
                    obj_bp = sn_utils.get_assembly_bp(obj)
                    if obj_bp:
                        if obj_bp.snap.is_cabinet_door or obj_bp.snap.is_cabinet_drawer_front:
                            if obj_bp not in door_bps:
                                door_bps.append(obj_bp)
        
        if self.base_doors or self.tall_doors or self.upper_doors or self.drawer_fronts:
            for obj in bpy.context.scene.objects:
                if obj.type == 'MESH' or 'CURVE':
                    obj_bp = sn_utils.get_assembly_bp(obj)
                    if obj_bp:
                        if obj_bp.snap.is_cabinet_door:
                            product = sn_utils.get_parent_assembly_bp(obj_bp)
                            
                            if self.base_doors:
                                if product.lm_cabinets.product_sub_type in ('Base', 'Sink'):
                                    if obj_bp not in door_bps:
                                        door_bps.append(obj_bp)
                                    
                            if self.tall_doors:
                                if product.lm_cabinets.product_sub_type == 'Tall':
                                    if obj_bp not in door_bps:
                                        door_bps.append(obj_bp)    
                                    
                            if self.upper_doors:
                                if product.lm_cabinets.product_sub_type == 'Upper':
                                    if obj_bp not in door_bps:
                                        door_bps.append(obj_bp)
                                    
                        if obj_bp.snap.is_cabinet_drawer_front and self.drawer_fronts: 
                            if obj_bp not in door_bps:
                                door_bps.append(obj_bp) 
              
        return door_bps            
    
    def execute(self, context):
        props = cabinet_properties.get_scene_props()

        for obj_bp in self.get_door_selection():
            door_assembly = sn_types.Assembly(obj_bp)
            
            group_bp = sn_utils.get_group(path.join(path.dirname(__file__),
                                                 cabinet_properties.DOOR_FOLDER_NAME,
                                                 props.door_category,
                                                 props.get_door_style() + ".blend"))
            new_door = sn_types.Assembly(group_bp)
            new_door.obj_bp.snap.name_object = door_assembly.obj_bp.snap.name_object
            new_door.obj_bp.parent = door_assembly.obj_bp.parent
            new_door.obj_bp.location = door_assembly.obj_bp.location
            new_door.obj_bp.rotation_euler = door_assembly.obj_bp.rotation_euler
            
            property_id = door_assembly.obj_bp.snap.property_id
            
            sn_utils.copy_drivers(door_assembly.obj_bp,new_door.obj_bp)
            sn_utils.copy_prompt_drivers(door_assembly.obj_bp,new_door.obj_bp)
            sn_utils.copy_drivers(door_assembly.obj_x,new_door.obj_x)
            sn_utils.copy_drivers(door_assembly.obj_y,new_door.obj_y)
            sn_utils.copy_drivers(door_assembly.obj_z,new_door.obj_z)
            obj_list = []
            obj_list.append(door_assembly.obj_bp)
            for child in door_assembly.obj_bp.children:
                obj_list.append(child)
            sn_utils.delete_obj_list(obj_list)
            
            new_door.obj_bp.snap.property_id = property_id
            new_door.obj_bp.snap.is_cabinet_door = True
            for child in new_door.obj_bp.children:
                child.snap.property_id = property_id
                if child.type == 'EMPTY':
                    child.hide
                if child.type == 'MESH':
                    child.draw_type = 'TEXTURED'
                    child.snap.comment = props.get_door_style()
                    sn_utils.assign_materials_from_pointers(child)
                if child.snap.type == 'CAGE':
                    child.hide = True
                    
        return {'FINISHED'}

class OPERATOR_Update_Pull_Selection(bpy.types.Operator):
    bl_idname = cabinet_properties.LIBRARY_NAME_SPACE + ".update_pull_selection"
    bl_label = "Change Pulls"
    bl_description = "This will update all of the door pulls that are currently selected"
    bl_options = {'UNDO'}
    
    update_all = bpy.props.BoolProperty(name="Update All",default=False)
    
    def execute(self, context):
        props = cabinet_properties.get_scene_props()
        pulls = []
        
        if self.update_all:
            for obj in context.scene.objects:
                if obj.snap.is_cabinet_pull == True:
                    pulls.append(obj)
        else:
            for obj in context.selected_objects:
                if obj.snap.is_cabinet_pull == True:
                    pulls.append(obj)
                
        for pull in pulls:
            pull_assembly = sn_types.Assembly(pull.parent)
            pull_assembly.set_name(props.pull_name)
            pull_length = pull_assembly.get_prompt("Pull Length")
            new_pull = sn_utils.get_object(path.join(path.dirname(__file__),
                                                  cabinet_properties.PULL_FOLDER_NAME,
                                                  props.pull_category,
                                                  props.pull_name+".blend"))
            new_pull.snap.is_cabinet_pull = True
            new_pull.snap.name_object = pull.snap.name_object
            new_pull.snap.comment = props.pull_name
            new_pull.parent = pull.parent
            new_pull.location = pull.location
            new_pull.rotation_euler = pull.rotation_euler
            sn_utils.assign_materials_from_pointers(new_pull)
            pull_length.set_value(new_pull.dimensions.x)
            sn_utils.copy_drivers(pull,new_pull)
        sn_utils.delete_obj_list(pulls)
        return {'FINISHED'}

class OPERATOR_Update_Column_Selection(bpy.types.Operator):
    bl_idname = cabinet_properties.LIBRARY_NAME_SPACE + ".update_column_selection"
    bl_label = "Update Column"
    bl_description = "This will change the selected column style with the active column style"
    bl_options = {'UNDO'}
    
    column_type: bpy.props.StringProperty(name = "Column Type")
    
    def execute(self, context):
        props = cabinet_properties.get_scene_props()
        
        col_bps = []
        for obj in context.selected_objects:
            obj_bp = sn_utils.get_assembly_bp(obj)
            obj_props = cabinet_properties.get_object_props(obj_bp)
            if obj_props.is_column and obj_bp not in col_bps:
                col_bps.append(obj_bp)
        
        for obj_bp in col_bps:
            column_assembly = sn_types.Assembly(obj_bp)      
    
            new_column_bp = sn_utils.get_group(path.join(path.dirname(__file__),cabinet_properties.COLUMN_FOLDER_NAME,props.column_category,props.column_style+".blend"))
            new_column = sn_types.Assembly(new_column_bp)
            obj_props = cabinet_properties.get_object_props(new_column.obj_bp)
            obj_props.is_column = True
            new_column.obj_bp.snap.name_object = column_assembly.obj_bp.snap.name_object
            new_column.obj_bp.parent = column_assembly.obj_bp.parent
            new_column.obj_bp.location = column_assembly.obj_bp.location
            new_column.obj_bp.rotation_euler = column_assembly.obj_bp.rotation_euler
            
            property_id = column_assembly.obj_bp.snap.property_id
            
            sn_utils.copy_drivers(column_assembly.obj_bp,new_column.obj_bp)
            sn_utils.copy_prompt_drivers(column_assembly.obj_bp,new_column.obj_bp)
            sn_utils.copy_drivers(column_assembly.obj_x,new_column.obj_x)
            sn_utils.copy_drivers(column_assembly.obj_y,new_column.obj_y)
            sn_utils.copy_drivers(column_assembly.obj_z,new_column.obj_z)
            obj_list = []
            obj_list.append(column_assembly.obj_bp)
            for child in column_assembly.obj_bp.children:
                obj_list.append(child)
            sn_utils.delete_obj_list(obj_list)
    
            new_column.obj_bp.snap.property_id = property_id
            for child in new_column.obj_bp.children:
                child.snap.property_id = property_id
                if child.type == 'EMPTY':
                    child.hide
                if child.type == 'MESH':
                    child.draw_type = 'TEXTURED'
                    sn_utils.assign_materials_from_pointers(child)
                if child.snap.type == 'CAGE':
                    child.hide = True

        return {'FINISHED'}
        
class OPERATOR_Place_Applied_Panel(bpy.types.Operator):
    bl_idname = cabinet_properties.LIBRARY_NAME_SPACE + ".place_applied_panel"
    bl_label = "Place Applied Panel"
    bl_description = "This will allow you to place the active panel on cabinets and closets for an applied panel"
    bl_options = {'UNDO'}
    
    #READONLY
    filepath: bpy.props.StringProperty(name="Material Name")
    type_insert: bpy.props.StringProperty(name="Type Insert")
    
    item_name = None
    dir_name = ""
    
    assembly = None
    
    cages = []
    
    def get_panel(self,context):
        props = cabinet_properties.get_scene_props()
        bp = sn_utils.get_group(path.join(path.dirname(__file__),
                                       cabinet_properties.DOOR_FOLDER_NAME,
                                       props.door_category,
                                       props.get_door_style() + ".blend"))
        self.assembly = sn_types.Assembly(bp)
        
    def set_xray(self,turn_on=True):
        cages = []
        for child in self.assembly.obj_bp.children:
            child.show_x_ray = turn_on
            if turn_on:
                child.draw_type = 'WIRE'
            else:
                if child.snap.type == 'CAGE':
                    cages.append(child)
                child.draw_type = 'TEXTURED'
                print("assign_materials_from_pointers from place_applied_panel")
                sn_utils.assign_materials_from_pointers(child)
        sn_utils.delete_obj_list(cages)

    def invoke(self, context, event):
        self.get_panel(context)
        context.window.cursor_set('PAINT_BRUSH')
        context.scene.update() # THE SCENE MUST BE UPDATED FOR RAY CAST TO WORK
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel_drop(self,context,event):
        if self.assembly:
            sn_utils.delete_object_and_children(self.assembly.obj_bp)
        bpy.context.window.cursor_set('DEFAULT')
        sn_utils.delete_obj_list(self.cages)
        return {'FINISHED'}

    def add_to_left(self,part,product):
        self.assembly.obj_bp.parent = product.obj_bp
        
        toe_kick_height = 0
        if product.get_prompt('Toe Kick Height'):
            toe_kick_height = product.get_prompt('Toe Kick Height')
        
        if product.obj_z.location.z > 0:
            self.assembly.obj_bp.location = (0,0,toe_kick_height)
        else:
            self.assembly.obj_bp.location = (0,0,product.obj_z.location.z)
        
        self.assembly.obj_bp.rotation_euler = (0,math.radians(-90),0)
        self.assembly.obj_x.location.x = math.fabs(product.obj_z.location.z) - toe_kick_height
        self.assembly.obj_y.location.y = product.obj_y.location.y
    
    def add_to_right(self,part,product):
        self.assembly.obj_bp.parent = product.obj_bp
        
        toe_kick_height = 0
        if product.get_prompt('Toe Kick Height'):
            toe_kick_height = product.get_prompt('Toe Kick Height')
        
        if product.obj_z.location.z > 0:
            self.assembly.obj_bp.location = (product.obj_x.location.x,0,toe_kick_height)
        else:
            self.assembly.obj_bp.location = (product.obj_x.location.x,0,product.obj_z.location.z)
            
        self.assembly.obj_bp.rotation_euler = (0,math.radians(-90),math.radians(180))
        self.assembly.obj_x.location.x = math.fabs(product.obj_z.location.z) - toe_kick_height
        self.assembly.obj_y.location.y = math.fabs(product.obj_y.location.y)
        
    def add_to_back(self,part,product):
        self.assembly.obj_bp.parent = product.obj_bp
        
        toe_kick_height = 0
        if product.get_prompt('Toe Kick Height'):
            toe_kick_height = product.get_prompt('Toe Kick Height').get_value()
        
        if product.obj_z.location.z > 0:
            self.assembly.obj_bp.location = (0,0,toe_kick_height)
        else:
            self.assembly.obj_bp.location = (0,0,product.obj_z.location.z)
            
        self.assembly.obj_bp.rotation_euler = (0,math.radians(-90),math.radians(-90))
        self.assembly.obj_x.location.x = math.fabs(product.obj_z.location.z) - toe_kick_height
        self.assembly.obj_y.location.y = product.obj_x.location.x
    
    def door_panel_drop(self,context,event):
        selected_point, selected_obj = sn_utils.get_selection_point(context,event,objects=self.cages)
        bpy.ops.object.select_all(action='DESELECT')
        sel_product_bp = sn_utils.get_bp(selected_obj,'PRODUCT')
        sel_assembly_bp = sn_utils.get_assembly_bp(selected_obj)

        if sel_product_bp and sel_assembly_bp:
            product = sn_types.Assembly(sel_product_bp)
            assembly = sn_types.Assembly(sel_assembly_bp)
            if product and assembly and 'Door' not in assembly.obj_bp.snap.name_object:
                self.assembly.obj_bp.parent = None
                if product.placement_type == 'Corner':
                    pass
                    #TODO: IMPLEMENT CORNER PLACEMENT
                else:
                    if 'Left' in assembly.obj_bp.snap.name_object:
                        self.add_to_left(assembly,product)
                    if 'Right' in assembly.obj_bp.snap.name_object:
                        self.add_to_right(assembly,product)
                    if 'Back' in assembly.obj_bp.snap.name_object:
                        self.add_to_back(assembly,product)
        else:
            self.assembly.obj_bp.parent = None
            self.assembly.obj_bp.location = selected_point

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            self.set_xray(False)
            sn_utils.delete_obj_list(self.cages)
            bpy.context.window.cursor_set('DEFAULT')
            if event.shift:
                self.get_panel(context)
            else:
                bpy.ops.object.select_all(action='DESELECT')
                context.scene.objects.active = self.assembly.obj_bp
                self.assembly.obj_bp.select = True
                return {'FINISHED'}
        
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        context.area.tag_redraw()
        
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}
        
        if event.type in {'ESC'}:
            self.cancel_drop(context,event)
            return {'FINISHED'}
        
        return self.door_panel_drop(context,event)


class DROP_OPERATOR_Place_Toe_Kick_Assembly(bpy.types.Operator, PlaceClosetInsert):
    bl_idname = cabinet_properties.LIBRARY_NAME_SPACE + ".place_toe_kick_assembly"
    bl_label = "Place Toe Kick Assembly"
    bl_description = "This places the toe kick assembly"
    bl_options = {'UNDO'}

    # READONLY
    object_name: bpy.props.StringProperty(name="Object Name")

    product = None
    objects = []
    cages = []
    selected_obj = None
    selected_point = None
    selected_cab_1 = None
    max_length = 96.0
    panel_bps = []
    sel_product_bp = None
    valid_cabinet_types = ["Base", "Tall", "Sink"]
    valid_cabinets = None
    valid_cabinet_bps = None

    def get_child_products(self, obj, reverse_order=False):
        products = []

        for child in obj.children:
            if "IS_BP_CABINET" in child:
                child.snap.comment = obj.snap.name_object
                products.append(child)

        # products.sort(key=lambda obj: obj.location.x, reverse=reverse_order)
        products.sort(key=lambda obj: math.fabs(obj.matrix_local.translation.x), reverse=reverse_order)

        return products

    def show_cages(self, context):
        """Show cages for all valid cabinets available for first selection"""
        self.cages.clear()
        targets = [sn_types.Assembly(obj) for obj in context.scene.objects if "CARCASS_TYPE" in obj and "IS_BP_CABINET" in obj]

        for assembly in targets:
            is_corner = assembly.obj_bp.get("IS_CORNER")
            wall = sn_utils.get_wall_bp(assembly.obj_bp)
            floor = sn_utils.get_floor_parent(assembly.obj_bp)
            floor_vis = False
            wall_vis = False

            if wall:
                for child in wall.children:
                    if child.type =='MESH':
                        wall_vis = child.visible_get()
                        break
            if floor:
                floor_vis = floor.visible_get()

            if floor_vis or wall_vis:
                if assembly.obj_bp.get("CARCASS_TYPE") in self.valid_cabinet_types and not is_corner:
                    cage = assembly.get_cage()
                    cage.display_type = 'WIRE'
                    cage.hide_select = False
                    cage.hide_viewport = False
                    self.cages.append(cage)

    def update_cages(self):
        """Hide cages that are no longer valid selections after the first cabinet has been selected"""
        for cage in self.cages:
            if cage.parent not in self.valid_cabinet_bps:
                cage.hide_viewport = True
                cage.hide_select = True

    def get_valid_cabinets(self):
        """
        Get valid cabinets based on first cabinet selection. Selection is made left-to-right.
        Only adjoining cabinets are valid and the toe kick may not be longer than 96 inches.
        This initializes self.valid_cabinets and self.valid_cabinet_bps then updates cage selection.
        """
        self.valid_cabinets = []

        if self.selected_cab_1:
            self.wall_bp = sn_utils.get_wall_bp(self.selected_cab_1.obj_bp)
            self.floor = sn_utils.get_floor_parent(self.selected_cab_1.obj_bp)
            rot_180 = round(math.degrees(self.selected_cab_1.obj_bp.rotation_euler.z)) == 180
            

            if self.floor:
                bp = self.floor
                world_rotation = round(math.degrees(self.floor.rotation_euler.z)) 
            else:
                bp = self.wall_bp
                world_rotation = round(math.degrees(self.wall_bp.rotation_euler.z)) 
            if bp:
                if self.floor and rot_180:
                    cabinet_bps = self.get_child_products(bp, reverse_order=True)
                else:
                    cabinet_bps = self.get_child_products(bp)

                self.valid_cabinets.append(self.selected_cab_1)
                spanned_length = self.selected_cab_1.obj_x.location.x
                prv_cab_dim_x = self.selected_cab_1.obj_x.matrix_world.translation.x

                for bp in cabinet_bps:
                    if bp.rotation_euler.z != self.selected_cab_1.obj_bp.rotation_euler.z:
                        continue
                    if prv_cab_dim_x and bp is not self.selected_cab_1.obj_bp:
                        if bp.matrix_world.translation.x == prv_cab_dim_x:
                            assy = sn_types.Assembly(bp)
                            
                            if world_rotation == 90:
                                spanned_length += abs(assy.obj_x.matrix_world.translation.y) - abs(assy.obj_bp.matrix_world.translation.y) 
                            elif world_rotation == -90:
                                spanned_length += abs(assy.obj_bp.matrix_world.translation.y) - abs(assy.obj_x.matrix_world.translation.y)      
                            else:
                                spanned_length += assy.obj_x.matrix_world.translation.x - assy.obj_bp.matrix_world.translation.x

                            if spanned_length > sn_unit.inch(96):
                                break
                            else:
                                self.valid_cabinets.append(assy)
                                prv_cab_dim_x = assy.obj_x.matrix_world.translation.x
                            
                self.valid_cabinet_bps = [c.obj_bp for c in self.valid_cabinets]
                self.update_cages()

    def execute(self, context):
        self.is_log_shown = False
        self.toe_kick = self.asset
        self.show_cages(context)
        self.include_objects = self.cages

        return super().execute(context)

    def toe_kick_drop(self, context, event):
        if self.selected_obj:
            self.sel_product_bp = sn_utils.get_bp(self.selected_obj, 'PRODUCT')
            product = sn_types.Assembly(self.sel_product_bp)
            hover_product_bp = sn_utils.get_cabinet_bp(self.selected_obj)
            tk_setback = context.scene.lm_cabinets.carcass_defaults.toe_kick_setback
            tk_visible = False
            tk_len = 0
            world_rotation = 0

            if product and product.obj_bp and product.obj_bp.parent:
                world_rotation = round(math.degrees(product.obj_bp.parent.rotation_euler.z)) 

            if hover_product_bp:
                carcass_type = hover_product_bp.get("CARCASS_TYPE")
                if carcass_type in self.valid_cabinet_types:
                    hover_product = sn_types.Assembly(hover_product_bp)
                    rot_180 = False
                    if not tk_visible:
                        self.set_wire_and_xray(self.toe_kick.obj_bp, False)
                        tk_visible = True

                    for child in hover_product.obj_bp.children:
                        if child.get('IS_CAGE'):
                            cage = child
                            cage.hide_select = False
                            cage.select_set(True)

                    if not self.selected_cab_1:
                        self.toe_kick.obj_bp.parent = hover_product.obj_bp
                        self.toe_kick.obj_x.location.x = hover_product.obj_x.location.x
                        self.toe_kick.obj_y.location.y = hover_product.obj_y.location.y + tk_setback

                    elif hover_product.obj_bp == self.selected_cab_1.obj_bp or not self.valid_cabinets:
                        self.toe_kick.obj_x.location.x = self.selected_cab_1.obj_x.location.x
                        self.toe_kick.obj_y.location.y = self.selected_cab_1.obj_y.location.y + tk_setback

                    elif hover_product.obj_bp in self.valid_cabinet_bps:
                        rot_180 = round(math.degrees(self.selected_cab_1.obj_bp.rotation_euler.z)) == 180
                        cab_1_matrix_loc_x = self.selected_cab_1.obj_bp.matrix_world.translation.x
                        cab_2_matrix_obj_x = hover_product.obj_x.matrix_world.translation.x

                        if self.floor and rot_180:
                            self.toe_kick.obj_x.location.x = cab_1_matrix_loc_x - cab_2_matrix_obj_x
                        else:
                            self.toe_kick.obj_x.location.x = cab_2_matrix_obj_x - cab_1_matrix_loc_x

                        self.toe_kick.obj_y.location.y = self.selected_cab_1.obj_y.location.y + tk_setback

                    if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
                        if self.selected_cab_1:
                            if hover_product and hover_product.obj_bp:
                                Cabinet_Width = self.selected_cab_1.obj_x.snap.get_var("location.x", "Cabinet_Width")
                                driver_vars = [Cabinet_Width]
                                formula = "Cabinet_Width"

                                if len(self.valid_cabinets) > 1:
                                    for i, cab in enumerate(self.valid_cabinets):
                                        if world_rotation == 90:
                                            exclude_cabinet = cab.obj_bp.matrix_world.translation.y > hover_product_bp.matrix_world.translation.y
                                        elif world_rotation == -90:
                                            exclude_cabinet = cab.obj_bp.matrix_world.translation.y < hover_product_bp.matrix_world.translation.y
                                            if exclude_cabinet == False:
                                                exclude_cabinet = cab.obj_bp.matrix_world.translation.y > self.selected_cab_1.obj_bp.matrix_world.translation.y
                                        else:
                                            exclude_cabinet = cab.obj_bp.matrix_world.translation.x > hover_product_bp.matrix_world.translation.x

                                        if cab.obj_bp is self.selected_cab_1.obj_bp:
                                            continue
                                        elif not self.floor and not rot_180 and exclude_cabinet:
                                            continue
                                        else:
                                            eval("driver_vars.append(cab.obj_x.snap.get_var('location.x', 'Cab_Width_{}'))".format(str(i+1), str(i+1)))
                                            formula += "+Cab_Width_{}".format(str(i+1))

                                self.toe_kick.dim_x(formula, driver_vars)
                                sn_utils.set_wireframe(self.toe_kick.obj_bp, False)
                                bpy.context.window.cursor_set('DEFAULT')
                                bpy.ops.object.select_all(action='DESELECT')
                                context.view_layer.objects.active = self.toe_kick.obj_bp
                                self.toe_kick.obj_bp.select_set(True)
                                self.toe_kick.obj_y["IS_MIRROR"] = True

                                if self.floor:
                                    collections = bpy.data.collections
                                    scene_coll = context.scene.collection
                                    floor_coll = collections["Floor"]

                                    if floor_coll:
                                        if self.floor.name in scene_coll.objects:
                                            scene_coll.objects.unlink(self.floor)
                                        sn_utils.add_assembly_to_collection(self.toe_kick.obj_bp, floor_coll, recursive=True)
                                        sn_utils.remove_assembly_from_collection(self.toe_kick.obj_bp, scene_coll, recursive=True)

                                return self.finish(context)
                            else:
                                return {'RUNNING_MODAL'}

                    if event.type == 'LEFTMOUSE' and event.value == 'PRESS' and self.selected_cab_1 == None:
                        self.selected_cab_1 = hover_product
                        self.get_valid_cabinets()
                        bpy.context.window.cursor_set('DEFAULT')
                        bpy.ops.object.select_all(action='DESELECT')
                        context.view_layer.objects.active = self.toe_kick.obj_bp
                        self.toe_kick.obj_bp.parent =  self.selected_cab_1.obj_bp

                        for child in self.selected_cab_1.obj_bp.children:
                            if child.get("IS_BP_CARCASS"):
                                carcass = sn_types.Assembly(child)

                        tk_setback = context.scene.lm_cabinets.carcass_defaults.toe_kick_setback
                        dim_y = self.selected_cab_1.obj_y.location.y + tk_setback
                        self.toe_kick.obj_y.location.y = dim_y

                        toe_kick_height = carcass.get_prompt("Toe Kick Height").distance_value
                        self.toe_kick.get_prompt("Toe Kick Height").set_value(toe_kick_height)

                        if self.toe_kick.get_prompt("Toe Kick Setback"):
                            self.toe_kick.get_prompt("Toe Kick Setback").set_value(tk_setback)

                        self.toe_kick.obj_x.location.x = hover_product.obj_x.location.x
                        self.toe_kick.obj_bp.location.z = 0

                        self.toe_kick.obj_bp.snap.type_group = 'INSERT'
                        self.toe_kick.obj_bp.snap.export_as_subassembly = True
                        self.toe_kick.obj_bp["IS_BP_TOE_KICK_INSERT"] = True
                        self.toe_kick.obj_bp.sn_closets.is_toe_kick_insert_bp = True

                    return {'RUNNING_MODAL'}

        return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        context.area.tag_redraw()
        self.reset_selection()
        bpy.ops.object.select_all(action='DESELECT')
        self.selected_point, self.selected_obj, _ = sn_utils.get_selection_point(context, event, objects=self.objects)

        if not self.toe_kick:
            self.toe_kick = self.asset

        if self.event_is_cancel_command(event):
            context.area.header_text_set(None)
            return self.cancel_drop(context)

        if self.event_is_pass_through(event):
            return {'PASS_THROUGH'}
        
        return self.toe_kick_drop(context, event)

class OPERATOR_Remove_Location_Constraint(bpy.types.Operator):
    """ This will remove a cabinet's location constraint.
    """
    bl_idname = cabinet_properties.LIBRARY_NAME_SPACE + ".remove_location_constraint"
    bl_label = "Remove Location Constraint"
    bl_description = "This will remove a cabinet's location constraint."
    bl_options = {'UNDO'}
    obj_bp_name: bpy.props.StringProperty(name="Cabinet Base Point Name")

    def execute(self, context):
        obj_bp = bpy.data.objects.get(self.obj_bp_name)
        obj_bp_matrix_local_x = obj_bp.matrix_local.translation.x
        if obj_bp and obj_bp.constraints:
            for constraint in obj_bp.constraints:
                if constraint.type == "COPY_LOCATION":
                    obj_bp.constraints.remove(constraint)

        obj_bp.location.x = obj_bp_matrix_local_x

        return {'FINISHED'}
    
bpy.utils.register_class(OPERATOR_Frameless_Standard_Draw_Plan)
#bpy.utils.register_class(OPERATOR_Cabinet_Update)
bpy.utils.register_class(OPERATOR_Auto_Add_Molding)
bpy.utils.register_class(OPERATOR_Delete_Molding)
bpy.utils.register_class(OPERATOR_Update_Door_Selection)
bpy.utils.register_class(OPERATOR_Update_Pull_Selection)
bpy.utils.register_class(OPERATOR_Update_Column_Selection)
bpy.utils.register_class(OPERATOR_Place_Applied_Panel)
bpy.utils.register_class(DROP_OPERATOR_Place_Toe_Kick_Assembly)
bpy.utils.register_class(OPERATOR_Remove_Location_Constraint)