import bpy
from bpy.types import Operator
import os
from snap import sn_types, sn_unit
from . import cabinet_properties
from snap.libraries.closets.ops.drop_closet import PlaceClosetInsert

APPLIANCE_PATH = os.path.join(os.path.dirname(__file__),"Appliances")
LIBRARY_NAME_SPACE = "sn_kitchen_bath"
LIBRARY_NAME = "Cabinets"
INSERT_APPLIANCE_CATEGORY_NAME = "Starter Appliances"


class Parametric_Built_In_Appliance(sn_types.Assembly):
    # library_name = "Cabinet Appliances"
    library_name = LIBRARY_NAME
    category_name = INSERT_APPLIANCE_CATEGORY_NAME
    placement_type = "EXTERIOR"
    type_assembly = "INSERT"
    show_in_library = True
    id_prompt = cabinet_properties.LIBRARY_NAME_SPACE + ".frameless_cabinet_prompts"
    # drop_id = "sn_closets.drop_insert"
    drop_id = cabinet_properties.LIBRARY_NAME_SPACE + ".insert_appliance_drop"
    
    # Name of the appliance in the assembly library
    appliance_name = ""
    
    # Size of the built in appliance so it can center in the opening
    appliance_width = 0
    appliance_height = 0
    
    def draw(self):
        self.create_assembly()
        
        Width = self.obj_x.snap.get_var('location.x', 'Width')
        Depth = self.obj_y.snap.get_var('location.y', 'Depth')
        Height = self.obj_z.snap.get_var('location.z', 'Height')
        self.obj_bp['IS_BP_APPLIANCE'] = True
        self.obj_bp['PLACEMENT_TYPE'] = "Exterior"
        
        appliance_bp = self.add_assembly_from_file(os.path.join(APPLIANCE_PATH,self.appliance_name+".blend"))
        appliance = sn_types.Assembly(appliance_bp)

        if self.appliance_name in {'Microwave','Single Oven'}:
            appliance.dim_x('Width',[Width])
            appliance.dim_z('Height',[Height])
            appliance.loc_y(value=sn_unit.inch(-1))
        else:
            appliance.dim_x('Width',[Width])
            appliance.dim_y('-Depth-INCH(1)',[Depth])
            appliance.dim_z('Height',[Height])

            appliance.loc_y('Depth',[Depth])
        
        self.update()


#---------SPLITTER OPERATORS
class OPS_KB_Appliance_Insert_Drop(Operator, PlaceClosetInsert):
    bl_idname = "lm_cabinets.insert_appliance_drop"
    bl_label = "Custom drag and drop for appliance inserts"


    def execute(self, context):
        return super().execute(context)    

    def confirm_placement(self, context):
        super().confirm_placement(context)

        insert = sn_types.Assembly(self.insert.obj_bp)
        if self.selected_opening.obj_bp['OPENING_NBR']:
                insert.obj_bp['OPENING_NBR'] = self.selected_opening.obj_bp['OPENING_NBR']


bpy.utils.register_class(OPS_KB_Appliance_Insert_Drop)

#---------INSERT: PARAMETRIC APPLIANCES        
        
class INSERT_Microwave(Parametric_Built_In_Appliance):
    
    def __init__(self):
        self.library_name = LIBRARY_NAME
        self.category_name = INSERT_APPLIANCE_CATEGORY_NAME
        self.assembly_name = "Microwave"
        self.width = sn_unit.inch(30)
        self.height = sn_unit.inch(14)
        self.depth = sn_unit.inch(12.5)
        self.appliance_name = "Microwave"      

class INSERT_Single_Oven(Parametric_Built_In_Appliance):
    
    def __init__(self):
        self.library_name = LIBRARY_NAME
        self.category_name = INSERT_APPLIANCE_CATEGORY_NAME
        self.assembly_name = "Single Oven"
        self.width = sn_unit.inch(30)
        self.height = sn_unit.inch(14)
        self.depth = sn_unit.inch(12.5)
        self.appliance_name = "Single Oven"
        
class INSERT_Dishwasher(Parametric_Built_In_Appliance):
    
    def __init__(self):
        self.library_name = LIBRARY_NAME
        self.category_name = INSERT_APPLIANCE_CATEGORY_NAME
        self.assembly_name = "Dishwasher"
        self.width = sn_unit.inch(30)
        self.height = sn_unit.inch(14)
        self.depth = sn_unit.inch(12.5)
        self.appliance_name = "Dishwasher"

class INSERT_Wine_Cooler(Parametric_Built_In_Appliance):
    
    def __init__(self):
        # self.category_name = "Appliances - Parametric"

        self.library_name = LIBRARY_NAME
        self.category_name = INSERT_APPLIANCE_CATEGORY_NAME
        self.assembly_name = "Wine Cooler"
        self.width = sn_unit.inch(30)
        self.height = sn_unit.inch(14)
        self.depth = sn_unit.inch(12.5)
        self.appliance_name = "Wine Cooler"

