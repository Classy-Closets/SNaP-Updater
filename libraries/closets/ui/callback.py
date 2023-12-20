import bpy

from snap import sn_utils
from snap import sn_types
from snap import sn_unit


active_operator = None


def get_active_operator(context):
    global active_operator

    if active_operator:
        return active_operator


def update_closet_height(self, context):
    ''' EVENT changes height for all closet openings
    '''

    if self.init_height_list:
        return

    self.opening_1_height = self.height
    self.opening_2_height = self.height
    self.opening_3_height = self.height
    self.opening_4_height = self.height
    self.opening_5_height = self.height
    self.opening_6_height = self.height
    self.opening_7_height = self.height
    self.opening_8_height = self.height
    self.opening_9_height = self.height
    obj_product_bp = sn_utils.get_closet_bp(context.active_object)
    product = sn_types.Assembly(obj_product_bp)
    product.run_all_calculators()

    for i in range(1, 10):
        opening_height = product.get_prompt("Opening " + str(i) + " Height")
        if opening_height:
            opening_height.set_value(sn_unit.millimeter(float(self.height)))

    product.run_all_calculators()


def update_hang_height(self, context):
    global active_operator
    if active_operator:
        operator = active_operator

    if operator:
        if not operator.skip:
            operator.update_hang_height()
            operator.update_flat_molding_heights()
            operator.update_top_location()
            operator.update_countertop()

        operator.skip = False


def update_top_assemblies(self, context):
    global active_operator
    if active_operator:
        operator = active_operator

    if operator:
        operator.update_flat_molding_heights()
        operator.update_hang_height()
        operator.check_hang_height()
        operator.update_top_location()
        operator.update_countertop()


def update_placement(self, context):
    global active_operator
    if active_operator:
        operator = active_operator

    if operator:
        if operator.initialized:
            operator.update_placement(context)


def update_overall_width(self, context):
    global active_operator

    if active_operator:
        operator = active_operator

    if operator:
        if operator.initialized:
            operator.closet.obj_x.location.x = operator.width
            operator.run_calculators(operator.closet.obj_bp)
            operator.default_width = operator.closet.obj_x.location.x


def update_opening_equal_status(self, context):
    operator = get_active_operator(context)

    if operator and not operator.skip:
        operator.update_opening_equal_status()

    operator.skip = False


def update_opening_widths(self, context):
    operator = get_active_operator(context)

    if operator and not operator.skip:
        operator.update_opening_widths()

    operator.skip = False


def update_opening_heights(self, context):
    global active_operator
    if active_operator:
        operator = active_operator

    if operator:
        if not operator.skip:
            operator.update_opening_heights()

        operator.skip = False


def update_toe_kick_height(self, context):
    global active_operator
    if active_operator:
        operator = active_operator

    if operator:
        if operator.initialized:
            operator.closet.get_prompt("Toe Kick Height").set_value(operator.tk_height)
            operator.check_tk_height()
            operator.update_tk_height()


def update_end_conditions(self, context):
    global active_operator
    if active_operator:
        operator = active_operator

    if operator:
        if operator.initialized:
            if hasattr(operator, "left_end_condition") and hasattr(operator, "right_end_condition"):
                operator.update_end_conditions(context)


def update_fillers(self, context):
    operator = get_active_operator(context)

    if operator:
        if operator.initialized:
            add_left_filler = operator.closet.get_prompt("Add Left Filler")
            add_right_filler = operator.closet.get_prompt("Add Right Filler")
            add_left_filler.set_value(self.add_left_filler)
            add_right_filler.set_value(self.add_right_filler)
            operator.reset_fillers()
            operator.run_calculators(operator.closet.obj_bp)


def update_dog_ear(self, context):
    global active_operator
    if active_operator:
        operator = active_operator

    if operator:
        operator.check_front_angle_depth()


def update_blind_panels(self, context):
    global active_operator
    if active_operator:
        operator = active_operator

    if operator:
        operator.update_blind_corners()


def update_filler_amt(self, context):
    global active_operator
    if active_operator:
        operator = active_operator

    if operator:
        if operator.initialized:
            operator.closet.get_prompt("Left Side Wall Filler").set_value(operator.left_filler_amt)
            operator.closet.get_prompt("Right Side Wall Filler").set_value(operator.right_filler_amt)
            operator.run_calculators(operator.closet.obj_bp)


def update_op_1_floor_mount(self, context):
    op = get_active_operator(context)
    if op and op.initialized:
        op.closet.get_prompt("Opening 1 Floor Mounted").set_value(self.op_1_floor_mount)
        op.set_hang_height()
        op.check_hang_height()
        update_top_assemblies(op, context)


def update_op_2_floor_mount(self, context):
    op = get_active_operator(context)
    if op and op.initialized:
        op.closet.get_prompt("Opening 2 Floor Mounted").set_value(self.op_2_floor_mount)
        op.set_hang_height()
        op.check_hang_height()
        update_top_assemblies(op, context)


def update_op_3_floor_mount(self, context):
    op = get_active_operator(context)
    if op and op.initialized:
        op.closet.get_prompt("Opening 3 Floor Mounted").set_value(self.op_3_floor_mount)
        op.set_hang_height()
        op.check_hang_height()
        update_top_assemblies(op, context)


def update_op_4_floor_mount(self, context):
    op = get_active_operator(context)
    if op and op.initialized:
        op.closet.get_prompt("Opening 4 Floor Mounted").set_value(self.op_4_floor_mount)
        op.set_hang_height()
        op.check_hang_height()
        update_top_assemblies(op, context)


def update_op_5_floor_mount(self, context):
    op = get_active_operator(context)
    if op and op.initialized:
        op.closet.get_prompt("Opening 5 Floor Mounted").set_value(self.op_5_floor_mount)
        op.set_hang_height()
        op.check_hang_height()
        update_top_assemblies(op, context)


def update_op_6_floor_mount(self, context):
    op = get_active_operator(context)
    if op and op.initialized:
        op.closet.get_prompt("Opening 6 Floor Mounted").set_value(self.op_6_floor_mount)
        op.set_hang_height()
        op.check_hang_height()
        update_top_assemblies(op, context)


def update_op_7_floor_mount(self, context):
    op = get_active_operator(context)
    if op and op.initialized:
        op.closet.get_prompt("Opening 7 Floor Mounted").set_value(self.op_7_floor_mount)
        op.set_hang_height()
        op.check_hang_height()
        update_top_assemblies(op, context)


def update_op_8_floor_mount(self, context):
    op = get_active_operator(context)
    if op and op.initialized:
        op.closet.get_prompt("Opening 8 Floor Mounted").set_value(self.op_8_floor_mount)
        op.set_hang_height()
        op.check_hang_height()
        update_top_assemblies(op, context)


def update_op_9_floor_mount(self, context):
    op = get_active_operator(context)
    if op and op.initialized:
        op.closet.get_prompt("Opening 9 Floor Mounted").set_value(self.op_9_floor_mount)
        op.set_hang_height()
        op.check_hang_height()
        update_top_assemblies(op, context)


def update_op_1_full_back(self, context):
    op = get_active_operator(context)
    if op:
        op.closet.get_prompt("Add Full Back 1").set_value(self.op_1_full_back)
        op.update_backing(context)


def update_op_2_full_back(self, context):
    op = get_active_operator(context)
    if op:
        op.closet.get_prompt("Add Full Back 2").set_value(self.op_2_full_back)
        op.update_backing(context)


def update_op_3_full_back(self, context):
    op = get_active_operator(context)
    if op:
        op.closet.get_prompt("Add Full Back 3").set_value(self.op_3_full_back)
        op.update_backing(context)


def update_op_4_full_back(self, context):
    op = get_active_operator(context)
    if op:
        op.closet.get_prompt("Add Full Back 4").set_value(self.op_4_full_back)
        op.update_backing(context)


def update_op_5_full_back(self, context):
    op = get_active_operator(context)
    if op:
        op.closet.get_prompt("Add Full Back 5").set_value(self.op_5_full_back)
        op.update_backing(context)


def update_op_6_full_back(self, context):
    op = get_active_operator(context)
    if op:
        op.closet.get_prompt("Add Full Back 6").set_value(self.op_6_full_back)
        op.update_backing(context)


def update_op_7_full_back(self, context):
    op = get_active_operator(context)
    if op:
        op.closet.get_prompt("Add Full Back 7").set_value(self.op_7_full_back)
        op.update_backing(context)


def update_op_8_full_back(self, context):
    op = get_active_operator(context)
    if op:
        op.closet.get_prompt("Add Full Back 8").set_value(self.op_8_full_back)
        op.update_backing(context)


def update_op_9_full_back(self, context):
    op = get_active_operator(context)
    if op:
        op.closet.get_prompt("Add Full Back 9").set_value(self.op_9_full_back)
        op.update_backing(context)


def update_backing_throughout(self, context):
    op = get_active_operator(context)
    if op:
        if op.initialized:
            op.closet.get_prompt("Add Backing Throughout").set_value(self.add_backing_throughout)
            op.update_backing(context)
