from os import path

import bpy

from snap import sn_types
from snap import sn_paths
from snap.libraries.closets import closet_paths
from snap.libraries.closets.common import common_parts as closet_parts


CABINET_PANEL = path.join(sn_paths.KITCHEN_BATH_ASSEMBLIES, "Cabinet Panel.blend")
PART_WITH_FRONT_EDGEBANDING = path.join(closet_paths.get_closet_assemblies_path(), "Part with Edgebanding.blend")
PART_WITH_NO_EDGEBANDING = path.join(closet_paths.get_closet_assemblies_path(), "Part with No Edgebanding.blend")
FULL_BACK = path.join(closet_paths.get_closet_assemblies_path(), "Full Back.blend")
FACE = path.join(closet_paths.get_closet_assemblies_path(), "Face.blend")


def add_panel(assembly, island_panel=False):
    panel = sn_types.Part(assembly.add_assembly_from_file(CABINET_PANEL))
    assembly.add_assembly(panel)
    panel.obj_bp['IS_BP_ASSEMBLY'] = True
    panel.obj_bp['IS_BP_PANEL'] = True
    panel.obj_bp['IS_KB_PART'] = True
    props = panel.obj_bp.sn_closets
    props.is_panel_bp = True  # TODO: remove
    panel.set_name("Partition")
    panel.add_prompt("CatNum", 'QUANTITY', 0)

    # Machining info
    panel.add_prompt("Left Depth", 'DISTANCE', 0)
    panel.add_prompt("Right Depth", 'DISTANCE', 0)
    panel.add_prompt("Stop Drilling Bottom Left", 'DISTANCE', 0)
    panel.add_prompt("Stop Drilling Top Left", 'DISTANCE', 0)
    panel.add_prompt("Stop Drilling Bottom Right", 'DISTANCE', 0)
    panel.add_prompt("Stop Drilling Top Right", 'DISTANCE', 0)
    panel.cutpart("Panel")
    panel.edgebanding("Edge", l2=True)
    panel.set_material_pointers("Closet_Part_Edges", "FrontBackEdge")

    for child in panel.obj_bp.children:
        if child.snap.type_mesh == 'CUTPART':
            child.snap.use_multiple_edgeband_pointers = True
            child.snap.delete_protected = True

    return panel


def add_kd_shelf(assembly):
    defaults = bpy.context.scene.sn_closets.closet_defaults
    shelf = sn_types.Part(assembly.add_assembly_from_file(PART_WITH_FRONT_EDGEBANDING))
    assembly.add_assembly(shelf)
    shelf.obj_bp['IS_SHELF'] = True
    shelf.obj_bp['IS_KB_PART'] = True
    props = shelf.obj_bp.sn_closets
    props.is_shelf_bp = True
    shelf.set_name("Shelf")
    shelf.add_prompt("CatNum", 'QUANTITY', 0)
    shelf.add_prompt("Shelf Pin Qty", 'QUANTITY', 0)
    shelf.add_prompt("Cam Qty", 'QUANTITY', 0)
    shelf.add_prompt("Is Locked Shelf", 'CHECKBOX', True)
    # shelf.add_prompt("Is Forced Locked Shelf", 'CHECKBOX', False)
    # shelf.add_prompt("Is Bottom Exposed KD", 'CHECKBOX', False)
    shelf.add_prompt("Adj Shelf Clip Gap", 'DISTANCE', defaults.adj_shelf_clip_gap)
    shelf.add_prompt("Adj Shelf Setback", 'DISTANCE', defaults.adj_shelf_setback)
    shelf.add_prompt("Locked Shelf Setback", 'DISTANCE', defaults.locked_shelf_setback)
    shelf.add_prompt("Drill On Top", 'CHECKBOX', False)
    shelf.add_prompt("Remove Left Holes", 'CHECKBOX', False)
    shelf.add_prompt("Remove Right Holes", 'CHECKBOX', False)
    shelf.cutpart("Shelf")
    shelf.edgebanding('Edge', l2=True)
    return shelf


def add_back(assembly):
    backing = sn_types.Part(assembly.add_assembly_from_file(FULL_BACK))
    assembly.add_assembly(backing)
    backing.obj_bp.snap.comment_2 = "1037"
    backing.obj_bp['IS_BP_ASSEMBLY'] = True
    backing.obj_bp["IS_BACK"] = True
    backing.obj_bp['IS_KB_PART'] = True
    props = backing.obj_bp.sn_closets
    props.is_back_bp = True
    backing.set_name("Backing")
    backing.cutpart("Back")
    return backing


def add_door(assembly):
    door = sn_types.Part(assembly.add_assembly_from_file(FACE))
    assembly.add_assembly(door)
    door.set_name("Door")
    door.cutpart("Slab_Door")
    door.edgebanding('Door_Edges', l1=True, w1=True, l2=True, w2=True)
    door.add_prompt("CatNum", 'QUANTITY', 1006)
    door.add_prompt("Door Type", 'COMBOBOX', 0, ['Base','Tall','Upper'])
    door.add_prompt("Door Swing", 'COMBOBOX', 0, ['Left','Right','Top','Bottom'])
    door.add_prompt("No Pulls", 'CHECKBOX', False)
    door.obj_bp['IS_DOOR'] = True
    door.obj_bp['IS_KB_PART'] = True
    obj_props = door.obj_bp.sn_closets
    obj_props.is_door_bp = True  # TODO: remove
    obj_props.door_type = 'FLAT'
    return door


def add_drawer_front(assembly):
    front = sn_types.Part(assembly.add_assembly_from_file(FACE))
    assembly.add_assembly(front)
    front.obj_bp.snap.comment_2 = "1007"
    front.set_name("Drawer Face")
    front.cutpart("Slab_Drawer_Front")
    front.add_prompt("No Pulls", 'CHECKBOX', False)
    front.add_prompt("Use Double Pulls", 'CHECKBOX', False)
    front.add_prompt("Center Pulls on Drawers", 'CHECKBOX', False)
    front.add_prompt("Drawer Pull From Top", 'DISTANCE', 0)
    front.edgebanding('Door_Edges',l1=True, w1=True, l2=True, w2=True)
    front.obj_bp.snap.is_cabinet_drawer_front = True  # TODO: Remove
    front.obj_bp.snap.comment = "Melamine Drawer Face"
    obj_props = front.obj_bp.sn_closets
    obj_props.door_type = 'FLAT'
    obj_props.is_drawer_front_bp = True  # TODO: Remove
    front.obj_bp["IS_BP_DRAWER_FRONT"] = True
    front.obj_bp['IS_KB_PART'] = True
    return front


def add_false_front(assembly):
    false_front = sn_types.Part(assembly.add_assembly_from_file(FACE))
    assembly.add_assembly(false_front)
    false_front.set_name("False Front")
    false_front.obj_bp['IS_BP_DRAWER_FRONT'] = True
    false_front.obj_bp['IS_BP_FALSE_FRONT'] = True
    false_front.obj_bp['IS_KB_PART'] = True
    return false_front


def add_filler(assembly):
    part = closet_parts.add_filler(assembly)
    part.obj_bp['IS_KB_PART'] = True
    return part


def add_toe_kick(assembly):
    kick = sn_types.Part(assembly.add_assembly_from_file(PART_WITH_NO_EDGEBANDING))
    assembly.add_assembly(kick)
    kick.obj_bp.snap.comment_2 = "1034"
    kick.obj_bp['IS_BP_TOE_KICK'] = True
    kick.obj_bp['IS_KB_PART'] = True
    props = kick.obj_bp.sn_closets
    props.is_toe_kick_bp = True
    kick.set_name("Toe Kick")
    kick.cutpart("Toe_Kick")
    return kick


def add_drawer_partition(assembly):
    part = sn_types.Part(assembly.add_assembly_from_file(PART_WITH_NO_EDGEBANDING))
    assembly.add_assembly(part)
    part.obj_bp['IS_BP_DRAWER_PART'] = True
    part.obj_bp['DRILL_22MM_FROM_TOP'] = True
    part.obj_bp['IS_KB_PART'] = True
    # part.obj_bp.snap.comment_2 = "1034"
    # props = part.obj_bp.sn_closets
    # props.is_toe_kick_bp = True
    part.set_name("Drawer Partition")
    part.cutpart("Panel")
    part.obj_bp.sn_closets.is_panel_bp = True

    # Machining info
    part.add_prompt("Left Depth", 'DISTANCE', 0)
    part.add_prompt("Right Depth", 'DISTANCE', 0)
    part.add_prompt("Stop Drilling Bottom Left", 'DISTANCE', 0)
    part.add_prompt("Stop Drilling Top Left", 'DISTANCE', 0)
    part.add_prompt("Stop Drilling Bottom Right", 'DISTANCE', 0)
    part.add_prompt("Stop Drilling Top Right", 'DISTANCE', 0)
    part.cutpart("Panel")
    part.edgebanding("Edge", l2=True)
    part.set_material_pointers("Closet_Part_Edges", "FrontBackEdge")

    for child in part.obj_bp.children:
        if child.snap.type_mesh == 'CUTPART':
            child.snap.use_multiple_edgeband_pointers = True
            child.snap.delete_protected = True

    return part
