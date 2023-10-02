import bpy
from bpy.types import Operator
import os
import math
from bpy.props import FloatProperty, EnumProperty
from snap import sn_types, sn_unit, sn_utils
from snap.libraries.kitchen_bath import cabinet_properties
from snap.libraries.closets.ops.drop_closet import PlaceClosetInsert

# APPLIANCE_PATH = os.path.join(os.path.dirname(__file__),"Appliances")
APPLIANCE_PATH = os.path.join(os.path.dirname(__file__),"assets/Built-In")
LIBRARY_NAME_SPACE = "sn_kitchen_bath"
LIBRARY_NAME = "Cabinets"
INSERT_APPLIANCE_CATEGORY_NAME = "Starter Appliances"


class Parametric_Built_In_Appliance(sn_types.Assembly):
    # library_name = "Cabinet Appliances"
    library_name = LIBRARY_NAME
    category_name = INSERT_APPLIANCE_CATEGORY_NAME
    placement_type = "EXTERIOR"
    type_assembly = "INSERT"
    appliance_type = "Built-In Appliance"
    appliance_subtype = ""
    appliance_name = ""
    appliance_width = 0
    appliance_height = 0
    show_in_library = True
    resize_enabled = True
    autofill_enabled = True
    
    # id_prompt = cabinet_properties.LIBRARY_NAME_SPACE + ".frameless_cabinet_prompts"
    id_prompt = "sn_appliances.parametric_built_in_appliance"
    # id_prompt = "wm.popup_props"
    drop_id = cabinet_properties.LIBRARY_NAME_SPACE + ".insert_appliance_drop"
    

    
    def draw(self):
        self.create_assembly()
        
        Width = self.obj_x.snap.get_var('location.x', 'Width')
        Depth = self.obj_y.snap.get_var('location.y', 'Depth')
        Height = self.obj_z.snap.get_var('location.z', 'Height')
        self.obj_bp['IS_BP_APPLIANCE'] = True
        self.obj_bp['PLACEMENT_TYPE'] = "Exterior"
        self.obj_bp["TYPE_ASSEMBLY"] = self.type_assembly
        self.obj_bp["APPLIANCE_TYPE"] = self.appliance_type
        self.obj_bp["APPLIANCE_SUBTYPE"] = self.appliance_subtype
        self.obj_bp["AUTOFILL_ENABLED"] = self.autofill_enabled
        self.obj_bp["RESIZE_ENABLED"] = self.resize_enabled
        
        appliance_bp = self.add_assembly_from_file(os.path.join(APPLIANCE_PATH,self.appliance_name+".blend"))
        appliance = sn_types.Assembly(appliance_bp)
        print("appliance_name=",self.appliance_name)
        if self.appliance_name in {'Microwave Generic','Wall Oven Generic'}:
            print("1")
            appliance.dim_x('Width',[Width])
            appliance.dim_z('Height',[Height])
            appliance.loc_y(value=sn_unit.inch(-1))
        elif not self.autofill_enabled:
            print("2")
            appliance.dim_x('Width',[Width])
            # appliance.loc_x('Width/2',[Width])
            # appliance.loc_y('Depth',[Depth])               
        else:
            print("3")
            appliance.dim_x('Width',[Width])
            appliance.dim_y('-Depth-INCH(1)',[Depth])
            appliance.dim_z('Height',[Height])

            appliance.loc_y('Depth',[Depth])
        
        self.update()

#---------APPLIANCE OPERATORS
class OPS_KB_Appliance_Insert_Drop(Operator, PlaceClosetInsert):
    bl_idname = "lm_cabinets.insert_appliance_drop"
    bl_label = "Custom drag and drop for appliance inserts"

    def execute(self, context):
        return super().execute(context)    

    def confirm_placement(self, context):
        print("self.selected_opening.obj_bp=",self.selected_opening.obj_bp.name)
        for child in self.selected_opening.obj_bp.parent.children:
            if child.get("IS_BP_APPLIANCE") and child.get("OPENING_NBR") == self.selected_opening.obj_bp.get("OPENING_NBR"):
                print("child.name=",child.name)
                sn_utils.delete_object_and_children(child)

        super().confirm_placement(context)

        insert = sn_types.Assembly(self.insert.obj_bp)
        if self.selected_opening.obj_bp['OPENING_NBR']:
                insert.obj_bp['OPENING_NBR'] = self.selected_opening.obj_bp['OPENING_NBR']


bpy.utils.register_class(OPS_KB_Appliance_Insert_Drop)

class PROMPTS_Parametric_Built_In_Appliance(sn_types.Prompts_Interface):
    bl_idname = "sn_appliances.parametric_built_in_appliance"
    bl_label = "Built In Appliance Prompts"
    bl_options = {'UNDO'}

    plane: bpy.props.StringProperty(name="Plane", default="")  # noqa F722
    appliance_bp = None
    resize_enabled = False
    
    def draw_product_dimensions(self, layout):
        row = layout.row()
        box = row.box()
        col = box.column(align=True)

        row1 = col.row(align=True)
        row1.label(text='Width:')
        if self.resize_enabled:
            row1.prop(self.product.obj_bp, 'dimensions', index=0, text="")
        else:
            row1.label(text=str(round(sn_unit.meter_to_inch(self.product.obj_bp.dimensions[0]),2)) + "\"")

        row3 = col.row(align=True)
        row3.label(text='Height:')
        if self.resize_enabled:
            row3.prop(self.product.obj_bp, 'dimensions', index=2, text="")
        else:
            row3.label(text=str(round(sn_unit.meter_to_inch(self.product.obj_bp.dimensions[2]),2)) + "\"")

        row2 = col.row(align=True)
        row2.label(text='Depth:')
        if self.resize_enabled:
            row2.prop(self.product.obj_bp, 'dimensions', index=1, text="")
        else:
            row2.label(text=str(round(sn_unit.meter_to_inch(self.product.obj_bp.dimensions[1]),2)) + "\"")


    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        obj = bpy.context.selected_objects[0]
        self.product = sn_types.Assembly(obj_bp=obj)
        self.appliance_bp = sn_utils.get_appliance_bp(obj)
        if self.appliance_bp:
            self.resize_enabled = self.appliance_bp.get("RESIZE_ENABLED")
        
        split_name = obj.name.split(".")
        category = split_name[0]

        if category == "Outlets and Switches":
            self.plane = "XZ"
        else:
            self.plane = ""

        return super().invoke(context, event, width=400)

    def draw(self, context):

        super().draw(context)
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)

        if self.appliance_bp:
            row.label(text=self.appliance_bp.snap.name_object, icon='LATTICE_DATA')

        box = layout.box()
        row = box.row(align=True)
        self.draw_product_dimensions(row)


bpy.utils.register_class(PROMPTS_Parametric_Built_In_Appliance)

#---------INSERT: PARAMETRIC APPLIANCE INSERTS       
        
class INSERT_Microwave_Generic(Parametric_Built_In_Appliance):
    
    def __init__(self):
        self.library_name = LIBRARY_NAME
        self.category_name = INSERT_APPLIANCE_CATEGORY_NAME
        self.assembly_name = "Microwave Generic"
        self.appliance_name = "Microwave Generic"      
        self.appliance_type = "Built-In Appliance"
        self.appliance_subtype = "Microwave"
        self.resize_enabled = False
        self.autofill_enabled = True
        self.width = sn_unit.inch(30)
        self.height = sn_unit.inch(14)
        self.depth = sn_unit.inch(12.5)
        
class INSERT_Wall_Oven_Generic(Parametric_Built_In_Appliance):
    
    def __init__(self):
        self.library_name = LIBRARY_NAME
        self.category_name = INSERT_APPLIANCE_CATEGORY_NAME
        self.assembly_name = "Wall Oven Generic"
        self.appliance_type = "Built-In Appliance"
        self.appliance_subtype = "Wall Oven"
        self.resize_enabled = False
        self.autofill_enabled = True
        self.width = sn_unit.inch(30)
        self.height = sn_unit.inch(14)
        self.depth = sn_unit.inch(12.5)
        self.appliance_name = "Wall Oven Generic"
        self.appliance_type = "Built-In Appliance"
        self.appliance_subtype = "Wall Oven"
        
class INSERT_Wall_Oven_Monogram(Parametric_Built_In_Appliance):
    
    def __init__(self):
        self.library_name = LIBRARY_NAME
        self.category_name = INSERT_APPLIANCE_CATEGORY_NAME
        self.assembly_name = "Wall Oven Monogram"
        self.appliance_name = "Wall Oven Monogram"
        self.appliance_type = "Built-In Appliance"
        self.appliance_subtype = "Wall Oven"
        self.resize_enabled = True
        self.autofill_enabled = False
        self.width = sn_unit.inch(30)
        self.height = sn_unit.inch(14)
        self.depth = sn_unit.inch(12.5)
        
class INSERT_Microwave_Monogram(Parametric_Built_In_Appliance):
    
    def __init__(self):
        self.library_name = LIBRARY_NAME
        self.category_name = INSERT_APPLIANCE_CATEGORY_NAME
        self.assembly_name = "Microwave Monogram"
        self.appliance_name = "Microwave Monogram"
        self.appliance_type = "Built-In Appliance"
        self.appliance_subtype = "Wall Oven"
        self.resize_enabled = True
        self.autofill_enabled = False
        self.width = sn_unit.inch(30)
        self.height = sn_unit.inch(14)
        self.depth = sn_unit.inch(12.5)

class INSERT_Wall_Oven_Hearth_Monogram(Parametric_Built_In_Appliance):
    
    def __init__(self):
        self.library_name = LIBRARY_NAME
        self.category_name = INSERT_APPLIANCE_CATEGORY_NAME
        self.assembly_name = "Wall Oven Hearth Monogram"
        self.appliance_name = "Wall Oven Hearth Monogram"
        self.appliance_type = "Built-In Appliance"
        self.appliance_subtype = "Wall Oven"
        self.resize_enabled = True
        self.autofill_enabled = False
        self.width = sn_unit.inch(30)
        self.height = sn_unit.inch(14)
        self.depth = sn_unit.inch(12.5)

class INSERT_Dishwasher_Generic(Parametric_Built_In_Appliance):
    
    def __init__(self):
        self.library_name = LIBRARY_NAME
        self.category_name = INSERT_APPLIANCE_CATEGORY_NAME
        self.assembly_name = "Dishwasher Generic"
        self.appliance_name = "Dishwasher Generic"
        self.appliance_type = "Built-In Appliance"
        self.appliance_subtype = "Dishwasher"
        self.resize_enabled = False
        self.autofill_enabled = True
        self.width = sn_unit.inch(30)
        self.height = sn_unit.inch(14)
        self.depth = sn_unit.inch(12.5)
        
class INSERT_Dishwasher_Cove(Parametric_Built_In_Appliance):
    
    def __init__(self):
        self.library_name = LIBRARY_NAME
        self.category_name = INSERT_APPLIANCE_CATEGORY_NAME
        self.assembly_name = "Dishwasher Cove"
        self.appliance_name = "Dishwasher Cove"
        self.appliance_type = "Built-In Appliance"
        self.appliance_subtype = "Dishwasher"
        self.resize_enabled = True
        self.autofill_enabled = False
        self.width = sn_unit.inch(30)
        self.height = sn_unit.inch(14)
        self.depth = sn_unit.inch(12.5)

class INSERT_Wine_Cooler_Generic(Parametric_Built_In_Appliance):
    
    def __init__(self):
        self.library_name = LIBRARY_NAME
        self.category_name = INSERT_APPLIANCE_CATEGORY_NAME
        self.assembly_name = "Wine Cooler Generic"
        self.appliance_name = "Wine Cooler Generic"
        self.appliance_type = "Built-In Appliance"
        self.appliance_subtype = "Wine Cooler"
        self.resize_enabled = False
        self.autofill_enabled = True
        self.width = sn_unit.inch(30)
        self.height = sn_unit.inch(14)
        self.depth = sn_unit.inch(12.5)

class INSERT_Gas_Rangetop_36_Monogram(Parametric_Built_In_Appliance):

    def __init__(self):
        self.library_name = LIBRARY_NAME
        self.category_name = INSERT_APPLIANCE_CATEGORY_NAME
        self.assembly_name = "Gas Rangetop 36 Monogram"
        self.appliance_name = "Gas Rangetop 36 Monogram"
        self.appliance_type = "Rangetop Appliance"
        self.appliance_subtype = "Rangetop"
        self.resize_enabled = False
        self.autofill_enabled = False
        self.width = sn_unit.inch(30)
        self.height = sn_unit.inch(14)
        self.depth = sn_unit.inch(12.5)

class INSERT_Gas_Rangetop_48_Monogram(Parametric_Built_In_Appliance):

       def __init__(self):
        self.library_name = LIBRARY_NAME
        self.category_name = INSERT_APPLIANCE_CATEGORY_NAME
        self.assembly_name = "Gas Rangetop 48 Monogram"
        self.appliance_name = "Gas Rangetop 48 Monogram"
        self.appliance_type = "Rangetop Appliance"
        self.appliance_subtype = "Rangetop"
        self.resize_enabled = False
        self.autofill_enabled = False
        self.width = sn_unit.inch(30)
        self.height = sn_unit.inch(14)
        self.depth = sn_unit.inch(12.5)
        

