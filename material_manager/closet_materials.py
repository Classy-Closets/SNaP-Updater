import inspect
import time

import bpy
from bpy.types import (
    Panel,
    PropertyGroup,
)
from bpy.props import (
    IntProperty,
    BoolProperty,
    PointerProperty,
    CollectionProperty,
    EnumProperty,
    StringProperty
)
from snap import sn_types
from snap import sn_unit
from snap import sn_db
from snap import sn_utils
from snap.material_manager import property_groups
from snap.libraries.closets.data import data_closet_carcass_island


enum_items_kd_fitting = []
enum_items_location_code = []


def update_stain_color(self, context):
    if not self.main_tabs == 'STAIN':
        return
    else:
        mat_color_name = self.materials.get_mat_color().name
        stain_colors = self.get_stain_colors()

        if mat_color_name in stain_colors:
            self.stain_color_index = self.stain_colors.find(mat_color_name)
            return
        if mat_color_name == "Cafe Au Lait (Cabinet Almond)":
            self.stain_color_index = self.stain_colors.find("Almond")
            return
        elif mat_color_name == "Bridal Shower (Antique White) Δ":
            self.stain_color_index = self.stain_colors.find("Warm Spring")
            return
        else:
            self.stain_color_index = self.stain_colors.find("Winter White (Oxford White)")
            bpy.ops.snap.message_box(
                'INVOKE_DEFAULT',
                message='"{}" is not an available stain color!'.format(mat_color_name),
                icon='INFO')


def update_material_and_edgeband_colors(self, context):
    start_time = time.perf_counter()

    assign_materials = self.color_change
    self.color_change = False
    mat_color_name = self.materials.get_mat_color().name
    mat_type = self.materials.get_mat_type()
    stain_colors = self.get_stain_colors()
    paint_colors = self.get_paint_colors()
    moderno_colors = self.get_moderno_colors()
    self.discontinued_color = ""
    self.edge_discontinued_color = ""
    self.cleat_edge_discontinued_color = ""
    self.dd_mat_discontinued_color = ""
    self.dd_edge_discontinued_color = ""
    self.stain_discontinued_color = ""

    if not self.use_custom_color_scheme and self.defaults_set:
        self.set_all_material_colors()

    elif self.use_custom_color_scheme:
        self.set_default_upgrade_selection()

    if mat_type.name == "Garage Material":
        steel_grey_black_edge = mat_color_name == "Steel Grey" and self.use_black_edge
        cosmic_dust = mat_color_name == "Cosmic Dust"
        if steel_grey_black_edge or cosmic_dust:
            self.set_edge("Black")
        if mat_color_name == "Cafe Au Lait" and not self.use_custom_color_scheme:
            self.set_edge(mat_color_name)
        if mat_color_name == "Danish Maple" and not self.use_custom_color_scheme:
            self.set_edge("Hardrock Maple")
        if mat_color_name == "Winter White" and not self.use_custom_color_scheme:
            self.set_edge("Winter White")

    # Paint/Stain
    elif mat_type.name == "Upgrade Options":
        previous_upgrade_index = self.upgrade_type_index

        # Available in paint or stain
        if mat_color_name == "Onyx":
            if previous_upgrade_index == 1:
                self.upgrade_type_index = 1
                self.paint_color_index = self.paint_colors.find(mat_color_name)
            else:
                self.upgrade_type_index = 2
                self.stain_color_index = self.stain_colors.find(mat_color_name)

        # Stain
        elif mat_color_name in stain_colors:
            self.upgrade_type_index = 2
            self.stain_color_index = self.stain_colors.find(mat_color_name)

        # Paint
        else:
            self.upgrade_type_index = 1
            self.paint_color_index = self.paint_colors.find("Winter White")

            if (mat_color_name == "Snow Drift" or mat_color_name == "Mountain Peak") and not self.use_custom_color_scheme:
                self.paint_color_index = self.paint_colors.find("Winter White")

            elif mat_color_name == "Bridal Shower (Antique White) Δ" and not self.use_custom_color_scheme:
                self.paint_color_index = self.paint_colors.find("Warm Spring")

            elif mat_color_name in paint_colors:
                self.paint_color_index = self.paint_colors.find(mat_color_name)

    # Moderno
    if mat_color_name in moderno_colors:
        self.moderno_color_index = self.moderno_colors.find(mat_color_name)
        return

    # Garage material "Use Black EB"
    update_black_edge = False

    if self.use_black_edge != self.prv_use_black_edge:
        update_black_edge = True
        self.prv_use_black_edge = self.use_black_edge

    if assign_materials or update_black_edge:
        try:
            bpy.ops.closet_materials.poll_assign_materials()
            self.color_change = False
        except Exception:
            pass

    print("update_material_and_edgeband_colors finished. Time --- {} seconds ---".format(round(time.perf_counter() - start_time, 8)))


def update_render_materials(self, context):
    if self.color_change:
        try:
            bpy.ops.closet_materials.poll_assign_materials()
        except Exception:
            pass


def update_kb_render_materials(self, context):
    bpy.ops.closet_materials.poll_assign_materials()


def enum_kd_fitting(self, context):
    if context is None:
        return []

    if len(enum_items_kd_fitting) > 1:
        return enum_items_kd_fitting

    else:
        conn = sn_db.connect_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT\
                *\
            FROM\
                {CCItems}\
            WHERE\
                ProductType == 'HW' AND\
                Name LIKE '{}'\
            ;".format("%" + "KD - FF" + "%", CCItems="CCItems_" + sn_utils.get_franchise_location())
        )

        rows = cursor.fetchall()

        for row in rows:
            enum_items_kd_fitting.append((row[0], row[2], row[2]))

        conn.close()

        return enum_items_kd_fitting


def update_countertops(self, context):
    ct_type = self.countertops.get_type()
    visible_objects = [obj for obj in context.view_layer.objects if obj.visible_get()]
    countertop_bp = [
        obj.parent for obj in visible_objects
        if obj.type == 'MESH' and obj.parent and "IS_BP_COUNTERTOP" in obj.parent]

    for obj in countertop_bp:
        parent_assy = sn_types.Assembly(obj.parent)
        assy = sn_types.Assembly(obj)
        ct_type_ppt = None
        island = False

        if not assy and parent_assy:
            return

        if "IS_BP_ISLAND" in parent_assy.obj_bp:
            carcass = data_closet_carcass_island.Closet_Island_Carcass(parent_assy.obj_bp)
            ct_type_ppt = carcass.get_prompt("Countertop Type")
            island = True

        else:
            countertop = sn_types.Assembly(parent_assy.obj_bp)
            ct_type_ppt = countertop.get_prompt("Countertop Type")

        room_type_hpl = ct_type.name in ("HPL", "Custom")
        is_hpl_assy = "COUNTERTOP_HPL" in assy.obj_bp

        # Enure HPL countertop thickness formula is correct
        if room_type_hpl and is_hpl_assy:
            if assy.obj_z.location.z != sn_unit.inch(1.5):
                if ct_type_ppt:
                    Countertop_Type = ct_type_ppt.get_var()
                    assy.dim_z("IF(Countertop_Type==1,INCH(0.75),INCH(1.5))", [Countertop_Type])

        if ct_type_ppt and not obj.sn_closets.use_unique_material:
            ct_type_ppt.set_value(context.scene.closet_materials.ct_type_index)

        if island:
            carcass.add_countertop()

    self.color_change = True
    update_render_materials(self, context)


def set_color_index(self, context):
    ct_type = self.countertops.get_type()
    countertop_mfgs = ct_type.manufactuers

    if len(countertop_mfgs) > 0:
        ct_mfg = ct_type.manufactuers[self.ct_mfg_index]

        for i, color in enumerate(ct_mfg.colors):
            self.ct_stain_color_index = i
            break


def get_mat_types(self, context):
    return context.scene.closet_materials.materials.get_type_list()


def get_kb_base_mat_colors(self, context):
    return context.scene.closet_materials.materials.get_mat_color_list(self.kb_base_mat_types)


def get_kb_upper_mat_colors(self, context):
    return context.scene.closet_materials.materials.get_mat_color_list(self.kb_upper_mat_types)


def get_kb_island_mat_colors(self, context):
    return context.scene.closet_materials.materials.get_mat_color_list(self.kb_island_mat_types)


class SN_MAT_PT_Closet_Materials_Interface(Panel):
    """Panel to Store all of the Material Options"""
    bl_label = "Room Materials"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 4

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='MATERIAL')

    def draw(self, context):
        layout = self.layout
        props = context.scene.closet_materials
        props.draw(layout)


class Edges(PropertyGroup):
    edge_types: bpy.props.StringProperty(name="Edge Types")


class SnapMaterialSceneProps(PropertyGroup):
    """
    Closet Materials
    """
    main_tabs: EnumProperty(
        name="Closet Material Tabs",
        items=[('MATERIAL', "Material", ""),
               ('COUNTERTOP', "Countertop", ""),
               ('HARDWARE', "Hardware", ""),
               ('DOORS_AND_DRAWER_FACES', "Upgraded Door & Drawer Faces", ""),
               ('MOLDING',"Molding",'Show the molding options.'),
               ('GLASS', "Glass", "")],
        default='MATERIAL',
        update=update_stain_color)

    use_custom_color_scheme: BoolProperty(
        name="Use Custom edge and color scheme",
        description="Use Custom edge and color scheme.",
        default=False,
        update=update_material_and_edgeband_colors)

    use_black_edge: BoolProperty(
        name="Use Black edge",
        description="Use Black edge",
        default=False,
        update=update_material_and_edgeband_colors)

    prv_use_black_edge: BoolProperty(default=False)

    default_color = "Winter White"
    default_edge_color = "Winter White"
    default_paint_color = "Winter White"
    default_mat_type = "Solid Color Smooth Finish"
    default_edge_type = "1mm Dolce"
    default_glass_color = "Clear"
    default_kb_countertop_color = "White Aurora"
    defaults_set: BoolProperty(name="Default materials have been set", default=False)
    color_change: BoolProperty(name="Material Color Updated", default=False)

    materials: PointerProperty(type=property_groups.Materials)
    mat_type_index: IntProperty(name="Material Type Index", default=0)
    mat_color_index: IntProperty(name="Material Color Index", default=0, update=update_material_and_edgeband_colors)

    solid_color_index: IntProperty(name="Solid Smooth Material Color Index", default=0, update=update_material_and_edgeband_colors)
    grain_color_index: IntProperty(name="Grain Smooth Material Color Index", default=0, update=update_material_and_edgeband_colors)
    solid_tex_color_index: IntProperty(name="Solid Textured Material Color Index", default=0, update=update_material_and_edgeband_colors)
    grain_tex_color_index: IntProperty(name="Grain Textured Material Color Index", default=0, update=update_material_and_edgeband_colors)
    linen_color_index: IntProperty(name="Linen Material Color Index", default=0, update=update_material_and_edgeband_colors)
    matte_color_index: IntProperty(name="Matte Material Color Index", default=0, update=update_material_and_edgeband_colors)
    garage_color_index: IntProperty(name="Garage Material Color Index", default=0, update=update_material_and_edgeband_colors)
    oversized_color_index: IntProperty(name="Oversized Material Color Index", default=0, update=update_material_and_edgeband_colors)

    use_kb_color_scheme: BoolProperty(name="Use Kitchen & Bath Color Scheme", default=False)
    kb_base_mat_types: EnumProperty(name="Base Cabinet Material Type", items=get_mat_types, update=update_kb_render_materials)
    kb_upper_mat_types: EnumProperty(name="Upper Cabinet Material Type", items=get_mat_types, update=update_kb_render_materials)
    kb_island_mat_types: EnumProperty(name="Island Cabinet Material Type", items=get_mat_types, update=update_kb_render_materials)

    kb_base_mat: EnumProperty(name="Base Cabinet Material Type", items=get_kb_base_mat_colors, update=update_kb_render_materials)
    kb_upper_mat: EnumProperty(name="Unique Material Type", items=get_kb_upper_mat_colors, update=update_kb_render_materials)
    kb_island_mat: EnumProperty(name="Unique Material Type", items=get_kb_island_mat_colors, update=update_kb_render_materials)

    edges: PointerProperty(type=property_groups.Edges)
    edge_type_index: IntProperty(name="Edge Type Index", default=0)
    edge_color_index: IntProperty(name="Edge Color Index", default=0, update=update_render_materials)

    secondary_edges: PointerProperty(type=property_groups.SecondaryEdges)
    secondary_edge_type_index: IntProperty(name="Secondary Edge Type Index", default=0)
    secondary_edge_color_index: IntProperty(name=" Secondary Edge Color Index", default=0, update=update_render_materials)

    door_drawer_edges: PointerProperty(type=property_groups.DoorDrawerEdges)
    door_drawer_edge_type_index: IntProperty(name="Door/Drawer Edge Type Index", default=0)
    door_drawer_edge_color_index: IntProperty(name="Door/Drawer Edge Color Index", default=0, update=update_render_materials)

    door_drawer_materials: PointerProperty(type=property_groups.DoorDrawerMaterials)
    door_drawer_mat_type_index: IntProperty(name="Door/Drawer Material Type Index", default=0)
    door_drawer_mat_color_index: IntProperty(name="Door/Drawer Material Color Index", default=0, update=update_render_materials)

    dd_solid_color_index: IntProperty(name="DD Solid Smooth Material Color Index", default=0, update=update_material_and_edgeband_colors)
    dd_grain_color_index: IntProperty(name="DD Grain Smooth Material Color Index", default=0, update=update_material_and_edgeband_colors)
    dd_solid_tex_color_index: IntProperty(name="DD Solid Textured Material Color Index", default=0, update=update_material_and_edgeband_colors)
    dd_grain_tex_color_index: IntProperty(name="DD Grain Textured Material Color Index", default=0, update=update_material_and_edgeband_colors)
    dd_linen_color_index: IntProperty(name="DD Linen Material Color Index", default=0, update=update_material_and_edgeband_colors)
    dd_matte_color_index: IntProperty(name="DD Matte Material Color Index", default=0, update=update_material_and_edgeband_colors)
    dd_garage_color_index: IntProperty(name="DD Garage Material Color Index", default=0, update=update_material_and_edgeband_colors)
    dd_oversized_color_index: IntProperty(name="DD Oversized Material Color Index", default=0, update=update_material_and_edgeband_colors)

    countertops: PointerProperty(type=property_groups.Countertops)
    ct_type_index: IntProperty(name="Countertop Type Index", default=0, update=update_countertops)
    ct_mfg_index: IntProperty(name="Countertop Manufactuer Index", default=0, update=set_color_index)
    ct_color_index: IntProperty(name="Countertop Color Index", default=0, update=update_render_materials)
    # Standard Quartz countertop colors: "Marbella" and "Nimbus" were removed 2.6.0 -> 2.6.1
    ct_updated_to_261: BoolProperty(name="Standard Quartz countertop colors updated to 2.6.1", default=False)
    pull_sel_updated_to_261: BoolProperty(name="Pull selection updated to 2.6.1", default=False)

    upgrade_options: PointerProperty(type=property_groups.UpgradeOptions)
    upgrade_type_index: IntProperty(name="Upgrade Type Index", default=0)

    stain_colors: CollectionProperty(type=property_groups.StainColor)
    stain_color_index: IntProperty(name="Stain Color List Index", default=0, update=update_render_materials)

    paint_colors: CollectionProperty(type=property_groups.PaintColor)
    paint_color_index: IntProperty(name="Paint Color List Index", default=0, update=update_render_materials)

    five_piece_melamine_door_colors: CollectionProperty(type=property_groups.FivePieceMelamineDoorColor)
    five_piece_melamine_door_mat_color_index: IntProperty(name="Five Piece Melamine Door Color List Index", default=6, update=update_render_materials)

    ct_stain_colors: CollectionProperty(type=property_groups.StainColor)
    ct_stain_color_index: IntProperty(name="Countertop Stain Color List Index", default=0, update=update_render_materials)
    ct_paint_colors: CollectionProperty(type=property_groups.PaintColor)
    ct_paint_color_index: IntProperty(name="Countertop Paint Color List Index", default=0, update=update_render_materials)

    glaze_colors: CollectionProperty(type=property_groups.GlazeColor)
    glaze_color_index: IntProperty(name="Glaze Color List Index", default=0, update=update_render_materials)
    glaze_styles: CollectionProperty(type=property_groups.GlazeStyle)
    glaze_style_index: IntProperty(name="Glaze Style List Index", default=0)

    moderno_colors: CollectionProperty(type=property_groups.DoorColor)
    moderno_color_index: IntProperty(name="Door Color List Index", default=0, update=update_render_materials)

    glass_colors: CollectionProperty(type=property_groups.GlassColor)
    glass_color_index: IntProperty(name="Glass Color List Index", default=0, update=update_render_materials)

    backing_veneer_color: CollectionProperty(type=property_groups.BackingVeneerColor)
    color_conversions: CollectionProperty(type=property_groups.ColorConversions)
    discontinued_color: StringProperty(name="Main Material Discontinued Color", default="")
    edge_discontinued_color: StringProperty(name="Edge Discontinued Color", default="")
    cleat_edge_discontinued_color: StringProperty(name="Cleat Edge Discontinued Color", default="")
    dd_mat_discontinued_color: StringProperty(name="Door Drawer Material Discontinued Color", default="")
    dd_edge_discontinued_color: StringProperty(name="Door Drawer Edge Discontinued Color", default="")
    stain_discontinued_color: StringProperty(name="Stain Discontinued Color", default="")

    wire_basket_colors: EnumProperty(
        name="Wire Basket Color",
        items=(
            ('CHROME', 'Chrome', "Chrome"),
            ('WHITE', 'White', "White")
        ),
        default='CHROME'
    )

    kd_fitting_color: EnumProperty(
        name="KD Fitting Color",
        items=enum_kd_fitting,
    )

    drawer_slides: CollectionProperty(type=property_groups.DrawerSlide)
    drawer_slide_index: IntProperty(name="Drawer Slide List Index", default=0)

    def check_render_mats(self):
        ct_type = self.countertops.get_type()
        butcher_block = ct_type.name == "Wood" and len(ct_type.manufactuers) < 0

        try:
            edge = self.edges.get_edge_color().has_render_mat
            edge2 = self.secondary_edges.get_edge_color().has_render_mat
            mat = self.materials.get_mat_color().has_render_mat

            if not butcher_block:
                ct = self.countertops.color_has_render_mat()
            else:
                ct = True

            if all((edge, edge2, mat, ct)):
                return True
            else:
                return False
        except:
            return False

    def get_edge_description(self, obj=None, assembly=None, part_name=None):
        type_code = self.edges.get_edge_type().type_code
        color_code = self.edges.get_edge_color().color_code

        name = sn_db.query_db(
            "SELECT\
                Description\
            FROM\
                {CCItems}\
            WHERE ProductType = 'EB' AND TypeCode = '{type_code}' AND ColorCode = '{color_code}';\
            ".format(type_code=type_code, color_code=color_code, CCItems="CCItems_" + sn_utils.get_franchise_location())
        )

        if len(name) == 0:
            print(
                "No SKU found for - Edge Type Code: {} Color Code: {}".format(type_code, color_code))
            return "Unknown"
        elif len(name) == 1:
            return name[0][0]
        else:
            print(
                "Multiple SKUs found for - Edge Type Code: {} Color Code: {}".format(type_code, color_code))
            print(name)
            return "Unknown"

    def get_edge_sku(self, obj=None, assembly=None, part_name=None):
        type_code = self.edges.get_edge_type().type_code
        color_code = self.edges.get_edge_color().color_code
        obj_props = assembly.obj_bp.sn_closets
        custom_colors = bpy.context.scene.closet_materials.use_custom_color_scheme

        countertop_parts = [
            obj_props.is_countertop_bp,
            obj_props.is_hpl_top_bp
            ]

        door_drawer_parts = [
            obj_props.is_door_bp,
            obj_props.is_drawer_front_bp,
            obj_props.is_hamper_front_bp
        ]

        drawer_box_parts = [
            obj_props.is_drawer_back_bp,
            obj_props.is_drawer_side_bp,
            obj_props.is_drawer_bottom_bp,
            obj_props.is_drawer_sub_front_bp,
        ]

        # 1/2 Melamine drawer box parts
        if any(drawer_box_parts):
            box_type_ppt = assembly.get_prompt("Box Type")
            if box_type_ppt:
                if box_type_ppt.get_value() == 0:
                    return "EB-0000316"  # 1/2 White EB

        # There is no edgebanding for garage colors, so we have to hardcode in alternate edgebanding.
        if self.materials.get_mat_type().type_code == 1:
            sku = self.get_garage_edge_sku(obj, assembly, part_name)
            if sku != "Unknown":
                return sku

            elif not custom_colors:
                # Remove unicode characters from color name
                color_name_clean = self.materials.get_mat_color().name.encode("ascii", "ignore").lstrip()
                color_name = color_name_clean.decode()
                if color_name == "Cafe Au Lait":
                    return "EB-0000311"
                elif color_name == "Steel Grey":
                    return "EB-0000331" if not self.use_black_edge else "EB-0000324"
                elif color_name == "Cosmic Dust":
                    return "EB-0000324"
                elif color_name == "Danish Maple":
                    return "EB-0000333"
                else:
                    return "EB-0000338"

        # Stain/Paint EB
        if self.materials.get_mat_type().name == "Upgrade Options":
            return "EB-0000433"  # EB Alder Veneer 1MM

        if any(door_drawer_parts):
            type_code = self.door_drawer_edges.get_edge_type().type_code
            color_code = self.door_drawer_edges.get_edge_color().color_code

        # Countertops with Unique Material
        if any(countertop_parts):
            if obj_props.use_unique_material and 'Melamine' not in part_name:
                mat_type = self.materials.mat_types[obj_props.unique_mat_types]
                mat_name = sn_utils.get_unique_material_name(obj_props.unique_mat, assembly.obj_bp)
                type_code = mat_type.type_code
                if type_code == 5: # Change EB typecode to old 1037 to locate in CCItems
                    type_code = 1037
                color_code = mat_type.colors[mat_name].color_code

        # 1/2 Melamine drawer box parts
        if any(drawer_box_parts):
            box_type_ppt = assembly.get_prompt("Box Type")
            parent_assembly = None
            parent_box_type_ppt = None
            if assembly.obj_bp.parent:
                parent_assembly = sn_types.Assembly(assembly.obj_bp.parent)
            if parent_assembly:
                parent_box_type_ppt = parent_assembly.get_prompt("Box Type")

            if box_type_ppt:
                if box_type_ppt.get_value() == 0:
                    return "EB-0000316"  # 1/2 White EB
            elif parent_box_type_ppt:
                if parent_box_type_ppt.get_value() == 0:
                    return "EB-0000316"  # 1/2 White EB

        if assembly.obj_bp.get("IS_BP_FILE_RAIL"):
            return "EB-0000316"  # 1/2 White EB

        sku = sn_db.query_db(
            "SELECT\
                SKU\
            FROM\
                {CCItems}\
            WHERE ProductType = 'EB' AND TypeCode = '{type_code}' AND ColorCode = '{color_code}';\
            ".format(type_code=type_code, color_code=color_code, CCItems="CCItems_" + sn_utils.get_franchise_location())
        )

        if len(sku) == 0:
            print(
                "No SKU found for - Edge Type Code: {} Color Code: {}".format(type_code, color_code))
            return "Unknown"
        elif len(sku) == 1:
            return sku[0][0]
        else:
            print(
                "Multiple SKUs found for - Edge Type Code: {} Color Code: {}".format(type_code, color_code))
            print(sku)
            return "Unknown"

    def get_secondary_edge_sku(self, obj=None, assembly=None, part_name=None):
        type_code = self.secondary_edges.get_edge_type().type_code
        color_code = self.secondary_edges.get_edge_color().color_code

        # There is no edgebanding for garage colors, so we have to hardcode in alternate edgebanding.
        if self.materials.get_mat_type().type_code == 1:
            sku = self.get_garage_edge_sku(obj, assembly, part_name)
            if sku != "Unknown":
                return sku
            # Remove unicode characters from color name
            color_name_clean = self.materials.get_mat_color().name.encode("ascii", "ignore").lstrip()
            color_name = color_name_clean.decode()
            if color_name == "Cafe Au Lait (Cabinet Almond)":
                return "EB-0000311"
            elif color_name == "Steel Grey (Fog Grey)":
                return "EB-0000331"
            elif color_name == "Cosmic Dust (Graphite Spectrum)":
                return "EB-0000324"
            elif color_name == "Danish Maple (Hard Rock Maple)":
                return "EB-0000333"
            else:
                return "EB-0000338"

        # Stain/Paint EB
        if self.materials.get_mat_type().name == "Upgrade Options":
            return "EB-0000433"  # EB Alder Veneer 1MM

        sku = sn_db.query_db(
            "SELECT\
                SKU\
            FROM\
                {CCItems}\
            WHERE ProductType = 'EB' AND TypeCode = '{type_code}' AND ColorCode = '{color_code}';\
            ".format(type_code=type_code, color_code=color_code, CCItems="CCItems_" + sn_utils.get_franchise_location())
        )

        if len(sku) == 0:
            print("No SKU found for - Edge Type Code: {} Color Code: {}".format(type_code, color_code))
            return "Unknown"
        elif len(sku) == 1:
            return sku[0][0]
        else:
            print("Multiple SKUs found for - Edge Type Code: {} Color Code: {}".format(type_code, color_code))
            print(sku)
            return "Unknown"

    def get_edge_inventory_name(self, sku="", display_name=True):
        if sku:
            edge_sku = sku
        else:
            edge_sku = self.get_edge_sku(None, None, None)

        if sku == "EB-0000316":
            return "Winter White (Oxford White)"

        # search_col = "DisplayName" if display_name else "Description"
        search_col = "Description"
        edge_name = sn_db.query_db(
            "SELECT\
                {col}\
            FROM\
                {CCItems}\
            WHERE\
                SKU == '{sku}';\
            ".format(sku=edge_sku, col=search_col, CCItems="CCItems_" + sn_utils.get_franchise_location())
        )

        if len(edge_name) == 0:
            print(
                "No Name found for - Material SKU: {sku}".format(sku=edge_sku))
            return "Unknown"
        elif len(edge_name) == 1:
            return edge_name[0][0]
        else:
            print(
                "Multiple Names found for - Material SKU: {sku}".format(sku=edge_sku))
            print(edge_name)
            return "Unknown"

    def get_garage_edge_sku(self, obj=None, assembly=None, part_name=None):
        part_thickness = 0
        type_code = self.edges.get_edge_type().type_code
        cutpart_name = ""
        mat_type = self.materials.get_mat_type()

        interior_edged_parts = [
            "Garage_Interior_Shelf",
            "Garage_Cleat",
            "Garage_Cover_Cleat"
        ]

        if assembly:
            for child in assembly.obj_bp.children:
                if child.snap.type_mesh == 'CUTPART':
                    cutpart_name = child.snap.cutpart_name

        if obj:
            part_thickness = sn_unit.meter_to_inch(sn_utils.get_part_thickness(obj))
            if obj.snap.type_mesh == 'CUTPART':
                cutpart_name = obj.snap.cutpart_name

        # This is to look for our 1" thick white edgebanding
        if part_thickness == 1:
            sku = sn_db.query_db(
                "SELECT\
                    SKU\
                FROM\
                    {CCItems}\
                WHERE ProductType = 'EB' AND TypeCode = '{type_code}' AND ColorCode = {color_code};\
                ".format(type_code=3047, color_code = 110100, CCItems="CCItems_" + sn_utils.get_franchise_location())
            )
            if len(sku) == 0:
                print(
                    "No SKU found for - Edgeband Type Code: {} Winter White (Oxford White)".format(type_code))
                return "Unknown"
            elif len(sku) == 1:
                return sku[0][0]
            else:
                print(
                    "Multiple SKUs found for - Edgeband Type Code: {} Winter White (Oxford White)".format(type_code))
                print(sku)
                return "Unknown"

        if cutpart_name == "Garage_Cleat":
            return "EB-0000338"

        elif cutpart_name == "Garage_Cover_Cleat":
            return "EB-0000316"
        
        elif cutpart_name in "Garage_Interior_Shelf":
            sku = sn_db.query_db(
                "SELECT\
                    SKU\
                FROM\
                    {CCItems}\
                WHERE ProductType = 'EB' AND TypeCode = '{type_code}' AND DisplayName LIKE 'Winter White (Oxford White)';\
                ".format(type_code=type_code, CCItems="CCItems_" + sn_utils.get_franchise_location())
            )
            if len(sku) == 0:
                print(
                    "No SKU found for - Edgeband Type Code: {} Winter White (Oxford White)".format(type_code))
                return "Unknown"
            elif len(sku) == 1:
                return sku[0][0]
            else:
                print(
                    "Multiple SKUs found for - Edgeband Type Code: {} Winter White (Oxford White)".format(type_code))
                print(sku)
                return "Unknown"
        else:
            return "Unknown"

    def get_mat_sku(self, obj=None, assembly=None, part_name=None):
        # print(obj, assembly, part_name)
        mat_type = self.materials.get_mat_type()
        type_code = mat_type.type_code
        color_name = self.materials.get_mat_color().name
        part_thickness = 0

        # Type Code 1 is a temp code for Garage Materials because Garage Materials share 15200 with standard melamine material
        if type_code == 1:
            sku = self.get_garage_material_sku(obj, assembly, part_name)
            if sku != "Unknown":
                return sku
            type_code = 8

        if type_code == 2 and color_name == "Cafe Au Lait (Cabinet Almond)":
            type_code = 15200

        if type_code == 15225 and (color_name != "Winter White (Oxford White)" and color_name != "Cafe Au Lait (Cabinet Almond)"):  # Need to change type code for oversized materials that are not White or Almond to the Textured Type Code
            type_code = 15150

        if obj:
            part_thickness = sn_unit.meter_to_inch(sn_utils.get_part_thickness(obj))

        if type_code == 10:  # Upgrade Options
            if not obj:
                if self.upgrade_options.get_type().name == "Stain":
                    prod_type = 'S'
                else:
                    prod_type = 'PL'

                sku = sn_db.query_db(
                    "SELECT\
                        SKU\
                    FROM\
                        {CCItems}\
                    WHERE ProductType in ('{prod_type}') AND TypeCode = 0 AND ColorCode = 0 AND DisplayName LIKE '{name}';\
                    ".format(name=color_name, prod_type=prod_type, CCItems="CCItems_" + sn_utils.get_franchise_location())
                )

                if len(sku) == 0:
                    print("No SKU found for - Material Type Code: {} Color Code: {}".format(type_code, 0))
                    return "Unknown"
                elif len(sku) == 1:
                    return sku[0][0]
                else:
                    print("Multiple SKUs found for - Material Type Code: {} Color Code: {}".format(type_code, 0))
                    print(sku)
                    return "Unknown"

            is_wood_door = obj.snap.type_mesh == 'BUYOUT'
            is_drawer_bottom = "IS_BP_DRAWER_BOTTOM" in assembly.obj_bp

            if not is_wood_door and not is_drawer_bottom:
                if part_thickness == 0.75 or part_thickness == 0:
                    if self.upgrade_options.get_type().name == "Stain":
                        return "VN-0000014"
                    else:
                        return "WD-0000010"

                elif part_thickness == 0.25:
                    if self.upgrade_options.get_type().name == "Stain":
                        return "VN-0000004"
                    else:
                        return "WD-0000007"

        else:
            color_code = self.materials.get_mat_color().color_code

        if assembly:
            obj_props = assembly.obj_bp.sn_closets

            drawer_box_parts = [
                obj_props.is_drawer_back_bp,
                obj_props.is_drawer_side_bp,
                obj_props.is_drawer_bottom_bp,
                obj_props.is_drawer_sub_front_bp,
                obj_props.is_file_rail_bp
            ]

            backing_parts = [
                obj_props.is_back_bp,
                obj_props.is_top_back_bp,
                obj_props.is_bottom_back_bp
            ]

            door_drawer_parts = [
                obj_props.is_door_bp,
                obj_props.is_drawer_front_bp,
                obj_props.is_hamper_front_bp
            ]

            glass_shelf_parts = [
                obj_props.is_glass_shelf_bp
            ]

            shelf_lip_parts = [
                obj_props.is_shelf_lip_bp,
                obj_props.is_deco_shelf_lip_bp
            ]

            countertop_parts = [
                obj_props.is_countertop_bp,
                obj_props.is_hpl_top_bp
            ]

            if any(door_drawer_parts):
                door_style = assembly.get_prompt("Door Style")

                if door_style:
                    if "Traviso" in door_style.get_value() or "Melamine Door Glass" in door_style.get_value():
                        if self.get_five_piece_melamine_door_color().name != 'None':
                            return self.get_five_piece_melamine_door_color().sku

                    elif door_style.get_value() != "Slab Door" and door_style.get_value() != "Melamine Door Glass":
                        if obj.snap.material_slots:
                            door_color = obj.snap.material_slots[0].item_name
                            if door_color:
                                if self.upgrade_options.get_type().name == "Stain":
                                    has_stain = door_color in self.get_stain_colors()
                                    if has_stain:
                                        return self.stain_colors[door_color].sku
                                else:
                                    has_paint = door_color in self.get_paint_colors()
                                    if has_paint:
                                        return self.paint_colors[door_color].sku

                    elif door_style.get_value() == "Slab Door":
                        if type_code == 10:
                            if self.upgrade_options.get_type().name == "Stain":
                                return "VN-0000014"
                            else:
                                return "WD-0000010"

                mat_type = self.door_drawer_materials.get_mat_type()
                type_code = mat_type.type_code
                color_code = self.door_drawer_materials.get_mat_color().color_code
                color_name = self.door_drawer_materials.get_mat_color().name
                # This is usually only ever necessary if the user selects Garage Material for Doors when Custom Color Scheme is selected
                if type_code == 1:
                    sku = self.get_garage_material_sku(obj, assembly, part_name)
                    if sku != "Unknown":
                        return sku
                    type_code = 8

            if any(backing_parts):
                if obj_props.use_unique_material:
                    mat_type = self.materials.mat_types[obj_props.unique_mat_types]
                    mat_name = sn_utils.get_unique_material_name(obj_props.unique_mat, assembly.obj_bp)
                    color_code = mat_type.colors[mat_name].color_code

            if any(drawer_box_parts):
                box_type_ppt = assembly.get_prompt("Box Type")
                parent_assembly = None
                parent_box_type_ppt = None
                if assembly.obj_bp.parent:
                    parent_assembly = sn_types.Assembly(assembly.obj_bp.parent)
                if parent_assembly:
                    parent_box_type_ppt = parent_assembly.get_prompt("Box Type")
                
                use_dovetail_construction = assembly.get_prompt("Use Dovetail Construction")

                box_type = 0
                if box_type_ppt:
                    box_type = box_type_ppt.get_value()
                elif parent_box_type_ppt:
                    box_type = parent_box_type_ppt.get_value()

                if use_dovetail_construction:
                    if use_dovetail_construction.get_value() or box_type == 2:
                        if obj_props.is_drawer_bottom_bp:
                            sku = 'BB-0000004'  # WHITE PAPER 3/8 G1
                        else:
                            material_name = 'BBBB PREFINISH RIP ' + str(round(sn_unit.meter_to_inch(assembly.obj_y.location.y), 2))
                            sku = sn_db.query_db(
                                "SELECT\
                                    SKU\
                                FROM\
                                    {CCItems}\
                                WHERE\
                                    ProductType IN ('BB') AND\
                                    Name LIKE '%{material_name}%' \
                                ;\
                                ".format(CCItems="CCItems_" + sn_utils.get_franchise_location(), material_name=material_name)
                            )

                            if len(sku) == 0:
                                return "Unknown"
                            elif len(sku) == 1:
                                return sku[0][0]
                            else:
                                print("Multiple SKUs found for: ", material_name)
                                print(sku)
                                return "Unknown"
                    elif box_type == 1:
                        if obj_props.is_drawer_bottom_bp:
                            sku = 'PM-0000002'  # WHITE PAPER 3/8 G1
                        else:
                            sku = sn_db.query_db(
                                "SELECT\
                                    SKU\
                                FROM\
                                    {CCItems}\
                                WHERE ProductType in ('PM', 'WD') AND TypeCode = '{type_code}' AND ColorCode = '{color_code}';\
                                ".format(type_code=type_code, color_code=color_code, CCItems="CCItems_" + sn_utils.get_franchise_location())
                            )

                            if len(sku) == 0:
                                print("No SKU found for - Material Type Code: {} Color Code: {}".format(type_code, color_code))
                                return "Unknown"
                            elif len(sku) == 1:
                                print(sku[0][0])
                                return sku[0][0]
                            else:
                                print("Multiple SKUs found for - Material Type Code: {} Color Code: {}".format(type_code, color_code))
                                print(sku)
                                return "Unknown"
                    else:
                        if obj_props.is_drawer_bottom_bp:
                            sku = 'PM-0000002'  # WHITE PAPER 3/8 G1
                        else:
                            sku = 'PM-0000004'  # WHITE  PAPER 1/2 G2
                else:
                    if obj_props.is_drawer_bottom_bp:
                        sku = 'PM-0000002'  # WHITE PAPER 3/8 G1
                    elif obj_props.is_file_rail_bp:
                        parent_assembly = None
                        parent_box_type_ppt = None
                        parent_box_type = -1
                        if assembly.obj_bp.parent:
                            parent_assembly = sn_types.Assembly(assembly.obj_bp.parent)
                        if parent_assembly:
                            parent_box_type_ppt = parent_assembly.get_prompt("Box Type")
                            if parent_box_type_ppt:
                                parent_box_type = parent_box_type_ppt.get_value()
                            if parent_box_type == 2:
                                material_name = 'BBBB PREFINISH RIP 9.73'
                                sku = sn_db.query_db(
                                    "SELECT\
                                        SKU\
                                    FROM\
                                        {CCItems}\
                                    WHERE\
                                        ProductType IN ('BB') AND\
                                        Name LIKE '%{material_name}%' \
                                    ;\
                                    ".format(CCItems="CCItems_" + sn_utils.get_franchise_location(), material_name=material_name)
                                )
                                if len(sku) == 0:
                                    return "Unknown"
                                elif len(sku) == 1:
                                    return sku[0][0]
                                else:
                                    print("Multiple SKUs found for: ", material_name)
                                    print(sku)
                                    return "Unknown"
                            else:
                                sku = 'PM-0000004'  # WHITE  PAPER 1/2 G2
                        else:
                            sku = 'PM-0000004'  # WHITE  PAPER 1/2 G2
                    else:
                        sku = 'PM-0000004'  # WHITE  PAPER 1/2 G2
                return sku

            if any(glass_shelf_parts):
                glass_color = 'Clear'
                part_thickness = round(part_thickness, 2)
                sku = sn_db.query_db(
                    "SELECT\
                        SKU\
                    FROM\
                        {CCItems}\
                    WHERE\
                        ProductType IN ('GL') AND\
                        Thickness == '{thickness}' AND\
                        Name LIKE '%{glass_color}%'\
                    ;\
                    ".format(glass_color=glass_color, thickness=part_thickness, CCItems="CCItems_" + sn_utils.get_franchise_location())
                )

                if glass_color == 'None':
                    print("Glass color not selected. Sku determined by thickness: {}".format(part_thickness))
                    if part_thickness == 0.125:
                        return 'GL-0000003'
                    if part_thickness == 0.25:
                        return 'GL-0000004'
                    if part_thickness == 0.38:
                        return 'GL-0000006'
                    if part_thickness == 0.5:
                        return "GL-0000008"
                if len(sku) == 0:
                    print("SKU match not found for selected glass parts - Glass Color: {} Material Thickness: {}".format(glass_color, part_thickness))
                    print("Special order Sku returned: SO-0000001")
                    return 'SO-0000001'
                elif len(sku) == 1:
                    return sku[0][0]
                else:
                    print("Multiple SKUs found for - Glass Color: {} Material Thickness: {}".format(glass_color, part_thickness))
                    print("Default sku returned: " + str(sku[0][0]))
                    return sku[0][0]

            if any(countertop_parts):
                countertop_type = None
                if assembly:
                    parent_assembly = sn_types.Assembly(assembly.obj_bp.parent)
                    if parent_assembly:
                        countertop_type = parent_assembly.get_prompt("Countertop Type")
                if obj_props.use_unique_material:
                    if 'Quartz' in part_name:
                        color = "None"
                        if countertop_type.get_value() == 4:
                            color = obj_props.unique_countertop_quartz
                        elif countertop_type.get_value() == 5:
                            color = obj_props.unique_countertop_standard_quartz
                        sku = sn_db.query_db(
                        "SELECT\
                            SKU\
                        FROM\
                            {CCItems}\
                        WHERE\
                            ProductType IN ('QZ') AND\
                            DisplayName LIKE '%{color_name}%'\
                        ;\
                        ".format(color_name=color, CCItems="CCItems_" + sn_utils.get_franchise_location())
                        )
                        if len(sku) == 0:
                            print(
                                "No SKU found for - Countertop: {}".format(part_name))
                            print("Returning Special Order SKU")
                            return "SO-0000001"
                        elif len(sku) == 1:
                            return sku[0][0]
                        else:
                            print("Multiple SKUs found for - Countertop: {} ".format(part_name))
                            print(sku)
                            print("Returning Special Order SKU")
                            return "SO-0000001"
                    else:
                        mat_type = self.materials.mat_types[obj_props.unique_mat_types]
                        mat_name = sn_utils.get_unique_material_name(obj_props.unique_mat, assembly.obj_bp)
                        type_code = mat_type.type_code
                        color_code = mat_type.colors[mat_name].color_code

                if (part_name is not None and 'Quartz' in part_name) and (countertop_type):
                    if countertop_type.get_value() == 4 or countertop_type.get_value() == 5:
                        color = self.countertops.get_color().name
                        sku = sn_db.query_db(
                        "SELECT\
                            SKU\
                        FROM\
                            {CCItems}\
                        WHERE\
                            ProductType IN ('QZ') AND\
                            DisplayName LIKE '%{color_name}%'\
                        ;\
                        ".format(color_name=color, CCItems="CCItems_" + sn_utils.get_franchise_location())
                        )
                        if len(sku) == 0:
                            print(
                                "No SKU found for - Countertop: {}".format(part_name))
                            print("Returning Special Order SKU")
                            return "SO-0000001"
                        elif len(sku) == 1:
                            return sku[0][0]
                        else:
                            print("Multiple SKUs found for - Countertop: {} ".format(part_name))
                            print(sku)
                            print("Returning Special Order SKU")
                            return "SO-0000001"

                if part_name is not None and 'Melamine' not in part_name:
                    return 'SO-0000001'

            if any(shelf_lip_parts) and not assembly.obj_bp.get("IS_BP_MEL_SHELF_LIP"):
                if assembly.obj_bp.get("IS_SHOE_SHELF_LIP") and "Shelf Lip" not in part_name:
                    if 'Ogee' in part_name:
                        part_name = "OGEE EDGING"
                    sku = sn_db.query_db(
                        "SELECT\
                            SKU\
                        FROM\
                            {CCItems}\
                        WHERE\
                            ProductType IN ('MD') AND\
                            DisplayName LIKE '%{lip_name}%'\
                        ;\
                        ".format(lip_name=part_name, CCItems="CCItems_" + sn_utils.get_franchise_location())
                    )
                    if len(sku) == 0:
                        print(
                            "No SKU found for - Shelf Lip: {}".format(part_name))
                        return "Unknown"
                    elif len(sku) == 1:
                        return sku[0][0]
                    else:
                        print("Multiple SKUs found for - Shelf Lip: {} ".format(part_name))
                        print(sku)
                        return "Unknown"
                else:
                    if part_thickness == 0.75 or part_thickness == 0:
                        if self.upgrade_options.get_type().name == "Stain":
                            return "VN-0000014"
                        else:
                            return "WD-0000010"
                    elif part_thickness == 0.25:
                        if self.upgrade_options.get_type().name == "Stain":
                            return "VN-0000004"
                        else:
                            return "WD-0000007"

            if (obj_props.is_crown_molding or obj_props.is_base_molding) and not assembly.obj_bp.get("IS_BP_FLAT_CROWN"):
                sku = sn_db.query_db(
                    "SELECT\
                        SKU\
                    FROM\
                        {CCItems}\
                    WHERE\
                        DisplayName == '{molding_name}'\
                    ;\
                    ".format(molding_name=part_name, CCItems="CCItems_" + sn_utils.get_franchise_location())
                )

                if len(sku) == 0:
                    print(
                        "No SKU found for - Molding Name: {}".format(part_name))
                    return "Unknown"
                elif len(sku) == 1:
                    return sku[0][0]
                else:
                    print("Multiple SKUs found for - Molding Name: {} ".format(part_name))
                    print(sku)
                    return "Unknown"

        if type_code == 2 and color_name == "Cafe Au Lait (Cabinet Almond)":
            type_code = 15200

        if part_thickness == 0.25:
            if any(backing_parts) or obj_props.is_toe_kick_skin_bp:
                if assembly.obj_bp.get("IS_CEDAR_BACK"):
                    sku = 'VN-0000006'
                    return sku

            sku = sn_db.query_db(
                "SELECT\
                    SKU\
                FROM\
                    {CCItems}\
                WHERE\
                    ProductType IN ('PM', 'WD') AND\
                    Thickness == '{thickness}' AND\
                    ColorCode == '{color_code}'\
                ;\
                ".format(thickness=str(part_thickness), color_code=color_code, CCItems="CCItems_" + sn_utils.get_franchise_location())
            )

            if len(sku) == 0:
                print(
                    "No SKU found for - Material Thickness: {} Color Code: {}".format(part_thickness, color_code))
                return "Unknown"
            elif len(sku) == 1:
                return sku[0][0]
            else:
                print("Multiple SKUs found for - Material Thickness: {} Color Code: {}".format(
                    part_thickness, color_code))
                print(sku)
                return "Unknown"

        if part_thickness == 0.375:
            sku = sn_db.query_db(
                "SELECT\
                    SKU\
                FROM\
                    {CCItems}\
                WHERE\
                    ProductType IN ('PM', 'WD') AND\
                    Thickness == '{thickness}' AND\
                    ColorCode == '{color_code}'\
                ;\
                ".format(thickness=str(part_thickness), color_code=color_code, CCItems="CCItems_" + sn_utils.get_franchise_location())
            )

            if len(sku) == 0:
                # Use 0.75 material if 0.375 sku not found
                part_thickness = 0.75
            elif len(sku) == 1:
                return sku[0][0]
            else:
                print("Multiple SKUs found for - Material Thickness: {} Color Code: {}".format(
                    part_thickness, color_code))
                print(sku)
                return "Unknown"

        if part_thickness == 0.75 or part_thickness == 0:
            sku = sn_db.query_db(
                "SELECT\
                    SKU\
                FROM\
                    {CCItems}\
                WHERE ProductType in ('PM', 'WD') AND TypeCode = '{type_code}' AND ColorCode = '{color_code}';\
                ".format(type_code=type_code, color_code=color_code, CCItems="CCItems_" + sn_utils.get_franchise_location())
            )

            if len(sku) == 0:
                print("No SKU found for - Material Type Code: {} Color Code: {}".format(type_code, color_code))
                return "Unknown"
            elif len(sku) == 1:
                # print(sku[0][0])
                return sku[0][0]
            else:
                print("Multiple SKUs found for - Material Type Code: {} Color Code: {}".format(type_code, color_code))
                print(sku)
                return "Unknown"
    
    def get_garage_material_sku(self, obj=None, assembly=None, part_name=None):
        part_thickness = 0
        cutpart_name = ""
        obj_props = assembly.obj_bp.sn_closets
        
        type_code = 8
        color_code = self.materials.get_mat_color().color_code
        color_name = self.materials.get_mat_color().name

        exterior_parts = [
            "Garage_End_Panel",
            "Garage_Slab_Door",
            "Garage_Bottom_KD",
            "Garage_Top_KD",
            "Garage_Slab_Drawer_Front"
        ]

        interior_parts = [
            "Garage_Mid_Panel",
            "Garage_Interior_Shelf",
            "Garage_Back",
            "Garage_Interior_KD",
            "Garage_Cover_Cleat",
            "Garage_Cleat"
        ]

        door_drawer_parts = [
                obj_props.is_door_bp,
                obj_props.is_drawer_front_bp,
                obj_props.is_hamper_front_bp
            ]
        
        if any(door_drawer_parts):
            mat_type = self.door_drawer_materials.get_mat_type()
            color_code = self.door_drawer_materials.get_mat_color().color_code
            color_name = self.door_drawer_materials.get_mat_color().name
        else:
            mat_type = self.materials.get_mat_type()
            color_code = self.materials.get_mat_color().color_code
            color_name = self.materials.get_mat_color().name

        if assembly:
            obj_props = assembly.obj_bp.sn_closets

            backing_parts = [
                obj_props.is_back_bp,
                obj_props.is_top_back_bp,
                obj_props.is_bottom_back_bp
            ]
            
            if any(backing_parts):
                if obj_props.use_unique_material:
                    return "Unknown"

            for child in assembly.obj_bp.children:
                if child.snap.type_mesh == 'CUTPART':
                    cutpart_name = child.snap.cutpart_name

        if obj:
            part_thickness = sn_unit.meter_to_inch(sn_utils.get_part_thickness(obj))
            if obj.snap.type_mesh == 'CUTPART':
                cutpart_name = obj.snap.cutpart_name

        if part_thickness == 0 or part_thickness == 0.38:
            part_thickness = 0.75

        if part_thickness == 1:
            return "PM-0000475"
        
        if color_name == "Snow Drift":
            return 'PM-0000690'

        if cutpart_name in exterior_parts:
            sku = sn_db.query_db(
                "SELECT\
                    SKU\
                FROM\
                    {CCItems}\
                WHERE ProductType in ('PM', 'WD') AND TypeCode = '{type_code}' AND ColorCode LIKE '{color_code}';\
                ".format(type_code=type_code, color_code=color_code, CCItems="CCItems_" + sn_utils.get_franchise_location())
            )

            if len(sku) == 0:
                print(
                    "No SKU found for - Material Type Code: {} Color Code: {}".format(type_code, color_code))
                return "Unknown"
            elif len(sku) == 1:
                return sku[0][0]
            else:
                print(
                    "Multiple SKUs found for - Material Type Code: {} Color Code: {}".format(type_code, color_code))
                print(sku)
                return "Unknown"

        elif cutpart_name in interior_parts:
            type_code = 2
            sku = sn_db.query_db(
                "SELECT\
                    SKU\
                FROM\
                    {CCItems}\
                WHERE ProductType in ('PM', 'WD') AND TypeCode = '{type_code}' AND DisplayName LIKE '{display_name}' AND Thickness = '{part_thickness}';\
                ".format(type_code=type_code, display_name="Winter White", part_thickness=part_thickness, CCItems="CCItems_" + sn_utils.get_franchise_location())
            )

            if len(sku) == 0:
                print(
                    "No SKU found for - Material Type Code: {} Display Name: {} Part Thickness: {}".format(type_code, "Winter White (Oxford White)", part_thickness))
                return "Unknown"
            elif len(sku) == 1:
                return sku[0][0]
            else:
                print(
                    "Multiple SKUs found for - Material Type Code: {} Display Name: {} Part Thickness: {}".format(type_code, "Winter White (Oxford White)", part_thickness))
                print(sku)
                return "Unknown"
        else:
            return "Unknown"

    def get_mat_inventory_name(self, sku="", display_name=True):
        if sku:
            mat_sku = sku
        else:
            mat_sku = self.get_mat_sku(None, None, None)

        search_col = "DisplayName" if display_name else "Description"

        mat_name = sn_db.query_db(
            "SELECT\
                {col}\
            FROM\
                {CCItems}\
            WHERE\
                SKU == '{sku}';\
            ".format(col=search_col,sku=mat_sku, CCItems="CCItems_" + sn_utils.get_franchise_location())
        )

        if len(mat_name) == 0:
            print(
                "No Name found for - Material SKU: {sku}".format(sku=mat_sku))
            return "Unknown"
        elif len(mat_name) == 1:
            return mat_name[0][0]
        else:
            print(
                "Multiple Names found for - Material SKU: {sku}".format(sku=mat_sku))
            print(mat_name)
            return "Unknown"

    def get_glass_sku(self, glass_color):
        glass_thickness = 0.25
        if 'Frosted' in glass_color or 'Smoked' in glass_color:
            glass_thickness = 0.125
        if glass_color == 'Clear':
            glass_color = 'Clear Annealed'
        if glass_color == 'Double Sided Mirror':
            return 'GL-0000010'
        rows = sn_db.query_db(
            "SELECT\
                SKU\
            FROM\
                {CCItems}\
            WHERE\
                ProductType = 'GL' AND\
                Thickness == '{GlassThickness}' AND\
                DisplayName LIKE '%{DisplayName}%';\
            ".format(CCItems="CCItems_" + sn_utils.get_franchise_location(), DisplayName=glass_color, GlassThickness=glass_thickness)
        )
        if len(rows) == 0:
            sku = 'SO-0000001'
            print("No Pricing SKU Returned for Material Name:  " + glass_color)
            print("Special Order SKU given to:  " + glass_color)
        for row in rows:
            sku = row[0]
        return sku

    def get_stain_color(self):
        return self.stain_colors[self.stain_color_index]

    def get_stain_colors(self):
        return [color.name for color in self.stain_colors]

    def get_paint_color(self):
        return self.paint_colors[self.paint_color_index]

    def get_paint_colors(self):
        return [color.name for color in self.paint_colors]

    def get_five_piece_melamine_door_color(self):
        return self.five_piece_melamine_door_colors[self.five_piece_melamine_door_mat_color_index]

    def get_five_piece_melamine_door_colors(self):
        return [color.name for color in self.five_piece_melamine_door_colors]

    def get_paint_color_list(self):
        colors = []
        for color in self.paint_colors:
            colors.append((color.name, color.name, color.name))
        return colors

    def get_stain_color_list(self):
        colors = []
        for color in self.stain_colors:
            colors.append((color.name, color.name, color.name))
        return colors

    def get_ct_paint_color(self):
        paint_colors = self.countertops.get_type().get_mfg().colors
        return paint_colors[self.ct_paint_color_index]

    def get_ct_stain_color(self):
        stain_colors = self.countertops.get_type().get_mfg().colors
        return stain_colors[self.ct_stain_color_index]

    def get_moderno_colors(self):
        return [color.name for color in self.moderno_colors]

    def get_glaze_color(self):
        return self.glaze_colors[self.glaze_color_index]

    def get_glaze_style(self):
        return self.glaze_styles[self.glaze_style_index]

    def get_glass_color(self):
        return self.glass_colors[self.glass_color_index]
    
    def get_glass_colors(self):
        colors = []
        for color in self.glass_colors:
            colors.append((color.name, color.name, color.name))
        return colors

    def get_drawer_slide_type(self):
        return self.drawer_slides[self.drawer_slide_index]

    def get_kb_material_list(self):
        material_list = [self.kb_base_mat, self.kb_upper_mat, self.kb_island_mat]
        return material_list

    def get_mat_color_index(self, mat_type):
        if self.upgrade_options.get_type().name == "Paint":
            upgrade_color_index = self.paint_color_index
        else:
            upgrade_color_index = self.stain_color_index

        mat_color_indexes = {
            "Solid Color Smooth Finish": self.solid_color_index,
            "Grain Pattern Smooth Finish": self.grain_color_index,
            "Solid Color Textured Finish": self.solid_tex_color_index,
            "Grain Pattern Textured Finish": self.grain_tex_color_index,
            "Linen Pattern Linen Finish": self.linen_color_index,
            "Solid Color Matte Finish": self.matte_color_index,
            "Garage Material": self.garage_color_index,
            "Oversized Material": self.oversized_color_index,
            "Upgrade Options": upgrade_color_index}

        return mat_color_indexes[mat_type]

    def get_dd_mat_color_index(self, mat_type):
        if self.upgrade_options.get_type().name == "Paint":
            upgrade_color_index = self.paint_color_index
        else:
            upgrade_color_index = self.stain_color_index

        mat_color_indexes = {
            "Solid Color Smooth Finish": self.dd_solid_color_index,
            "Grain Pattern Smooth Finish": self.dd_grain_color_index,
            "Solid Color Textured Finish": self.dd_solid_tex_color_index,
            "Grain Pattern Textured Finish": self.dd_grain_tex_color_index,
            "Linen Pattern Linen Finish": self.dd_linen_color_index,
            "Solid Color Matte Finish": self.dd_matte_color_index,
            "Garage Material": self.dd_garage_color_index,
            "Oversized Material": self.dd_oversized_color_index,
            "Upgrade Options": upgrade_color_index}

        return mat_color_indexes[mat_type]

    def set_all_edge_colors(self, mat_color):
        for type_index, edge_type in enumerate(self.edges.edge_types):
            if mat_color.name in edge_type.colors:
                color_index = edge_type.colors.find(mat_color.name)
                self.edge_type_index = type_index
                self.secondary_edge_type_index = type_index
                self.door_drawer_edge_type_index = type_index
                self.edge_color_index = color_index
                self.secondary_edge_color_index = color_index
                self.door_drawer_edge_color_index = color_index
                break

    def set_edge(self, color_name):
        for type_index, edge_type in enumerate(self.edges.edge_types):
            if color_name in edge_type.colors:
                color_index = edge_type.colors.find(color_name)
                self.edge_type_index = type_index
                self.secondary_edge_type_index = type_index
                self.door_drawer_edge_type_index = type_index
                self.edge_color_index = color_index
                self.secondary_edge_color_index = color_index
                self.door_drawer_edge_color_index = color_index
                break

    def set_all_material_colors(self):
        material_type = self.materials.get_mat_type()
        material_color = self.materials.get_mat_color()
        self.door_drawer_mat_type_index = self.door_drawer_materials.mat_types.find(material_type.name)
        door_drawer_mat_type = self.door_drawer_materials.get_mat_type()
        self.door_drawer_mat_color_index = door_drawer_mat_type.colors.find(material_color.name)

        if self.five_piece_melamine_door_colors.find(material_color.name) != -1:
            if "Bridal Shower (Antique White) Δ" in material_color.name:
                self.five_piece_melamine_door_mat_color_index = self.five_piece_melamine_door_colors.find("Warm Spring")
            else:
                self.five_piece_melamine_door_mat_color_index = self.five_piece_melamine_door_colors.find(material_color.name)

        if "Snow Drift" in material_color.name or "Mountain Peak" in material_color.name or "Winter White" in material_color.name:
            self.set_all_edge_colors(self.materials.mat_types[0].colors[self.materials.mat_types[0].colors.find("Winter White")])
        elif "Bridal Shower (Antique White) Δ" in material_color.name:
            self.set_all_edge_colors(self.materials.mat_types[0].colors[self.materials.mat_types[0].colors.find("Warm Spring")])
        else:
            self.set_all_edge_colors(material_color)

    def set_defaults(self):
        self.set_default_material_type()
        self.set_default_edge_type()
        self.set_default_material_color()
        self.set_default_dd_material_color()
        self.set_default_edge_color()
        self.set_default_glass_color()
        self.set_default_secondary_edge_color()
        self.set_default_door_drawer_edge_color()
        self.set_default_countertop_mat()
        self.defaults_set = True

    def set_default_countertop_mat(self):
        active_lib = bpy.context.scene.snap.active_library_name

        if active_lib == "Kitchen Bath Library":
            self.ct_type_index = 5
            self.std_quartz_colors = self.countertops.countertop_types['Standard Quartz'].colors
            for i, color in enumerate(self.std_quartz_colors):
                if color.name == self.default_kb_countertop_color:
                    self.ct_color_index = i
        else:
            self.ct_type_index = 0
            self.ct_mfg_index = 0
            self.ct_color_index = 0

    def set_default_material_type(self):
        self.upgrade_type_index = 1 if not self.use_custom_color_scheme else 0

        for i, type in enumerate(self.materials.mat_types):
            if type.name == self.default_mat_type:
                self.mat_type_index = i
                break
        for i, type in enumerate(self.door_drawer_materials.mat_types):
            if type.name == self.default_mat_type:
                self.door_drawer_mat_type_index = i
                break

    def set_default_edge_type(self):
        self.edge_type_index = self.edges.edge_types.find(self.default_edge_type)
        self.secondary_edge_type_index = self.secondary_edges.edge_types.find(self.default_edge_type)
        self.door_drawer_edge_type_index = self.door_drawer_edges.edge_types.find(self.default_edge_type)

    def set_default_material_color(self):
        color_idx = None
        mat_type = self.materials.get_mat_type()
        if mat_type.name == self.default_mat_type:
            color_idx = mat_type.colors.find(self.default_color)

        self.color_change = False

        if color_idx:
            self.solid_color_index = color_idx
        else:
            self.solid_color_index = 0

    def set_default_upgrade_selection(self):
        self.upgrade_type_index = self.upgrade_options.types.find("Paint")
        self.paint_color_index = self.paint_colors.find(self.default_paint_color)

    def set_default_dd_material_color(self):
        door_drawer_mat_type = self.door_drawer_materials.get_mat_type()
        door_drawer_color_idx = door_drawer_mat_type.colors.find(self.default_color)

        if door_drawer_color_idx:
            self.door_drawer_mat_color_index = door_drawer_color_idx
        else:
            self.door_drawer_mat_color_index = 0

    def set_default_edge_color(self):
        edge_type = self.edges.get_edge_type()
        color_idx = edge_type.colors.find(self.default_edge_color)

        if color_idx:
            self.edge_color_index = color_idx
        else:
            self.edge_color_index = 0

    def set_default_glass_color(self):
        color_idx = self.glass_colors.find(self.default_glass_color)

        if color_idx:
            self.glass_color_index = color_idx
        else:
            self.glass_color_index = 2

    def set_default_secondary_edge_color(self):
        secondary_edge_type = self.secondary_edges.get_edge_type()
        color_idx = secondary_edge_type.colors.find(self.default_edge_color)

        if color_idx:
            self.secondary_edge_color_index = color_idx
        else:
            self.secondary_edge_color_index = 0

    def set_default_door_drawer_edge_color(self):
        edge_type = self.door_drawer_edges.get_edge_type()
        color_idx = edge_type.colors.find(self.default_edge_color)

        if color_idx:
            self.door_drawer_edge_color_index = color_idx
        else:
            self.door_drawer_edge_color_index = 0

    def draw(self, layout):
        options = bpy.context.scene.sn_closets.closet_options

        c_box = layout.box()
        tab_col = c_box.column(align=True)
        row = tab_col.row(align=True)
        row.prop_enum(self, "main_tabs", 'MATERIAL')
        row.prop_enum(self, "main_tabs", 'COUNTERTOP')
        row.prop_enum(self, "main_tabs", 'HARDWARE')
        row = tab_col.row(align=True)
        row.prop_enum(self, "main_tabs", 'MOLDING')
        row.prop_enum(self, "main_tabs", 'GLASS')
        row = tab_col.row(align=True)
        row.prop_enum(self, "main_tabs", 'DOORS_AND_DRAWER_FACES')

        if self.main_tabs == 'MATERIAL':
            box = c_box.box()
            box.label(text="Options:")

            if not self.use_kb_color_scheme:
                box.prop(self, "use_custom_color_scheme")

            if self.materials.get_mat_type().name == "Garage Material":
                if "Steel Grey" in self.materials.get_mat_color().name:
                    row = box.row()
                    row.prop(self, "use_black_edge", text="Use Black Edgebanding")

            if self.use_custom_color_scheme:
                self.materials.draw(c_box)
                self.edges.draw(c_box)
                self.secondary_edges.draw(c_box)
                box = c_box.box()
                box.label(text="Doors/Drawer Faces:")
                self.door_drawer_edges.draw(box)
                self.door_drawer_materials.draw(box)
                self.upgrade_options.draw(c_box)

                box = c_box.box()
                box.label(text="Traviso (Five Piece Melamine Door) Color Selection")

                if len(self.five_piece_melamine_door_colors) > 0:
                    active_five_piece_melamine_door_color = self.get_five_piece_melamine_door_color()
                    row = box.row(align=True)
                    split = row.split(factor=0.25)
                    split.label(text="Color:")
                    split.menu(
                        'SNAP_MATERIAL_MT_Five_Piece_Melamine_Door_Colors',
                        text=active_five_piece_melamine_door_color.name, icon='RADIOBUT_ON')

                box = c_box.box()
                box.label(text="Moderno Door Color Selection:")

                if len(self.moderno_colors) > 0:
                    active_door_color = self.moderno_colors[self.moderno_color_index]
                    row = box.row(align=True)
                    split = row.split(factor=0.25)
                    split.label(text="Color:")
                    split.menu(
                        'SNAP_MATERIAL_MT_Door_Colors',
                        text=active_door_color.name, icon='RADIOBUT_ON')
                else:
                    row = box.row()
                    row.label(text="None", icon='ERROR')

            elif not self.use_custom_color_scheme:
                row = box.row()
                row.prop(self, "use_kb_color_scheme")

                if self.use_kb_color_scheme:
                    box = c_box.box()
                    row = box.row()
                    row.label(text="Base Cabinets:")
                    row = box.row()
                    row.prop(self, "kb_base_mat_types", text="Type")
                    row = box.row()
                    row.prop(self, "kb_base_mat", text="Color")

                    box = c_box.box()
                    row = box.row()
                    row.label(text="Upper Cabinets:")
                    row = box.row()
                    row.prop(self, "kb_upper_mat_types", text="Type")
                    row = box.row()
                    row.prop(self, "kb_upper_mat", text="Color")

                    box = c_box.box()
                    row = box.row()
                    row.label(text="Island Cabinets:")
                    row = box.row()
                    row.prop(self, "kb_island_mat_types", text="Type")
                    row = box.row()
                    row.prop(self, "kb_island_mat", text="Color")

            if not self.use_kb_color_scheme:
                self.materials.draw(c_box)

        if self.main_tabs == 'COUNTERTOP':
            self.countertops.draw(c_box)

        if self.main_tabs == 'GLASS':
            box = c_box.box()
            box.label(text="Glass Inset Color Selection:")

            if len(self.glass_colors):
                active_glass_color = self.glass_colors[self.glass_color_index]
                row = box.row(align=True)
                split = row.split(factor=0.25)
                split.label(text="Color:")
                split.menu(
                    'SNAP_MATERIAL_MT_Glass_Colors',
                    text=active_glass_color.name, icon='RADIOBUT_ON')
            else:
                row = box.row()
                row.label(text="None", icon='ERROR')

        if self.main_tabs == 'MOLDING':
            options.draw_molding_options(c_box)

        if self.main_tabs == 'DOORS_AND_DRAWER_FACES':
            options.draw_door_options(c_box)

        if self.main_tabs == 'HARDWARE':
            box = c_box.box()
            box.label(text="Hardware:")
            options.draw_hardware_options(box)
            col = box.column()
            row = col.row(align=True)
            split = row.split(factor=0.40)
            split.label(text="Wire Basket Color:")
            split.prop(self, "wire_basket_colors", expand=True)
            row = col.row(align=True)
            split = row.split(factor=0.40)
            split.label(text="KD Fitting Color:")
            split.prop(self, "kd_fitting_color", text="")

        else:
            c_box.operator(
                "closet_materials.poll_assign_materials",
                text="Update Materials", icon='FILE_REFRESH')

    @classmethod
    def register(cls):
        bpy.types.Scene.closet_materials = PointerProperty(
            name="SNaP Materials",
            description="SNaP Material Scene Properties",
            type=cls,
        )

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.closet_materials


classes = (
    SN_MAT_PT_Closet_Materials_Interface,
    SnapMaterialSceneProps
)

register, unregister = bpy.utils.register_classes_factory(classes)
