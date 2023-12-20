import math
import time


import bpy
from bpy.props import (
    BoolProperty,
    StringProperty,
    FloatProperty,
    IntProperty,
    EnumProperty,
)

from . import callback
from snap import sn_types
from snap import sn_unit
from snap import sn_utils
from snap.libraries.closets.common import common_lists
from snap.libraries.closets.data import data_closet_carcass
from snap.libraries.closets import closet_props

panel_heights = []


class PanelHeights:
    def __init__(self, start, max, start_hole_amt):
        self.max = max
        self.start = start
        self.hole_amt = start_hole_amt

    def __iter__(self):
        self.num = self.start
        return self

    def __next__(self):
        if self.num > self.max:
            raise StopIteration

        mm = self.num
        inch = round(self.num / 25.4, 2)
        name = '{}H-{}"'.format(str(self.hole_amt), str(inch))
        self.num += 32
        self.hole_amt += 1

        return ((str(mm), name, ""))


def get_panel_heights(self, context):
    global panel_heights
    mat_type = context.scene.closet_materials.materials.get_mat_type()
    if mat_type.name == 'Oversized Material' or mat_type.type_code == 15225:
        start = 115  # Millimeter
        max_height = 2419  # Millimeter
        start_hole_amt = 3
        mat_color = mat_type.get_mat_color()
        max_height = mat_color.oversize_max_len
        panel_heights = PanelHeights(start, max_height, start_hole_amt)
        panel_heights_iter = iter(panel_heights)
        panel_heights = list(panel_heights_iter)

        return panel_heights

    elif len(panel_heights) > 0:  # This check was causing the panel heights list to not update if changes to material were made after a partition had it's prompt menu open
        return panel_heights 
    else:
        start = 115  # Millimeter
        max_height = 2419  # Millimeter
        start_hole_amt = 3
        panel_heights = PanelHeights(start, max_height, start_hole_amt)
        panel_heights_iter = iter(panel_heights)
        panel_heights = list(panel_heights_iter)

        return panel_heights


class PROMPTS_Opening_Starter(sn_types.Prompts_Interface):
    bl_idname = "sn_closets.openings"
    bl_label = "Partition Prompt"

    closet_name: StringProperty(name="Closet Name", default="")
    width: FloatProperty(name="Width", unit='LENGTH', precision=5, update=callback.update_overall_width)
    height: EnumProperty(name="Height", items=get_panel_heights, update=callback.update_closet_height)
    depth: FloatProperty(name="Depth", unit='LENGTH', precision=4)
    exterior_changed: BoolProperty(name="Exterior Changed")

    product_tabs: EnumProperty(
        name="Product Tabs",
        items=[
            ('OPENINGS', 'Opening Sizes', 'Show the Width x Height x Depth for each opening'),
            ('CONSTRUCTION', 'Construction Options', 'Show Additional Construction Options')],
        default='OPENINGS')

    placement_on_wall: EnumProperty(
        name="Placement on Wall",
        items=[
            ('SELECTED_POINT', "Selected Point", ""),
            ('FILL', "Fill", ""),
            ('FILL_LEFT', "Fill Left", ""),
            ('LEFT', "Left", ""),
            ('CENTER', "Center", ""),
            ('RIGHT', "Right", ""),
            ('FILL_RIGHT', "Fill Right", "")],
        default='SELECTED_POINT',
        update=callback.update_placement)

    current_location: FloatProperty(
        name="Current Location",
        default=0,
        subtype='DISTANCE',
        precision=4,
        update=callback.update_placement)

    quantity: IntProperty(name="Quantity", default=1)
    left_offset: FloatProperty(name="Left Offset", default=0, subtype='DISTANCE', precision=4)
    right_offset: FloatProperty(name="Right Offset", default=0, subtype='DISTANCE', precision=4)
    loc_left_side: FloatProperty(name="Loc Left Side", unit='LENGTH', precision=4)
    loc_right_side: FloatProperty(name="Loc Right Side", unit='LENGTH', precision=4)
    init_height_list: BoolProperty(name="Init Height List", default=True)
    default_height: StringProperty(name="Default Height", default='1203')
    hang_height: FloatProperty(name="Hang Height", unit='LENGTH', precision=4, update=callback.update_hang_height)
    tk_height: FloatProperty(name="Toe Kick Height", unit='LENGTH', precision=4, update=callback.update_toe_kick_height)
    left_end_condition: EnumProperty(name="Left Side", items=common_lists.END_CONDITIONS, default='WP', update=callback.update_end_conditions)
    right_end_condition: EnumProperty(name="Right Side", items=common_lists.END_CONDITIONS, default='WP', update=callback.update_end_conditions)
    add_backing_throughout: BoolProperty(name="Add Backing Throughout", default=False, update=callback.update_backing_throughout)
    add_left_filler: BoolProperty(name="Add Left Filler", default=False, update=callback.update_fillers)
    add_right_filler: BoolProperty(name="Add Right Filler", default=False, update=callback.update_fillers)
    right_filler_changed: BoolProperty(name="Right Filler Amount Changed", default=False)
    right_filler_amt: FloatProperty(name="Right Filler Amount", subtype='DISTANCE', precision=4, default=0, update=callback.update_filler_amt)
    left_filler_amt: FloatProperty(name="Left Filler Amount", subtype='DISTANCE', precision=4, default=0, update=callback.update_filler_amt)
    active_dog_ear: BoolProperty(name="Active Dog Ear", default=False, update=callback.update_dog_ear)
    add_left_blind: BoolProperty(name="Add Left Blind Corner Panel", default=False, update=callback.update_blind_panels)
    add_right_blind: BoolProperty(name="Add Right Blind Corner Panel", default=False, update=callback.update_blind_panels)

    opening_1_height: EnumProperty(name="Opening 1 Height", items=get_panel_heights, update=callback.update_opening_heights)
    opening_2_height: EnumProperty(name="Opening 2 Height", items=get_panel_heights, update=callback.update_opening_heights)
    opening_3_height: EnumProperty(name="Opening 3 Height", items=get_panel_heights, update=callback.update_opening_heights)
    opening_4_height: EnumProperty(name="Opening 4 Height", items=get_panel_heights, update=callback.update_opening_heights)
    opening_5_height: EnumProperty(name="Opening 5 Height", items=get_panel_heights, update=callback.update_opening_heights)
    opening_6_height: EnumProperty(name="Opening 6 Height", items=get_panel_heights, update=callback.update_opening_heights)
    opening_7_height: EnumProperty(name="Opening 7 Height", items=get_panel_heights, update=callback.update_opening_heights)
    opening_8_height: EnumProperty(name="Opening 8 Height", items=get_panel_heights, update=callback.update_opening_heights)
    opening_9_height: EnumProperty(name="Opening 9 Height", items=get_panel_heights, update=callback.update_opening_heights)

    op_1_floor_mount: BoolProperty(name="Opening 1 Floor Mounted", default=False, update=callback.update_op_1_floor_mount)
    op_2_floor_mount: BoolProperty(name="Opening 2 Floor Mounted", default=False, update=callback.update_op_2_floor_mount)
    op_3_floor_mount: BoolProperty(name="Opening 3 Floor Mounted", default=False, update=callback.update_op_3_floor_mount)
    op_4_floor_mount: BoolProperty(name="Opening 4 Floor Mounted", default=False, update=callback.update_op_4_floor_mount)
    op_5_floor_mount: BoolProperty(name="Opening 5 Floor Mounted", default=False, update=callback.update_op_5_floor_mount)
    op_6_floor_mount: BoolProperty(name="Opening 6 Floor Mounted", default=False, update=callback.update_op_6_floor_mount)
    op_7_floor_mount: BoolProperty(name="Opening 7 Floor Mounted", default=False, update=callback.update_op_7_floor_mount)
    op_8_floor_mount: BoolProperty(name="Opening 8 Floor Mounted", default=False, update=callback.update_op_8_floor_mount)
    op_9_floor_mount: BoolProperty(name="Opening 9 Floor Mounted", default=False, update=callback.update_op_9_floor_mount)

    op_1_full_back: BoolProperty(name="Opening 1 Add Full Back", default=False, update=callback.update_op_1_full_back)
    op_2_full_back: BoolProperty(name="Opening 2 Add Full Back", default=False, update=callback.update_op_2_full_back)
    op_3_full_back: BoolProperty(name="Opening 3 Add Full Back", default=False, update=callback.update_op_3_full_back)
    op_4_full_back: BoolProperty(name="Opening 4 Add Full Back", default=False, update=callback.update_op_4_full_back)
    op_5_full_back: BoolProperty(name="Opening 5 Add Full Back", default=False, update=callback.update_op_5_full_back)
    op_6_full_back: BoolProperty(name="Opening 6 Add Full Back", default=False, update=callback.update_op_6_full_back)
    op_7_full_back: BoolProperty(name="Opening 7 Add Full Back", default=False, update=callback.update_op_7_full_back)
    op_8_full_back: BoolProperty(name="Opening 8 Add Full Back", default=False, update=callback.update_op_8_full_back)
    op_9_full_back: BoolProperty(name="Opening 9 Add Full Back", default=False, update=callback.update_op_9_full_back)

    op_1_width_equal: BoolProperty(name="Opening 1 Width Equal", update=callback.update_opening_equal_status)
    op_2_width_equal: BoolProperty(name="Opening 2 Width Equal", update=callback.update_opening_equal_status)
    op_3_width_equal: BoolProperty(name="Opening 3 Width Equal", update=callback.update_opening_equal_status)
    op_4_width_equal: BoolProperty(name="Opening 4 Width Equal", update=callback.update_opening_equal_status)
    op_5_width_equal: BoolProperty(name="Opening 5 Width Equal", update=callback.update_opening_equal_status)
    op_6_width_equal: BoolProperty(name="Opening 6 Width Equal", update=callback.update_opening_equal_status)
    op_7_width_equal: BoolProperty(name="Opening 7 Width Equal", update=callback.update_opening_equal_status)
    op_8_width_equal: BoolProperty(name="Opening 8 Width Equal", update=callback.update_opening_equal_status)
    op_9_width_equal: BoolProperty(name="Opening 9 Width Equal", update=callback.update_opening_equal_status)

    op_1_width: FloatProperty(name="Opening 1 Width", subtype='DISTANCE', precision=4, update=callback.update_opening_widths)
    op_2_width: FloatProperty(name="Opening 2 Width", subtype='DISTANCE', precision=4, update=callback.update_opening_widths)
    op_3_width: FloatProperty(name="Opening 3 Width", subtype='DISTANCE', precision=4, update=callback.update_opening_widths)
    op_4_width: FloatProperty(name="Opening 4 Width", subtype='DISTANCE', precision=4, update=callback.update_opening_widths)
    op_5_width: FloatProperty(name="Opening 5 Width", subtype='DISTANCE', precision=4, update=callback.update_opening_widths)
    op_6_width: FloatProperty(name="Opening 6 Width", subtype='DISTANCE', precision=4, update=callback.update_opening_widths)
    op_7_width: FloatProperty(name="Opening 7 Width", subtype='DISTANCE', precision=4, update=callback.update_opening_widths)
    op_8_width: FloatProperty(name="Opening 8 Width", subtype='DISTANCE', precision=4, update=callback.update_opening_widths)
    op_9_width: FloatProperty(name="Opening 9 Width", subtype='DISTANCE', precision=4, update=callback.update_opening_widths)

    product = None

    is_island = None
    is_single_island = None

    insert_bps = []

    default_width = 0
    selected_location = 0

    calculators = []

    back = None
    selected_obj = None

    closet = None
    carcass = None
    countertop = None
    doors = None
    drawers = None
    interior_assembly = None
    exterior_assembly = None
    splitters = []
    op_is_floor_mount = {}
    op_door_height_exceeded = {}

    is_island = None
    is_single_island = None
    show_tk_mess = None

    prev_all_backing = None
    prev_hang_height = None

    skip = False
    initialized = False

    def reset_variables(self):
        self.product_tabs = 'OPENINGS'
        callback.active_operator = None

        self.calculators = []
        self.init_height_list = True

        self.left_side = None
        self.right_side = None
        self.left_filler = None
        self.right_filler = None
        self.back = None
        self.prev_all_backing = None

        self.closet = None
        self.insert_bps = []
        self.countertop = None
        # self.carcass = None
        # self.doors = None
        # self.drawers = None
        # self.interior_assembly = None
        # self.exterior_assembly = None
        # self.splitters = []

    def get_assemblies(self, context):
        # self.carcass = None
        # self.interior_assembly = None
        # self.exterior_assembly = None
        self.countertop = None
        # self.drawers = None
        self.calculators = []
        self.drawer_calculator = None
        # self.doors = None
        self.back = None
        opening_widths_calculator = self.closet.get_calculator('Opening Widths Calculator')
        if opening_widths_calculator:
            self.calculators.append(opening_widths_calculator)

        for child in self.closet.obj_bp.children:
            obj_props = child.sn_closets

            # if "IS_CARCASS_BP" in child and child["IS_CARCASS_BP"]:
            #     self.carcass = data_closet_carcass.Closet_Carcass(child)
            # if "IS_INTERIOR_BP" in child and child["IS_INTERIOR_BP"]:
            #     self.interior_assembly = sn_types.Assembly(child)
            # if "IS_EXTERIOR_BP" in child and child["IS_EXTERIOR_BP"]:
            #     self.exterior_assembly = sn_types.Assembly(child)
            if "IS_BP_COUNTERTOP" in child and child["IS_BP_COUNTERTOP"]:
                self.countertop = sn_types.Assembly(child)
            # if "IS_DRAWERS_BP" in child and child["IS_DRAWERS_BP"]:
            #     self.drawers = sn_types.Assembly(child)
            #     # self.calculators.append(self.drawers.get_calculator('Front Height Calculator'))
            # if "IS_DOORS_BP" in child and child["IS_DOORS_BP"]:
            #     self.doors = sn_types.Assembly(child)
            if "IS_BP_SPLITTER" in child and child["IS_BP_SPLITTER"]:
                assy = sn_types.Assembly(child)
                calculator = assy.get_calculator('Opening Heights Calculator')
                # if assy:
                #     self.splitters.append(assy)
                if calculator:
                    self.calculators.append(calculator)

            props = [
                obj_props.is_drawer_stack_bp,
                obj_props.is_hamper_insert_bp,
                obj_props.is_door_insert_bp,
                obj_props.is_closet_bottom_bp,
                obj_props.is_closet_top_bp,
                obj_props.is_splitter_bp,
                "IS_BP_ROD_AND_SHELF" in child,
                "IS_BP_TOE_KICK_INSERT" in child,
                "IS_BP_SHOE_SHELVES" in child]

            if any(props):
                self.insert_bps.append(child)

            for nchild in child.children:
                obj_props = nchild.sn_closets
                props = [
                    obj_props.is_drawer_stack_bp,
                    obj_props.is_hamper_insert_bp,
                    obj_props.is_door_insert_bp,
                    obj_props.is_splitter_bp,
                    "IS_BP_SHOE_SHELVES" in child]

                if any(props):
                    self.insert_bps.append(nchild)

    def set_hang_height(self):
        closet = self.closet

        # If all openings are hanging, set hang height to closet height
        if self.all_hanging_openings():
            self.skip = True
            self.hang_height = closet.obj_z.location.z
            self.prev_hang_height = self.hang_height
            return

        # If any openings are floor mounted, set hang height to tallest opening
        else:
            max_height = 0
            opening_qty = closet.get_prompt("Opening Quantity").get_value()
            tk_height = closet.get_prompt("Toe Kick Height").distance_value

            for i in range(1, opening_qty + 1):
                is_op_floor_mounted = closet.get_prompt("Opening " + str(i) + " Floor Mounted").get_value()

                if not is_op_floor_mounted:
                    height = closet.obj_z.location.z
                else:
                    opening_height = closet.get_prompt("Opening " + str(i) + " Height").distance_value
                    height = opening_height + tk_height

                if height > max_height:
                    max_height = height

            self.skip = True
            self.hang_height = max_height
            self.prev_hang_height = self.hang_height

    def set_opening_floor_mounts(self):
        for i in range(1, 10):
            op_floor_mount = self.closet.get_prompt("Opening " + str(i) + " Floor Mounted")
            if op_floor_mount:
                exec(f"self.op_{str(i)}_floor_mount = op_floor_mount.get_value()")

    def all_floor_mounted_openings(self):
        """All openings are floor mounted"""
        closet_floor_mounted = True
        closet = self.closet
        opening_qty = closet.get_prompt("Opening Quantity").get_value()

        for i in range(1, opening_qty + 1):
            floor_mount_ppt_name = "Opening " + str(i) + " Floor Mounted"
            is_floor_mounted = closet.get_prompt(floor_mount_ppt_name).get_value()
            self.op_is_floor_mount[floor_mount_ppt_name] = is_floor_mounted
            closet_floor_mounted = closet_floor_mounted and is_floor_mounted

        return closet_floor_mounted

    def invoke(self, context, event):
        start_time = time.perf_counter()
        self.reset_variables()
        self.initialized = False
        callback.active_operator = self
        bp = sn_utils.get_closet_bp(context.object)
        self.closet = data_closet_carcass.Closet_Carcass(bp)
        self.closet_name = self.closet.obj_bp.name
        self.get_assemblies(context)
        self.run_calculators(self.closet.obj_bp)
        self.set_hang_height()

        if self.closet.obj_bp:
            self.set_default_heights(context)
            self.set_default_widths(context)
            self.set_default_width_equal_status()
            self.width = math.fabs(self.closet.obj_x.location.x)
            left_end_condition = self.closet.get_prompt("Left End Condition")
            right_end_condition = self.closet.get_prompt("Right End Condition")
            self.is_island = self.closet.get_prompt("Is Island")
            self.is_single_island = self.closet.get_prompt("Inside Depth")
            add_backing_throughout_ppt = self.closet.get_prompt("Add Backing Throughout")
            tk_height = self.closet.get_prompt("Toe Kick Height")
            add_left_filler = self.closet.get_prompt("Add Left Filler")
            add_right_filler = self.closet.get_prompt("Add Right Filler")
            left_filler_amt = self.closet.get_prompt("Left Side Wall Filler")
            right_filler_amt = self.closet.get_prompt("Right Side Wall Filler")

            if tk_height:
                self.tk_height = tk_height.get_value()

            if add_backing_throughout_ppt:
                self.add_backing_throughout = add_backing_throughout_ppt.get_value()
                self.prev_all_backing = add_backing_throughout_ppt.get_value()

                for i in range(self.closet.opening_qty):
                    exec(f"self.op_{str(i + 1)}_full_back = self.closet.get_prompt('Add Full Back {str(i + 1)}').get_value()")

            if left_end_condition:
                combobox_index = left_end_condition.get_value()
                self.left_end_condition = left_end_condition.combobox_items[combobox_index].name

            if right_end_condition:
                combobox_index = right_end_condition.get_value()
                self.right_end_condition = right_end_condition.combobox_items[combobox_index].name

            if self.is_island:
                opening_1_height = self.closet.get_prompt("Opening 1 Height")
                opening_1_depth = self.closet.get_prompt("Opening 1 Depth")
                self.depth = opening_1_depth.get_value()
                self.height = self.convert_to_height(opening_1_height.get_value(),context)

            if self.is_single_island:
                opening_1_height = self.closet.get_prompt("Opening 1 Height")
                opening_1_depth = self.closet.get_prompt("Opening 1 Depth")
                self.depth = opening_1_depth.get_value()
                self.height = self.convert_to_height(opening_1_height.get_value(),context)

            if add_left_filler:
                self.add_left_filler = add_left_filler.get_value()
                if left_filler_amt:
                    self.left_filler_amt = left_filler_amt.get_value()

            if add_right_filler:
                self.add_right_filler = add_right_filler.get_value()
                if right_filler_amt:
                    self.right_filler_amt = right_filler_amt.get_value()

        self.current_location = self.closet.obj_bp.location.x
        self.selected_location = self.closet.obj_bp.location.x
        self.default_width = self.closet.obj_x.location.x
        self.placement_on_wall = 'SELECTED_POINT'
        self.left_offset = 0
        self.right_offset = 0
        self.set_opening_floor_mounts()
        self.all_floor_mounted = self.all_floor_mounted_openings()
        self.all_hanging = self.all_hanging_openings()
        self.update_opening_inserts()

        self.initialized = True

        print("{} {}: Check Time --- {} seconds ---".format(
            self.bl_idname, "invoke",
            round(time.perf_counter() - start_time, 8)))

        return super().invoke(context, event)

    def update_hutch_backing(self, context):
        hutch_vertical_grain = self.closet.get_prompt('Hutch Vertical Grain')
        height_left_side = self.closet.get_prompt('Height Left Side')
        height_right_side = self.closet.get_prompt('Height Right Side')
        has_capping_bottom = self.closet.get_prompt('Has Capping Bottom')
        prompts = [hutch_vertical_grain, height_left_side, height_right_side, has_capping_bottom]
        if all(prompts):
            hutch_height = 0
            if height_left_side.get_value() >= height_right_side.get_value():
                hutch_height = height_left_side.get_value()
            else:
                hutch_height = height_right_side.get_value()
            if has_capping_bottom.get_value():
                hutch_height = hutch_height - sn_unit.inch(0.75)
            if self.closet.obj_x.location.x - sn_unit.inch(1.5) > sn_unit.inch(48.01) and hutch_height < sn_unit.inch(48.01):
                hutch_vertical_grain.set_value(False)
            else:
                hutch_vertical_grain.set_value(True)

    def check(self, context):
        start_time = time.perf_counter()

        # self.run_calculators(self.closet.obj_bp)
        # self.closet.obj_x.location.x = self.width
        # self.check_tk_height()
        # self.update_tk_height()
        # self.reset_fillers()
        # self.check_front_angle_depth()
        self.update_opening_inserts()
        # self.update_placement(context)
        # self.update_fillers(context)
        # self.update_backing(context)
        self.update_hutch_backing(context)
        # self.update_flat_molding_heights()
        # self.update_opening_heights()
        # self.update_hang_height()
        # self.check_hang_height()
        # self.update_top_location()
        # self.update_countertop()
        # self.run_calculators(self.closet.obj_bp)
        self.closet.obj_bp.select_set(True)

        print("{} : Check Time --- {} seconds ---".format(
            self.bl_idname,
            round(time.perf_counter() - start_time, 8)))

        return True

    def execute(self, context):
        self.show_tk_mess = False
        return {'FINISHED'}

    def draw(self, context):
        super().draw(context)
        layout = self.layout
        prompt_box = layout.box()
        # prompt_box.label(text=self.closet_name, icon='LATTICE_DATA')
        # prompt_box.label(text=self.closet.obj_bp.name, icon='LATTICE_DATA')

        row = prompt_box.row(align=True)  # Create a horizontal row
        split = row.split(factor=.85)  # Split the row into two columns

        # Add the left-justified label
        split.label(text=self.closet_name, icon='LATTICE_DATA')

        ver_text = f"v{self.closet.obj_bp.get('SNAP_VERSION')}"

        if not ver_text:
            ver_text = "version unknown"

        # Add the right-justified label
        split.label(text=ver_text, icon='INFO')

        split = prompt_box.split(factor=.5)

        self.draw_product_size(split)
        self.draw_common_prompts(split)

        row = prompt_box.row(align=True)
        row.prop_enum(self, "product_tabs", 'OPENINGS') 
        row.prop_enum(self, "product_tabs", 'CONSTRUCTION') 

        if self.product_tabs == 'OPENINGS':
            self.draw_splitter_widths(prompt_box)

        if self.product_tabs == 'CONSTRUCTION':
            self.draw_construction_options(prompt_box)

        # TODO: Check if on wall before displaying
        self.draw_product_placment(prompt_box)

    def draw_construction_options(self, layout):
        # prompts = []
        box = layout.box()

        toe_kick_height = self.closet.get_prompt("Toe Kick Height")
        toe_kick_setback = self.closet.get_prompt("Toe Kick Setback")
        # add_left_filler = self.closet.get_prompt("Add Left Filler")
        # add_right_filler = self.closet.get_prompt("Add Right Filler")
        # left_wall_filler = self.closet.get_prompt("Left Side Wall Filler")
        # right_wall_filler = self.closet.get_prompt("Right Side Wall Filler")
        add_top_accent_shelf = self.closet.get_prompt("Add Top Accent Shelf")
        top_shelf_overhang = self.closet.get_prompt("Top Shelf Overhang")
        crown_molding_height = self.closet.get_prompt("Crown Molding Height")
        crown_molding_depth = self.closet.get_prompt("Front Angle Height")
        extend_left_end_pard_forward = self.closet.get_prompt("Extend Left End Pard Forward")
        extend_right_end_pard_forward = self.closet.get_prompt("Extend Right End Pard Forward")
        extend_left_end_pard_down = self.closet.get_prompt("Extend Left End Pard Down")
        extend_right_end_pard_down = self.closet.get_prompt("Extend Right End Pard Down")
        no_drill_left = self.closet.get_prompt("No Drilling Left Partition")
        no_drill_right = self.closet.get_prompt("No Drilling Right Partition")
        height_left_side = self.closet.get_prompt("Height Left Side")
        height_right_side = self.closet.get_prompt("Height Right Side")
        loc_left_side = self.closet.get_prompt("Loc Left Side")
        loc_right_side = self.closet.get_prompt("Loc Right Side")
        add_hanging_rail = self.closet.get_prompt("Add Hanging Rail")
        left_filler_setback_amount = self.closet.get_prompt("Left Filler Setback Amount")
        right_filler_setback_amount = self.closet.get_prompt("Right Filler Setback Amount")        
        left_end_deduction = self.closet.get_prompt("Left End Deduction")
        right_end_deduction = self.closet.get_prompt("Right End Deduction")
        edge_bottom_of_left_filler = self.closet.get_prompt("Edge Bottom of Left Filler")
        edge_bottom_of_right_filler = self.closet.get_prompt("Edge Bottom of Right Filler")
        add_capping_left_filler = self.closet.get_prompt("Add Capping Left Filler")
        add_capping_right_filler = self.closet.get_prompt("Add Capping Right Filler")
        add_hutch_backing = self.closet.get_prompt("Add Hutch Backing")

        # edge_bottom_of_filler = self.closet.get_prompt("Edge Bottom of Filler")
        # remove_top_shelf = self.closet.get_prompt("Remove Top Shelf")

        # SIDE OPTIONS:
        self.draw_ctf_options(box)

        # if remove_top_shelf:
        #     remove_top_shelf.draw_prompt(box,split_text=False)

        self.draw_top_options(box)
        self.draw_cleat_options(box)
        self.draw_bottom_options(box)
        self.draw_bottom_edgebanding_options(box)

        # Fillers
        filler_box = box.box()
        split = filler_box.split()
        col = split.column(align=True)
        col.label(text="Filler Options:")
        row = col.row()
        row.prop(self, 'add_left_filler', text="Add Left Filler")
        row.prop(self, 'add_right_filler', text="Add Right Filler")
        row = col.row()
        distance_row = col.row()
        setback_amount_row = col.row()
        capping_filler_row = col.row()
        edge_row = col.row()

        if self.add_left_filler:
            distance_row.prop(self, 'left_filler_amt', text="Left Filler Amount")
            setback_amount_row.prop(left_filler_setback_amount, 'distance_value', text="Left Filler Setback Amount")
            capping_filler_row.prop(add_capping_left_filler, 'checkbox_value', text="Add Capping Left Filler")
            edge_row.prop(edge_bottom_of_left_filler, 'checkbox_value', text="Edge Bottom of Left Filler")

        elif self.add_right_filler:
            distance_row.label(text="")
            setback_amount_row.label(text="")
            capping_filler_row.label(text="")
            edge_row.label(text="")

        if self.add_right_filler:
            distance_row.prop(self, 'right_filler_amt', text="Right Filler Amount")
            setback_amount_row.prop(right_filler_setback_amount, 'distance_value', text="Right Filler Setback Amount")
            capping_filler_row.prop(add_capping_right_filler, 'checkbox_value', text="Add Capping Right Filler")
            edge_row.prop(edge_bottom_of_right_filler, 'checkbox_value', text="Edge Bottom of Right Filler")

        elif self.add_left_filler:
            distance_row.label(text="")
            setback_amount_row.label(text="")
            capping_filler_row.label(text="")
            edge_row.label(text="")

        row = box.row()

        split = box.split()
        col = split.column(align=True)
        col.label(text="Left/Right End Options:")
        if no_drill_left and no_drill_right:
            row = col.row()
            row.prop(no_drill_left, 'checkbox_value', text="No Drilling Left Partition")
            row.prop(no_drill_right, 'checkbox_value', text="No Drilling Right Partition")
        row = col.row()
        row.prop(extend_left_end_pard_down, 'checkbox_value', text="Extend Left Partition")
        row.prop(extend_right_end_pard_down, 'checkbox_value', text="Extend Right Partition")
        forward_row = col.row()
        down_row = col.row()
        hutch_row = col.row()
        if extend_left_end_pard_down and extend_right_end_pard_down:
            if extend_left_end_pard_down.get_value():
                row = col.row()
                forward_row.prop(left_end_deduction, 'distance_value', text="Left Forward Extension Amount")
                down_row.prop(height_left_side, 'distance_value', text="Left Down Extension Amount")
            elif extend_right_end_pard_down.get_value():
                forward_row.label(text="")
                down_row.label(text="")
            if extend_right_end_pard_down.get_value():
                forward_row.prop(right_end_deduction, 'distance_value', text="Right Forward Extension Amount")
                down_row.prop(height_right_side, 'distance_value', text="Right Down Extension Amount")
            elif extend_left_end_pard_down.get_value():
                forward_row.label(text="")
                down_row.label(text="")

            if extend_left_end_pard_down.get_value() and extend_right_end_pard_down.get_value():
                hutch_row.prop(add_hutch_backing, 'checkbox_value', text="Add Hutch Backing")

        self.draw_dogear_and_corbel_options(box)

        # CARCASS OPTIONS:
        col = box.column(align=True)
        col.label(text="Full Back Options:")
        row = col.row()
        self.draw_backing_options(box)

        self.draw_blind_corner_options(box)

        if add_top_accent_shelf and top_shelf_overhang:
            row = col.row()
            row.prop(add_top_accent_shelf, 'checkbox_value', text="Add Top Accent Shelf")
            row.prop(top_shelf_overhang, 'distance_value', text="Top Shelf Overhang")

        if crown_molding_height and crown_molding_depth:
            row = col.row()
            row.prop(crown_molding_height, 'distance_value', text="Crown Molding Height")
            row.prop(crown_molding_depth, 'distance_value', text="Crown Molding Depth")

        col = box.column(align=True)
        col.label(text="Base Options:")

        # TOE KICK OPTIONS
        if toe_kick_height and toe_kick_setback:
            row = col.row()

            row.label(text="Toe Kick")
            row.prop(self, "tk_height", text="Height")
            #     row.label(text="Toe Kick")
            #     row.prop(toe_kick_height, "distance_value", text="Height")

    def draw_splitter_widths(self, layout):
        props = bpy.context.scene.sn_closets

        col = layout.column(align=True)
        box = col.box()
        row = box.row()
        row.label(text="Section:")
        row.label(text="", icon='BLANK1')
        row.label(text="Interior Width:")
        if not self.is_island or not self.is_single_island:
            row.label(text="Pard Size:")
            row.label(text="Depth:")

        box = col.box()

        for i in range(1, 10):
            calculator = self.closet.get_calculator('Opening Widths Calculator')
            width = eval("calculator.get_calculator_prompt('Opening {} Width')".format(str(i)))
            height = self.closet.get_prompt("Opening " + str(i) + " Height")
            depth = self.closet.get_prompt("Opening " + str(i) + " Depth")
            show_door_limit_warning = False

            if self.op_door_height_exceeded:
                opening = self.op_door_height_exceeded.get(str(i))
                if opening:
                    show_door_limit_warning = True
                    message = "Traviso door style not permitted in sizes above 47H!"

            if width:
                row = box.row()

                if show_door_limit_warning:
                    row.label(text=str(i) + ":", icon='ERROR')
                else:
                    row.label(text=str(i) + ":")

                # Opening width is set to equal
                if width.equal is False:
                    row.prop(self, f"op_{str(i)}_width_equal", text="")
                else:
                    if self.get_number_of_equal_widths() != 1:
                        row.prop(self, f"op_{str(i)}_width_equal", text="")
                    else:
                        row.label(text="", icon='BLANK1')

                # Opening width
                if width.equal:
                    row.label(text=str(round(sn_unit.meter_to_active_unit(width.distance_value), 3)) + '"')
                else:
                    row.prop(self, f'op_{str(i)}_width', text="")

                floor_mount = eval("self.op_{}_floor_mount".format(str(i)))
                row.prop(self, "op_{}_floor_mount".format(str(i)), text="", icon='TRIA_DOWN' if floor_mount else 'TRIA_UP')

                if props.closet_defaults.use_32mm_system:
                    row.prop(self, 'opening_' + str(i) + '_height', text="")
                else:
                    row.prop(height, 'distance_value', text="")
                row.prop(depth, 'distance_value', text="")

                if show_door_limit_warning:
                    warning_box = box.box()
                    row = warning_box.row()
                    row.label(text=message)

    def draw_ctf_options(self,layout):
        prompts = []

        for i in range(1,10):
            prompt = self.closet.get_prompt("CTF Opening " + str(i))
            if prompt:
                prompts.append(prompt)
                
        row = layout.row()
        row.label(text="Variable Section:")
        for i, prompt in enumerate(prompts):
            row.prop(prompt, "checkbox_value", text=str(i + 1))

    def draw_backing_options(self, layout):
        full_back_prompts = []
        top_back_thickness_prompts = []
        center_back_thickness_prompts = []
        bottom_back_thickness_prompts = []
        add_all_ppt = self.closet.get_prompt("Add Backing Throughout")

        for i in range(1, 10):
            add_full_back = self.closet.get_prompt("Add Full Back " + str(i))
            top_back_thickness = self.closet.get_prompt("Opening " + str(i) + " Top Backing Thickness")
            center_back_thickness = self.closet.get_prompt("Opening " + str(i) + " Center Backing Thickness")
            bottom_back_thickness = self.closet.get_prompt("Opening " + str(i) + " Bottom Backing Thickness")

            if add_full_back:
                full_back_prompts.append(add_full_back)
            if top_back_thickness:
                top_back_thickness_prompts.append(top_back_thickness)
            if center_back_thickness:
                center_back_thickness_prompts.append(center_back_thickness)
            if bottom_back_thickness:
                bottom_back_thickness_prompts.append(bottom_back_thickness)

        box = layout.box()

        if add_all_ppt:
            row = box.row()
            row.prop(self, 'add_backing_throughout')

        row = box.row()

        for i in range(self.closet.opening_qty):
            col = row.column(align=True)
            full_back_ppt = full_back_prompts[i]
            col.prop(self, 'op_{}_full_back'.format(str(i + 1)), text=str(i + 1))

            if full_back_ppt.get_value():
                # Disable for now TODO: 3/4" capping full back
                # if back_thickness_prompts[i].get_value() == '3/4"':
                #     col.prop(inset_prompts[i], "checkbox_value", text="Inset")

                for child in self.closet.obj_bp.children:
                    if child.sn_closets.is_back_bp:
                        if child.sn_closets.opening_name == str(i + 1):
                            back_assembly = sn_types.Assembly(child)
                            is_single_back = back_assembly.get_prompt('Is Single Back')
                            backing_sections = back_assembly.get_prompt("Backing Sections")
                            use_top = back_assembly.get_prompt("Top Section Backing")
                            use_center = back_assembly.get_prompt("Center Section Backing")
                            use_bottom = back_assembly.get_prompt("Bottom Section Backing")
                            single_back = back_assembly.get_prompt("Single Back")
                            BIB = back_assembly.get_prompt("Bottom Insert Backing")
                            BIG = back_assembly.get_prompt("Bottom Insert Gap")

                            #1 Section
                            if backing_sections and backing_sections.get_value() == 1:
                                col.prop(use_center, 'checkbox_value', text="Back " + str(i + 1))
                                if use_center.get_value():
                                    center_back_thickness_prompts[i].draw_combobox_prompt(col, text=" ")

                            # 2 Section
                            if backing_sections and backing_sections.get_value() == 2:
                                show_single_back = use_top.get_value() and use_bottom.get_value()
                                no_gap = True
                                if BIB and BIG:
                                    if BIB.get_value() > 0 and BIG.get_value() > 0:
                                        no_gap = False

                                # Single back
                                if show_single_back and no_gap:
                                    single_back.draw(col, alt_text="Single Back", allow_edit=False)

                                    if is_single_back.get_value():
                                        center_back_thickness_prompts[i].draw_combobox_prompt(col, text=" ")

                                # Top
                                use_top = back_assembly.get_prompt("Top Section Backing")
                                col.prop(use_top, 'checkbox_value', text="Top " + str(i + 1))
                                if use_top.get_value() and not is_single_back.get_value():
                                    top_back_thickness_prompts[i].draw_combobox_prompt(col, text=" ")

                                # Bottom
                                use_bottom = back_assembly.get_prompt("Bottom Section Backing")
                                col.prop(use_bottom, 'checkbox_value', text="Bottom " + str(i + 1))
                                if use_bottom.get_value() and not is_single_back.get_value():
                                    bottom_back_thickness_prompts[i].draw_combobox_prompt(col, text=" ")

                            # 3 Section
                            if backing_sections and backing_sections.get_value() == 3:
                                single_back_config = [
                                    use_top.get_value() and use_bottom.get_value() and use_center.get_value(),
                                    use_top.get_value() and use_center.get_value(),
                                    use_bottom.get_value() and use_center.get_value()
                                ]

                                no_gap = True
                                top = use_top.get_value()
                                ctr = use_center.get_value()
                                btm = use_bottom.get_value()
                                if BIB and BIG:
                                    if BIB.get_value() > 0 and BIG.get_value() > 0:
                                        if top and ctr and not btm:
                                            no_gap = True
                                        else:
                                            no_gap = False

                                if any(single_back_config) and no_gap:
                                    single_back.draw(col, alt_text="Single Back", allow_edit=False)
                                    if single_back.get_value():
                                        center_back_thickness_prompts[i].draw_combobox_prompt(col, text=" ")

                                #Top
                                use_top = back_assembly.get_prompt("Top Section Backing")
                                col.prop(use_top, 'checkbox_value', text="Top " + str(i + 1))
                                if use_top.get_value() and not is_single_back.get_value():
                                    top_back_thickness_prompts[i].draw_combobox_prompt(col, text=" ")

                                #Center
                                use_center = back_assembly.get_prompt("Center Section Backing")
                                col.prop(use_center, 'checkbox_value', text="Center " + str(i + 1))
                                if use_center.get_value() and not is_single_back.get_value():
                                    center_back_thickness_prompts[i].draw_combobox_prompt(col, text=" ")

                                #Bottom
                                use_bottom = back_assembly.get_prompt("Bottom Section Backing")
                                col.prop(use_bottom, 'checkbox_value', text="Bottom " + str(i + 1))
                                if use_bottom.get_value() and not is_single_back.get_value():
                                    bottom_back_thickness_prompts[i].draw_combobox_prompt(col, text=" ")

    def draw_cleat_options(self,layout):
        prompts = []

        for i in range(1,10):
            prompt = self.closet.get_prompt("Add " + str(i) + " Bottom Cleat")
            if prompt:
                prompts.append(prompt)

        row = layout.row()
        row.label(text="Bottom Cleat:")
        for i, prompt in enumerate(prompts):
            row.prop(prompt, "checkbox_value", text=str(i + 1))

        prompts_drawn = 1
        for i, prompt in enumerate(prompts):
            if prompt.checkbox_value:
                prompts_drawn += 1

        row = layout.split(factor=1/prompts_drawn)
        row.label(text="Custom Cleat Locations:")
        for i, prompt in enumerate(prompts):
            cleat_row = row.column()
            show = self.closet.get_prompt("Use " + str(i + 1) + " Custom Cleat Location")
            cleat_row.prop(show, "checkbox_value", text=str(i + 1))
            if prompt.checkbox_value and show.get_value():
                loc_prompt = self.closet.get_prompt("Cleat " + str(i + 1) + " Location")
                cleat_row.prop(loc_prompt, "distance_value", text=str(i + 1))

    def draw_dogear_and_corbel_options(self, layout):
        front_angle_height = self.closet.get_prompt("Front Angle Height")
        front_angle_depth = self.closet.get_prompt("Front Angle Depth")
        dog_ear_active = self.closet.get_prompt("Dog Ear Active")
        corbel_partitions = self.closet.get_prompt('Corbel Partitions')
        corbel_height_all = self.closet.get_prompt('Corbel Height All')

        row = layout.row()
        row.label(text="Dog Ear and Corbel Options:")
        box = layout.box()
        col = box.column()
        split = col.split(factor=0.5)

        col = split.column()
        row = col.row()
        row.label(text="Active Dog Ear:")
        row.prop(dog_ear_active, "checkbox_value",text="")

        if dog_ear_active.get_value():
            row = col.row()
            row.label(text="Dog Ear To Depth:")
            col = row.column()
            col.prop(front_angle_depth, 'distance_value', text="")

        col = split.column()
        row = col.row()
        row.label(text="Corbel Partitions:")
        row.prop(corbel_partitions, "checkbox_value",text="")

        if corbel_partitions.get_value():
            row = col.row()
            row.label(text="Corbel Height:")
            col = row.column()
            col.prop(corbel_height_all, 'distance_value', text="")

    def draw_top_options(self,layout):
        prompts = []
        for i in range(1,10):
            prompt = self.closet.get_prompt("Remove Top Shelf " + str(i))
            if prompt:
                prompts.append(prompt)            
            
        row = layout.row()
        row.label(text="Top KD:")
        for i, prompt in enumerate(prompts):
            row.prop(prompt,"checkbox_value",text=str(i + 1))      

    def draw_bottom_options(self, layout):
        prompts = []

        for i in range(1, 10):
            prompt = self.closet.get_prompt("Remove Bottom Hanging Shelf " + str(i))
            if prompt:
                prompts.append(prompt)

        row = layout.row()
        row.label(text="Bottom KD:")
        for i, prompt in enumerate(prompts):
            op_floor_mount = eval("self.op_" + str(i + 1) + "_floor_mount")
            col = row.column()

            if op_floor_mount:
                row = row.row()
                col.prop(prompt, "checkbox_value", text=str(i + 1))
                col.enabled = False
            else:
                col.prop(prompt, "checkbox_value", text=str(i + 1))
                col.enabled = True

    def draw_bottom_edgebanding_options(self, layout):
        prompts = []
        for i in range(1, 11):
            prompt = self.closet.get_prompt("Panel " + str(i) + " Exposed Bottom")
            if prompt:
                prompts.append(prompt)

        row = layout.row()
        row.label(text="Edge Bottom of Partition:")
        row = layout.row()
        for i, prompt in enumerate(prompts):
            row.prop(prompt,"checkbox_value",text=str(i + 1))

    def draw_blind_corner_options(self, layout):
        blind_corner_left = self.closet.get_prompt("Blind Corner Left")
        blind_corner_right = self.closet.get_prompt("Blind Corner Right")
        blind_corner_left_depth = self.closet.get_prompt("Blind Corner Left Depth")
        blind_corner_right_depth = self.closet.get_prompt("Blind Corner Right Depth")

        if blind_corner_left and blind_corner_right:
            row = layout.row()
            row.label(text="Blind Corner Options:")

            row = layout.row()
            row.prop(self, "add_left_blind", text="Left")

            if blind_corner_left and blind_corner_left.get_value():
                row.prop(blind_corner_left_depth, "distance_value", text="Depth: ")

            row = layout.row()
            row.prop(self, "add_right_blind", text="Right")

            if blind_corner_right and blind_corner_right.get_value():
                row.prop(blind_corner_right_depth, "distance_value", text="Depth: ")

    def draw_product_placment(self, layout):
        box = layout.box()

        row = box.row(align=True)
        row.label(text='Placement',icon='LATTICE_DATA')
        row.prop_enum(self, "placement_on_wall", 'SELECTED_POINT', icon='RESTRICT_SELECT_OFF', text="Selected Point")
        row.prop_enum(self, "placement_on_wall", 'FILL', icon='ARROW_LEFTRIGHT', text="Fill")
        row.prop_enum(self, "placement_on_wall", 'LEFT', icon='TRIA_LEFT', text="Left")
        row.prop_enum(self, "placement_on_wall", 'CENTER', icon='TRIA_UP_BAR', text="Center")
        row.prop_enum(self, "placement_on_wall", 'RIGHT', icon='TRIA_RIGHT', text="Right")

        if self.placement_on_wall == 'FILL':
            row = box.row()
            row.label(text='Offset', icon='ARROW_LEFTRIGHT')
            row.prop(self, "left_offset", icon='TRIA_LEFT', text="Left")
            row.prop(self, "right_offset", icon='TRIA_RIGHT', text="Right")

        if self.placement_on_wall in 'LEFT':
            row = box.row()
            row.label(text='Offset', icon='BACK')
            row.prop(self, "left_offset", icon='TRIA_LEFT', text="Left")

        if self.placement_on_wall in 'CENTER':
            row = box.row()

        if self.placement_on_wall in 'RIGHT':
            row = box.row()
            row.label(text='Offset', icon='FORWARD')
            row.prop(self, "right_offset", icon='TRIA_RIGHT', text="Right")

        if self.placement_on_wall == 'SELECTED_POINT':
            row = box.row()
            row.label(text='Location:')
            row.prop(self, 'current_location', text="")

        row.label(text='Move Off Wall:')
        row.prop(self.closet.obj_bp, 'location', index=1, text="")

        row.label(text='Rotation:')
        row.prop(self.closet.obj_bp, 'rotation_euler', index=2, text="")

    def update_product_size(self):
        if 'IS_MIRROR' in self.closet.obj_x and self.closet.obj_x['IS_MIRROR']:
            self.closet.obj_x.location.x = -self.width
        else:
            self.closet.obj_x.location.x = self.width

        if 'IS_MIRROR' in self.closet.obj_y and self.closet.obj_y['IS_MIRROR']:
            self.closet.obj_y.location.y = -self.depth
        else:
            self.closet.obj_y.location.y = self.depth

        if 'IS_MIRROR' in self.closet.obj_z and self.closet.obj_z['IS_MIRROR']:
            self.closet.obj_z.location.z = -self.height
        else:
            self.closet.obj_z.location.z = self.height

    def update_opening_heights(self):
        opening_qty = self.closet.get_prompt("Opening Quantity").get_value()

        for i in range(1, opening_qty + 1):
            opening_height = self.closet.get_prompt("Opening " + str(i) + " Height")
            if opening_height:
                height = eval("float(self.opening_" + str(i) + "_height)/1000")
                opening_height.set_value(height)
    
    def update_opening_floors(self):
        opening_qty = self.closet.get_prompt("Opening Quantity").get_value()

        for i in range(1, opening_qty + 1):
            opening_floor = self.closet.get_prompt("Opening " + str(i) + " Floor Mounted")
            if opening_floor:
                floor = eval("self.Opening_" + str(i) + "_Floor_Mounted")
                opening_floor.set_value(floor)

    def update_opening_floors(self):
        opening_qty = self.closet.get_prompt("Opening Quantity").get_value()

        for i in range(1, opening_qty + 1):
            opening_floor = self.closet.get_prompt("Opening " + str(i) + " Floor Mounted")
            if opening_floor:
                floor = eval("self.op_" + str(i) + "_floor_mount")
                opening_floor.set_value(floor)

        self.update_panel_materials()

    def update_panel_materials(self):
        for child in self.closet.obj_bp.children:
            if child.sn_closets.is_panel_bp:
                panel = sn_types.Assembly(child)
                self.set_panel_material(panel)

        bpy.ops.snap.update_scene_from_pointers()

    def update_flat_molding_heights(self):
        molding_bps = [obj for obj in self.closet.obj_bp.children if 'IS_BP_CROWN_MOLDING' in obj]
        wall_bp = self.closet.obj_bp.parent
        wall = sn_types.Assembly(wall_bp)

        for obj_bp in molding_bps:
            molding = sn_types.Assembly(obj_bp)
            dist_from_ceiling = molding.get_prompt('Distance From Ceiling')
            if dist_from_ceiling:
                dist_from_ceiling.set_value(wall.obj_z.location.z - molding.obj_bp.location.z)

    def update_top_shelf_location(self, top_shelf):
        top_assembly = sn_types.Assembly(obj_bp=top_shelf)
        closet = self.closet
        opening_qty = closet.get_prompt("Opening Quantity").get_value()
        left_thk = closet.get_prompt("Left Side Thickness").get_value()
        panel_thk = closet.get_prompt("Panel Thickness").get_value()
        right_thk = closet.get_prompt("Left Side Thickness").get_value()
        width_1 = closet.get_prompt("Opening 1 Width").distance_value
        tk_height = closet.get_prompt("Toe Kick Height").distance_value
        use_left_filler = closet.get_prompt("Add Left Filler").get_value()
        use_right_filler = closet.get_prompt("Add Right Filler").get_value()
        left_filler_amt = closet.get_prompt("Left Side Wall Filler").get_value()
        right_filler_amt = closet.get_prompt("Right Side Wall Filler").get_value()
        right_filler = 0
        left_filler = 0

        # Include left and right filler amt if in use
        if use_left_filler:
            left_filler = left_filler_amt
        if use_right_filler:
            right_filler = right_filler_amt

        opening_loc_x = left_filler + left_thk
        opening_dim_x = width_1
        top_loc_x = top_assembly.obj_bp.location.x
        top_dim_x = top_assembly.obj_x.location.x
        is_all_floor = True
        max_op_height = 0

        for i in range(1, opening_qty + 1):
            height = closet.get_prompt("Opening " + str(i) + " Height")
            width = closet.get_prompt("Opening " + str(i) + " Width").distance_value
            height = height.distance_value
            is_floor_mounted = closet.get_prompt("Opening " + str(i) + " Floor Mounted").get_value()
            is_op_covered = False

            if round(top_loc_x, 2) <= round(opening_loc_x, 2):
                if round(top_loc_x + top_dim_x - panel_thk * i, 2) >= round(opening_loc_x, 2):
                    is_op_covered = True

            if is_op_covered:
                is_all_floor = is_all_floor and is_floor_mounted
                if height > max_op_height:
                    max_op_height = height

            if i == opening_qty - 1:
                opening_dim_x = width + right_thk + right_filler
            else:
                opening_dim_x = width + panel_thk
            opening_loc_x += opening_dim_x

        if is_all_floor:
            top_assembly.obj_bp.location.z = max_op_height + tk_height
        else:
            top_assembly.obj_bp.location.z = closet.obj_z.location.z

    def update_top_location(self):
        children = self.closet.obj_bp.children
        for child in children:
            if "Top Shelf" in child.name:
                top_shelf = child
                self.update_top_shelf_location(top_shelf)

    def check_tk_height(self):
        toe_kick_height = self.closet.get_prompt("Toe Kick Height").distance_value

        if toe_kick_height < sn_unit.inch(3):
            self.closet.get_prompt("Toe Kick Height").set_value(sn_unit.inch(3))

            if self.countertop:
                self.countertop.obj_bp.location.z += sn_unit.inch(3) - toe_kick_height

            # we need to make sure everything else is synched up with the forced change
            bpy.ops.snap.log_window(
                'INVOKE_DEFAULT',
                message="Minimum Toe Kick Height is 3\"",
                icon="ERROR")

    def update_tk_height(self):
        toe_kick_height = self.closet.get_prompt("Toe Kick Height").distance_value
        children = self.closet.obj_bp.children
        for child in children:
            if "Toe Kick" in child.name:
                toe_kick = child
                tk = sn_types.Assembly(toe_kick)
                tk_height_ppt = tk.get_prompt("Toe Kick Height")
                if tk_height_ppt:
                    tk_height_ppt.set_value(toe_kick_height)

    def reset_fillers(self):
        add_left_filler = self.closet.get_prompt("Add Left Filler").get_value()
        add_right_filler = self.closet.get_prompt("Add Right Filler").get_value()

        if not add_left_filler:
            left_wall_filler = self.closet.get_prompt("Left Side Wall Filler")
            left_filler_setback_amount = self.closet.get_prompt("Left Filler Setback Amount")
            edge_bottom_of_left_filler = self.closet.get_prompt("Edge Bottom of Left Filler")
            add_capping_left_filler = self.closet.get_prompt("Add Capping Left Filler")
            left_wall_filler.set_value(0)
            self.left_filler_amt = 0
            left_filler_setback_amount.set_value(0)
            edge_bottom_of_left_filler.set_value(False)
            add_capping_left_filler.set_value(False)

        if not add_right_filler:
            right_wall_filler = self.closet.get_prompt("Right Side Wall Filler")
            right_filler_setback_amount = self.closet.get_prompt("Right Filler Setback Amount")
            edge_bottom_of_righ_filler = self.closet.get_prompt("Edge Bottom of Right Filler")
            add_capping_right_filler = self.closet.get_prompt("Add Capping Right Filler")
            right_wall_filler.set_value(0)
            self.right_filler_amt = 0
            right_filler_setback_amount.set_value(0)
            edge_bottom_of_righ_filler.set_value(False)
            add_capping_right_filler.set_value(False)

    def check_front_angle_depth(self):
        Dog_Ear_Active = self.closet.get_prompt('Dog Ear Active').get_value()
        Front_Angle_Depth = self.closet.get_prompt('Front Angle Depth')

        if not Dog_Ear_Active:
            Front_Angle_Depth.set_value(sn_unit.inch(12))

    def check_corbel_height(self):
        Corbel_Partitions = self.get_prompt('Corbel Partitions').get_var('Corbel_Partitions')
        Corbel_Height = self.get_prompt('Corbel Height').get_var('Corbel_Height')
        if Corbel_Partitions:
            Corbel_Height.set_value(sn_unit.inch(12))

    def check_hang_height(self):
        """Check and update openings for floor mounted/hanging toggle"""
        closet = self.closet
        opening_qty = closet.get_prompt("Opening Quantity").get_value()

        for i in range(1, opening_qty + 1):
            floor_mount_ppt_name = "Opening " + str(i) + " Floor Mounted"
            is_floor_mounted = closet.get_prompt(floor_mount_ppt_name).get_value()
            remove_btm_kd = closet.get_prompt("Remove Bottom Hanging Shelf " + str(i))

            if is_floor_mounted:
                remove_btm_kd.set_value(True)
                tk_height = closet.get_prompt("Toe Kick Height").distance_value
                opening_height = closet.get_prompt("Opening " + str(i) + " Height").distance_value
                height = opening_height + tk_height
                if height > closet.obj_z.location.z:
                    self.closet.obj_z.location.z = height
                    self.hang_height = height
            else:
                if self.op_is_floor_mount[floor_mount_ppt_name]:
                    remove_btm_kd.set_value(False)
                self.update_opening_inserts()

            self.op_is_floor_mount[floor_mount_ppt_name] = is_floor_mounted

    def get_panel(self, num):
        for child in self.closet.obj_bp.children:
            if 'IS_BP_PANEL' in child and 'PARTITION_NUMBER' in child:
                if child.get("PARTITION_NUMBER") == num:
                    return sn_types.Assembly(child)

    def update_opening_equal_status(self):
        opening_qty = self.closet.get_prompt("Opening Quantity").get_value()

        for i in range(1, opening_qty + 1):
            opening_width = self.closet.get_prompt("Opening " + str(i) + " Width")

            if opening_width:
                equal = eval(f"self.op_{str(i)}_width_equal")
                opening_width.equal = equal

                if not equal:
                    exec(f"self.op_{str(i)}_width = opening_width.distance_value")

        self.run_calculators(self.closet.obj_bp)

    def update_opening_widths(self):
        opening_qty = self.closet.get_prompt("Opening Quantity").get_value()

        for i in range(1, opening_qty + 1):
            opening_width = self.closet.get_prompt("Opening " + str(i) + " Width")

            if opening_width:
                width = eval(f"float(self.op_{str(i)}_width)")
                opening_width.set_value(width)

        self.run_calculators(self.closet.obj_bp)

    def update_backing_ppts(self, opening_num):
        add_backing_throughout_ppt = self.closet.get_prompt("Add Backing Throughout")
        add_backing_ppt = self.closet.get_prompt("Add Full Back " + str(opening_num))
        backing_parts = self.closet.backing_parts[str(opening_num)]

        if self.prev_all_backing != self.add_backing_throughout and add_backing_throughout_ppt:
            if self.add_backing_throughout and add_backing_throughout_ppt:
                if add_backing_ppt:
                    add_backing_ppt.set_value(self.add_backing_throughout)
                add_backing_throughout_ppt.set_value(self.add_backing_throughout)

            for part in backing_parts:
                use_top = part.get_prompt("Top Section Backing")
                use_center = part.get_prompt("Center Section Backing")
                use_bottom = part.get_prompt("Bottom Section Backing")

                if use_top:
                    use_top.set_value(self.add_backing_throughout)
                if use_center:
                    use_center.set_value(self.add_backing_throughout)
                if use_bottom:
                    use_bottom.set_value(self.add_backing_throughout)

            add_backing_throughout_ppt.set_value(self.add_backing_throughout)
            add_backing_ppt.set_value(self.add_backing_throughout)

    def update_backing(self, context):
        for i in range(self.closet.opening_qty):
            opening_num = i + 1
            add_backing_ppt = self.closet.get_prompt("Add Full Back " + str(opening_num))
            self.update_backing_ppts(opening_num)

            # Find backing parts for current opening
            if str(opening_num) in self.closet.backing_parts.keys():
                backing_parts = self.closet.backing_parts[str(opening_num)]

            # If adding backing throughout, and there are no backing parts, add backing
            if add_backing_ppt.get_value() and not backing_parts:
                if opening_num == 1:
                    self.closet.add_backing(opening_num, None)
                    self.closet.update()
                else:
                    panel = self.get_panel(i)
                    self.closet.add_backing(opening_num, panel)
                    self.closet.update()

                self.update_backing_ppts(opening_num)

            # If not adding backing throughout, and there are backing parts, remove backing
            if not add_backing_ppt.get_value() and backing_parts:
                for assembly in backing_parts:
                    sn_utils.delete_object_and_children(assembly.obj_bp)

                backing_parts.clear()

                for child in self.closet.obj_bp.children:
                    obj_props = child.sn_closets
                    props = [
                        obj_props.is_drawer_stack_bp,
                        obj_props.is_hamper_insert_bp,
                        obj_props.is_door_insert_bp,
                        obj_props.is_closet_bottom_bp,
                        obj_props.is_closet_top_bp,
                        obj_props.is_splitter_bp,
                        "IS_BP_ROD_AND_SHELF" in child,
                        "IS_BP_TOE_KICK_INSERT" in child,
                        "IS_BP_SHOE_SHELVES" in child]

                    if any(props):
                        child_assembly = sn_types.Assembly(child)
                        setback_ppt = child_assembly.get_prompt("Shelf Backing Setback")
                        if setback_ppt:
                            setback_ppt.set_value(0)

        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.closet_materials.assign_materials()
        self.prev_all_backing = self.add_backing_throughout

    def update_blind_corners(self):
        more_than_one_opening = self.closet.get_prompt("Opening 2 Height")
        blind_corner_left = self.closet.get_prompt("Blind Corner Left")
        blind_corner_right = self.closet.get_prompt("Blind Corner Right")

        blind_corner_left.set_value(self.add_left_blind)
        blind_corner_right.set_value(self.add_right_blind)

        if self.add_left_blind and self.add_right_blind:
            if more_than_one_opening:
                blind_corner_left.set_value(blind_corner_left.get_value())
                blind_corner_right.set_value(blind_corner_right.get_value())
            else:
                if self.add_left_blind:
                    blind_corner_right.set_value(False)
                    self.add_left_blind = False
                elif self.add_right_blind:
                    blind_corner_left.set_value(False)
                    self.add_right_blind = False

    def update_end_conditions(self, context):
        left_end_condition = self.closet.get_prompt("Left End Condition")
        right_end_condition = self.closet.get_prompt("Right End Condition")
        props_exist = 'left_end_condition' in self.properties.keys() and 'right_end_condition' in self.properties.keys()

        if left_end_condition and right_end_condition and props_exist:
            enum_index = self.properties['left_end_condition']
            left_end_condition.set_value(enum_index)

            enum_index = self.properties['right_end_condition']
            right_end_condition.set_value(enum_index)
            mat_type = context.scene.closet_materials.materials.get_mat_type()

            if mat_type.name == "Garage Material":
                closet_props.update_render_materials(self, context)

    def update_countertop(self):
        """Update countertop Z location and depth"""

        if self.countertop:
            tallest_pard = self.countertop.get_prompt('Tallest Pard Height')
            Relative_Offset = self.countertop.get_prompt("Relative Offset")
            Countertop_Height = self.countertop.get_prompt("Countertop Height")

            # Set tallest pard height to hang height if not already set
            if tallest_pard and tallest_pard.get_value() != self.hang_height:
                tallest_pard.set_value(self.hang_height)

            # Set countertop height prompt value to tallest pard height + relative offset
            if Relative_Offset is not None and Countertop_Height is not None:
                Countertop_Height.set_value(tallest_pard.get_value() + Relative_Offset.get_value())

            # Set countertop Z location to countertop height prompt value
            if Countertop_Height is not None:
                self.countertop.obj_bp.location.z = Countertop_Height.get_value()

            # Adjust countertop depth to deepest opening
            opening_num = self.closet.get_prompt('Opening Quantity').get_value()
            max_depth = 0

            for i in range(1, opening_num + 1):
                current_depth = self.closet.get_prompt('Opening {} Depth'.format(i)).get_value()
                max_depth = max([max_depth, current_depth])

            self.countertop.obj_y.location.y = max_depth
            self.countertop.obj_bp.location.y = - max_depth

    def update_opening_inserts(self):
        start_time = time.perf_counter()

        capping_bottoms = 0

        for obj_bp in self.insert_bps:
            insert = sn_types.Assembly(obj_bp)
            obj_props = obj_bp.sn_closets
            Cleat_Loc = insert.get_prompt("Cleat Location")
            Shelf_Backing_Setback = insert.get_prompt("Shelf Backing Setback")
            Remove_Bottom_Shelf = insert.get_prompt("Remove Bottom Shelf")
            opening = insert.obj_bp.sn_closets.opening_name

            if insert and opening:
                if insert.obj_bp.sn_closets.is_splitter_bp:
                    floor = self.closet.get_prompt("Opening " + str(obj_bp.sn_closets.opening_name) + " Floor Mounted")
                    parent_remove_bottom_shelf = self.closet.get_prompt('Remove Bottom Hanging Shelf ' + str(obj_bp.sn_closets.opening_name))
                    remove_bottom_shelf = insert.get_prompt("Remove Bottom Shelf")
                    parent_has_bottom_kd = insert.get_prompt("Parent Has Bottom KD")
                    prompts = [floor, parent_remove_bottom_shelf, remove_bottom_shelf, parent_has_bottom_kd]

                    if all(prompts):
                        if parent_remove_bottom_shelf.get_value() or floor.get_value():
                            parent_has_bottom_kd.set_value(True)
                            remove_bottom_shelf.set_value(False)
                        else:
                            parent_remove_bottom_shelf.set_value(False)
                            remove_bottom_shelf.set_value(True)
                            parent_has_bottom_kd.set_value(False)

                for child in self.closet.obj_bp.children:
                    if child.sn_closets.is_back_bp and not child.sn_closets.is_hutch_back_bp:
                        if child.sn_closets.opening_name == opening:
                            # Upadate for backing configurations
                            back_assembly = sn_types.Assembly(child)
                            B_Sec = back_assembly.get_prompt('Backing Sections')
                            TOP = back_assembly.get_prompt("Top Section Backing")
                            CTR = back_assembly.get_prompt("Center Section Backing")
                            BTM = back_assembly.get_prompt("Bottom Section Backing")
                            BIB = back_assembly.get_prompt("Bottom Insert Backing")
                            BIG = back_assembly.get_prompt("Bottom Insert Gap")
                            SB = back_assembly.get_prompt("Single Back")
                            TBT = self.closet.get_prompt('Opening ' + str(opening) + ' Top Backing Thickness')
                            CBT = self.closet.get_prompt('Opening ' + str(opening) + ' Center Backing Thickness')
                            BBT = self.closet.get_prompt('Opening ' + str(opening) + ' Bottom Backing Thickness')
                            prompts = [B_Sec, TOP, CTR, BTM, SB, TBT, CBT, BBT]
                            # For backwards compatability/older library data
                            if all(prompts):
                                # 1 section backing drawer on bottom
                                if B_Sec.get_value() == 1:
                                    if CTR.get_value() and CBT.get_value() == 1:  # 1 is 3/4"
                                        if Cleat_Loc:
                                            Cleat_Loc.set_value(2)
                                    elif CTR.get_value() and CBT.get_value() in (0, 2):  # 0 is 1/4"
                                        if Cleat_Loc:
                                            Cleat_Loc.set_value(0)

                                    if "IS_BP_ROD_AND_SHELF" in obj_bp or obj_props.is_splitter_bp or obj_bp.get('IS_BP_SHOE_SHELVES'):
                                        if CTR.get_value():
                                            if CBT.get_value() == 1:
                                                Shelf_Backing_Setback.set_value(sn_unit.inch(0.75))
                                            else:
                                                Shelf_Backing_Setback.set_value(sn_unit.inch(0.25))
                                        else:
                                            Shelf_Backing_Setback.set_value(sn_unit.inch(0))

                                if B_Sec.get_value() == 2:
                                    single_back = SB.get_value() and TOP.get_value() and BTM.get_value()

                                    if obj_props.is_hamper_insert_bp:
                                        if single_back:
                                            Cleat_Loc.set_value(2)
                                            if CBT.get_value() == 1:
                                                Shelf_Backing_Setback.set_value(sn_unit.inch(0.75))
                                            else:
                                                Shelf_Backing_Setback.set_value(sn_unit.inch(0.25))
                                        elif TOP.get_value() and TBT.get_value() == 1:
                                            Cleat_Loc.set_value(2)
                                            Shelf_Backing_Setback.set_value(sn_unit.inch(0))
                                        elif TOP.get_value() and TBT.get_value() == 0:
                                            Shelf_Backing_Setback.set_value(sn_unit.inch(0))
                                            Cleat_Loc.set_value(0)
                                        else:
                                            Shelf_Backing_Setback.set_value(sn_unit.inch(0))

                                    if obj_props.is_drawer_stack_bp:
                                        if single_back:
                                            if CBT.get_value() == 0:
                                                Cleat_Loc.set_value(0)
                                            else:
                                                Cleat_Loc.set_value(2)

                                        elif BTM.get_value():
                                            if BBT.get_value() == 1:
                                                Cleat_Loc.set_value(0)
                                            else:
                                                Cleat_Loc.set_value(2)

                                    if obj_props.is_door_insert_bp:
                                        door_insert = sn_types.Assembly(obj_bp)
                                        use_bottom_kd_setback = door_insert.get_prompt("Use Bottom KD Setback")
                                        if use_bottom_kd_setback:
                                            use_bottom_kd_setback.set_value(single_back)
                                        if single_back or TOP.get_value():
                                            if CBT.get_value() == 1:
                                                Shelf_Backing_Setback.set_value(sn_unit.inch(0.75))
                                            else:
                                                Shelf_Backing_Setback.set_value(sn_unit.inch(0.25))
                                        else:
                                            Shelf_Backing_Setback.set_value(sn_unit.inch(0))

                                    if "IS_BP_ROD_AND_SHELF" in obj_bp:
                                        if single_back:
                                            if CBT.get_value() == 1:
                                                Shelf_Backing_Setback.set_value(sn_unit.inch(0.75))
                                            else:
                                                Shelf_Backing_Setback.set_value(sn_unit.inch(0.25))
                                        elif TOP.get_value():
                                            if TBT.get_value() == 1:
                                                Shelf_Backing_Setback.set_value(sn_unit.inch(0.75))
                                            else:
                                                Shelf_Backing_Setback.set_value(sn_unit.inch(0.25))
                                    
                                    if obj_props.is_splitter_bp or obj_bp.get('IS_BP_SHOE_SHELVES'):
                                        if single_back:
                                            if CBT.get_value() == 1:
                                                Shelf_Backing_Setback.set_value(sn_unit.inch(0.75))
                                            else:
                                                Shelf_Backing_Setback.set_value(sn_unit.inch(0.25))
                                        elif TOP.get_value():
                                            if TBT.get_value() == 1:
                                                Shelf_Backing_Setback.set_value(sn_unit.inch(0.75))
                                            else:
                                                Shelf_Backing_Setback.set_value(sn_unit.inch(0.25))
                                        else:
                                            Shelf_Backing_Setback.set_value(sn_unit.inch(0))

                                    if BIB and BIG:
                                        if BIB.get_value() > 0 and BIG.get_value() > 0:
                                            SB.set_value(False)
                                            if TOP.get_value() and Cleat_Loc:
                                                if TBT.get_value() == 1:
                                                    Cleat_Loc.set_value(2)
                                                if TBT.get_value() == 0:
                                                    Cleat_Loc.set_value(0)

                                if B_Sec.get_value() == 3:
                                    full_back = SB.get_value() and TOP.get_value() and CTR.get_value() and BTM.get_value()
                                    top_ctr_back = SB.get_value() and TOP.get_value() and CTR.get_value()
                                    btm_ctr_back = SB.get_value() and BTM.get_value() and CTR.get_value()
                                    top_back = TOP.get_value()

                                    if BIB and BIG:
                                        if BIB.get_value() > 0 and BIG.get_value() > 0:
                                            if not top_ctr_back:
                                                SB.set_value(False)

                                    if obj_props.is_hamper_insert_bp:
                                        if full_back or btm_ctr_back:
                                            Cleat_Loc.set_value(2)
                                            if CBT.get_value() == 1:
                                                Shelf_Backing_Setback.set_value(sn_unit.inch(0.75))
                                            else:
                                                Shelf_Backing_Setback.set_value(sn_unit.inch(0.25))
                                        elif top_ctr_back and CBT.get_value() == 1:
                                            Cleat_Loc.set_value(2)
                                        elif CTR.get_value() and CBT.get_value() == 1:
                                            Cleat_Loc.set_value(2)
                                        else:
                                            Cleat_Loc.set_value(0)
                                            Shelf_Backing_Setback.set_value(sn_unit.inch(0))

                                    if obj_props.is_door_insert_bp:
                                        door_insert = sn_types.Assembly(obj_bp)
                                        use_bottom_kd_setback = door_insert.get_prompt("Use Bottom KD Setback")
                                        if use_bottom_kd_setback:
                                            if full_back or top_ctr_back:
                                                use_bottom_kd_setback.set_value(True)
                                            else:
                                                use_bottom_kd_setback.set_value(False)

                                        if full_back or top_ctr_back:
                                            if CBT.get_value() == 1:
                                                Shelf_Backing_Setback.set_value(sn_unit.inch(0.75))
                                            else:
                                                Shelf_Backing_Setback.set_value(sn_unit.inch(0.25))
                                        elif top_back:
                                            if TBT.get_value() == 1:
                                                Shelf_Backing_Setback.set_value(sn_unit.inch(0.75))
                                            else:
                                                Shelf_Backing_Setback.set_value(sn_unit.inch(0.25))
                                        else:
                                            Shelf_Backing_Setback.set_value(sn_unit.inch(0))

                                    if "IS_BP_ROD_AND_SHELF" in obj_bp:
                                        if full_back or top_ctr_back:
                                            if CBT.get_value() == 1:
                                                Shelf_Backing_Setback.set_value(sn_unit.inch(0.75))
                                            else:
                                                Shelf_Backing_Setback.set_value(sn_unit.inch(0.25))
                                        else:
                                            Shelf_Backing_Setback.set_value(sn_unit.inch(0))

                                    if obj_props.is_splitter_bp or obj_bp.get('IS_BP_SHOE_SHELVES'):
                                        if full_back or top_ctr_back:
                                            if CBT.get_value() == 1:
                                                Shelf_Backing_Setback.set_value(sn_unit.inch(0.75))
                                            else:
                                                Shelf_Backing_Setback.set_value(sn_unit.inch(0.25))
                                        else:
                                            Shelf_Backing_Setback.set_value(sn_unit.inch(0))

                    if child.sn_closets.is_shelf_bp:
                        if child.sn_closets.opening_name == opening:
                            RBS = self.closet.get_prompt('Remove Bottom Hanging Shelf ' + str(opening))
                            RTS = self.closet.get_prompt('Remove Top Shelf ' + str(opening))
                            floor = self.closet.get_prompt("Opening " + str(opening) + " Floor Mounted")
                            prompts = [RBS, RTS, floor]

                            if all(prompts):
                                if obj_props.is_hamper_insert_bp:
                                    # For Hampers, Remove_Bottom_Shelf == True
                                    # means that there is no bottom shelf
                                    if(RBS.get_value() or floor.get_value()):
                                        Remove_Bottom_Shelf.set_value(True)
                                    else:
                                        Remove_Bottom_Shelf.set_value(False)

                                if obj_props.is_drawer_stack_bp:
                                    # For Drawers, Remove_Bottom_Shelf == False
                                    # means that there is no bottom shelf
                                    Lift_Drawers_From_Bottom = insert.get_prompt("Lift Drawers From Bottom")
                                    if((RBS.get_value() or floor.get_value()) and Lift_Drawers_From_Bottom.get_value() is False):
                                        Remove_Bottom_Shelf.set_value(False)
                                        insert.get_prompt("Pard Has Bottom KD").set_value(True)
                                    elif(Lift_Drawers_From_Bottom.get_value() is False):
                                        insert.get_prompt("Pard Has Bottom KD").set_value(False)
                                    else:
                                        insert.get_prompt("Pard Has Bottom KD").set_value(False)

                    if child.sn_closets.is_closet_bottom_bp:
                        capping_bottom_assembly = sn_types.Assembly(child)
                        capping_bottoms += 1
                        extend_left_end_pard_down = self.closet.get_prompt("Extend Left End Pard Down")
                        extend_right_end_pard_down = self.closet.get_prompt("Extend Right End Pard Down")
                        height_left_side = self.closet.get_prompt("Height Left Side")
                        height_right_side = self.closet.get_prompt("Height Right Side")
                        left_partition_extended = capping_bottom_assembly.get_prompt("Left Partition Extended")
                        right_partition_extended = capping_bottom_assembly.get_prompt("Right Partition Extended")
                        left_partition_extension_height = capping_bottom_assembly.get_prompt("Left Partition Extension Height")
                        right_partition_extension_height = capping_bottom_assembly.get_prompt("Right Partition Extension Height")
                        against_left_wall = capping_bottom_assembly.get_prompt('Against Left Wall')
                        against_right_wall = capping_bottom_assembly.get_prompt('Against Right Wall')
                        prompts = [
                            extend_left_end_pard_down, extend_right_end_pard_down, height_left_side, height_right_side,
                            left_partition_extended, right_partition_extended, left_partition_extension_height,
                            right_partition_extension_height, against_left_wall, against_right_wall]
                        if all(prompts):
                            left_partition_extended.set_value(extend_left_end_pard_down.get_value())
                            right_partition_extended.set_value(extend_right_end_pard_down.get_value())
                            left_partition_extension_height.set_value(height_left_side.get_value())
                            right_partition_extension_height.set_value(height_right_side.get_value())
                            if(extend_left_end_pard_down.get_value() and height_left_side.get_value() > 0):
                                against_left_wall.set_value(False)
                            if(extend_right_end_pard_down.get_value() and height_right_side.get_value() > 0):
                                against_right_wall.set_value(False)

                    if "IS_BP_ROD_AND_SHELF" in obj_bp:
                        extra_deep_pard = insert.get_prompt("Extra Deep Pard")
                        add_deep_rod_setback = insert.get_prompt("Add Deep Rod Setback")
                        depth = self.closet.get_prompt('Opening {} Depth'.format(opening))
                        add_bottom_deep_shelf_setback = insert.get_prompt("Add Bottom Deep Shelf Setback")
                        is_hang_double = insert.get_prompt("Is Hang Double")
                        prompts = [extra_deep_pard, add_deep_rod_setback, depth, is_hang_double, add_bottom_deep_shelf_setback]

                        if all(prompts):
                            if depth.get_value() >= extra_deep_pard.get_value():
                                add_deep_rod_setback.set_value(depth.get_value() - sn_unit.inch(12))
                                if is_hang_double.get_value():
                                    add_bottom_deep_shelf_setback.set_value(depth.get_value() - sn_unit.inch(12))

                if "IS_BP_DOOR_INSERT" in obj_bp:
                    door_insert = sn_types.Assembly(obj_bp)
                    height_exceeded_ppt = door_insert.get_prompt("Door Height Exceeded")

                    for child in obj_bp.children:
                        if child.get("IS_DOOR"):
                            door_assy = sn_types.Assembly(child)
                            door_style = door_assy.get_prompt("Door Style")
                            if door_style and ("Traviso" in (door_style.get_value())):
                                constraint = [c for c in door_assy.obj_x.constraints if c.type == 'LIMIT_LOCATION']

                                if constraint:
                                    constraint = constraint[0]
                                    bpy.context.view_layer.update()
                                    door_height_exceeded = door_assy.obj_x.location.x > constraint.max_x
                                    height_exceeded_ppt = door_insert.get_prompt("Door Height Exceeded")

                                    if not height_exceeded_ppt:
                                        height_exceeded_ppt = door_insert.add_prompt("Door Height Exceeded", 'CHECKBOX', False)

                                    height_exceeded_ppt.set_value(door_height_exceeded)
                                    self.op_door_height_exceeded[obj_bp.sn_closets.opening_name] = height_exceeded_ppt.get_value()

                                    if height_exceeded_ppt.get_value():
                                        door_insert.get_prompt("Fill Opening").set_value(False)
                                        door_insert.get_prompt("Insert Height").set_value(sn_unit.millimeter(1485.392))
                                        for index, height in enumerate(common_lists.OPENING_HEIGHTS):
                                            if not 1485.392 >= float(height[0]):
                                                self.door_opening_height = common_lists.OPENING_HEIGHTS[index - 1][0]
                                                break

            if obj_props.is_closet_top_bp:
                extend_left = insert.get_prompt("Extend Left Amount")
                extend_right = insert.get_prompt("Extend Right Amount")
                on_left_most_panel = insert.get_prompt("On Left Most Panel")
                on_right_most_panel = insert.get_prompt("On Right Most Panel")

                add_left_filler = self.closet.get_prompt("Add Left Filler")
                add_right_filler = self.closet.get_prompt("Add Right Filler")
                left_wall_filler = self.closet.get_prompt("Left Side Wall Filler")
                right_wall_filler = self.closet.get_prompt("Right Side Wall Filler")
                prompts = [extend_left, extend_right, add_left_filler, add_right_filler,
                           left_wall_filler, right_wall_filler, on_left_most_panel, on_right_most_panel]

                if all(prompts):
                    if add_left_filler.get_value() and on_left_most_panel.get_value():
                        extend_left.set_value(left_wall_filler.get_value())
                    elif self.add_left_filler and add_left_filler.get_value() is False and on_left_most_panel.get_value():
                        extend_left.set_value(sn_unit.inch(0))

                    if add_right_filler.get_value() and on_right_most_panel.get_value():
                        extend_right.set_value(right_wall_filler.get_value())
                    elif self.add_right_filler and add_right_filler.get_value() is False and on_right_most_panel.get_value():
                        extend_right.set_value(sn_unit.inch(0))

            if "IS_BP_TOE_KICK_INSERT" in obj_bp:
                toe_kick_thickness = 0
                if insert.get_prompt('Toe Kick Thickness'):
                    toe_kick_thickness = insert.get_prompt('Toe Kick Thickness').get_value()
                far_left_panel_selected = insert.get_prompt("Far Left Panel Selected")
                if far_left_panel_selected:
                    if far_left_panel_selected.get_value():
                        left_filler = self.closet.get_prompt("Add Left Filler")
                        left_filler_length = self.closet.get_prompt("Left Side Wall Filler")
                        left_filler_setback = self.closet.get_prompt("Left Filler Setback Amount")
                        filler_prompts = [left_filler, left_filler_length, left_filler_setback]
                        if all(filler_prompts):
                            extend_left_amount = insert.get_prompt("Extend Left Amount")
                            if extend_left_amount:
                                if left_filler.get_value():
                                    if left_filler_setback.get_value() == 0:
                                        extend_left_amount.set_value(left_filler_length.get_value() - (toe_kick_thickness/2))

                far_right_panel_selected = insert.get_prompt("Far Right Panel Selected")
                if far_right_panel_selected:
                    if far_right_panel_selected.get_value():
                        right_filler = self.closet.get_prompt("Add Right Filler")
                        right_filler_length = self.closet.get_prompt("Right Side Wall Filler")
                        right_filler_setback = self.closet.get_prompt("Right Filler Setback Amount")
                        filler_prompts = [right_filler, right_filler_length, right_filler_setback]
                        if all(filler_prompts):
                            extend_right_amount = insert.get_prompt("Extend Right Amount")
                            if extend_right_amount:
                                if right_filler.get_value():
                                    if right_filler_setback.get_value() == 0:
                                        extend_right_amount.set_value(right_filler_length.get_value() + (toe_kick_thickness/2))

        has_capping_bottom = self.closet.get_prompt("Has Capping Bottom")

        if has_capping_bottom:
            if capping_bottoms > 0:
                has_capping_bottom.set_value(True)
            else:
                has_capping_bottom.set_value(False)

        print("{} {}: Time --- {} seconds ---".format(
            self.bl_idname, "update_opening_inserts",
            round(time.perf_counter() - start_time, 8)))

    def set_product_defaults(self):
        self.closet.obj_bp.location.x = self.selected_location + self.left_offset
        self.closet.obj_x.location.x = self.default_width - (self.left_offset + self.right_offset)

    def update_placement(self, context):
        left_x = self.closet.get_collision_location('LEFT')
        right_x = self.closet.get_collision_location('RIGHT')
        offsets = self.left_offset + self.right_offset

        if hasattr(self, "default_width"):
            if not self.placement_on_wall == 'FILL':
                self.width = self.default_width
                self.closet.obj_x.location.x = self.width
            else:
                self.width = self.closet.obj_x.location.x

        if self.placement_on_wall == 'SELECTED_POINT':
            self.closet.obj_bp.location.x = self.current_location
        if self.placement_on_wall == 'FILL':
            self.closet.obj_bp.location.x = left_x + self.left_offset
            self.closet.obj_x.location.x = (right_x - left_x - offsets) / self.quantity
        if self.placement_on_wall == 'LEFT':
            self.closet.obj_bp.location.x = left_x + self.left_offset
        if self.placement_on_wall == 'CENTER':
            x_loc = left_x + (right_x - left_x) / 2 - ((self.closet.calc_width() / 2) * self.quantity)
            self.closet.obj_bp.location.x = x_loc
        if self.placement_on_wall == 'RIGHT':
            if self.closet.obj_bp.snap.placement_type == 'CORNER':
                self.closet.obj_bp.rotation_euler.z = math.radians(-90)
            self.closet.obj_bp.location.x = (right_x - self.closet.calc_width()) - self.right_offset

        self.run_calculators(self.closet.obj_bp)

    def update_hang_height(self):
        """Updates the hang height of the closet based on the height of the openings."""

        closet = self.closet
        delta_hang_height = self.hang_height - self.prev_hang_height
        tk_height_ppt = closet.get_prompt("Toe Kick Height")
        tk_height = closet.get_prompt("Toe Kick Height").distance_value
        is_tk_driven = False

        if self.all_floor_mounted_openings():
            new_tk_height = tk_height + delta_hang_height
            tk_height_ppt.set_value(new_tk_height)
            is_tk_driven = True
        else:
            opening_qty = closet.get_prompt("Opening Quantity").get_value()

            for i in range(1, opening_qty + 1):
                is_floor_mounted = closet.get_prompt("Opening " + str(i) + " Floor Mounted").get_value()

                if is_floor_mounted:
                    opening_height = closet.get_prompt("Opening " + str(i) + " Height").distance_value
                    height = opening_height + tk_height
                    is_eq_height = round(height, 2) == round(closet.obj_z.location.z, 2)

                    # If hang height is lowered, and opening height is equal to closet height, adjust TK height
                    if is_eq_height and delta_hang_height < 0:
                        # delta_hang_height will be negative
                        new_tk_height = tk_height + delta_hang_height
                        tk_height_ppt.set_value(new_tk_height)
                        new_height = opening_height + new_tk_height
                        closet.obj_z.location.z = new_height
                        is_tk_driven = True

        if not is_tk_driven:
            closet.obj_z.location.z = self.hang_height

        self.check_tk_height()
        self.update_tk_height()
        self.set_hang_height()
        self.prev_hang_height = self.hang_height

    def all_hanging_openings(self):
        """All openings are hanging"""
        closet = self.closet
        opening_qty = closet.get_prompt("Opening Quantity").get_value()

        for i in range(1, opening_qty + 1):
            is_op_floor_mounted = closet.get_prompt("Opening " + str(i) + " Floor Mounted").get_value()

            if is_op_floor_mounted:
                return False

        return True

    def set_default_width_equal_status(self):
        """Sets the default width equal status of the openings."""
        closet = self.closet
        opening_qty = closet.get_prompt("Opening Quantity").get_value()

        for i in range(1, opening_qty + 1):
            width_ppt_name = "Opening " + str(i) + " Width"
            width_ppt = closet.get_prompt(width_ppt_name)

            if width_ppt:
                self.skip = True
                exec(f'self.op_{str(i)}_width_equal = width_ppt.equal')

    def set_default_widths(self, context):
        """Sets the default widths of the openings."""
        calculator = self.closet.get_calculator('Opening Widths Calculator')

        for i in range(1, 10):
            width = eval(f"calculator.get_calculator_prompt('Opening {str(i)} Width')")

            if width:
                opening_width = round(sn_unit.meter_to_millimeter(width.get_value()), 2)
                self.skip = True
                exec(f'self.op_{str(i)}_width = opening_width/1000')

    def set_default_heights(self, context):
        self.height = self.default_height
        self.init_height_list = False

        for i in range(1, 10):
            opening_height_prompt = self.closet.get_prompt("Opening " + str(i) + " Height")

            if opening_height_prompt:
                opening_height = round(sn_unit.meter_to_millimeter(opening_height_prompt.get_value()), 0)
                panel_heights = get_panel_heights(self, context)

                for index, height in enumerate(panel_heights):
                    if int(height[0]) == int(opening_height):
                        self.skip = True
                        exec('self.opening_' + str(i) + '_height = str(height[0])')

    def convert_to_height(self, number, context):
        panel_heights = get_panel_heights(self,context)
        for index, height in enumerate(panel_heights):
            if not number * 1000 >= float(height[0]):
                return panel_heights[index - 1][0]

    def draw_product_size(self,layout):
        row = layout.row()
        box = row.box()
        col = box.column(align=True)

        row = col.row(align=True)
        if self.object_has_driver(self.closet.obj_x):
            row.label(text='Width: ' + str(sn_unit.meter_to_active_unit(math.fabs(self.closet.obj_x.location.x))))
        elif self.placement_on_wall == 'FILL':
            width = round(sn_unit.meter_to_inch(self.closet.obj_x.location.x), 2)
            label = str(width).replace(".0", "") + '"'
            row.label(text="Overall Width:")
            row.label(text=label)
        else:
            row.label(text='Overall Width:')
            row.prop(self,'width',text="")
        
        row = col.row(align=True)
        if self.object_has_driver(self.closet.obj_z):
            row.label(text='Hang Height: ' + str(sn_unit.meter_to_active_unit(math.fabs(self.closet.obj_z.location.z))))
        else:
            row.label(text='Hang Height:')
            row.prop(self, 'hang_height', text="")

        row = col.row(align=True)
        row.label(text='Set Pard Size:')
        row.prop(self, 'height', text="")

    def object_has_driver(self,obj):
        if obj.animation_data:
            if len(obj.animation_data.drivers) > 0:
                return True

    def draw_common_prompts(self, layout):
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        row.label(text="Left End Condition:")
        row.prop(self, 'left_end_condition', text="")
        row = col.row(align=True)
        row.label(text="Right End Condition:")
        row.prop(self, 'right_end_condition', text="")

        if self.left_end_condition == 'OFF' or self.right_end_condition == 'OFF':
            shelf_gap = self.closet.get_prompt("Shelf Gap")
            row = col.row(align=True)
            row.label(text="Shelf Gap:")
            row.prop(shelf_gap, 'distance_value', text="")

    def get_number_of_equal_widths(self):
        number_of_equal_widths = 0
        
        for i in range(1,10):
            calculator = self.closet.get_calculator('Opening Widths Calculator')
            width = eval("calculator.get_calculator_prompt('Opening {} Width')".format(str(i)))

            if width:
                number_of_equal_widths += 1 if width.equal else 0
            else:
                break
            
        return number_of_equal_widths

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

    def set_panel_material(self, assembly):
        cab_mat_props = bpy.context.scene.closet_materials
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

        self.set_material(assembly)


def register():
    bpy.utils.register_class(PROMPTS_Opening_Starter)


def unregister():
    bpy.utils.unregister_class(PROMPTS_Opening_Starter)

