import os

import bpy
from bpy.types import PropertyGroup
from bpy.props import (
    StringProperty,
    BoolProperty,
    IntProperty,
    CollectionProperty,
    PointerProperty,
    FloatProperty,
    EnumProperty
)

from snap import sn_paths


def render_material_exists(material_name):
    materials_dir = sn_paths.CLOSET_MATERIAL_DIR
    search_directory = os.path.join(materials_dir, "Closet Materials")
    search_directory_v2 = os.path.join(materials_dir, "Closet Materials V2")
    mat_exists = False

    if os.path.isdir(search_directory_v2):
        files = os.listdir(search_directory_v2)
        if material_name + ".blend" in files:
            mat_exists = True

    if mat_exists:
        if os.path.isdir(search_directory):
            files = os.listdir(search_directory)
            if material_name + ".blend" in files:
                mat_exists = True

    return mat_exists


class ColorMixIn:
    has_render_mat: BoolProperty(name="Has Rendering Material")
    oversize_max_len: IntProperty(name="Oversize Material Max Length", default=0)

    def render_material_exists(self, material_name):
        cls_type = self.bl_rna.name

        if cls_type in ("EdgeColor", "MaterialColor", "StainColor", "PaintColor"):
            snap_db_mat_dir = sn_paths.CLOSET_MATERIAL_DIR
            search_directory = snap_db_mat_dir

        elif cls_type == "CountertopColor":
            countertop_mat_dir = sn_paths.COUNTERTOP_MATERIAL_DIR
            search_directory = countertop_mat_dir

        mat_exists = False

        if os.path.isdir(search_directory):
            files = os.listdir(search_directory)
            if material_name + ".blend" in files:
                mat_exists = True

        if not mat_exists:
            if os.path.isdir(sn_paths.CLOSET_MATERIAL_LEGACY_DIR):
                files = os.listdir(sn_paths.CLOSET_MATERIAL_LEGACY_DIR)
                if material_name + ".blend" in files:
                    mat_exists = True

        return mat_exists

    def check_render_material(self):
        if self.render_material_exists(self.name):
            self.has_render_mat = True
        else:
            self.has_render_mat = False

    def get_icon(self):
        if self.has_render_mat:
            return 'RADIOBUT_OFF'
        else:
            return 'ERROR'


class EdgeColor(PropertyGroup, ColorMixIn):
    color_code: IntProperty()
    description: StringProperty()

    def draw(self, layout):
        pass


class EdgeType(PropertyGroup):
    description: StringProperty()
    type_code: IntProperty()
    colors: CollectionProperty(type=EdgeColor)

    def set_color_index(self, index):
        scene_props = bpy.context.scene.closet_materials
        scene_props.edge_color_index = index

    def get_edge_color(self):
        scene_props = bpy.context.scene.closet_materials
        return self.colors[scene_props.edge_color_index]

    def get_inventory_edge_name(self):
        return "EB {} {}".format(self.name, self.type_code)    

    def draw(self, layout):
        color = self.get_edge_color()

        row = layout.row()
        split = row.split(factor=0.25)
        split.label(text="Color:")
        split.menu(
            "SNAP_MATERIAL_MT_Edge_Colors",
            text=color.name,
            icon='RADIOBUT_ON' if color.has_render_mat else 'ERROR')

        if not color.has_render_mat:
            row = layout.row()
            split = row.split(factor=0.25)
            split.label(text="")
            box = split.box()
            row = box.row()
            row.label(text="Missing render material.", icon='ERROR')   


class Edges(PropertyGroup):
    edge_types: CollectionProperty(type=EdgeType)

    def set_type_index(self, index):
        scene_props = bpy.context.scene.closet_materials
        scene_props.edge_type_index = index
        scene_props.set_default_edge_color()

    def get_edge_type(self):
        scene_props = bpy.context.scene.closet_materials
        return self.edge_types[scene_props.edge_type_index]

    def get_edge_color(self):
        return self.get_edge_type().get_edge_color()

    def draw(self, layout):
        box = layout.box()
        box.label(text="Edge Selection:")
        scene_props = bpy.context.scene.closet_materials

        if scene_props.edge_discontinued_color:
            warning_box = box.box()
            msg = '"{}" is no longer available to order!'.format(scene_props.edge_discontinued_color)
            warning_box.label(text=msg, icon='ERROR')

        if len(self.edge_types) > 0:
            row = box.row()
            split = row.split(factor=0.25)
            split.label(text="Type:")
            split.menu('SNAP_MATERIAL_MT_Edge_Types', text=self.get_edge_type().name, icon='RADIOBUT_ON')
            self.get_edge_type().draw(box)

        else:
            row = box.row()
            row.label(text="None", icon='ERROR')


class DoorDrawerEdgeType(PropertyGroup):   
    description: StringProperty()
    type_code: IntProperty()
    colors: CollectionProperty(type=EdgeColor)

    def set_color_index(self, index):
        scene_props = bpy.context.scene.closet_materials
        scene_props.door_drawer_edge_color_index = index

    def get_edge_color(self):
        scene_props = bpy.context.scene.closet_materials
        try:
            return self.colors[scene_props.door_drawer_edge_color_index]
        except IndexError:
            return self.colors[-1]

    def get_inventory_edge_name(self):
        return "EB {} {}".format(self.name, self.type_code)    

    def draw(self, layout):
        color = self.get_edge_color()

        row = layout.row()
        split = row.split(factor=0.25)
        split.label(text="Color:")            
        split.menu(
            "SNAP_MATERIAL_MT_Door_Drawer_Edge_Colors",
            text=color.name,
            icon='RADIOBUT_ON' if color.has_render_mat else 'ERROR')

        if not color.has_render_mat:
            row = layout.row()
            split = row.split(factor=0.25)
            split.label(text="")             
            box = split.box()
            row = box.row()
            row.label(text="Missing render material.", icon='ERROR')   


class DoorDrawerEdges(PropertyGroup):
    edge_types: CollectionProperty(type=DoorDrawerEdgeType)

    def set_type_index(self, index):
        scene_props = bpy.context.scene.closet_materials
        scene_props.door_drawer_edge_type_index = index
        scene_props.set_default_door_drawer_edge_color()

    def get_edge_type(self):
        scene_props = bpy.context.scene.closet_materials
        return self.edge_types[scene_props.door_drawer_edge_type_index]

    def get_edge_color(self):
        return self.get_edge_type().get_edge_color()        

    def draw(self, layout):
        box = layout.box()
        box.label(text="Edge Selection:")
        scene_props = bpy.context.scene.closet_materials

        if scene_props.dd_edge_discontinued_color:
            warning_box = box.box()
            msg = '"{}" is no longer available to order!'.format(scene_props.dd_edge_discontinued_color)
            warning_box.label(text=msg, icon='ERROR')

        if len(self.edge_types) > 0:
            row = box.row()
            split = row.split(factor=0.25)
            split.label(text="Type:")
            split.menu('SNAP_MATERIAL_MT_Door_Drawer_Edge_Types', text=self.get_edge_type().name, icon='RADIOBUT_ON')
            self.get_edge_type().draw(box)

        else:
            row = box.row()
            row.label(text="None", icon='ERROR')


class SecondaryEdgeType(PropertyGroup):   
    description: StringProperty()
    type_code: IntProperty()
    colors: CollectionProperty(type=EdgeColor)

    def set_color_index(self, index):
        scene_props = bpy.context.scene.closet_materials
        scene_props.secondary_edge_color_index = index

    def get_edge_color(self):
        scene_props = bpy.context.scene.closet_materials
        return self.colors[scene_props.secondary_edge_color_index]         

    def get_inventory_edge_name(self):
        return "EB {} {}".format(self.name, self.type_code)          

    def draw(self, layout):
        color = self.get_edge_color()

        row = layout.row()
        split = row.split(factor=0.25)
        split.label(text="Color:")            
        split.menu(
            "SNAP_MATERIAL_MT_Secondary_Edge_Colors",
            text=color.name,
            icon='RADIOBUT_ON' if color.has_render_mat else 'ERROR')

        if not color.has_render_mat:
            row = layout.row()
            split = row.split(factor=0.25)
            split.label(text="")             
            box = split.box()
            row = box.row()
            row.label(text="Missing render material.", icon='ERROR') 


class SecondaryEdges(PropertyGroup):
    edge_types: CollectionProperty(type=SecondaryEdgeType)

    def set_type_index(self, index):
        scene_props = bpy.context.scene.closet_materials
        scene_props.secondary_edge_type_index = index
        scene_props.set_default_secondary_edge_color()

    def get_edge_type(self):
        scene_props = bpy.context.scene.closet_materials
        return self.edge_types[scene_props.secondary_edge_type_index]

    def get_edge_color(self):
        return self.get_edge_type().get_edge_color()

    def has_render_mat(self):
        return self.get_edge_type().has_render_mat

    def draw(self, layout):
        box = layout.box()
        box.label(text="Cleat Edge Selection:")
        scene_props = bpy.context.scene.closet_materials

        if scene_props.cleat_edge_discontinued_color:
            warning_box = box.box()
            msg = '"{}" is no longer available to order!'.format(scene_props.cleat_edge_discontinued_color)
            warning_box.label(text=msg, icon='ERROR')

        if len(self.edge_types) > 0:
            row = box.row()
            split = row.split(factor=0.25)
            split.label(text="Type:")
            split.menu('SNAP_MATERIAL_MT_Secondary_Edge_Types', text=self.get_edge_type().name, icon='RADIOBUT_ON')
            self.get_edge_type().draw(box)

        else:
            row = box.row()
            row.label(text="None", icon='ERROR')        


class MaterialColor(PropertyGroup, ColorMixIn):
    description: StringProperty()
    color_code: IntProperty()
    two_sided_display_name: StringProperty()

    def draw(self, layout):
        pass


class MaterialType(PropertyGroup):
    description: StringProperty()
    type_code: IntProperty()
    colors: CollectionProperty(type=MaterialColor)

    def set_color_index(self, index):
        scene_props = bpy.context.scene.closet_materials
        mat_type = scene_props.materials.get_mat_type()

        if mat_type.name == "Solid Color Smooth Finish":
            scene_props.solid_color_index = index
        if mat_type.name == "Grain Pattern Smooth Finish":
            scene_props.grain_color_index = index
        if mat_type.name == "Solid Color Textured Finish":
            scene_props.solid_tex_color_index = index
        if mat_type.name == "Grain Pattern Textured Finish":
            scene_props.grain_tex_color_index = index
        if mat_type.name == "Linen Pattern Linen Finish":
            scene_props.linen_color_index = index
        if mat_type.name == "Solid Color Matte Finish":
            scene_props.matte_color_index = index
        if mat_type.name == "Garage Material":
            scene_props.garage_color_index = index
        if mat_type.name == "Oversized Material":
            scene_props.oversized_color_index = index

    def get_color_index(self):
        scene_props = bpy.context.scene.closet_materials
        mat_type = scene_props.materials.get_mat_type()

        if mat_type.name == "Solid Color Smooth Finish":
            return scene_props.solid_color_index
        if mat_type.name == "Grain Pattern Smooth Finish":
            return scene_props.grain_color_index
        if mat_type.name == "Solid Color Textured Finish":
            return scene_props.solid_tex_color_index
        if mat_type.name == "Grain Pattern Textured Finish":
            return scene_props.grain_tex_color_index
        if mat_type.name == "Linen Pattern Linen Finish":
            return scene_props.linen_color_index
        if mat_type.name == "Solid Color Matte Finish":
            return scene_props.matte_color_index
        if mat_type.name == "Garage Material":
            return scene_props.garage_color_index
        if mat_type.name == "Oversized Material":
            return scene_props.oversized_color_index

    def get_mat_color(self):
        scene_props = bpy.context.scene.closet_materials
        if self.name == "Upgrade Options":
            upgrade_type = scene_props.upgrade_options.get_type()
            if upgrade_type.name == "Paint":
                return scene_props.paint_colors[scene_props.paint_color_index]
            else:
                return scene_props.stain_colors[scene_props.stain_color_index]

        if self.name == "Solid Color Smooth Finish":
            return self.colors[scene_props.solid_color_index]
        if self.name == "Grain Pattern Smooth Finish":
            return self.colors[scene_props.grain_color_index]
        if self.name == "Solid Color Textured Finish":
            return self.colors[scene_props.solid_tex_color_index]
        if self.name == "Grain Pattern Textured Finish":
            return self.colors[scene_props.grain_tex_color_index]
        if self.name == "Linen Pattern Linen Finish":
            return self.colors[scene_props.linen_color_index]
        if self.name == "Solid Color Matte Finish":
            return self.colors[scene_props.matte_color_index]
        if self.name == "Garage Material":
            return self.colors[scene_props.garage_color_index]
        if self.name == "Oversized Material":
            return self.colors[scene_props.oversized_color_index]

    def get_inventory_material_name(self):
        return "{} {}".format(self.name, self.type_code)

    def draw(self, layout):
        scene_props = bpy.context.scene.closet_materials
        if self.name == "Upgrade Options":
            scene_props.upgrade_options.draw(layout)
            return

        row = layout.row()
        split = row.split(factor=0.25)
        color = self.get_mat_color()

        if self.name == "Garage Material":
            split.label(text="Exterior Color:")
            color_name = color.two_sided_display_name
        else:
            split.label(text="Color:")
            color_name = color.name

        split.menu(
            "SNAP_MATERIAL_MT_Mat_Colors",
            text=color_name,
            icon='RADIOBUT_ON' if color.has_render_mat else 'ERROR')

        # NOTE dealing with the situation it's needed to show exactly
        #      109" -> 2768 == 108.98" and 2769 == 109.02"
        if color.oversize_max_len > 0 and color.oversize_max_len != 2768:
            row = layout.row()
            split = row.split(factor=0.25)
            split.label(text="")

            max_len_inch = round(color.oversize_max_len / 25.4, 2)
            max_len_str = 'Max Length: {}"'.format(max_len_inch)
            split.label(text=max_len_str, icon='INFO')
        elif color.oversize_max_len > 0 and color.oversize_max_len == 2768:
            row = layout.row()
            split = row.split(factor=0.25)
            split.label(text="")

            max_len_inch = 109
            max_len_str = 'Max Length: {}"'.format(max_len_inch)
            split.label(text=max_len_str, icon='INFO')

        if not color.has_render_mat:
            row = layout.row()
            split = row.split(factor=0.25)
            split.label(text="")
            box = split.box()
            row = box.row()
            row.label(text="Missing render material.", icon='ERROR')


class Materials(PropertyGroup):
    mat_types: CollectionProperty(type=MaterialType)
    textured_mel_color_list = []
    mel_color_list = []
    veneer_backing_color_list = []
    garage_mat_color_list = []

    def create_color_lists(self):
        self.textured_mel_color_list.clear()
        self.mel_color_list.clear()
        self.veneer_backing_color_list.clear()
        self.garage_mat_color_list.clear()

        for mat_type in self.mat_types:
            if mat_type.name == 'Textured Melamine':
                for color in mat_type.colors:
                    self.textured_mel_color_list.append((color.name, color.name, color.name))
            if mat_type.name == 'Melamine':
                for color in mat_type.colors:
                    self.mel_color_list.append((color.name, color.name, color.name))
            if mat_type.name == 'Veneer':
                # Add 1/4" backing veneer
                for color in mat_type.colors:
                    if (color.name, color.name, color.name) not in self.veneer_backing_color_list:
                        self.veneer_backing_color_list.append((color.name, color.name, color.name))
            if mat_type.name == 'Garage Material':
                for color in mat_type.colors:
                    self.garage_mat_color_list.append((color.name, color.name, color.name))

    def set_type_index(self, index):
        defaults = bpy.context.scene.sn_closets.closet_defaults
        scene_props = bpy.context.scene.closet_materials
        scene_props.mat_type_index = index
        mat_type = self.get_mat_type()
        scene_props.set_default_material_color()

        if mat_type.name != "Garage Material":
            bpy.ops.sn_prompt.update_all_prompts_in_scene(
                prompt_name='Thick Adjustable Shelves',
                prompt_type='CHECKBOX',
                bool_value=False)
        else:
            bpy.ops.sn_prompt.update_all_prompts_in_scene(
                prompt_name='Thick Adjustable Shelves',
                prompt_type='CHECKBOX',
                bool_value=defaults.thick_adjustable_shelves)

    def get_mat_type(self):
        scene_props = bpy.context.scene.closet_materials
        return self.mat_types[scene_props.mat_type_index]

    def get_type_list(self):
        items = []
        for i, type in enumerate(self.mat_types):
            items.append((type.name, type.name, type.name))
        return items

    def get_mat_color_list(self, type_name):
        colors = []
        for color in self.mat_types[type_name].colors:
            if "Δ" in color.name:
                clean_name = color.name.replace("Δ", "(Discontinued)")
                colors.append((clean_name, clean_name, clean_name))
            else:
                colors.append((color.name, color.name, color.name))
        return colors

    def get_mat_color(self):
        return self.get_mat_type().get_mat_color()

    def has_render_mat(self):
        return self.get_mat_type().has_render_mat

    def draw(self, layout):
        box = layout.box()
        box.label(text="Material Selection:")
        scene_props = bpy.context.scene.closet_materials
        inventory_name = scene_props.materials.get_mat_color().name

        if scene_props.discontinued_color:
            warning_box = box.box()
            msg = '"{}" is no longer available to order!'.format(scene_props.discontinued_color)
            warning_box.label(text=msg, icon='ERROR')

        if "Δ" in inventory_name:
            warning_box = box.box()
            msg = 'Discontinued. Not available for new customers.'
            warning_box.label(text=msg, icon='ERROR')

        if len(self.mat_types) > 0:
            row = box.row()
            split = row.split(factor=0.25)
            split.label(text="Type:")
            split.menu('SNAP_MATERIAL_MT_Mat_Types', text=self.get_mat_type().name, icon='RADIOBUT_ON')
            self.get_mat_type().draw(box)
            row = box.row()
            if self.get_mat_type().name == "Garage Material":
                row.label(text="Two Sided Color Schemes Come With White Interiors")
            if (self.get_mat_type().name == "Solid Color Matte Finish") and (scene_props.use_custom_color_scheme == False) and self.get_mat_color().name != 'Cloud':
                row.label(text="Painted Wooden Door/Drawer Faces Will NOT Be Matte")

        else:
            row = box.row()
            row.label(text="None", icon='ERROR')


class DoorDrawerMaterialType(PropertyGroup):
    description: StringProperty()
    type_code: IntProperty()
    colors: CollectionProperty(type=MaterialColor)

    def set_color_index(self, index):
        scene_props = bpy.context.scene.closet_materials
        mat_type = scene_props.door_drawer_materials.get_mat_type()

        if mat_type.name == "Solid Color Smooth Finish":
            scene_props.dd_solid_color_index = index
        if mat_type.name == "Grain Pattern Smooth Finish":
            scene_props.dd_grain_color_index = index
        if mat_type.name == "Solid Color Textured Finish":
            scene_props.dd_solid_tex_color_index = index
        if mat_type.name == "Grain Pattern Textured Finish":
            scene_props.dd_grain_tex_color_index = index
        if mat_type.name == "Linen Pattern Linen Finish":
            scene_props.dd_linen_color_index = index
        if mat_type.name == "Solid Color Matte Finish":
            scene_props.dd_matte_color_index = index
        if mat_type.name == "Garage Material":
            scene_props.dd_garage_color_index = index
        if mat_type.name == "Oversized Material":
            scene_props.dd_oversized_color_index = index

    def get_color_index(self):
        scene_props = bpy.context.scene.closet_materials
        mat_type = scene_props.door_drawer_materials.get_mat_type()

        if mat_type.name == "Solid Color Smooth Finish":
            return scene_props.dd_solid_color_index
        if mat_type.name == "Grain Pattern Smooth Finish":
            return scene_props.dd_grain_color_index
        if mat_type.name == "Solid Color Textured Finish":
            return scene_props.dd_solid_tex_color_index
        if mat_type.name == "Grain Pattern Textured Finish":
            return scene_props.dd_grain_tex_color_index
        if mat_type.name == "Linen Pattern Linen Finish":
            return scene_props.dd_linen_color_index
        if mat_type.name == "Solid Color Matte Finish":
            return scene_props.dd_matte_color_index
        if mat_type.name == "Garage Material":
            return scene_props.dd_garage_color_index
        if mat_type.name == "Oversized Material":
            return scene_props.dd_oversized_color_index

    def get_mat_color(self):
        scene_props = bpy.context.scene.closet_materials
        if self.name == "Upgrade Options":
            upgrade_type = scene_props.upgrade_options.get_type()
            if upgrade_type.name == "Paint":
                return scene_props.paint_colors[scene_props.paint_color_index]
            else:
                return scene_props.stain_colors[scene_props.stain_color_index]
        elif scene_props.use_custom_color_scheme:
            if self.name == "Solid Color Smooth Finish":
                return self.colors[scene_props.dd_solid_color_index]
            if self.name == "Grain Pattern Smooth Finish":
                return self.colors[scene_props.dd_grain_color_index]
            if self.name == "Solid Color Textured Finish":
                return self.colors[scene_props.dd_solid_tex_color_index]
            if self.name == "Grain Pattern Textured Finish":
                return self.colors[scene_props.dd_grain_tex_color_index]
            if self.name == "Linen Pattern Linen Finish":
                return self.colors[scene_props.dd_linen_color_index]
            if self.name == "Solid Color Matte Finish":
                return self.colors[scene_props.dd_matte_color_index]
            if self.name == "Garage Material":
                return self.colors[scene_props.dd_garage_color_index]
            if self.name == "Oversized Material":
                return self.colors[scene_props.dd_oversized_color_index]
        else:
            return self.colors[scene_props.door_drawer_mat_color_index]

    def get_inventory_material_name(self):
        return "{} {}".format(self.name, self.type_code)

    def draw(self, layout):
        color = self.get_mat_color()

        row = layout.row()
        split = row.split(factor=0.25)

        if self.name == "Garage Material":
            split.label(text="Exterior Color:")
            color_name = color.two_sided_display_name
        else:
            split.label(text="Color:")
            color_name = color.name

        # split.label(text="Color:")            
        split.menu(
            "SNAP_MATERIAL_MT_Door_Drawer_Mat_Colors",
            text=color_name,
            icon='RADIOBUT_ON' if color.has_render_mat else 'ERROR')

        if not color.has_render_mat:
            row = layout.row()
            split = row.split(factor=0.25)
            split.label(text="")             
            box = split.box()
            row = box.row()
            row.label(text="Missing render material.", icon='ERROR') 


class DoorDrawerMaterials(PropertyGroup):
    mat_types: CollectionProperty(type=DoorDrawerMaterialType)
    textured_mel_color_list = []
    mel_color_list = []
    veneer_backing_color_list = []

    def create_color_lists(self):
        self.textured_mel_color_list.clear()
        self.mel_color_list.clear()
        self.veneer_backing_color_list.clear()

        for mat_type in self.mat_types:
            if mat_type.name == 'Textured Melamine':
                for color in mat_type.colors:
                    self.textured_mel_color_list.append((color.name, color.name, color.name))
            if mat_type.name == 'Melamine':
                for color in mat_type.colors:
                    self.mel_color_list.append((color.name, color.name, color.name))
            if mat_type.name == 'Veneer':
                # Add 1/4" backing veneer
                for color in mat_type.colors:
                    if (color.name, color.name, color.name) not in self.veneer_backing_color_list:
                        self.veneer_backing_color_list.append((color.name, color.name, color.name))

    def set_type_index(self, index):
        scene_props = bpy.context.scene.closet_materials
        scene_props.door_drawer_mat_type_index = index
        scene_props.set_default_material_color()

    def get_mat_type(self):
        scene_props = bpy.context.scene.closet_materials
        return self.mat_types[scene_props.door_drawer_mat_type_index]

    def get_mat_color(self):
        scene_props = bpy.context.scene.closet_materials
        if self.name == "Upgrade Options":
            if self.upgrade_options == 'PAINT':
                return scene_props.paint_colors[scene_props.paint_color_index]
            else:
                return scene_props.stain_colors[scene_props.stain_color_index]
        else:        
            return self.get_mat_type().get_mat_color()

    def has_render_mat(self):
        return self.get_mat_type().has_render_mat

    def draw(self, layout):
        box = layout.box()
        box.label(text="Material Selection:")
        scene_props = bpy.context.scene.closet_materials

        if scene_props.dd_mat_discontinued_color:
            warning_box = box.box()
            msg = '"{}" is no longer available to order!'.format(scene_props.dd_mat_discontinued_color)
            warning_box.label(text=msg, icon='ERROR')

        if len(self.mat_types) > 0:
            row = box.row()
            split = row.split(factor=0.25)
            split.label(text="Type:")
            split.menu('SNAP_MATERIAL_MT_Door_Drawer_Mat_Types', text=self.get_mat_type().name, icon='RADIOBUT_ON')
            self.get_mat_type().draw(box) 

        else:
            row = box.row()
            row.label(text="None", icon='ERROR')               


class CountertopColor(PropertyGroup, ColorMixIn):
    chip_code: StringProperty()
    vendor: StringProperty()


class CountertopManufactuer(PropertyGroup):
    description: StringProperty()
    color_code: IntProperty()
    colors: CollectionProperty(type=CountertopColor)

    def set_color_index(self, index):
        scene_props = bpy.context.scene.closet_materials
        scene_props.ct_color_index = index

    def get_color(self):
        scene_props = bpy.context.scene.closet_materials
        if self.name == "Wood Painted MDF":
            return scene_props.get_ct_paint_color()
        if self.name == "Wood Stained Veneer":
            return scene_props.get_ct_stain_color()
        elif self.colors:
            return self.colors[scene_props.ct_color_index]

    def get_color_list(self):
        scene_props = bpy.context.scene.closet_materials
        colors = []
        if self.name == 'Butcher Block':
            return [("Craft Oak", "Craft Oak", "Craft Oak")]

        if self.name == "Wood Stained Veneer":
            return [(color.name, color.name, color.name) for color in scene_props.ct_stain_colors]
        if self.name == "Wood Painted MDF":
            return [(color.name, color.name, color.name) for color in scene_props.ct_paint_colors]

        for color in self.colors:
            colors.append((color.name, color.name, color.name))
        return colors


class CountertopType(PropertyGroup):
    type_code: IntProperty()
    description: StringProperty()
    manufactuers: CollectionProperty(type=CountertopManufactuer)
    colors: CollectionProperty(type=CountertopColor)

    def set_color_index(self, index):
        scene_props = bpy.context.scene.closet_materials
        scene_props.ct_color_index = index

    def set_mfg_index(self, index):
        scene_props = bpy.context.scene.closet_materials
        scene_props.ct_mfg_index = index
        scene_props.ct_color_index = 0

    def get_mfg(self):
        scene_props = bpy.context.scene.closet_materials
        return self.manufactuers[scene_props.ct_mfg_index]

    def get_color(self):
        scene_props = bpy.context.scene.closet_materials

        if len(self.colors) > 0:
            return self.colors[scene_props.ct_color_index] 

        elif len(self.manufactuers) > 0:
            return self.get_mfg().get_color()

    def draw(self, layout):
        if len(self.colors) > 0:
            color = self.get_color()

            row = layout.row()
            split = row.split(factor=0.25)
            split.label(text="Color:")
            split.menu(
                "SNAP_MATERIAL_MT_Countertop_Colors",
                text=color.name,
                icon='RADIOBUT_ON' if color.has_render_mat else 'ERROR')

            if not color.has_render_mat:
                row = layout.row()
                split = row.split(factor=0.25)
                split.label(text="")
                box = split.box()
                row = box.row()
                row.label(text="Missing render material.", icon='ERROR')

        elif len(self.manufactuers) > 0:
            mfg = self.get_mfg()
            color = mfg.get_color()
            wood_ct = self.name == "Wood"
            butcher_block = mfg.name == "Butcher Block"

            row = layout.row()
            split = row.split(factor=0.25)
            if wood_ct:
                split.label(text="Style:")
            else:
                split.label(text="Manufactuer:")
            split.menu("SNAP_MATERIAL_MT_Countertop_Mfgs", text=mfg.name, icon='RADIOBUT_ON')

            if wood_ct and not butcher_block:
                if mfg.name == "Wood Painted MDF":
                    row = layout.row()
                    split = row.split(factor=0.25)
                    split.label(text="Color:")
                    split.menu(
                        "SNAP_MATERIAL_MT_Ct_Paint_Colors",
                        text=color.name,
                        icon='RADIOBUT_ON')

                elif mfg.name == "Wood Stained Veneer":
                    row = layout.row()
                    split = row.split(factor=0.25)
                    split.label(text="Color:")
                    split.menu(
                        "SNAP_MATERIAL_MT_Ct_Stain_Colors",
                        text=color.name,
                        icon='RADIOBUT_ON')

            elif not butcher_block:
                row = layout.row()
                split = row.split(factor=0.25)
                split.label(text="Color:")
                split.menu(
                    "SNAP_MATERIAL_MT_Countertop_Colors",
                    text=mfg.get_color().name,
                    icon='RADIOBUT_ON')


class CustomCountertops(PropertyGroup):
    name: StringProperty(name="Name")
    vendor: StringProperty(name="Vendor")
    color_code: StringProperty(name="Color Code")
    price: FloatProperty(name="Price")

    def get_color(self):
        pass

    def draw(self, layout):
        layout.prop(self, 'name')
        layout.prop(self, 'vendor')
        layout.prop(self, 'color_code')
        layout.prop(self, 'price')


class Countertops(PropertyGroup):
    countertop_types: CollectionProperty(type=CountertopType)
    custom_countertop: PointerProperty(type=CustomCountertops)

    def get_granite_color_list(self):
        granite_color_list = []
        for mat_type in self.countertop_types:
            if mat_type.name == 'Granite':
                for color in mat_type.colors:
                    granite_color_list.append((color.name, color.name, color.name))
        return granite_color_list

    def get_hpl_mfg_list(self):
        mfgs = []
        for mat_type in self.countertop_types:
            if mat_type.name == 'HPL':
                for mfg in mat_type.manufactuers:
                    mfgs.append((mfg.name, mfg.name, mfg.name))
        return mfgs

    def get_quartz_mfg_list(self):
        mfgs = []
        for mat_type in self.countertop_types:
            if mat_type.name == 'Quartz':
                for mfg in mat_type.manufactuers:
                    mfgs.append((mfg.name, mfg.name, mfg.name))
        return mfgs

    def get_standard_quartz_color_list(self):
        standard_quartz_color_list = []
        for mat_type in self.countertop_types:
            if mat_type.name == 'Standard Quartz':
                for color in mat_type.colors:
                    standard_quartz_color_list.append((color.name, color.name, color.name))
        return standard_quartz_color_list

    def set_ct_type_index(self, index):
        scene_props = bpy.context.scene.closet_materials
        scene_props.ct_type_index = index
        scene_props.ct_mfg_index = 0
        scene_props.ct_color_index = 0

    def get_type(self):
        scene_props = bpy.context.scene.closet_materials
        return self.countertop_types[scene_props.ct_type_index]

    def get_color(self):
        scene_props = bpy.context.scene.closet_materials
        ct_type = self.get_type()
        mfg = None

        if len(ct_type.manufactuers) > 0:
            mfg = ct_type.get_mfg()

        if "Wood" in ct_type.name:
            if mfg.name == "Wood Painted MDF":
                return mfg.colors[scene_props.ct_paint_color_index]
            if mfg.name == "Wood Stained Veneer":
                return mfg.colors[scene_props.ct_stain_color_index]
        else:
            return self.get_type().get_color()

    def get_color_name(self):
        ct_type = self.get_type()
        mfg = None

        if len(ct_type.manufactuers) > 0:
            mfg = ct_type.get_mfg()

        if "Melamine" in ct_type.name:
            materials = bpy.context.scene.closet_materials.materials
            return materials.get_mat_color().name

        if "Wood" in ct_type.name and mfg:
            if mfg.name == "Butcher Block":
                return "Craft Oak"
            else:
                color = self.get_color()
                return color.name

        else:
            color = self.get_color()
            return color.name

    def color_has_render_mat(self):
        if self.get_type().name == "Wood":
            return True

        color = self.get_color()

        if color:
            if color.has_render_mat:
                return True
            else:
                return False
        else:
            return True

    def get_ct_inventory_name(self):
        ct_type = self.get_type()
        ct_color = self.get_color()
        ct_mfg = ct_type.get_mfg()

        if len(ct_type.colors) > 0:
            return "{} {}".format(ct_type.name, ct_color.name)

        elif len(ct_type.manufactuers) > 0:
            return "{} {} {}".format(ct_type.name, ct_mfg.name, ct_color.name)

    def draw(self, layout):
        box = layout.box()
        box.label(text="Countertop Selection:")

        if len(self.countertop_types) > 0:
            row = box.row()
            split = row.split(factor=0.25)
            split.label(text="Type:")
            split.menu('SNAP_MATERIAL_MT_Countertop_Types', text=self.get_type().name, icon='RADIOBUT_ON')
            self.get_type().draw(box)

            if self.get_type().name == "Custom":
                self.custom_countertop.draw(box)

        else:
            row = box.row()
            row.label(text="None", icon='ERROR')


class StainColor(PropertyGroup, ColorMixIn):
    description: StringProperty()
    sku: StringProperty()


class PaintColor(PropertyGroup, ColorMixIn):
    description: StringProperty()
    sku: StringProperty()


class UpgradeType(PropertyGroup):

    def get_color(self):
        scene_props = bpy.context.scene.closet_materials
        if self.name == "Paint":
            return scene_props.paint_colors[scene_props.paint_color_index]
        elif self.name == "Stain":
            return scene_props.stain_colors[scene_props.stain_color_index]

    def draw(self, layout):
        scene_props = bpy.context.scene.closet_materials
        if self.name == "None":
            return

        row = layout.row()
        split = row.split(factor=0.25)
        split.label(text="Color:")

        if self.name == "Paint":
            split.menu('SNAP_MATERIAL_MT_Paint_Colors', text=scene_props.get_paint_color().name, icon='RADIOBUT_ON')
        elif self.name == "Stain":
            split.menu('SNAP_MATERIAL_MT_Stain_Colors', text=scene_props.get_stain_color().name, icon='RADIOBUT_ON')


class UpgradeOptions(PropertyGroup):
    types: CollectionProperty(type=UpgradeType)

    def get_type(self):
        scene_props = bpy.context.scene.closet_materials
        return self.types[scene_props.upgrade_type_index]

    def set_type_index(self, index):
        scene_props = bpy.context.scene.closet_materials
        scene_props.upgrade_type_index = index

    def draw(self, layout):
        custom_colors = bpy.context.scene.closet_materials.use_custom_color_scheme
        scene_props = bpy.context.scene.closet_materials

        if len(self.types) > 0:
            if custom_colors:
                layout = layout.box()
                layout.label(text="Paint/Stain Options:")
                if scene_props.dd_mat_discontinued_color:
                    warning_box = layout.box()
                    msg = '"{}" is no longer available to order!'.format(scene_props.dd_mat_discontinued_color)
                    warning_box.label(text=msg, icon='ERROR')

            row = layout.row()
            split = row.split(factor=0.25)
            split.label(text="Option:")
            split.menu('SNAP_MATERIAL_MT_Upgrade_Types', text=self.get_type().name, icon='RADIOBUT_ON')
            self.get_type().draw(layout)

            if custom_colors and scene_props.upgrade_options.get_type().name != "None":
                active_glaze_color = scene_props.get_glaze_color()
                row = layout.row(align=True)
                split = row.split(factor=0.25)
                split.label(text="Glaze Color:")
                split.menu(
                    'SNAP_MATERIAL_MT_Glaze_Colors',
                    text=active_glaze_color.name, icon='RADIOBUT_ON')

                if active_glaze_color.name != "None":
                    active_glaze_style = scene_props.get_glaze_style()
                    row = layout.row(align=True)
                    split = row.split(factor=0.25)
                    split.label(text="Glaze Style:")
                    split.menu(
                        'SNAP_MATERIAL_MT_Glaze_Styles',
                        text=active_glaze_style.name, icon='RADIOBUT_ON')

        else:
            row = layout.row()
            row.label(text="None", icon='ERROR')


class FivePieceMelamineDoorColor(PropertyGroup):
    description: StringProperty()
    sku: StringProperty()


class GlazeColor(PropertyGroup):
    description: StringProperty()
    sku: StringProperty()


class GlazeStyle(PropertyGroup):
    description: StringProperty()
    sku: StringProperty()


class DoorColor(PropertyGroup):
    description: StringProperty()
    sku: StringProperty()


class GlassColor(PropertyGroup):
    description: StringProperty()
    sku: StringProperty()


class BackingVeneerColor(PropertyGroup):
    description: StringProperty()
    sku: StringProperty()


class ColorConversions(PropertyGroup):
    name: StringProperty()
    new_name: StringProperty()


class DrawerSlideSize(PropertyGroup):
    slide_length_inch: FloatProperty()
    front_hole_dim_mm: IntProperty()
    back_hole_dim_mm: IntProperty()


class DrawerSlide(PropertyGroup):
    db_name: StringProperty()
    sizes: CollectionProperty(type=DrawerSlideSize)


classes = (
    EdgeColor,
    EdgeType,
    Edges,
    DoorDrawerEdgeType,
    DoorDrawerEdges,
    SecondaryEdgeType,
    SecondaryEdges,
    MaterialColor,
    MaterialType,
    Materials,
    DoorDrawerMaterialType,
    DoorDrawerMaterials,
    CountertopColor,
    CountertopManufactuer,
    CountertopType,
    CustomCountertops,
    Countertops,
    StainColor,
    PaintColor,
    UpgradeType,
    UpgradeOptions,
    FivePieceMelamineDoorColor,
    GlazeColor,
    GlazeStyle,
    DoorColor,
    GlassColor,
    BackingVeneerColor,
    DrawerSlideSize,
    DrawerSlide,
    ColorConversions
)

register, unregister = bpy.utils.register_classes_factory(classes)