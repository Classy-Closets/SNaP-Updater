import os
import shutil
import pathlib

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty

from snap import sn_utils
from snap import sn_paths


class SN_WM_OT_message_box(bpy.types.Operator):
    bl_idname = "snap.message_box"
    bl_label = "System Info"

    message: StringProperty(name="Message", description="Message to Display")
    message2: bpy.props.StringProperty(name="Message_2", default="")
    icon: StringProperty(name="Icon", description="Icon name", default='NONE')
    width: bpy.props.IntProperty(name="Width", default=300)

    def check(self, context):
        return True

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=self.width)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        for line in self.message.split('\n'):
            box.label(text=line, icon=self.icon)

    def execute(self, context):
        return {'FINISHED'}


class SN_WM_OT_pull_message_box(bpy.types.Operator):
    bl_idname = "snap.pull_message_box"
    bl_label = "System Info"

    message: StringProperty(name="Message", description="Message to Display")
    message2: bpy.props.StringProperty(name="Message_2", default="")
    icon: StringProperty(name="Icon", description="Icon name", default='NONE')
    width: bpy.props.IntProperty(name="Width", default=300)

    pull_selection: bpy.props.EnumProperty(
        name="Pull Hardware Selection",
        items=[
            ('SELECT', "Select Pull Hardware", "Select Pull Hardware"),
            ('KEEP_DEFAULT', "Keep Default Pulls", "Keep Default Pulls")],
        default='SELECT')

    def check(self, context):
        return True

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=self.width)

    def draw(self, context):
        layout = self.layout
        box = layout.box()

        for line in self.message.split('\n'):
            box.label(text=line, icon=self.icon)

        row = box.row()
        row.prop(self, "pull_selection", expand=True)

    def execute(self, context):
        if self.pull_selection == 'SELECT':
            bpy.context.scene.sn_closets.closet_defaults.no_pulls = True
        else:
            bpy.context.scene.sn_closets.closet_defaults.no_pulls = False
        return {'FINISHED'}


class SN_WM_OT_snap_drag_drop(Operator):
    bl_idname = "wm.snap_drag_drop"
    bl_label = "Drag and Drop"
    bl_description = "This is a special operator that will be called when an image is dropped from the file browser"

    filepath: StringProperty(name="Message", default="Error")

    def invoke(self, context, event):
        path = pathlib.Path(self.filepath)

        if path.suffix == ".blend":
            bpy.ops.wm.open_mainfile(filepath=self.filepath)
            return {'FINISHED'}

        return self.execute(context)

    def execute(self, context):
        wm_props = context.window_manager.snap
        scene_props = context.scene.snap

        if scene_props.active_library_name in wm_props.libraries:
            lib = wm_props.libraries[scene_props.active_library_name]
            eval('bpy.ops.' + lib.drop_id + '("INVOKE_DEFAULT",filepath=self.filepath)')

        return {'FINISHED'}


class SN_WM_OT_load_snap_defaults(Operator):
    bl_idname = "snap.load_snap_defaults"
    bl_label = "Load SNap Defaults"

    keep_startup_file: BoolProperty(name="Keep Current Startup File", default=True)
    keep_prefs: BoolProperty(name="Keep Current User Preferences", default=True)

    # Persistent startup data
    cam_bore_face_depth = None
    toe_kick_type = None

    @classmethod
    def poll(cls, context):
        return True

    def init_db(self):
        import time
        time_start = time.time()
        franchise_location = sn_utils.get_franchise_location()
        path = os.path.join(sn_paths.CSV_DIR_PATH, "CCItems_" + franchise_location + ".csv")
        if not os.path.exists(path):
            path = os.path.join(sn_paths.CSV_DIR_PATH, "CCItems_PHX.csv")
        filename = os.path.basename(path)
        filepath = path
        bpy.ops.snap.import_csv('EXEC_DEFAULT', filename=filename, filepath=filepath, rebuild_db=True)
        print("Rebuild Database Finished: %.4f sec" % (time.time() - time_start))

    def copy_config_files(self, path):
        src_userpref_file = sn_paths.PREFS_PATH
        src_startup_file = sn_paths.STARTUP_FILE_PATH

        if not os.path.exists(path):
            os.makedirs(path)

        if not self.keep_prefs:
            dst_userpref_file = os.path.join(path, "userpref.blend")
            shutil.copyfile(src_userpref_file, dst_userpref_file)

        if not self.keep_startup_file:
            dst_startup_file = os.path.join(path, "startup.blend")
            shutil.copyfile(src_startup_file, dst_startup_file)

    def use_auto_set_scripts_dir(self):
        bl_ver = "{}.{}".format(bpy.app.version[0], bpy.app.version[1])
        bl_dir = os.path.dirname(bpy.app.binary_path)
        startup_dir = os.path.join(bl_dir, bl_ver, "scripts", "startup")
        src = os.path.join(sn_paths.SNAP_CONFIG_DIR, "set_scripts_path.py")
        dst = os.path.join(startup_dir, "set_scripts_path.py")
        shutil.copyfile(src, dst)
        print("Found testing environment, using auto-set scripts directory:", dst)

    def remove_old_data(self):
        for subdir, dirs, files in os.walk(sn_paths.CLOSET_THUMB_DIR):
            for dir in dirs:
                if "Closet Products -" in dir:
                    print("Removing:", os.path.join(subdir, dir))
                    shutil.rmtree(os.path.join(subdir, dir))

    def get_persistient_startup_data(self):
        if not self.keep_startup_file:
            closet_defaults = bpy.context.scene.sn_closets.closet_defaults
            closet_machining = bpy.context.scene.closet_machining

            self.cam_bore_face_depth = closet_machining.cam_bore_face_depth
            self.toe_kick_type = closet_defaults.toe_kick_type

    def set_persistient_startup_data(self, config_path):
        if not self.keep_startup_file:
            # Set properties from previous startup file
            update_startup_file = False

            # Load the startup file
            if os.path.exists(config_path):
                startup_path = os.path.join(config_path, "startup.blend")
                bpy.ops.wm.open_mainfile(filepath=startup_path)
                closet_defaults = bpy.context.scene.sn_closets.closet_defaults
                closet_machining = bpy.context.scene.closet_machining

                # Cam Bore Face Depth (KD Shelf Drill Depth)
                if self.cam_bore_face_depth:
                    if closet_machining.cam_bore_face_depth != self.cam_bore_face_depth:
                        closet_machining.cam_bore_face_depth = self.cam_bore_face_depth
                        update_startup_file = True

                # Toe Kick Type
                if self.toe_kick_type:
                    if closet_defaults.toe_kick_type != self.toe_kick_type:
                        closet_defaults.toe_kick_type = self.toe_kick_type
                        update_startup_file = True

                # Save the current scene as the new startup file
                if update_startup_file:
                    bpy.ops.wm.save_as_mainfile(filepath=startup_path)
                    bpy.ops.wm.read_homefile(app_template="")

    def execute(self, context):
        import ctypes
        VK_R = 0x52
        config_path = sn_paths.CONFIG_PATH
        app_template_path = sn_paths.APP_TEMPLATE_PATH
        franchise_location = context.preferences.addons['snap'].preferences.franchise_location

        bpy.ops.script.execute_preset(
            filepath=sn_paths.SNAP_THEME_PATH,
            menu_idname='USERPREF_MT_interface_theme_presets')

        self.get_persistient_startup_data()
        self.copy_config_files(config_path)
        self.copy_config_files(app_template_path)
        self.remove_old_data()
        self.use_auto_set_scripts_dir()
        context.preferences.addons['snap'].preferences.franchise_location = franchise_location
        self.set_persistient_startup_data(config_path)
        self.init_db()

        bl_ver = "{}.{}".format(bpy.app.version[0], bpy.app.version[1])
        if bl_ver != "3.0":
            import subprocess
            import requests
            import tempfile

            tmp_dir = tempfile.gettempdir()
            tmp_filepath = os.path.join(tmp_dir, 'SNaP-2.2.2-setup-windows-x64.exe')
            url = 'https://github.com/Classy-Closets/Snap-Update-Testing/releases/download/v2.2.2/SNaP-2.2.2-update-setup-windows-x64.exe'
            print("Updating Blender version:", bl_ver, " -> 3.0")

            if os.path.exists(tmp_filepath):
                print("updater exists: ", tmp_filepath)
                subprocess.Popen(tmp_filepath)
            else:
                r = requests.get(url, allow_redirects=True)
                open(tmp_filepath, 'wb').write(r.content)
                print("Saved updater to:", tmp_filepath)
                if os.path.exists(tmp_filepath):
                    subprocess.Popen(tmp_filepath)

            ctypes.windll.user32.keybd_event(VK_R)
            bpy.ops.wm.quit_blender()

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=550)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row()
        row.label(
            text="Are you sure you want to restore the SNap defaults?",
            icon='QUESTION')

        row = box.row()
        row.label(
            text="You will need to restart the application for the changes to take effect.",
            icon='BLANK1')

        row = box.row()
        row.prop(self, "keep_startup_file")
        row = box.row()
        row.prop(self, "keep_prefs")


classes = (
    SN_WM_OT_message_box,
    SN_WM_OT_pull_message_box,
    SN_WM_OT_snap_drag_drop,
    SN_WM_OT_load_snap_defaults,
)

register, unregister = bpy.utils.register_classes_factory(classes)
