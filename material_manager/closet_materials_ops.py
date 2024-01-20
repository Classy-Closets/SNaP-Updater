import os
import subprocess
import time

import bpy
from bpy.types import Operator
from bpy.props import BoolProperty, StringProperty

from snap import sn_unit
from snap import sn_paths
from snap import sn_utils
from snap import sn_types
from snap.ops.sn_prompt import SN_PPT_OT_update_all_prompts_in_scene


def set_material_pointers(obj_bp, material_pointer_name, slot_name=""):
    """
    Sets every material slot for every mesh to the material_pointer_name.

    **Parameters:**

    * **material_pointer_name** (string, (never None)) - Name of the material pointer to assign.

    * **slot_name** (string, (optional)) - If not "" then the material_pointer_name will be assigned to the slot.

    **Returns:** None
    """
    for slot in obj_bp.snap.material_slots:
        if slot_name == "":
            slot.pointer_name = material_pointer_name
        elif slot_name == slot.name:
            slot.pointer_name = material_pointer_name
    for child in obj_bp.children:
        if child.type == 'MESH':
            if len(child.snap.material_slots) < 1:
                bpy.ops.sn_material.add_material_pointers(object_name=child.name)
            for slot in child.snap.material_slots:
                if slot_name == "":
                    slot.pointer_name = material_pointer_name
                elif slot_name == slot.name:
                    slot.pointer_name = material_pointer_name


def edgebanding(obj_bp, edgebanding_name, w1=False, l1=False, w2=False, l2=False):
    """
    Assigns every mesh cut part to the edgebanding_name.

    **Parameters:**

    * **edgebanding_name** (string, (never None)) - Name of the edgepart pointer to assign.

    * **w1** (bool, (optional, default=False)) - Determines if to edgeband width 1 of the part.

    * **w2** (bool, (optional, default=False)) - Determines if to edgeband width 2 of the part.

    * **l1** (bool, (optional, default=False)) - Determines if to edgeband length 1 of the part.

    * **l2** (bool, (optional, default=False)) - Determines if to edgeband length 2 of the part.

    **Returns:** None
    """

    for child in obj_bp.children:
        if child.type == 'MESH' and child.snap.type_mesh == 'EDGEBANDING':
            child.snap.edgepart_name = edgebanding_name
        if child.type == 'MESH' and child.snap.type_mesh == 'CUTPART':
            child.snap.edgepart_name = edgebanding_name
            if w1:
                child.snap.edge_w1 = edgebanding_name
            if l1:
                child.snap.edge_l1 = edgebanding_name
            if w2:
                child.snap.edge_w2 = edgebanding_name
            if l2:
                child.snap.edge_l2 = edgebanding_name


class SN_MAT_OT_Poll_Assign_Materials(Operator):
    bl_idname = "closet_materials.poll_assign_materials"
    bl_label = ""
    bl_description = ""
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene.closet_materials.check_render_mats()

    def execute(self, context):
        mat_props = context.scene.closet_materials
        mat_props.discontinued_color = ""
        mat_props.edge_discontinued_color = ""
        mat_props.cleat_edge_discontinued_color = ""
        mat_props.dd_mat_discontinued_color = ""
        mat_props.dd_edge_discontinued_color = ""
        mat_props.stain_discontinued_color = ""

        bpy.ops.closet_materials.assign_materials()

        return {'FINISHED'}


class SN_MAT_OT_Assign_Materials(Operator):
    bl_idname = "closet_materials.assign_materials"
    bl_label = "Assign Materials"
    bl_description = "This will assign the material names"
    bl_options = {'UNDO'}

    update_countertops: BoolProperty(name="Update Countertops", default=False)
    only_update_pointers: BoolProperty(
        name="Only Update Pointers", default=False)

    closet_props = None
    props_closet_materials = None

    @classmethod
    def poll(cls, context):
        return context.scene.closet_materials.check_render_mats()

    def scene_assemblies(self, context):
        for obj in bpy.context.scene.objects:
            if 'IS_BP_ASSEMBLY' in obj:
                assembly = sn_types.Assembly(obj_bp=obj)
                yield assembly

    def scene_assembly_bps(self, context):
        for obj in bpy.context.scene.objects:
            if 'IS_BP_ASSEMBLY' in obj:
                yield obj

    def set_manufacturing_material(self, obj):
        """ Sets the cutpart_material_name property so the materials
            get exported as the correct names.
        """
        props = bpy.context.scene.closet_materials
        mat_type = props.materials.get_mat_type()
        edge_type = props.edges.get_edge_type()
        door_drawer_edge_type = props.door_drawer_edges.get_edge_type()
        edge2_type = props.secondary_edges.get_edge_type()

        obj.snap.cutpart_material_name = mat_type.get_inventory_material_name()

        if obj.snap.edge_w1 != "":
            if obj.snap.edge_w1 == 'Edge':
                obj.snap.edgeband_material_name_w1 = edge_type.get_inventory_edge_name()
            elif obj.snap.edge_w1 == 'Door_Edges':
                obj.snap.edgeband_material_name_w1 = door_drawer_edge_type.get_inventory_edge_name()
            else:
                obj.snap.edgeband_material_name_w1 = edge2_type.get_inventory_edge_name()
        if obj.snap.edge_w2 != "":
            if obj.snap.edge_w2 == 'Edge':
                obj.snap.edgeband_material_name_w2 = edge_type.get_inventory_edge_name()
            elif obj.snap.edge_w2 == 'Door_Edges':
                obj.snap.edgeband_material_name_w2 = door_drawer_edge_type.get_inventory_edge_name()
            else:
                obj.snap.edgeband_material_name_w2 = edge2_type.get_inventory_edge_name()
        if obj.snap.edge_l1 != "":
            if obj.snap.edge_l1 == 'Edge':
                obj.snap.edgeband_material_name_l1 = edge_type.get_inventory_edge_name()
            elif obj.snap.edge_l1 == 'Door_Edges':
                obj.snap.edgeband_material_name_l1 = door_drawer_edge_type.get_inventory_edge_name()
            else:
                obj.snap.edgeband_material_name_l1 = edge2_type.get_inventory_edge_name()
        if obj.snap.edge_l2 != "":
            if obj.snap.edge_l2 == 'Edge':
                obj.snap.edgeband_material_name_l2 = edge_type.get_inventory_edge_name()
            elif obj.snap.edge_l2 == 'Door_Edges':
                obj.snap.edgeband_material_name_l2 = door_drawer_edge_type.get_inventory_edge_name()
            else:
                obj.snap.edgeband_material_name_l2 = edge2_type.get_inventory_edge_name()

    def set_material(self, assembly):
        for child in assembly.obj_bp.children:
            if child.snap.type_mesh == 'CUTPART':
                self.set_manufacturing_material(child)

    def set_material_2(self, obj_bp):
        for child in obj_bp.children:
            if child.snap.type_mesh == 'CUTPART':
                self.set_manufacturing_material(child)

    def set_door_material(self, obj_bp):
        for obj in obj_bp.children:
            if obj.snap.type_mesh == 'CUTPART':
                cab_mat_props = self.props_closet_materials
                mat_type = cab_mat_props.door_drawer_materials.get_mat_type()
                mat_color_name = cab_mat_props.door_drawer_materials.get_mat_color().name
                edge_type = cab_mat_props.door_drawer_edges.get_edge_type()
                door_part = sn_types.Part(obj_bp)
                custom_colors = cab_mat_props.use_custom_color_scheme

                if mat_type.name == "Garage Material":
                    door_part.cutpart("Garage_Slab_Door")
                    if mat_color_name == "Cosmic Dust" or self.use_black_edge and mat_color_name == "Steel Grey":
                        door_part.edgebanding("Black_Edge", l1=True, w1=True, l2=True, w2=True)
                        door_part.set_material_pointers("Black", "TopBottomEdge")
                        door_part.set_material_pointers("Black", "LeftRightEdge")
                    else:
                        if custom_colors:
                            door_part.edgebanding('Door_Edges', l1=True, w1=True, l2=True, w2=True)
                            door_part.set_material_pointers("Door_Edge", "TopBottomEdge")
                            door_part.set_material_pointers("Door_Edge", "LeftRightEdge")
                        else:
                            door_part.edgebanding("Exterior_Edge", l1=True, w1=True, l2=True, w2=True)
                            door_part.set_material_pointers("Garage_Panel_Edges", "TopBottomEdge")
                            door_part.set_material_pointers("Garage_Panel_Edges", "LeftRightEdge")
                else:
                    door_part.cutpart("Slab_Door")
                    door_part.edgebanding('Door_Edges', l1=True, w1=True, l2=True, w2=True)
                    door_part.set_material_pointers("Door_Edge", "TopBottomEdge")
                    door_part.set_material_pointers("Door_Edge", "LeftRightEdge")

                obj.snap.cutpart_material_name = mat_type.get_inventory_material_name()
                obj.snap.edgeband_material_name_w1 = edge_type.get_inventory_edge_name()
                obj.snap.edgeband_material_name_w2 = edge_type.get_inventory_edge_name()
                obj.snap.edgeband_material_name_l1 = edge_type.get_inventory_edge_name()
                obj.snap.edgeband_material_name_l2 = edge_type.get_inventory_edge_name()

    def set_drawer_bottom_material(self, obj_bp):
        for obj in obj_bp.children:
            if obj.snap.type_mesh == 'CUTPART':
                box_type = self.closet_props.closet_options.box_type

                if box_type == 'MEL':
                    obj.snap.cutpart_material_name = "White Paper 11300"
                else:
                    obj.snap.cutpart_material_name = "Baltic Birch 30250"

    def set_drawer_part_material(self, part):
        for obj in part.obj_bp.children:
            if obj.snap.type_mesh == 'CUTPART':
                box_type = part.get_prompt("Box Type")
                if box_type:
                    if box_type.get_value() == 1 and not part.obj_bp.get('IS_BP_DRAWER_BOTTOM'):
                        drawer_part = sn_types.Part(part.obj_bp)
                        drawer_part.cutpart("Panel")
                        drawer_part.edgebanding("Edge", l1=True)
                        cab_mat_props = self.props_closet_materials
                        mat_type = cab_mat_props.door_drawer_materials.get_mat_type()
                        edge_type = cab_mat_props.door_drawer_edges.get_edge_type()
                        obj.snap.cutpart_material_name = mat_type.get_inventory_material_name()
                        obj.snap.edgeband_material_name_l1 = edge_type.get_inventory_edge_name()
                        obj.snap.edgeband_material_name_l2 = ""
                        obj.snap.edgeband_material_name_w1 = ""
                        obj.snap.edgeband_material_name_w2 = ""
                    elif box_type.get_value() == 2:
                        drawer_part = sn_types.Part(part.obj_bp)
                        drawer_part.cutpart("Drawer_Part")
                        drawer_part.edgebanding("Drawer_Box_Edge", l1=True)
                        obj.snap.cutpart_material_name = "Baltic Birch 32200"
                        obj.snap.edgeband_material_name_l1 = "Winter White (Oxford White) 1030"
                        obj.snap.edgeband_material_name_l2 = ""
                        obj.snap.edgeband_material_name_w1 = ""
                        obj.snap.edgeband_material_name_w2 = ""
                    else:
                        drawer_part = sn_types.Part(part.obj_bp)
                        drawer_part.cutpart("Drawer_Part")
                        drawer_part.edgebanding("Drawer_Box_Edge", l1=True)
                        obj.snap.cutpart_material_name = "Winter White (Oxford White) 12200"
                        obj.snap.edgeband_material_name_l1 = "Winter White (Oxford White) 1030"
                        obj.snap.edgeband_material_name_l2 = ""
                        obj.snap.edgeband_material_name_w1 = ""
                        obj.snap.edgeband_material_name_w2 = ""
                else:
                    props = self.props_closet_materials
                    box_type = self.closet_props.closet_options.box_type

                    if box_type == 'MEL':
                        obj.snap.cutpart_material_name = "Winter White (Oxford White) 12200"
                    else:
                        obj.snap.cutpart_material_name = "Baltic Birch 32200"

                    obj.snap.edgeband_material_name_l1 = "Winter White (Oxford White) 1030"
                    obj.snap.edgeband_material_name_l2 = ""
                    obj.snap.edgeband_material_name_w1 = ""
                    obj.snap.edgeband_material_name_w2 = ""

    def update_material_pointers(self, context):
        mat_props = self.props_closet_materials
        default_props = self.closet_props.closet_options

        for spec_group in context.scene.snap.spec_groups:
            surface_pointer = spec_group.materials["Closet_Part_Surfaces"]
            garage_interior_pointer = spec_group.materials["Garage_Interior_Surface"]
            edge_pointer = spec_group.materials["Closet_Part_Edges"]
            edge_pointer_2 = spec_group.materials["Closet_Part_Edges_Secondary"]
            door_pointer = spec_group.materials["Door_Surface"]
            door_edge_pointer = spec_group.materials["Door_Edge"]
            molding_pointer = spec_group.materials["Molding"]
            drawer_surface = spec_group.materials["Drawer_Box_Surface"]
            wood_door_pointer = spec_group.materials["Wood_Door_Surface"]
            five_piece_melamine_door_pointer = spec_group.materials["Five_Piece_Melamine_Door_Surface"]
            moderno_door_pointer = spec_group.materials["Moderno_Door"]
            glass_panel_pointer = spec_group.materials["Glass"]

            countertop_pointer = spec_group.materials["Countertop_Surface"]
            countertop_hpl_pointer = spec_group.materials["Countertop_HPL_Surface"]
            countertop_granite_pointer = spec_group.materials["Countertop_Granite_Surface"]
            countertop_quartz_pointer = spec_group.materials["Countertop_Quartz_Surface"]

            garage_exterior_surface_pointer = spec_group.materials["Garage_Exterior_Surface"]
            garage_panel_edge_pointer = spec_group.materials["Garage_Panel_Edges"]
            garage_interior_edge_pointer = spec_group.materials["Garage_Interior_Edges"]
            cabinet_countertop_pointer = spec_group.materials["Cabinet_Countertop_Surface"]
            countertop_wood_pointer = spec_group.materials["Countertop_Butcher_Block_Surface"]

            hood_surface_pointer = spec_group.materials["Hood_Surface"]
            cabinet_base_surface_pointer = spec_group.materials["Cabinet_Base_Surface"]
            cabinet_upper_surface_pointer = spec_group.materials["Cabinet_Upper_Surface"]
            cabinet_island_surface_pointer = spec_group.materials["Cabinet_Island_Surface"]
            cabinet_molding_surface_pointer = spec_group.materials["Cabinet_Molding_Surface"]

            # Set garage pointers
            garage_exterior_surface_pointer.category_name = "Closet Materials"
            garage_exterior_surface_pointer.item_name = mat_props.materials.get_mat_color().name

            garage_panel_edge_pointer.category_name = "Closet Materials"
            garage_panel_edge_pointer.item_name = mat_props.edges.get_edge_color().name

            garage_interior_edge_pointer.category_name = "Closet Materials"
            garage_interior_edge_pointer.item_name = "Winter White (Oxford White)"

            # Construction Defaults
            if default_props.box_type == 'MEL':
                drawer_surface.category_name = "Closet Materials"
                drawer_surface.item_name = "Winter White (Oxford White)"
            else:
                drawer_surface.category_name = "Closet Materials"
                drawer_surface.item_name = "Birch"

            surface_pointer.category_name = "Closet Materials"
            surface_pointer.item_name = mat_props.materials.get_mat_color().name

            garage_interior_pointer.category_name = "Closet Materials"
            if mat_props.materials.get_mat_type().name == "Garage Material":
                garage_interior_pointer.item_name = "Winter White (Oxford White)"
            else:
                garage_interior_pointer.item_name = mat_props.materials.get_mat_color().name

            molding_pointer.category_name = "Closet Materials"
            stain_color = surface_pointer.item_name in mat_props.get_stain_colors()
            paint_color = surface_pointer.item_name in mat_props.get_paint_colors()
            material_name = mat_props.materials.get_mat_color().name
            white_color = (material_name == "Snow Drift" or material_name == "Mountain Peak")
            if white_color:
                molding_pointer.item_name = "Winter White"
            elif stain_color or paint_color:
                molding_pointer.item_name = surface_pointer.item_name

            door_pointer.category_name = "Closet Materials"
            door_pointer.item_name = mat_props.door_drawer_materials.get_mat_color().name

            edge_pointer.category_name = "Closet Materials"
            edge_pointer_2.category_name = "Closet Materials"
            door_edge_pointer.category_name = "Closet Materials"

            if mat_props.materials.get_mat_type().name == "Oversized Material":
                edge_pointer.item_name = mat_props.default_edge_color
                edge_pointer_2.item_name = mat_props.default_edge_color
                door_edge_pointer.item_name = mat_props.default_edge_color
            if mat_props.materials.get_mat_type().name == "Upgrade Options":
                edge_pointer.item_name = mat_props.upgrade_options.get_type().get_color().name
                edge_pointer_2.item_name = mat_props.upgrade_options.get_type().get_color().name
                door_edge_pointer.item_name = mat_props.upgrade_options.get_type().get_color().name
            else:
                edge_pointer.item_name = mat_props.edges.get_edge_color().name
                edge_pointer_2.item_name = mat_props.secondary_edges.get_edge_color().name
                door_edge_pointer.item_name = mat_props.door_drawer_edges.get_edge_color().name

            wood_door_pointer.category_name = "Closet Materials"
            mat_color_name = mat_props.materials.get_mat_color().name
            has_paint = mat_color_name in mat_props.get_paint_colors()
            has_stain = mat_color_name in mat_props.get_stain_colors()
            custom_colors = mat_props.use_custom_color_scheme
            white_color = (mat_color_name == "Snow Drift" or mat_color_name == "Mountain Peak")
            is_antique_white = (mat_color_name == "Bridal Shower (Antique White) Δ")
            is_coastal_living = mat_color_name == "Coastal Living"
            if  (white_color or is_antique_white or is_coastal_living) and not custom_colors:
                has_paint = True

            if not custom_colors:
                if has_paint:
                    if white_color:
                        wood_door_pointer.item_name = "Winter White"
                    elif is_antique_white:
                        wood_door_pointer.item_name = "Warm Spring"
                    elif is_coastal_living:
                        wood_door_pointer.item_name = "Deep Blue"
                    else:
                        wood_door_pointer.item_name = mat_props.materials.get_mat_color().name
                elif has_stain:
                    wood_door_pointer.item_name = mat_props.materials.get_mat_color().name

            elif mat_props.upgrade_options.get_type().name == "Stain":
                wood_door_pointer.item_name = mat_props.stain_colors[mat_props.stain_color_index].name
            elif mat_props.upgrade_options.get_type().name == "Paint":
                wood_door_pointer.item_name = mat_props.paint_colors[mat_props.paint_color_index].name
            else:
                wood_door_pointer.item_name = mat_props.materials.get_mat_color().name

            five_piece_melamine_door_pointer.category_name = "Closet Materials"
            door_color = mat_props.five_piece_melamine_door_colors[mat_props.five_piece_melamine_door_mat_color_index]
            five_piece_melamine_door_pointer.item_name = door_color.name

            moderno_door_pointer.category_name = "Closet Materials"
            mat_has_moderno_color = mat_color_name in mat_props.moderno_colors

            if custom_colors:
                moderno_door_pointer.item_name = mat_props.moderno_colors[mat_props.moderno_color_index].name
            elif mat_has_moderno_color:
                moderno_door_pointer.item_name = mat_color_name

            glass_panel_pointer.category_name = "Glass"
            glass_panel_pointer.item_name = "Glass"

            # Countertops
            if "Melamine" in mat_props.countertops.get_type().name:
                countertop_pointer.category_name = "Closet Materials"
                cabinet_countertop_pointer.category_name = "Closet Materials"
                countertop_pointer.item_name = mat_props.countertops.get_color_name()
            elif "Wood" in mat_props.countertops.get_type().name:
                countertop_wood_pointer.category_name = "Closet Materials"
                color_name = mat_props.countertops.get_color_name()
                if color_name == "Other/Custom":
                    color_name = "Winter White (Oxford White)"
                countertop_wood_pointer.item_name = color_name
            else:
                countertop_hpl_pointer.category_name = "Countertop Materials"
                countertop_granite_pointer.category_name = "Countertop Materials"
                cabinet_countertop_pointer.category_name = "Countertop Materials"
                countertop_quartz_pointer.category_name = "Countertop Materials"

                countertop_hpl_pointer.item_name = mat_props.countertops.get_color_name()
                countertop_granite_pointer.item_name = mat_props.countertops.get_color_name()
                countertop_quartz_pointer.item_name = mat_props.countertops.get_color_name()

            cabinet_countertop_pointer.item_name = mat_props.countertops.get_color_name()

            if hood_surface_pointer:
                mat_color_name = mat_props.materials.get_mat_color().name
                has_paint = mat_color_name in mat_props.get_paint_colors()
                has_stain = mat_color_name in mat_props.get_stain_colors()
                if has_stain or has_paint:
                    hood_surface_pointer.item_name = mat_props.materials.get_mat_color().name

            # KB Cabinets
            cabinet_base_surface_pointer.category_name = "Closet Materials"
            cabinet_upper_surface_pointer.category_name = "Closet Materials"
            cabinet_island_surface_pointer.category_name = "Closet Materials"
            cabinet_molding_surface_pointer.category_name = "Closet Materials"
            hood_surface_pointer.category_name = "Closet Materials"

            cabinet_base_surface_pointer.item_name = mat_props.kb_base_mat
            cabinet_upper_surface_pointer.item_name = mat_props.kb_upper_mat
            cabinet_island_surface_pointer.item_name = mat_props.kb_island_mat
            cabinet_molding_surface_pointer.item_name = "Winter White"
            hood_surface_pointer.item_name = mat_props.kb_hood_mat
            

    def update_drawer_materials(self):
        props = self.closet_props
        box_type = props.closet_options.box_type

        for spec_group in bpy.context.scene.snap.spec_groups:
            drawer_part = spec_group.cutparts['Drawer_Part']
            drawer_back = spec_group.cutparts['Drawer_Back']
            drawer_bottom = spec_group.cutparts['Drawer_Bottom']

            if box_type == 'MEL':
                drawer_part.thickness = sn_unit.inch(.5)
                drawer_back.thickness = sn_unit.inch(.5)
                drawer_bottom.thickness = sn_unit.inch(.375)
            else:
                drawer_part.thickness = sn_unit.inch(.5)
                drawer_back.thickness = sn_unit.inch(.5)
                drawer_bottom.thickness = sn_unit.inch(.25)

    def set_shelf_material(self, assembly, is_locked_shelf=False):
        cab_mat_props = self.props_closet_materials
        mat_type = cab_mat_props.materials.get_mat_type()
        mat_color_name = cab_mat_props.materials.get_mat_color().name
        shelf_part = sn_types.Part(assembly.obj_bp)

        is_locked_shelf_ppt = assembly.get_prompt("Is Locked Shelf")
        if is_locked_shelf_ppt:
            if is_locked_shelf_ppt.get_value():
                is_locked_shelf = True

        is_exposed = False
        is_bottom_exposed_kd = assembly.get_prompt("Is Bottom Exposed KD")
        if is_bottom_exposed_kd:
            if is_bottom_exposed_kd.get_value():
                is_exposed = True

        if mat_type.name == "Garage Material":
            section_product = sn_types.Assembly(sn_utils.get_closet_bp(assembly.obj_bp))
            if is_locked_shelf:
                if section_product.obj_bp.get("IS_BP_CORNER_SHELVES") or section_product.obj_bp.get("IS_BP_L_SHELVES"):
                    has_door = False
                    door = section_product.get_prompt("Door")
                    if door:
                        has_door = door.get_value()

                    if has_door:
                        if is_exposed:
                            # If the z dimension is negative, I need to flip the cutpart sides.
                            if assembly.obj_z.location.z > 0:
                                shelf_part.cutpart("Garage_Bottom_KD")
                            else:
                                shelf_part.cutpart("Garage_Top_KD")
                        else:
                            shelf_part.cutpart("Garage_Interior_KD")
                        if abs(sn_unit.meter_to_inch(assembly.obj_z.location.z)) > 0.76:
                            shelf_part.cutpart("Garage_Interior_Shelf")
                            shelf_part.edgebanding("Interior_Edge", l2=True)
                            shelf_part.set_material_pointers("Garage_Interior_Edges", "Edgebanding")
                        elif mat_color_name == "Cosmic Dust" or self.use_black_edge and mat_color_name == "Steel Grey":
                            shelf_part.edgebanding("Black_Edge", l2=True)
                            shelf_part.set_material_pointers("Black", "Edgebanding")
                        else:
                            shelf_part.edgebanding("Exterior_Edge", l2=True)
                            shelf_part.set_material_pointers("Garage_Panel_Edges", "Edgebanding")
                    else:
                        shelf_part.cutpart("Garage_Interior_Shelf")
                        shelf_part.edgebanding("Interior_Edge", l2=True)
                        shelf_part.set_material_pointers("Garage_Interior_Edges", "Edgebanding")

                else:
                    if is_exposed:
                        # If the z dimension is negative, I need to flip the cutpart sides.
                        if assembly.obj_z.location.z > 0:
                            shelf_part.cutpart("Garage_Bottom_KD")
                        else:
                            shelf_part.cutpart("Garage_Top_KD")
                    else:
                        shelf_part.cutpart("Garage_Interior_KD")
                    if abs(sn_unit.meter_to_inch(assembly.obj_z.location.z)) > 0.76:
                        shelf_part.cutpart("Garage_Interior_Shelf")
                        shelf_part.edgebanding("Interior_Edge", l2=True)
                        shelf_part.set_material_pointers("Garage_Interior_Edges", "Edgebanding")
                    elif mat_color_name == "Cosmic Dust" or self.use_black_edge and mat_color_name == "Steel Grey":
                        shelf_part.edgebanding("Black_Edge", l2=True)
                        shelf_part.set_material_pointers("Black", "Edgebanding")
                    else:
                        shelf_part.edgebanding("Exterior_Edge", l2=True)
                        shelf_part.set_material_pointers("Garage_Panel_Edges", "Edgebanding")
            else:
                shelf_part.cutpart("Garage_Interior_Shelf")
                shelf_part.edgebanding("Interior_Edge", l2=True)
                shelf_part.set_material_pointers("Garage_Interior_Edges", "Edgebanding")
        else:
            shelf_part.cutpart("Shelf")
            shelf_part.edgebanding("Edge", l2=True)
            shelf_part.set_material_pointers("Closet_Part_Edges", "Edgebanding")

    def set_cleat_material(self, obj_bp):
        cab_mat_props = self.props_closet_materials
        mat_type = cab_mat_props.materials.get_mat_type()
        cleat_part = sn_types.Part(obj_bp)
        if mat_type.name == "Garage Material":
            if obj_bp.get("IS_COVER_CLEAT"):
                cleat_part.cutpart("Garage_Cover_Cleat")
                cleat_part.edgebanding("Interior_Edge", l1=True)
                cleat_part.set_material_pointers("Garage_Interior_Edges", "Edgebanding")
            elif not obj_bp.get("IS_WALL_CLEAT"):
                cleat_part.cutpart("Garage_Cleat")
                cleat_part.edgebanding("Interior_Edge", l1=True)
                cleat_part.set_material_pointers("Garage_Interior_Edges", "Edgebanding")

        else:
            if obj_bp.get("IS_COVER_CLEAT"):
                cleat_part.cutpart("Cover_Cleat")
                cleat_part.edgebanding("Edge_2", l1=True)
                cleat_part.set_material_pointers("Closet_Part_Edges_Secondary", "Edgebanding")
            else:
                cleat_part.cutpart("Cleat")
                cleat_part.edgebanding("Edge_2", l1=True)
                cleat_part.set_material_pointers("Closet_Part_Edges_Secondary", "Edgebanding")

    def set_back_material(self, obj_bp):
        cab_mat_props = self.props_closet_materials
        mat_type = cab_mat_props.materials.get_mat_type()
        back_part = sn_types.Part(obj_bp)

        if not obj_bp.sn_closets.use_unique_material:
            if mat_type.name == "Garage Material":
                for child in obj_bp.children:
                    if child.snap.type_mesh == 'CUTPART':
                        for mat_slot in child.snap.material_slots:
                            if mat_slot.name == "Full Back Color":
                                mat_slot.pointer_name = "Garage_Interior_Surface"
                back_part.cutpart("Garage_Back")
            else:

                for child in obj_bp.children:
                    if child.snap.type_mesh == 'CUTPART':
                        pointer_name = "Closet_Part_Surfaces"
                        op_num = obj_bp.sn_closets.opening_name

                        if op_num:
                            carcass = sn_types.Assembly(sn_utils.get_closet_bp(obj_bp))

                            if obj_bp.sn_closets.is_top_back_bp:
                                back_type = carcass.get_prompt(
                                    "Opening {} Top Backing Thickness".format(op_num)).get_value()
                            elif obj_bp.sn_closets.is_back_bp:
                                back_type = carcass.get_prompt(
                                    "Opening {} Center Backing Thickness".format(op_num)).get_value()
                            elif obj_bp.sn_closets.is_bottom_back_bp:
                                back_type = carcass.get_prompt(
                                    "Opening {} Bottom Backing Thickness".format(op_num)).get_value()

                            if back_type == 2:
                                pointer_name = "Backing_Cedar"
                                obj_bp["IS_CEDAR_BACK"] = True
                            else:
                                obj_bp["IS_CEDAR_BACK"] = False

                        for mat_slot in child.snap.material_slots:
                            if mat_slot.name == "Full Back Color":
                                mat_slot.pointer_name = pointer_name

                back_part.cutpart("Back")

    def set_drawer_front_material(self, obj_bp):
        cab_mat_props = self.props_closet_materials
        mat_type = cab_mat_props.materials.get_mat_type()
        mat_color_name = cab_mat_props.materials.get_mat_color().name
        drawer_front_part = sn_types.Part(obj_bp)
        custom_colors = cab_mat_props.use_custom_color_scheme

        if mat_type.name == "Garage Material" and not custom_colors:
            drawer_front_part.cutpart("Garage_Slab_Drawer_Front")
            if mat_color_name == "Cosmic Dust" or self.use_black_edge and mat_color_name == "Steel Grey":
                drawer_front_part.edgebanding("Black_Edge", l1=True, w1=True, l2=True, w2=True)
                drawer_front_part.set_material_pointers("Black", "TopBottomEdge")
                drawer_front_part.set_material_pointers("Black", "LeftRightEdge")
            else:
                drawer_front_part.edgebanding("Exterior_Edge", l1=True, w1=True, l2=True, w2=True)
                drawer_front_part.set_material_pointers("Garage_Panel_Edges", "TopBottomEdge")
                drawer_front_part.set_material_pointers("Garage_Panel_Edges", "LeftRightEdge")
        else:
            drawer_front_part.cutpart("Slab_Drawer_Front")
            drawer_front_part.edgebanding('Door_Edges',l1=True, w1=True, l2=True, w2=True)
            drawer_front_part.set_material_pointers("Door_Edge", "TopBottomEdge")
            drawer_front_part.set_material_pointers("Door_Edge", "LeftRightEdge")
    
    def set_glass_color(self, obj_bp):
        cab_mat_props = self.props_closet_materials
        glass_color_name = cab_mat_props.get_glass_color().name
        use_unique_glass_color = obj_bp.sn_closets.use_unique_glass_color
        assembly = sn_types.Assembly(obj_bp)

        door_style = assembly.get_prompt("Door Style")
        if door_style:
            if "Glass" in door_style.get_value():
                if not use_unique_glass_color:
                    glass_color = assembly.get_prompt("Glass Color")
                    if glass_color:
                        glass_color.set_value(glass_color_name)

    def set_countertop_material(self, assembly):
        cab_mat_props = self.props_closet_materials
        mat_type = cab_mat_props.materials.get_mat_type()
        mat_color_name = cab_mat_props.materials.get_mat_color().name
        countertop_part = sn_types.Part(assembly.obj_bp)
        countertop_type = cab_mat_props.countertops.get_type()
        island_assy = sn_types.Assembly(sn_utils.get_island_bp(assembly.obj_bp))
        countertop_type_ppt = island_assy.get_prompt("Countertop Type")
        unique_mat = assembly.obj_bp.sn_closets.use_unique_material

        if countertop_type_ppt and unique_mat:
            ppt_val = countertop_type_ppt.get_value()
            if "Melamine" in countertop_type.name and ppt_val == 0:
                assembly.obj_bp.sn_closets.use_unique_material = False
            if countertop_type.name == "Custom" and ppt_val == 1:
                assembly.obj_bp.sn_closets.use_unique_material = False
            if countertop_type.name == "Granite" and ppt_val == 2:
                assembly.obj_bp.sn_closets.use_unique_material = False
            if countertop_type.name == "HPL" and ppt_val == 3:
                assembly.obj_bp.sn_closets.use_unique_material = False
            if countertop_type.name == "Quartz" and ppt_val == 4:
                assembly.obj_bp.sn_closets.use_unique_material = False
            if countertop_type.name == "Standard Quartz" and ppt_val == 5:
                assembly.obj_bp.sn_closets.use_unique_material = False
            if countertop_type.name == "Wood" and ppt_val == 6:
                assembly.obj_bp.sn_closets.use_unique_material = False

        if not assembly.obj_bp.sn_closets.use_unique_material:
            if mat_type.name == "Garage Material" and "Melamine" in countertop_type.name:
                if mat_color_name == "Cosmic Dust" or self.use_black_edge and mat_color_name == "Steel Grey":
                    countertop_part.edgebanding('Black_Edge', l1=True, l2=True, w1=True, w2=True)
                    countertop_part.set_material_pointers("Black", "Edgebanding")
                else:
                    countertop_part.edgebanding('Exterior_Edge', l1=True, l2=True, w1=True, w2=True)
                    countertop_part.set_material_pointers("Garage_Panel_Edges", "Edgebanding")
            else:
                countertop_part.edgebanding('Edge', l1=True, l2=True, w1=True, w2=True)
                if assembly.obj_bp.sn_closets.is_hpl_top_bp:
                    countertop_part.set_material_pointers("Countertop_HPL_Surface", "Edgebanding")
                else:
                    countertop_part.set_material_pointers("Closet_Part_Edges", "Edgebanding")

            exposed_left = assembly.get_prompt("Exposed Left")
            exposed_right = assembly.get_prompt("Exposed Right")
            exposed_back = assembly.get_prompt("Exposed Back")
            if exposed_left:
                if exposed_left.get_value():
                    for child in assembly.obj_bp.children:
                        if child.snap.type_mesh == 'CUTPART':
                            if mat_type.name == "Garage Material":
                                if mat_color_name == "Cosmic Dust" or self.use_black_edge and mat_color_name == "Steel Grey":
                                    child.snap.edge_w1 = 'Black_Edge'
                                    for mat_slot in child.snap.material_slots:
                                        if mat_slot.name == 'LeftEdge':
                                            mat_slot.pointer_name = "Black"
                                else:
                                    child.snap.edge_w1 = 'Exterior_Edge'
                                    for mat_slot in child.snap.material_slots:
                                        if mat_slot.name == 'LeftEdge':
                                            mat_slot.pointer_name = "Garage_Panel_Edges"
                            else:
                                child.snap.edge_w1 = 'Edge'
                                for mat_slot in child.snap.material_slots:
                                    if mat_slot.name == 'LeftEdge':
                                        mat_slot.pointer_name = "Closet_Part_Edges"
                else:
                    for child in assembly.obj_bp.children:
                        if child.snap.type_mesh == 'CUTPART':
                            child.snap.edge_w1 = ''
                            for mat_slot in child.snap.material_slots:
                                if mat_slot.name == 'LeftEdge':
                                    mat_slot.pointer_name = "Core"
            if exposed_right:
                if exposed_right.get_value():
                    for child in assembly.obj_bp.children:
                        if child.snap.type_mesh == 'CUTPART':
                            if mat_type.name == "Garage Material":
                                if mat_color_name == "Cosmic Dust" or self.use_black_edge and mat_color_name == "Steel Grey":
                                    child.snap.edge_w2 = 'Black_Edge'
                                    for mat_slot in child.snap.material_slots:
                                        if mat_slot.name == 'RightEdge':
                                            mat_slot.pointer_name = "Black"
                                else:
                                    child.snap.edge_w2 = 'Exterior_Edge'
                                    for mat_slot in child.snap.material_slots:
                                        if mat_slot.name == 'RightEdge':
                                            mat_slot.pointer_name = "Garage_Panel_Edges"
                            else:
                                child.snap.edge_w2 = 'Edge'
                                for mat_slot in child.snap.material_slots:
                                    if mat_slot.name == 'RightEdge':
                                        mat_slot.pointer_name = "Closet_Part_Edges"
                else:
                    for child in assembly.obj_bp.children:
                        if child.snap.type_mesh == 'CUTPART':
                            child.snap.edge_w2 = ''
                            for mat_slot in child.snap.material_slots:
                                if mat_slot.name == 'RightEdge':
                                    mat_slot.pointer_name = "Core"

            if exposed_back:
                if exposed_back.get_value():
                    for child in assembly.obj_bp.children:
                        if child.snap.type_mesh == 'CUTPART':
                            if mat_type.name == "Garage Material":
                                if mat_color_name == "Cosmic Dust" or self.use_black_edge and mat_color_name == "Steel Grey":
                                    child.snap.edge_l2 = 'Black_Edge'
                                    for mat_slot in child.snap.material_slots:
                                        if mat_slot.name == 'BackEdge':
                                            mat_slot.pointer_name = "Black"
                                else:
                                    child.snap.edge_l2 = 'Exterior_Edge'
                                    for mat_slot in child.snap.material_slots:
                                        if mat_slot.name == 'BackEdge':
                                            mat_slot.pointer_name = "Garage_Panel_Edges"
                            else:
                                child.snap.edge_l2 = 'Edge'
                                for mat_slot in child.snap.material_slots:
                                    if mat_slot.name == 'BackEdge':
                                        mat_slot.pointer_name = "Closet_Part_Edges"
                else:
                    for child in assembly.obj_bp.children:
                        if child.snap.type_mesh == 'CUTPART':
                            child.snap.edge_l2 = ''
                            for mat_slot in child.snap.material_slots:
                                if mat_slot.name == 'BackEdge':
                                    mat_slot.pointer_name = "Core"

    def set_countertop_material_2(self, obj_bp):
        cab_mat_props = self.props_closet_materials
        mat_type = cab_mat_props.materials.get_mat_type()
        mat_color_name = cab_mat_props.materials.get_mat_color().name
        countertop_type = cab_mat_props.countertops.get_type()
        island_bp = sn_utils.get_island_bp(obj_bp)
        unique_mat = obj_bp.sn_closets.use_unique_material

        if island_bp:
            for child in island_bp.children:
                if "obj_prompts" in child:
                    ct_ppt_obj = child

                    if ct_ppt_obj:
                        if "Countertop Type" in ct_ppt_obj.snap.prompts:
                            countertop_type_ppt = ct_ppt_obj.snap.prompts["Countertop Type"]

                            if countertop_type_ppt and unique_mat:
                                ppt_val = countertop_type_ppt.get_value()
                                if "Melamine" in countertop_type.name and ppt_val == 0:
                                    obj_bp.sn_closets.use_unique_material = False
                                if countertop_type.name == "Custom" and ppt_val == 1:
                                    obj_bp.sn_closets.use_unique_material = False
                                if countertop_type.name == "Granite" and ppt_val == 2:
                                    obj_bp.sn_closets.use_unique_material = False
                                if countertop_type.name == "HPL" and ppt_val == 3:
                                    obj_bp.sn_closets.use_unique_material = False
                                if countertop_type.name == "Quartz" and ppt_val == 4:
                                    obj_bp.sn_closets.use_unique_material = False
                                if countertop_type.name == "Standard Quartz" and ppt_val == 5:
                                    obj_bp.sn_closets.use_unique_material = False
                                if countertop_type.name == "Wood" and ppt_val == 6:
                                    obj_bp.sn_closets.use_unique_material = False

                    break

        if not obj_bp.sn_closets.use_unique_material:
            if mat_type.name == "Garage Material":
                if mat_color_name == "Cosmic Dust" or self.use_black_edge and mat_color_name == "Steel Grey":
                    edgebanding(obj_bp, 'Black_Edge', l1=True, l2=True, w1=True, w2=True)
                    set_material_pointers(obj_bp, "Black", "Edgebanding")
                else:
                    edgebanding(obj_bp, 'Exterior_Edge', l1=True, l2=True, w1=True, w2=True)
                    set_material_pointers(obj_bp, "Garage_Panel_Edges", "Edgebanding")
            else:
                edgebanding(obj_bp, 'Edge', l1=True, l2=True, w1=True, w2=True)
                if obj_bp.sn_closets.is_hpl_top_bp:
                    set_material_pointers(obj_bp, "Countertop_HPL_Surface", "Edgebanding")
                else:
                    set_material_pointers(obj_bp, "Closet_Part_Edges", "Edgebanding")

            exposed_left = None
            exposed_right = None
            exposed_back = None
            ppt_obj = None

            for child in obj_bp.children:
                if "obj_prompts" in child:
                    ppt_obj = child
                    break

            if ppt_obj:
                if "Exposed Left" in ppt_obj.snap.prompts:
                    exposed_left = ppt_obj.snap.prompts["Exposed Left"]
                if "Exposed Right" in ppt_obj.snap.prompts:
                    exposed_right = ppt_obj.snap.prompts["Exposed Right"]
                if "Exposed Back" in ppt_obj.snap.prompts:
                    exposed_back = ppt_obj.snap.prompts["Exposed Back"]

            if exposed_left:
                if exposed_left.get_value():
                    for child in obj_bp.children:
                        if child.snap.type_mesh == 'CUTPART':
                            if mat_type.name == "Garage Material":
                                if mat_color_name == "Cosmic Dust" or self.use_black_edge and mat_color_name == "Steel Grey":
                                    child.snap.edge_w1 = 'Black_Edge'
                                    for mat_slot in child.snap.material_slots:
                                        if mat_slot.name == 'LeftEdge':
                                            mat_slot.pointer_name = "Black"
                                else:
                                    child.snap.edge_w1 = 'Exterior_Edge'
                                    for mat_slot in child.snap.material_slots:
                                        if mat_slot.name == 'LeftEdge':
                                            mat_slot.pointer_name = "Garage_Panel_Edges"
                            else:
                                child.snap.edge_w1 = 'Edge'
                                for mat_slot in child.snap.material_slots:
                                    if mat_slot.name == 'LeftEdge':
                                        mat_slot.pointer_name = "Closet_Part_Edges"
                else:
                    for child in obj_bp.children:
                        if child.snap.type_mesh == 'CUTPART':
                            child.snap.edge_w1 = ''
                            for mat_slot in child.snap.material_slots:
                                if mat_slot.name == 'LeftEdge':
                                    mat_slot.pointer_name = "Core"
            if exposed_right:
                if exposed_right.get_value():
                    for child in obj_bp.children:
                        if child.snap.type_mesh == 'CUTPART':
                            if mat_type.name == "Garage Material":
                                if mat_color_name == "Cosmic Dust" or self.use_black_edge and mat_color_name == "Steel Grey":
                                    child.snap.edge_w2 = 'Black_Edge'
                                    for mat_slot in child.snap.material_slots:
                                        if mat_slot.name == 'RightEdge':
                                            mat_slot.pointer_name = "Black"
                                else:
                                    child.snap.edge_w2 = 'Exterior_Edge'
                                    for mat_slot in child.snap.material_slots:
                                        if mat_slot.name == 'RightEdge':
                                            mat_slot.pointer_name = "Garage_Panel_Edges"
                            else:
                                child.snap.edge_w2 = 'Edge'
                                for mat_slot in child.snap.material_slots:
                                    if mat_slot.name == 'RightEdge':
                                        mat_slot.pointer_name = "Closet_Part_Edges"
                else:
                    for child in obj_bp.children:
                        if child.snap.type_mesh == 'CUTPART':
                            child.snap.edge_w2 = ''
                            for mat_slot in child.snap.material_slots:
                                if mat_slot.name == 'RightEdge':
                                    mat_slot.pointer_name = "Core"

            if exposed_back:
                if exposed_back.get_value():
                    for child in obj_bp.children:
                        if child.snap.type_mesh == 'CUTPART':
                            if mat_type.name == "Garage Material":
                                if mat_color_name == "Cosmic Dust" or self.use_black_edge and mat_color_name == "Steel Grey":
                                    child.snap.edge_l2 = 'Black_Edge'
                                    for mat_slot in child.snap.material_slots:
                                        if mat_slot.name == 'BackEdge':
                                            mat_slot.pointer_name = "Black"
                                else:
                                    child.snap.edge_l2 = 'Exterior_Edge'
                                    for mat_slot in child.snap.material_slots:
                                        if mat_slot.name == 'BackEdge':
                                            mat_slot.pointer_name = "Garage_Panel_Edges"
                            else:
                                child.snap.edge_l2 = 'Edge'
                                for mat_slot in child.snap.material_slots:
                                    if mat_slot.name == 'BackEdge':
                                        mat_slot.pointer_name = "Closet_Part_Edges"
                else:
                    for child in obj_bp.children:
                        if child.snap.type_mesh == 'CUTPART':
                            child.snap.edge_l2 = ''
                            for mat_slot in child.snap.material_slots:
                                if mat_slot.name == 'BackEdge':
                                    mat_slot.pointer_name = "Core"

    def set_wire_basket_material(self, assembly):
        basket_part = sn_types.Part(assembly.obj_bp)
        wire_basket_color_ppt = assembly.get_prompt("Wire Basket Color")
        if wire_basket_color_ppt:
            wire_basket_color = wire_basket_color_ppt.get_value()
            if wire_basket_color == 0:
                basket_part.material('Chrome')
            else:
                basket_part.material('White')

    def set_pull_out_canvas_hamper_material(self, assembly):
        hamper_part = sn_types.Part(assembly.obj_bp)
        basket_color_ppt = assembly.get_prompt("Basket Color")
        if basket_color_ppt:
            basket_color = basket_color_ppt.get_value()
            if basket_color == 0:
                # Black
                hamper_part.material("Black")
            elif basket_color == 1:
                # Matt Aluminum
                hamper_part.material("Aluminum")
            elif basket_color == 2:
                # Matt Nickel
                hamper_part.material("Nickel")
            else:
                # Chrome
                hamper_part.material("Chrome")

    def update_closet_defaults(self, context):
        """
        Currently this function will just update the 1" thick adjustable shelves option when
        Garage Material was just selected, but we can use this to hopefully change closet defaults whenever necessary.
        """
        closet_defaults = context.scene.sn_closets.closet_defaults
        cab_mat_props = self.props_closet_materials
        mat_type = cab_mat_props.materials.get_mat_type()
        if closet_defaults.temp_mat_type_name != mat_type.name:
            if mat_type.name == "Garage Material":
                closet_defaults.thick_adjustable_shelves = True
                exec("bpy.ops.sn_prompt.update_all_prompts_in_scene(prompt_name='Thick Adjustable Shelves', prompt_type='CHECKBOX', bool_value=True)")
            else:
                closet_defaults.thick_adjustable_shelves = False
                exec("bpy.ops.sn_prompt.update_all_prompts_in_scene(prompt_name='Thick Adjustable Shelves', prompt_type='CHECKBOX', bool_value=False)")

            closet_defaults.temp_mat_type_name = mat_type.name

    def set_metal_accessory_material(self, obj_bp):
        assembly = sn_types.Assembly(obj_bp.parent)
        metal_color = assembly.get_prompt("Metal Color")

        if metal_color:
            for child in obj_bp.children:
                for cchild in child.children:
                    for mat_slot in cchild.snap.material_slots:
                        if mat_slot.name == 'Chrome':
                            if metal_color.get_value() == 0:
                                mat_slot.pointer_name = "Chrome"
                            elif metal_color.get_value() == 1:
                                mat_slot.pointer_name = "Aluminum"
                            elif metal_color.get_value() == 2:
                                mat_slot.pointer_name = "Nickel"
                            elif metal_color.get_value() == 3:
                                mat_slot.pointer_name = "Gold"
                            elif metal_color.get_value() == 4:
                                mat_slot.pointer_name = "Bronze"
                            elif metal_color.get_value() == 5:
                                mat_slot.pointer_name = "Slate"
                            elif metal_color.get_value() == 6:
                                mat_slot.pointer_name = "Black"

    def set_panel_material(self, assembly):
        cab_mat_props = self.props_closet_materials
        mat_type = cab_mat_props.materials.get_mat_type()
        mat_color_name = cab_mat_props.materials.get_mat_color().name
        panel_part = sn_types.Part(assembly.obj_bp)
        section_product = sn_types.Assembly(sn_utils.get_closet_bp(assembly.obj_bp))
        opening_qty = 0
        left_end_condition = 'WP'
        right_end_condition = 'WP'

        if section_product and section_product.get_prompt("Opening Quantity"):
            opening_qty = section_product.get_prompt("Opening Quantity").get_value()
            left_end_condition = section_product.get_prompt("Left End Condition").get_value()
            right_end_condition = section_product.get_prompt("Right End Condition").get_value()

        if mat_type.name == "Garage Material":
            # Check left end panel condition
            if panel_part.obj_bp.get('PARTITION_NUMBER') == 0:
                if left_end_condition == 0:  # 0='EP'
                    panel_part.cutpart("Garage_End_Panel")
                else:
                    panel_part.cutpart("Garage_Mid_Panel")
            # Check right end panel condition
            elif panel_part.obj_bp.get('PARTITION_NUMBER') == opening_qty:
                if right_end_condition == 0:  # 0='EP'
                    panel_part.cutpart("Garage_End_Panel")
                else:
                    panel_part.cutpart("Garage_Mid_Panel")
            else:
                panel_part.cutpart("Garage_Mid_Panel")

            if section_product.obj_bp.get("IS_BP_CORNER_SHELVES") or section_product.obj_bp.get("IS_BP_L_SHELVES"):
                door = section_product.get_prompt("Door")
                if door:
                    if not door.get_value():
                        panel_part.set_material_pointers("Garage_Interior_Edges", "FrontBackEdge")
                        panel_part.set_material_pointers("Garage_Interior_Edges", "TopBottomEdge")
                    else:
                        if mat_color_name == "Cosmic Dust" or self.use_black_edge and mat_color_name == "Steel Grey":
                            panel_part.set_material_pointers("Black", "FrontBackEdge")
                            panel_part.set_material_pointers("Black", "TopBottomEdge")
                        else:
                            panel_part.set_material_pointers(
                            "Garage_Panel_Edges", "FrontBackEdge")
                            panel_part.set_material_pointers(
                            "Garage_Panel_Edges", "TopBottomEdge")
                else:
                    if mat_color_name == "Cosmic Dust" or self.use_black_edge and mat_color_name == "Steel Grey":
                        panel_part.set_material_pointers("Black", "FrontBackEdge")
                        panel_part.set_material_pointers("Black", "TopBottomEdge")
                    else:
                        panel_part.set_material_pointers(
                        "Garage_Panel_Edges", "FrontBackEdge")
                        panel_part.set_material_pointers(
                        "Garage_Panel_Edges", "TopBottomEdge")

            else:
                if mat_color_name == "Cosmic Dust" or self.use_black_edge and mat_color_name == "Steel Grey":
                    panel_part.set_material_pointers("Black", "FrontBackEdge")
                    panel_part.set_material_pointers("Black", "TopBottomEdge")
                else:
                    panel_part.set_material_pointers(
                    "Garage_Panel_Edges", "FrontBackEdge")
                    panel_part.set_material_pointers(
                    "Garage_Panel_Edges", "TopBottomEdge")

        else:
            # Set back to closet material pointers, same as common_parts.add_panel
            panel_part.cutpart("Panel")
            panel_part.edgebanding("Edge", l2=True)
            panel_part.edgebanding("Edge_2", w2=True, w1=True)
            panel_part.set_material_pointers("Closet_Part_Edges", "FrontBackEdge")
            panel_part.set_material_pointers("Closet_Part_Edges_Secondary", "TopBottomEdge")

        # 36H or lower have to be edgebanded, but 46.10 doesn't work, so I made it 46.11 and now it does
        if assembly.obj_x.location.x > sn_unit.inch(46.11):
            exposed_bottom = assembly.get_prompt("Exposed Bottom")
            if exposed_bottom:
                if exposed_bottom.get_value():
                    for child in assembly.obj_bp.children:
                        if child.snap.type_mesh == 'CUTPART':
                            if mat_type.name == "Garage Material":
                                if mat_color_name == "Cosmic Dust" or self.use_black_edge and mat_color_name == "Steel Grey":
                                    child.snap.edge_w1 = 'Black_Edge'
                                    child.snap.edge_w2 = 'Black_Edge'
                                    for mat_slot in child.snap.material_slots:
                                        if mat_slot.name == 'TopBottomEdge':
                                            mat_slot.pointer_name = "Black"
                                else:
                                    child.snap.edge_w1 = 'Exterior_Edge'
                                    child.snap.edge_w2 = 'Exterior_Edge'
                                    for mat_slot in child.snap.material_slots:
                                        if mat_slot.name == 'TopBottomEdge':
                                            mat_slot.pointer_name = "Garage_Panel_Edges"
                            else:
                                child.snap.edge_w1 = 'Edge_2'
                                child.snap.edge_w2 = 'Edge_2'
                                for mat_slot in child.snap.material_slots:
                                    if mat_slot.name == 'TopBottomEdge':
                                        mat_slot.pointer_name = "Closet_Part_Edges_Secondary"
                else:
                    for child in assembly.obj_bp.children:
                        if child.snap.type_mesh == 'CUTPART':
                            child.snap.edge_w1 = ''
                            child.snap.edge_w2 = ''
                            slot_name = "TopBottomEdge"

                            if "IS_BP_ISLAND_PANEL" in panel_part.obj_bp:
                                if panel_part.obj_x.location.x > panel_part.obj_y.location.y:
                                    slot_name = "FrontBackEdge"

                            for mat_slot in child.snap.material_slots:
                                if mat_slot.name == slot_name:
                                    mat_slot.pointer_name = "Core"
            else:
                for child in assembly.obj_bp.children:
                    if child.snap.type_mesh == 'CUTPART':
                        child.snap.edge_w1 = ''
                        child.snap.edge_w2 = ''
                        for mat_slot in child.snap.material_slots:
                            if mat_slot.name == 'TopBottomEdge':
                                mat_slot.pointer_name = "Core"
        else:
            for child in assembly.obj_bp.children:
                if child.snap.type_mesh == 'CUTPART':
                    if mat_type.name == "Garage Material":
                        if mat_color_name == "Cosmic Dust" or self.use_black_edge and mat_color_name == "Steel Grey":
                            child.snap.edge_w1 = 'Black_Edge'
                            child.snap.edge_w2 = 'Black_Edge'
                            for mat_slot in child.snap.material_slots:
                                if mat_slot.name == 'TopBottomEdge':
                                    mat_slot.pointer_name = "Black"
                        else:
                            child.snap.edge_w1 = 'Exterior_Edge'
                            child.snap.edge_w2 = 'Exterior_Edge'
                            for mat_slot in child.snap.material_slots:
                                if mat_slot.name == 'TopBottomEdge':
                                    mat_slot.pointer_name = "Garage_Panel_Edges"
                    else:
                        child.snap.edge_w1 = 'Edge_2'
                        child.snap.edge_w2 = 'Edge_2'
                        for mat_slot in child.snap.material_slots:
                            if mat_slot.name == 'TopBottomEdge':
                                mat_slot.pointer_name = "Closet_Part_Edges_Secondary"

    def set_material_pointers(self, obj_bp, material_pointer_name, slot_name=""):
        """
        Sets every material slot for every mesh to the material_pointer_name.

        **Parameters:**

        * **material_pointer_name** (string, (never None)) - Name of the material pointer to assign.

        * **slot_name** (string, (optional)) - If not "" then the material_pointer_name will be assigned to the slot.

        **Returns:** None
        """
        for slot in self.obj_bp.snap.material_slots:
            if slot_name == "":
                slot.pointer_name = material_pointer_name
            elif slot_name == slot.name:
                slot.pointer_name = material_pointer_name
        for child in self.obj_bp.children:
            if child.type == 'MESH':
                if len(child.snap.material_slots) < 1:
                    bpy.ops.sn_material.add_material_pointers(object_name=child.name)
                for slot in child.snap.material_slots:
                    if slot_name == "":
                        slot.pointer_name = material_pointer_name
                    elif slot_name == slot.name:
                        slot.pointer_name = material_pointer_name

    def og_update_assemblies(self, context, use_black_edge, cab_mat_props):
        for assembly in self.scene_assemblies(context):
            props = assembly.obj_bp.sn_closets

            if props.is_panel_bp or assembly.obj_bp.get("IS_BP_MITERED_PARD"):
                # self.set_panel_material(assembly)
                continue

            if props.is_countertop_bp or assembly.obj_bp.get("IS_BP_COUNTERTOP"):
                self.set_countertop_material(assembly)

            # Kitchen countertop color
            if assembly.obj_bp.get("IS_BP_CABINET_COUNTERTOP"):
                countertop_part = sn_types.Part(assembly.obj_bp)
                countertop_part.set_material_pointers("Cabinet_Countertop_Surface", "Countertop Surface")
                countertop_part.cutpart("Panel")

            needed_assemblies = [
                props.is_plant_on_top_bp,  # Topshelf
                props.is_crown_molding,  # Crown
                "IS_FILLER" in assembly.obj_bp,
                "IS_WALL_CLEAT" in assembly.obj_bp
            ]

            if any(needed_assemblies):
                if props.is_plant_on_top_bp or "IS_FILLER" in assembly.obj_bp:
                    exposed_pointer_name = "Black" if use_black_edge else "Closet_Part_Edges"
                    assembly.set_material_pointers(exposed_pointer_name, "Edgebanding")
                elif props.is_crown_molding:
                    exposed_pointer_name = "Black" if use_black_edge else "Closet_Part_Edges_Secondary"
                elif "IS_WALL_CLEAT" in assembly.obj_bp:
                    mat_type = cab_mat_props.materials.get_mat_type()
                    garage_material_black = mat_type.name == 'Garage Material' and use_black_edge
                    exposed_pointer_name = "Black" if garage_material_black else 'Closet_Part_Edges'

                exposed_prompts = [
                    (assembly.get_prompt("Exposed Left"), "LeftEdge"),
                    (assembly.get_prompt("Exposed Right"), "RightEdge"),
                    (assembly.get_prompt("Exposed Back"), "BackEdge"),
                    (assembly.get_prompt("Exposed Front"), "FrontEdge")
                ]

                for child in assembly.obj_bp.children:
                    if child.snap.type_mesh == 'CUTPART':
                        cut_part_mesh = child
                        break

                if cut_part_mesh:
                    for exposed_prompt, mat_slot_name in exposed_prompts:
                        if exposed_prompt:
                            exposed_value = exposed_prompt.get_value()
                            mat_slot = cut_part_mesh.snap.material_slots.get(mat_slot_name)

                            if exposed_prompt.name == "Exposed Front":
                                cut_part_mesh.snap.edge_l1 = 'Edge' if exposed_value else ''

                                # Crown molding
                                if "IS_BP_FLAT_CROWN" in sn_utils.get_bp(assembly.obj_bp, 'INSERT'):
                                    exposed_prompt.set_value(True)

                            elif exposed_prompt.name == "Exposed Back":
                                pass

                            elif exposed_prompt.name == "Exposed Left":
                                cut_part_mesh.snap.edge_w1 = 'Edge' if exposed_value else ''

                            elif exposed_prompt.name == "Exposed Right":
                                cut_part_mesh.snap.edge_w2 = 'Edge' if exposed_value else ''

                            if mat_slot:
                                if exposed_value:
                                    cut_part_mesh.snap.material_slots[mat_slot_name].pointer_name = exposed_pointer_name
                                else:
                                    cut_part_mesh.snap.material_slots[mat_slot_name].pointer_name = "Core"

            # Metal Garage Leg
            if "IS_BP_METAL_LEG" in assembly.obj_bp:
                metal_color = sn_types.Assembly(
                    assembly.obj_bp.parent).get_prompt("Metal Color")
                if metal_color:
                    for child in assembly.obj_bp.children:
                        for mat_slot in child.snap.material_slots:
                            if mat_slot.name == 'Metal':
                                if metal_color.get_value() == 0:
                                    mat_slot.pointer_name = "Steel"
                                elif metal_color.get_value() == 1:
                                    mat_slot.pointer_name = "Black"
                                elif metal_color.get_value() == 2:
                                    mat_slot.pointer_name = "Chrome"

            if "IS_BP_VALET_ROD" in assembly.obj_bp:
                metal_color = assembly.get_prompt("Metal Color")
                if metal_color:
                    for child in assembly.obj_bp.children:
                        for cchild in child.children:
                            for mat_slot in cchild.snap.material_slots:
                                if mat_slot.name == 'Chrome':
                                    if metal_color.get_value() == 0:
                                        mat_slot.pointer_name = "Chrome"
                                    elif metal_color.get_value() == 1:
                                        mat_slot.pointer_name = "Aluminum"
                                    elif metal_color.get_value() == 2:
                                        mat_slot.pointer_name = "Nickel"
                                    elif metal_color.get_value() == 3:
                                        mat_slot.pointer_name = "Gold"
                                    elif metal_color.get_value() == 4:
                                        mat_slot.pointer_name = "Bronze"
                                    elif metal_color.get_value() == 5:
                                        mat_slot.pointer_name = "Slate"
                                    elif metal_color.get_value() == 6:
                                        mat_slot.pointer_name = "Black"

            if "IS_BP_BELT_RACK" in assembly.obj_bp:
                metal_color = assembly.get_prompt("Metal Color")
                if metal_color:
                    for child in assembly.obj_bp.children:
                        for mat_slot in child.snap.material_slots:
                            if mat_slot.name == 'Chrome':
                                if metal_color.get_value() == 0:
                                    mat_slot.pointer_name = "Chrome"
                                elif metal_color.get_value() == 1:
                                    mat_slot.pointer_name = "Aluminum"
                                elif metal_color.get_value() == 2:
                                    mat_slot.pointer_name = "Nickel"
                                elif metal_color.get_value() == 3:
                                    mat_slot.pointer_name = "Gold"
                                elif metal_color.get_value() == 4:
                                    mat_slot.pointer_name = "Bronze"
                                elif metal_color.get_value() == 5:
                                    mat_slot.pointer_name = "Slate"
                                elif metal_color.get_value() == 6:
                                    mat_slot.pointer_name = "Black"

            if "IS_BP_TIE_RACK" in assembly.obj_bp:
                metal_color = assembly.get_prompt("Metal Color")
                if metal_color:
                    for child in assembly.obj_bp.children:
                        for mat_slot in child.snap.material_slots:
                            if mat_slot.name == 'Chrome':
                                if metal_color.get_value() == 0:
                                    mat_slot.pointer_name = "Chrome"
                                elif metal_color.get_value() == 1:
                                    mat_slot.pointer_name = "Aluminum"
                                elif metal_color.get_value() == 2:
                                    mat_slot.pointer_name = "Nickel"
                                elif metal_color.get_value() == 3:
                                    mat_slot.pointer_name = "Gold"
                                elif metal_color.get_value() == 4:
                                    mat_slot.pointer_name = "Bronze"
                                elif metal_color.get_value() == 5:
                                    mat_slot.pointer_name = "Slate"
                                elif metal_color.get_value() == 6:
                                    mat_slot.pointer_name = "Black"

            if assembly.obj_prompts:
                catnum = assembly.get_prompt("CatNum")
                if catnum:
                    assembly.obj_bp.snap.comment_2 = str(
                        int(catnum.get_value()))

            shelves = [
                props.is_shelf_bp,
                assembly.obj_bp.get("IS_SHELF"),
                assembly.obj_bp.get("IS_BP_L_SHELF"),
                assembly.obj_bp.get("IS_BP_ANGLE_SHELF"),
                assembly.obj_bp.get("IS_DOOR_STRIKER")
            ]

            if props.is_door_bp:
                self.set_door_material(assembly)

            elif any(shelves):
                self.set_shelf_material(assembly)

            elif assembly.obj_bp.get("IS_CLEAT"):
                self.set_cleat_material(assembly)

            elif assembly.obj_bp.get("IS_BACK"):
                self.set_back_material(assembly)

            elif props.is_drawer_bottom_bp:
                self.set_drawer_bottom_material(assembly)

            elif props.is_drawer_back_bp or props.is_drawer_side_bp or props.is_drawer_sub_front_bp:
                self.set_drawer_part_material(assembly)

            elif assembly.obj_bp.get("IS_BP_DRAWER_FRONT"):
                self.set_drawer_front_material(assembly)

            elif assembly.obj_bp.get("IS_BP_WIRE_HAMPER"):
                self.set_wire_basket_material(assembly)

            elif assembly.obj_bp.name == "Single Pull Out Canvas Hamper" or assembly.obj_bp.name == "Double Pull Out Canvas Hamper":
                self.set_pull_out_canvas_hamper_material(assembly)

            else:
                self.set_material(assembly)

    def update_assemblies(self, context, use_black_edge, cab_mat_props):
        
        for obj_bp in self.scene_assembly_bps(context):
            props = obj_bp.sn_closets
            is_kb_part = obj_bp.get("IS_KB_PART")

            if not is_kb_part:
                if props.is_panel_bp or obj_bp.get("IS_BP_MITERED_PARD"):
                    assembly = sn_types.Assembly(obj_bp)
                    self.set_panel_material(assembly)
                    # Now also set from carcass prompt UI when height is changed
                    continue

            # Countertop edgebanding
            if props.is_countertop_bp or obj_bp.get("IS_BP_COUNTERTOP"):
                self.set_countertop_material_2(obj_bp)
                continue

            # Kitchen countertop color
            if obj_bp.get("IS_BP_CABINET_COUNTERTOP"):
                countertop_part = sn_types.Part(obj_bp)
                countertop_part.set_material_pointers("Cabinet_Countertop_Surface", "Countertop Surface")
                countertop_part.cutpart("Panel")
                continue

            needed_assemblies = [
                props.is_plant_on_top_bp,  # Topshelf
                props.is_crown_molding,  # Crown
                "IS_FILLER" in obj_bp,
                "IS_WALL_CLEAT" in obj_bp
            ]

            if any(needed_assemblies):
                if props.is_plant_on_top_bp or "IS_FILLER" in obj_bp:
                    assembly = sn_types.Assembly(obj_bp)
                    exposed_pointer_name = "Black" if use_black_edge else "Closet_Part_Edges"
                    assembly.set_material_pointers(exposed_pointer_name, "Edgebanding")

                elif props.is_crown_molding:
                    exposed_pointer_name = "Black" if use_black_edge else "Closet_Part_Edges_Secondary"

                elif "IS_WALL_CLEAT" in obj_bp:
                    mat_type = cab_mat_props.materials.get_mat_type()
                    garage_material_black = mat_type.name == 'Garage Material' and use_black_edge
                    exposed_pointer_name = "Black" if garage_material_black else 'Closet_Part_Edges'

                for child in obj_bp.children:
                    if "obj_prompts" in child:
                        ppt_obj = child
                        cut_part_mesh = None

                        exposed_prompts = []

                        if "Exposed Left" in ppt_obj.snap.prompts:
                            exposed_prompts.append((ppt_obj.snap.prompts["Exposed Left"], "LeftEdge"))
                        if "Exposed Right" in ppt_obj.snap.prompts:
                            exposed_prompts.append((ppt_obj.snap.prompts["Exposed Right"], "RightEdge"))
                        if "Exposed Back" in ppt_obj.snap.prompts:
                            exposed_prompts.append((ppt_obj.snap.prompts["Exposed Back"], "BackEdge"))
                        if "Exposed Front" in ppt_obj.snap.prompts:
                            exposed_prompts.append((ppt_obj.snap.prompts["Exposed Front"], "FrontEdge"))

                        for child in obj_bp.children:
                            if child.snap.type_mesh == 'CUTPART':
                                cut_part_mesh = child
                                break

                        if cut_part_mesh:
                            for exposed_prompt, mat_slot_name in exposed_prompts:
                                if exposed_prompt:
                                    exposed_value = exposed_prompt.get_value()
                                    mat_slot = cut_part_mesh.snap.material_slots.get(mat_slot_name)

                                    if exposed_prompt.name == "Exposed Front":
                                        cut_part_mesh.snap.edge_l1 = 'Edge' if exposed_value else ''

                                        # Crown molding
                                        if "IS_BP_FLAT_CROWN" in sn_utils.get_bp(obj_bp, 'INSERT'):
                                            exposed_prompt.set_value(True)

                                    elif exposed_prompt.name == "Exposed Back":
                                        pass

                                    elif exposed_prompt.name == "Exposed Left":
                                        cut_part_mesh.snap.edge_w1 = 'Edge' if exposed_value else ''

                                    elif exposed_prompt.name == "Exposed Right":
                                        cut_part_mesh.snap.edge_w2 = 'Edge' if exposed_value else ''

                                    if mat_slot:
                                        if exposed_value:
                                            cut_part_mesh.snap.material_slots[mat_slot_name].pointer_name = exposed_pointer_name
                                        else:
                                            cut_part_mesh.snap.material_slots[mat_slot_name].pointer_name = "Core"

                        if "CatNum" in ppt_obj.snap.prompts:
                            catnum = ppt_obj.snap.prompts["CatNum"]
                            if catnum:
                                obj_bp.snap.comment_2 = str(int(catnum.get_value()))

            shelves = [
                props.is_shelf_bp,
                obj_bp.get("IS_SHELF"),
                obj_bp.get("IS_BP_L_SHELF"),
                obj_bp.get("IS_BP_ANGLE_SHELF"),
                obj_bp.get("IS_DOOR_STRIKER")
            ]

            accessories = ["IS_BP_BELT_RACK" in obj_bp,
                           "IS_BP_VALET_ROD" in obj_bp,
                           "IS_BP_TIE_RACK" in obj_bp]

            pullout_hampers = [obj_bp.name == "Single Pull Out Canvas Hamper",
                               obj_bp.name == "Double Pull Out Canvas Hamper"]
            

            if props.is_door_bp and not is_kb_part:
                self.set_door_material(obj_bp)
                door_assembly = sn_types.Assembly(obj_bp)
                if door_assembly.get_prompt("Glass Color"):
                    self.set_glass_color(obj_bp)
                continue

            elif any(shelves) and not is_kb_part:
                assembly = sn_types.Assembly(obj_bp)
                self.set_shelf_material(assembly)

            elif any(accessories):
                self.set_metal_accessory_material(obj_bp)
                continue

            elif obj_bp.get("IS_BP_METAL_LEG"):
                metal_color = sn_types.Assembly(obj_bp.parent).get_prompt("Metal Color")
                if metal_color:
                    for child in obj_bp.children:
                        for mat_slot in child.snap.material_slots:
                            if mat_slot.name == 'Metal':
                                if metal_color.get_value() == 0:
                                    mat_slot.pointer_name = "Steel"
                                elif metal_color.get_value() == 1:
                                    mat_slot.pointer_name = "Black"
                                elif metal_color.get_value() == 2:
                                    mat_slot.pointer_name = "Chrome"

                continue

            elif obj_bp.get("IS_CLEAT"):
                self.set_cleat_material(obj_bp)
                continue

            elif obj_bp.get("IS_BACK") and not is_kb_part:
                self.set_back_material(obj_bp)
                continue

            elif props.is_drawer_bottom_bp:
                self.set_drawer_bottom_material(obj_bp)
                continue

            elif props.is_drawer_back_bp or props.is_drawer_side_bp or props.is_drawer_sub_front_bp:
                assembly = sn_types.Assembly(obj_bp)
                self.set_drawer_part_material(assembly)

            elif obj_bp.get("IS_BP_DRAWER_FRONT") and not is_kb_part:
                self.set_drawer_front_material(obj_bp)
                continue

            elif obj_bp.get("IS_BP_WIRE_HAMPER"):
                assembly = sn_types.Assembly(obj_bp)
                self.set_wire_basket_material(assembly)

            elif any(pullout_hampers):
                assembly = sn_types.Assembly(obj_bp)
                self.set_pull_out_canvas_hamper_material(assembly)

            else:
                self.set_material_2(obj_bp)

    def execute(self, context):
        start_time = time.perf_counter()
        self.closet_props = context.scene.sn_closets
        self.props_closet_materials = context.scene.closet_materials
        self.use_black_edge = self.props_closet_materials.use_black_edge
        cab_mat_props = self.props_closet_materials
        mat_color_name = cab_mat_props.materials.get_mat_color().name
        use_black_edge = (self.use_black_edge and mat_color_name == "Steel Grey") or mat_color_name == "Cosmic Dust"

        if self.only_update_pointers:
            self.update_material_pointers(context)
            self.update_drawer_materials()
        else:
            self.update_drawer_materials()

            # self.og_update_assemblies(context, use_black_edge, cab_mat_props)
            self.update_assemblies(context, use_black_edge, cab_mat_props)
            self.update_material_pointers(context)
            self.update_closet_defaults(context)
            bpy.ops.snap.update_scene_from_pointers()

        print("{}: ASSIGN MATERIALS MAIN Finished updating materials to {} in {} seconds --- ".format(
            self.bl_idname,
            mat_color_name,
            round(time.perf_counter() - start_time, 8)))

        return {'FINISHED'}


class SN_MAT_OT_update_scene_from_pointers(Operator):
    bl_idname = "snap.update_scene_from_pointers"
    bl_label = "Update Scene From Pointers"
    bl_description = "This will update the scene with the updated pointer information."

    def execute(self, context):
        # start_time = time.perf_counter()

        for obj in context.visible_objects:
            obj.location = obj.location

        for obj in bpy.data.objects:
            if obj.type in {'MESH', 'CURVE'}:
                sn_utils.assign_materials_from_pointers(obj)

        # print("{}: Finished updating scene from pointers in {} seconds --- ".format(
        #     self.bl_idname,
        #     round(time.perf_counter() - start_time, 8)))
        return {'FINISHED'}


class SN_MAT_OT_Unpack_Material_Images(Operator):
    bl_idname = "closet_materials.unpack_material_images"
    bl_label = "Unpack Closet Material Images"
    bl_description = ""
    bl_options = {'UNDO'}

    material_files = []
    materials_dir: StringProperty(
        name="Materials Path",
        description="Material directory to unpack",
        subtype='FILE_PATH')

    _timer = None

    item_list = []

    def invoke(self, context, event):
        wm = context.window_manager
        props = context.window_manager.snap
        self.materials_dir = sn_paths.COUNTERTOP_MATERIAL_DIR
        textures_dir = os.path.join(self.materials_dir, "textures")

        if not os.path.exists(textures_dir):
            os.makedirs(textures_dir)

        bpy.ops.sn_library.open_browser_window(
            path=os.path.join(self.materials_dir, "textures"))

        self.item_list = []

        for f in os.listdir(self.materials_dir):
            if ".blend" in f:
                self.item_list.append(f)

        props.total_items = len(self.item_list)
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)

        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        progress = context.window_manager.snap

        if event.type == 'ESC':
            return {'FINISHED'}

        if event.type == 'TIMER':
            if progress.current_item + 1 <= len(self.item_list):
                b_file = self.item_list[progress.current_item]
                mat_file_path = os.path.abspath(
                    os.path.join(self.materials_dir, b_file))
                script = os.path.join(
                    bpy.app.tempdir, 'unpack_material_images.py')
                script_file = open(script, 'w')
                script_file.write("import bpy\n")
                script_file.write(
                    "bpy.ops.file.unpack_all(method='WRITE_LOCAL')\n")
                script_file.close()
                print(bpy.app.binary_path)
                print(mat_file_path)
                print(bpy.app.binary_path + ' "' + mat_file_path +
                      '"' + ' -b --python ' + '"' + script + '"')
                subprocess.call(bpy.app.binary_path + ' "' + mat_file_path +
                                '"' + ' -b --python ' + '"' + script + '"')
                progress.current_item += 1
                if progress.current_item + 1 <= len(self.item_list):
                    header_text = "Processing Item " + \
                        str(progress.current_item + 1) + \
                        " of " + str(progress.total_items)
                    context.area.header_text_set(text=header_text)
            else:
                return self.cancel(context)
        return {'PASS_THROUGH'}

    def cancel(self, context):
        progress = context.window_manager.snap
        progress.current_item = 0
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        context.window.cursor_set('DEFAULT')
        context.area.header_text_set(None)
        return {'FINISHED'}


class SN_MAT_OT_check_mats(Operator):
    bl_idname = "closet_materials.check_mats"
    bl_label = "check_mats"
    bl_description = ""
    bl_options = {'UNDO'}

    def execute(self, context):
        materials_dir = sn_paths.CLOSET_MATERIAL_DIR
        search_directory = os.path.join(
            materials_dir, "Closet Materials")
        tex_directory = os.path.join(search_directory, "textures")

        mat_file_list = []
        tex_list = []

        for f in os.listdir(search_directory):
            if ".blend" in f:
                mat_file_list.append(f.split(".")[0])

        for f in os.listdir(tex_directory):
            tex_list.append(f.split(".")[0])

        for f in os.listdir(search_directory):
            if f.split(".")[0] in tex_list:
                pass
            else:
                print("Material file not in tex dir:", f)

        for f in os.listdir(tex_directory):
            if f.split(".")[0] in mat_file_list:
                pass
            else:
                print("Texture not in material file dir:", f)

        return {'FINISHED'}


class SN_MAT_OT_Create_Material_Library(Operator):
    bl_idname = "closet_materials.create_material_library"
    bl_label = "Create Closet Material Library"
    bl_description = ""
    bl_options = {'UNDO'}

    def execute(self, context):
        materials_dir = sn_paths.COUNTERTOP_MATERIAL_DIR
        tex_directory = os.path.join(materials_dir, "textures")
        template_dir = os.path.join(materials_dir, "template_material")
        new_materials_dir = os.path.join(template_dir, "Materials")
        template_file = os.path.join(
            materials_dir, "template_material", "template_material.blend")

        for image_name in os.listdir(tex_directory):
            tex_file_path = os.path.abspath(
                os.path.join(tex_directory, image_name))

            script = os.path.join(
                bpy.app.tempdir, 'create_material_library.py')
            script_file = open(script, 'w')
            script_file.write("import bpy\n")
            script_file.write(
                "bpy.ops.image.open(filepath=r'" + tex_file_path + "', files=[{'name':'" + image_name + "', 'name':'" + image_name + "'}], relative_path=False, show_multiview=False)\n")
            script_file.write(
                "bpy.data.materials['template_material'].node_tree.nodes['Image Texture'].image = bpy.data.images['" + image_name + "']\n")
            script_file.write(
                "bpy.data.materials['template_material'].name = '" + image_name.split(".")[0] + "'\n")
            script_file.write("bpy.ops.wm.save_as_mainfile(filepath=r'" + os.path.normpath(
                os.path.join(new_materials_dir, image_name.split(".")[0])) + ".blend')\n")

            script_file.close()
            subprocess.call(bpy.app.binary_path + ' "' + template_file +
                            '"' + ' -b --python ' + '"' + script + '"')

        return {'FINISHED'}


class SN_MAT_OT_Sync_Unique_Material_Selection(Operator):
    bl_idname = "closet_materials.sync_unique_material_selection"
    bl_label = "Sync Unique Material Selection"
    bl_description = ""
    bl_options = {'UNDO'}

    object_name: StringProperty(name="Object Name")

    def execute(self, context):
        obj = bpy.data.objects[self.object_name]
        assembly = sn_types.Assembly(sn_utils.get_assembly_bp(obj))
        props = assembly.obj_bp.sn_closets

        if obj.snap.material_slots:
            material_name = obj.material_slots[0].name

            if material_name not in self.get_mat_colors(context, props.unique_mat_types):
                for mat_type in self.get_mat_types(context):
                    colors = self.get_mat_colors(context, mat_type)
                    if material_name in colors:
                        props.unique_mat_types = mat_type
                        props.unique_mat = material_name

        return {'FINISHED'}

    def get_mat_types(self, context):
        mat_type_list = context.scene.closet_materials.materials.get_type_list()
        return [mat_type[0] for mat_type in mat_type_list]

    def get_mat_colors(self, context, unique_mat_types):
        mat_color_list = context.scene.closet_materials.materials.get_mat_color_list(unique_mat_types)
        return [mat_color[0] for mat_color in mat_color_list]


classes = (
    SN_MAT_OT_Poll_Assign_Materials,
    SN_MAT_OT_Assign_Materials,
    SN_MAT_OT_update_scene_from_pointers,
    SN_MAT_OT_Unpack_Material_Images,
    SN_MAT_OT_check_mats,
    SN_MAT_OT_Create_Material_Library,
    SN_MAT_OT_Sync_Unique_Material_Selection
)

register, unregister = bpy.utils.register_classes_factory(classes)

# if __name__ == "__main__":
#     register()
