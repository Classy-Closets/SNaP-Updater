import bpy
import os
import re
import pathlib
import xml.etree.ElementTree as ET
from bpy.types import UIList, PropertyGroup, Menu
from bpy.props import (StringProperty,
                       BoolProperty,
                       EnumProperty,
                       IntProperty,
                       CollectionProperty,
                       PointerProperty)
from . import pm_utils, pm_ops
from shutil import copyfile
global create_project_flag
create_project_flag = False

from snap import sn_utils


def update_project_props(self, context):
    self.modify_project_file()

def update_room_props(self, context):
    self.modify_room_data()

def make_new_name(path, new_name):
    return path + "\\" + new_name + ".blend"

def rename_room(self, context):
    props = bpy.context.window_manager.sn_project
    empty_name = self.name == ""

    if props.projects_loaded:
        if empty_name:
            self.name = self.og_name
            bpy.ops.snap.log_window(
                "INVOKE_DEFAULT",
                message="Room Name Error",
                message2="Please provide a room name.",
                icon="ERROR",
                width=400)

        if re.compile("[@_!#$'%^&*()<>?/\|}{~:]").search(self.name) == None:
            if self.file_path:
                curr_opnd_file = bpy.data.filepath
                new_room_name = self.name
                ccp_file = ""
                old_bl_path = str(self.file_path)
                new_bl_path = ""
                proj = props.projects[props.project_index]

                for room in proj.rooms:
                    ccp_file = str(proj.file_path)
                    if room.file_path == self.file_path and ccp_file != "":
                        xml_tree = ET.parse(ccp_file)
                        xml_root = xml_tree.getroot()
                        for element in xml_root.findall('Rooms'):
                            for element_room in list(element):
                                rel_path = os.path.join(*old_bl_path.split(os.sep)[-2:])
                                if element_room.attrib["path"] == rel_path:
                                    old_room = element_room.attrib["name"]
                                    renaming = old_room != new_room_name
                                    is_opnd_room = old_room in curr_opnd_file
                                    if renaming:
                                        print("Room name changed to:", self.name)
                                        element_room.attrib["name"] = new_room_name
                                        element_room.text = new_room_name
                                        new_bl_path = make_new_name(proj.dir_path, new_room_name)
                                        new_rel_bl_path = os.path.join(*new_bl_path.split(os.sep)[-2:])
                                        element_room.attrib["path"] = new_rel_bl_path
                                        xml_tree.write(ccp_file)
                                        copyfile(old_bl_path, new_bl_path)
                                        if is_opnd_room:
                                            bpy.ops.project_manager.open_room(file_path=new_bl_path)
                                        else:
                                            room.file_path = new_rel_bl_path
                                        os.remove(old_bl_path)
                                        break

            self.og_name = self.name
            return
        else:
            self.name = self.og_name
            bpy.ops.snap.log_window(
                "INVOKE_DEFAULT",
                message="Room Name Error",
                message2="Room Name CANNOT contain: [@_!#$'%^&*()<>?/\|}{~:]",
                icon="ERROR",
                width=400)
            return

def rename_project(self, context):
    props = bpy.context.window_manager.sn_project
    proj = props.projects[props.project_index]
    empty_name = self.name == ""

    if create_project_flag:
        return

    if props.projects_loaded:
        if props.projects_loaded:
            if empty_name:
                self.name = self.og_name
                bpy.ops.snap.log_window(
                    "INVOKE_DEFAULT",
                    message="Room Name Error",
                    message2="Please provide a room name.",
                    icon="ERROR",
                    width=400)
                return

        if re.compile("[@_!#$'%^&*()<>?/\|}{~:]").search(self.name) is None and not empty_name:
            # Rename Project Directory
            new_project_dir = os.path.join(pm_utils.get_project_dir(), self.name)
            if os.path.exists(proj.dir_path):
                os.rename(proj.dir_path, new_project_dir)
                proj.dir_path = new_project_dir
                print("Project name changed to:", self.name)

            """Update .ccp"""
            old_ccp_path = pathlib.PurePath(proj.file_path)
            ccp_path = os.path.join(new_project_dir, ".snap", old_ccp_path.name)
            new_ccp_path = os.path.join(new_project_dir, ".snap", self.name + ".ccp")

            # Rename copied .ccp
            if os.path.exists(ccp_path):
                os.rename(ccp_path, new_ccp_path)
                proj.file_path = new_ccp_path

            # Update name in .ccp
            if os.path.exists(new_ccp_path):
                tree = ET.parse(new_ccp_path)
                root = tree.getroot()

                for elm in root.findall("ProjectInfo"):
                    items = list(elm)

                    for item in items:
                        if item.tag == 'name':
                            item.text = self.name

                # Update room filepaths
                for elm in root.findall("Rooms"):
                    items = list(elm)

                    for item in items:
                        bfile_path = pathlib.Path(item.attrib['path'])
                        new_path = os.path.join(self.name, bfile_path.parts[-1])
                        item.attrib['path'] = new_path

                    for room in proj.rooms:
                        old_room_path = pathlib.PurePath(room.file_path)
                        room.file_path = os.path.join(new_project_dir, old_room_path.name)

                tree.write(new_ccp_path)
            self.og_name = self.name
            return
        else:
            self.name = self.og_name
            bpy.ops.snap.log_window(
                "INVOKE_DEFAULT",
                message="Project Name Error",
                message2="Project Name CANNOT contain: [@_!#$'%^&*()<>?/\|}{~:]",
                icon="ERROR",
                width=400)
            return


class CollectionMixIn:
    dir_path: StringProperty(name="Directory Path", default="", subtype='DIR_PATH')

    def init(self, col, name=""):
        self.set_unique_name(col, name)
        self.dir_path = os.path.join(pm_utils.get_project_dir(), self.get_clean_name(self.name))

    def format_name(self, stem, nbr):
        return '{st}.{nbr:03d}'.format(st=stem, nbr=int(nbr))

    def get_clean_name(self, name):
        illegal = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']

        for i in illegal:
            if i in name:
                name = name.replace(i, '')
        return name

    def set_unique_name(self, col, name):
        if name == "":
            name = "New Project"
            return

        existing_names = []

        for i in col.items():
            existing_names.append(i[0])

        if name not in existing_names:
            self.name = name
            return

        # If name already exists in collection
        match = re.match(r'(.*)\.(\d{3,})', name)

        if match is None:
            stem, nbr = name, 1
        else:
            stem, nbr = match.groups()

        nbr_int = int(nbr)
        new_name = self.format_name(stem, nbr_int)

        while new_name in col:
            nbr_int += 1
            new_name = self.format_name(stem, nbr_int)
        self.name = new_name


class Room(PropertyGroup, CollectionMixIn):
    name: StringProperty(name="Room Name", default="", update=rename_room)
    og_name: StringProperty(name="Starting Room Name", default="")
    file_path: StringProperty(name="Room Filepath", default="", subtype='FILE_PATH')
    selected: BoolProperty(name="Room Selected", default=False)
    version: StringProperty(name="Version", default="")

    prop_id: StringProperty(name="Proposal ID", default="", update=update_room_props)
    prop_published: StringProperty(name="Proposal Published", default="", update=update_room_props)
    prop_published_utc: StringProperty(name="Proposal Published UTC", default="", update=update_room_props)
    
    prop_selected: BoolProperty(name="Room on Proposal", default=False, update=update_room_props)
    prop_thumbnail: StringProperty(name="Proposal Room Thumbnail", default="", update=update_room_props)
    prop_thumbnail_custom: StringProperty(name="Proposal Room Custom Thumbnail", default="", update=update_room_props)
    prop_thumbnail_custom_utc: StringProperty(name="Proposal Room Custom Thumbnail UTC", default="", update=update_room_props)
    prop_3d_prepared: StringProperty(name="Room 3D Prepared", default="", update=update_room_props)
    prop_3d_prepared_utc: StringProperty(name="Room 3D Prepared UTC", default="", update=update_room_props)
    prop_3d_exported: StringProperty(name="Room 3D Exported", default="", update=update_room_props)
    prop_3d_exported_utc: StringProperty(name="Room 3D Exported UTC", default="", update=update_room_props)
    prop_3d_exported_url: StringProperty(name="Room 3D Exported URL", default="", update=update_room_props)
    prop_3d_exported_uid: StringProperty(name="Room 3D Exported UID", default="", update=update_room_props)
    prop_3d_exported_acct: StringProperty(name="Room 3D Exported Account", default="", update=update_room_props)

    prop_room_label: StringProperty(name="Proposal Room Label", default="", maxlen=22, update=update_room_props)
    prop_room_estimate: StringProperty(name="Proposal Room Estimate", default="", update=update_room_props)
    prop_room_estimate_custom: StringProperty(name="Proposal Room Custom Estimate", default="", update=update_room_props)
    prop_room_ext_color_custom: StringProperty(name="Proposal Room Custom Ext Color", default="", update=update_room_props)
    prop_room_int_color_custom: StringProperty(name="Proposal Room Custom Int Color", default="", update=update_room_props)
    prop_room_trim_color_custom: StringProperty(name="Proposal Room Custom Trim Color", default="", update=update_room_props)
    prop_room_hardware_custom: StringProperty(name="Proposal Room Custom Hardware", default="", update=update_room_props)
    prop_room_rods_custom: StringProperty(name="Proposal Room Custom Rods", default="", update=update_room_props)
    prop_room_door_drawer_custom: StringProperty(name="Proposal Room Custom Door Drawer", default="", update=update_room_props)
    prop_room_boxes_custom: StringProperty(name="Proposal Room Custom Boxes", default="", update=update_room_props)
    prop_room_hamper_custom: StringProperty(name="Proposal Room Custom Hamper", default="", update=update_room_props)
    prop_room_accessories_custom: StringProperty(name="Proposal Room Custom Accessories", default="", update=update_room_props)
    prop_room_countertop_custom: StringProperty(name="Proposal Room Custom Countertop", default="", update=update_room_props)
    prop_room_backing_custom: StringProperty(name="Proposal Room Custom Backing", default="", update=update_room_props)
    prop_room_glass_custom: StringProperty(name="Proposal Room Custom Glass", default="", update=update_room_props)
    prop_room_notes: StringProperty(name="Proposal Room Notes", default="", maxlen=175, update=update_room_props)

    def init(self, name, path=None, project_index=None, save_room_file=True):
        wm = bpy.context.window_manager.sn_project
        # On initial load, project index won't work.
        col = wm.projects[project_index or wm.project_index].rooms
        super().init(col, name=name)
        self.og_name = self.name

        # Set file name
        self.file_name = self.get_clean_name(self.name)

        if path:
            self.file_path = path

        else:
            # Set filepath
            project = wm.projects[wm.project_index]
            proj_dir = os.path.join(project.dir_path, project.name)
            self.file_path = os.path.join(os.path.dirname(proj_dir), '{}.{}'.format(self.file_name, "blend"))

            # Save file to project dir
            if save_room_file:
                scene = sn_utils.get_main_scene()
                scene.sn_roombuilder.room_version = sn_utils.get_version_str()
                bpy.ops.wm.save_as_mainfile(filepath=self.file_path)

            wm.current_file_project = project.name
            wm.current_file_room = self.name

            self.update_project_xml(project)

        self.load_room_data()
  
    def update_project_xml(self, project):
        # write info to project file
        tree = ET.parse(project.file_path)
        root = tree.getroot()

        for elm in root.findall("Rooms"):
            # we want to save using relative path
            rel_loc = os.path.join(*self.file_path.split(os.sep)[-2:])
            elm_room = ET.Element("Room", {'name': self.name, 'path': rel_loc})
            elm_room.text = self.name
            elm.append(elm_room)
            # elm_selected = ET.Element("Room", {'selected': self.selected, 'path': rel_loc})
            # elm_selected.text = self.selected
            # elm.append(elm_selected)
            

        tree.write(project.file_path)

    def modify_room_data(self):
        wm = bpy.context.window_manager.sn_project
        project = wm.projects[wm.project_index]
        tree = ET.parse(project.file_path)
        root = tree.getroot()

        for rooms in root.findall("Rooms"):
            for room in rooms.findall("Room"):
                if room.attrib['name'] == self.name:
                    room.set('prop_id', str(self.prop_id))
                    room.set('prop_published', self.prop_published)
                    room.set('prop_published_utc', self.prop_published_utc)
                    room.set('prop_selected', str(self.prop_selected))
                    room.set('prop_thumbnail', self.prop_thumbnail)
                    room.set('prop_thumbnail_custom', self.prop_thumbnail_custom)
                    room.set('prop_thumbnail_custom_utc', self.prop_thumbnail_custom_utc)
                    room.set('prop_3d_prepared', self.prop_3d_prepared)
                    room.set('prop_3d_prepared_utc', self.prop_3d_prepared_utc)
                    room.set('prop_3d_exported', self.prop_3d_exported)
                    room.set('prop_3d_exported_utc', self.prop_3d_exported_utc)
                    room.set('prop_3d_exported_url', self.prop_3d_exported_url)
                    room.set('prop_3d_exported_uid', str(self.prop_3d_exported_uid))
                    room.set('prop_3d_exported_acct', self.prop_3d_exported_acct)

                    room.set('prop_room_label', self.prop_room_label)
                    room.set('prop_room_estimate', self.prop_room_estimate)
                    if self.prop_room_estimate_custom.strip() != "":
                        room.set('prop_room_estimate_custom', self.prop_room_estimate_custom)
                    else:
                        room.set('prop_room_estimate_custom', "")
                    room.set('prop_room_ext_color_custom', self.prop_room_ext_color_custom)
                    room.set('prop_room_int_color_custom', self.prop_room_int_color_custom)
                    room.set('prop_room_trim_color_custom', self.prop_room_trim_color_custom)
                    room.set('prop_room_hardware_custom', self.prop_room_hardware_custom)
                    room.set('prop_room_rods_custom', self.prop_room_rods_custom)
                    room.set('prop_room_door_drawer_custom', self.prop_room_door_drawer_custom)
                    room.set('prop_room_boxes_custom', self.prop_room_boxes_custom)
                    room.set('prop_room_hamper_custom', self.prop_room_hamper_custom)
                    room.set('prop_room_accessories_custom', self.prop_room_accessories_custom)
                    room.set('prop_room_countertop_custom', self.prop_room_countertop_custom)
                    room.set('prop_room_backing_custom', self.prop_room_backing_custom)
                    room.set('prop_room_glass_custom', self.prop_room_glass_custom)
                    room.set('prop_room_notes', self.prop_room_notes)
                       
        tree.write(project.file_path)

    def load_room_data(self):
        wm = bpy.context.window_manager.sn_project
        project = wm.projects[wm.project_index]
        tree = ET.parse(project.file_path)
        root = tree.getroot()

        for rooms in root.findall("Rooms"):
            for room in rooms.findall("Room"):
                if room.attrib['name'] == self.name:
                    if "prop_id" in room.attrib and room.get('prop_id') != "":
                        self.prop_id = room.get('prop_id')
                    if "prop_selected" in room.attrib and room.get('prop_selected') != "":
                        if room.get('prop_selected') == "True":
                            self.prop_selected = True
                        else:
                            self.prop_selected = False
                    if "prop_published" in room.attrib and room.get('prop_published') != "":
                        self.prop_published = room.get('prop_published')
                    if 'prop_published_utc' in room.attrib and room.get('prop_published_utc') != "":
                        self.prop_published_utc = room.get('prop_published_utc')
                    if "prop_thumbnail" in room.attrib and room.get('prop_thumbnail') != "":
                        self.prop_thumbnail = room.get('prop_thumbnail')
                    if "prop_thumbnail_custom" in room.attrib and room.get('prop_thumbnail_custom') != "":
                        self.prop_thumbnail_custom = room.get('prop_thumbnail_custom')
                    if "prop_thumbnail_custom_utc" in room.attrib and room.get('prop_thumbnail_custom_utc') != "":
                        self.prop_thumbnail_custom_utc = room.get('prop_thumbnail_custom_utc')
                    if "prop_3d_prepared" in room.attrib and room.get('prop_3d_prepared') != "":
                        self.prop_3d_prepared = room.get('prop_3d_prepared')
                    if "prop_3d_prepared_utc" in room.attrib and room.get('prop_3d_prepared_utc') != "":
                        self.prop_3d_prepared_utc = room.get('prop_3d_prepared_utc')
                    if "prop_3d_exported" in room.attrib and room.get('prop_3d_exported') != "":
                        self.prop_3d_exported = room.get('prop_3d_exported')
                    if "prop_3d_exported_utc" in room.attrib and room.get('prop_3d_exported_utc') != "":
                        self.prop_3d_exported_utc = room.get('prop_3d_exported_utc')
                    if "prop_3d_exported_url" in room.attrib and room.get('prop_3d_exported_url') != "":
                        self.prop_3d_exported_url = room.get('prop_3d_exported_url')
                    if "prop_3d_exported_uid" in room.attrib and room.get('prop_3d_exported_uid') != "":
                        self.prop_3d_exported_uid = room.get('prop_3d_exported_uid')
                    if "prop_3d_exported_acct" in room.attrib and room.get('prop_3d_exported_acct') != "":
                        self.prop_3d_exported_acct = room.get('prop_3d_exported_acct')
                    if "prop_room_label" in room.attrib and room.get('prop_room_label') != "":
                        self.prop_room_label = room.get('prop_room_label')
                    if "prop_room_estimate" in room.attrib and room.get('prop_room_estimate') != "":
                        self.prop_room_estimate = room.get('prop_room_estimate')
                    if "prop_room_estimate_custom" in room.attrib and room.get('prop_room_estimate_custom') != "":
                        self.prop_room_estimate_custom = "$" + room.get('prop_room_estimate_custom').replace("$","")

                    if "prop_room_ext_color_custom" in room.attrib and room.get('prop_room_ext_color_custom') != "":
                        self.prop_room_ext_color_custom = room.get('prop_room_ext_color_custom')
                    if "prop_room_int_color_custom" in room.attrib and room.get('prop_room_int_color_custom') != "":
                        self.prop_room_int_color_custom = room.get('prop_room_int_color_custom')
                    if "prop_room_trim_color_custom" in room.attrib and room.get('prop_room_trim_color_custom') != "":
                        self.prop_room_trim_color_custom = room.get('prop_room_trim_color_custom')
                    if "prop_room_hardware_custom" in room.attrib and room.get('prop_room_hardware_custom') != "":
                        self.prop_room_hardware_custom = room.get('prop_room_hardware_custom')
                    if "prop_room_rods_custom" in room.attrib and room.get('prop_room_rods_custom') != "":
                        self.prop_room_rods_custom = room.get('prop_room_rods_custom')
                    if "prop_room_door_drawer_custom" in room.attrib and room.get('prop_room_door_drawer_custom') != "":
                        self.prop_room_door_drawer_custom = room.get('prop_room_door_drawer_custom')
                    if "prop_room_boxes_custom" in room.attrib and room.get('prop_room_boxes_custom') != "":
                        self.prop_room_boxes_custom = room.get('prop_room_boxes_custom')
                    if "prop_room_hamper_custom" in room.attrib and room.get('prop_room_hamper_custom') != "":
                        self.prop_room_hamper_custom = room.get('prop_room_hamper_custom')
                    if "prop_room_accessories_custom" in room.attrib and room.get('prop_room_accessories_custom') != "":
                        self.prop_room_accessories_custom = room.get('prop_room_accessories_custom')
                    if "prop_room_countertop_custom" in room.attrib and room.get('prop_room_countertop_custom') != "":
                        self.prop_room_countertop_custom = room.get('prop_room_countertop_custom')
                    if "prop_room_backing_custom" in room.attrib and room.get('prop_room_backing_custom') != "":
                        self.prop_room_backing_custom = room.get('prop_room_backing_custom')
                    if "prop_room_glass_custom" in room.attrib and room.get('prop_room_glass_custom') != "":
                        self.prop_room_glass_custom = room.get('prop_room_glass_custom')    
                    if "prop_room_notes" in room.attrib and room.get('prop_room_notes') != "":
                        self.prop_room_notes = room.get('prop_room_notes')

    def set_filename(self):
        self.file_name = self.get_clean_name(self.name)

    def set_filepath(self):
        wm = bpy.context.window_manager.sn_project
        proj_filepath = wm.projects[wm.project_index].file_path
        self.file_path = os.path.join(os.path.dirname(proj_filepath), '{}.{}'.format(self.file_name, "blend"))


class Project(PropertyGroup, CollectionMixIn):
    name: StringProperty(name="Project Name", default="", update=rename_project)
    og_name: StringProperty(name="Starting Room Name", default="")
    file_path: StringProperty(name="Project File Path", default="", subtype='FILE_PATH')
    rooms: CollectionProperty(name="Rooms", type=Room)
    room_index: IntProperty(name="Room Index")

    project_id: IntProperty(name="Project ID", description="Project ID")
    customer_name: StringProperty(name="Customer Name",
                                  description="Customer Name",
                                  update=update_project_props)
    client_id: StringProperty(name="Client ID", description="Client ID", update=update_project_props)
    lead_id: StringProperty(name="Lead ID", description="Lead ID", update=update_project_props)
    project_address: StringProperty(name="Project Address",
                                    description="Project Address",
                                    update=update_project_props)
    city: StringProperty(name="City", description="City", update=update_project_props)
    state: StringProperty(name="State", description="State", update=update_project_props)
    zip_code: StringProperty(name="Zip Code", description="Zip Code", update=update_project_props)
    customer_phone_1: StringProperty(name="Customer Phone 1",
                                     description="Customer Phone 1",
                                     update=update_project_props)
    customer_phone_2: StringProperty(name="Customer Phone 2",
                                     description="Customer Phone 2",
                                     update=update_project_props)
    customer_email: StringProperty(name="Customer Email",
                                   description="Customer Email",
                                   update=update_project_props)
    project_notes: StringProperty(name="Project Notes",
                                  description="Project Notes",
                                  update=update_project_props)
    designer: StringProperty(name="Designer", description="Designer", update=update_project_props)
    design_date: StringProperty(name="Design Date", description="Design Date", update=update_project_props)
    
    prop_id: StringProperty(name="Proposal ID", default="", update=update_project_props)
    prop_published: StringProperty(name="Proposal Published", default="", update=update_project_props)
    prop_published_utc: StringProperty(name="Proposal Published UTC", default="", update=update_project_props)
    prop_status: StringProperty(name="Proposal Status", default="", update=update_project_props)


    def init(self, name, path=None):
        col = bpy.context.window_manager.sn_project.projects
        super().init(col, name=name)
        self.og_name = self.name

        self.create_dir()
        self.set_filename()
        proj_filepath = os.path.join(self.dir_path, ".snap", '{}.{}'.format(self.file_name, "ccp"))
        self.set_filepath(proj_filepath)

        # File path passed in
        if path:
            self.read_project_file()
        # File already exists in project directory
        elif os.path.exists(proj_filepath):
            self.read_project_file()
        else:
            project_id = self.get_id()
            self.project_id = project_id
            self.create_file(project_id)

    def create_dir(self):
        if not os.path.exists(self.dir_path):
            os.mkdir(self.dir_path)
        pm_utils.create_hidden_folder(self.dir_path)    

    def set_filename(self):
        self.file_name = self.get_clean_name(self.name)

    def set_filepath(self, proj_filepath):
        self.file_path = proj_filepath

    def get_id(self):
        addon_prefs = bpy.context.preferences.addons[__name__.split(".")[0]].preferences
        addon_prefs.project_id_count += 1
        bpy.ops.wm.save_userpref()
        return addon_prefs.project_id_count

    def get_lead_id(self):
        if self.lead_id:
            return self.lead_id

    def create_file(self, project_id):
        ccp = pm_utils.CCP()
        ccp.filename = self.file_name
        root = ccp.create_tree()
        project_info = ccp.add_element(root, 'ProjectInfo')

        ccp.add_element_with_text(project_info, "project_id", str(project_id))
        ccp.add_element_with_text(project_info, "name", self.name)
        ccp.add_element_with_text(project_info, "customer_name", "None")
        ccp.add_element_with_text(project_info, "client_id", "None")
        ccp.add_element_with_text(project_info, "lead_id", "None")
        ccp.add_element_with_text(project_info, "project_address", "None")
        ccp.add_element_with_text(project_info, "city", "None")
        ccp.add_element_with_text(project_info, "state", "None")
        ccp.add_element_with_text(project_info, "zip_code", "None")
        ccp.add_element_with_text(project_info, "customer_phone_1", "None")
        ccp.add_element_with_text(project_info, "customer_phone_2", "None")
        ccp.add_element_with_text(project_info, "customer_email", "None")
        ccp.add_element_with_text(project_info, "project_notes", "None")
        ccp.add_element_with_text(project_info, "designer", "None")
        ccp.add_element_with_text(project_info, "design_date", "None")
        ccp.add_element_with_text(project_info, "prop_id", "None")
        ccp.add_element_with_text(project_info, "prop_published", "None")
        ccp.add_element_with_text(project_info, "prop_published_utc", "None")
        ccp.add_element_with_text(project_info, "prop_status", "None")

        ccp.add_element(root, 'Rooms')

        ccp.write(os.path.join(self.dir_path, ".snap"))

    def modify_project_file(self):
        ccp = pm_utils.CCP()
        tree = ET.parse(self.file_path)
        root = tree.getroot()

        for elm in root.findall("ProjectInfo"):
            items = list(elm)
            missing_lead_id = True
            missing_prop_id = True
            missing_prop_published = True
            missing_prop_pubhlished_utc = True
            missing_prop_status = True

            for item in items:
                if item.tag == 'customer_name':
                    item.text = self.customer_name

                if item.tag == 'client_id':
                    item.text = self.client_id
                
                if item.tag == 'lead_id':
                    missing_lead_id = False
                    item.text = self.lead_id

                if item.tag == 'project_address':
                    item.text = self.project_address

                if item.tag == 'city':
                    item.text = self.city

                if item.tag == 'state':
                    item.text = self.state

                if item.tag == 'zip_code':
                    item.text = self.zip_code

                if item.tag == 'customer_phone_1':
                    item.text = self.customer_phone_1

                if item.tag == 'customer_phone_2':
                    item.text = self.customer_phone_2

                if item.tag == 'customer_email':
                    item.text = self.customer_email

                if item.tag == 'project_notes':
                    item.text = self.project_notes

                if item.tag == 'designer':
                    item.text = self.designer

                if item.tag == 'design_date':
                    item.text = self.design_date

                if item.tag == 'prop_id':
                    missing_prop_id = False
                    item.text = self.prop_id

                if item.tag == 'prop_published':
                    missing_prop_published = False
                    if item.text != "":
                        item.text = self.prop_published

                if item.tag == 'prop_published_utc':
                    missing_prop_pubhlished_utc = False
                    if item.text != "":
                        item.text = self.prop_published_utc

                if item.tag == 'prop_status':
                    missing_prop_status = False
                    if item.text != "":
                        item.text = self.prop_status

            if missing_lead_id:
                ccp.add_element_with_text(elm, "lead_id", self.lead_id)

            if missing_prop_id:
                ccp.add_element_with_text(elm, "prop_id", self.prop_id)

            if missing_prop_published:
                ccp.add_element_with_text(elm, "prop_published", self.prop_published)
            
            if missing_prop_pubhlished_utc:
                ccp.add_element_with_text(elm, "prop_published_utc", self.prop_published_utc)

            if missing_prop_status:
                ccp.add_element_with_text(elm, "prop_status", self.prop_status)

        tree.write(self.file_path)

    def read_project_file(self):
        tree = ET.parse(self.file_path)
        root = tree.getroot()

        for elm in root.findall("ProjectInfo"):
            items = list(elm)

            for item in items:
                if item.text:

                    if item.tag == 'project_id':
                        self.project_id = int(item.text)

                    if item.tag == 'customer_name':
                        self.customer_name = item.text

                    if item.tag == 'client_id':
                        self.client_id = item.text

                    if item.tag == 'lead_id':
                        self.lead_id = item.text

                    if item.tag == 'project_address':
                        self.project_address = item.text

                    if item.tag == 'city':
                        self.city = item.text

                    if item.tag == 'state':
                        self.state = item.text

                    if item.tag == 'zip_code':
                        self.zip_code = item.text

                    if item.tag == 'customer_phone_1':
                        self.customer_phone_1 = item.text

                    if item.tag == 'customer_phone_2':
                        self.customer_phone_2 = item.text

                    if item.tag == 'customer_email':
                        self.customer_email = item.text

                    if item.tag == 'project_notes':
                        self.project_notes = item.text

                    if item.tag == 'designer':
                        self.designer = item.text

                    if item.tag == 'design_date':
                        self.design_date = item.text

                    if item.tag == 'prop_id':
                        self.prop_id = item.text

                    if item.tag == 'prop_published':
                        self.prop_published = item.text

                    if item.tag == 'prop_published_utc':
                        self.prop_published_utc = item.text

    def draw_room_info(self, layout):
        active_room_path = self.rooms[self.room_index].file_path
        col = layout.column(align=True)
        col.template_list("SNAP_UL_Rooms", "", self, "rooms", self, "room_index", maxrows=5)
        row = col.row(align=True)
        row.operator(
            "project_manager.open_room",
            text="Open Room",
            icon='FILE_TICK').file_path = active_room_path

        row.operator(
            "product_manager.copy_room",
            text="Copy Room",
            icon='PACKAGE').file_path = active_room_path

        row.menu('SNAP_MT_Room_Tools', text="", icon='DOWNARROW_HLT')

    def draw_render_info(self, layout):
        box = layout.box()
        box.label(text="RENDERS HERE")

    def draw(self, layout):
        if len(self.rooms) > 0:
            self.draw_room_info(layout)
        else:
            box = layout.box()
            box.label(text="No rooms", icon='ERROR')
            row = layout.row()
            row.operator("project_manager.import_room", text="Import Room", icon='IMPORT')

    def add_room(self, name, project_index=None, save_room_file=True):
        room = self.rooms.add()
        room.init(name, project_index=project_index, save_room_file=save_room_file)
        return room

    def add_room_from_file(self, name, path, project_index=None):
        room = self.rooms.add()
        room.init(name, path, project_index=project_index)
        return room


class WM_PROPERTIES_Projects(PropertyGroup):
    projects: CollectionProperty(name="Projects", type=Project)
    project_index: IntProperty(name="Project Index")
    current_file_room: StringProperty(name="Current File Room", description="Current blend file room name")
    current_file_project: StringProperty(name="Current File Project", description="Current blend file project name")
    use_compact_ui: BoolProperty(name="Use Compact Projects UI Panel", default=False)
    projects_loaded: BoolProperty(name="Projects Loaded", default=False, description="All projects have been loaded")

    def get_project(self):
        return self.projects[self.project_index]

    @classmethod
    def register(cls):

        bpy.types.WindowManager.sn_project = PointerProperty(
            name="Project Settings",
            description="SNaP Project Manager Properties",
            type=cls,
        )


classes = (
    Room,
    Project,
    WM_PROPERTIES_Projects
)


register, unregister = bpy.utils.register_classes_factory(classes)
