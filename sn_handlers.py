import os
import shutil
import stat

import bpy
from bpy.app.handlers import persistent
from snap import sn_utils
from snap import sn_paths
from snap import sn_types
from . import sn_utils
from . import addon_updater_ops
from snap.libraries.kitchen_bath import cabinet_properties

@persistent
def load_driver_functions(scene=None):
    """ Load Default Drivers
    """
    import inspect
    from snap import sn_driver_functions
    for name, obj in inspect.getmembers(sn_driver_functions):
        if name not in bpy.app.driver_namespace:
            bpy.app.driver_namespace[name] = obj


@persistent
def load_materials_from_db(scene=None):
    import time
    time_start = time.time()
    path = os.path.join(sn_paths.CSV_DIR_PATH, "CCItems_" + bpy.context.preferences.addons['snap'].preferences.franchise_location + ".csv")
    filename = os.path.basename(path)
    filepath = path
    bpy.ops.snap.import_csv('EXEC_DEFAULT', filename=filename, filepath=filepath)
    print("load_materials_from_db Finished: %.4f sec" % (time.time() - time_start))


# @persistent
# def load_pointers(scene=None):
#     snap_pointers.write_pointer_files()
#     snap_pointers.update_pointer_properties()




@persistent
def assign_material_pointers(scene=None):

    def get_material_indexes(mat_props, mat_types, room_mat_color, is_garage_material):
        if is_garage_material:
            if room_mat_color == "Winter White (Oxford White)":
                return 6, 4
            mat_type = mat_props.materials.mat_types["Garage Material"]
            for i, color in enumerate(mat_type.colors):
                if room_mat_color in color.name:
                    return 6, i
        else:
            for mat_idx, mat_type in enumerate(mat_types):
                for color_idx, color in enumerate(mat_type.colors):
                    if room_mat_color in color.name:
                        return mat_idx, color_idx

        return None, None

    def get_part_mesh(obj_bp, mesh_type):
        for obj in obj_bp.children:
            if obj.type == 'MESH' and obj.snap.type_mesh == mesh_type:
                return obj

    def get_mat_slot_item_name(obj, slot_name, type):
        part_mesh = get_part_mesh(obj, type)
        mat_slot = part_mesh.snap.material_slots[slot_name]
        if mat_slot:
            item_name = mat_slot.item_name
            return item_name

    def get_converted_name(name):
        new_name = ""
        if name in mat_props.color_conversions:
            converted_name = mat_props.color_conversions[name].new_name
            new_name = converted_name
        return new_name if new_name else name

    def message_box(type_name, color_name):
        bpy.ops.snap.message_box(
            'INVOKE_DEFAULT',
            message="\"{}\"\nThis {} color is no longer available to order!".format(color_name, type_name))

    if bpy.data.is_saved:
        # If 2Ds generated
        if "_Main" in bpy.data.scenes:
            scene = bpy.data.scenes["_Main"]
        else:
            scene = bpy.data.scenes["Scene"]

        mat_props = scene.closet_materials
        custom_colors = mat_props.use_custom_color_scheme
        mat_type = mat_props.materials.get_mat_type()
        edge_type = mat_props.edges.get_edge_type()
        cleat_edge_type = mat_props.secondary_edges.get_edge_type()
        door_drawer_mat_type = mat_props.door_drawer_materials.get_mat_type()
        door_drawer_edge_type = mat_props.door_drawer_edges.get_edge_type()

        if mat_props.mat_color_index >= len(mat_type.colors):
            mat_props.mat_color_index = len(mat_type.colors) - 1

        if mat_props.door_drawer_mat_color_index >= len(door_drawer_mat_type.colors):
            mat_props.door_drawer_mat_color_index = len(door_drawer_mat_type.colors) - 1

        # if not custom_colors:
        for obj in scene.objects:
            part_mesh = None
            room_mat_color = None
            is_garage_material = False

            if mat_type.type_code == 1 or mat_type.type_code == 4:
                if "IS_BP_DRAWER_FRONT" in obj or "IS_DOOR" in obj:
                    part_mesh = get_part_mesh(obj, 'CUTPART')

            else:
                if "IS_BP_PANEL" in obj:
                    part_mesh = get_part_mesh(obj, 'CUTPART')

            if part_mesh:
                use_unique_material = part_mesh.sn_closets.use_unique_material
                if not use_unique_material:
                    bottom_mat_ptr = part_mesh.snap.material_slots["Bottom"].pointer_name
                    if bottom_mat_ptr == "Garage_Interior_Surface":
                        is_garage_material = True
                    room_mat_color = part_mesh.snap.material_slots["Top"].item_name
                    break

        if room_mat_color:
            current_mat_color = mat_type.get_mat_color().name

            if room_mat_color in mat_props.color_conversions:
                converted_name = mat_props.color_conversions[room_mat_color].new_name
                room_mat_color = converted_name

            if current_mat_color != room_mat_color:
                mat_types = mat_props.materials.mat_types
                new_type_idx, new_color_idx = get_material_indexes(mat_props, mat_types, room_mat_color, is_garage_material)
                if new_type_idx is not None and new_color_idx is not None:
                    mat_props.mat_type_index = new_type_idx
                    mat_type.set_color_index(new_color_idx)
                else:
                    mat_props.discontinued_color = room_mat_color
                    message_box("Material", room_mat_color)

        if custom_colors:
            edge = None
            garage_room_edge = None
            cleat_edge = None
            door_drawer_mat = None
            door_drawer_edge = None
            room_stain_color = None

            for obj in scene.objects:
                part_mesh = None
                color_exists = False

                # Edge
                if not edge and "IS_BP_PANEL" in obj:
                    item_name = get_mat_slot_item_name(obj, "FrontBackEdge", 'CUTPART')
                    if item_name:
                        edge = item_name
                        continue

                # Cleat Edge
                if not cleat_edge and "IS_CLEAT" in obj:
                    item_name = get_mat_slot_item_name(obj, "Edgebanding", 'CUTPART')
                    if item_name:
                        cleat_edge = item_name
                        continue

                # Door/drawer mat
                if not room_stain_color and "IS_DOOR" in obj:
                    # Wood door
                    part_mesh = get_part_mesh(obj, 'BUYOUT')
                    if part_mesh and not room_stain_color:
                        mat_slot = part_mesh.material_slots[0]
                        if mat_slot:
                            room_stain_color = mat_slot.material.name
                            continue

                # Melamine door
                if not door_drawer_mat and "IS_DOOR" in obj:
                    part_mesh = get_part_mesh(obj, 'CUTPART')
                    if part_mesh:
                        mat_name = get_mat_slot_item_name(obj, "Top", 'CUTPART')
                        if mat_name:
                            door_drawer_mat = mat_name
                        edge_name = get_mat_slot_item_name(obj, "TopBottomEdge", 'CUTPART')
                        if edge_name:
                            door_drawer_edge = edge_name
                        continue

                # Garage material custom edge
                if "IS_BP_PLANT_ON_TOP" in obj:
                    part_mesh = get_part_mesh(obj, 'CUTPART')
                    garage_room_edge = part_mesh.snap.material_slots["Edgebanding"].pointer_name

            # Set custom edge
            if edge:
                edge = get_converted_name(edge)
                if edge_type.get_edge_color().name != edge:
                    new_type_idx, new_color_idx = get_material_indexes(mat_props, mat_props.edges.edge_types, edge, is_garage_material)
                    if new_type_idx is not None and new_color_idx is not None:
                        mat_props.edge_type_index = new_type_idx
                        edge_type.set_color_index(new_color_idx)
                    else:
                        mat_props.edge_discontinued_color = edge
                        message_box("Edge", edge)

            if garage_room_edge:
                # if garage material
                print("Garage", mat_type.name)

            # Set custom cleat edge
            if cleat_edge:
                cleat_edge = get_converted_name(cleat_edge)
                if cleat_edge_type.get_edge_color().name != cleat_edge:
                    new_type_idx, new_color_idx = get_material_indexes(mat_props, mat_props.secondary_edges.edge_types, cleat_edge, is_garage_material)
                    if new_type_idx is not None and new_color_idx is not None:
                        mat_props.secondary_edge_type_index = new_type_idx
                        cleat_edge_type.set_color_index(new_color_idx)
                    else:
                        mat_props.cleat_edge_discontinued_color = cleat_edge
                        message_box("Edge", cleat_edge)

            # Set custom door/drawer mat
            if door_drawer_mat:
                door_drawer_mat = get_converted_name(door_drawer_mat)
                if door_drawer_mat_type.get_mat_color().name != door_drawer_mat:
                    new_type_idx, new_color_idx = get_material_indexes(mat_props, mat_props.door_drawer_materials.mat_types, door_drawer_mat, is_garage_material)
                    if new_type_idx is not None and new_color_idx is not None:
                        mat_props.door_drawer_mat_type_index = new_type_idx
                        door_drawer_mat_type.set_color_index(new_color_idx)
                    else:
                        mat_props.dd_mat_discontinued_color = door_drawer_mat
                        message_box("Material", door_drawer_mat)

            # Set custom door/drawer edge
            if door_drawer_edge:
                door_drawer_edge = get_converted_name(door_drawer_edge)
                if door_drawer_edge_type.get_edge_color().name != door_drawer_edge:
                    new_type_idx, new_color_idx = get_material_indexes(mat_props, mat_props.door_drawer_edges.edge_types, door_drawer_edge, is_garage_material)
                    if new_type_idx is not None and new_color_idx is not None:
                        mat_props.door_drawer_edge_type_index = new_type_idx
                        door_drawer_edge_type.set_color_index(new_color_idx)
                    else:
                        mat_props.dd_edge_discontinued_color = door_drawer_edge
                        message_box("Edge", door_drawer_edge)

            # Set custom stain color
            if room_stain_color:
                room_stain_color = get_converted_name(room_stain_color)
                color_found = False

                for i, color in enumerate(mat_props.stain_colors):
                    if color.name == room_stain_color:
                        mat_props.stain_color_index = i
                        mat_props.upgrade_type_index = 2
                        color_found = True

                if not color_found:
                    for i, color in enumerate(mat_props.paint_colors):
                        if color.name == room_stain_color:
                            mat_props.paint_color_index = i
                            mat_props.upgrade_type_index = 1
                            color_found = True

                if not color_found:
                    mat_props.stain_discontinued_color = room_stain_color
                    message_box("Stain/Paint", room_stain_color)

    bpy.ops.closet_materials.assign_materials(only_update_pointers=True)


@persistent
def assign_materials(scene=None):
    bpy.ops.closet_materials.assign_materials()


@persistent
def sync_spec_groups(scene):
    """ Syncs Spec Groups with the current library modules
    """
    bpy.ops.sn_material.reload_spec_group_from_library_modules()


@persistent
def load_libraries(scene=None):
    wm_props = bpy.context.window_manager.snap
    scene_props = bpy.context.scene.snap
    prefs = bpy.context.preferences.addons["snap"].preferences

    wm_props.add_library(
        name="Product Library",
        lib_type='SNAP',
        root_dir=sn_paths.CLOSET_ROOT,
        thumbnail_dir=sn_paths.CLOSET_THUMB_DIR,
        drop_id='sn_closets.drop',
        use_custom_icon=True,
        icon='closet_lib',
    )

    wm_props.add_library(
        name="Kitchen Bath Library",
        lib_type='SNAP',
        root_dir=sn_paths.KITCHEN_BATH_ROOT,
        thumbnail_dir=sn_paths.KITCHEN_BATH_THUMB_DIR,
        drop_id='sn_closets.drop',
        use_custom_icon=True,
        icon='cabinet_lib',
    )

    wm_props.add_library(
        name="Window and Door Library",
        lib_type='SNAP',
        root_dir=sn_paths.DOORS_AND_WINDOWS_ROOT,
        thumbnail_dir=sn_paths.DOORS_AND_WINDOWS_THUMB_DIR,
        drop_id='windows_and_doors.drop',
        use_custom_icon=False,
        icon='MOD_LATTICE'
    )

    wm_props.add_library(
        name="Appliance Library",
        lib_type='SNAP',
        root_dir=sn_paths.APPLIANCE_DIR,
        thumbnail_dir=sn_paths.APPLIANCE_THUMB_DIR,
        drop_id='sn_appliances.drop',
        use_custom_icon=False,
        icon='TOPBAR',
    )

    wm_props.add_library(
        name="Object Library",
        lib_type='STANDARD',
        root_dir=sn_paths.OBJECT_DIR,
        drop_id='sn_library.drop_object_from_library',
        use_custom_icon=False,
        icon='OBJECT_DATA'
    )

    wm_props.add_library(
        name="Material Library",
        lib_type='STANDARD',
        root_dir=sn_paths.MATERIAL_DIR,
        drop_id='sn_library.drop_material_from_library',
        use_custom_icon=False,
        icon='MATERIAL'
    )

    wm_props.get_library_assets()

    if not bpy.data.is_saved or scene_props.active_library_name == "Product Library":
        path = os.path.join(sn_paths.CLOSET_THUMB_DIR, sn_paths.DEFAULT_CATEGORY)

        if scene_props.active_library_name == "Kitchen Bath Library" and prefs.enable_kitchen_bath_lib:
            path = os.path.join(sn_paths.KITCHEN_BATH_THUMB_DIR, sn_paths.DEFAULT_KITCHEN_BATH_CATEGORY)
        else:
            scene_props.active_library_name = "Product Library"

        if os.path.exists(path):
            sn_utils.update_file_browser_path(bpy.context, path)
            bpy.ops.sn_library.change_library_category(category=sn_paths.DEFAULT_CATEGORY)


@persistent
def load_library_modules(scene):
    """ Register Every Library Module on Startup
    """
    bpy.ops.snap.load_library_modules()


@persistent
def default_settings(scene=None):
    scene = bpy.context.scene
    prefs = bpy.context.preferences
    bg_mode = bpy.app.background
    # Units
    scene.unit_settings.system = 'IMPERIAL'
    scene.unit_settings.length_unit = 'INCHES'
    # Render
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'GPU'
    scene.cycles.preview_samples = 0
    scene.cycles.use_preview_denoising = True
    scene.cycles.preview_denoiser = 'AUTO'
    scene.cycles.max_bounces = 6
    scene.cycles.transparent_max_bounces = 6
    scene.cycles.transmission_bounces = 6
    prefs.view.render_display_type = 'NONE'
    # Prefs
    prefs.use_preferences_save = False  # Disable autosave
    if not bpy.data.is_saved:
        scene.closet_materials.set_defaults()
    else:
        scene.closet_materials.defaults_set = True

    defaults = cabinet_properties.get_scene_props().size_defaults
    defaults.load_default_heights()


@persistent
def init_machining_collection(scene=None):
    mac_col = bpy.data.collections.get("Machining")
    if mac_col:
        for obj in mac_col.objects:
            obj.display_type = 'WIRE'
        mac_col.hide_viewport = True


def del_dir(action, name, exc):
    os.chmod(name, stat.S_IWRITE)
    os.remove(name)


@persistent
def check_for_update(scene=None):
    source_dir = os.path.join(os.path.dirname(__file__), "snap_updater", "source")
    staging_dir = os.path.join(os.path.dirname(__file__), "snap_updater", "update_staging")
    update_dirs = [source_dir, staging_dir]

    for dir_path in update_dirs:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path, onerror=del_dir)

    if "snap" in bpy.context.preferences.addons.keys():
        addon_updater_ops.check_for_update_background()


@persistent
def create_wall_collections(scene=None):
    bg_mode = bpy.app.background
    existing_walls = []

    for obj in bpy.data.objects:
        if obj.get("IS_BP_WALL"):
            existing_walls.append(obj)
            break

    if bpy.data.is_saved and existing_walls and not bg_mode:
        collections = bpy.data.collections
        wall_coll = {}

        for coll in collections:
            if coll.snap.type == 'WALL':
                wall_coll[coll.name] = wall_coll

        if not wall_coll:
            backup_path = bpy.data.filepath.replace(".blend", "-backup.blend")
            print("Saving backup", backup_path)
            bpy.ops.wm.save_as_mainfile(filepath=backup_path, copy=True)
            print("Rebuilding wall collections...")
            bpy.ops.sn_roombuilder.rebuild_wall_collections()


def register():
    bpy.app.handlers.load_post.append(check_for_update)
    bpy.app.handlers.load_post.append(load_driver_functions)
    bpy.app.handlers.load_post.append(load_materials_from_db)
    bpy.app.handlers.load_post.append(sync_spec_groups)
    bpy.app.handlers.load_post.append(default_settings)
    bpy.app.handlers.load_post.append(assign_material_pointers)
    bpy.app.handlers.save_pre.append(assign_materials)
    bpy.app.handlers.load_post.append(load_libraries)
    bpy.app.handlers.load_post.append(load_library_modules)
    bpy.app.handlers.load_post.append(init_machining_collection)
    bpy.app.handlers.load_post.append(create_wall_collections)


def unregister():
    bpy.app.handlers.load_post.remove(check_for_update)
    bpy.app.handlers.load_post.remove(load_driver_functions)
    bpy.app.handlers.load_post.remove(load_materials_from_db)
    bpy.app.handlers.load_post.remove(sync_spec_groups)
    bpy.app.handlers.load_post.remove(default_settings)
    bpy.app.handlers.load_post.remove(assign_material_pointers)
    bpy.app.handlers.save_pre.remove(assign_materials)
    bpy.app.handlers.load_post.remove(load_libraries)
    bpy.app.handlers.load_post.remove(load_library_modules)
    bpy.app.handlers.load_post.remove(init_machining_collection)
    bpy.app.handlers.load_post.remove(create_wall_collections)