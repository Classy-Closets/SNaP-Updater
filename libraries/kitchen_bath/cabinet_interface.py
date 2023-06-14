from ctypes.wintypes import tagMSG
import bpy
from bpy.props import (
    StringProperty,
    FloatProperty,
    EnumProperty
    )


import math
import snap
from snap import sn_types, sn_unit, sn_utils
from snap.libraries.kitchen_bath.carcass_simple import Inside_Corner_Carcass, Standard_Carcass, Island_Carcass
from snap.libraries.kitchen_bath.cabinets import Standard
from . import cabinet_properties
from .frameless_exteriors import Doors, Vertical_Drawers, Horizontal_Drawers
from snap.libraries.closets.ui.closet_prompts_ui import get_panel_heights
from snap.libraries.closets.common.common_lists import FRONT_HEIGHTS

ISLAND_FRONT_ROW = 0
ISLAND_BACK_ROW = 1
ISLAND_BASE_CARCASS = 0
ISLAND_APPLIANCE_CARCASS = 1
ISLAND_SINK_CARCASS = 2

def draw_carcass_options(self, carcass,layout):
    left_fin_end = carcass.get_prompt("Left Fin End")
    right_fin_end = carcass.get_prompt("Right Fin End")
    remove_left_side = carcass.get_prompt('Remove Left Side')
    remove_right_side = carcass.get_prompt('Remove Right Side')
    left_wall_filler = carcass.get_prompt("Left Side Wall Filler")
    right_wall_filler = carcass.get_prompt("Right Side Wall Filler")
    
    valance_height_top = carcass.get_prompt("Valance Height Top")
    toe_kick_height = carcass.get_prompt("Toe Kick Height")
    remove_bottom = carcass.get_prompt("Remove Bottom")
    remove_back = carcass.get_prompt("Remove Back")
    use_thick_back = carcass.get_prompt("Use Thick Back")
    use_nailers = carcass.get_prompt("Use Nailers")
    cabinet_depth_left = carcass.get_prompt("Cabinet Depth Left")
    cabinet_depth_right = carcass.get_prompt("Cabinet Depth Right")

    product = sn_types.Assembly(carcass.obj_bp.parent)
    blind_panel_width = product.get_prompt('Blind Panel Width')
    blind_panel_reveal = product.get_prompt('Blind Panel Reveal')

    carcass_type = carcass.obj_bp.get('CARCASS_TYPE')

    # SIDE OPTIONS:
    if carcass_type and carcass_type != "Island":
        if left_wall_filler and right_wall_filler:
            col = layout.column(align=True)
            col.label(text="Side Options:")
            
            row = col.row()
            row.prop(left_wall_filler,'distance_value',text="Left Filler Amount")
            row.prop(right_wall_filler,'distance_value',text="Right Filler Amount")

    # BLIND CORNER OPTIONS
    if blind_panel_width:
        col = layout.column(align=True)
        col.label(text="Blind Panel Options:")
        row = col.row()
        row.prop(blind_panel_width,'distance_value',text="Blind Panel Width")
        row.label(text=" ")
        # row.prop(blind_panel_reveal,'distance_value',text="Blind Panel Reveal")
    
    # CARCASS OPTIONS:
    col = layout.column(align=True)
    if carcass_type and carcass_type != 'Island':
        col.label(text="Carcass Options:")
    row = col.row()
    
    if remove_left_side and carcass_type and carcass_type == 'Appliance':
        row.prop(remove_left_side,'checkbox_value',text="Remove Left Side")
        row.prop(remove_right_side,'checkbox_value',text="Remove Right Side")

    if carcass_type and carcass_type not in ['Appliance','Island']:
        if use_thick_back:
            row.prop(use_thick_back,'checkbox_value',text="Use Thick Back")
        if remove_bottom:
            row.prop(remove_bottom,'checkbox_value',text="Remove Bottom")
        if remove_back:
            row.prop(remove_back,'checkbox_value',text="Remove Back")
        if cabinet_depth_left:
            row = col.row()
            row.prop(cabinet_depth_left,'distance_value',text="Cabinet Depth Left")
            row.prop(cabinet_depth_right,'distance_value',text="Cabinet Depth Right")
        
    # TOE KICK OPTIONS
    if carcass_type and carcass_type != "Appliance":
        if carcass_type != "Island" or (carcass_type == "Island" and get_appliance_subtype_count(self) < len(self.island_openings)):
            if toe_kick_height:
                col = layout.column(align=True)
                toe_kick_setback = carcass.get_prompt("Toe Kick Setback")
                left_toe_kick_filler = carcass.get_prompt("Left Toe Kick Filler")
                right_toe_kick_filler = carcass.get_prompt("Right Toe Kick Filler")
                col.label(text="Toe Kick Options:")
                row = col.row()
                row.prop(toe_kick_height,'distance_value',text="Toe Kick Height")
                row.prop(toe_kick_setback,'distance_value',text="Toe Kick Setback")
                row = col.row()
                if left_toe_kick_filler:
                    row.prop(left_toe_kick_filler,'distance_value',text="Extend Left Amount")
                    row.prop(right_toe_kick_filler,'distance_value',text="Extend Right Amount")
        
    # VALANCE OPTIONS
    if valance_height_top:
        r_full_height = carcass.get_prompt("Right Side Full Height")
        l_full_height = carcass.get_prompt("Left Side Full Height")
        valance_each_unit = carcass.get_prompt("Valance Each Unit")
        
        col = layout.column(align=True)
        col.label(text="Valance Options:")
        door_valance_top = carcass.get_prompt("Door Valance Top")
        row = col.row()
        row.prop(valance_height_top,'distance_value',text="Valance Height Top")
        row.prop(door_valance_top,'checkbox_value',text="Door Valance Top")

        valance_height_bottom = carcass.get_prompt("Valance Height Bottom")
        
        if valance_height_bottom:
            door_valance_bottom = carcass.get_prompt("Door Valance Bottom")
            row = col.row()
            row.prop(valance_height_bottom,'distance_value',text="Valance Height Bottom")
            row.prop(door_valance_bottom,'checkbox_value',text="Door Valance Bottom")
        
        row = col.row()
        row.prop(l_full_height,'checkbox_value',text="Left Side Full Height")
        row.prop(r_full_height,'checkbox_value',text="Right Side Full Height")
        
        row = col.row()
        row.prop(valance_each_unit,'checkbox_value',text="Add Valance For Each Unit")

def draw_island_options(self, island_row, carcass, layout):
    col = layout.column(align=True)
    is_Double_Sided = carcass.get_prompt("Double Sided").get_value()
    
    if is_Double_Sided:
        if island_row == ISLAND_FRONT_ROW:
            col.label(text="Front Sections:")
        elif island_row == ISLAND_BACK_ROW:
            col.label(text="Back Sections:")
    else:
        col.label(text="Island Sections:")

    if island_row == ISLAND_FRONT_ROW:
        start_nbr = 0
        if self.show_double_sided:
            end_nbr = int(len(self.island_openings)/2) - 1
        else:
            end_nbr = int(len(self.island_openings)) - 1
        step_nbr = 1
    elif island_row == ISLAND_BACK_ROW:
        end_nbr = int(len(self.island_openings)/2) - 2
        start_nbr = int(len(self.island_openings)) - 1
        step_nbr = -1

    for index in range(start_nbr,end_nbr+1,step_nbr):
        child = self.island_openings[index]

        row = col.row()

        if child.get("ISLAND_ROW_NBR") == 2 and is_Double_Sided:
            label = str(get_back_opening_from_section(self, child.get("OPENING_NBR") - 1) + 1)
        else:
            label = str(child.get("OPENING_NBR"))
        opening_nbr = child.get("OPENING_NBR")
        opening_ppt = carcass.get_prompt("Opening " + str(opening_nbr) + " Width") 

        calculator = carcass.get_calculator("Front Row Widths Calculator")
        if calculator.get_calculator_prompt("Opening " + str(opening_nbr) + " Width"):
            draw_hole_size_width(opening_nbr, row, opening_ppt, calculator, "Section", "Section " + label)
        else:
            calculator = carcass.get_calculator("Back Row Widths Calculator")
            draw_hole_size_width(opening_nbr, row, opening_ppt, calculator, "Section", "Section " + label)
        
        has_children = False
        for obj_bp in child.parent.children:
            if obj_bp.get('PLACEMENT_TYPE') or obj_bp.get('IS_BP_SPLITTER'):
                if obj_bp.get("OPENING_NBR") == child.get("OPENING_NBR"):
                    has_children = True
        if not has_children:
            for obj_bp in child.children:
                if obj_bp.get('PLACEMENT_TYPE') or obj_bp.get('IS_BP_SPLITTER'):
                    if obj_bp.get("OPENING_NBR") == child.get("OPENING_NBR"):
                        has_children = True

        if has_children:
            subtype_val = eval('self.carcass_subtype_' + str(opening_nbr))
            if subtype_val == "0":
                subtype_label = "  Base"
            elif subtype_val == "1":
                subtype_label = "  Appliance"
            elif subtype_val == "2": 
                subtype_label = "  Sink"

            row.label(text=subtype_label)
        else:
            row.prop(self, 'carcass_subtype_' + str(opening_nbr), text="")
    
    if island_row == ISLAND_BACK_ROW:
        chase_dpeth_ppt = carcass.get_prompt("Chase Depth")
        if chase_dpeth_ppt:
            row = layout.row(align=True)
            col = row.column()
            
            col.label(text=" ")
            col = row.column()
            col.prop(chase_dpeth_ppt, 'distance_value',text="Chase Depth")

def get_back_opening_from_section(self, section_index):
    section_nbr = section_index + 1
    start_nbr = int(len(self.island_openings)/2)+1
    end_nbr = int(len(self.island_openings))

    offset = start_nbr - section_nbr 
    opening_index = end_nbr - abs(offset) - 1

    return opening_index

def get_section_from_back_opening(self, opening_nbr):
    start_nbr = int(len(self.island_openings)/2)+1
    end_nbr = int(len(self.island_openings))

    offset = start_nbr - opening_nbr 
    section_nbr = end_nbr - abs(offset) 

    return section_nbr

def draw_countertop_options(ctop,product,layout):
    Add_Backsplash = ctop.get_prompt("Add Backsplash")
    Add_Left_Backsplash = ctop.get_prompt("Add Left Backsplash")
    Add_Right_Backsplash = ctop.get_prompt("Add Right Backsplash")
    Add_Left_Rear_Backsplash = ctop.get_prompt("Add Left Rear Backsplash")
    Add_Right_Rear_Backsplash = ctop.get_prompt("Add Right Rear Backsplash")
    Side_Splash_Setback = ctop.get_prompt('Side Splash Setback')
    Splash_Height = ctop.get_prompt('Splash Height')
    Add_Left_Waterfall = ctop.get_prompt("Add Left Waterfall")
    Add_Right_Waterfall = ctop.get_prompt("Add Right Waterfall")

    Countertop_Overhang_Front = product.get_prompt("Countertop Overhang Front")
    Countertop_Overhang_Right_Front = product.get_prompt("Countertop Overhang Right Front")
    Countertop_Overhang_Left_Front = product.get_prompt("Countertop Overhang Left Front")
    Countertop_Overhang_Back = product.get_prompt("Countertop Overhang Back")
    Countertop_Overhang_Right_Back = product.get_prompt("Countertop Overhang Right Back")
    Countertop_Overhang_Left_Back = product.get_prompt("Countertop Overhang Left Back")
    Countertop_Overhang_Left = product.get_prompt("Countertop Overhang Left")
    Countertop_Overhang_Right = product.get_prompt("Countertop Overhang Right")
  
    box = layout.box()
    # col = box.column(align=True)
    # col.label(text="Countertop Options:")

    if Countertop_Overhang_Left:
        col = box.column(align=False)
        col.label(text="Countertop Overhang:")

        if Countertop_Overhang_Front:
            row_1 = col.row(align=True)
            row_1.prop(Countertop_Overhang_Front,'distance_value',text="Front")
            row_1.prop(Countertop_Overhang_Back,'distance_value',text="Back")

        if Countertop_Overhang_Right_Front:
            row_1 = col.row(align=True)
            row_1.prop(Countertop_Overhang_Left_Front,'distance_value',text="Front Left")
            row_1.prop(Countertop_Overhang_Right_Front,'distance_value',text="Front Right")
            
            row_2 = col.row(align=True)
            row_2.prop(Countertop_Overhang_Left_Back,'distance_value',text="Back Left")
            row_2.prop(Countertop_Overhang_Right_Back,'distance_value',text="Back Right")

        row_3 = col.row(align=True)
        if Add_Left_Waterfall and Add_Left_Waterfall.get_value():
            row_3.label(text=" ")
        else:
            row_3.prop(Countertop_Overhang_Left,'distance_value',text="Left")
        if Add_Right_Waterfall and Add_Right_Waterfall.get_value():
            row_3.label(text=" ")
        else:
            row_3.prop(Countertop_Overhang_Right,'distance_value',text="Right")

    if Add_Backsplash or Add_Left_Backsplash or Add_Right_Backsplash:
        col = box.column(align=False)
        col.label(text="Countertop Backsplash:")

        if Add_Backsplash:
            row = col.row(align=True)
            row.prop(Add_Backsplash,'checkbox_value',text="")
            row.label(text="Add Back Splash")
        
        if Add_Left_Backsplash:
            row = col.row(align=True)
            row.prop(Add_Left_Backsplash,'checkbox_value',text="")            
            row.label(text="Add Left Splash")
            row.prop(Add_Right_Backsplash,'checkbox_value',text="")            
            row.label(text="Add Right Splash")
        
        if Add_Left_Rear_Backsplash:
            row = col.row(align=True)
            row.prop(Add_Left_Rear_Backsplash,'checkbox_value',text="")            
            row.label(text="Add Left Rear Splash")
            row.prop(Add_Right_Rear_Backsplash,'checkbox_value',text="")   
            row.label(text="Add Right Rear Splash")

        row_1 = col.row(align=True)
        row_1.prop(Splash_Height,'distance_value',text="Height")
        if Add_Left_Backsplash and Add_Left_Backsplash.get_value() or Add_Right_Backsplash and Add_Right_Backsplash.get_value():
            row_1.prop(Side_Splash_Setback,'distance_value',text="Setback")
        else:
            row_1.label(text="")


    if Add_Left_Waterfall:
        col = box.column(align=False)
        col.label(text="Countertop Waterfall:")
        row = col.row(align=True)
        row.prop(Add_Left_Waterfall,'checkbox_value',text="")            
        row.label(text="Add Left Waterfall")
        row.prop(Add_Right_Waterfall,'checkbox_value',text="")            
        row.label(text="Add Right Waterfall")

def draw_door_options(self,door,layout):
    open_door = door.get_prompt('Open Door')
    door_swing = door.get_prompt('Door Swing')
    inset_front = door.get_prompt('Inset Front')
    
    half_overlay_top = door.get_prompt('Half Overlay Top')
    half_overlay_bottom = door.get_prompt('Half Overlay Bottom')
    half_overlay_left = door.get_prompt('Half Overlay Left')
    half_overlay_right = door.get_prompt('Half Overlay Right')
    
    row = layout.row()
    row.label(text="  Door Options:")
    
    if open_door:
        if door_swing:
            open_label = "Open Door"
        else:
            open_label = "Open Doors"
        row.prop(open_door, 'factor_value', text=open_label)
        
    if door_swing:
        row = layout.row()
        row.label(text="     Door Swing:")
        if self.product.obj_bp.get("IS_BP_ISLAND"):
            opening_bp = self.get_island_opening(door.obj_bp)
            opening_nbr = opening_bp.get('OPENING_NBR')
        else:
            opening_nbr = 1
        exec('self.door_swing_' + str(opening_nbr) + ' = str(door_swing.get_value())')
        row.prop(self, 'door_swing_' + str(opening_nbr), text="")

    if inset_front:
        if not inset_front.get_value():
            row = layout.row()
            row.label(text="     Half Overlays:  ")
            if half_overlay_top:
                row.prop(half_overlay_top,'checkbox_value',text="Top")
                row.prop(half_overlay_bottom,'checkbox_value',text="Bottom")
                row.prop(half_overlay_left,'checkbox_value',text="Left")
                row.prop(half_overlay_right,'checkbox_value',text="Right")

def draw_drawer_options(self, drawers,layout):
    open_drawers = drawers.get_prompt("Open Drawers")
    drawer_qty = drawers.get_prompt("Drawer Quantity")
    half_overlay_top = drawers.get_prompt("Half Overlay Top")
    half_overlay_bottom = drawers.get_prompt("Half Overlay Bottom")
    half_overlay_left = drawers.get_prompt("Half Overlay Left")
    half_overlay_right = drawers.get_prompt("Half Overlay Right")
    add_drawer_boxes_ppt = drawers.get_prompt("Add Drawer Boxes")
    
    row = layout.row()
    row.label(text="  Drawer Options:")

    open_label = "Open Drawers"

    if drawer_qty:
        if drawer_qty.get_value() == 1:
            open_label = "Open Drawer"
    if add_drawer_boxes_ppt:
        row.prop(add_drawer_boxes_ppt, "checkbox_value", text=open_label)
    elif open_drawers:
        row.prop(open_drawers, "factor_value", text=open_label)

    if half_overlay_top:
        col = layout.column(align=True)
        row = col.row()
        row.label(text="     Half Overlays:  ")
        row.prop(half_overlay_top,'checkbox_value',text="Top")
        row.prop(half_overlay_bottom,'checkbox_value',text="Bottom")
        row.prop(half_overlay_left,'checkbox_value',text="Left")
        row.prop(half_overlay_right,'checkbox_value',text="Right")
    
    calculator = drawers.get_calculator('Vertical Drawers Calculator')
    df_2_height = None
    if drawers.obj_bp.get('VERTICAL_DRAWERS'):
        df_2_height = calculator.get_calculator_prompt('Drawer Front 2 Height')
    drawer_front_heights = get_drawer_front_heights()

    if df_2_height:
        for i in range(1,10):
            drawer_height = calculator.get_calculator_prompt("Drawer Front " + str(i) + " Height")
            if drawer_height:
                self.active_obj = drawers.obj_bp
                draw_hole_size_height(i, layout, drawer_height, drawer_front_heights, calculator, type="Drawer Front")
            else:
                break

def draw_appliance_options(appliance,layout):
    row = layout.row()

    label = appliance.obj_bp.name
    if label.find(".") > 0:
        label = label[:-4]

    row.label(text="Opening 1 - " + label, icon='RADIOBUT_ON')

def draw_interior_options(assembly,layout):


    adj_shelf_qty = assembly.get_prompt("Adj Shelf Qty")
    fix_shelf_qty = assembly.get_prompt("Fixed Shelf Qty")
    shelf_qty = assembly.get_prompt("Shelf Qty")
    shelf_setback = assembly.get_prompt("Shelf Setback")
    adj_shelf_setback = assembly.get_prompt("Adj Shelf Setback")
    fix_shelf_setback = assembly.get_prompt("Fixed Shelf Setback")
    div_qty_per_row = assembly.get_prompt("Divider Qty Per Row")
    division_qty = assembly.get_prompt("Division Qty")
    adj_shelf_rows = assembly.get_prompt("Adj Shelf Rows")
    fixed_shelf_rows = assembly.get_prompt("Fixed Shelf Rows")
    
    row = layout.row()
    row.label(text="  Interior Options:")
    
    row = layout.row()
    split = row.split(factor=.025)
    colA = split.column()
    colB = split.column()

    split = colB.split(factor=0.5)
    col1 = split.column()
    col1.alignment = 'RIGHT'
    col2 = split.column()
    col2.alignment = 'RIGHT'


    if shelf_qty:
        # row = layout.row()
        # row.prop(shelf_qty, 'quantity_value', text="")
        col1.prop(shelf_qty, 'quantity_value', text="Shelf Quantity")

    
    if shelf_setback:
        # row.prop(shelf_setback,'distance_value', text="")
        col2.prop(shelf_setback, 'distance_value', text="Shelf Setback")

    if adj_shelf_qty:
        # row = layout.row()
        # adj_shelf_qty.draw(row,allow_edit=False)
        col1.prop(adj_shelf_qty, 'quantity_value', text="Adj Shelf Quantity")

    if adj_shelf_setback:
        # adj_shelf_setback.draw(row,allow_edit=False)
        col2.prop(adj_shelf_setback, 'distance_value', text="Shelf Setback")
        
    if fix_shelf_qty:
        row = layout.row()
        fix_shelf_qty.draw(row,allow_edit=False)

    if fix_shelf_setback:
        fix_shelf_setback.draw(row,allow_edit=False)
        
    if div_qty_per_row:
        row = layout.row()
        div_qty_per_row.draw(row,allow_edit=False)

    if division_qty:
        row = layout.row()
        division_qty.draw(row,allow_edit=False)

    if adj_shelf_rows:
        row = layout.row()
        adj_shelf_rows.draw(row,allow_edit=False)

    if fixed_shelf_rows:
        row = layout.row()
        fixed_shelf_rows.draw(row,allow_edit=False)

def draw_hole_size_height(i, box, calc_ppt, heights, calculator, type="Opening", child_name=""):
    row = box.row()
    if type == "Opening":
        row.label(text=type + " " + str(i) + " - " + child_name, icon='RADIOBUT_ON')
    else:
        row.label(text="     " + type + " " + str(i) + ": " + child_name)
    
    if not calc_ppt.equal:
        row.prop(calc_ppt, 'equal', text="")
    else:
        if get_number_of_equal_heights(calculator, type) != 1:
            row.prop(calc_ppt, 'equal', text="")
        else:
            row.label(text="", icon='BLANK1')
    
    label = "No Even Hole Size"
    for height in heights:
        full_height = calc_ppt.distance_value

        if type == "Opening":
            full_height_mm = sn_unit.meter_to_millimeter(full_height + sn_unit.inch(0.75))
        elif type == "Drawer Front":
            full_height_mm = sn_unit.meter_to_millimeter(full_height) 

        if int(height[0]) == round(full_height_mm):
            label = height[1]
            break
   
    if calc_ppt.equal:
        row.label(text=label)
    else:
        # the below will collide calculator prompts if more than 1 drawer stack or splitter in same cabinet or island section opening..
        row.menu("SNAP_MT_{}_{}_Heights".format(type.replace(" ","_"), str(i)), text=label)

def draw_hole_size_width(i, box, calc_ppt, calculator, type="Opening", child_name=""):
    row = box.row()

    if type == "Section":
        wm = bpy.context.window_manager.snap
        kb_icon = wm.libraries["Kitchen Bath Library"].icon
        if child_name != "":
            section_label = child_name #+ " " + str(i)
        else:
            section_label = "Island Section " + str(i)
        row.label(text=section_label, icon_value=snap.snap_icons[kb_icon].icon_id)
    elif type == "Opening":
        row.label(text=type + " " + str(i) + " - " + child_name, icon='RADIOBUT_ON')
    else:
        row.label(text="     " + type + " " + str(i) + ": " + child_name)
    
    if not calc_ppt.equal:
        row.prop(calc_ppt, 'equal', text="")
    else:
        equal_openings =  get_number_of_equal_widths(calculator)
        if equal_openings != 1 and len(calculator.prompts) > 1:
            row.prop(calc_ppt, 'equal', text="")
        else:
            row.label(text="", icon='BLANK1')
    
    width = round(sn_unit.meter_to_inch(calc_ppt.distance_value), 2)
    label = str(width).replace(".0", "") + '" Width'
    if len(calculator.prompts) > 1:
        if calc_ppt.equal:
            row.label(text=label)
        else:
            row.prop(calc_ppt, 'distance_value', text="Width")

def draw_splitter_options(assembly,layout):
    opening_heights = get_opening_heights()
    inserts = []

    for child in sn_utils.get_assembly_bp_list(assembly.obj_bp, []):
         if child.get('IS_BP_ASSEMBLY') and not child.get("IS_BP_SHELVES") and child.snap.type_group == 'INSERT':
            inserts.append(child)

    if assembly.get_prompt("Opening 1 Height"):
        name = "Height"
    else:
        name = "Width"
        
    box = layout.box()
    
    for i in range(1,10):
        opening = assembly.get_prompt("Opening " + str(i) + " " + name)
        calculator = assembly.get_calculator('Opening Heights Calculator')
        child_label = ""
        if opening:
            if i <= len(inserts):
                child_label = " (" + inserts[i-1].name.replace(".001","") + ")"
            draw_hole_size_height(i, box, opening, opening_heights, calculator, "Opening", child_label)
        else:
            break

def draw_insert_options(self,assembly,layout):
    opening_heights = get_opening_heights()
    inserts = []
    interiors = []
    exteriors = []
    root_bp = None
    is_Splitter = assembly.obj_bp.get("IS_BP_SPLITTER")
    is_Opening = assembly.obj_bp.get("IS_BP_OPENING")
    is_Island = assembly.obj_bp.get("ISLAND_ROW_NBR")
    exterior = None
    interior = None

    if is_Splitter:
        assembly_list = sn_utils.get_assembly_bp_list(assembly.obj_bp, [])
    elif is_Island:
        assembly_list = []
        for obj_bp in assembly.obj_bp.parent.children:
            if obj_bp.get('IS_BP_ASSEMBLY'):
                assembly_list.append(obj_bp)
        for obj_bp in assembly.obj_bp.children:
            if obj_bp.get('IS_BP_ASSEMBLY'):
                assembly_list.append(obj_bp)
    else:
        assembly_list = sn_utils.get_assembly_bp_list(assembly.obj_bp.parent, [])

    for child in assembly_list:
        if child.get('PLACEMENT_TYPE'):
            if is_Splitter or child.get("OPENING_NBR") == assembly.obj_bp.get("OPENING_NBR"):
                if child.get('PLACEMENT_TYPE') == 'Exterior':
                    exteriors.append(child)
                elif child.get('PLACEMENT_TYPE') == "Interior":
                    interiors.append(child)
                inserts.append(child)

    if is_Splitter:
        if assembly.get_prompt("Opening 1 Height"):
            name = "Height"
        else:
            name = "Width"

        for i in range(1,10):
            calculator = assembly.get_calculator("Opening " + name + "s Calculator")
            opening_ppt = calculator.get_calculator_prompt("Opening " + str(i) + " " + name) 
            if opening_ppt:
                box = layout.box()    

                label = "Empty"
                for insert in inserts:
                    if insert.get('OPENING_NBR'):
                        if insert.get('OPENING_NBR') == i:
                            if insert.get('PLACEMENT_TYPE') == "Exterior":
                                label = insert.name
                            elif insert.get('PLACEMENT_TYPE') == "Interior" and label == "Empty":
                                label = insert.name
                if label.find(".") > 0:
                    label = label[:-4]
                
                draw_hole_size_height(i, box, opening_ppt, opening_heights, calculator, "Opening", label)

                for insert in exteriors:
                    if insert.get('OPENING_NBR') == i:
                        exterior = sn_types.Assembly(insert)
                        if exterior.obj_bp.get('IS_BP_DOOR_INSERT'):
                            draw_door_options(self, exterior, box)
                        elif exterior.obj_bp.get('IS_DRAWERS_BP'):
                            draw_drawer_options(self, exterior, box)

                for insert in interiors:
                    if insert.get('OPENING_NBR') == i:
                        interior = sn_types.Assembly(insert)
                        draw_interior_options(interior, box)
            else:
                break
    else:
        box = layout.box()    
        for insert in exteriors:
            exterior = sn_types.Assembly(insert)
            if exterior.obj_bp.get('IS_BP_DOOR_INSERT'):
                draw_door_options(self, exterior, box)
            elif exterior.obj_bp.get('IS_DRAWERS_BP'):
                draw_drawer_options(self, exterior, box)
            elif exterior.obj_bp.get('IS_BP_APPLIANCE'):
                draw_appliance_options(exterior, box)

        for insert in interiors:
            interior = sn_types.Assembly(insert)
            draw_interior_options(interior, box)

def get_number_of_equal_heights(calculator, type="Opening"):
    number_of_equal_heights = 0

    for i in range(1, 10):
        height = eval("calculator.get_calculator_prompt('{} {} Height')".format(type, str(i)))

        if height:
            number_of_equal_heights += 1 if height.equal else 0
        else:
            break

    return number_of_equal_heights

def get_number_of_equal_widths(calculator):
    number_of_equal_widths = 0

    for i in range(1, 10):
        width = eval("calculator.get_calculator_prompt('Opening {} Width')".format(str(i)))
        if width:
            number_of_equal_widths += 1 if width.equal else 0

    return number_of_equal_widths

def get_drawer_front_heights(end_hole_amt=24):
    start = 92
    start_hole_amt = 3
    df_heights = OpeningHeights(start, start_hole_amt, end_hole_amt, drawer_front=True)
    heights_iter = iter(df_heights)
    df_heights = list(heights_iter)

    return df_heights

def get_opening_heights(end_hole_amt=77):
    start = 96
    start_hole_amt = 3
    opening_heights = OpeningHeights(start, start_hole_amt, end_hole_amt)
    heights_iter = iter(opening_heights)
    opening_heights = list(heights_iter)
    return opening_heights

def get_appliance_subtype_count(self):
    appliance_count = 0

    for opening in self.island_openings:
        value = eval('self.carcass_subtype_' + str(opening.get('OPENING_NBR')))

        if int(value) == ISLAND_APPLIANCE_CARCASS:
            appliance_count += 1
        
    return appliance_count

class OpeningHeights:
    def __init__(self, start, start_hole_amt, end_hole_amt, drawer_front=False):
        self.start = start
        self.end_hole_amt = end_hole_amt - 1
        self.hole_amt = start_hole_amt
        self.drawer_front = drawer_front

    def __iter__(self):
        self.num = self.start
        return self

    def __next__(self):
        mm = self.num
        height_deduction = 0 if self.drawer_front else 0.75
        
        inch = round(self.num / 25.4 - height_deduction, 2)
        name = '{}H-{}"'.format(str(self.hole_amt), str(inch))
        self.num += 32
        self.hole_amt += 1

        if(self.hole_amt > self.end_hole_amt):
            raise StopIteration

        return ((str(mm), name, ""))

class SNAP_PT_Cabinet_Options(bpy.types.Panel):
    """Panel to Store all of the Cabinet Options"""
    bl_id = cabinet_properties.LIBRARY_NAME_SPACE + "_Advanced_Cabinet_Options"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Advanced Cabinet Options"

    props = None

    @classmethod
    def poll(cls, context):
        prefs = context.preferences.addons["snap"].preferences
        return prefs.enable_kitchen_bath_lib

    def draw_header(self, context):
        layout = self.layout
        wm = context.window_manager.snap
        kb_icon = wm.libraries["Kitchen Bath Library"].icon
        layout.label(text='', icon_value=snap.snap_icons[kb_icon].icon_id)        

    def draw_molding_options(self,layout):
        molding_box = layout.box()
        row = molding_box.row(align=True)
        row.label(text="Moldings Options:")
        row = molding_box.row(align=True)
        row.prop(self.props,'expand_crown_molding',text="",icon='TRIA_DOWN' if self.props.expand_crown_molding else 'TRIA_RIGHT',emboss=False)
        row.label(text="Crown:")
        row.prop(self.props,'crown_molding_category',text="",icon='FILE_FOLDER')
        row.prop(self.props,'crown_molding',text="")
        row.operator(cabinet_properties.LIBRARY_NAME_SPACE + ".auto_add_molding",text="",icon='PLUS').molding_type = 'Crown'
        row.operator(cabinet_properties.LIBRARY_NAME_SPACE + '.delete_molding',text="",icon='X').molding_type = 'Crown'
        if self.props.expand_crown_molding:
            row = molding_box.row()
            row.label(text="",icon='BLANK1')
            row.template_icon_view(self.props,"crown_molding",show_labels=True)
            
        row = molding_box.row(align=True)
        row.prop(self.props,'expand_base_molding',text="",icon='TRIA_DOWN' if self.props.expand_base_molding else 'TRIA_RIGHT',emboss=False)
        row.label(text="Base:")
        row.prop(self.props,'base_molding_category',text="",icon='FILE_FOLDER')
        row.prop(self.props,'base_molding',text="")
        row.operator(cabinet_properties.LIBRARY_NAME_SPACE + ".auto_add_molding",text="",icon='PLUS').molding_type = 'Base'
        row.operator(cabinet_properties.LIBRARY_NAME_SPACE + '.delete_molding',text="",icon='X').molding_type = 'Base'
        if self.props.expand_base_molding:
            row = molding_box.row()
            row.label(text="",icon='BLANK1')
            row.template_icon_view(self.props,"base_molding",show_labels=True)
            
        row = molding_box.row(align=True)
        row.prop(self.props,'expand_light_rail_molding',text="",icon='TRIA_DOWN' if self.props.expand_light_rail_molding else 'TRIA_RIGHT',emboss=False)
        row.label(text="Light Rail:")
        row.prop(self.props,'light_rail_molding_category',text="",icon='FILE_FOLDER')
        row.prop(self.props,'light_rail_molding',text="")
        row.operator(cabinet_properties.LIBRARY_NAME_SPACE + ".auto_add_molding",text="",icon='PLUS').molding_type = 'Light'
        row.operator(cabinet_properties.LIBRARY_NAME_SPACE + '.delete_molding',text="",icon='X').molding_type = 'Light'
        if self.props.expand_light_rail_molding:
            row = molding_box.row()
            row.label(text="",icon='BLANK1')
            row.template_icon_view(self.props,"light_rail_molding",show_labels=True)            
            
    def draw_hardware_options(self,layout):
        #IMPLEMENT CHANGING HINGES GLOBALLY
        #IMPLEMENT CHANGING DRAWER SLIDES GLOBALLY
        hardware_box = layout.box()
        hardware_box.label(text="Hardware Options:")
        
        row = hardware_box.row(align=True)
        row.prop(self.props,'expand_pull',text="",icon='TRIA_DOWN' if self.props.expand_pull else 'TRIA_RIGHT',emboss=False)
        row.label(text='Pulls:')
        row.prop(self.props,'pull_category',text="",icon='FILE_FOLDER')
        row.prop(self.props,'pull_name',text="")
        row.operator(cabinet_properties.LIBRARY_NAME_SPACE + '.update_pull_selection',text="",icon='FILE_REFRESH').update_all = True
        row.operator(cabinet_properties.LIBRARY_NAME_SPACE + '.update_pull_selection',text="",icon='MAN_TRANS').update_all = False
        if self.props.expand_pull:
            row = hardware_box.row()
            row.label(text="",icon='BLANK1')
            row.template_icon_view(self.props,"pull_name",show_labels=True)

    def draw_door_style_options(self,layout):
        door_style_box = layout.box()
        door_style_box.label(text="Door Options:")
        row = door_style_box.row(align=True)
        row.prop(self.props,'expand_door',text="",icon='TRIA_DOWN' if self.props.expand_door else 'TRIA_RIGHT',emboss=False)
        row.label(text="Doors:")
        row.prop(self.props,'door_category',text="",icon='FILE_FOLDER')
        row.prop(self.props,'door_style',text="")
        row.operator(cabinet_properties.LIBRARY_NAME_SPACE + '.update_door_selection',text="",icon='MAN_TRANS')
        if self.props.expand_door:
            row = door_style_box.row()
            row.label(text="",icon='BLANK1')
            row.template_icon_view(self.props,"door_style",show_labels=True)
        row = door_style_box.row(align=True)
        row.label(text="Applied Panel:")
        row.operator(cabinet_properties.LIBRARY_NAME_SPACE + '.place_applied_panel',text="Add Applied Panel",icon='MAN_TRANS')
            
    def draw_interior_defaults(self,layout):
        col = layout.column(align=True)
        
        box = col.box()
        
        box.label(text="Default Shelf Quantity:")
        row = box.row()
        row.label(text="Base Cabinets:")
        row.prop(self.props.interior_defaults,"base_adj_shelf_qty",text="Quantity")
        row = box.row()
        row.label(text="Tall Cabinets:")
        row.prop(self.props.interior_defaults,"tall_adj_shelf_qty",text="Quantity")
        row = box.row()
        row.label(text="Upper Cabinets:")
        row.prop(self.props.interior_defaults,"upper_adj_shelf_qty",text="Quantity")
        
        box = col.box()
        
        box.label(text="Default Shelf Setback:")
        row = box.row()
        row.label(text="Adjustable:")
        row.prop(self.props.interior_defaults,"adj_shelf_setback",text="Setback")
        row = box.row()
        row.label(text="Fixed:")
        row.prop(self.props.interior_defaults,"fixed_shelf_setback",text="Setback")
        
    def draw_exterior_defaults(self,layout):
        col = layout.column(align=True)
        
        box = col.box()
        box.label(text="Door & Drawer Defaults:")
        
        row = box.row(align=True)
        row.prop(self.props.exterior_defaults,"inset_door")
        
        row = box.row(align=True)
        row.prop(self.props.exterior_defaults,"use_buyout_drawer_boxes")
        row.prop(self.props.exterior_defaults,"horizontal_grain_on_drawer_fronts")        
        
        if not self.props.exterior_defaults.no_pulls:
            box = col.box()
            box.label(text="Pull Placement:")
            
            row = box.row(align=True)
            row.label(text="Base Doors:")
            row.prop(self.props.exterior_defaults,"base_pull_location",text="From Top of Door")
            
            row = box.row(align=True)
            row.label(text="Tall Doors:")
            row.prop(self.props.exterior_defaults,"tall_pull_location",text="From Bottom of Door")
            
            row = box.row(align=True)
            row.label(text="Upper Doors:")
            row.prop(self.props.exterior_defaults,"upper_pull_location",text="From Bottom of Door")
            
            row = box.row(align=True)
            row.label(text="Distance From Edge:")
            row.prop(self.props.exterior_defaults,"pull_from_edge",text="")
            
            row = box.row(align=True)
            row.prop(self.props.exterior_defaults,"center_pulls_on_drawers")
    
            if not self.props.exterior_defaults.center_pulls_on_drawers:
                row.prop(self.props.exterior_defaults,"drawer_pull_from_top",text="Distance From Top")
        
        box = col.box()
        box.label(text="Door & Drawer Reveals:")
        
        if self.props.exterior_defaults.inset_door:
            row = box.row(align=True)
            row.label(text="Inset Reveals:")
            row.prop(self.props.exterior_defaults,"inset_reveal",text="")
        else:
            row = box.row(align=True)
            row.label(text="Standard Reveals:")
            row.prop(self.props.exterior_defaults,"left_reveal",text="Left")
            row.prop(self.props.exterior_defaults,"right_reveal",text="Right")
            
            row = box.row(align=True)
            row.label(text="Base Door Reveals:")
            row.prop(self.props.exterior_defaults,"base_top_reveal",text="Top")
            row.prop(self.props.exterior_defaults,"base_bottom_reveal",text="Bottom")
            
            row = box.row(align=True)
            row.label(text="Tall Door Reveals:")
            row.prop(self.props.exterior_defaults,"tall_top_reveal",text="Top")
            row.prop(self.props.exterior_defaults,"tall_bottom_reveal",text="Bottom")
            
            row = box.row(align=True)
            row.label(text="Upper Door Reveals:")
            row.prop(self.props.exterior_defaults,"upper_top_reveal",text="Top")
            row.prop(self.props.exterior_defaults,"upper_bottom_reveal",text="Bottom")
            
        row = box.row(align=True)
        row.label(text="Vertical Gap:")
        row.prop(self.props.exterior_defaults,"vertical_gap",text="")
    
        row = box.row(align=True)
        row.label(text="Door To Cabinet Gap:")
        row.prop(self.props.exterior_defaults,"door_to_cabinet_gap",text="")
        
    def draw_carcass_defaults(self,layout):
        col = layout.column(align=True)

        box = col.box()
        row = box.row(align=True)
        row.label(text="Cabinet Back Options:")
        row = box.row(align=True)
        row.prop(self.props.carcass_defaults,"remove_back")
        row.prop(self.props.carcass_defaults,"use_nailers")
        row.prop(self.props.carcass_defaults,"use_thick_back")
        row = box.row(align=True)
        row.label(text="Nailer Width:")
        row.prop(self.props.carcass_defaults,"nailer_width",text="")
        row = box.row(align=True)
        row.label(text="Center Nailer Switch:")
        row.prop(self.props.carcass_defaults,"center_nailer_switch",text="")

        box = col.box()
        row = box.row(align=True)
        row.label(text="Cabinet Top Options:")
        row = box.row(align=True)
        row.prop(self.props.carcass_defaults,"use_full_tops")
        if not self.props.carcass_defaults.use_full_tops:
            row = box.row(align=True)
            row.label(text="Stretcher Width:")
            row.prop(self.props.carcass_defaults,"stretcher_width",text="")
        row = box.row(align=True)
        row.label(text="Sub Front Height:")
        row.prop(self.props.carcass_defaults,"sub_front_height",text="")

        box = col.box()
        row = box.row(align=True)
        row.label(text="Cabinet Valance Options:")
        row = box.row(align=True)
        row.label(text="Valance Height Top:")
        row.prop(self.props.carcass_defaults,"valance_height_top")
        row = box.row(align=True)
        row.label(text="Valance Height Bottom:")
        row.prop(self.props.carcass_defaults,"valance_height_bottom")
        row = box.row(align=True)
        row.prop(self.props.carcass_defaults,"door_valance_top")
        row.prop(self.props.carcass_defaults,"door_valance_bottom")
        row = box.row(align=True)
        row.prop(self.props.carcass_defaults,"valance_each_unit")
        
        box = col.box()
        row = box.row(align=True)
        row.label(text="Cabinet Base Assembly:")
        row = box.row(align=True)
        row.label(text="Toe Kick Height:")
        row.prop(self.props.carcass_defaults,"toe_kick_height")
        row = box.row(align=True)
        row.label(text="Toe Kick Setback:")
        row.prop(self.props.carcass_defaults,"toe_kick_setback")
        row = box.row(align=True)
        row.prop(self.props.carcass_defaults,"use_leg_levelers")
    
    def draw_cabinet_sizes(self,layout):

        col = layout.column(align=True)

        box = col.box()
        box.label(text="Standard Frameless Cabinet Sizes:")
        
        row = box.row(align=True)
        row.label(text="Base:")
        row.prop(self.props.size_defaults,"base_cabinet_height",text="")
        row.prop(self.props.size_defaults,"base_cabinet_depth",text="Depth")
        
        row = box.row(align=True)
        row.label(text="Tall:")
        row.prop(self.props.size_defaults,"tall_cabinet_height",text="")
        row.prop(self.props.size_defaults,"tall_cabinet_depth",text="Depth")
        
        row = box.row(align=True)
        row.label(text="Upper:")
        row.prop(self.props.size_defaults,"upper_cabinet_height",text="")
        row.prop(self.props.size_defaults,"upper_cabinet_depth",text="Depth")

        row = box.row(align=True)
        row.label(text="Sink:")
        row.prop(self.props.size_defaults,"sink_cabinet_height",text="")
        row.prop(self.props.size_defaults,"sink_cabinet_depth",text="Depth")

        row = box.row(align=True)
        row.label(text="Island:")
        row.prop(self.props.size_defaults,"island_cabinet_height",text="")
        row.prop(self.props.size_defaults,"island_cabinet_depth",text="Depth")
        
        row = box.row(align=True)
        row.label(text="Suspended:")
        row.prop(self.props.size_defaults,"suspended_cabinet_height",text="")
        row.prop(self.props.size_defaults,"suspended_cabinet_depth",text="Depth")
        
        row = box.row(align=True)
        row.label(text="1 Door Wide:")
        row.prop(self.props.size_defaults,"width_1_door",text="Width")
        
        row = box.row(align=True)
        row.label(text="2 Door Wide:")
        row.prop(self.props.size_defaults,"width_2_door",text="Width")
        
        row = box.row(align=True)
        row.label(text="Drawer Stack Width:")
        row.prop(self.props.size_defaults,"width_drawer",text="Width")
        
        box = col.box()
        box.label(text="Blind Cabinet Widths:")
        
        row = box.row(align=True)
        row.label(text='Base:')
        row.prop(self.props.size_defaults,"base_width_blind",text="Width")
        
        row = box.row(align=True)
        row.label(text='Tall:')
        row.prop(self.props.size_defaults,"tall_width_blind",text="Width")
        
        row = box.row(align=True)
        row.label(text='Upper:')
        row.prop(self.props.size_defaults,"upper_width_blind",text="Width")
        
        box = col.box()
        box.label(text="Inside Corner Cabinet Sizes:")
        row = box.row(align=True)
        row.label(text="Base:")
        row.prop(self.props.size_defaults,"base_inside_corner_size",text="")
        
        row = box.row(align=True)
        row.label(text="Upper:")
        row.prop(self.props.size_defaults,"upper_inside_corner_size",text="")
        
        box = col.box()
        box.label(text="Placement:")
        row = box.row(align=True)
        row.label(text="Height Above Floor:")
        row.prop(self.props.size_defaults,"height_above_floor",text="")
        
        box = col.box()
        box.label(text="Drawer Heights:")
        row = box.row(align=True)
        row.prop(self.props.size_defaults,"equal_drawer_stack_heights")
        if not self.props.size_defaults.equal_drawer_stack_heights:
            row = box.row(align=True)
            row.label(text="Top Drawer Front Height")
            row = box.row(align=True)
            row.prop(self.props.size_defaults,"top_drawer_front_height", text="")
    
    def draw(self, context):
        self.props = cabinet_properties.get_scene_props()
        layout = self.layout

        box = layout.box()
        row = box.row()
        row.prop(self.props,'main_tabs',expand=True)
        
        if self.props.main_tabs == 'DEFAULTS':
            col = box.column(align=True)
            box = col.box()
            row = box.row()
            row.prop(self.props,'defaults_tabs',expand=True)
            
            if self.props.defaults_tabs == 'SIZES':
                self.draw_cabinet_sizes(box)
            
            if self.props.defaults_tabs == 'CARCASS':
                self.draw_carcass_defaults(box)
            
            if self.props.defaults_tabs == 'EXTERIOR':
                self.draw_exterior_defaults(box)
                
            if self.props.defaults_tabs == 'INTERIOR':
                self.draw_interior_defaults(box)
            
        if self.props.main_tabs == 'OPTIONS':
            col = box.column(align=True)
            self.draw_molding_options(col)
            # self.draw_hardware_options(col)
            # self.draw_door_style_options(col)

#---------PRODUCT: EXTERIOR PROMPTS

class PROMPTS_Door_Prompts(bpy.types.Operator):
    bl_idname = cabinet_properties.LIBRARY_NAME_SPACE + ".door_prompts"
    bl_label = "Door Prompts" 
    bl_description = "This shows all of the available door options"
    bl_options = {'UNDO'}
    
    object_name: StringProperty(name="Object Name")
    
    assembly = None
    
    @classmethod
    def poll(cls, context):
        return True
        
    def check(self, context):
        self.assembly.obj_bp.location = self.assembly.obj_bp.location # Redraw Viewport
        return True
        
    def execute(self, context):
        return {'FINISHED'}

    def invoke(self,context,event):
        obj = bpy.data.objects[self.object_name]
        obj_insert_bp = sn_utils.get_bp(obj,'INSERT')
        self.assembly = sn_types.Assembly(obj_insert_bp)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=sn_utils.get_prop_dialog_width(500))
        
    def draw(self, context):
        layout = self.layout
        if self.assembly.obj_bp:
            if self.assembly.obj_bp.name in context.scene.objects:
                draw_door_options(self.assembly,layout)

def update_overall_width(self, context):
    if hasattr(self, "default_width"):
        if not self.placement_on_wall == 'FILL':
            self.width = self.default_width
            self.closet.obj_x.location.x = self.width
        else:
            self.width = self.closet.obj_x.location.x

class PROMPTS_Frameless_Cabinet_Prompts(sn_types.Prompts_Interface):
    bl_idname = cabinet_properties.LIBRARY_NAME_SPACE + ".frameless_cabinet_prompts"
    bl_label = "Frameless Cabinet Prompts" 
    bl_options = {'UNDO'}
    
    object_name: StringProperty(name="Object Name")
    active_obj = None

    width: FloatProperty(name="Width",unit='LENGTH',precision=4)
    height: EnumProperty(name="Default Hanging Panel Height", items=get_panel_heights)
    height_raw: FloatProperty(name="Height",unit='LENGTH',precision=4)
    depth: FloatProperty(name="Depth",unit='LENGTH',precision=4)
    front_row_depth: FloatProperty(name="Front Row Depth",unit='LENGTH',precision=4)
    back_row_depth: FloatProperty(name="Front Row Depth",unit='LENGTH',precision=4)
    display_x: FloatProperty(name="Depth",unit='LENGTH',precision=4)

    product_tabs: EnumProperty(name="Product Tabs",items=[('CARCASS',"Carcass","Carcass Options"),
                                                                   ('INSERTS',"Inserts","Insert Options"),
                                                                   ('ROW1',"Front","Front Options"),
                                                                   ('ROW2',"Back","Back Options"),
                                                                   ('EXTERIOR',"Exterior","Exterior Options"),
                                                                   ('INTERIOR',"Interior","Interior Options"),
                                                                   ('SPLITTER',"Openings","Openings Options")])
   
    section_tabs: EnumProperty(name="Section Tabs",items=[('SECTION1',"Seciton 1","Section 1 Options"),
                                                                   ('SECTION2',"Section 2","Section 2 Options"),
                                                                   ('SECTION3',"Section 3","Section 3 Options"),
                                                                   ('SECTION4',"Section 4","Section 4 Options"),
                                                                   ('SECTION5',"Section 5","Section 5 Options"),
                                                                   ('SECTION6',"Section 6","Section 6 Options"),
                                                                   ('SECTION7',"Section 7","Section 7 Options"),
                                                                   ('SECTION8',"Section 8","Section 8 Options")])

    door_rotation: FloatProperty(name="Door Rotation",subtype='ANGLE',min=0,max=math.radians(120))
    
    door_swing_1: EnumProperty(name="Door Swing 1",items=[('0',"Left Swing","Left Swing"),('1',"Right Swing","Right Swing")])
    door_swing_2: EnumProperty(name="Door Swing 2",items=[('0',"Left Swing","Left Swing"),('1',"Right Swing","Right Swing")])
    door_swing_3: EnumProperty(name="Door Swing 3",items=[('0',"Left Swing","Left Swing"),('1',"Right Swing","Right Swing")])
    door_swing_4: EnumProperty(name="Door Swing 4",items=[('0',"Left Swing","Left Swing"),('1',"Right Swing","Right Swing")])
    door_swing_5: EnumProperty(name="Door Swing 5",items=[('0',"Left Swing","Left Swing"),('1',"Right Swing","Right Swing")])
    door_swing_6: EnumProperty(name="Door Swing 6",items=[('0',"Left Swing","Left Swing"),('1',"Right Swing","Right Swing")])
    door_swing_7: EnumProperty(name="Door Swing 7",items=[('0',"Left Swing","Left Swing"),('1',"Right Swing","Right Swing")])
    door_swing_8: EnumProperty(name="Door Swing 8",items=[('0',"Left Swing","Left Swing"),('1',"Right Swing","Right Swing")])
    
    carcass_subtype_1: EnumProperty(name='Carcass Subtype 1',items=[('0',"Base","Base"),('1',"Appliance","Appliance"),('2',"Sink","Sink")])
    carcass_subtype_2: EnumProperty(name='Carcass Subtype 2',items=[('0',"Base","Base"),('1',"Appliance","Appliance"),('2',"Sink","Sink")])
    carcass_subtype_3: EnumProperty(name='Carcass Subtype 3',items=[('0',"Base","Base"),('1',"Appliance","Appliance"),('2',"Sink","Sink")])
    carcass_subtype_4: EnumProperty(name='Carcass Subtype 4',items=[('0',"Base","Base"),('1',"Appliance","Appliance"),('2',"Sink","Sink")])
    carcass_subtype_5: EnumProperty(name='Carcass Subtype 5',items=[('0',"Base","Base"),('1',"Appliance","Appliance"),('2',"Sink","Sink")])
    carcass_subtype_6: EnumProperty(name='Carcass Subtype 6',items=[('0',"Base","Base"),('1',"Appliance","Appliance"),('2',"Sink","Sink")])
    carcass_subtype_7: EnumProperty(name='Carcass Subtype 7',items=[('0',"Base","Base"),('1',"Appliance","Appliance"),('2',"Sink","Sink")])
    carcass_subtype_8: EnumProperty(name='Carcass Subtype 8',items=[('0',"Base","Base"),('1',"Appliance","Appliance"),('2',"Sink","Sink")])

    placement_on_wall: EnumProperty(
        name="Placement on Wall",items=[('SELECTED_POINT', "Selected Point", ""),
                                        ('FILL', "Fill", ""),
                                        ('LEFT', "Left", ""),
                                        ('CENTER', "Center", ""),
                                        ('RIGHT', "Right", "")],
                                        default='SELECTED_POINT')

    left_end_condition: EnumProperty(
        name="Left End Condition",items=[('0', 'Middle Panel', "Middle Panel"),
                                        ('1', 'End Panel', "End Panel")])                                     
    right_end_condition: EnumProperty(
        name="Right End Condition",items=[('0', 'Middle Panel', "Middle Panel"),
                                        ('1', 'End Panel', "End Panel")])

    left_offset: FloatProperty(name="Left Offset", default=0, subtype='DISTANCE', precision=4)
    right_offset: FloatProperty(name="Right Offset", default=0, subtype='DISTANCE', precision=4)

    constraint_button: EnumProperty(
        name="Constraint Button Options",items=[('0', 'Default', "Default"),
                                                ('1', 'Remove Link', "Remove Link")],
                                                default="0")
    
    selected_location = 0
    last_placement = 'SELECTED_POINT'
    default_width = 0
    display_last_x = 0
    is_constrained_x = False
    constraint_target_x = None
    constraint_product_x = None
    
    product = None
    
    open_door_prompts = []
    
    show_exterior_options = False
    show_interior_options = False
    show_splitter_options = False
    show_insert_options = True
    show_placement_options = False
    show_island_options = False
    show_double_sided = False

    carcass = None
    exterior = None
    interior = None
    counter_top = None
    wall_bp = None
    
    doors = []
    drawers = []
    splitters = []
    openings = []
    island_openings = []
    island_splitters = []
    interiors = []
    inserts = []
    calculators = []

    def reset_variables(self):
        self.product_tabs = 'CARCASS'
        self.section_tabs = 'SECTION1'
        self.active_obj = None
        self.width = 0
        self.height_raw = 0
        self.display_x = 0
        self.display_last_x = 0
        self.constraint_button = "0"
        self.is_constrained_x = False
        self.constraint_target_x = None
        self.constraint_product_x = None
        self.show_double_sided = False
        self.doors = []
        self.drawers = []
        self.splitters = []
        self.openings = []
        self.island_openings = []
        self.island_splitters = []
        self.inserts = []
        self.interiors = []
        self.calculators = []

    def remove_constraints(self):
        bpy.ops.lm_cabinets.remove_location_constraint(obj_bp_name=self.product.obj_bp.name)
        self.is_constrained_x = False

    def update_constraint_flags(self):
        self.is_constrained_x = False
        for constraint in self.product.obj_bp.constraints:
            if constraint.type == 'COPY_LOCATION':
                self.is_constrained_x = True
                self.constraint_target_x = constraint.target
                self.constraint_product_x = sn_utils.get_bp(constraint.target, 'PRODUCT')

    def update_prompts(self):
        for obj_bp in self.doors:
            door = sn_types.Assembly(obj_bp)
            door_swing_ppt = door.get_prompt("Door Swing")
            if door_swing_ppt:
                if self.product.obj_bp.get("IS_BP_ISLAND"):
                    opening_bp = self.get_island_opening(obj_bp)
                    opening_nbr = opening_bp.get('OPENING_NBR')
                else:
                    opening_nbr = 1
                exec('door_swing_ppt.set_value(int(self.door_swing_' + str(opening_nbr) + '))')

        left_end_condition_ppt = self.carcass.get_prompt("Left End Condition")
        right_end_condition_ppt = self.carcass.get_prompt("Right End Condition")
        if left_end_condition_ppt:
            left_end_condition_ppt.set_value(int(self.left_end_condition))
            right_end_condition_ppt.set_value(int(self.right_end_condition))

        front_row_depth_ppt = self.carcass.get_prompt("Front Row Depth")
        back_row_depth_ppt = self.carcass.get_prompt("Back Row Depth")
        if front_row_depth_ppt:
            front_row_depth_ppt.set_value(self.front_row_depth)
        if back_row_depth_ppt:
            back_row_depth_ppt.set_value(self.back_row_depth)

        if self.product.obj_bp.get("IS_BP_ISLAND"):
            for opening_bp in self.island_openings:
                opening_nbr = opening_bp.get('OPENING_NBR')
                if opening_nbr:
                    carcass_subtype_ppt = self.carcass.get_prompt("Carcass Subtype " + str(opening_nbr))
                    if carcass_subtype_ppt:
                        carcass_subtype_val = eval('self.carcass_subtype_' + str(opening_nbr))
                        carcass_subtype_ppt.set_value(int(carcass_subtype_val))
                                        
    def update_overall_width(self):

        if not self.placement_on_wall == 'FILL':
            # self.width = self.default_width
            self.product.obj_x.location.x = self.width
        else:
            self.width = self.product.obj_x.location.x

    def update_product_size(self):
        self.product.obj_x.location.x = self.width
        toe_kick_offset = 0

        if self.carcass:
            toe_kick_ppt = self.carcass.get_prompt("Toe Kick Height")
            if toe_kick_ppt:
                toe_kick_offset = toe_kick_ppt.get_value()

        if 'IS_MIRROR' in self.product.obj_y:
            self.product.obj_y.location.y = -self.depth
        else:
            self.product.obj_y.location.y = self.depth

        if "CARCASS_TYPE" in self.carcass.obj_bp:
            if self.carcass.obj_bp['CARCASS_TYPE'] != 'Appliance':
                if 'IS_MIRROR' in self.product.obj_z:
                    self.product.obj_z.location.z = sn_unit.millimeter(-float(self.height))+toe_kick_offset
                else:
                    self.product.obj_z.location.z = sn_unit.millimeter(float(self.height))+toe_kick_offset
        else:
            if 'IS_MIRROR' in self.product.obj_z:
                self.product.obj_z.location.z = -float(self.height_raw)
            else:
                self.product.obj_z.location.z = float(self.height_raw)

        if self.constraint_target_x:
            self.constraint_target_x.matrix_local.translation.x += self.display_x - self.display_last_x
        self.display_last_x = self.display_x

        sn_utils.run_calculators(self.product.obj_bp)

    def update_door_dimensions(self):
        for door_insert_bp in self.doors:
            doors = Doors(door_insert_bp)
            doors.update_dimensions()

    def update_drawer_dimensions(self):
        for drawer_insert in self.drawers:
            if "VERTICAL_DRAWERS" in drawer_insert.obj_bp:
                drawer = Vertical_Drawers(drawer_insert.obj_bp)
            else:
                drawer = Horizontal_Drawers(drawer_insert.obj_bp)
            drawer.update_dimensions()

    def update_carcass_dimensions(self):
        if self.carcass:
            if "STANDARD_CARCASS" in self.carcass.obj_bp:
                carcass = Standard_Carcass(self.carcass.obj_bp)
            elif "ISLAND_CARCASS" in self.carcass.obj_bp:
                carcass = Island_Carcass(self.carcass.obj_bp)
            else:
                carcass = Inside_Corner_Carcass(self.carcass.obj_bp)
            carcass.update_dimensions()

    def update_product_dimensions(self):
        if self.product:
            prod_assembly = Standard(self.product.obj_bp)
            prod_assembly.update_dimensions()
                    
    def update_placement(self, context):
        if self.show_placement_options:
            product = self.get_product(context)
            left_x = product.get_collision_location('LEFT')
            right_x = product.get_collision_location('RIGHT')
            offsets = self.left_offset + self.right_offset
            
            if self.placement_on_wall == 'FILL':
                product.obj_bp.location.x = left_x + self.left_offset
                product.obj_x.location.x = right_x - left_x - offsets
            if self.placement_on_wall == 'LEFT':
                product.obj_bp.location.x = left_x + self.left_offset
            if self.placement_on_wall == 'CENTER':
                x_loc = left_x + (right_x - left_x) / 2 - (self.product.calc_width() / 2) 
                product.obj_bp.location.x = x_loc
            if self.placement_on_wall == 'RIGHT':
                if product.obj_bp.snap.placement_type == 'CORNER':
                    product.obj_bp.rotation_euler.z = math.radians(-90)
                product.obj_bp.location.x = (right_x - product.calc_width()) - self.right_offset
            if self.placement_on_wall == 'SELECTED_POINT' and self.last_placement != 'SELECTED_POINT':
                    product.obj_bp.location.x = self.selected_location
            elif self.placement_on_wall == 'SELECTED_POINT' and self.last_placement == 'SELECTED_POINT':
                self.selected_location = product.obj_bp.location.x

            self.last_placement = self.placement_on_wall

    def update_opening_heights(self):
        self.run_calculators(self.product.obj_bp)

        if len(self.splitters) > 0:
            splitter = self.splitters[0]  # TODO: Need to handle multiple splitters
            op_calculator = None
            op_num = 0

            for calc in self.calculators:
                if calc.name == "Opening Heights Calculator":
                    op_calculator = calc
                    op_num = len(calc.prompts)

            for i in range(1, op_num + 1):
                opening_height = splitter.get_prompt("Opening " + str(i) + " Height")
                if opening_height:
                    if not opening_height.equal:
                        op_heights = [float(height[0]) for height in get_opening_heights()]
                        height = opening_height.get_value()
                        full_height_mm = round(sn_unit.meter_to_millimeter(height + sn_unit.inch(0.75)))

                        if full_height_mm == round(sn_unit.meter_to_millimeter(height)):
                            opening_height.set_value(sn_unit.millimeter(full_height_mm))

    def update_holesize_split(self, inserts):
        object_qty = 0
        equal_qty = 0

        if len(inserts) > 0 and "IS_DRAWERS_BP" in inserts[0].obj_bp:
            type = "Drawer Front"
            heights = get_drawer_front_heights()
            calculator_name = "Vertical Drawers Calculator"
        else:
            type = "Opening"
            heights = get_opening_heights()
            calculator_name = "Opening Heights Calculator"

        for insert in inserts:
            test_height = insert.get_prompt(type + " 2 Height")
            if test_height:
                prompt_name = type.replace(" Front","") + " Quantity"
                if insert.get_prompt(prompt_name):
                    object_qty = insert.get_prompt(prompt_name).get_value()
                else: # no prompt on old assembly, loop through calc prompts to count them...
                    object_qty = 0
                    for i in range(1,10):
                        test_ppt = insert.get_prompt(type + " " + str(i) + " Height")
                        if test_ppt: 
                            object_qty += 1

                calculator = insert.get_calculator(calculator_name)
                equal_qty = get_number_of_equal_heights(calculator, type)
                for i in range(object_qty):
                    boolEven = False
                    intSize = 0
                    
                    height_ppt = insert.get_prompt(type + " " + str(i+1) + " Height")
                    if height_ppt:
                        if (height_ppt.equal == True and equal_qty > 1) or height_ppt.equal == False:
                            for height in heights:
                                full_height = height_ppt.distance_value
                                mm_offset = 0
                                if type == "Opening":
                                    full_height_mm = sn_unit.meter_to_millimeter(full_height + sn_unit.inch(0.75))
                                    mm_offset = 19
                                elif type == "Drawer Front":
                                    full_height_mm = sn_unit.meter_to_millimeter(full_height) 

                                if int(height[0]) == round(full_height_mm):
                                    boolEven = True
                                    break
                                elif int(height[0]) < round(full_height_mm):
                                    intSize = int(height[0]) - mm_offset
  
                            if boolEven == False:
                                height_ppt.equal = False
                                height_ppt.distance_value = sn_unit.millimeter(intSize)
                                equal_qty -= 1

    def update_drawer_boxes(self):
        for drawer_insert in self.drawers:
            if "VERTICAL_DRAWERS" in drawer_insert.obj_bp:
                drawer = Vertical_Drawers(drawer_insert.obj_bp)
            else:
                drawer = Horizontal_Drawers(drawer_insert.obj_bp)

            add_drawers_ppt = drawer.get_prompt("Add Drawer Boxes")
            open_drawers_ppt = drawer.get_prompt("Open Drawers")

            if add_drawers_ppt:
                if add_drawers_ppt.get_value() and not drawer.drawer_boxes:
                    box_type_ppt = drawer.get_prompt("Box Type")
                    if box_type_ppt:
                        drawer.add_drawer_boxes(box_type_ppt.get_value())
                    else:
                        drawer.add_drawer_boxes()
                    drawer.update()
                    open_drawers_ppt.set_value(1.0)
                    bpy.ops.object.select_all(action='DESELECT')
                elif not add_drawers_ppt.get_value() and drawer.drawer_boxes:
                    for assembly in drawer.drawer_boxes:
                        sn_utils.delete_object_and_children(assembly.obj_bp)
                    drawer.drawer_boxes.clear()
                    open_drawers_ppt.set_value(0)

    def update_island_carcass_subtypes(self):
        needs_left_side = []
        needs_right_side = []

        double_sided_ppt = self.carcass.get_prompt("Double Sided")
        double_sided = False
        if double_sided_ppt:
            double_sided = double_sided_ppt.get_value()

        if double_sided:
            needs_left_side.append(1)
            needs_left_side.append(len(self.island_openings))
            needs_right_side.append(int(len(self.island_openings)/2) + 1)
            needs_right_side.append(int(len(self.island_openings)/2))
        else:
            needs_left_side.append(1)
            needs_right_side.append(len(self.island_openings))
           
        for opening in self.island_openings:
            opening_nbr = opening.get("OPENING_NBR")
            Remove_Left_Side = self.carcass.get_prompt("Remove Left Side " + str(opening_nbr))
            Remove_Right_Side = self.carcass.get_prompt("Remove Right Side " + str(opening_nbr))
            
            if opening_nbr in needs_left_side:
                Remove_Left_Side.set_value(False)
            else:
                Remove_Left_Side.set_value(True)

            if opening_nbr in needs_right_side:
                Remove_Right_Side.set_value(False)
            else:
                Remove_Right_Side.set_value(True)

    def get_island_carcass_subtypes(self):
        for opening in self.island_openings:
            opening_nbr = opening.get("OPENING_NBR")

            carcass_subtype_ppt = self.carcass.get_prompt("Carcass Subtype " + str(opening_nbr))
            if carcass_subtype_ppt:
                exec('self.carcass_subtype_' + str(opening_nbr) + ' = str(carcass_subtype_ppt.get_value())')

    def check(self, context):
        self.update_prompts()
        self.update_overall_width()
        if self.is_constrained_x and self.constraint_button == "1":
            self.remove_constraints()
        self.update_constraint_flags()
        self.update_product_size()
        self.update_placement(context)
        self.update_opening_heights()
        self.update_holesize_split(self.splitters)
        self.update_holesize_split(self.drawers)
        self.update_drawer_boxes()
        self.update_island_carcass_subtypes()
        self.run_calculators(self.product.obj_bp)
        context.view_layer.update()
        self.update_product_dimensions()
        self.product = self.get_product(context)
        if self.active_obj:
            bpy.context.view_layer.objects.active = bpy.data.objects[self.active_obj.name]

        return True

    def execute(self, context):
        sn_utils.run_calculators(self.product.obj_bp)
        return {'FINISHED'}

    def get_product(self, context):
        obj = bpy.data.objects[bpy.context.object.name]
        obj_product_bp = sn_utils.get_bp(obj, 'PRODUCT')
        product = sn_types.Assembly(obj_product_bp)
        self.depth = math.fabs(product.obj_y.location.y)
        self.width = math.fabs(product.obj_x.location.x)
        return product

    def get_island_opening(self, obj=None):
        if not obj:
            if len(bpy.context.view_layer.objects.selected) > 0:
                obj = bpy.context.view_layer.objects.selected[0]

        if obj:
            if obj.get('ISLAND_ROW_NBR'):
                return obj
            else:
                if obj.parent and obj.parent.get("IS_BP_ISLAND"):
                    for opening in self.island_openings:
                        if opening.get('OPENING_NBR') == obj.get('OPENING_NBR'):
                            obj = opening
                            break
                else:
                    return self.get_island_opening(obj.parent)

        return obj
    
    def set_island_tab_defaults(self):
        if len(self.island_openings) > 0:
            opening = self.get_island_opening()
            if opening:
                row_nbr = opening.get('ISLAND_ROW_NBR') 
                if row_nbr == 1:
                    section_nbr = opening.get('OPENING_NBR')
                elif row_nbr == 2:
                    section_nbr = get_section_from_back_opening(self, opening.get('OPENING_NBR'))
                else:
                    section_nbr = None

                if row_nbr:
                    self.product_tabs = 'ROW' + str(row_nbr)
                if section_nbr:
                    self.section_tabs = 'SECTION' + str(section_nbr)
    
    def check_insert_tags(self, insert, tag_list):
        for tag in tag_list:
            if tag in insert and insert[tag]:
                return True
        return False

    def update_insert_tags(self,):
        notTagged = True
        opening_nbr = 1
        obj_bp_list = sn_utils.get_assembly_bp_list(self.product.obj_bp,[])
        openings = []
        inserts = []

        for obj_bp in obj_bp_list:
            if "IS_BP_OPENING" in obj_bp or obj_bp.snap.type_group == 'OPENING':
                obj_bp.hide_viewport = False
                openings.append(obj_bp)

            if "OPENING_NBR" in obj_bp:
                notTagged = False
            elif self.check_insert_tags(obj_bp, ["IS_BP_DOOR_INSERT","IS_DRAWERS_BP","IS_BP_APPLIANCE","IS_BP_SHELVES","IS_BP_DIVIDER","IS_BP_DIVISION"]):
                inserts.append(obj_bp)

        if len(openings) == 0:
            opening = self.product.add_opening()
            opening.obj_bp.snap.type_group = 'OPENING'
            opening.obj_bp["IS_BP_OPENING"] = True
            opening.obj_bp['OPENING_NBR'] = 1
            opening.obj_bp.parent = self.product.obj_bp
            openings.append(obj_bp)
        
        bpy.context.view_layer.update()
        
        if notTagged:
            self.product.obj_bp['TAGS_CONVERTED'] = True
            for opening in openings:
                opening["IS_BP_OPENING"] = True
                opening['OPENING_NBR'] = opening_nbr

                for insert in inserts:
                    if insert.location.z == opening.location.z:
                        insert['OPENING_NBR'] = opening['OPENING_NBR']
                    
                    if self.check_insert_tags(insert, ["IS_BP_DOOR_INSERT","IS_DRAWERS_BP","IS_BP_APPLIANCE"]):
                        insert["PLACEMENT_TYPE"] = "Exterior"
                    elif self.check_insert_tags(insert, ["IS_BP_SHELVES","IS_BP_DIVIDER","IS_BP_DIVISION"]):
                        insert["PLACEMENT_TYPE"] = "Interior"

                opening_nbr += 1
                opening.hide_viewport = True

    def invoke(self,context,event):
        self.reset_variables()
        self.product = self.get_product(context)
        self.update_insert_tags()
        self.update_constraint_flags()
        obj_bp_list = sn_utils.get_assembly_bp_list(self.product.obj_bp,[])
        self.show_placement_options = sn_utils.get_wall_bp(self.product.obj_bp)

        self.selected_location = self.product.obj_bp.location.x
        self.default_width = math.fabs(self.product.obj_x.location.x)
        self.height_raw = math.fabs(self.product.obj_z.location.z)
        self.display_x = math.fabs(self.product.obj_bp.matrix_local.translation.x)
        self.display_last_x = self.display_x
        self.placement_on_wall = 'SELECTED_POINT'
        self.last_placement = 'SELECTED_POINT'
        self.left_offset = 0
        self.right_offset = 0

        for obj_bp in obj_bp_list:
            if "IS_BP_CARCASS" in obj_bp:
                self.carcass = sn_types.Assembly(obj_bp)
                toe_kick_ppt = self.carcass.get_prompt("Toe Kick Height")
                if toe_kick_ppt:
                    self.height = str(round(math.fabs(sn_unit.meter_to_millimeter(self.product.obj_z.location.z-toe_kick_ppt.get_value()))))
                else:
                    self.height = str(round(math.fabs(sn_unit.meter_to_millimeter(self.product.obj_z.location.z))))
                left_end_condition_ppt = self.carcass.get_prompt("Left End Condition")
                right_end_condition_ppt = self.carcass.get_prompt("Right End Condition")
                if left_end_condition_ppt and right_end_condition_ppt:
                    self.left_end_condition = str(left_end_condition_ppt.get_value())
                    self.right_end_condition = str(right_end_condition_ppt.get_value())

                if "CARCASS_TYPE" in self.carcass.obj_bp:
                    if self.carcass.obj_bp['CARCASS_TYPE'] != "Appliance":
                        toe_kick_ppt = self.carcass.get_prompt("Toe Kick Height")
                        if toe_kick_ppt:
                            self.height = str(round(math.fabs(sn_unit.meter_to_millimeter(self.product.obj_z.location.z-toe_kick_ppt.get_value()))))
                        else:
                            self.height = str(round(math.fabs(sn_unit.meter_to_millimeter(self.product.obj_z.location.z))))
                    if self.carcass.obj_bp['CARCASS_TYPE'] == "Island":
                        self.show_island_options = True
                        double_sided_ppt = self.carcass.get_prompt("Double Sided")
                        if double_sided_ppt:
                            self.show_double_sided = double_sided_ppt.get_value()
                        front_row_depth_ppt = self.carcass.get_prompt("Front Row Depth")
                        back_row_depth_ppt = self.carcass.get_prompt("Back Row Depth")
                        if front_row_depth_ppt:
                            self.front_row_depth = front_row_depth_ppt.get_value()
                        if back_row_depth_ppt:
                            self.back_row_depth = back_row_depth_ppt.get_value()
                        for child in self.product.obj_bp.children:
                            if child.get("IS_BP_OPENING"):
                                self.island_openings.append(child)
                            elif child.get("IS_BP_SPLITTER"):
                                self.island_splitters.append(child)

                        calculator = self.carcass.get_calculator("Front Row Widths Calculator")
                        if calculator:
                            self.calculators.append(calculator)
                        calculator = self.carcass.get_calculator("Back Row Widths Calculator")
                        if calculator:
                            self.calculators.append(calculator)

            if "PLACEMENT_TYPE" in obj_bp:
                self.show_insert_options = True

            if "IS_BP_CABINET_COUNTERTOP" in obj_bp:
                if not self.counter_top:
                    self.counter_top = sn_types.Assembly(obj_bp)

            if "IS_BP_DOOR_INSERT" in obj_bp:
                self.show_exterior_options = True
                if obj_bp not in self.doors:
                    self.doors.append(obj_bp)
                    door = sn_types.Assembly(obj_bp)
                    door_swing_ppt = door.get_prompt("Door Swing")
                    if door_swing_ppt:
                        if self.product.obj_bp.get("IS_BP_ISLAND"):
                            opening_bp = self.get_island_opening(obj_bp)
                            opening_nbr = opening_bp.get('OPENING_NBR')
                        else:
                            opening_nbr = 1
                        exec('self.door_swing_' + str(opening_nbr) + ' = str(door_swing_ppt.get_value())')
           
            if "IS_DRAWERS_BP" in obj_bp:                
                self.show_exterior_options = True

                if "VERTICAL_DRAWERS" in obj_bp:
                    assy = Vertical_Drawers(obj_bp)
                else:
                    assy = Horizontal_Drawers(obj_bp)

                assy = Vertical_Drawers(obj_bp)
                calculator = assy.get_calculator("Vertical Drawers Calculator")
                if assy:
                    self.drawers.append(assy)
                if calculator:
                    self.calculators.append(calculator)

            if "IS_BP_OPENING" in obj_bp:
                assy = sn_types.Assembly(obj_bp)
                if assy not in self.openings:
                    self.openings.append(assy)

            if self.check_insert_tags(obj_bp, ["IS_BP_SPLITTER"]):
                self.show_splitter_options = True
                assy = sn_types.Assembly(obj_bp)

                if obj_bp not in self.splitters:
                    self.splitters.append(assy)

                calculator = assy.get_calculator('Opening Heights Calculator')
                if assy not in self.splitters:
                    self.splitters.append(assy)
                if calculator:
                    self.calculators.append(calculator)

            if self.check_insert_tags(obj_bp, ["IS_BP_SHELVES","IS_BP_DIVIDER","IS_BP_DIVISION"]):
                self.show_interior_options = True
                if obj_bp not in self.interiors:
                    self.interiors.append(obj_bp)

        ############ remove after sure all old project files are outdated...
        self.update_opening_heights()
        self.get_island_carcass_subtypes()
        self.set_island_tab_defaults()
        self.update_holesize_split(self.splitters)
        self.update_holesize_split(self.drawers)
        ################
        self.run_calculators(self.product.obj_bp)

        return super().invoke(context, event, width=550)

    def draw_product_placment(self,layout):
        box = layout.box()
        
        row = box.row(align=True)
        row.label(text='Placement',icon='LATTICE_DATA')
        row.prop_enum(self, "placement_on_wall", 'SELECTED_POINT', icon='RESTRICT_SELECT_OFF', text="Selected")
        row.prop_enum(self, "placement_on_wall", 'FILL', icon='ARROW_LEFTRIGHT', text="Fill")
        row.prop_enum(self, "placement_on_wall", 'LEFT', icon='TRIA_LEFT', text="Left") 
        row.prop_enum(self, "placement_on_wall", 'CENTER', icon='TRIA_UP_BAR', text="Center") 
        row.prop_enum(self, "placement_on_wall", 'RIGHT', icon='TRIA_RIGHT', text="Right") 
        
        if self.placement_on_wall == 'FILL':
            row = box.row()
            row.label(text='Offset',icon='ARROW_LEFTRIGHT')
            row.prop(self, "left_offset", icon='TRIA_LEFT', text="Left") 
            row.prop(self, "right_offset", icon='TRIA_RIGHT', text="Right") 
        
        if self.placement_on_wall in 'LEFT':
            row = box.row()
            row.label(text='Offset',icon='BACK')
            row.prop(self, "left_offset", icon='TRIA_LEFT', text="Left")
 
        if self.placement_on_wall in {'SELECTED_POINT','CENTER'}:
            row = box.row()
        
        if self.placement_on_wall in 'RIGHT':
            row = box.row()
            row.label(text='Offset',icon='FORWARD')
            row.prop(self, "right_offset", icon='TRIA_RIGHT', text="Right")          
        
    def draw_product_constraints(self, layout):

        box = layout.box()
        row = box.row()
        col = row.column(align=True)

        label = "LINKED TO: " + self.constraint_product_x.name
        col.label(text=label, icon='RESTRICT_INSTANCED_OFF')

        col = row.column(align=True)
        col.prop_enum(self, "constraint_button", '1') 
   
    def draw_product_size(self, layout, alt_height="", use_rot_z=True):
        box = layout.box()
        row = box.row()

        col = row.column(align=True)
        row1 = col.row(align=True)
        if self.object_has_driver(self.product.obj_x):
            row1.label(text='Width: ' + str(sn_unit.meter_to_active_unit(math.fabs(self.product.obj_x.location.x))))
        elif self.placement_on_wall == 'FILL':
            width = round(sn_unit.meter_to_inch(self.product.obj_x.location.x), 2)
            label = str(width).replace(".0", "") + '"'
            row1.label(text="Width:")
            row1.label(text=label)
        else:
            row1.label(text='Width:')
            row1.prop(self,'width',text="")

        row1 = col.row(align=True)
        if sn_utils.object_has_driver(self.product.obj_z):
            row1.label(text='Height: ' + str(round(sn_unit.meter_to_active_unit(math.fabs(self.product.obj_z.location.z)), 3)))
        else:
            row1.label(text='Height:')

            if alt_height == "":
                carcass_type = self.carcass.obj_bp.get("CARCASS_TYPE")
                if carcass_type:
                    if carcass_type == 'Appliance':
                        row1.prop(self, 'height_raw', text="")
                    elif carcass_type == 'Island' and get_appliance_subtype_count(self) == len(self.island_openings):
                        row1.prop(self, 'height_raw', text="")
                    else:
                        row1.prop(self, 'height', text="")
            else:
                row1.prop(self, alt_height, text="")

        row1 = col.row(align=True)
        if sn_utils.object_has_driver(self.product.obj_y):
            row1.label(text='Depth: ' + str(round(sn_unit.meter_to_active_unit(math.fabs(self.product.obj_y.location.y)), 3)))
        else:
            front_row_depth = self.carcass.get_prompt("Front Row Depth")
            back_row_depth = self.carcass.get_prompt("Back Row Depth")
            is_double_sided = self.carcass.obj_bp.get("DOUBLE_SIDED")
            
            front_depth_label = "Front Depth:" if is_double_sided else "Depth:"
            if front_row_depth:
                row1.label(text=front_depth_label)
                row1.prop(self, 'front_row_depth', text="")
                if "DOUBLE_SIDED" in self.carcass.obj_bp and back_row_depth:
                    row2 = col.row(align=True)
                    row2.label(text='Back Depth:')
                    row2.prop(self, 'back_row_depth', text="")    
            else:
                row1.label(text='Depth:')
                row1.prop(self, 'depth', text="")

        col = row.column(align=True)
        col.label(text="Location X:")
        col.label(text="Location Y:")
        col.label(text="Location Z:")
        if use_rot_z:
            col.label(text="Rotation Z:")

        col = row.column(align=True)
        if self.is_constrained_x:
            col.prop(self, 'display_x', text="")
        else:
            col.prop(self.product.obj_bp, 'location', index=0, text="")
        col.prop(self.product.obj_bp, 'location', index=1, text="")
        col.prop(self.product.obj_bp, 'location', index=2, text="")
        if use_rot_z:
            col.prop(self.product.obj_bp, 'rotation_euler', index=2, text="")

        left_end_condition = self.carcass.get_prompt("Left End Condition")
        right_end_condition = self.carcass.get_prompt("Right End Condition")
        if left_end_condition:
            box = layout.box()
            row = box.row()
            row.label(text="Left End Condition:")
            row.prop(self, 'left_end_condition', text="")
            row.label(text="Right End Condition:")
            row.prop(self, 'right_end_condition', text="")

    def object_has_driver(self,obj):
        if obj.animation_data:
            if len(obj.animation_data.drivers) > 0:
                return True
                
    def draw_carcass_prompts(self,layout):
        if self.carcass:
            if self.carcass.obj_bp.get("CARCASS_TYPE") == 'Island':
                draw_island_options(self, ISLAND_FRONT_ROW, self.carcass, layout)
                if self.show_double_sided:
                    draw_island_options(self, ISLAND_BACK_ROW, self.carcass, layout)
            draw_carcass_options(self, self.carcass, layout)
            
        if self.counter_top:
            draw_countertop_options(self.counter_top, self.product, layout)

    def draw_door_prompts(self,layout):
        for door_bp in self.doors:
            door = sn_types.Assembly(door_bp)

            for child in door.obj_bp.children:
                if "DOOR_HOLE_LABEL" in child:
                    print("Update Door Height Label...")
                    # height_hole_count_dim = sn_types.Dimension(child)
                    # height_hole_count_dim.set_label()

            draw_door_options(self, door, layout)
        
    def draw_drawer_prompts(self,layout):
        for drawer in self.drawers:
            draw_drawer_options(self, drawer, layout)

    def draw_interior_prompts(self,layout):
        for interior_bp in self.interiors:
            interior = sn_types.Assembly(interior_bp)
            draw_interior_options(interior, layout)

    def draw_splitter_prompts(self,layout):
        for splitter in self.splitters:
            draw_splitter_options(splitter, layout)

    def draw_insert_prompts(self,layout):
        if self.splitters:
            for splitter in self.splitters:
                draw_insert_options(self, splitter, layout)
        else:
            for opening in self.openings:
                draw_insert_options(self, opening, layout)

    def draw_island_sections(self, layout):
        opening_index = int(self.section_tabs[len(self.section_tabs)-1]) - 1
        if self.product_tabs == 'ROW2':
           opening_index = get_back_opening_from_section(self, opening_index)
        opening_bp = self.island_openings[opening_index]

        if opening_bp:
            box = layout.box()
            opening_nbr = opening_bp.get("OPENING_NBR")
             
            label = "Empty"
            for child in opening_bp.parent.children:
                if child.get('OPENING_NBR'):
                    if child.get('OPENING_NBR') == opening_nbr:
                        if child.get('PLACEMENT_TYPE') == "Exterior":
                            label = child.name
                        elif child.get('PLACEMENT_TYPE') == "Interior" and label == "Empty":
                            label = child.name
            splitter = None
            for splitter_bp in self.island_splitters:
                if splitter_bp.get("OPENING_NBR") == opening_bp.get("OPENING_NBR"):
                    splitter = sn_types.Assembly(splitter_bp)
                    label = splitter_bp.name
                    break
            if label.find(".") > 0:
                label = label[:-4]    

            calculator = self.carcass.get_calculator("Front Row Widths Calculator")
            if calculator.get_calculator_prompt("Opening " + str(opening_nbr) + " Width"):
                opening_ppt = calculator.get_calculator_prompt("Opening " + str(opening_nbr) + " Width")
                draw_hole_size_width(opening_nbr, box, opening_ppt, calculator, "Section", label)
            else:
                calculator = self.carcass.get_calculator("Back Row Widths Calculator")
                opening_ppt = calculator.get_calculator_prompt("Opening " + str(opening_nbr) + " Width")
                draw_hole_size_width(opening_nbr, box, opening_ppt, calculator, "Section", label)



            if splitter:
                draw_insert_options(self, splitter, box)
            else:
                opening = sn_types.Assembly(opening_bp)
                draw_insert_options(self, opening, box)

    def draw_section_tabs(self, layout):
        is_preset = False

        if self.product_tabs == 'ROW1':
            start_nbr = 1
            if self.show_double_sided:
                end_nbr = int(len(self.island_openings)/2)
            else:
                end_nbr = int(len(self.island_openings))
        elif self.product_tabs == 'ROW2':
            start_nbr = int(len(self.island_openings)/2)+1
            end_nbr = int(len(self.island_openings))
        
        row = layout.row(align=True)
        for i in range(start_nbr, end_nbr+1):
            row.prop_enum(self, 'section_tabs', 'SECTION' + str(i))
            if self.section_tabs == 'SECTION' + str(i):
                is_preset = True

        if not is_preset:
            self.section_tabs = 'SECTION' + str(start_nbr)
        
  
    def draw(self, context):
        super().draw(context)
        layout = self.layout

        if self.product.obj_bp:
            if self.product.obj_bp.name in context.scene.objects:
                box = layout.box()
                
                split = box.split(factor=.8)
                split.label(text=self.product.obj_bp.snap.name_object, icon='LATTICE_DATA')
                if self.is_constrained_x:
                    self.draw_product_constraints(box)
                self.draw_product_size(box)
                
                prompt_box = box.box()
                row = prompt_box.row(align=True)
                row.prop_enum(self, "product_tabs", 'CARCASS') 
                
                if self.show_island_options:
                    row.prop_enum(self, "product_tabs", 'ROW1')
                    if self.show_double_sided:
                        row.prop_enum(self, "product_tabs", 'ROW2')
                elif self.show_insert_options:
                    row.prop_enum(self, "product_tabs", 'INSERTS')

                if self.product_tabs == 'INSERTS':
                    self.draw_insert_prompts(prompt_box)

                if self.product_tabs in ['ROW1','ROW2']:
                    self.draw_section_tabs(prompt_box)
                    self.draw_island_sections(prompt_box)

                if self.product_tabs == 'CARCASS':
                    self.draw_carcass_prompts(prompt_box)

                if self.show_placement_options:
                    self.draw_product_placment(prompt_box)

bpy.utils.register_class(SNAP_PT_Cabinet_Options)
bpy.utils.register_class(PROMPTS_Door_Prompts)
bpy.utils.register_class(PROMPTS_Frameless_Cabinet_Prompts)
    