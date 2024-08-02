import bpy
import os
import re
import shutil
from snap import sn_utils, sn_paths, sn_types, sn_db, sn_unit
from snap.libraries.closets import project_pricing

import pathlib
from distutils.dir_util import copy_tree
import xml.etree.ElementTree as ET
from copy import deepcopy
import subprocess
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
from bpy.props import (StringProperty,
                       BoolProperty,
                       EnumProperty,
                       IntProperty)
from shutil import copyfile

from . import pm_utils, pm_props
import webbrowser
import uuid
import ctypes
import random
from datetime import datetime, timedelta, timezone
import pyperclip
import boto3
import time
import math
import mathutils
from urllib.parse import quote


# AWS_S3_REGION_NAME = 'us-west-2'
# AWS_S3_BUCKET_NAME = 'snap-proposals'
# AWS_S3_ACCESS_KEY_ID = 'gAAAAABl-2ovZa1SmRKioZSAnqdQlpmoRAynY0xbGQ5kO-ofJlXVjkehms-cQ5euGONLGH2A0xh2_ulRVlkxojPLBG73MYAc34hAJUly2t00BN3YOgY8JRc='
# AWS_S3_ACCESS_KEY = 'gAAAAABl-2d3mvtwZEBFupQt6hNjpEYI9jyy5kpGxxi4FnnuOHx3ypBWgD3GCu1oPt6g3Q6T6bVcbCNh3vqgL3oRNgIBxV5gJ5WsqzzdKsTNLOgb6WUNPNaheBEJmUGpvodb6DrGTjm2'

AWS_S3_REGION_NAME = 'us-west-1'
AWS_S3_BUCKET_NAME = 'snap-proposals-1'
AWS_S3_ACCESS_KEY_ID = 'gAAAAABmDxSuCsGbViR6sNeOi0L2JPBjkB66tKgZ-eKSWFVa0dBhNq8R1gd68B_waB9qmjQzC-QOrxeEeuJmnDwpuZIl897x1ca9Q48xURkOKbqexKgJYlc='
AWS_S3_ACCESS_KEY = 'gAAAAABmDxSue4C4ftTHw1XpBU3FXm4ZX2CBFWAA2yUv5BsBje1WL8up9Uh8mzlpOueFc83b1FHuxelztkLxygTuqhR3mjbYj8NADxWFMkGwj34_fY-ejZ1_FzLTSwLKMACJ-nB7FuWO'
PROPOSAL_LIFECYCLE_DAYS = 30



def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=pm_utils.decode(AWS_S3_ACCESS_KEY_ID),
        aws_secret_access_key=pm_utils.decode(AWS_S3_ACCESS_KEY),
        region_name=AWS_S3_REGION_NAME
    )

def upload_object_to_s3(file_name, bucket_name, object_name=None):
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    content_type = ''
    if object_name.endswith('.html'):
            content_type = 'text/html'
    
    s3_client = get_s3_client()
    public_folder = 'public/'

    try:
        response = s3_client.upload_file(file_name, bucket_name, public_folder + object_name, ExtraArgs={'ContentType': content_type})
        print("response=",response)
    except Exception as e:
        print(f"Upload failed: {e}")
        return False
    return True

def delete_s3_objects_by_prefix(bucket_name, prefix):
    
    s3_client = get_s3_client()
    target_prefix = 'public/' + prefix
    print("target_prefix=",target_prefix)

    if target_prefix != 'public/' and target_prefix != 'public//':
        objects_to_delete = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=target_prefix)

        # Check if there are objects to delete
        if 'Contents' in objects_to_delete:
            objects = [{'Key': obj['Key']} for obj in objects_to_delete['Contents']]
            s3_client.delete_objects(Bucket=bucket_name, Delete={'Objects': objects})
            print(f"All objects with prefix '{target_prefix}' deleted.")
        else:
            print(f"No objects found with prefix '{target_prefix}'.")

    return True

def get_s3_object_url(bucket_name, object_name, region_name):
    return f"https://{bucket_name}.s3-{region_name}.amazonaws.com/public/{quote(object_name)}"


class SNAP_OT_Copy_Room(Operator):
    bl_idname = "product_manager.copy_room"
    bl_label = "Copies the selected Room"
    bl_description = "Copies selected Room"

    file_path: StringProperty(name="File Path", description="Room File Path", subtype="FILE_PATH")
    new_room_name: StringProperty(name="Room Name", description="Room Name", default="")
    src_room = None
    new_room = None

    def register_room_in_xml(self):
        project_root, room_file = os.path.split(self.file_path)
        project_name = os.path.split(project_root)[1]
        room_relative_path = os.path.join(project_name, room_file)
        xml_path = os.path.join(project_root, '.snap', project_name + '.ccp')

        xml = ET.parse(xml_path)
        room_node = None

        rooms_node = xml.findall('.//Rooms')[0]
        for i, room in enumerate(rooms_node):
            if room.attrib['path'] == room_relative_path:
                room_node = room
                index = i
                break

        new_attrib = deepcopy(room_node.attrib)
        new_attrib['name'] = self.new_room.file_name
        new_attrib['path'] = os.path.join(project_name, self.new_room.file_name + '.blend')
        new_element = ET.Element('Room', attrib=new_attrib)
        new_element.text = new_attrib['name']
        rooms_node.insert(index + 1, new_element)
        xml.write(xml_path)

    def invoke(self, context, event):
        wm = context.window_manager

        proj_wm = wm.sn_project
        project = proj_wm.projects[proj_wm.project_index]
        self.src_room = project.rooms[project.room_index]
        self.new_room_name = self.src_room.name + " - Copy"
        return wm.invoke_props_dialog(self, width=sn_utils.get_prop_dialog_width(400))

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)
        col.label(text="'{}'".format(self.src_room.name))
        col.separator()
        col.label(text="New Room Name:")
        col.prop(self, "new_room_name", text="")

    def execute(self, context):
        props = context.window_manager.sn_project

        # only really necessary when the user copies the current room
        if len(bpy.data.filepath) > 0:
            bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

        clean_room_name = pm_props.CollectionMixIn().get_clean_name(self.new_room_name)
        new_filepath = os.path.join(os.path.dirname(self.file_path), clean_room_name) + ".blend"

        if len(props.projects) > 0:
            project = props.projects[props.project_index]
            self.new_room = project.add_room_from_file(self.new_room_name, new_filepath)
            project.main_tabs = 'ROOMS'

        new_path = os.path.join(os.path.dirname(self.new_room.file_path), self.new_room.file_name + ".blend")
        copyfile(self.file_path, new_path)
        self.register_room_in_xml()
        bpy.ops.wm.open_mainfile(filepath=new_path)
        return {'FINISHED'}


class SNAP_OT_Create_Project(Operator):
    """ This will create a project.
    """
    bl_idname = "project_manager.create_project"
    bl_label = "Create New Project"
    bl_description = "Creates a project"

    project_name: StringProperty(name="Project Name", description="Project Name", default="New Project")

    def listdir(self, path):
        return [d for d in os.listdir(path) if os.path.isdir(d)]

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=sn_utils.get_prop_dialog_width(400))

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)
        row = col.row()
        row.label(text="Project Name:")
        row.prop(self, "project_name", text="")

    def execute(self, context):
        wm = context.window_manager.sn_project
        pm_props.create_project_flag = True

        if self.project_name == "":
            return {'FINISHED'}

        if re.compile("[@_!#$'%^&*()<>?/\|}{~:]").search(self.project_name) == None:
            proj = wm.projects.add()
            proj.init(self.project_name.strip())

            for index, project in enumerate(wm.projects):
                if project.name == self.project_name:
                    wm.project_index = index
            pm_props.create_project_flag = False
            return {'FINISHED'}
        else:
            bpy.ops.snap.log_window(
                "INVOKE_DEFAULT",
                message="Project Name Error",
                message2="Project Name CANNOT contain: [@_!#$'%^&*()<>?/\|}{~:]",
                icon="ERROR",
                width=400)
            return {'FINISHED'}


class SNAP_OT_Copy_Project(Operator):
    """ This will copy a project.
    """
    bl_idname = "project_manager.copy_project"
    bl_label = "Copy Project"
    bl_description = "Copies a project"

    project_name: StringProperty(name="Project Name", description="Project Name", default="New Project")
    index: IntProperty(name="Project Index")
    source_project = None

    @classmethod
    def poll(cls, context):
        wm = context.window_manager.sn_project
        return len(wm.projects) > 0

    def invoke(self, context, event):
        wm = context.window_manager
        proj_wm = wm.sn_project
        self.source_project = proj_wm.projects[proj_wm.project_index]
        self.project_name = self.source_project.name + " - Copy"
        return wm.invoke_props_dialog(self, width=sn_utils.get_prop_dialog_width(400))

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)
        col.label(text="'{}'".format(self.source_project.name))
        col.separator()
        col.label(text="New Project Name:")
        col.prop(self, "project_name", text="")

    def update_project_file(self, project_path):
        """Update .ccp"""
        ccp_path = os.path.join(project_path, ".snap", self.source_project.name + ".ccp")
        new_ccp_path = os.path.join(project_path, ".snap", self.project_name + ".ccp")

        # Rename copied .ccp
        if os.path.exists(ccp_path):
            os.rename(ccp_path, new_ccp_path)

        # Update name in .ccp
        if os.path.exists(new_ccp_path):
            tree = ET.parse(new_ccp_path)
            root = tree.getroot()

            for elm in root.findall("ProjectInfo"):
                items = list(elm)

                for item in items:
                    if item.tag == 'name':
                        item.text = self.project_name

            # Update room filepaths
            for elm in root.findall("Rooms"):
                items = list(elm)

                for item in items:
                    bfile_path = pathlib.Path(item.attrib['path'])
                    new_path = os.path.join(self.project_name, bfile_path.parts[-1])
                    item.attrib['path'] = new_path

            tree.write(new_ccp_path)

    def execute(self, context):
        wm = context.window_manager.sn_project

        if not self.project_name:
            return {'FINISHED'}

        # Check if project name exists
        existing_project = wm.projects.get(self.project_name)
        if existing_project:
            bpy.ops.snap.message_box(
                'INVOKE_DEFAULT',
                message="Cannot create project that already exists: '{}'".format(existing_project.name))
            return {'FINISHED'}

        # Copy project
        dst_path = os.path.join(self.source_project.dir_path, "..", self.project_name)
        shutil.copytree(self.source_project.dir_path, dst_path)
        self.update_project_file(dst_path)
        hidden_dir = os.path.join(dst_path, ".snap")
        if os.path.exists(hidden_dir):
            pm_utils.set_file_attr_hidden(hidden_dir)

        # Reload projects and set index to copied project
        pm_utils.reload_projects()

        for index, project in enumerate(wm.projects):
            if project.name == self.project_name:
                wm.project_index = index

        return {'FINISHED'}


class SNAP_OT_Import_Project(Operator):
    """ This will import a project.
    """
    bl_idname = "project_manager.import_project"
    bl_label = "Import Project"
    bl_description = "Imports a project"

    filename: StringProperty(name="Project File Name", description="Project file name to import")
    filepath: StringProperty(name="Project Path", description="Project path to import", subtype="FILE_PATH")
    directory: StringProperty(name="Project File Directory Name", description="Project file directory name")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if pathlib.Path(self.filename).suffix == ".ccp":
            copy_tree(self.directory, os.path.join(pm_utils.get_project_dir(), self.filename.split('.')[0]))
            pm_utils.reload_projects()

        return {'FINISHED'}


class SNAP_OT_Unarchive_Project(Operator):
    """ This will unarchive a project.
    """
    bl_idname = "project_manager.unarchive_project"
    bl_label = "Unarchive Project"
    bl_description = "Unarchives a project"

    filename: StringProperty(name="Project File Name", description="Project file name to import")
    filepath: StringProperty(name="Project Path", description="Project path to import", subtype="FILE_PATH")
    directory: StringProperty(name="Project File Directory Name", description="Project file directory name")

    def invoke(self, context, event):
        self.filepath = os.path.join(os.path.expanduser("~"), "Documents", "SNaP Archived Projects", "")
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        import zipfile
        if pathlib.Path(self.filename).suffix == ".zip":
            with zipfile.ZipFile(os.path.join(pm_utils.get_archive_dir(), self.filename), "r") as zip_ref:
                zip_ref.extractall(os.path.join(pm_utils.get_project_dir(), self.filename.split('.')[0]))
                pm_utils.reload_projects()

        if os.path.exists(os.path.join(pm_utils.get_project_dir(), self.filename.split('.')[0])):
            os.remove(os.path.join(pm_utils.get_archive_dir(), self.filename))
        return {'FINISHED'}


class SNAP_OT_Delete_Project(Operator):
    bl_idname = "project_manager.delete_project"
    bl_label = "Delete Project"
    bl_options = {'UNDO'}

    index: IntProperty(name="Project Index")

    archive_project: BoolProperty(name="No, send to an archived folder",
                                          default=False,
                                          description="Archive project to zipped folder")

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column()

        props = context.window_manager.sn_project
        proj = props.projects[self.index]

        col.label(text="'{}'".format(proj.name))
        col.label(text="Are you sure you want to delete this project?")
        col.prop(self,'archive_project',text="Archive Project upon removal")

    def execute(self, context):
        props = context.window_manager.sn_project
        proj = props.projects[self.index]
        cleaned_name = proj.get_clean_name(proj.name)
        proj.proj_dir = os.path.join(pm_utils.get_project_dir(), cleaned_name)
        rbin_path = os.path.join(os.path.expanduser("~"), "Documents", "SNaP Projects Recycle Bin")
        rbin_proj_path = os.path.join(rbin_path, cleaned_name)
        archive_path = os.path.join(os.path.expanduser("~"), "Documents", "SNaP Archived Projects")
        props.projects.remove(self.index)
        props.project_index = 0

        if os.path.exists(rbin_proj_path):
            shutil.rmtree(rbin_proj_path)

        if not os.path.exists(rbin_path):
            os.mkdir(rbin_path)

        if self.archive_project:
            # import zipfile
            if os.path.isfile(os.path.join(archive_path, cleaned_name + ".zip")):
                os.remove(os.path.join(archive_path, cleaned_name + ".zip"))
            if not os.path.exists(archive_path):
                os.mkdir(archive_path)
            shutil.move(shutil.make_archive(proj.proj_dir, 'zip', proj.proj_dir), archive_path)

        shutil.move(proj.proj_dir, rbin_path)

        return {'FINISHED'}


class SNAP_OT_Add_Room(Operator):
    """ This will add a room to the active project.
    """
    bl_idname = "project_manager.add_room"
    bl_label = "Add Room"
    bl_description = "Adds a room to the active project"

    room_name: StringProperty(name="Room Name", description="Room Name")
    room_category: EnumProperty(name="Room Category",
                                description="Select the Category of the Room",
                                items=[
                                    ("Please Select", "REQUIRED Please Select a Category",
                                    "Please Select a Category"),
                                    ("FG-CLST", "Closet", "Closet"),
                                    ("FG-ENTC", "Entertainment Center", "Entertainment Center"),
                                    ("FG-GARG", "Garage", "Garage"),
                                    ("FG-HMOF", "Home Office", "Home Office"),
                                    ("FG-LNDY", "Laundry", "Laundry"),
                                    ("FG-MDRM", "Mud Room", "Mud Room"),
                                    ("FG-PNTY", "Pantry", "Pantry"),
                                    ("FG-KITN", "Kitchen", "Kitchen"),
                                    ("FG-BATH", "Bathroom", "Bathroom"),
                                    ("FG-RFCE", "Reface", "Reface"),
                                    ("FG-RMDL", "Remodel", "Remodel"),
                                    ("FG-STNE", "Stone", "Stone"),
                                    ("FG-SPEC", "Specialty", "Specialty"),
                                    ("FG-COMM", "Commercial", "Commercial"),
                                    ("FG-CMSS", "Commercial Solid Surface", "Commercial Solid Surface"),
                                    ("FG-CMST", "Commercial Stone", "Commercial Stone")])

    def execute(self, context):
        props = context.window_manager.sn_project

        if re.compile("[@_!#$'%^&*()<>?/\|}{~:]").search(self.room_name) == None:
            if len(props.projects) > 0:
                project = props.projects[props.project_index]
                project.add_room(self.room_name)
                project.main_tabs = 'ROOMS'
            return {'FINISHED'}
        else:
            bpy.ops.snap.log_window(
                "INVOKE_DEFAULT",
                message="Room Name Error",
                message2="Room Name CANNOT contain: [@_!#$'%^&*()<>?/\|}{~:]",
                icon="ERROR",
                width=400)
            return {'FINISHED'}


class SNAP_OT_Open_Room(Operator):
    """ This will open room .blend file.
    """
    bl_idname = "project_manager.open_room"
    bl_label = "Open Room"
    bl_description = "Opens a room file"

    file_path: StringProperty(name="File Path", description="Room File Path", subtype="FILE_PATH")

    def execute(self, context):
        props = context.window_manager.sn_project

        if len(props.projects) > 0:
            project = props.projects[props.project_index]

        if bpy.data.is_saved:
            bpy.ops.wm.save_mainfile()

        room_path = os.path.join(project.dir_path, os.path.basename(self.file_path))
        bpy.ops.wm.open_mainfile(filepath=room_path)
        sn_utils.update_accordions_prompt()
        sn_utils.fetch_mainscene_walls()

        return {'FINISHED'}


class SNAP_OT_Delete_Room(Operator):
    bl_idname = "project_manager.delete_room"
    bl_label = "Delete Room"
    bl_options = {'UNDO'}

    room_name: StringProperty(name="Room Name", description="Room Name")
    index: IntProperty(name="Project Index")
    invoke_default: BoolProperty(name="Invoke Default", default=False)

    def invoke(self, context, event):
        wm = context.window_manager
        self.invoke_default = True
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column()

        props = context.window_manager.sn_project
        proj = props.projects[props.project_index]
        room = proj.rooms[self.index]

        col.label(text="'{}'".format(room.name))
        col.label(text="Are you sure you want to delete this room?")

    def execute(self, context):
        props = context.window_manager.sn_project
        # if there is no project active, skip
        if len(props.projects) == 0:
            return {'FINISHED'}

        if not self.invoke_default:
            proj = props.projects[props.current_file_project]
            room = proj.rooms[props.current_file_room]
            self.room_name = room.name
            for i, room in enumerate(proj.rooms):
                if room.name == self.room_name:
                    proj.rooms.remove(i)
        else:
            proj = props.projects[props.project_index]
            room = proj.rooms[self.index]
            self.room_name = room.name
            proj.rooms.remove(self.index)

        tree = ET.parse(proj.file_path)
        root = tree.getroot()

        for elm in root.findall("Rooms"):
            items = list(elm)

            for item in items:
                if item.get("name") == self.room_name:
                    rel_path = os.path.join(*item.get("path").split(os.sep)[-2:])
                    proj_dir = pm_utils.get_project_dir()
                    room_filepath = os.path.join(proj_dir, rel_path)
                    elm.remove(item)

        tree.write(proj.file_path)

        # ToDo: install send2trash to interpreter to use here instead
        os.remove(room_filepath)
        proj.room_index = 0

        if proj.name == props.current_file_project:
            if self.room_name == props.current_file_room:
                bpy.ops.wm.read_homefile()

        return {'FINISHED'}


class SNAP_OT_Import_Room(Operator, ImportHelper):
    """ This will import a room into the currently selected project.
    """
    bl_idname = "project_manager.import_room"
    bl_label = "Import Room"
    bl_description = "Imports a room into the currently selected project"

    filename: StringProperty(name="Project File Name", description="Project file name to import")
    filepath: StringProperty(name="Project Path", description="Project path to import", subtype="FILE_PATH")
    directory: StringProperty(name="Project File Directory Name", description="Project file directory name")
    # ImportHelper mixin class uses this
    filename_ext = ".blend"
    filter_glob: StringProperty(default="*.blend", options={'HIDDEN'}, maxlen=255)

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        wm = context.window_manager
        proj_wm = wm.sn_project
        self.project = proj_wm.projects[proj_wm.project_index]

        if pathlib.Path(self.filename).suffix == ".blend":
            room = self.project.add_room(self.filename.replace(".blend", ""), save_room_file=False)
            new_filepath = os.path.join(self.project.dir_path, room.name + ".blend")
            copyfile(self.filepath, new_filepath)

        else:
            message = "This is not a valid file!: {}".format(self.filename)
            bpy.ops.snap.message_box('INVOKE_DEFAULT', message=message, icon='ERROR')

        return {'FINISHED'}


class SNAP_OT_Select_All_Rooms(Operator):
    bl_idname = "project_manager.select_all_rooms"
    bl_label = "Select All Rooms"
    bl_description = "This will select all of the rooms in the project"


    select_all: BoolProperty(name="Select All", default=True)

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        props = context.window_manager.sn_project
        proj = props.projects[props.project_index]

        for room in proj.rooms:
            room.selected = self.select_all

        return{'FINISHED'}


class SNAP_OT_Prepare_Project_XML(Operator):
    """ Create Project XML"""
    bl_idname = "project_manager.prepare_proj_xml"
    bl_label = "Create Project XML"
    bl_options = {'UNDO'}

    tmp_filename = "export_temp.py"
    xml_filename = "snap_job.xml"
    proj_dir: StringProperty(name="Project Directory", subtype='DIR_PATH')

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=256)

    def draw(self, context):
        layout = self.layout
        props = context.window_manager.sn_project
        proj = props.get_project()
        layout.label(text="Project: {}".format(proj.name))
        box = layout.box()

        for room in proj.rooms:
            col = box.column(align=True)
            row = col.row()
            row.prop(room, "selected", text="")
            row.label(text=room.name)

        row = layout.row()
        row.operator(
            "project_manager.select_all_rooms", text="Select All", icon='CHECKBOX_HLT').select_all = True
        row.operator(
            "project_manager.select_all_rooms", text="Deselect All", icon='CHECKBOX_DEHLT').select_all = False

    def create_prep_script(self):
        nrm_dir = self.proj_dir.replace("\\", "/")
        file = open(os.path.join(bpy.app.tempdir, self.tmp_filename), 'w')
        file.write("import bpy\n")
        file.write("bpy.ops.sn_export.export_xml('INVOKE_DEFAULT', xml_path='{}')\n".format(nrm_dir))
        file.close()

        return os.path.join(bpy.app.tempdir, self.tmp_filename)

    def execute(self, context):
        debug_mode = context.preferences.addons["snap"].preferences.debug_mode
        debug_mac = context.preferences.addons["snap"].preferences.debug_mac
        proj_props = bpy.context.window_manager.sn_project
        proj_name = proj_props.projects[proj_props.project_index].name
        path = os.path.join(pm_utils.get_project_dir(), proj_name, self.xml_filename)
        proj = proj_props.projects[proj_props.project_index]

        if bpy.data.is_dirty:
            # If file has not been saved, prepare closet for export and save main file
            bpy.ops.closet_machining.prepare_closet_for_export()
            bpy.ops.wm.save_mainfile()

        if os.path.exists(path):
            os.remove(path)

        self.proj_dir = os.path.join(pm_utils.get_project_dir(), proj_name)
        script_path = self.create_prep_script()

        # Call blender in background and run XML export on each room file in project
        for room in proj.rooms:
            if room.selected:
                subprocess.call(bpy.app.binary_path + ' "' + room.file_path + '" -b --python "' + script_path + '"')

        if debug_mode and debug_mac:
            bpy.ops.wm.open_mainfile(filepath=bpy.data.filepath)
            if "Machining" in bpy.data.collections:
                for obj in bpy.data.collections["Machining"].objects:
                    obj.display_type = 'WIRE'

        return {'FINISHED'}


class SNAP_OT_Load_Projects(Operator):
    bl_idname = "project_manager.load_projects"
    bl_label = "Load Projects"
    bl_description = ""

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        pm_utils.load_projects()

        return{'FINISHED'}
    

class SNAP_OT_Proposal_Select_All_Rooms(Operator):
    bl_idname = "project_manager.proposal_select_all_rooms"
    bl_label = "Select All Rooms"
    bl_description = "This will select all of the rooms in the Project Proposal room list"

    select_all: BoolProperty(name="Select All", default=True)

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        project = context.window_manager.sn_project.get_project()
        for room in project.rooms:
            room.prop_selected = self.select_all

        return{'FINISHED'}    


class SNAP_OT_Proposal_Prepare_Room_For_3D_Export(Operator):
    """Prepare Room For 3D Export"""
    bl_idname = "project_manager.prepare_room_for_3d_export"
    bl_label = "Prepare Room For 3D Export"
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        return self.execute(context)

    def save_export_to_glb(self):
        # export the final 3d scene to glb for better export to web
        if "io_scene_gltf2" not in bpy.context.preferences.addons:

            # Destination path in Blender's addon directory
            blender_addons_path = bpy.utils.user_resource('SCRIPTS') + "/addons"
            dest_path = os.path.join(blender_addons_path, "io_scene_gltf2")
            addon_folder_path = os.path.join(sn_paths.ROOT_DIR, "io_scene_gltf2")

            # Copy the addon folder to Blender's addon directory
            if not os.path.exists(dest_path):
                shutil.copytree(addon_folder_path, dest_path)
 
            bpy.ops.preferences.addon_enable(module="io_scene_gltf2")

        file_path = bpy.data.filepath.replace(".blend", ".gltf")
        bpy.ops.export_scene.gltf(filepath=file_path, export_format='GLB')

    def apply_all_modifiers(self, objects):
        for obj in objects:
            if obj.type == 'MESH':  # Assuming you only want to apply modifiers to mesh objects
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='OBJECT')  # Ensure the object is in object mode
                for modifier in obj.modifiers:
                    bpy.ops.object.modifier_apply({"object": obj}, modifier=modifier.name)
                
                obj.vertex_groups.clear()

    def import_texture_image(self, blend_file_path, material_name):
        new_texture_imaage = None
        imported_material = None

        if material_name + '_temp' not in bpy.data.materials:
            print("looking for material.name: ", material_name)

             # rename original material to avoid conflicts...
            existing_material = bpy.data.materials.get(material_name)
            existing_material.name = material_name + "_original"

            # append proper material definition from library...
            with bpy.data.libraries.load(blend_file_path, link=False) as (data_from, data_to):
                if material_name in data_from.materials:
                    data_to.materials.append(material_name)
                    
                else:
                    print(f"Material '{material_name}' not found in {blend_file_path}")
            
            # Rename the appended material
            imported_material = bpy.data.materials.get(material_name)
            if imported_material:
                imported_material.name = imported_material.name + '_temp'

            # retore original material name
            existing_material.name = material_name.replace("_original", "")
        
        else:
            imported_material = bpy.data.materials.get(material_name + '_temp')
            # print("found existing material=",imported_material.name)

        # find the texture image in the imported material
        nodes = imported_material.node_tree.nodes
        for node in nodes:
            if node.type == "TEX_IMAGE" and self.is_texture_image(node.image.name):
                new_texture_imaage = node.image
                print("found imported texture=",node.image.name) 

        return new_texture_imaage
     
    def is_texture_image(self, image_name):
        texture_image_names = ['DIFFUSE', 'COLOR','InteriorCarpet_02.jpg']
        for texture_image_name in texture_image_names:
            if texture_image_name in image_name:
                return True
        return False
                    
    def material_needs_simplification(self, material):
        target_materials = ['Biltmore Cherry Hardwood','Burled Cherry Hardwood','Golden Maple','Hazelnut Birch Hardwood',
                            'Natural Anagre Hardwood','Outdoor Deck Planks','Pacific Birch Hardwood','Provincial Oak Hardwood',
                            'Santao Rose Hardwood','Sparrow Walnut Hardwood','Vintage Planks Hardwood','Windsor Mahogany Hardwood',
                            'Beige Tile','Checker Tile','Grey Tile','Marble Tile',
                            '-Carpet Cool Grey','Carpet Burgundy','Carpet Burnt Orange','Carpet Butter Cream','Carpet Caramel',
                            'Carpet Charcoal','Carpet Coco','Carpet Deep Blue','Carpet Emerald','Carpet Gun Metal',
                            ]
        if material.name in target_materials:
            return True
        else:
            return False
    
    def create_sipmle_materials(self, objects):
        # print("start create_sipmle_materials obj=",obj.name)

        for obj in objects:

            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='OBJECT')

            # Ensure the object has a UV map
            if obj.type == 'MESH' and not obj.data.uv_layers:
                if len(obj.data.vertices) > 1 and len(obj.data.polygons) > 0:
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.uv.smart_project()
                    bpy.ops.object.mode_set(mode='OBJECT')

            for slot in obj.material_slots:
                if slot.material:
                    old_material = slot.material

                    if self.material_needs_simplification(old_material):
                        # print("material=",old_material.name)
                        nodes = old_material.node_tree.nodes
                        old_texture_image = None
                        imported_texture_image = None
        
                        for node in nodes:
                            if node.type == "TEX_IMAGE" and self.is_texture_image(node.image.name):
                                old_texture_image = node.image
                                                    
                        if old_texture_image:
                            print("old_texture_image=",old_texture_image.name)

                            if old_texture_image.name == 'InteriorCarpet_02.jpg':
                                # if texture image from old material, import texture image from current material libray... currently just carpet materials but could be expanded.
                                imported_texture_image = self.import_texture_image(os.path.join(sn_paths.MATERIAL_DIR, "Flooring - Carpet", old_material.name + ".blend"), old_material.name)
                                if imported_texture_image:
                                    old_texture_image = imported_texture_image
                            
                            # Create a new material
                            new_material = bpy.data.materials.new(name=old_material.name + '_suv')
                            new_material.use_nodes = True

                            # Get the material's node tree
                            nodes = new_material.node_tree.nodes
                            links = new_material.node_tree.links

                            # Clear any existing nodes
                            nodes.clear()

                            # Create the necessary nodes
                            uv_map_node = nodes.new(type='ShaderNodeUVMap')
                            uv_map_node.location = (-300, 0)
                            uv_map_node.uv_map = obj.data.uv_layers[0].name  # Use the name of the first UV map

                            mapping_node = nodes.new(type='ShaderNodeMapping')
                            mapping_node.location = (-300, 0)
                            mapping_node.inputs['Scale'].default_value = (5.0, 5.0, 5.0)  # Set the scale to 5

                            image_texture_node = nodes.new(type='ShaderNodeTexImage')
                            image_texture_node.location = (-100, 0)
                            image_texture_node.image = old_texture_image

                            principled_shader_node = nodes.new(type='ShaderNodeBsdfPrincipled')
                            principled_shader_node.location = (200, 0)

                            material_output_node = nodes.new(type='ShaderNodeOutputMaterial')
                            material_output_node.location = (600, 0)

                            links.new(uv_map_node.outputs['UV'], mapping_node.inputs['Vector'])
                            links.new(mapping_node.outputs['Vector'], image_texture_node.inputs['Vector'])
                            links.new(image_texture_node.outputs['Color'], principled_shader_node.inputs['Base Color'])
                            links.new(principled_shader_node.outputs['BSDF'], material_output_node.inputs['Surface'])

                            # print("new material=",new_material.name)
                            slot.material = new_material

    def tag_objects(self, obj, base_name):
        obj['base_name'] = base_name
        
        for child in obj.children:
            self.tag_objects(child, base_name)
 
    def tag_base_mesh_objects(self, objects):
        base_objects = []
        for obj in objects:       
            if obj.get("IS_BP_WALL") or "floor" in obj.name.lower():
                if "floor" in obj.name.lower():
                    obj.hide_viewport = False

                base_mesh = None
                if obj.type == 'MESH':
                    base_mesh = obj
                else:
                    for child in obj.children:
                        if child.type == 'MESH':
                            base_mesh = child
                            break

                if base_mesh:
                    base_mesh["IS_BASE_OBJECT"] = True
                    base_objects.append(base_mesh)
                    self.tag_objects(obj, base_mesh.name)

    def create_temp_material(self, material_name):
        material = bpy.data.materials.new(name=material_name)

        material.use_nodes = True
        nodes = material.node_tree.nodes

        for node in nodes:
            nodes.remove(node)

        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.inputs['Base Color'].default_value = (1, 1, 1, 1)  # RGBA
        output = nodes.new(type='ShaderNodeOutputMaterial')
        material.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
        print("created new material=",material.name)

        return material

    def get_objects_for_export(self, objects, export_scene):
        for obj in objects:
            object_types = [obj.type == 'MESH', obj.type == 'CURVE', obj.type == 'LIGHT']
           
            if obj.sn_roombuilder.is_ceiling:
                print(" Skipping Ceiling:", obj.name)
                continue
                
            if any(object_types):
                # Skip boolean modifier objects
                if obj.get("use_as_bool_obj"):
                    print(" Skipping", obj.name)
                    continue

                if obj.type == 'CURVE':
                    bpy.context.view_layer.objects.active = obj
                    obj.select_set(True)
                    bpy.ops.object.convert(target='MESH')
                    obj.select_set(False)
          
                # Skip single vertex meshes
                if obj.type == 'MESH':
                    num_vertices = len(obj.data.vertices)

                    if num_vertices == 1 and "Window" not in obj.name and "Door" not in obj.name:
                        print("  Single vet mesh, skipping", obj.name)
                        continue

                    if obj.get("IS_CAGE"):   # obj is likely an obstacle, need to verify material exists
                        obj.hide_select = False

                        if len(obj.material_slots) > 0:
                            # if obj material is none, assign winter white, or create new white mat if unavailable
                            if obj.material_slots[0].material is None:
                                material = bpy.data.materials.get('Winter White')
                                if material is None:
                                    material = bpy.data.materials.get('White Export')
                                if material is None:
                                    material = self.create_temp_material('White Export')
                                obj.material_slots[0].material = material

                    if obj.sn_roombuilder.is_floor:
                         if len(obj.material_slots) > 0:
                            material = obj.material_slots[0].material
                            nodes = material.node_tree.nodes
                            node = nodes.get("Glossy BSDF")
                            if node:
                                bpy.data.materials[material.name].node_tree.nodes.remove(node)

                # Duplicate the object and add it to the export scene
                dup_obj = obj.copy()
                dup_obj.data = obj.data.copy()
                dup_obj.animation_data_clear()
                dup_obj['base_name'] = obj.get('base_name')
                if obj.get('IS_BASE_OBJECT'):
                        dup_obj['IS_BASE_OBJECT'] = True
                if obj.parent and obj.parent.get("IS_BP_WALL"):
                    dup_obj['IS_BP_WALL'] = True
                export_scene.collection.objects.link(dup_obj)

    def execute(self, context):
        print("Preparing Room For 3D Export")
        wall_count = 0
        if "3D Export" in bpy.data.scenes:
            bpy.context.window.scene = bpy.data.scenes.get("3D Export")
            bpy.ops.scene.delete()
            bpy.context.window.scene = sn_utils.get_main_scene()

        export_scene = sn_utils.get_3d_export_scene()
        bpy.ops.object.select_all(action='DESELECT')

        self.tag_base_mesh_objects(bpy.context.scene.objects)
        self.get_objects_for_export(context.visible_objects, export_scene)

        bpy.context.window.scene = export_scene
        self.apply_all_modifiers(export_scene.objects)
        self.create_sipmle_materials(export_scene.objects)

        base_objects = [obj for obj in export_scene.objects if obj.get('IS_BASE_OBJECT')]
        for base_object in base_objects:
            bpy.ops.object.select_all(action='DESELECT')
            
            if base_object.get("IS_BP_WALL"):
                wall_count += 1
    
            for obj in export_scene.objects:
                if obj.get('base_name') == base_object.get('base_name') and not obj.get('IS_BASE_OBJECT'):
                    if obj.type == 'MESH':
                        obj.select_set(True)
                        obj.lock_location[0] = False
                        obj.lock_location[1] = False
                        obj.lock_location[2] = False

            base_object.select_set(True)
            bpy.context.view_layer.objects.active = base_object
            obj.lock_location[0] = False
            obj.lock_location[1] = False
            obj.lock_location[2] = False
            obj['WALL_COUNT'] = len(base_objects) - 1
            bpy.ops.object.join()
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        
        obj_room_wall = None
        obj_room_light = None
        obj_room_floor = None

        for obj in export_scene.objects:
            rotation_matrix = obj.matrix_world.to_euler()
            if "Floor" in obj.name:
                obj_room_floor = obj
            elif obj.type == 'LIGHT':
                obj_room_light = obj
            elif rotation_matrix.z == 0:
                obj_room_wall = obj

        for i, obj in enumerate(bpy.data.objects):
            new_name = obj.name + f"_{i}"
            obj.name = new_name
            if obj.type == 'MESH':
                obj.data.name = new_name + "_mesh"

        # print("obj_room_wall=",obj_room_wall.name)
        # print("obj_room_light=",obj_room_light.name)
        # print("obj_room_floor=",obj_room_floor.name)

        if obj_room_floor and obj_room_light:
            matrix_world = obj_room_floor.matrix_world
            bound_box = [matrix_world @ mathutils.Vector(corner) for corner in obj_room_floor.bound_box]
            center_x = (bound_box[0][0] + bound_box[6][0]) / 2
            center_y = (bound_box[0][1] + bound_box[6][1]) / 2
            center_z = (bound_box[0][2] + bound_box[6][2]) / 2
            if wall_count > 3:  #top view camera
                obj_room_light.location.x = center_x
                obj_room_light.location.y = center_y
                obj_room_light.location.z = obj_room_wall.location.z + center_z + 4.0
            else:   #front view camera
                obj_room_light.location.x = center_x
                obj_room_light.location.y = center_y - 2.0
                obj_room_light.location.z = obj_room_wall.location.z + (center_z * 2) + 2.0
                obj_room_light.data.energy = 200

            obj_room_floor.name = "Room_Floor__width=" + str(round(center_x * 2,2)) + "__depth=" + str(round(center_y * 2,2)) + "__height=" + str(round(center_z * 2,2))
                
        print("  Deleting extra scenes")
        for scene in bpy.data.scenes:
            if scene.name != "3D Export":
                bpy.data.scenes.remove(scene)

        bpy.ops.wm.save_mainfile()

        print("   Deleting orphaned objects")
        for obj in bpy.data.objects:
            if obj.users == 0 or (len(obj.users_scene) == 0):
                bpy.data.objects.remove(obj, do_unlink=True)

        bpy.ops.wm.save_mainfile()

        self.save_export_to_glb()
    
        print("3D Export Scene Ready")

        return {'FINISHED'}


class SNAP_OT_Proposal_Create_Room_Custom_Thumbnail(Operator):
    bl_idname = "project_manager.create_room_custom_thumbnail"
    bl_description = "Create Room Custom Thumbnail"
    bl_label = "Create Room Custom Thumbnail"

    active_room: StringProperty(name="Active Room", description="Active Room", default="")

    @classmethod
    def poll(cls, context):
        return True
    
    def is_viewport_rendered(self):
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        return space.shading.type == 'RENDERED'
        return False
    
    def execute(self, context):
        print("Create Room Custom Thumbnail")
        project = context.window_manager.sn_project.get_project()
        proposal_dir = os.path.join(project.dir_path, "Proposal")
        
        bpy.context.scene.render.image_settings.file_format = 'JPEG'
        bpy.context.scene.render.image_settings.quality = 90
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.render.resolution_x = 1279
        bpy.context.scene.render.resolution_y = 1048
        temp_path =  bpy.context.scene.render.filepath
        bpy.context.scene.render.filepath = os.path.join(proposal_dir, self.active_room.lower().replace(" ","_") + "_thumbnail_custom")
        # bpy.ops.render.opengl(write_still=True)
        if self.is_viewport_rendered():
            hidden_objs = []
            collections = bpy.data.collections
            wall_objects = sn_utils.get_wall_bps(context)
            # render-hide collections that are hidden in viewport but not hidden in render ivew
            for wall in wall_objects:
                wall_name = wall.snap.name_object
                if wall_name in collections:
                    wall_coll = collections[wall_name]
                    if wall_coll.hide_viewport == True and wall_coll.hide_render == False:
                        wall_coll.hide_render = True
                        hidden_objs.append(wall_coll)

            # render-hide objects that are hidden in viewport but not hidden in render ivew
            for obj in bpy.context.scene.objects:
                if obj.hide_viewport == True and obj.hide_render == False:
                    obj.hide_render = True
                    hidden_objs.append(obj)

            # render scene...
            orig_samples = bpy.context.scene.cycles.samples
            orig_denoise = bpy.context.scene.cycles.use_denoising
            bpy.context.scene.cycles.samples = 64
            bpy.context.scene.cycles.use_denoising = True  
            bpy.ops.render.render(write_still=True)
                       
            # restore original render visibility
            bpy.context.scene.cycles.samples = orig_samples
            bpy.context.scene.cycles.use_denoising = orig_denoise
            for coll in hidden_objs:
                coll.hide_render = False
        else:
            bpy.ops.render.opengl(write_still=True)
    
        from PIL import Image
        image = Image.open(bpy.context.scene.render.filepath + ".jpg")  #
        image.show()

        bpy.context.scene.render.filepath = temp_path
        room = project.rooms[self.active_room]
        room.prop_thumbnail_custom = "True"


        # Get the current datetime in UTC
        utc_datetime = datetime.utcnow()
        # Convert the UTC datetime to the local timezone
        local_datetime = utc_datetime.replace(tzinfo=timezone.utc).astimezone(tz=None)

        now = datetime.now()
        timezone_abbr = local_datetime.strftime('%Z')

        print("UTC Time:", utc_datetime.strftime("%Y-%m-%d %H:%M:%S"))
        print("Converted Time:", local_datetime.strftime("%Y-%m-%d %H:%M:%S"))
        print("Local Time: ", now.strftime("%Y-%m-%d %H:%M:%S %Z"))
        print("Local Timezone:", timezone_abbr)

        room.prop_thumbnail_custom_utc = str(utc_datetime)

        thumb_camera = bpy.data.objects.get("thumbnail_camera")
        if thumb_camera is not None:
             bpy.data.objects.remove(thumb_camera, do_unlink=True)

        return{'FINISHED'}
    

class SNAP_OT_Proposal_Start_Room_Custom_Thumbnail(Operator):
    bl_idname = "project_manager.start_room_custom_thumbnail"
    bl_description = "Start Room Custom Thumbnail"
    bl_label = "Start Room Custom Thumbnail"

    active_room: StringProperty(name="Active Room", description="Active Room", default="")

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        print("Create Room Custom Thumbnail")
        project = context.window_manager.sn_project.get_project()
        proposal_dir = os.path.join(project.dir_path, "Proposal")
        
        view = context.space_data
        bpy.ops.sn_object.add_camera()
        thumb_camera = bpy.context.object
        thumb_camera.name = "thumbnail_camera"
        view.lock_camera = True

        room = project.rooms[self.active_room]
        room.prop_thumbnail_custom = "Started"

        return{'FINISHED'}
    

class SNAP_OT_Proposal_Create_Room_Thumbnail(Operator):
    bl_idname = "project_manager.create_room_thumbnail"
    bl_description = "Create Room Thumbnail"
    bl_label = "Create Room Thumbnail"

    room_path: StringProperty(name="Room Path", description="Room Path", default="")

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        print("Create Room Thumbnail")
        needs_top_view = False
        focus_obj = None
        wall_count = 0

        # Append 3d export files to thumbnail scene...
        with bpy.data.libraries.load(self.room_path) as (data_from, data_to):
            data_to.objects = [name for name in data_from.objects]
            # print('These are the objs: ', data_to.objects)

        # Objects have to be linked to show up in a scene
        for obj in data_to.objects:
            if obj.type == 'MESH' and obj.get("IS_BP_WALL"):
                wall_count += 1
                focus_obj = obj
            bpy.context.scene.collection.objects.link(obj)   

        if wall_count > 3:
            needs_top_view = True

        if needs_top_view and focus_obj:
            camera_obj = bpy.data.objects['Camera Top View']
            bpy.context.scene.camera = camera_obj
            bpy.context.scene.camera.location.z += 10
        else:
            camera_obj = bpy.data.objects['Camera Front View']
            bpy.context.scene.camera = camera_obj
            bpy.context.scene.camera.location.z += .05
        bpy.context.scene.camera.data.lens = 40

        render = bpy.context.scene.render
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.render.resolution_x = 1279
        bpy.context.scene.render.resolution_y = 1048
        bpy.context.scene.render.image_settings.file_format = 'JPEG'
        bpy.context.scene.render.image_settings.quality = 90
        render.engine = 'BLENDER_EEVEE'
        bpy.context.scene.eevee.use_gtao = True
        bpy.context.scene.eevee.use_ssr = True
        render.film_transparent = False
        render.use_file_extension = True
        
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.view3d.camera_to_view_selected()

        temp_path =  bpy.context.scene.render.filepath
        bpy.context.scene.render.filepath = self.room_path.replace("-3d_export.blend","_thumbnail")
        bpy.ops.render.render(write_still=True)
                
        bpy.context.scene.render.filepath = temp_path
        # bpy.ops.wm.save_as_mainfile(filepath=self.room_path.replace(".blend","_temp.blend"))
        return{'FINISHED'}


class SNAP_OT_Proposal_View_Room_Thumbnail(Operator):
    bl_idname = "project_manager.view_room_thumbnail"
    bl_description = "Click to view room thumbnail"
    bl_label = "View Room Thumbnail"

    active_room: StringProperty(name="Active Room", description="Active Room", default="")


    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        print("View Room Thumbnail")
        thumb_path = ""
        project = context.window_manager.sn_project.get_project()
        proposal_dir = os.path.join(project.dir_path, "Proposal")
        room = project.rooms[self.active_room]

        if room.prop_thumbnail_custom == "True":
            thumb_path = os.path.join(proposal_dir, self.active_room.lower().replace(" ","_") + "_thumbnail_custom.jpg")
        elif room.prop_thumbnail == "True":
            thumb_path = os.path.join(proposal_dir, self.active_room.lower().replace(" ","_") + "_thumbnail.jpg")

        if thumb_path != "":       
            from PIL import Image
            image = Image.open(thumb_path)  #
            image.show()

        return{'FINISHED'}


class SNAP_OT_Proposal_Add_Room_To_Documents(Operator):
    """Add Room to Project Proposal"""
    bl_idname = "project_manager.add_room_to_proposal"
    bl_label = "Add Room to Project Proposal"
    bl_options = {'UNDO'}

    room_label: StringProperty(name="Room Label", description="Room Label", default="")
    room_estimate: StringProperty(name="Room Estimate", description="Room Estimate", default="")
    is_cabinet_bp: BoolProperty(name="Is Cabinet BP", default=False)
    
    ext_color: StringProperty(name="Ext Color", description="Ext Color", default="")
    int_color: StringProperty(name="Int Color", description="Int Color", default="")
    trim_color: StringProperty(name="Trim Color", description="Trim Color", default="")
    hardware: StringProperty(name="Hardware", description="Hardware", default="")
    rods: StringProperty(name="Rods", description="Rods", default="")
    door_drawer_style: StringProperty(name="Door/Drawer Style", description="Door/Drawer Style", default="")
    box_style: StringProperty(name="Box Style", description="Box Style", default="")
    hamper: StringProperty(name="Hamper", description="Hamper", default="")
    accessories: StringProperty(name="Accessories", description="Accessories", default="")
    countertop: StringProperty(name="Countertop", description="Countertop Selection", default="")
    backing: StringProperty(name="Backing", description="Backing", default="")
    glass: StringProperty(name="Glass", description="Glass", default="")
    notes: StringProperty(name="Notes", description="Notes", default="")
    

    def invoke(self, context, event):
        return self.execute(context)
    
    def get_box_style_description(self, style):
        if style == 0: 
            return "White Melamine"
        elif style == 1:
            return "3/4\" Melamine"
        elif style == 2:
            return "Dovetail"
        else:
            return ""
        
    def get_name_from_part_nbr(self, part_nbr):
        display_name = ""
        sql = "SELECT DisplayName\
                FROM {CCItems}\
                WHERE VendorItemNum = '{part_nbr}';\
            ".format(CCItems="CCItems_" + bpy.context.preferences.addons['snap'].preferences.franchise_location, part_nbr=part_nbr)
        
        rows = sn_db.query_db(sql)

        for row in rows:
            display_name = row[0]
            if part_nbr in display_name:
                display_name = display_name.replace(part_nbr, "")
                            
        # if display_name == "":
        #     return part_nbr
        # else:
        return display_name.title()

    def simulate_word_wrap(self, text, max_chars_per_line=58, target_lines=4):
        lines = []
        current_line = ""

        if text.strip() == "":
            text="None"

        words = text.split()
        for word in words:
            if len(current_line) + len(word) + 1 <= max_chars_per_line:
                # Add the word to the current line
                if current_line:
                    current_line += " "
                current_line += word
            else:
                # Start a new line
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        final_text =  "<br>&nbsp;&nbsp;".join(lines)

        br_count = final_text.count("<br>")
        if br_count < target_lines:
            br_needed = target_lines - br_count
            final_text += "<br>" * br_needed

        return final_text

    def get_door_drawer_type(self, door_drawer_style):
        
        if "Slab" in door_drawer_style:
            return 'slab'
        elif "Traviso" in door_drawer_style:
            return 'traviso'
        elif "Moderno" in door_drawer_style:
            return 'moderno'
        else:
            return 'wood'

    def get_hamper_style(self, hampers):
        hamper_style_list = []

        for hamper_bp in hampers:
            vendor_id = ""
            is_canvas = 'canvas' in hamper_bp.name.lower()
            is_basket = 'basket' in hamper_bp.name.lower()
            hamper_types = {0 : "Wire", 1: "Hafele Nylon"}
     
            if is_canvas or is_basket:
                hamper = sn_types.Assembly(hamper_bp)
                hamper_insert = sn_types.Assembly(hamper_bp.parent)

                hide_ppt = hamper.get_prompt("Hide")
                hamper_color_ppt = hamper_insert.get_prompt("Wire Basket Color")

                hamper_type_ppt = hamper_insert.get_prompt("Hamper Type")
                if hamper_type_ppt:
                    hamper_type = hamper_type_ppt.get_value()
                    hamper_type = hamper_types.get(hamper_type)

                if hide_ppt and hide_ppt.get_value() != True:
                    if hamper_type == "Wire" and is_basket:
                        if hamper_color_ppt:
                            basket_color = hamper_color_ppt.get_value()
                            color_id = 2 if basket_color == 0 else 7
                            basket_width = sn_unit.meter_to_inch(hamper.obj_x.location.x)
                            basket_depth = sn_unit.meter_to_inch(hamper.obj_y.location.y)
                            width_id = 1 if basket_width == 18.0 else 2
                            depth_id = 3 if basket_depth == 14.0 else 4
                            vendor_id = '547.42.{}{}{}'.format(color_id, depth_id, width_id)
                    elif hamper_type == "Hafele Nylon" and is_canvas:
                        basket_width = round(sn_unit.meter_to_inch(hamper_insert.obj_x.location.x), 2)
                        if 24.0 > basket_width >= 18.0:
                            # HAMPER TILT OUT 18" 20H 
                            vendor_id = '547.43.311'
                        elif 30.0 > basket_width >= 18.0:
                            # HAMPER TILT OUT 24" 20H DOUBLE BAG
                            vendor_id = '547.43.313'
                        elif basket_width >= 30.0:
                            # HAMPER TILT OUT 30" 20H DOUBLE BAG
                            vendor_id = '547.43.515'

                    # print("hamper item_nbr=",vendor_id)
                    if vendor_id:
                        hamper_style = self.get_name_from_part_nbr(vendor_id).replace("Hamper ","")
  
                        if hamper_style and hamper_style not in hamper_style_list:
                            hamper_style_list.append(hamper_style)
                        
        if len(hamper_style_list) > 0:
            return " / ".join(hamper_style_list)
        else:
            return "None"

    def get_rod_style(self, rods):
        rod_style_list = []
   
        for rod in rods:
            assembly = sn_types.Assembly(rod)
            hide_ppt = assembly.get_prompt("Hide")
            if hide_ppt and hide_ppt.get_value() != True:
                # Format the rod part name as may look like "Hang Rod Round" or "Elite Matte Gold Round 801.42.040"
                rod_style = rod.snap.name_object
                rod_style = re.sub(r'\s+\d+[\d\.]*$', '', rod_style)  # regex will strip any sequence of digits and dots at the end of the string

                if rod_style not in rod_style_list:
                    rod_style_list.append(rod_style)

        if len(rod_style_list) > 0:
            return " / ".join(rod_style_list)
        else:
            return "None"

    def get_backing_style(self, back_panels):
        hidden = True

        for back_panel in back_panels:
            assembly = sn_types.Assembly(back_panel)
            hide_ppt = assembly.get_prompt("Hide")
            if hide_ppt and hidden == True:
                hidden = hide_ppt.get_value()
               
        if len(back_panels) == 0 or hidden:
            return "No"
        else:
            return "Yes"

    def get_pull_style(self, pulls):
        pull_style_list = []
 
        for obj in pulls:
            if obj.parent:
                pull_style = ""
                part_nbr = obj.parent.snap.name_object
                # print("pull part_nbr=",part_nbr)
                if part_nbr:
                    if part_nbr == "Pull":
                        pull_style = "Standard Pulls"
                    elif part_nbr == "Specialty Handle": 
                        pull_style = "Specialty Pulls"
                    elif part_nbr == "Customer Provided Handle":
                        pull_style = "Customer Provided"
                    else:
                        pull_style = self.get_name_from_part_nbr(part_nbr).replace("Mm","mm")
                                       
            if pull_style and pull_style not in pull_style_list:
                pull_style_list.append(pull_style) 
            
        if len(pull_style_list) > 0:
            return " / ".join(pull_style_list)
        else:
            return "None"
                 
    def get_glass_color(self, context, door_drawer_fronts):
        glass_color_list = []

        # get current glass color from scene properties...
        scene_props = context.scene.closet_materials    
        default_glass_index = scene_props.glass_color_index
        default_glass_color = scene_props.glass_colors[default_glass_index].name
  
        # look for glass objects in the scene and check for custom glass...
        if self.is_cabinet_bp:
            return "None"
        else:
            for obj in door_drawer_fronts:
                if "glass" in obj.name.lower():
                    assy = sn_types.Assembly(obj)
                    color_ppt = assy.get_prompt("Glass Color")
                    color = ""
                    if color_ppt:
                        color = color_ppt.get_value()
                    else:
                        color = default_glass_color

                    if color and color not in glass_color_list:
                        glass_color_list.append(color)
                
        if len(glass_color_list) > 0:
            return " / ".join(glass_color_list)
        else:
            return "None"

    def get_door_drawer_style(self, door_drawer_fronts):
        door_drawer_style_list = []
        has_slab_style = False
        style = ""

        if self.is_cabinet_bp:
            return "None"
        else:
            for obj in door_drawer_fronts:
                print("door_drawer obj=",obj.name)
                assy = sn_types.Assembly(obj)
                style_ppt = assy.get_prompt("Door Style")
                if style_ppt:
                    style_ppt_value = style_ppt.get_value()
                    # print("glass prompted obj=",assy.obj_bp.snap.name_object)
                    style = style_ppt_value
                    if style.endswith("Door Glass"):
                        style = style.replace("Door Glass"," (Glass)")
                    elif style.endswith(" Door and Drawer"):
                        style = style.replace(" Door and Drawer","")
                    elif style.endswith(" Door"):
                        style = style.replace(" Door","")
                    elif style.endswith(" Drawer"):
                        style = style.replace(" Drawer","")
                    elif "Angled" in style:
                        style = ""
                else:  # if no door style prompt, may be an applied pannel which is missing prompts like this
                    part_name = assy.obj_bp.snap.name_object
                    # print("glass part_name=",part_name)
                    if part_name == "Left Door" or part_name == "Right Door" or part_name == "Drawer Front":
                        # style = "Slab"
                        has_slab_style = True
                    elif part_name.endswith(" Door Glass"):
                        style = part_name.replace("Door Glass"," (Glass)")
                    elif part_name.endswith(" Door"):
                        style = part_name.replace(" Door","")
                    else:
                        has_slab_style = True

                if style and style not in door_drawer_style_list:
                    door_drawer_style_list.append(style)

        if has_slab_style and "Slab" not in door_drawer_style_list:
            door_drawer_style_list.append("Slab")
               
        if len(door_drawer_style_list) > 0:
            return " / ".join(door_drawer_style_list)
        else:
            return "None"
     
    def get_room_box_style(self, drawer_inserts):
        box_style_list = []

        if self.is_cabinet_bp:
            return "None"
        else:
            # find drawer box style types
            for insert in drawer_inserts:
                drawer_assembly = sn_types.Assembly(insert)
                drawer_box_prompt = drawer_assembly.get_prompt("Box Type")
                if drawer_box_prompt:
                    style = self.get_box_style_description(drawer_box_prompt.get_value())
                    if style not in box_style_list:
                        box_style_list.append(style)

        if len(box_style_list) > 0:
            return " / ".join(box_style_list)
        else:
            return "None"
        
    def get_room_accessories(self, accessories):
        accessory_list = []

        for obj in accessories:
            accessory = ""
            assembly = sn_types.Assembly(obj)
            hide_ppt = assembly.get_prompt("Hide")
            if hide_ppt and hide_ppt.get_value() != True:
                if obj.get("IS_BP_BELT_RACK"):
                    accessory = 'Belt Rack'
                elif obj.get("IS_BP_TIE_RACK"):
                    accessory = 'Tie Rack'
                elif obj.get("IS_BP_VALET_ROD"):
                    accessory = 'Valet'
                elif obj.get("IS_BP_GARAGE_LEG"):
                    part_label = obj.snap.name_object
                    if "metal" in part_label.lower():
                        accessory = 'Garage Legs (Metal)'
                    elif "plastic" in part_label.lower():
                        accessory = 'Garage Legs (Plastic)'
                    else:
                        accessory = 'Garage Legs'
                elif obj.get("IS_BP_ACCESSORY"):
                    accessory = 'Hooks'  

                if accessory and accessory not in accessory_list:
                    accessory_list.append(accessory)

        if len(accessory_list) == 0:
            return "None"
        else:
            return " / ".join(accessory_list)
    
    def get_room_countertop(self, context, countertops):
        materials = []

        for ctop_bp in countertops:
            ct_mat_props = context.scene.closet_materials.countertops
            material_name = ""
            material_dict = {
                0: 'Melamine',    # 0: 'Melamine'
                1: 'Custom',    # 1: 'Custom'
                2: 'Granite',   # 2: 'Granite'
                3: 'HPL',    # 3: 'HPL'
                4: 'Quartz',    # 4: 'Quartz'
                5: 'Quartz',   # 5: 'Standard Quartz'
                6: 'Wood'       # 6: 'Wood'
            }
            
            ctop_assembly = sn_types.Assembly(ctop_bp)
            ctop_mat_pmpt = None
            ctop_mat_option = None
            material_str = None

            ctop_mat_pmpt = ctop_assembly.get_prompt("Countertop Type")
            if not ctop_mat_pmpt and ctop_bp.parent:
                ctop_parent_assembly = sn_types.Assembly(ctop_bp.parent)
                ctop_mat_pmpt = ctop_parent_assembly.get_prompt("Countertop Type")
            if ctop_mat_pmpt:
                ctop_mat_option = ctop_mat_pmpt.get_value()
                material_str = material_dict.get(ctop_mat_option)


            context_material = material_name
            material = ""
            if material_str is not None:
                material += material_str
            if not None:
                material += context_material
            material += " "
            for spec_group in context.scene.snap.spec_groups:
                if material_str == "Melamine":
                    material = spec_group.materials["Countertop_Surface"].item_name + ' ' + material
                if material_str == "Granite":
                    material = spec_group.materials["Countertop_Granite_Surface"].item_name + ' ' + material
                if material_str == "HPL":
                    material = spec_group.materials["Countertop_HPL_Surface"].item_name + ' ' + material
                if material_str == "Quartz":
                    material = spec_group.materials["Countertop_Quartz_Surface"].item_name + ' ' + material
                # if material_str == "Standard Quartz":
                #     material = spec_group.materials["Countertop_Quartz_Surface"].item_name + ' ' + material
                if material_str == "Wood":
                    for child in ctop_bp.children:
                        if child.get("COUNTERTOP_WOOD"):
                            if child.sn_closets.use_unique_material:
                                material = child.sn_closets.wood_countertop_types
                            else:
                                mfg = ct_mat_props.get_type().get_mfg()
                                material = mfg.name

            print("ctop material=",material)
            if material not in materials:
                materials.append(material)
                
        print("materials=",materials)
        if len(materials) > 0:        
            ctop_label = " / ".join(materials) 
            if len(ctop_label) > 50: 
                ctop_label = ctop_label.replace("Melamine", "Mel")
            if len(ctop_label) > 50:
                ctop_label = ctop_label[:50] + "..."
            return ctop_label
        else:
            return "None"

    def get_ext_color(self, context, door_drawer_fronts):
        ext_colors = []
        scene_props = context.scene.closet_materials
        
        if scene_props.use_kb_color_scheme:
            ext_colors = scene_props.get_kb_material_list()
        else:
            for obj in door_drawer_fronts:
                assy = sn_types.Assembly(obj)
                style_ppt = assy.get_prompt("Door Style")
                if style_ppt:
                    style_ppt_value = style_ppt.get_value()
                else:
                    style_ppt_value = "Slab"
                style = self.get_door_drawer_type(style_ppt_value)
                color = None

                if style == 'traviso':
                    color = scene_props.get_five_piece_melamine_door_color().name
                elif style == 'moderno':
                    color = scene_props.get_moderno_door_color().name
                elif style == 'slab':
                    mat_types = scene_props.materials.mat_types
                    type_index = scene_props.door_drawer_mat_type_index
                    material_type = mat_types[type_index]

                    if material_type.name == "Upgrade Options":
                        if scene_props.upgrade_options.get_type().name == "Paint":
                            color = scene_props.paint_colors[scene_props.paint_color_index].name
                        else:
                            color = scene_props.stain_colors[scene_props.stain_color_index].name
                    # elif material_type.name == "Garage Material":
                    #     color = scene_props.materials.get_mat_color().two_sided_display_name
                    else:
                        colors = material_type.colors
                        if scene_props.use_custom_color_scheme:
                            color_index = scene_props.get_dd_mat_color_index(material_type.name)
                        else:
                            color_index = scene_props.get_mat_color_index(material_type.name)
                        color = colors[color_index].name

                elif style == "wood" and scene_props.use_custom_color_scheme:
                    if scene_props.upgrade_options.get_type().name == "Paint":
                        color = scene_props.paint_colors[scene_props.paint_color_index].name
                    else:
                        color = scene_props.stain_colors[scene_props.stain_color_index].name
                else: 
                    color = scene_props.materials.get_mat_color().name
                print("color=",color)
                if color and color not in ext_colors:
                    ext_colors.append(color)

        if len(ext_colors) > 0:
            return " / ".join(ext_colors)
        else:
            return scene_props.materials.get_mat_color().name

    def get_int_color(self, context):
        scene_props = context.scene.closet_materials
        mat_types = scene_props.materials.mat_types
        type_index = scene_props.mat_type_index
        material_type = mat_types[type_index]

        if material_type.name == "Upgrade Options":
            if scene_props.upgrade_options.get_type().name == "Paint":
                colors = scene_props.paint_colors
            else:
                colors = scene_props.stain_colors
        else:
            colors = material_type.colors

        if material_type.name != "Garage Material":
            color_index = scene_props.get_mat_color_index(material_type.name)
            color = colors[color_index].name
        else:
            color = scene_props.materials.get_mat_color().two_sided_display_name
            if color and color.endswith(" White"):
                color = "Winter White"

        print("int_color=",color)
        if color:
            return color
        else:
            return scene_props.materials.get_mat_color().name

    def get_trim_color(self, context):
        scene_props = context.scene.closet_materials
        edge_types = scene_props.edges.edge_types
        type_index = scene_props.edge_type_index
        edge_type = edge_types[type_index]
        colors = edge_type.colors
        color_index = scene_props.edge_color_index
        color = colors[color_index].name

        print("trim_color=",color)
        if color:
            return color
        else:
            return scene_props.materials.get_mat_color().name

    def load_room_custom_selections(self, room):

        self.room_label = room.prop_room_label
        self.room_estimate = room.prop_room_estimate_custom

        self.ext_color = room.prop_room_ext_color_custom
        self.int_color = room.prop_room_int_color_custom
        self.trim_color = room.prop_room_trim_color_custom
        self.hardware = room.prop_room_hardware_custom
        self.rods = room.prop_room_rods_custom
        self.door_drawer_style = room.prop_room_door_drawer_custom
        self.hamper = room.prop_room_hamper_custom
        self.box_style = room.prop_room_boxes_custom
        self.accessories = room.prop_room_accessories_custom
        self.countertop = room.prop_room_countertop_custom
        self.backing = room.prop_room_backing_custom
        self.glass = room.prop_room_glass_custom
        self.notes = room.prop_room_notes
        
    def get_room_selection_data(self, context):
        drawer_inserts = []
        door_drawer_fronts = []
        accessories = []
        countertops = []
        pulls = []
        rods = []
        hampers = []
        back_panels = []

        project = context.window_manager.sn_project.get_project()
        room = project.rooms[project.room_index]
 
        self.load_room_custom_selections(room)

        main_scene = sn_utils.get_main_scene()
        for obj in main_scene.objects:
            if obj.get("IS_BP_CABNET") and self.is_cabinet_bp == False: 
                self.is_cabinet_bp = True

            if obj.get("IS_BP_DRAWER_STACK"):
                drawer_inserts.append(obj)
            elif obj.get("IS_DOOR") or obj.get("IS_BP_DRAWER_FRONT") or obj.get("IS_BP_HAMPER_FRONT") or obj.get("IS_BP_APPLIED_PANEL"):
                door_drawer_fronts.append(obj)
            elif obj.get("IS_BP_BELT_RACK") or obj.get("IS_BP_TIE_RACK") or obj.get("IS_BP_VALET_ROD") or obj.get("IS_BP_ACCESSORY") or obj.get("IS_BP_GARAGE_LEG"):
                accessories.append(obj)
            elif obj.get("IS_BP_COUNTERTOP"):
                countertops.append(obj)
            elif obj.get("IS_BACK"):
                back_panels.append(obj)
            elif obj.get("IS_BP_HAMPER"):
                hampers.append(obj)

        
            if obj.type == 'MESH':
                if obj.sn_closets.is_handle or obj.snap.is_cabinet_pull or obj.get("IS_SPECIALTY_PULL"):
                    pulls.append(obj)

                assembly_bp = sn_utils.get_assembly_bp(obj)
                if assembly_bp and assembly_bp.sn_closets and assembly_bp.sn_closets.is_hanging_rod:
                    rods.append(assembly_bp)

        # ////// Room Label
        if not self.room_label:
            self.room_label = room.name
        # ////// Room Estimate
        if not self.room_estimate:
            self.room_estimate = "&nbsp;"
        else:
            self.room_estimate = "$" + self.room_estimate.replace("$","") + "**"

        # ////// Exterior Color
        if not self.ext_color:
            self.ext_color = self.get_ext_color(context, door_drawer_fronts)
        # ////// Interior Color
        if not self.int_color:
            self.int_color = self.get_int_color(context)
        # ////// Trim Color
        if not self.trim_color:
            self.trim_color = self.get_trim_color(context)
        # ////// Hardware
        if not self.hardware:
            self.hardware = self.get_pull_style(pulls)
        # ////// Rods
        if not self.rods:
            self.rods = self.get_rod_style(rods)
        # ////// Door/Drawer Faces
        if not self.door_drawer_style:
            self.door_drawer_style = self.get_door_drawer_style(door_drawer_fronts)
        # ////// Hamper
        if not self.hamper:
            self.hamper = self.get_hamper_style(hampers)
        # ////// Box Style
        if not self.box_style:
            self.box_style = self.get_room_box_style(drawer_inserts)
        # ////// Accessories
        if not self.accessories:
            self.accessories = self.get_room_accessories(accessories)
        # ////// Countertop
        if not self.countertop:
            self.countertop = self.get_room_countertop(context, countertops)
        # ////// Backing
        if not self.backing:
            self.backing = self.get_backing_style(back_panels)
        # ////// Glass
        if not self.glass:
            self.glass = self.get_glass_color(context, door_drawer_fronts)
        # ////// Notes
        self.notes = self.simulate_word_wrap(self.notes)

    def add_room_to_proposal_document(self, context):
        project = context.window_manager.sn_project.get_project()
        room = project.rooms[project.room_index]

        proposal_path = os.path.join(project.dir_path, "Proposal", project.name + ".html")
        proposal_path_mobile = os.path.join(project.dir_path, "Proposal", project.name + "_mobile.html")
        template_path = os.path.join(os.path.dirname(__file__), 'proposals', 'prop_room.html')
        if room.prop_3d_exported == "True":
            room_thumb_html_path = os.path.join(os.path.dirname(__file__), 'proposals', 'prop_room_thumb_link.html')
        else:
            room_thumb_html_path = os.path.join(os.path.dirname(__file__), 'proposals', 'prop_room_thumb_nolink.html')
        
        # ////// Read html templates
        with open(proposal_path, 'r', encoding='utf-8') as file:
            html_content = file.read()

        with open(proposal_path_mobile, 'r', encoding='utf-8') as file:
            html_content_mobile = file.read()

        with open(room_thumb_html_path, 'r', encoding='utf-8') as file:
            html_room_thumb_segment = file.read()

        with open(template_path, 'r', encoding='utf-8') as file:
            html_room_segment = file.read()

        # ////// Room Label, estimate, 3d link, thumbnail
        html_room_segment = html_room_segment.replace("<room_label>", self.room_label)
        html_room_segment = html_room_segment.replace("<room_estimate>", self.room_estimate) 
        html_room_segment = html_room_segment.replace("<room_thumbnail_segment>", html_room_thumb_segment)
        
        # ///// Room Viewer/Classy Portal link
        room_viewer_doc = room.name.lower().replace(" ","_") + "_viewer.html"
        html_room_segment = html_room_segment.replace("<room_3d_link>", room_viewer_doc)
        if room.prop_thumbnail_custom == "True":
            html_room_segment = html_room_segment.replace("<room_thumbnail>", room.name.lower().replace(" ","_") + "_thumbnail_custom.jpg?key=" + str(random.randint(1, 100000)))
        else:
            html_room_segment = html_room_segment.replace("<room_thumbnail>", room.name.lower().replace(" ","_") + "_thumbnail.jpg?key=" + str(random.randint(1, 100000)))
        
        # ////// Room Customer Selections
        html_room_segment = html_room_segment.replace("<ext_color>", self.ext_color)
        html_room_segment = html_room_segment.replace("<int_color>", self.int_color)
        html_room_segment = html_room_segment.replace("<trim_color>", self.trim_color)
        html_room_segment = html_room_segment.replace("<hardware>", self.hardware)
        html_room_segment = html_room_segment.replace("<rods>", self.rods)
        html_room_segment = html_room_segment.replace("<door_drawer_faces>", self.door_drawer_style)
        html_room_segment = html_room_segment.replace("<drawer_boxes>", self.box_style)
        html_room_segment = html_room_segment.replace("<hamper>", self.hamper)
        html_room_segment = html_room_segment.replace("<accessories>", self.accessories)
        html_room_segment = html_room_segment.replace("<countertop>", self.countertop)
        html_room_segment = html_room_segment.replace("<backing>", self.backing)
        html_room_segment = html_room_segment.replace("<glass>", self.glass)
        html_room_segment = html_room_segment.replace("<notes>", self.notes)

        # ////// Add the room data to our proposal html documents
        html_content = html_content.replace("<room_segment>", html_room_segment)
        html_content = html_content.replace("<thumbnail_max_width>", "520")
        html_content_mobile = html_content_mobile.replace("<tr><td><room_segment></td></tr>", html_room_segment + "<tr><td><room_segment></td></tr>")
        html_content_mobile = html_content_mobile.replace("<thumbnail_max_width>", "550")
        # ////// Embed AWS S3 URLs to final html docs
        html_content = html_content.replace("<s3_resource_url>", "https://" + AWS_S3_BUCKET_NAME + ".s3." + AWS_S3_REGION_NAME + ".amazonaws.com/public/resource")
        html_content_mobile = html_content_mobile.replace("<s3_resource_url>", "https://" + AWS_S3_BUCKET_NAME + ".s3." + AWS_S3_REGION_NAME + ".amazonaws.com/public/resource")

        # ////// Stamp proposal expiration date on the documents
        html_content = html_content.replace("<doc_date>", datetime.today().strftime('%Y-%m-%d'))
        html_content = html_content.replace("<exp_days>", str(PROPOSAL_LIFECYCLE_DAYS))
        html_content_mobile = html_content_mobile.replace("<doc_date>", datetime.today().strftime('%Y-%m-%d'))
        html_content_mobile = html_content_mobile.replace("<exp_days>", str(PROPOSAL_LIFECYCLE_DAYS))

        # https://snap-proposals.s3.us-west-2.amazonaws.com/public/resource
        # ////// Save the proposal files
        with open(proposal_path, 'w', encoding='utf-8') as file:
                file.write(html_content)

        with open(proposal_path_mobile, 'w', encoding='utf-8') as file:
                file.write(html_content_mobile)

    def add_room_viewer_document(self, context):
        project = context.window_manager.sn_project.get_project()
        proposal_dir = os.path.join(project.dir_path, "Proposal")
        room = project.rooms[project.room_index]
        room_path = os.path.join(proposal_dir, room.name.lower().replace(" ","_") + "_viewer.html")
       
        with open(room_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
       
        html_content = html_content.replace("<model_uid>", room.prop_3d_exported_uid)
        html_content = html_content.replace("<s3_resource_url>", "https://" + AWS_S3_BUCKET_NAME + ".s3." + AWS_S3_REGION_NAME + ".amazonaws.com/public/resource")
        html_content = html_content.replace("<doc_date>", datetime.today().strftime('%Y-%m-%d'))
        html_content = html_content.replace("<exp_days>", str(PROPOSAL_LIFECYCLE_DAYS))
        with open(room_path, 'w', encoding='utf-8') as file:
                file.write(html_content)

    def execute(self, context):
        print("Add Room to Proposal")

        self.get_room_selection_data(context)
       
        self.add_room_to_proposal_document(context)

        self.add_room_viewer_document(context)

        return {'FINISHED'}


class SNAP_OT_Proposal_Operations(Operator):
    """ Library management tools.
    """
    bl_idname = "project_manager.proposal_operations"
    bl_label = "Project Proposal Operations"
    bl_description = "Project Proposal Operations"
    bl_options = {'UNDO'}
    
    operation_type: EnumProperty(name="Operation Type",items=[('PREPARE_THUMBS','Prepare Thumbs','Prepare Thumbs'),
                                                                ('PREPARE_3D','Prepare 3D','Prepare 3D'),
                                                                ('EXPORT_3D','Export 3D','Export 3D'),
                                                                ('BUILD_PROPOSAL','Build Proposal','Build Proposal'),
                                                                ('DELETE_CUSTOM_THUMB','Delete Custom Thumbnail','Delete Custom Thumbnail'),
                                                                ('DELETE_PREPARE_3D','Delete Prepare 3D','Delete Prepare 3D'),
                                                                ('DELETE_EXPORT_3D','Delete Export 3D','Delete Export 3D'),
                                                                ('DELETE_ROOM_PROGRESS','Delete Room Progress','Delete Room Progress'),
                                                                ('DELETE_PROPOSAL','Delete Proposal','Delete Proposal')])
    
    _timer = None

    project = None
    room_list = []
    proposal_dir = ""
    proposal_path = ""
    proposal_path_mobile = ""

    status_updated = False
    header_text = ""
   
    @classmethod
    def poll(cls, context):
        return True
    
    def invoke(self, context, event):
        wm = context.window_manager
        props = wm.snap
        self.project = context.window_manager.sn_project.get_project()
        self.proposal_dir = os.path.join(self.project.dir_path, "Proposal")
        self.proposal_path = os.path.join(self.proposal_dir, self.project.name + ".html")
        self.proposal_path_mobile = os.path.join(self.proposal_dir, self.project.name + "_mobile.html")

        if self.operation_type != 'BUILD_PROPOSAL':
            self.project.prop_status = "Starting..."
        else:
            self.project.prop_status = "Generating Proposal Room Data"
            self.header_text = "Generating Proposal Room Data"
            bpy.context.area.tag_redraw()

        if bpy.data.is_dirty:
            bpy.ops.wm.save_mainfile()
 
        if self.project.prop_id == "" or self.project.prop_id == "None" or self.project.prop_id == "True":
            self.project.prop_id = str(uuid.uuid4())

        if not os.path.exists(self.proposal_dir):
            os.makedirs(self.proposal_dir, exist_ok=True)
        
        if self.operation_type == 'BUILD_PROPOSAL':
            self.prepare_project_proposal_files()
              
        self.room_list = []
        for room in self.project.rooms:
            if room.prop_selected:
                if self.operation_type == 'PREPARE_3D':
                    room.prop_3d_prepared = ""
                    room.prop_thumbnail = ""
                elif self.operation_type == 'EXPORT_3D':
                    room.prop_3d_exported = ""
                self.room_list.append(room)

            if self.operation_type == 'BUILD_PROPOSAL':
                room.prop_published = ""
                room.prop_published_utc = ""
                
        props.total_items = len(self.room_list)

        self._timer = wm.event_timer_add(1.0, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}
        
    def modal(self, context, event):
        context.window.cursor_set('WAIT')
        
        progress = context.window_manager.snap
        context.area.header_text_set(text=self.header_text)
        self.project.prop_status = self.header_text
                
        self.mouse_loc = (event.mouse_region_x,event.mouse_region_y)
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            return self.cancel(context)

        if event.type == 'TIMER':
            if progress.current_item + 1 <= len(self.room_list):
                if self.operation_type == 'PREPARE_3D':
                    print("starting prepare_room_for_3d_export: " + self.room_list[progress.current_item].name)
                    
                    if self.status_updated == False:
                        self.header_text = "Preparing " + self.room_list[progress.current_item].name + " for 3D Export"
                        bpy.context.area.tag_redraw()
                        self.status_updated = True
                    elif self.status_updated == True:
                        self.prepare_room_for_3d_export(self.room_list[progress.current_item])
                        self.project.rooms[self.room_list[progress.current_item].name].prop_3d_prepared = "True"
                        self.project.rooms[self.room_list[progress.current_item].name].prop_3d_prepared_utc = str(datetime.utcnow())
                        bpy.context.area.tag_redraw()
                        print("finished prepare_room_for_3d_export: " + self.room_list[progress.current_item].name)
               
                        print("starting create_room_thumbnail: " + self.room_list[progress.current_item].name)
                        self.create_room_thumbnail(self.room_list[progress.current_item])
                        self.project.rooms[self.room_list[progress.current_item].name].prop_thumbnail = "True"
                        bpy.context.area.tag_redraw()
                        print("finished create_room_thumbnail: " + self.room_list[progress.current_item].name)
                        self.status_updated = False
                        progress.current_item += 1
                        
                elif self.operation_type == 'EXPORT_3D':
                    if self.status_updated == False:
                        self.header_text = "Exporting " + self.room_list[progress.current_item].name + " to Classy Portal"
                        bpy.context.area.tag_redraw()
                        self.status_updated = True
                    elif self.status_updated == True:
                        print("starting export_room_to_sketchfab: " + self.room_list[progress.current_item].name)
                        room_name = self.room_list[progress.current_item].name
                        bpy.ops.project_manager.update_room_in_sketchfab(active_room=room_name)
                        self.project.rooms[self.room_list[progress.current_item].name].prop_3d_exported = "True"
                        self.project.rooms[self.room_list[progress.current_item].name].prop_3d_exported_utc = str(datetime.utcnow())
                        self.status_updated = False
                        print("ending export_room_to_sketchfab: " + self.room_list[progress.current_item].name)
                        progress.current_item += 1

                elif self.operation_type == 'BUILD_PROPOSAL':
                    if self.status_updated == False:
                        self.header_text = "Adding " + self.room_list[progress.current_item].name + " to Project Proposal"
                        bpy.context.area.tag_redraw()
                        self.status_updated = True
                    elif self.status_updated == True:
                        print("starting add_room_to_proposal: " + self.room_list[progress.current_item].name)
                        self.add_room_to_proposal(self.room_list[progress.current_item])
                        self.project.rooms[self.room_list[progress.current_item].name].prop_id = self.project.prop_id
                        self.project.rooms[self.room_list[progress.current_item].name].prop_published = "True"
                        self.project.rooms[self.room_list[progress.current_item].name].prop_published_utc = str(datetime.utcnow())
                        print("ending add_room_to_proposal: " + self.room_list[progress.current_item].name)
                        self.status_updated = False
                        bpy.context.area.tag_redraw()
                        progress.current_item += 1

                elif self.operation_type == 'DELETE_CUSTOM_THUMB':
                    if self.status_updated == False:
                        self.header_text = "Resetting Thumbnail for " + self.room_list[progress.current_item].name + ""
                        bpy.context.area.tag_redraw()
                        self.status_updated = True
                    elif self.status_updated == True:
                        print("starting delete_room_custom_thumbnail: " + self.room_list[progress.current_item].name)
                        self.delete_room_custom_thumbnail(self.room_list[progress.current_item])
                        print("ending delete_room_custom_thumbnail: " + self.room_list[progress.current_item].name)
                        self.status_updated = False
                        bpy.context.area.tag_redraw()
                        progress.current_item += 1

                elif self.operation_type == 'DELETE_PREPARE_3D':
                    if self.status_updated == False:
                        self.header_text = "Deleting 3D Preparation for " + self.room_list[progress.current_item].name + ""
                        bpy.context.area.tag_redraw()
                        self.status_updated = True
                    elif self.status_updated == True:
                        print("starting delete_room_3d_prep: " + self.room_list[progress.current_item].name)
                        self.delete_room_3d_prep(self.room_list[progress.current_item])
                        print("ending delete_room_3d_prep: " + self.room_list[progress.current_item].name)
                        self.status_updated = False
                        bpy.context.area.tag_redraw()
                        progress.current_item += 1

                elif self.operation_type == 'DELETE_EXPORT_3D':
                    if self.status_updated == False:
                        self.header_text = "Deleting " + self.room_list[progress.current_item].name + " from Sketchfab"
                        bpy.context.area.tag_redraw()
                        self.status_updated = True
                    elif self.status_updated == True:
                        print("starting delete_room_from_sketchfab: " + self.room_list[progress.current_item].name)
                        self.delete_room_3d_export(self.room_list[progress.current_item])
                        print("ending delete_room_from_sketchfab: " + self.room_list[progress.current_item].name)
                        self.status_updated = False
                        bpy.context.area.tag_redraw()
                        progress.current_item += 1

                elif self.operation_type == 'DELETE_ROOM_PROGRESS':
                    if self.status_updated == False:
                        self.header_text = "Deleting Progress for " + self.room_list[progress.current_item].name + ""
                        bpy.context.area.tag_redraw()
                        self.status_updated = True
                    elif self.status_updated == True:
                        print("starting delete_room_progress: " + self.room_list[progress.current_item].name)
                        self.delete_room_progress(self.room_list[progress.current_item])
                        print("ending delete_room_progress: " + self.room_list[progress.current_item].name)
                        self.status_updated = False
                        bpy.context.area.tag_redraw()
                        progress.current_item += 1

                elif self.operation_type == 'DELETE_PROPOSAL':
                    self.project.prop_status = "Deleting Published Proposal"
                    self.header_text = "Deleting Published Proposal"
                    self.status_updated = False
                    bpy.context.area.tag_redraw()
                    progress.current_item += 1

                context.area.header_text_set(text=self.header_text)
                self.project.prop_status = self.header_text

            else:
                print("end loop status_updated=",self.status_updated)
                if self.operation_type == 'BUILD_PROPOSAL':
                    if self.status_updated == False:
                        self.project.prop_status = "Publishing Project Proposal to the web"
                        self.header_text = "Publishing Project Proposal to the web"
                        self.status_updated = True
                    else:
                        print("starting upload_to_s3_bucket")
                        self.publish_project_proposal_files()
                        return self.cancel(context)
                elif self.operation_type == 'DELETE_PROPOSAL':
                    if self.status_updated == False:
                        self.project.prop_status = "Deleting Published Proposal"
                        self.header_text = "Deleting Published Proposal"
                        self.status_updated = True
                    else:
                        print("starting delete_published_proposal")
                        self.delete_published_proposal()
                        return self.cancel(context)

                else:
                    return self.cancel(context)
        
        return {'PASS_THROUGH'}

    def publish_project_proposal_files(self):
        print("publish_project_proposal_files")
        bucket_name = AWS_S3_BUCKET_NAME
        region_name = AWS_S3_REGION_NAME
        object_name = self.project.prop_id + '/' + self.project.name + ".html"
        object_name_mobile = self.project.prop_id + '/' + self.project.name + "_mobile.html"

        # Upload the html file
        if upload_object_to_s3(self.proposal_path, bucket_name, object_name):
            print("Upload successful")
            proposal_url = get_s3_object_url(bucket_name, object_name, region_name)
            self.project.prop_published = "True"    
            self.project.prop_published_utc = str(datetime.utcnow())      
        else:
            print("Upload failed")
            self.project.prop_published = "True"  
            self.project.prop_published_utc = str(datetime.utcnow())     

        # Upload the mobile html file
        if upload_object_to_s3(self.proposal_path_mobile, bucket_name, object_name_mobile):
            print("Upload mobile successful")
        else:
            print("Upload mobile failed")

        # upload the room viewer files
        for room in self.room_list:
            print("room viewer to upload: ", room.name)
            file_path = os.path.join(self.proposal_dir, room.name.lower().replace(" ","_") + "_viewer.html")
            object_name = self.project.prop_id + '/' + room.name.lower().replace(" ","_") + "_viewer.html"
            if upload_object_to_s3(file_path, bucket_name, object_name):
                print("Upload room viewer successful")
            else:
                print("Upload room viewr failed")

        # upload the room thumb files
        for room in self.room_list:
            print("room thumb to upload: ", room.name)
            if room.prop_thumbnail_custom == "True":
                file_path = os.path.join(self.proposal_dir, room.name.lower().replace(" ","_") + "_thumbnail_custom.jpg")
                object_name = self.project.prop_id + '/' + room.name.lower().replace(" ","_") + "_thumbnail_custom.jpg"
            else:
                file_path = os.path.join(self.proposal_dir, room.name.lower().replace(" ","_") + "_thumbnail.jpg")
                object_name = self.project.prop_id + '/' + room.name.lower().replace(" ","_") + "_thumbnail.jpg"
            if upload_object_to_s3(file_path, bucket_name, object_name):
                print("Upload thumb successful")
            else:
                print("Upload thumb failed")
               
        webbrowser.open(proposal_url)

    def prepare_project_proposal_files(self):
        template_folder = os.path.join(os.path.dirname(__file__), 'proposals')

        shutil.copyfile(os.path.join(template_folder, 'prop_body.html'), self.proposal_path)

        shutil.copyfile(os.path.join(template_folder, 'prop_body_mobile.html'), self.proposal_path_mobile)

        for room in self.project.rooms:
            if room.prop_selected == True:
                room_path = os.path.join(self.proposal_dir, room.name.lower().replace(" ","_") + "_viewer.html")
                shutil.copyfile(os.path.join(template_folder, 'prop_room_viewer.html'), room_path)

    def create_room_thumbnail(self, room):
        print("create_room_thumbnail: " + room.name)
        room_path = os.path.join(self.proposal_dir, room.name.lower().replace(" ","_") + "-3d_export.blend")
        thumbnail_blend_path = os.path.join(sn_paths.ROOT_DIR, 'library_manager', 'thumbnail_room.blend')
       
        script = os.path.join(bpy.app.tempdir, 'create_room_thumbnail.py')
        script_file = open(script, 'w')
        script_file.write("import bpy\n")
        script_file.write("bpy.ops.project_manager.create_room_thumbnail(room_path=r'" + room_path + "')\n")
        script_file.close()
        subprocess.call(bpy.app.binary_path + ' "' + thumbnail_blend_path + '" -b --python "' + script + '"')

    def prepare_room_for_3d_export(self, room):
        bpy.context.area.tag_redraw()
        export_file_path = os.path.join(self.proposal_dir, room.name.lower().replace(" ","_") + "-3d_export.blend")
        shutil.copyfile(room.file_path, export_file_path)
        
        script_start = time.time()
        script = os.path.join(bpy.app.tempdir, 'prepare_3d_export.py')
        script_file = open(script, 'w')
        script_file.write("import bpy\n")
        script_file.write("bpy.ops.project_manager.prepare_room_for_3d_export()\n")
        script_file.close()
        subprocess.call(bpy.app.binary_path + ' "' + export_file_path + '" -b --python "' + script + '"')
        script_end = time.time()

        script_time = script_end - script_start
        print("---------------------------------")
        print(f"Script Start Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(script_start))}")
        print(f"Script End Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(script_end))}")
        print(f"Script Elapsed Time: {script_time} seconds")

    def delete_room_custom_thumbnail(self, room):
        print("delete_room_custom_thumbnail: " + room.name)
        if room.prop_selected == True and room.prop_thumbnail_custom == "True":
            file_path = os.path.join(self.project.dir_path, "Proposal", room.name.lower().replace(" ","_") + "_thumbnail_custom.jpg")
            print("removing custom thumbnail file: ",file_path)
            if os.path.exists(file_path):
                os.remove(file_path)
            room.prop_thumbnail_custom = ""
            room.prop_thumbnail_custom_utc = ""

    def delete_room_3d_prep(self, room):
        print("delete_room_3d_prep: " + room.name)
        if room.prop_selected == True and room.prop_3d_prepared == "True":
            file_path = os.path.join(self.project.dir_path, "Proposal", room.name.lower().replace(" ","_") + "-3d_export.blend")
            print("removing 3d_prep file: ",file_path)
            if os.path.exists(file_path):
                os.remove(file_path)
            room.prop_3d_prepared = ""
            room.prop_3d_prepared_utc = ""

            file_path = os.path.join(self.project.dir_path, "Proposal", room.name.lower().replace(" ","_") + "_thumbnail.jpg")
            print("removing custom thumbnail file: ",file_path)
            if os.path.exists(file_path):
                os.remove(file_path)
            room.prop_thumbnail = ""

    def delete_room_3d_export(self, room):
        print("delete_room_3d_export: " + room.name)
        if room.prop_selected == True and room.prop_3d_exported == "True" and room.prop_3d_exported_uid != "":
            bpy.ops.project_manager.update_room_in_sketchfab(active_room=room.name, http_method="DELETE")
        elif room.prop_selected == True and room.prop_3d_exported == "True":
            room.prop_3d_exported = ""
            room.prop_3d_exported_utc = ""
            room.prop_3d_exported_url = ""
            room.prop_3d_exported_uid = ""

    def delete_room_progress(self, room):
        print("delete_room_progress: " + room.name)
        if room.prop_selected == True:
            if room.prop_thumbnail_custom == "True":
                self.delete_room_custom_thumbnail(room)
            if room.prop_3d_prepared == "True":
                self.delete_room_3d_prep(room)
            if room.prop_3d_exported == "True":
                self.delete_room_3d_export(room)

    def delete_published_proposal(self):
        bucket_name = AWS_S3_BUCKET_NAME
        target_folder = self.project.prop_id + '/' 
        delete_s3_objects_by_prefix(bucket_name, target_folder)

        file_path = os.path.join(self.project.dir_path, "Proposal", self.project.name + ".html")
        if os.path.exists(file_path):
            os.remove(file_path)

        self.project.prop_published = ""
        self.project.prop_published_utc = ""

    def add_room_to_proposal(self, room):
        print("add_room_to_proposal: " + room.name)
        filepath = room.file_path
        script = os.path.join(bpy.app.tempdir, 'add_room_to_proposal.py')
        script_file = open(script, 'w')
        script_file.write("import bpy\n")
        script_file.write("bpy.ops.project_manager.add_room_to_proposal()\n")
        script_file.close()
        subprocess.call(bpy.app.binary_path + ' "' + filepath + '" -b --python "' + script + '"')

    def cancel(self, context):
        self.project.prop_status = ""
        progress = context.window_manager.snap
        progress.current_item = 0
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        context.window.cursor_set('DEFAULT')
        context.area.header_text_set(None)        

        return {'FINISHED'}


class SNAP_OT_Proposal_View(Operator):
    bl_idname = "project_manager.proposal_view"
    bl_label = "View Proposal on the Web"
    bl_description = "View the published proposal on the web"

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        project = context.window_manager.sn_project.get_project()

        bucket_name = AWS_S3_BUCKET_NAME
        region_name = AWS_S3_REGION_NAME
        object_name = project.prop_id + '/' + project.name + ".html"
        proposal_url = get_s3_object_url(bucket_name, object_name, region_name)
        
        webbrowser.open(proposal_url)

        return{'FINISHED'}


class SNAP_OT_Proposal_Copy_URL(Operator):
    bl_idname = "project_manager.proposal_copy_url"
    bl_label = "Copy Proposal URL to Clipboard"
    bl_description = "Copy the published proposal URL to your windows clipboard"

    @classmethod
    def poll(cls, context):
        project = context.window_manager.sn_project.get_project()
        
        if project.prop_published == "True":
            return True
        else:
            return False
   
    def execute(self, context):
        project = context.window_manager.sn_project.get_project()

        bucket_name = AWS_S3_BUCKET_NAME
        region_name = AWS_S3_REGION_NAME
        object_name = project.prop_id + '/' + project.name + ".html"
        proposal_url = get_s3_object_url(bucket_name, object_name, region_name)
        
        pyperclip.copy(proposal_url)

        return{'FINISHED'}


class SNAP_OT_Proposal_Copy_Link(Operator):
    bl_idname = "project_manager.proposal_copy_link"
    bl_label = "Copy Proposal Link to Clipboard"
    bl_description = "Copy the published proposal link to your windows clipboard"

    @classmethod
    def poll(cls, context):
        project = context.window_manager.sn_project.get_project()
        
        if project.prop_published == "True":
            return True
        else:
            return False
        
    def execute(self, context):
        project = context.window_manager.sn_project.get_project()

        bucket_name = AWS_S3_BUCKET_NAME
        region_name = AWS_S3_REGION_NAME
        object_name = project.prop_id + '/' + project.name + ".html"
        proposal_url = get_s3_object_url(bucket_name, object_name, region_name)

        #// copy base url to clipboard to ensure windows clipboard is initialized...
        pyperclip.copy(proposal_url)
            
        # Create the HTML formatted link
        html = f'<a href="{proposal_url}">Click here for your Classy Closets Proposal</a>'

        CF_HTML = ctypes.windll.user32.RegisterClipboardFormatW("HTML Format")
        HTML_HEADER = """Version:0.9
            StartHTML:{start_html:08d}
            EndHTML:{end_html:08d}
            StartFragment:{start_fragment:08d}
            EndFragment:{end_fragment:08d}
            """

        # Calculate the positions
        start_html = len(HTML_HEADER.format(start_html=0, end_html=0, start_fragment=0, end_fragment=0))
        start_fragment = start_html
        end_fragment = start_fragment + len(html)
        end_html = end_fragment

        # Format the header with correct positions
        header = HTML_HEADER.format(start_html=start_html, end_html=end_html, start_fragment=start_fragment, end_fragment=end_fragment)
        full_html = header + html

        # Prepare the HTML data
        data = full_html.encode('utf-8')

        # Allocate global memory
        h_global_mem = ctypes.windll.kernel32.GlobalAlloc(0x2000, len(data) + 1)
        pch_data = ctypes.windll.kernel32.GlobalLock(h_global_mem)
        ctypes.cdll.msvcrt.strcpy(ctypes.c_char_p(pch_data), data)
        ctypes.windll.kernel32.GlobalUnlock(h_global_mem)

        # Set the clipboard data
        ctypes.windll.user32.OpenClipboard(0)
        ctypes.windll.user32.EmptyClipboard()
        ctypes.windll.user32.SetClipboardData(CF_HTML, h_global_mem)
        ctypes.windll.user32.CloseClipboard()
        print("The HTML fragement link has been copied to the clipboard.")

        return{'FINISHED'}


class SNAP_OT_Proposal_Build_Poll(Operator):
    bl_idname = "project_manager.proposal_build_poll"
    bl_label = "Publish/Update Project Proposal"
    bl_description = "Publish/Update the published proposal on the web"

    @classmethod
    def poll(cls, context):
        project = context.window_manager.sn_project.get_project()
        room_count = 0
        validation = True
       
        if project.prop_status != "":
            return False
        else:
            for room in project.rooms:
                if room.prop_selected and room.prop_3d_prepared != "True":
                    validation = False
                # elif room.prop_selected and room.prop_3d_exported != "True":
                #     validation = False
                if room.prop_selected:
                    room_count += 1

            if room_count == 0 or validation == False:
                return False
            else:
                return True
   
    def execute(self, context):

        bpy.ops.project_manager.proposal_operations('INVOKE_DEFAULT', operation_type='BUILD_PROPOSAL')

        return{'FINISHED'}


class SNAP_OT_Proposal_Prepare_3D_Poll(Operator):
    bl_idname = "project_manager.proposal_prepare_3d_poll"
    bl_label = "Prepare selected rooms for 3D export"
    bl_description = "Prepare selected rooms for 3D export"

    @classmethod
    def poll(cls, context):
        project = context.window_manager.sn_project.get_project()
        
        for room in project.rooms:
            if room.prop_selected:
                return True
                break
        return False

   
    def execute(self, context):
        print("starting project_manager.prepare_project_proposal")

        bpy.ops.project_manager.proposal_operations('INVOKE_DEFAULT', operation_type='PREPARE_3D')

        return{'FINISHED'}
    

class SNAP_OT_Proposal_Export_3D_Poll(Operator):
    bl_idname = "project_manager.proposal_export_3d_poll"
    bl_label = "Export selected rooms to Classy Portal (Lead ID required)"
    bl_description = "Export selected rooms to Classy Portal (Lead ID required)"

    @classmethod
    def poll(cls, context):
        project = context.window_manager.sn_project.get_project()
        room_count = 0
        validation = True
       
        if project.lead_id.strip() == "" or project.lead_id == "None":
            validation = False
        else:
            for room in project.rooms:
                if room.prop_selected and room.prop_3d_prepared != "True":
                    validation = False
                if room.prop_selected:
                    room_count += 1

            if room_count == 0 or validation == False:
                return False
            else:
                return True
   
    def execute(self, context):

        bpy.ops.project_manager.proposal_operations('INVOKE_DEFAULT', operation_type='EXPORT_3D')

        return{'FINISHED'}
    

class SNAP_OT_Proposal_Delete_Custom_Thumbnail_Poll(Operator):
    bl_idname = "project_manager.proposal_delete_custom_thumbnail_poll"
    bl_label = "Restore default thumbnails for selected rooms"
    bl_description = "Restore default thumbnails for selected rooms"

    @classmethod
    def poll(cls, context):
        project = context.window_manager.sn_project.get_project()
        
        for room in project.rooms:
            if room.prop_selected and room.prop_thumbnail_custom == "True":
                return True
        return False
   
    def execute(self, context):

        bpy.ops.project_manager.proposal_operations('INVOKE_DEFAULT', operation_type='DELETE_CUSTOM_THUMB')

        return{'FINISHED'}
    

class SNAP_OT_Proposal_Delete_Prepare_3D_Poll(Operator):
    bl_idname = "project_manager.proposal_delete_prepare_3d_poll"
    bl_label = "Clear 3D preparation for selected rooms"
    bl_description = "Clear 3D preparation for selected rooms"

    @classmethod
    def poll(cls, context):
        project = context.window_manager.sn_project.get_project()
        
        for room in project.rooms:
            if room.prop_selected and room.prop_3d_prepared == "True":
                return True
        return False
   
    def execute(self, context):

        bpy.ops.project_manager.proposal_operations('INVOKE_DEFAULT', operation_type='DELETE_PREPARE_3D')

        return{'FINISHED'}
    
    
class SNAP_OT_Proposal_Delete_Export_3D_Poll(Operator):
    bl_idname = "project_manager.proposal_delete_export_3d_poll"
    bl_label = "Clear 3D Export for selected rooms"
    bl_description = "Clear 3D Export for selected rooms"

    @classmethod
    def poll(cls, context):
        project = context.window_manager.sn_project.get_project()
        
        for room in project.rooms:
            if room.prop_selected and room.prop_3d_exported == "True":
                return True
        return False
   
    def execute(self, context):

        bpy.ops.project_manager.proposal_operations('INVOKE_DEFAULT', operation_type='DELETE_EXPORT_3D')

        return{'FINISHED'}
    

class SNAP_OT_Proposal_Delete_All_Progress_Poll(Operator):
    bl_idname = "project_manager.proposal_delete_all_progress_poll"
    bl_label = "Clear ALL progress for selected rooms"
    bl_description = "Clear ALL progress for selected rooms"

    @classmethod
    def poll(cls, context):
        project = context.window_manager.sn_project.get_project()
        
        for room in project.rooms:
            if room.prop_selected and room.prop_3d_exported == "True":
                return True
            elif room.prop_selected and room.prop_3d_prepared == "True":
                return True
            elif room.prop_selected and room.prop_thumbnail_custom == "True":
                return True
        return False
   
    def execute(self, context):

        bpy.ops.project_manager.proposal_operations('INVOKE_DEFAULT', operation_type='DELETE_ROOM_PROGRESS')

        return{'FINISHED'}
    

class SNAP_OT_Proposal_Delete_Published_Poll(Operator):
    bl_idname = "project_manager.proposal_delete_published_poll"
    bl_label = "Delete published proposal from the web"
    bl_description = "Delete published proposal from the web"

    @classmethod
    def poll(cls, context):
        project = context.window_manager.sn_project.get_project()
        
        if project.prop_published == "True":
            return True
        else:
            return False
   
    def execute(self, context):

        bpy.ops.project_manager.proposal_operations('INVOKE_DEFAULT', operation_type='DELETE_PROPOSAL')

        return{'FINISHED'}



classes = (
    SNAP_OT_Create_Project,
    SNAP_OT_Copy_Project,
    SNAP_OT_Import_Project,
    SNAP_OT_Delete_Project,
    SNAP_OT_Add_Room,
    SNAP_OT_Open_Room,
    SNAP_OT_Delete_Room,
    SNAP_OT_Import_Room,
    SNAP_OT_Select_All_Rooms,
    SNAP_OT_Prepare_Project_XML,
    SNAP_OT_Copy_Room,
    SNAP_OT_Load_Projects,
    SNAP_OT_Unarchive_Project,

    SNAP_OT_Proposal_Select_All_Rooms,
    SNAP_OT_Proposal_Prepare_Room_For_3D_Export,
    SNAP_OT_Proposal_Add_Room_To_Documents,
    SNAP_OT_Proposal_Create_Room_Custom_Thumbnail,
    SNAP_OT_Proposal_Start_Room_Custom_Thumbnail,
    SNAP_OT_Proposal_Create_Room_Thumbnail,
    SNAP_OT_Proposal_View_Room_Thumbnail,

    SNAP_OT_Proposal_Operations,

    SNAP_OT_Proposal_View,
    SNAP_OT_Proposal_Copy_URL,
    SNAP_OT_Proposal_Copy_Link,
    SNAP_OT_Proposal_Build_Poll,
    SNAP_OT_Proposal_Prepare_3D_Poll,
    SNAP_OT_Proposal_Export_3D_Poll,
    SNAP_OT_Proposal_Delete_Custom_Thumbnail_Poll,
    SNAP_OT_Proposal_Delete_Prepare_3D_Poll,
    SNAP_OT_Proposal_Delete_Export_3D_Poll,
    SNAP_OT_Proposal_Delete_All_Progress_Poll,
    SNAP_OT_Proposal_Delete_Published_Poll,

)


register, unregister = bpy.utils.register_classes_factory(classes)
