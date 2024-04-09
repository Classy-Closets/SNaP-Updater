import bpy
from bpy.types import Panel

from snap import sn_types, sn_utils


def get_mat_types():
    mat_type_list = bpy.context.scene.closet_materials.materials.get_type_list()
    return [mat_type[0] for mat_type in mat_type_list]


def get_mat_colors(unique_mat_types):
    mat_color_list = bpy.context.scene.closet_materials.materials.get_mat_color_list(unique_mat_types)
    return [mat_color[0] for mat_color in mat_color_list]


def draw_unique_mats(layout, assembly):
    props = assembly.obj_bp.sn_closets

    parts = [
        props.is_back_bp,
        props.is_bottom_back_bp,
        props.is_top_back_bp,
        props.is_countertop_bp,
        assembly.obj_bp.get("IS_BP_HOOD_BODY"),]

    if any(parts):
        layout.prop(props, "use_unique_material")
        selection_valid = True

        if props.use_unique_material:
            # Check if unique material selection is valid
            # if material is in current material type category
            if not props.is_countertop_bp:
                for obj in assembly.obj_bp.children:
                    if obj.type == 'MESH':
                        if obj.snap.material_slots:
                            material_name = obj.material_slots[0].name
                            if material_name not in get_mat_colors(props.unique_mat_types):
                                selection_valid = False
                                for mat_type in get_mat_types():
                                    colors = get_mat_colors(mat_type)
                                    if material_name in colors:
                                        layout.operator(
                                            "closet_materials.sync_unique_material_selection",
                                            text="Sync Unique Material Selection").object_name = obj.name
                            else:
                                selection_valid = True

            if selection_valid:
                if "(Discontinued)" in props.unique_mat:
                    warning_box = layout.box()
                    msg = 'Discontinued. Not available for new customers.'
                    warning_box.label(text=msg, icon='ERROR')

                if props.is_countertop_bp:
                    island_bp = sn_utils.get_island_bp(assembly.obj_bp)
                    island_assy = sn_types.Assembly(island_bp)
                    island_countertop_type = island_assy.get_prompt("Countertop Type")

                    parent_assembly = sn_types.Assembly(assembly.obj_bp.parent)
                    parent_countertop_type = parent_assembly.get_prompt("Countertop Type")

                    if island_countertop_type:
                        ct_types = {
                            '0': 'Melamine',
                            '1': 'Custom',
                            '2': 'Granite',
                            '3': 'HPL',
                            "4": "Quartz",
                            "5": "Standard Quartz",
                            "6": "Wood"}

                        ct_type = ct_types[str(island_countertop_type.get_value())]

                        if ct_type == "Custom":
                            col = layout.column()
                            col.prop(props, "custom_countertop_color", text="Color")
                            col.prop(props, "custom_countertop_name", text="Name")
                            col.prop(props, "custom_countertop_vendor", text="Vendor")
                            col.prop(props, "custom_countertop_color_code", text="Color Code")
                            col.prop(props, "custom_countertop_price", text="Price")
                            return
                        if ct_type == "Standard Quartz":
                            layout.label(text="Standard Quartz Color:")
                            layout.prop(props, "unique_countertop_standard_quartz", text="")
                            return

                    if "COUNTERTOP_MELAMINE" in assembly.obj_bp:
                        layout.label(text="Type:")
                        col = layout.column(align=True)
                        col.prop(props, "unique_mat_types", text="")
                        layout.label(text="Color:")
                        layout.prop(props, "unique_mat", text="")
                        return

                    if "COUNTERTOP_HPL" in assembly.obj_bp:
                        layout.label(text="Manufactuer:")
                        layout.prop(props, "unique_countertop_hpl_mfg", text="")
                        layout.label(text="HPL Color:")
                        layout.prop(props, "unique_countertop_hpl", text="")
                        return

                    if "COUNTERTOP_GRANITE" in assembly.obj_bp:
                        layout.label(text="Granite Color:")
                        layout.prop(props, "unique_countertop_granite", text="")
                        return

                    if "COUNTERTOP_QUARTZ" in assembly.obj_bp:
                        if parent_countertop_type:
                            if parent_countertop_type.get_value() == 5:
                                layout.label(text="Standard Quartz Color:")
                                layout.prop(props, "unique_countertop_standard_quartz", text="")
                                return
                            else:
                                layout.label(text="Quartz Manufactuer:")
                                layout.prop(props, "unique_countertop_quartz_mfg", text="")
                                layout.label(text="Quartz Color:")
                                layout.prop(props, "unique_countertop_quartz", text="")
                                return
                        else:
                            layout.label(text="Quartz Manufactuer:")
                            layout.prop(props, "unique_countertop_quartz_mfg", text="")
                            layout.label(text="Quartz Color:")
                            layout.prop(props, "unique_countertop_quartz", text="")
                            return

                    if parent_countertop_type:
                        if "COUNTERTOP_WOOD" in assembly.obj_bp and parent_countertop_type.get_value() != 5:
                            row = layout.row()
                            row.label(text="Countertop Type")
                            layout.prop(props, "wood_countertop_types", text="")

                            if not props.wood_countertop_types == 'Butcher Block':
                                layout.label(text="Wood Color:")
                                layout.prop(props, "unique_countertop_wood", text="")
                            return
                    elif "COUNTERTOP_WOOD" in assembly.obj_bp:
                        row = layout.row()
                        row.label(text="Countertop Type")
                        layout.prop(props, "wood_countertop_types", text="")

                        if not props.wood_countertop_types == 'Butcher Block':
                            layout.label(text="Wood Color:")
                            layout.prop(props, "unique_countertop_wood", text="")
                        return

                elif assembly.obj_bp.get("IS_BP_HOOD_BODY"):
                    row = layout.row()
                    row.label(text="Hood Material Type")
                    row.prop(props, "upgrade_options", text="")
                    row = layout.row()
                    row.label(text="Color:")
                    row.prop(props, "unique_upgrade_color", text="")

                else:
                    row = layout.row()
                    row.label(text="Backing Material Type")
                    layout.prop(props, "unique_mat_types", text="")
                    row = layout.row()

                    if props.unique_mat_types == 'Upgrade Options':
                        row.label(text="Option:")
                        layout.prop(props, "upgrade_options", text="")
                        layout.prop(props, "unique_upgrade_color", text="")
                    else:
                        row.label(text="Backing Material Color:")
                        layout.prop(props, "unique_mat", text="")

def draw_unique_glass(layout, assembly):
    props = assembly.obj_bp.sn_closets

    if assembly.obj_bp.get("IS_DOOR"):
        door_style = assembly.get_prompt("Door Style")
        if door_style:
            if "Glass" in door_style.get_value():
                layout.prop(props, "use_unique_glass_color")

                if props.use_unique_glass_color:
                    row = layout.row()
                    if "Melamine" in door_style.get_value():
                        row.label(text="Unique Melamine Glass Color:")
                        layout.prop(props, "unique_melamine_glass_color", text="")
                    else:
                        row.label(text="Unique Glass Color:")
                        layout.prop(props, "unique_glass_color", text="")


class SNAP_PT_closet_options(Panel):
    bl_label = "Room Defaults"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 3

    props = None

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='PREFERENCES')

    def draw(self, context):
        self.props = bpy.context.scene.sn_closets
        self.props.draw(self.layout)


class SNAP_PT_Closet_Properties(Panel):
    bl_label = "Room Properties"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Item"
    bl_context = "objectmode"
    bl_order = 1

    props = None

    def draw_shelf_interface(self, layout, shelf, context):
        material_props = context.scene.closet_materials
        mat_type = material_props.materials.get_mat_type()
        is_lock_shelf_ppt = shelf.get_prompt("Is Locked Shelf")
        is_bottom_exposed_kd_prompt = shelf.get_prompt("Is Bottom Exposed KD")
        is_forced_locked_shelf = shelf.get_prompt("Is Forced Locked Shelf")
        if is_forced_locked_shelf:
            if not is_forced_locked_shelf.get_value():
                box = layout.box()
                if is_lock_shelf_ppt:
                    is_lock_shelf_ppt.draw(box)
                    # box.prop(shelf.obj_bp.snap, "is_locked_shelf", text="Is Locked Shelf")
                if is_bottom_exposed_kd_prompt:
                    if is_lock_shelf_ppt.get_value() and mat_type.name == "Garage Material":
                        box.prop(shelf.obj_bp.snap, "is_bottom_exposed_kd", text="Is Bottom Exposed KD")
            else:
                box = layout.box()
                box.label(text="Is Forced Locked Shelf")
                if is_bottom_exposed_kd_prompt:
                    if is_lock_shelf_ppt.get_value() and mat_type.name == "Garage Material":
                        box.prop(shelf.obj_bp.snap, "is_bottom_exposed_kd", text="Is Bottom Exposed KD")
        else:
            if is_lock_shelf_ppt:
                box = layout.box()
                if is_lock_shelf_ppt:
                    is_lock_shelf_ppt.draw(box)
                    # box.prop(shelf.obj_bp.snap, "is_locked_shelf", text="Is Locked Shelf")
                if is_bottom_exposed_kd_prompt:
                    if is_lock_shelf_ppt.get_value() and mat_type.name == "Garage Material":
                        box.prop(shelf.obj_bp.snap, "is_bottom_exposed_kd", text="Is Bottom Exposed KD")

    def draw_header(self, context):
        layout = self.layout

    def draw_product_props(self, layout, obj_product_bp):
        product = sn_types.Assembly(obj_product_bp)
        row = layout.row(align=True)
        row.label(text="Product: " + product.obj_bp.snap.name_object, icon='OUTLINER_OB_LATTICE')
        row = layout.row(align=True)
        row.operator(
            "sn_closets.copy_product", text="Copy Product", icon='PASTEDOWN')
        row.operator(
            'sn_closets.delete_closet', text="Delete Product", icon='X')

    def draw_insert_props(self, layout, obj_insert_bp):
        insert = sn_types.Assembly(obj_insert_bp)
        row = layout.row(align=True)
        row.label(text="Insert: " + insert.obj_bp.snap.name_object, icon='STICKY_UVS_LOC')
        row = layout.row(align=True)
        row.operator("sn_closets.copy_insert", text="Copy Insert", icon='PASTEDOWN')
        row.operator('sn_closets.delete_closet_insert', text="Delete Insert", icon='X')

    def draw_assembly_props(self, layout, obj_assembly_bp, context):
        assembly = sn_types.Assembly(obj_assembly_bp)
        row = layout.row(align=True)
        row.label(text="Part: " + assembly.obj_bp.snap.name_object, icon='OUTLINER_DATA_LATTICE')
        if assembly.obj_bp.get("ALLOW_PART_DELETE"):
            row = layout.row()
            row.operator(
                'sn_closets.delete_part',
                text="Delete Part - {}".format(assembly.obj_bp.snap.name_object),
                icon='X')
        self.draw_shelf_interface(layout, assembly, context)
        draw_unique_mats(layout, assembly)
        draw_unique_glass(layout, assembly)

    def draw(self, context):
        layout = self.layout
        obj_product_bp = sn_utils.get_bp(context.object, 'PRODUCT')
        obj_insert_bp = sn_utils.get_bp(context.object, 'INSERT')
        obj_assembly_bp = sn_utils.get_assembly_bp(context.object)

        col = layout.column(align=True)
        box = col.box()
        if obj_product_bp:
            self.draw_product_props(box, obj_product_bp)
        else:
            box.label(text="No Product Selected", icon='OUTLINER_DATA_LATTICE')
        box = col.box()
        if obj_insert_bp:
            self.draw_insert_props(box, obj_insert_bp)
        else:
            box.label(text="No Insert Selected", icon='STICKY_UVS_LOC')
        box = col.box()
        if obj_assembly_bp:
            self.draw_assembly_props(box, obj_assembly_bp, context)
        else:
            box.label(text="No Part Selected", icon='OUTLINER_DATA_LATTICE')

classes = (
    SNAP_PT_closet_options,
    SNAP_PT_Closet_Properties
)

register, unregister = bpy.utils.register_classes_factory(classes)
