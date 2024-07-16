

import os

import bpy
from bpy.types import Panel
from bpy.types import Menu, UIList

from . import pm_utils
from snap import sn_utils
import snap
import datetime

class SNAP_UL_Projects(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        project = context.window_manager.sn_project.get_project()
        layout.label(text="", icon='FILEBROWSER')
        layout.prop(item, 'name', text='', emboss=False)
        if item.name == project.name:
            layout.popover("SNAP_PT_Project_Info", icon='INFO', text="")
            layout.operator("project_manager.delete_project", text="", icon='X', emboss=True).index = index


class SNAP_UL_Rooms(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        project = context.window_manager.sn_project.get_project()
        room = project.rooms[project.room_index]
        layout.label(text="", icon='SNAP_PEEL_OBJECT')
        layout.prop(item, 'name', text='', emboss=False)
        if item.name == room.name:
            if bpy.data.is_saved:
                directory, file_name = os.path.split(bpy.data.filepath)
                file_name = os.path.splitext(file_name)[0]  # Remove extension

                # If this item is the open file, show the room info popover
                if file_name == item.name:
                    layout.popover("SNAP_PT_Room_Info", icon='INFO', text="")

            layout.operator("project_manager.delete_room", text="", icon='X', emboss=True).index = index


class SNAP_MT_Project_Tools(Menu):
    bl_label = "Project Tools"

    def draw(self, context):
        layout = self.layout
        layout.operator("sn_library.open_browser_window",
                        text="Open Projects Location in Browser",
                        icon='FILE_FOLDER').path = pm_utils.get_project_dir()

        layout.operator("project_manager.unarchive_project",
                        text="Open Archived Projects Location in Browser",
                        icon='FILE_FOLDER').filepath = pm_utils.get_archive_dir()


class SNAP_MT_Room_Tools(Menu):
    bl_label = "Room Tools"

    def draw(self, context):
        layout = self.layout
        layout.operator("project_manager.import_room", text="Import Room", icon='IMPORT')


class SNAP_PT_Project_Popup_Menu(Panel):
    bl_label = "Project Popup"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'HEADER'
    bl_label = "Presets"
    path_menu = Menu.path_menu

    @classmethod
    def draw_panel_header(cls, layout):
        layout.emboss = 'PULLDOWN_MENU'
        layout.popover(
            panel="SNAP_PT_Project_Tools",
            icon='COLLAPSEMENU',
            text="")

    def draw(self, context):
        layout = self.layout
        layout.emboss = 'NONE'
        layout.operator_context = 'EXEC_DEFAULT'
        Menu.draw_preset(self, context)


class SNAP_PT_Projects(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Projects"
    bl_order = 0

    props = None

    def draw_header_preset(self, _context):
        SNAP_PT_Project_Popup_Menu.draw_panel_header(self.layout)

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='INFO')

    def draw_common_ops(self, box):
        row = box.row(align=True)
        row.operator("project_manager.prepare_proj_xml", icon='EXPORT')

    def draw(self, context):
        wm = bpy.context.window_manager.sn_project
        projects = wm.projects
        layout = self.layout
        box = layout.box()

        if len(projects) > 0:
            active_project = wm.projects[wm.project_index]

            if wm.use_compact_ui:
                row_1 = box.row()
                col = row_1.column(align=True)
                row_2 = col.row(align=True)
                row_2.operator("project_manager.create_project", icon='FILE_NEW')
                row_2.menu('SNAP_MT_Project_Tools', text="", icon='DOWNARROW_HLT')
                col.template_list("SNAP_UL_Projects", "", wm, "projects", wm, "project_index", maxrows=5)
                self.draw_common_ops(col)
                active_project.draw(row_1)
            else:
                col = box.column(align=True)
                row = col.row(align=True)
                row.operator("project_manager.create_project", icon='FILE_NEW')
                row.operator("project_manager.copy_project", text="Copy Project", icon='DUPLICATE')
                row.menu('SNAP_MT_Project_Tools', text="", icon='DOWNARROW_HLT')
                if(len(projects) < 5):
                    col.template_list("SNAP_UL_Projects", "", wm, "projects", wm, "project_index", rows=len(projects))
                    self.draw_common_ops(col)
                    active_project = wm.projects[wm.project_index]
                    col.separator()
                    active_project.draw(col)
                else:
                    col.template_list("SNAP_UL_Projects", "", wm, "projects", wm, "project_index", maxrows=5)
                    self.draw_common_ops(col)
                    col.separator()
                    active_project = wm.projects[wm.project_index]
                    active_project.draw(col)
        else:
            row = box.row(align=True)
            row.operator("project_manager.create_project", icon='FILE_NEW')
            row.menu('SNAP_MT_Project_Tools', text="", icon='DOWNARROW_HLT')


class SNAP_PT_Project_Tools(Panel):
    bl_space_type = 'INFO'
    bl_label = "Project Tools"
    bl_region_type = 'HEADER'
    bl_ui_units_x = 10

    def draw(self, context):
        wm = context.window_manager.sn_project
        layout = self.layout
        layout.prop(wm, "use_compact_ui")


class SNAP_PT_Project_Info(Panel):
    bl_space_type = 'INFO'
    bl_label = "Project Info"
    bl_region_type = 'HEADER'
    bl_ui_units_x = 22

    def draw(self, context):
        proj_props = context.window_manager.sn_project.get_project()
        layout = self.layout
        layout.label(text="Project Info")
        box = layout.box()
        col = box.column()
        col.prop(proj_props, 'lead_id')
        col.prop(proj_props, 'customer_name')
        col.prop(proj_props, 'project_address')
        col.prop(proj_props, 'city')
        col.prop(proj_props, 'state')
        col.prop(proj_props, 'zip_code')
        col.prop(proj_props, 'customer_phone_1')
        col.prop(proj_props, 'customer_phone_2')
        col.prop(proj_props, 'customer_email')
        col.prop(proj_props, 'project_notes')
        col.prop(proj_props, 'designer')
        col.prop(proj_props, 'design_date')


class SNAP_PT_Room_Info(Panel):
    bl_space_type = 'INFO'
    bl_label = "Room Info"
    bl_region_type = 'HEADER'
    bl_ui_units_x = 7

    def draw(self, context):
        layout = self.layout
        layout.label(text="Room Info")
        box = layout.box()
        row = box.row()
        text = sn_utils.get_room_version()

        if not text:
            text = "Unknown"

        row.label(text=f"Room Version: {text}")


class SNAP_PT_Proposal_Room_Info(Panel):
    bl_space_type = 'INFO'
    bl_label = "Proposal Room Info"
    bl_region_type = 'HEADER'
    bl_ui_units_x = 20

    def utc_to_local_datetime_string(self, datetime_string):
        try:
            utc_datetime = datetime.datetime.strptime(datetime_string, "%Y-%m-%d %H:%M:%S.%f")
            local_datetime = utc_datetime.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
            return local_datetime.strftime("%m/%d/%Y %I:%M %p")
        except ValueError:
            return "N/A"
        
    def draw_proposal_datetime(self, layout, label_text, datetime_string, prop_datetime):
        row = layout.row()
        col = row.column()
        col.scale_x = 0.7
        icon = 'BLANK1'

        if datetime_string != "N/A" and prop_datetime != "N/A":
            try:
                if datetime.datetime.strptime(prop_datetime, '%m/%d/%Y %I:%M %p') < datetime.datetime.strptime(datetime_string, '%m/%d/%Y %I:%M %p'):
                    icon = 'ERROR'
            except ValueError:
                pass

        col.label(text=label_text)
        col = row.column()
        col.label(text=datetime_string,icon=icon)

    def draw(self, context):
        project = context.window_manager.sn_project.get_project()
        room_props = project.rooms[project.room_index]
        layout = self.layout
        layout.label(text=room_props.name + " Proposal Info")
        box = layout.box()
        col = box.column()

        published_datetime_string = self.utc_to_local_datetime_string(room_props.prop_published_utc)

        datetime_string = self.utc_to_local_datetime_string(room_props.prop_thumbnail_custom_utc)
        self.draw_proposal_datetime(col, "     Custom Thumbnail: ", datetime_string, published_datetime_string)

        datetime_string = self.utc_to_local_datetime_string(room_props.prop_3d_prepared_utc)
        self.draw_proposal_datetime(col, "      Prepare for Export: ", datetime_string, published_datetime_string)

        datetime_string = self.utc_to_local_datetime_string(room_props.prop_3d_exported_utc)
        self.draw_proposal_datetime(col, "Export to Classy Portal: ", datetime_string, published_datetime_string)

        datetime_string = self.utc_to_local_datetime_string(room_props.prop_published_utc)
        self.draw_proposal_datetime(col, "          Room Published: ", datetime_string, published_datetime_string)

        layout.label(text=room_props.name + " Custom Text")
        box = layout.box()
        col = box.column()
 
        col.prop(room_props, 'prop_room_label', text="Room Label")
        col.prop(room_props, 'prop_room_estimate_custom', text="Room Estimate")
        col.prop(room_props, 'prop_room_ext_color_custom', text="Exterior Color")
        col.prop(room_props, 'prop_room_int_color_custom', text="Interior Color")
        col.prop(room_props, 'prop_room_trim_color_custom', text="Trim Color")
        col.prop(room_props, 'prop_room_hardware_custom', text="Hardware")
        col.prop(room_props, 'prop_room_rods_custom', text="Rods")
        col.prop(room_props, 'prop_room_door_drawer_custom', text="Doors/Drawers")
        col.prop(room_props, 'prop_room_boxes_custom', text="Boxes")
        col.prop(room_props, 'prop_room_hamper_custom', text="Hamper")
        col.prop(room_props, 'prop_room_accessories_custom', text="Accessories")
        col.prop(room_props, 'prop_room_countertop_custom', text="Countertop")
        col.prop(room_props, 'prop_room_backing_custom', text="Backing")
        col.prop(room_props, 'prop_room_glass_custom', text="Glass")
        col.prop(room_props, 'prop_room_notes', text="Notes")


class VIEW_MT_Proposal_Tools(bpy.types.Menu):
    bl_label = "Elevation Scene Options"

    def draw(self, context):
        layout = self.layout
        layout.operator("project_manager.proposal_select_all_rooms",
                        text="Select All", icon='CHECKBOX_HLT').select_all = True
        layout.operator("project_manager.proposal_select_all_rooms",
                        text="Deselect All", icon='CHECKBOX_DEHLT').select_all = False
        
        layout.separator()

        layout.operator('project_manager.proposal_delete_custom_thumbnail_poll',
                        text="Reset Room Thumbnail",icon='RESTRICT_RENDER_ON')

        layout.operator('project_manager.proposal_delete_prepare_3d_poll',
                        text="Clear Room Preparation",icon='X')

        layout.operator('project_manager.proposal_delete_export_3d_poll',
                        text="Clear 3D Upload",icon='X')

        layout.operator('project_manager.proposal_delete_all_progress_poll',
                        text="Clear All Room Progress",icon='X')
        
        layout.separator()

        layout.operator('project_manager.proposal_copy_url',
                        text="Copy Proposal URL to Clipboard", icon='COPYDOWN')
        
        layout.operator('project_manager.proposal_copy_link',
                        text="Copy Proposal Link to Clipboard", icon='COPYDOWN')

        layout.separator()

        layout.operator('project_manager.proposal_delete_published_poll',
                        text="Delete Published Proposal", icon='X')

    
class SNAP_UL_Proposal_Rooms(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        project = context.window_manager.sn_project.get_project()
        room = project.rooms[project.room_index]
        layout.label(text=item.name, icon='SNAP_PEEL_OBJECT')
        # layout.prop(item, 'name', text='', emboss=False)

        directory, file_name = os.path.split(bpy.data.filepath)
        file_name = os.path.splitext(file_name)[0]  # Remove extension
        props = None

        if item.name == room.name:
            layout.popover("SNAP_PT_Proposal_Room_Info", icon='INFO', text="")
        else:
            layout.label(text='', icon='BLANK1')

        if file_name == item.name and bpy.data.is_saved:
            if item.prop_thumbnail_custom and item.prop_thumbnail_custom == "Started":
                props = layout.operator('project_manager.create_room_custom_thumbnail',text="",icon='FULLSCREEN_ENTER')
                props.active_room = item.name
            else:
                props = layout.operator('project_manager.start_room_custom_thumbnail',text="",icon='RESTRICT_RENDER_OFF')
                props.active_room = item.name
        else:
            layout.label(text='', icon='BLANK1')

        if item.prop_thumbnail_custom and item.prop_thumbnail_custom != "":
            # layout.label(text='',icon='IMAGE_PLANE')
            props = layout.operator('project_manager.view_room_thumbnail',text="",icon='IMAGE_PLANE')
            props.active_room = item.name
        elif item.prop_thumbnail and item.prop_thumbnail != "":
            # layout.label(text='',icon='IMAGE_DATA')
            props = layout.operator('project_manager.view_room_thumbnail',text="",icon='IMAGE_DATA')
            props.active_room = item.name
        else:
            layout.label(text='',icon='BLANK1')

        if item.prop_3d_prepared and item.prop_3d_prepared == "True":
            layout.label(text='',icon='FILE_BLEND')
        else:
            layout.label(text='',icon='BLANK1')

        if item.prop_3d_exported and item.prop_3d_exported == "True":
            layout.label(text='',icon='CUBE')
        else:
            layout.label(text='',icon='BLANK1')

        layout.prop(item, 'prop_selected', text='')


class SNAP_PT_Project_Proposal(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Project Proposal"
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 7

    props = None
    temp_label = "Test Label"

    @classmethod
    def poll(cls, context):
        prefs = bpy.context.preferences.addons["snap"].preferences
        if prefs.enable_project_proposal_panel and prefs.project_proposal_password == "Cla$$yProposals123":
            return True
        else:
            return False
        # return True

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='GREASEPENCIL')

    def draw(self, context):
        project = context.window_manager.sn_project.get_project()

        layout = self.layout
        col = layout.column(align=True)
        box = col.box()
        row = box.row(align=True)

        row.operator('project_manager.proposal_prepare_3d_poll',text="Prepare Room",icon='FILE_BLEND')
        row.operator('project_manager.proposal_export_3d_poll',text="Generate 3D",icon='CUBE')

        box = layout.box()
        row = box.row(align=True)
        col = row.column(align=True)

        project = context.window_manager.sn_project.get_project()
        col.template_list("SNAP_UL_Proposal_Rooms", "", project, "rooms", project, "room_index", rows=1, type="DEFAULT")

        if project.lead_id.strip() == "" or project.lead_id == "None":
            row=box.row(align=True)
            row.label(text="Warning:  Project Lead ID required to generate 3Ds", icon = 'ERROR')

        row = box.row(align=True)
        if project.prop_status != "":
            row.label(text="Status: " + project.prop_status, icon='PREFERENCES')
        else:
            row.label(text="Status: Idle", icon='PREFERENCES')

        row = box.row(align=True)
        if project.prop_published != "" and project.prop_published != "None":
            row.operator('project_manager.proposal_copy_link',text="",icon='COPYDOWN')
            row.operator('project_manager.proposal_view',text="",icon='HIDE_OFF')
            row.operator('project_manager.proposal_build_poll',text="Update Published Proposal",icon='URL')
        else:
            row.operator('project_manager.proposal_build_poll',text="Publish Proposal",icon='URL')

        row.menu('VIEW_MT_Proposal_Tools', text="", icon='DOWNARROW_HLT')

classes = (
    SNAP_UL_Projects,
    SNAP_UL_Rooms,
    SNAP_MT_Project_Tools,
    SNAP_PT_Project_Popup_Menu,
    SNAP_PT_Projects,
    SNAP_PT_Project_Tools,
    SNAP_PT_Project_Info,
    SNAP_PT_Room_Info,
    SNAP_MT_Room_Tools,
    SNAP_PT_Proposal_Room_Info,
    VIEW_MT_Proposal_Tools,
    SNAP_UL_Proposal_Rooms,
    SNAP_PT_Project_Proposal,
)

register, unregister = bpy.utils.register_classes_factory(classes)
