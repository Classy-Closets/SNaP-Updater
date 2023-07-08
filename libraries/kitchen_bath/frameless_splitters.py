

import bpy
from bpy.types import Operator
import math
from os import path
from snap import sn_types, sn_unit, sn_utils
from . import cabinet_properties
from . import common_parts
from . import frameless_exteriors
from . import cabinet_interiors
from snap.libraries.closets import closet_paths
from snap.libraries.closets.ops.drop_closet import PlaceClosetInsert
from . import cabinet_interface

LIBRARY_NAME_SPACE = "sn_kitchen_bath"
LIBRARY_NAME = "Cabinets"
INSERT_SPLITTER_CATEGORY_NAME = "Starter Splitters"

ROOT_DIR = path.dirname(__file__)
PART_WITH_EDGEBANDING = path.join(closet_paths.get_closet_assemblies_path(), "Part with Edgebanding.blend")

def add_opening_width_dimension(opening):
    Width = opening.obj_x.snap.get_var('location.x','Width')
    Height = opening.obj_y.snap.get_var('location.y','Height')

    for child in opening.obj_bp.children:
        if child.get('OPENING_WIDTH_LABEL'):
            sn_utils.delete_object_and_children(child)
    
    dim = sn_types.Dimension()
    dim.anchor["IS_KB_LABEL"] = True
    dim.anchor["OPENING_WIDTH_LABEL"] = True
    dim.parent(opening.obj_bp)
    dim.start_x("Width*0.5", [Width])
    dim.start_y("Height*0.5", [Height])
    dim.start_z("INCH(1.0)")
    dim.set_label("")

def create_dimensionss(splitter):
    for child in splitter.obj_bp.children:
        if 'IS_BP_OPENING' in child:
            opening = sn_types.Assembly(child)
            add_opening_width_dimension(opening)

def update_dimensions(splitter):
    dimensions = []
    
    for child in splitter.obj_bp.children:
        if 'IS_BP_OPENING' in child:
            for nchild in child.children:
                if 'OPENING_WIDTH_LABEL' in nchild:
                    dimensions.append(nchild)

    for anchor in dimensions:
        assembly = sn_types.Assembly(anchor.parent)
        width = math.fabs(sn_unit.meter_to_inch(assembly.obj_x.location.x))
        anchor.snap.opengl_dim.gl_label = str(round(width, 2)) + '\"'

def get_splitter_count(product):
    count = 0

    splitters = sn_utils.get_tagged_bp_list(product.obj_bp, "IS_BP_SPLITTER", [])

    if splitters:
        count = len(splitters)
        
    return count + 1

class Vertical_Splitters(sn_types.Assembly):
    
    library_name = LIBRARY_NAME
    category_name = INSERT_SPLITTER_CATEGORY_NAME
    type_assembly = "INSERT"
    placement_type = "SPLITTER"
    show_in_library = True
    id_prompt = cabinet_properties.LIBRARY_NAME_SPACE + ".frameless_cabinet_prompts"
    drop_id = "lm_cabinets.insert_splitters_drop"

    mirror_y = False
    open_name = ""
    splitter_nbr = 1
    vertical_openings = 2 #1-10

    calculator = None
    calculator_name = "Opening Heights Calculator"
    calculator_obj_name = "Opening Heights Calc Distance Obj"    
    
    opening_1_height = 0
    opening_2_height = 0
    opening_3_height = 0
    opening_4_height = 0
    opening_5_height = 0
    opening_6_height = 0
    opening_7_height = 0
    opening_8_height = 0
    opening_9_height = 0
    opening_10_height = 0
    
    remove_splitter_1 = False
    remove_splitter_2 = False
    remove_splitter_3 = False
    remove_splitter_4 = False
    remove_splitter_5 = False
    remove_splitter_6 = False
    remove_splitter_7 = False
    remove_splitter_8 = False
    remove_splitter_9 = False
    
    interior_1 = None
    exterior_1 = None
    interior_2 = None
    exterior_2 = None
    interior_3 = None
    exterior_3 = None
    interior_4 = None
    exterior_4 = None
    interior_5 = None
    exterior_5 = None
    interior_6 = None
    exterior_6 = None
    interior_7 = None
    exterior_7 = None
    interior_8 = None
    exterior_8 = None
    interior_9 = None
    exterior_9 = None
    interior_10 = None
    exterior_10 = None
    interior_11 = None
    exterior_11 = None
    
    def add_prompts(self):
        self.add_prompt("Thickness", 'DISTANCE', sn_unit.inch(.75))
        self.add_prompt("Left Thickness", 'DISTANCE', sn_unit.inch(.75))
        self.add_prompt("Right Thickness", 'DISTANCE', sn_unit.inch(.75))
        self.add_prompt("Top Thickness", 'DISTANCE', sn_unit.inch(.75))
        self.add_prompt("Bottom Thickness", 'DISTANCE', sn_unit.inch(.75))
        self.add_prompt("Extend Top Amount", 'DISTANCE', sn_unit.inch(0))
        self.add_prompt("Extend Bottom Amount", 'DISTANCE', sn_unit.inch(0))
        self.add_prompt("Opening Quantity", 'QUANTITY', self.vertical_openings)

        self.add_prompt("Left Depth", 'DISTANCE', sn_unit.inch(24))
        self.add_prompt("Right Depth", 'DISTANCE', sn_unit.inch(24))
        
    def add_insert(self, insert, index, z_loc_vars=[], z_loc_expression="", opening_nbr=""):
        Width = self.obj_x.snap.get_var("location.x","Width")
        Depth = self.obj_y.snap.get_var("location.y","Depth")
        height_prompt = eval("self.calculator.get_calculator_prompt('Opening {} Height')".format(str(index)))
        opening_height = eval("height_prompt.get_var(self.calculator.name, 'Opening_{}_Height')".format(str(index)))
        z_dim_expression = "Opening_" + str(index) + "_Height"
        
        if insert:
            if not insert.obj_bp:
                insert.draw()

            insert.obj_bp.parent = self.obj_bp
            insert.obj_bp['SPLITTER_NBR'] = self.splitter_nbr
            insert.obj_bp['OPENING_NBR'] = opening_nbr

            if index == self.vertical_openings:
                insert.loc_z(value = 0)
            else:
                insert.loc_z(z_loc_expression,z_loc_vars)

            insert.dim_x('Width',[Width])
            insert.dim_y('Depth',[Depth])
            insert.dim_z(z_dim_expression,[opening_height])

            if index == 1:
                # ALLOW DOOR TO EXTEND TO TOP OF VALANCE
                extend_top_amount = insert.get_prompt("Extend Top Amount")
                if extend_top_amount:
                    Extend_Top_Amount = self.get_prompt("Extend Top Amount").get_var()
                    insert.get_prompt('Extend Top Amount').set_formula('Extend_Top_Amount',[Extend_Top_Amount])
            
            if index == self.vertical_openings:
                # ALLOW DOOR TO EXTEND TO BOTTOM OF VALANCE
                extend_bottom_amount = insert.get_prompt("Extend Bottom Amount")
                if extend_bottom_amount:
                    Extend_Bottom_Amount = self.get_prompt("Extend Bottom Amount").get_var()
                    insert.get_prompt('Extend Bottom Amount').set_formula('Extend_Bottom_Amount',[Extend_Bottom_Amount])
        
    def get_opening(self,index):
        opening = self.add_opening()
        opening.set_name("Opening " + str(index))
        opening.obj_bp['IS_BP_OPENING'] = True
        opening.obj_bp['SPLITTER_NBR'] = self.splitter_nbr
        opening.obj_bp['OPENING_NBR'] = index
        opening.add_prompt("Left Side Thickness", 'DISTANCE', sn_unit.inch(.75))
        opening.add_prompt("Right Side Thickness", 'DISTANCE', sn_unit.inch(.75))
        opening.add_prompt("Top Thickness", 'DISTANCE', sn_unit.inch(.75))
        opening.add_prompt("Bottom Thickness", 'DISTANCE', sn_unit.inch(.75))
        opening.add_prompt("Extend Top Amount", 'DISTANCE', sn_unit.inch(0))
        opening.add_prompt("Extend Bottom Amount", 'DISTANCE', sn_unit.inch(0))
        
        exterior = eval('self.exterior_' + str(index))
        interior = eval('self.interior_' + str(index))
        
        if interior:
            opening.obj_bp.snap.interior_open = False
        
        if exterior:
            opening.obj_bp.snap.exterior_open = False
            
        return opening

    def add_calculator(self, amt):
        Height = self.obj_z.snap.get_var('location.z', 'Height')
        Thickness = self.get_prompt('Thickness').get_var("Thickness")

        calc_distance_obj = self.add_empty(self.calculator_obj_name)
        calc_distance_obj.empty_display_size = .001
        self.calculator = self.obj_prompts.snap.add_calculator(self.calculator_name, calc_distance_obj)
        self.calculator.set_total_distance("Height-Thickness*{}".format(str(amt - 1)), [Height, Thickness])

    def add_calculator_prompts(self, amt):
        self.calculator.prompts.clear()
        for i in range(1, amt + 1):
            prompt = self.calculator.add_calculator_prompt("Opening " + str(i) + " Height")
            size = eval("self.opening_" + str(i) + "_height")
            if size > 0:
                prompt.set_value(size)
                prompt.equal = False

    def add_splitters(self):
        Width = self.obj_x.snap.get_var("location.x","Width")
        Height = self.obj_z.snap.get_var("location.z","Height")
        Depth = self.obj_y.snap.get_var("location.y","Depth")
        Thickness = self.get_prompt('Thickness').get_var()
        previous_splitter = None

        if not self.calculator:
            self.add_calculator(self.vertical_openings)

        self.add_calculator_prompts(self.vertical_openings)        
        
        for i in range(1,self.vertical_openings):
            height_prompt = eval("self.calculator.get_calculator_prompt('Opening {} Height')".format(str(i)))
            opening_height = eval("height_prompt.get_var(self.calculator.name, 'Opening_{}_Height')".format(str(i)))            

            z_loc_vars = []
            z_loc_vars.append(opening_height)
            
            if previous_splitter:
                z_loc = previous_splitter.obj_bp.snap.get_var("location.z", "Splitter_Z_Loc")
                z_loc_vars.append(z_loc)
                
            splitter = common_parts.add_kd_shelf(self)
            splitter.set_name("Splitter " + str(i))
            if previous_splitter:
                z_loc_vars.append(Thickness)
                splitter.loc_z('Splitter_Z_Loc-Opening_' + str(i) + '_Height-Thickness',z_loc_vars)
            else:
                z_loc_vars.append(Height)
                splitter.loc_z('Height-Opening_' + str(i) + '_Height',z_loc_vars)

            splitter.dim_x('Width',[Width])
            splitter.dim_y('Depth',[Depth])
            splitter.dim_z('-Thickness',[Thickness])
            remove_splitter = eval("self.remove_splitter_" + str(i))

            if remove_splitter:
                splitter.get_prompt('Hide').set_fomula(value=True)
            
            previous_splitter = splitter
            
            opening_z_loc_vars = []
            opening_z_loc = previous_splitter.obj_bp.snap.get_var("location.z", "Splitter_Z_Loc")
            opening_z_loc_vars.append(opening_z_loc)
            
            opening = self.get_opening(i)
            self.add_insert(opening, i, opening_z_loc_vars, "Splitter_Z_Loc", opening.obj_bp["OPENING_NBR"])

            exterior = eval('self.exterior_' + str(i))
            self.add_insert(exterior, i, opening_z_loc_vars, "Splitter_Z_Loc", opening.obj_bp["OPENING_NBR"])
            
            interior = eval('self.interior_' + str(i))
            self.add_insert(interior, i, opening_z_loc_vars, "Splitter_Z_Loc", opening.obj_bp["OPENING_NBR"])
            
        #ADD LAST INSERT

        bottom_opening = self.get_opening(self.vertical_openings)
        self.add_insert(bottom_opening, self.vertical_openings, opening_nbr=bottom_opening.obj_bp["OPENING_NBR"])

        bottom_exterior = eval('self.exterior_' + str(self.vertical_openings))
        self.add_insert(bottom_exterior, self.vertical_openings, opening_nbr=bottom_opening.obj_bp["OPENING_NBR"])
        
        bottom_interior = eval('self.interior_' + str(self.vertical_openings))
        self.add_insert(bottom_interior, self.vertical_openings, opening_nbr=bottom_opening.obj_bp["OPENING_NBR"])

    def draw(self):
        self.create_assembly()
        self.add_prompts()

        self.splitter_nbr = get_splitter_count(self)
        self.obj_bp['IS_BP_SPLITTER'] = True
        self.obj_bp['IS_BP_VERTICAL_SPLITTER'] = True
        self.obj_bp['SPLITTER_NBR'] = self.splitter_nbr
        self.obj_bp['PLACEMENT_TYPE'] = "Splitter"
        self.add_splitters()

        self.update()

    def export(self):
        print("EXPORT:", "Splitters")

class Horizontal_Splitters(sn_types.Assembly):
    
    library_name = LIBRARY_NAME
    category_name = INSERT_SPLITTER_CATEGORY_NAME
    type_assembly = "INSERT"
    placement_type = "SPLITTER"
    show_in_library = True
    id_prompt = cabinet_properties.LIBRARY_NAME_SPACE + ".frameless_cabinet_prompts"
    drop_id = "lm_cabinets.insert_splitters_drop"
    
    mirror_y = False
    open_name = ""
    splitter_nbr = 1
    horizontal_openings = 2 #1-10

    calculator = None
    calculator_name = "Opening Widths Calculator"
    calculator_obj_name = "Opening Widths Distance Obj"   

    opening_1_width = 0
    opening_2_width = 0
    opening_3_width = 0
    opening_4_width = 0
    opening_5_width = 0
    opening_6_width = 0
    opening_7_width = 0
    opening_8_width = 0
    opening_9_width = 0
    opening_10_width = 0
    
    interior_1 = None
    exterior_1 = None
    interior_2 = None
    exterior_2 = None
    interior_3 = None
    exterior_3 = None
    interior_4 = None
    exterior_4 = None
    interior_5 = None
    exterior_5 = None
    interior_6 = None
    exterior_6 = None
    interior_7 = None
    exterior_7 = None
    interior_8 = None
    exterior_8 = None
    interior_9 = None
    exterior_9 = None
    interior_10 = None
    exterior_10 = None
    interior_11 = None
    exterior_11 = None
    
    def create_dimensions(self):
        create_dimensionss(self) # Call module level function to create/recreate splitter opening dim labels

    def update_dimensions(self):
        update_dimensions(self)  # Call module level function to find and update splitter opening dim labels

    def add_prompts(self):
        for i in range(1,self.horizontal_openings+1):
            size = eval("self.opening_" + str(i) + "_width")
            self.add_prompt("Opening " + str(i) + " Width", 'DISTANCE', size, True if size == 0 else False)
    
        self.add_prompt("Thickness", 'DISTANCE', sn_unit.inch(.75))
        self.add_prompt("Opening Quantity", 'QUANTITY', self.horizontal_openings)
        
    def add_insert(self,insert,index,x_loc_vars=[],x_loc_expression="", opening_nbr=""):
        Height = self.obj_z.snap.get_var("location.z","Height")
        Depth = self.obj_y.snap.get_var("location.y","Depth")
        width_prompt = eval("self.calculator.get_calculator_prompt('Opening {} Width')".format(str(index)))
        opening_width = eval("width_prompt.get_var(self.calculator.name, 'Opening_{}_Width')".format(str(index)))
        x_dim_expression = "Opening_" + str(index) + "_Width"

        if insert:
            if not insert.obj_bp:
                insert.draw()
            if insert.obj_bp.get("IS_BP_OPENING"):
                add_opening_width_dimension(insert)
            insert.obj_bp.parent = self.obj_bp
            insert.obj_bp['SPLITTER_NBR'] = self.splitter_nbr
            insert.obj_bp['OPENING_NBR'] = opening_nbr    
            if index == 1:
                insert.loc_x(value = 0)
            else:
                insert.loc_x(x_loc_expression,x_loc_vars)

            insert.dim_x(x_dim_expression, [opening_width])
            insert.dim_y('Depth',[Depth])
            insert.dim_z('Height',[Height])
   
            half_overlay_left_ppt = insert.get_prompt("Half Overlay Left")
            half_overlay_right_ppt = insert.get_prompt("Half Overlay Right")
            if self.horizontal_openings > 1 and half_overlay_left_ppt and half_overlay_right_ppt:
                if opening_nbr == 1:
                    insert.get_prompt('Half Overlay Right').set_value(True)
                elif opening_nbr == self.horizontal_openings:
                    insert.get_prompt('Half Overlay Left').set_value(True)
                else:
                    insert.get_prompt('Half Overlay Right').set_value(True)
                    insert.get_prompt('Half Overlay Left').set_value(True)
        
    def get_opening(self,index):
        opening = self.add_opening()
        opening.set_name("Opening " + str(index))
        opening.obj_bp.name = "Opening " + str(index)
        opening.obj_bp['IS_BP_OPENING'] = True
        opening.obj_bp['SPLITTER_NBR'] = self.splitter_nbr
        opening.obj_bp['OPENING_NBR'] = index
        opening.add_prompt("Left Side Thickness", 'DISTANCE', sn_unit.inch(.75))
        opening.add_prompt("Right Side Thickness", 'DISTANCE', sn_unit.inch(.75))
        opening.add_prompt("Top Thickness", 'DISTANCE', sn_unit.inch(.75))
        opening.add_prompt("Bottom Thickness", 'DISTANCE', sn_unit.inch(.75))
        opening.add_prompt("Extend Top Amount", 'DISTANCE', sn_unit.inch(0))
        opening.add_prompt("Extend Bottom Amount", 'DISTANCE', sn_unit.inch(0))
        
        exterior = eval('self.exterior_' + str(index))
        interior = eval('self.interior_' + str(index))
        
        if interior:
            opening.obj_bp.mv.interior_open = False
        
        if exterior:
            opening.obj_bp.mv.exterior_open = False
            
        return opening
        
    def add_calculator(self, amt):
        Width = self.obj_x.snap.get_var('location.x', 'Width')
        Thickness = self.get_prompt('Thickness').get_var("Thickness")

        calc_distance_obj = self.add_empty(self.calculator_obj_name)
        calc_distance_obj.empty_display_size = .001
        self.calculator = self.obj_prompts.snap.add_calculator(self.calculator_name, calc_distance_obj)
        self.calculator.set_total_distance("Width-Thickness*{}".format(str(amt - 1)), [Width, Thickness])

    def add_calculator_prompts(self, amt):
        self.calculator.prompts.clear()
        for i in range(1, amt + 1):
            prompt = self.calculator.add_calculator_prompt("Opening " + str(i) + " Width")
            size = eval("self.opening_" + str(i) + "_width")
            if size > 0:
                prompt.set_value(size)
                prompt.equal = False

    def add_splitters(self):
        Height = self.obj_z.snap.get_var("location.z","Height")
        Depth = self.obj_y.snap.get_var("location.y","Depth")
        Thickness = self.get_prompt('Thickness').get_var()
        previous_splitter = None
        
        if not self.calculator:
            self.add_calculator(self.horizontal_openings)

        self.add_calculator_prompts(self.horizontal_openings) 
        
        for i in range(1,self.horizontal_openings):
            width_prompt = eval("self.calculator.get_calculator_prompt('Opening {} Width')".format(str(i)))
            opening_width = eval("width_prompt.get_var(self.calculator.name, 'Opening_{}_Width')".format(str(i)))  

            x_loc_vars = []
            x_loc_vars.append(opening_width)
            
            if previous_splitter:
                x_loc = previous_splitter.obj_bp.snap.get_var("location.x","Splitter_X_Loc")
                x_loc_vars.append(x_loc)

            splitter = common_parts.add_kd_shelf(self)
            splitter.set_name("Splitter " + str(i))
            if previous_splitter:
                x_loc_vars.append(Thickness)
                splitter.loc_x("Splitter_X_Loc+Thickness+Opening_" + str(i) + "_Width",x_loc_vars)
            else:
                splitter.loc_x("Opening_" + str(i) + "_Width",x_loc_vars)

            splitter.rot_y(value=math.radians(-90))
            splitter.dim_x('Height',[Height])
            splitter.dim_y('Depth',[Depth])
            splitter.dim_z('-Thickness',[Thickness])
   
            previous_splitter = splitter

            opening_x_loc_vars = []
            opening_x_loc = previous_splitter.obj_bp.snap.get_var("location.x","Splitter_X_Loc")
            opening_x_loc_vars.append(opening_x_loc)
            opening_x_loc_vars.append(Thickness)
            opening_x_loc_vars.append(opening_width)
            x_loc_expression = "Splitter_X_Loc-Opening_" + str(i) + "_Width"

            opening = self.get_opening(i)
            self.add_insert(opening, i, opening_x_loc_vars, x_loc_expression, opening.obj_bp["OPENING_NBR"])

            exterior = eval('self.exterior_' + str(i))
            self.add_insert(exterior, i, opening_x_loc_vars, x_loc_expression, opening.obj_bp["OPENING_NBR"])
            
            interior = eval('self.interior_' + str(i))
            self.add_insert(interior, i, opening_x_loc_vars, x_loc_expression, opening.obj_bp["OPENING_NBR"])

        #ADD LAST INSERT
        width_prompt = eval("self.calculator.get_calculator_prompt('Opening {} Width')".format(str(self.horizontal_openings)))
        opening_width = eval("width_prompt.get_var(self.calculator.name, 'Opening_{}_Width')".format(str(self.horizontal_openings)))  
        last_opening = self.get_opening(self.horizontal_openings)
        opening_x_loc_vars = []
        opening_x_loc = previous_splitter.obj_bp.snap.get_var("location.x","Splitter_X_Loc")
        opening_x_loc_vars.append(opening_x_loc)
        opening_x_loc_vars.append(Thickness)
        opening_x_loc_vars.append(opening_width)

        x_loc_expression = "Splitter_X_Loc+Thickness"
        self.add_insert(last_opening, self.horizontal_openings,opening_x_loc_vars, x_loc_expression, last_opening.obj_bp["OPENING_NBR"])

        last_exterior = eval('self.exterior_' + str(self.horizontal_openings))
        self.add_insert(last_exterior, self.horizontal_openings,opening_x_loc_vars, x_loc_expression, last_opening.obj_bp["OPENING_NBR"])
          
        last_interior = eval('self.interior_' + str(self.horizontal_openings))
        self.add_insert(last_interior, self.horizontal_openings,opening_x_loc_vars, x_loc_expression, last_opening.obj_bp["OPENING_NBR"])

    def draw(self):
        self.create_assembly()
        self.add_prompts()
        
        self.splitter_nbr = get_splitter_count(self)
        self.obj_bp['IS_BP_SPLITTER'] = True
        self.obj_bp['IS_BP_HORIZONTAL_SPLITTER'] = True
        self.obj_bp['SPLITTER_NBR'] = self.splitter_nbr
        self.obj_bp['PLACEMENT_TYPE'] = "Splitter"
        self.add_splitters()

        self.update()

#---------SPLITTER OPERATORS
class OPS_KB_Splitters_Drop(Operator, PlaceClosetInsert):
    bl_idname = "lm_cabinets.insert_splitters_drop"
    bl_label = "Custom drag and drop for splitter insert"


    def execute(self, context):
        return super().execute(context)    

    def confirm_placement(self, context):
        super().confirm_placement(context)

        insert = sn_types.Assembly(self.insert.obj_bp)
        product_bp = sn_utils.get_bp(self.insert.obj_bp, 'PRODUCT')

        splitters = sn_utils.get_tagged_bp_list(product_bp, "IS_BP_SPLITTER", [])
        splitter_qty = len(splitters)

        insert.obj_bp["SPLITTER_NBR"] = splitter_qty
        if self.selected_opening.obj_bp['OPENING_NBR']:
                insert.obj_bp['OPENING_NBR'] = self.selected_opening.obj_bp['OPENING_NBR']

        for obj_bp in insert.obj_bp.children:
            if "OPENING_NBR" in obj_bp:
                obj_bp["SPLITTER_NBR"] = splitter_qty

        cabinet_interface.update_product_dimensions(product_bp)

    def finish(self, context):
            super().finish(context)

            return {'FINISHED'}

bpy.utils.register_class(OPS_KB_Splitters_Drop)        
#---------SPLITTER INSERTS        
class INSERT_2_Horizontal_Openings(Horizontal_Splitters):
    
    def __init__(self):
        self.library_name = LIBRARY_NAME
        self.category_name = INSERT_SPLITTER_CATEGORY_NAME
        self.assembly_name = "2 Horizontal Openings"
        self.horizontal_openings = 2
        self.width = sn_unit.inch(18)
        self.height = sn_unit.inch(34)
        self.depth = sn_unit.inch(23)
        
class INSERT_3_Horizontal_Openings(Horizontal_Splitters):
    
    def __init__(self):
        self.library_name = LIBRARY_NAME
        self.category_name = INSERT_SPLITTER_CATEGORY_NAME
        self.assembly_name = "3 Horizontal Openings"
        self.horizontal_openings = 3
        self.width = sn_unit.inch(18)
        self.height = sn_unit.inch(34)
        self.depth = sn_unit.inch(23)
        
class INSERT_4_Horizontal_Openings(Horizontal_Splitters):
    
    def __init__(self):
        self.library_name = LIBRARY_NAME
        self.category_name = INSERT_SPLITTER_CATEGORY_NAME
        self.assembly_name = "4 Horizontal Openings"
        self.horizontal_openings = 4
        self.width = sn_unit.inch(18)
        self.height = sn_unit.inch(34)
        self.depth = sn_unit.inch(23)
        
class INSERT_5_Horizontal_Openings(Horizontal_Splitters):
    
    def __init__(self):
        self.library_name = LIBRARY_NAME
        self.category_name = INSERT_SPLITTER_CATEGORY_NAME
        self.assembly_name = "5 Horizontal Openings"
        self.horizontal_openings = 5
        self.width = sn_unit.inch(18)
        self.height = sn_unit.inch(34)
        self.depth = sn_unit.inch(23)
        
class INSERT_2_Vertical_Openings(Vertical_Splitters):
    
    def __init__(self):
        self.library_name = LIBRARY_NAME
        self.category_name = INSERT_SPLITTER_CATEGORY_NAME
        self.assembly_name = "2 Vertical Openings"
        self.vertical_openings = 2
        self.width = sn_unit.inch(18)
        self.height = sn_unit.inch(34)
        self.depth = sn_unit.inch(23)

class INSERT_3_Vertical_Openings(Vertical_Splitters):
    
    def __init__(self):
        self.library_name = LIBRARY_NAME
        self.category_name = INSERT_SPLITTER_CATEGORY_NAME
        self.assembly_name = "3 Vertical Openings"
        self.vertical_openings = 3
        self.width = sn_unit.inch(18)
        self.height = sn_unit.inch(34)
        self.depth = sn_unit.inch(23)
        
class INSERT_4_Vertical_Openings(Vertical_Splitters):
    
    def __init__(self):
        self.library_name = LIBRARY_NAME
        self.category_name = INSERT_SPLITTER_CATEGORY_NAME
        self.assembly_name = "4 Vertical Openings"
        self.vertical_openings = 4
        self.width = sn_unit.inch(18)
        self.height = sn_unit.inch(34)
        self.depth = sn_unit.inch(23)
        
class INSERT_5_Vertical_Openings(Vertical_Splitters):
    
    def __init__(self):
        self.library_name = LIBRARY_NAME
        self.category_name = INSERT_SPLITTER_CATEGORY_NAME
        self.assembly_name = "5 Vertical Openings"
        self.vertical_openings = 5
        self.width = sn_unit.inch(18)
        self.height = sn_unit.inch(34)
        self.depth = sn_unit.inch(23)

class INSERT_1_Opening(Vertical_Splitters):
    
    def __init__(self):
        self.library_name = LIBRARY_NAME
        self.category_name = INSERT_SPLITTER_CATEGORY_NAME
        self.assembly_name = "1 Opening"
        self.vertical_openings = 1
        self.width = sn_unit.inch(18)
        self.height = sn_unit.inch(34)
        self.depth = sn_unit.inch(23)

class INSERT_1_Door_1_Drawer_Base_Combo(Vertical_Splitters):
        
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = INSERT_SPLITTER_CATEGORY_NAME
        self.assembly_name = "2 Vertical Openings"
        self.vertical_openings = 2
        self.width = sn_unit.inch(18)
        self.height = sn_unit.inch(34)
        self.depth = sn_unit.inch(23)

        self.opening_1_height = sn_unit.millimeter(float(props.top_drawer_front_height)) - sn_unit.inch(0.58)
        self.exterior_1 = frameless_exteriors.INSERT_1_Drawer()
        self.exterior_1.prompts = {'Half Overlay Bottom':True}
        self.exterior_2 = frameless_exteriors.INSERT_Base_Single_Door()
        self.exterior_2.prompts = {'Half Overlay Top':True}
        self.interior_2 = cabinet_interiors.INSERT_Shelves()
        self.interior_2.shelf_qty = int_props.base_adj_shelf_qty

class INSERT_2_Door_1_Drawer_Base_Combo(Vertical_Splitters):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = INSERT_SPLITTER_CATEGORY_NAME
        self.assembly_name = "2 Vertical Openings"
        self.vertical_openings = 2
        self.width = sn_unit.inch(18)
        self.height = sn_unit.inch(34)
        self.depth = sn_unit.inch(23)

        self.opening_1_height = sn_unit.millimeter(float(props.top_drawer_front_height)) - sn_unit.inch(0.58)
        self.exterior_1 = frameless_exteriors.INSERT_1_Drawer()
        self.exterior_1.prompts = {'Half Overlay Bottom':True}
        self.exterior_2 = frameless_exteriors.INSERT_Base_Double_Door()
        self.exterior_2.prompts = {'Half Overlay Top':True}
        self.interior_2 = cabinet_interiors.INSERT_Shelves()
        self.interior_2.shelf_qty = int_props.base_adj_shelf_qty

class INSERT_2_Door_2_Drawer_Base_Combo(Vertical_Splitters):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = INSERT_SPLITTER_CATEGORY_NAME
        self.assembly_name = "2 Vertical Openings"
        self.vertical_openings = 2
        self.width = sn_unit.inch(18)
        self.height = sn_unit.inch(34)
        self.depth = sn_unit.inch(23)
        
        self.opening_1_height = sn_unit.millimeter(float(props.top_drawer_front_height)) - sn_unit.inch(0.58)
        self.exterior_1 = frameless_exteriors.INSERT_Horizontal_Drawers()
        self.exterior_1.prompts = {'Half Overlay Bottom':True}
        self.exterior_2 = frameless_exteriors.INSERT_Base_Double_Door()
        self.exterior_2.prompts = {'Half Overlay Top':True}
        self.interior_2 = cabinet_interiors.INSERT_Shelves()
        self.interior_2.shelf_qty = int_props.base_adj_shelf_qty
