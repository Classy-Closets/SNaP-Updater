import bpy
import os
from bpy.app.handlers import persistent
import xml.etree.ElementTree as ET
from . import pm_utils
from snap import sn_utils


@persistent
def create_project_path(scene):
    # Can't use in register function, as context is _RestrictContext until addons loaded
    addon_prefs = bpy.context.preferences.addons[__name__.split(".")[0]].preferences

    if not os.path.exists(addon_prefs.project_dir):
        os.makedirs(addon_prefs.project_dir)


@persistent
def check_pull_selection(scene=None):
    current_room_ver = sn_utils.get_room_version()
    app_ver = sn_utils.get_version_str()

    if bpy.data.is_saved:
        default_pull = "155.00.932"
        pulls = [
            obj.snap.name_object
            for obj in bpy.data.objects
            if obj.type == 'MESH' and obj.parent and obj.parent.sn_closets.is_handle]

        if all(x == default_pull for x in pulls):
            if current_room_ver < app_ver:
                message = f"This room is using default pulls ({default_pull})"
                bpy.ops.snap.pull_message_box('INVOKE_DEFAULT', message=message)


@persistent
def load_projects(scene=None):
    """ Loads all projects.
    """
    pm_utils.load_projects()


def register():
    bpy.app.handlers.load_post.append(load_projects)
    bpy.app.handlers.load_post.append(check_pull_selection)
    bpy.app.handlers.load_post.append(create_project_path)


def unregister():
    bpy.app.handlers.load_post.remove(load_projects)
    bpy.app.handlers.load_post.remove(check_pull_selection)
    bpy.app.handlers.load_post.remove(create_project_path)
