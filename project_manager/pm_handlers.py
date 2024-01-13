import bpy
import os
from bpy.app.handlers import persistent
import xml.etree.ElementTree as ET
from . import pm_utils
from snap import sn_utils
from snap import sn_types
from snap.libraries.closets.data import data_closet_carcass
from snap.libraries.kitchen_bath import cabinets

@persistent
def create_project_path(scene):
    # Can't use in register function, as context is _RestrictContext until addons loaded
    addon_prefs = bpy.context.preferences.addons[__name__.split(".")[0]].preferences

    if not os.path.exists(addon_prefs.project_dir):
        os.makedirs(addon_prefs.project_dir)


@persistent
def check_section_prompt_id(scene=None):
    """Ensure all hanging sections have the correct prompt id tag"""
    sections = [
        obj for obj in bpy.data.objects
        if obj.get("IS_BP_CLOSET") and obj.name in sn_utils.get_main_scene().objects]

    for section_bp in sections:
        exclude = [
            section_bp.get("IS_BP_ISLAND"),
            section_bp.get("IS_TOPSHELF_SUPPORT_CORBELS"),
            section_bp.get("IS_WALL_CLEAT"),
            section_bp.get("IS_BP_CORNER_SHELVES"),
            section_bp.get("IS_BP_L_SHELVES")]

        if any(exclude):
            continue

        # //// Trap and correct Classy Hood Cabinets from old files that have the wrong prompt id
        if section_bp.get("IS_BP_HOOD_CABINET"):
            section_bp["ID_PROMPT"] = "sn_appliances.parametric_wall_appliance"
            section = cabinets.Hood(section_bp)
            section.id_prompt = "sn_appliances.parametric_wall_appliance"
            section.type_assembly = "PRODUCT"
            section.update()
        elif section_bp.get("ID_PROMPT") != "sn_closets.openings":
            section_bp["ID_PROMPT"] = "sn_closets.openings"
            section = data_closet_carcass.Closet_Carcass(section_bp)
            section.id_prompt = "sn_closets.openings"
            section.type_assembly = "PRODUCT"
            section.update()


@persistent
def check_countertop_selection(scene=None):
    """Standard Quartz countertop colors: "Marbella" and "Nimbus" were removed 2.6.0 -> 2.6.1"""
    current_room_ver = sn_utils.get_room_version()
    closet_materials = bpy.context.scene.closet_materials
    countertop_type = closet_materials.countertops.get_type()
    countertop_index = closet_materials.ct_color_index

    if bpy.data.is_saved:
        if current_room_ver < "2.6.1":
            if not closet_materials.ct_updated_to_261:
                if countertop_type.name == "Standard Quartz":
                    # "Marbella" and "Nimbus"
                    if countertop_index in (7, 9):
                        countertop_index = 0
                    elif countertop_index == 8:
                        countertop_index -= 1
                    elif countertop_index > 9:
                        countertop_index -= 2

                    closet_materials.ct_color_index = countertop_index
                    closet_materials.ct_updated_to_261 = True

        elif current_room_ver < "2.8.0":
            print("Updating room to 2.8.0")
            closet_materials.color_change = False
            if not closet_materials.ct_updated_to_280:
                if countertop_type.name == "Standard Quartz":
                    idx = int(countertop_index)
                    # Added "Apollo"
                    if countertop_index == 0:
                        idx += 1
                    # Added "Bianco Tiza"
                    elif countertop_index < 2:
                        idx += 2
                    # Added "Gemstone Beige"
                    elif countertop_index < 11:
                        idx += 3
                    # Added "Steel"
                    else:
                        idx += 4

                    closet_materials.ct_color_index = idx
                    closet_materials.ct_updated_to_280 = True


@persistent
def check_pull_selection(scene=None):
    current_room_ver = sn_utils.get_room_version()
    app_ver = sn_utils.get_version_str()
    closet_options = bpy.context.scene.sn_closets.closet_options
    closet_materials = bpy.context.scene.closet_materials

    if bpy.data.is_saved:
        default_pull = "155.00.932"
        pulls = [
            obj.snap.name_object
            for obj in bpy.data.objects
            if obj.type == 'MESH' and obj.parent and (obj.parent.sn_closets.is_handle or obj.snap.is_cabinet_pull) and obj.visible_get()]

        if current_room_ver < app_ver:
            if not closet_materials.pull_sel_updated_to_261:
                if closet_options.pull_category == "Other - Customer Provided":
                    closet_options.pull_category = "Polished Chrome"
                elif closet_options.pull_category == "Other - Special Hardware":
                    closet_options.pull_category = "Satin Bronzed Copper"
                elif closet_options.pull_category == "Polished Chrome":
                    closet_options.pull_category = "Satin Nickel"
                elif closet_options.pull_category == "Satin Bronzed Copper":
                    closet_options.pull_category = "Stainless Steel Look"

                if pulls:
                    if all(x == default_pull for x in pulls):
                        message = f"This room is using default pulls ({default_pull})"
                        bpy.ops.snap.pull_message_box('INVOKE_DEFAULT', message=message)

                closet_materials.pull_sel_updated_to_261 = True

@persistent
def check_oversize_color_selection(scene=None):
    """
    Version 2.6.3 removes all oversize color options except 'Snow Drift XL'.
    Update files created < 2.6.3 to this color.
    """
    current_room_ver = sn_utils.get_room_version()
    closet_materials = bpy.context.scene.closet_materials
    mat_type = closet_materials.materials.get_mat_type()

    if current_room_ver < "2.6.3":
        print("Room file created pre 2.6.3. Version 2.6.3 removes all oversize color options except 'Snow Drift XL', setting index to 0")
        if mat_type.name == "Oversized Material":
            closet_materials.color_change = True
        else:
            closet_materials.color_change = False

        closet_materials.oversized_color_index = 0
        closet_materials.dd_oversized_color_index = 0


@persistent
def load_projects(scene=None):
    """ Loads all projects.
    """
    pm_utils.load_projects()


def register():
    bpy.app.handlers.load_post.append(load_projects)
    bpy.app.handlers.load_post.append(check_pull_selection)
    bpy.app.handlers.load_post.append(check_countertop_selection)
    bpy.app.handlers.load_post.append(check_section_prompt_id)
    bpy.app.handlers.load_post.append(check_oversize_color_selection)
    bpy.app.handlers.load_post.append(create_project_path)


def unregister():
    bpy.app.handlers.load_post.remove(load_projects)
    bpy.app.handlers.load_post.remove(check_pull_selection)
    bpy.app.handlers.load_post.remove(check_countertop_selection)
    bpy.app.handlers.load_post.remove(check_section_prompt_id)
    bpy.app.handlers.load_post.remove(check_oversize_color_selection)
    bpy.app.handlers.load_post.remove(create_project_path)
