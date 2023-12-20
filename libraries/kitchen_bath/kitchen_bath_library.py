from snap import sn_unit
from . import cabinets
from . import carcass_simple
from . import frameless_exteriors
from . import cabinet_interiors
from . import frameless_splitters
from . import cabinet_properties
# from . import frameless_appliances
from snap.libraries.appliances import appliance_inserts 
from snap.libraries.closets.data import data_base_assembly


LIBRARY_NAME = "Cabinets"
BASE_CATEGORY_NAME = "Base Cabinets"
TALL_CATEGORY_NAME = "Tall Cabinets"
UPPER_CATEGORY_NAME = "Upper Cabinets"
STARTER_CATEGORY_NAME = "Starter Cabinets"
DRAWER_CATEGORY_NAME = "Drawer Cabinets"
BLIND_CORNER_CATEGORY_NAME = "Blind Corner Cabinets"
INSIDE_CORNER_CATEGORY_NAME = "Inside Corner Cabinets"
HOOD_CATEGORY_NAME = "Hood Cabinets"


class PRODUCT_1_Door_Base(cabinets.Standard):

    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = BASE_CATEGORY_NAME
        self.width = props.width_1_door
        self.height = props.base_cabinet_height
        self.depth = props.base_cabinet_depth
        self.add_empty_opening = True
        self.carcass = carcass_simple.INSERT_Base_Carcass()
        self.exterior = frameless_exteriors.INSERT_Base_Single_Door()
        self.exterior.sink_mounted = False
        self.exterior.prompts = {'Half Overlay Top':False}
        self.interior = cabinet_interiors.INSERT_Shelves()
        self.interior.shelf_qty = int_props.base_adj_shelf_qty

class PRODUCT_2_Door_Base(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = BASE_CATEGORY_NAME
        self.width = props.width_2_door
        self.height = props.base_cabinet_height
        self.depth = props.base_cabinet_depth
        self.carcass = carcass_simple.INSERT_Base_Carcass()
        self.add_empty_opening = True
        self.exterior = frameless_exteriors.INSERT_Base_Double_Door()
        self.exterior.sink_mounted = False
        self.exterior.prompts = {'Half Overlay Top':False}
        self.interior = cabinet_interiors.INSERT_Shelves()
        self.interior.shelf_qty = int_props.base_adj_shelf_qty
        
class PRODUCT_1_Door_Sink(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = BASE_CATEGORY_NAME
        self.width = props.width_1_door
        self.height = props.sink_cabinet_height
        self.depth = props.sink_cabinet_depth
        self.carcass = carcass_simple.INSERT_Sink_Carcass()
        self.add_empty_opening = True
        self.exterior = frameless_exteriors.INSERT_Base_Single_Door()
        self.exterior.prompts = {'Half Overlay Top':False}
        self.interior = cabinet_interiors.INSERT_Shelves()
        self.interior.shelf_qty = 0

class PRODUCT_2_Door_Sink(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = BASE_CATEGORY_NAME
        self.width = props.width_2_door
        self.height = props.sink_cabinet_height
        self.depth = props.sink_cabinet_depth
        self.carcass = carcass_simple.INSERT_Sink_Carcass()
        self.add_empty_opening = True
        self.exterior = frameless_exteriors.INSERT_Base_Double_Door()
        self.exterior.prompts = {'Half Overlay Top':False}
        self.interior = cabinet_interiors.INSERT_Shelves()
        self.interior.shelf_qty = 0

class PRODUCT_2_Door_Rangetop_36_Base(cabinets.Standard):

    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = BASE_CATEGORY_NAME
        # self.width = props.width_1_door
        self.width = sn_unit.inch(36)
        self.height = props.rangetop_cabinet_height 
        self.depth = props.rangetop_cabinet_depth
        self.add_empty_opening = True
        self.add_countertop = False
        self.rangetop = appliance_inserts.INSERT_Gas_Rangetop_36_Monogram()
        self.carcass = carcass_simple.INSERT_Base_Carcass()
        self.exterior = frameless_exteriors.INSERT_Base_Double_Door()
        self.exterior.sink_mounted = False
        self.exterior.prompts = {'Half Overlay Top':False}
        self.interior = cabinet_interiors.INSERT_Shelves()
        self.interior.shelf_qty = int_props.base_adj_shelf_qty

class PRODUCT_2_Door_Rangetop_48_Base(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = BASE_CATEGORY_NAME
        # self.width = props.width_2_door
        self.width = sn_unit.inch(48)
        self.height = props.rangetop_cabinet_height
        self.depth = props.rangetop_cabinet_depth
        self.carcass = carcass_simple.INSERT_Base_Carcass()
        self.add_empty_opening = True
        self.add_countertop = False
        self.rangetop = appliance_inserts.INSERT_Gas_Rangetop_48_Monogram()
        self.exterior = frameless_exteriors.INSERT_Base_Double_Door()
        self.exterior.sink_mounted = False
        self.exterior.prompts = {'Half Overlay Top':False}
        self.interior = cabinet_interiors.INSERT_Shelves()
        self.interior.shelf_qty = int_props.base_adj_shelf_qty
   
class PRODUCT_2_Door_with_False_Front_Sink(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = BASE_CATEGORY_NAME
        self.width = props.width_2_door
        self.height = props.sink_cabinet_height
        self.depth = props.sink_cabinet_depth
        self.carcass = carcass_simple.INSERT_Sink_Carcass()
        self.add_empty_opening = True
        self.exterior = frameless_exteriors.INSERT_Base_Double_Door_with_False_Front()
        self.interior = cabinet_interiors.INSERT_Shelves()
        self.interior.shelf_qty = 0
        
class PRODUCT_2_Door_2_False_Front_Sink(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = BASE_CATEGORY_NAME
        self.width = props.width_2_door
        self.height = props.sink_cabinet_height
        self.depth = props.sink_cabinet_depth
        self.carcass = carcass_simple.INSERT_Sink_Carcass()
        self.add_empty_opening = True
        self.exterior = frameless_exteriors.INSERT_Base_Double_Door_with_2_False_Front()
        self.exterior.prompts = {'Half Overlay Top':False}
        self.interior = cabinet_interiors.INSERT_Shelves()
        self.interior.shelf_qty = 0
         
class PRODUCT_1_Door_1_Drawer_Base(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = BASE_CATEGORY_NAME
        self.width = props.width_1_door
        self.height = props.base_cabinet_height
        self.depth = props.base_cabinet_depth
        self.carcass = carcass_simple.INSERT_Base_Carcass()
        self.splitter = frameless_splitters.INSERT_2_Vertical_Openings()
        self.splitter.opening_1_height = sn_unit.millimeter(float(props.top_drawer_front_height)) - sn_unit.inch(0.58)
        self.splitter.exterior_1 = frameless_exteriors.INSERT_1_Drawer()
        self.splitter.exterior_1.prompts = {'Half Overlay Bottom':True}
        self.splitter.exterior_2 = frameless_exteriors.INSERT_Base_Single_Door()
        self.splitter.exterior_2.sink_mounted = False
        self.splitter.exterior_2.prompts = {'Half Overlay Top':True}
        self.splitter.interior_2 = cabinet_interiors.INSERT_Shelves()
        self.splitter.interior_2.shelf_qty = int_props.base_adj_shelf_qty

class PRODUCT_2_Door_2_Drawer_Base(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = BASE_CATEGORY_NAME
        self.width = props.width_2_door
        self.height = props.base_cabinet_height
        self.depth = props.base_cabinet_depth
        self.carcass = carcass_simple.INSERT_Base_Carcass()
        self.splitter = frameless_splitters.INSERT_2_Vertical_Openings()
        self.splitter.opening_1_height = sn_unit.millimeter(float(props.top_drawer_front_height)) - sn_unit.inch(0.58)
        self.splitter.exterior_1 = frameless_exteriors.INSERT_Horizontal_Drawers()
        self.splitter.exterior_1.prompts = {'Half Overlay Bottom':True}
        self.splitter.exterior_2 = frameless_exteriors.INSERT_Base_Double_Door()
        self.splitter.exterior_2.sink_mounted = False
        self.splitter.exterior_2.prompts = {'Half Overlay Top':True}
        self.splitter.interior_2 = cabinet_interiors.INSERT_Shelves()
        self.splitter.interior_2.shelf_qty = int_props.base_adj_shelf_qty

class PRODUCT_2_Door_1_Drawer_Base(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = BASE_CATEGORY_NAME
        self.width = props.width_2_door
        self.height = props.base_cabinet_height
        self.depth = props.base_cabinet_depth
        self.carcass = carcass_simple.INSERT_Base_Carcass()
        self.splitter = frameless_splitters.INSERT_2_Vertical_Openings()
        self.splitter.opening_1_height = sn_unit.millimeter(float(props.top_drawer_front_height)) - sn_unit.inch(0.58)
        self.splitter.exterior_1 = frameless_exteriors.INSERT_1_Drawer()
        self.splitter.exterior_1.prompts = {'Half Overlay Bottom':True}
        self.splitter.exterior_2 = frameless_exteriors.INSERT_Base_Double_Door()
        self.splitter.exterior_2.sink_mounted = False
        self.splitter.exterior_2.prompts = {'Half Overlay Top':True}
        self.splitter.interior_2 = cabinet_interiors.INSERT_Shelves()
        self.splitter.interior_2.shelf_qty = int_props.base_adj_shelf_qty

class PRODUCT_Microwave_2_Door_Base(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = BASE_CATEGORY_NAME
        self.width = props.width_2_door
        self.height = props.base_cabinet_height
        self.depth = props.base_cabinet_depth
        self.carcass = carcass_simple.INSERT_Base_Carcass()
        self.splitter = frameless_splitters.INSERT_2_Vertical_Openings()
        self.splitter.exterior_1 = appliance_inserts.INSERT_Microwave_Generic()
        self.splitter.opening_2_height = sn_unit.inch(11.85)
        self.splitter.exterior_2 = frameless_exteriors.INSERT_Base_Double_Door()
        self.splitter.exterior_2.sink_mounted = False
        self.splitter.exterior_2.prompts = {'Half Overlay Top':False}
        self.splitter.interior_2 = cabinet_interiors.INSERT_Shelves()
        self.splitter.interior_2.shelf_qty = 0
 
class PRODUCT_Microwave_1_Drawer_Base(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = BASE_CATEGORY_NAME
        self.width = props.width_2_door
        self.height = props.base_cabinet_height
        self.depth = props.base_cabinet_depth
        self.carcass = carcass_simple.INSERT_Base_Carcass()
        self.splitter = frameless_splitters.INSERT_2_Vertical_Openings()
        self.splitter.exterior_1 = appliance_inserts.INSERT_Microwave_Generic()
        self.splitter.opening_2_height = sn_unit.inch(11.85)
        self.splitter.exterior_2 = frameless_exteriors.INSERT_1_Drawer()

class PRODUCT_Dishwasher_Base(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = BASE_CATEGORY_NAME
        self.width = props.width_dishwasher
        self.height = props.base_cabinet_height
        self.depth = props.base_cabinet_depth
        self.carcass = carcass_simple.INSERT_Appliance_Carcass()
        self.add_empty_opening = True
        self.exterior = appliance_inserts.INSERT_Dishwasher_Generic()

class PRODUCT_Wine_Cooler_Base(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = BASE_CATEGORY_NAME
        self.width = props.width_wine_cooler
        self.height = props.base_cabinet_height
        self.depth = props.base_cabinet_depth
        self.carcass = carcass_simple.INSERT_Appliance_Carcass()
        self.add_empty_opening = True
        self.exterior = appliance_inserts.INSERT_Wine_Cooler_Generic()

class PRODUCT_4_Door_Oven_Tall(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = TALL_CATEGORY_NAME
        self.width = props.width_2_door
        self.height = props.tall_cabinet_height
        self.depth = props.tall_cabinet_depth
        self.carcass = carcass_simple.INSERT_Tall_Carcass()
        self.splitter = frameless_splitters.INSERT_3_Vertical_Openings()
        self.splitter.opening_1_height = sn_unit.inch(29.49)
        self.splitter.interior_1 = cabinet_interiors.INSERT_Shelves()
        self.splitter.exterior_1 = frameless_exteriors.INSERT_Upper_Double_Door()
        self.splitter.exterior_1.sink_mounted = False
        self.splitter.exterior_1.prompts = {'Half Overlay Top':False}
        self.splitter.interior_1 = cabinet_interiors.INSERT_Shelves()
        self.splitter.opening_2_height = sn_unit.inch(30.75)
        self.splitter.exterior_2 = appliance_inserts.INSERT_Wall_Oven_Generic()
        self.splitter.interior_3 = cabinet_interiors.INSERT_Shelves()
        self.splitter.exterior_3 = frameless_exteriors.INSERT_Base_Double_Door()
        self.splitter.exterior_3.sink_mounted = False
        self.splitter.exterior_3.prompts = {'Half Overlay Top':False}
        self.splitter.interior_3 = cabinet_interiors.INSERT_Shelves()

class PRODUCT_4_Door_Micro_and_Oven_Tall(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = TALL_CATEGORY_NAME
        self.width = props.width_2_door
        self.height = props.tall_cabinet_height
        self.depth = props.tall_cabinet_depth
        self.carcass = carcass_simple.INSERT_Tall_Carcass()
        self.splitter = frameless_splitters.INSERT_4_Vertical_Openings()
        self.splitter.opening_1_height = sn_unit.inch(19.41)
        self.splitter.interior_1 = cabinet_interiors.INSERT_Shelves()
        self.splitter.exterior_1 = frameless_exteriors.INSERT_Upper_Double_Door()
        self.splitter.exterior_1.sink_mounted = False
        self.splitter.exterior_1.prompts = {'Half Overlay Top':False}
        self.splitter.interior_1 = cabinet_interiors.INSERT_Shelves()
        self.splitter.opening_2_height = sn_unit.inch(19.41)
        self.splitter.exterior_2 = appliance_inserts.INSERT_Microwave_Generic()
        self.splitter.exterior_3 = appliance_inserts.INSERT_Wall_Oven_Generic()
        self.splitter.opening_4_height = sn_unit.inch(19.41)
        self.splitter.interior_4 = cabinet_interiors.INSERT_Shelves()
        self.splitter.exterior_4 = frameless_exteriors.INSERT_Base_Double_Door()
        self.splitter.exterior_4.sink_mounted = False
        self.splitter.exterior_4.prompts = {'Half Overlay Top':False}
        self.splitter.interior_4 = cabinet_interiors.INSERT_Shelves()

class PRODUCT_Refrigerator_Tall(cabinets.Refrigerator):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = TALL_CATEGORY_NAME
        self.width = props.width_2_door
        self.height = props.tall_cabinet_height
        self.depth = props.tall_cabinet_depth
        self.carcass = carcass_simple.INSERT_Tall_Carcass()
        self.carcass.prompts = {'Remove Bottom':True}
        self.splitter = frameless_splitters.INSERT_2_Vertical_Openings()
        self.splitter.opening_1_height = sn_unit.inch(23.19)
        self.splitter.exterior_1 = frameless_exteriors.INSERT_Upper_Double_Door()
        self.splitter.exterior_1.sink_mounted = False
        self.splitter.exterior_1.prompts = {'Half Overlay Top':False}
        self.splitter.interior_1 = cabinet_interiors.INSERT_Shelves()
        
class PRODUCT_1_Door_Tall(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = TALL_CATEGORY_NAME
        self.width = props.width_1_door
        self.height = props.tall_cabinet_height
        self.depth = props.tall_cabinet_depth
        self.carcass = carcass_simple.INSERT_Tall_Carcass()
        self.add_empty_opening = True
        self.exterior = frameless_exteriors.INSERT_Tall_Single_Door()
        self.exterior.sink_mounted = False
        self.exterior.prompts = {'Half Overlay Top':False}
        self.interior = cabinet_interiors.INSERT_Shelves()
        self.interior.shelf_qty = int_props.tall_adj_shelf_qty
        
class PRODUCT_2_Door_Tall(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = TALL_CATEGORY_NAME
        self.width = props.width_2_door
        self.height = props.tall_cabinet_height
        self.depth = props.tall_cabinet_depth
        self.carcass = carcass_simple.INSERT_Tall_Carcass()
        self.add_empty_opening = True
        self.exterior = frameless_exteriors.INSERT_Tall_Double_Door()
        self.exterior.sink_mounted = False
        self.exterior.prompts = {'Half Overlay Top':False}
        self.interior = cabinet_interiors.INSERT_Shelves()
        self.interior.shelf_qty = int_props.tall_adj_shelf_qty
        
class PRODUCT_1_Double_Door_Tall(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = TALL_CATEGORY_NAME
        self.width = props.width_1_door
        self.height = props.tall_cabinet_height
        self.depth = props.tall_cabinet_depth
        self.carcass = carcass_simple.INSERT_Tall_Carcass()
        self.splitter = frameless_splitters.INSERT_2_Vertical_Openings()
        self.splitter.opening_1_height = sn_unit.inch(44.6)
        self.splitter.interior_1 = cabinet_interiors.INSERT_Shelves()
        self.splitter.exterior_1 = frameless_exteriors.INSERT_Upper_Single_Door()
        self.splitter.exterior_1.sink_mounted = False
        self.splitter.exterior_1.prompts = {'Half Overlay Bottom':True}
        self.splitter.interior_1 = cabinet_interiors.INSERT_Shelves()
        self.splitter.exterior_2 = frameless_exteriors.INSERT_Base_Single_Door()
        self.splitter.exterior_2.sink_mounted = False
        self.splitter.exterior_2.prompts = {'Half Overlay Top':True}
        self.splitter.interior_2 = cabinet_interiors.INSERT_Shelves()
   
class PRODUCT_2_Double_Door_Tall(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = TALL_CATEGORY_NAME
        self.width = props.width_2_door
        self.height = props.tall_cabinet_height
        self.depth = props.tall_cabinet_depth
        self.carcass = carcass_simple.INSERT_Tall_Carcass()
        self.splitter = frameless_splitters.INSERT_2_Vertical_Openings()
        self.splitter.opening_1_height = sn_unit.inch(44.6)
        self.splitter.interior_1 = cabinet_interiors.INSERT_Shelves()
        self.splitter.exterior_1 = frameless_exteriors.INSERT_Upper_Double_Door()
        self.splitter.exterior_1.sink_mounted = False
        self.splitter.exterior_1.prompts = {'Half Overlay Bottom':True}
        self.splitter.interior_1 = cabinet_interiors.INSERT_Shelves()
        self.splitter.exterior_2 = frameless_exteriors.INSERT_Base_Double_Door()
        self.splitter.exterior_2.sink_mounted = False
        self.splitter.exterior_2.prompts = {'Half Overlay Top':True}
        self.splitter.interior_2 = cabinet_interiors.INSERT_Shelves()
        
class PRODUCT_2_Door_2_Drawer_Tall(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = TALL_CATEGORY_NAME
        self.width = props.width_2_door
        self.height = props.tall_cabinet_height
        self.depth = props.tall_cabinet_depth
        self.carcass = carcass_simple.INSERT_Tall_Carcass()
        self.splitter = frameless_splitters.INSERT_2_Vertical_Openings()
        self.splitter.opening_2_height = sn_unit.inch(21.93)  #18 H
        self.splitter.exterior_1 = frameless_exteriors.INSERT_Tall_Double_Door()
        self.splitter.exterior_1.sink_mounted = False
        self.splitter.exterior_1.prompts = {'Half Overlay Bottom':True}
        self.splitter.interior_1 = cabinet_interiors.INSERT_Shelves()
        self.splitter.exterior_2 = frameless_exteriors.INSERT_2_Drawer_Stack()
        self.splitter.exterior_2.prompts = {'Half Overlay Top':True}

class PRODUCT_2_Door_3_Drawer_Tall(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = TALL_CATEGORY_NAME
        self.width = props.width_2_door
        self.height = props.tall_cabinet_height
        self.depth = props.tall_cabinet_depth
        self.carcass = carcass_simple.INSERT_Tall_Carcass()
        self.splitter = frameless_splitters.INSERT_2_Vertical_Openings()
        self.splitter.opening_2_height = sn_unit.inch(21.93)  #18H
        self.splitter.exterior_1 = frameless_exteriors.INSERT_Tall_Double_Door()
        self.splitter.exterior_1.sink_mounted = False
        self.splitter.exterior_1.prompts = {'Half Overlay Bottom':True}
        self.splitter.interior_1 = cabinet_interiors.INSERT_Shelves()
        self.splitter.exterior_2 = frameless_exteriors.INSERT_3_Drawer_Stack()
        self.splitter.exterior_2.prompts = {'Half Overlay Top':True}

class PRODUCT_1_Door_Upper(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = UPPER_CATEGORY_NAME
        self.width = props.width_1_door
        self.height = props.upper_cabinet_height
        self.depth = props.upper_cabinet_depth
        self.mirror_z = True
        self.height_above_floor = props.height_above_floor
        self.carcass = carcass_simple.INSERT_Upper_Carcass()
        self.add_empty_opening = True
        self.exterior = frameless_exteriors.INSERT_Upper_Single_Door()
        self.exterior.sink_mounted = False
        self.exterior.prompts = {'Half Overlay Top':False}
        self.interior = cabinet_interiors.INSERT_Shelves()
        self.interior.shelf_qty = int_props.upper_adj_shelf_qty
        
class PRODUCT_2_Door_Upper(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = UPPER_CATEGORY_NAME
        self.width = props.width_2_door
        self.height = props.upper_cabinet_height
        self.depth = props.upper_cabinet_depth
        self.mirror_z = True
        self.height_above_floor = props.height_above_floor
        self.carcass = carcass_simple.INSERT_Upper_Carcass()
        self.add_empty_opening = True
        self.exterior = frameless_exteriors.INSERT_Upper_Double_Door()
        self.exterior.sink_mounted = False
        self.exterior.prompts = {'Half Overlay Top':False}
        self.interior = cabinet_interiors.INSERT_Shelves()
        self.interior.shelf_qty = int_props.upper_adj_shelf_qty

class PRODUCT_1_Double_Door_Upper(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = UPPER_CATEGORY_NAME
        self.width = props.width_1_door
        self.height = props.upper_cabinet_height
        self.depth = props.upper_cabinet_depth
        self.mirror_z = True
        self.height_above_floor = props.height_above_floor
        self.carcass = carcass_simple.INSERT_Upper_Carcass()
        self.splitter = frameless_splitters.INSERT_2_Vertical_Openings()
        self.splitter.opening_1_height = sn_unit.inch(18.15)
        self.splitter.exterior_1 = frameless_exteriors.INSERT_Upper_Single_Door()
        self.splitter.exterior_1.sink_mounted = False
        self.splitter.exterior_1.prompts = {'Half Overlay Bottom':True}
        self.splitter.interior_1 = cabinet_interiors.INSERT_Shelves()
        self.splitter.exterior_2 = frameless_exteriors.INSERT_Upper_Single_Door()
        self.splitter.exterior_2.sink_mounted = False
        self.splitter.exterior_2.prompts = {'Half Overlay Top':True}
        self.splitter.interior_2 = cabinet_interiors.INSERT_Shelves()

class PRODUCT_2_Double_Door_Upper(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = UPPER_CATEGORY_NAME
        self.width = props.width_2_door
        self.height = props.upper_cabinet_height
        self.depth = props.upper_cabinet_depth
        self.mirror_z = True
        self.height_above_floor = props.height_above_floor
        self.carcass = carcass_simple.INSERT_Upper_Carcass()
        self.splitter = frameless_splitters.INSERT_2_Vertical_Openings()
        self.splitter.opening_1_height = sn_unit.inch(18.15)
        self.splitter.exterior_1 = frameless_exteriors.INSERT_Upper_Double_Door()
        self.splitter.exterior_1.sink_mounted = False
        self.splitter.exterior_1.prompts = {'Half Overlay Bottom':True}
        self.splitter.interior_1 = cabinet_interiors.INSERT_Shelves()
        self.splitter.exterior_2 = frameless_exteriors.INSERT_Upper_Double_Door()
        self.splitter.exterior_2.sink_mounted = False
        self.splitter.exterior_2.prompts = {'Half Overlay Top':True}
        self.splitter.interior_2 = cabinet_interiors.INSERT_Shelves()

class PRODUCT_Microwave_2_Door_Upper(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = UPPER_CATEGORY_NAME
        self.width = props.width_2_door
        self.height = props.upper_cabinet_height
        self.depth = props.upper_cabinet_depth
        self.mirror_z = True
        self.height_above_floor = props.height_above_floor
        self.carcass = carcass_simple.INSERT_Upper_Carcass()
        self.splitter = frameless_splitters.INSERT_2_Vertical_Openings()
        self.splitter.opening_1_height = sn_unit.inch(18.15)
        self.splitter.exterior_1 = frameless_exteriors.INSERT_Upper_Double_Door()
        self.splitter.exterior_1.sink_mounted = False
        self.splitter.exterior_1.prompts = {'Half Overlay Top':False}
        self.splitter.interior_1 = cabinet_interiors.INSERT_Shelves()
        self.splitter.exterior_2 = appliance_inserts.INSERT_Microwave_Generic()

class PRODUCT_2_Door_Upper_with_Microwave(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = UPPER_CATEGORY_NAME
        self.width = sn_unit.inch(30)
        self.height = str(float(props.upper_cabinet_height) - 512)
        self.depth = props.upper_cabinet_depth
        self.mirror_z = True
        self.height_above_floor = props.height_above_floor
        self.carcass = carcass_simple.INSERT_Upper_Carcass()
        self.add_empty_opening = True
        self.exterior = frameless_exteriors.INSERT_Upper_Double_Door()
        self.exterior.sink_mounted = False
        self.exterior.prompts = {'Half Overlay Top':False}
        self.interior = cabinet_interiors.INSERT_Shelves()
        self.add_microwave = True
         
class PRODUCT_2_Door_Upper_with_Vent(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = UPPER_CATEGORY_NAME
        self.width = props.width_2_door
        self.height = str(float(props.upper_cabinet_height) - 512)
        self.depth = props.upper_cabinet_depth
        self.mirror_z = True
        self.height_above_floor = props.height_above_floor
        self.carcass = carcass_simple.INSERT_Upper_Carcass()
        self.add_empty_opening = True
        self.exterior = frameless_exteriors.INSERT_Upper_Double_Door()
        self.exterior.sink_mounted = False
        self.exterior.prompts = {'Half Overlay Top':False}
        self.interior = cabinet_interiors.INSERT_Shelves()
        self.add_vent_hood = True
        
class PRODUCT_2_Door_2_Drawer_Upper(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = UPPER_CATEGORY_NAME
        self.width = props.width_2_door
        self.height = props.upper_cabinet_height
        self.depth = props.upper_cabinet_depth
        self.mirror_z = True
        self.height_above_floor = props.height_above_floor
        self.carcass = carcass_simple.INSERT_Upper_Carcass()
        self.splitter = frameless_splitters.INSERT_2_Vertical_Openings()
        self.splitter.exterior_1 = frameless_exteriors.INSERT_Upper_Double_Door()
        self.splitter.exterior_1.sink_mounted = False
        self.splitter.exterior_1.prompts = {'Half Overlay Bottom':True}
        self.splitter.interior_1 = cabinet_interiors.INSERT_Shelves()
        self.splitter.opening_2_height = sn_unit.inch(19.41)  # 16H
        self.splitter.exterior_2 = frameless_exteriors.INSERT_2_Drawer_Stack()
        self.splitter.exterior_2.prompts = {'Half Overlay Top':True}
        
class PRODUCT_1_Drawer_Base(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = DRAWER_CATEGORY_NAME
        self.width = props.width_drawer
        self.height = props.base_cabinet_height
        self.depth = props.base_cabinet_depth
        self.carcass = carcass_simple.INSERT_Base_Carcass()
        self.add_empty_opening = True
        self.exterior = frameless_exteriors.INSERT_1_Drawer()

class PRODUCT_2_Drawer_Base(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = DRAWER_CATEGORY_NAME
        self.width = props.width_drawer
        self.height = props.base_cabinet_height
        self.depth = props.base_cabinet_depth
        self.carcass = carcass_simple.INSERT_Base_Carcass()
        self.add_empty_opening = True
        self.exterior = frameless_exteriors.INSERT_2_Drawer_Stack()
        if not props.equal_drawer_stack_heights:
            self.exterior.top_drawer_front_height = props.top_drawer_front_height

class PRODUCT_3_Drawer_Base(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = DRAWER_CATEGORY_NAME
        self.width = props.width_drawer
        self.height = props.base_cabinet_height
        self.depth = props.base_cabinet_depth
        self.carcass = carcass_simple.INSERT_Base_Carcass()
        self.add_empty_opening = True
        self.exterior = frameless_exteriors.INSERT_3_Drawer_Stack()
        if not props.equal_drawer_stack_heights:
            self.exterior.top_drawer_front_height = props.top_drawer_front_height
            
class PRODUCT_4_Drawer_Base(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = DRAWER_CATEGORY_NAME
        self.width = props.width_drawer
        self.height = props.base_cabinet_height
        self.depth = props.base_cabinet_depth
        self.carcass = carcass_simple.INSERT_Base_Carcass()
        self.add_empty_opening = True
        self.exterior = frameless_exteriors.INSERT_4_Drawer_Stack()
        if not props.equal_drawer_stack_heights:
            self.exterior.top_drawer_front_height = props.top_drawer_front_height
            
class PRODUCT_1_Drawer_Suspended(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = DRAWER_CATEGORY_NAME
        self.width = props.width_drawer
        self.height = props.suspended_cabinet_height
        self.depth = props.suspended_cabinet_depth
        self.mirror_z = True
        self.carcass = carcass_simple.INSERT_Suspended_Carcass()
        self.add_empty_opening = True
        self.height_above_floor = props.base_cabinet_height
        self.exterior = frameless_exteriors.INSERT_1_Drawer()
        
class PRODUCT_2_Drawer_Suspended(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = DRAWER_CATEGORY_NAME
        self.width = props.width_drawer * 2
        self.height = props.suspended_cabinet_height
        self.depth = props.suspended_cabinet_depth
        self.mirror_z = True
        self.carcass = carcass_simple.INSERT_Suspended_Carcass()
        self.add_empty_opening = True
        self.height_above_floor = props.base_cabinet_height
        self.exterior = frameless_exteriors.INSERT_Horizontal_Drawers()

class PRODUCT_1_Door_Blind_Left_Corner_Base(cabinets.Blind_Corner):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = BLIND_CORNER_CATEGORY_NAME
        self.blind_side = "Left"
        self.width = props.base_width_blind
        self.height = props.base_cabinet_height
        self.depth = props.base_cabinet_depth
        self.carcass = carcass_simple.INSERT_Base_Carcass()
        self.add_empty_opening = True
        self.exterior = frameless_exteriors.INSERT_Base_Single_Door()
        self.exterior.sink_mounted = False
        self.exterior.prompts = {'Half Overlay Top':False}
        self.interior = cabinet_interiors.INSERT_Shelves()
        self.interior.shelf_qty = int_props.base_adj_shelf_qty

class PRODUCT_1_Door_Blind_Right_Corner_Base(cabinets.Blind_Corner):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = BLIND_CORNER_CATEGORY_NAME
        self.blind_side = "Right"
        self.width = props.base_width_blind
        self.height = props.base_cabinet_height
        self.depth = props.base_cabinet_depth
        self.carcass = carcass_simple.INSERT_Base_Carcass()
        self.add_empty_opening = True
        self.exterior = frameless_exteriors.INSERT_Base_Single_Door()
        self.exterior.sink_mounted = False
        self.exterior.prompts = {'Half Overlay Top':False}
        self.interior = cabinet_interiors.INSERT_Shelves()
        self.interior.shelf_qty = int_props.base_adj_shelf_qty

class PRODUCT_1_Door_Blind_Left_Corner_Tall(cabinets.Blind_Corner):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = BLIND_CORNER_CATEGORY_NAME
        self.blind_side = "Left"
        self.width = props.tall_width_blind
        self.height = props.tall_cabinet_height
        self.depth = props.tall_cabinet_depth
        self.carcass = carcass_simple.INSERT_Tall_Carcass()
        self.add_empty_opening = True
        self.exterior = frameless_exteriors.INSERT_Tall_Single_Door()
        self.exterior.sink_mounted = False
        self.exterior.prompts = {'Half Overlay Top':False}
        self.interior = cabinet_interiors.INSERT_Shelves()
        self.interior.shelf_qty = int_props.tall_adj_shelf_qty

class PRODUCT_1_Door_Blind_Right_Corner_Tall(cabinets.Blind_Corner):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = BLIND_CORNER_CATEGORY_NAME
        self.blind_side = "Right"
        self.width = props.tall_width_blind
        self.height = props.tall_cabinet_height
        self.depth = props.tall_cabinet_depth
        self.carcass = carcass_simple.INSERT_Tall_Carcass()
        self.add_empty_opening = True
        self.exterior = frameless_exteriors.INSERT_Tall_Single_Door()
        self.exterior.sink_mounted = False
        self.exterior.prompts = {'Half Overlay Top':False}
        self.interior = cabinet_interiors.INSERT_Shelves()
        self.interior.shelf_qty = int_props.tall_adj_shelf_qty

class PRODUCT_1_Door_Blind_Left_Corner_Upper(cabinets.Blind_Corner):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = BLIND_CORNER_CATEGORY_NAME
        self.blind_side = "Left"
        self.height_above_floor = props.height_above_floor
        self.mirror_z = True
        self.width = props.upper_width_blind
        self.height = props.upper_cabinet_height
        self.depth = props.upper_cabinet_depth
        self.carcass = carcass_simple.INSERT_Upper_Carcass()
        self.add_empty_opening = True
        self.exterior = frameless_exteriors.INSERT_Upper_Single_Door()
        self.exterior.sink_mounted = False
        self.exterior.prompts = {'Half Overlay Top':False}
        self.interior = cabinet_interiors.INSERT_Shelves()
        self.interior.shelf_qty = int_props.upper_adj_shelf_qty

class PRODUCT_1_Door_Blind_Right_Corner_Upper(cabinets.Blind_Corner):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = BLIND_CORNER_CATEGORY_NAME
        self.blind_side = "Right"
        self.height_above_floor = props.height_above_floor
        self.mirror_z = True
        self.width = props.upper_width_blind
        self.height = props.upper_cabinet_height
        self.depth = props.upper_cabinet_depth
        self.carcass = carcass_simple.INSERT_Upper_Carcass()
        self.add_empty_opening = True
        self.exterior = frameless_exteriors.INSERT_Upper_Single_Door()
        self.exterior.sink_mounted = False
        self.exterior.prompts = {'Half Overlay Top':False}
        self.interior = cabinet_interiors.INSERT_Shelves()
        self.interior.shelf_qty = int_props.upper_adj_shelf_qty

class PRODUCT_2_Door_Blind_Left_Corner_Base(cabinets.Blind_Corner):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = BLIND_CORNER_CATEGORY_NAME
        self.blind_side = "Left"
        self.width = props.base_width_blind
        self.height = props.base_cabinet_height
        self.depth = props.base_cabinet_depth
        self.carcass = carcass_simple.INSERT_Base_Carcass()
        self.add_empty_opening = True
        self.exterior = frameless_exteriors.INSERT_Base_Double_Door()
        self.exterior.sink_mounted = False
        self.interior = cabinet_interiors.INSERT_Shelves()
        self.interior.shelf_qty = int_props.base_adj_shelf_qty

class PRODUCT_2_Door_Blind_Right_Corner_Base(cabinets.Blind_Corner):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = BLIND_CORNER_CATEGORY_NAME
        self.blind_side = "Right"
        self.width = props.base_width_blind
        self.height = props.base_cabinet_height
        self.depth = props.base_cabinet_depth
        self.carcass = carcass_simple.INSERT_Base_Carcass()
        self.add_empty_opening = True
        self.exterior = frameless_exteriors.INSERT_Base_Double_Door()
        self.exterior.sink_mounted = False
        self.exterior.prompts = {'Half Overlay Top':False}
        self.interior = cabinet_interiors.INSERT_Shelves()
        self.interior.shelf_qty = int_props.base_adj_shelf_qty

class PRODUCT_2_Door_Blind_Left_Corner_Tall(cabinets.Blind_Corner):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = BLIND_CORNER_CATEGORY_NAME
        self.blind_side = "Left"
        self.width = props.tall_width_blind
        self.height = props.tall_cabinet_height
        self.depth = props.tall_cabinet_depth
        self.carcass = carcass_simple.INSERT_Tall_Carcass()
        self.add_empty_opening = True
        self.exterior = frameless_exteriors.INSERT_Tall_Double_Door()
        self.exterior.sink_mounted = False
        self.exterior.prompts = {'Half Overlay Top':False}
        self.interior = cabinet_interiors.INSERT_Shelves()
        self.interior.shelf_qty = int_props.tall_adj_shelf_qty

class PRODUCT_2_Door_Blind_Right_Corner_Tall(cabinets.Blind_Corner):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = BLIND_CORNER_CATEGORY_NAME
        self.blind_side = "Right"
        self.width = props.tall_width_blind
        self.height = props.tall_cabinet_height
        self.depth = props.tall_cabinet_depth
        self.carcass = carcass_simple.INSERT_Tall_Carcass()
        self.add_empty_opening = True
        self.exterior = frameless_exteriors.INSERT_Tall_Double_Door()
        self.exterior.sink_mounted = False
        self.exterior.prompts = {'Half Overlay Top':False}
        self.interior = cabinet_interiors.INSERT_Shelves()
        self.interior.shelf_qty = int_props.tall_adj_shelf_qty

class PRODUCT_2_Door_Blind_Left_Corner_Upper(cabinets.Blind_Corner):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = BLIND_CORNER_CATEGORY_NAME
        self.blind_side = "Left"
        self.height_above_floor = props.height_above_floor
        self.mirror_z = True
        self.width = props.upper_width_blind
        self.height = props.upper_cabinet_height
        self.depth = props.upper_cabinet_depth
        self.carcass = carcass_simple.INSERT_Upper_Carcass()
        self.add_empty_opening = True
        self.exterior = frameless_exteriors.INSERT_Upper_Double_Door()
        self.exterior.sink_mounted = False
        self.exterior.prompts = {'Half Overlay Top':False}
        self.interior = cabinet_interiors.INSERT_Shelves()
        self.interior.shelf_qty = int_props.upper_adj_shelf_qty

class PRODUCT_2_Door_Blind_Right_Corner_Upper(cabinets.Blind_Corner):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = BLIND_CORNER_CATEGORY_NAME
        self.blind_side = "Right"
        self.height_above_floor = props.height_above_floor
        self.mirror_z = True
        self.width = props.upper_width_blind
        self.height = props.upper_cabinet_height
        self.depth = props.upper_cabinet_depth
        self.carcass = carcass_simple.INSERT_Upper_Carcass()
        self.add_empty_opening = True
        self.exterior = frameless_exteriors.INSERT_Upper_Double_Door()
        self.exterior.sink_mounted = False
        self.exterior.prompts = {'Half Overlay Top':False}
        self.interior = cabinet_interiors.INSERT_Shelves()
        self.interior.shelf_qty = int_props.upper_adj_shelf_qty

class PRODUCT_1_Door_1_Drawer_Blind_Right_Corner_Base(cabinets.Blind_Corner):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = BLIND_CORNER_CATEGORY_NAME
        self.blind_side = "Right"
        self.width = props.base_width_blind
        self.height = props.base_cabinet_height
        self.depth = props.base_cabinet_depth
        self.carcass = carcass_simple.INSERT_Base_Carcass()
        self.splitter = frameless_splitters.INSERT_2_Vertical_Openings()
        self.splitter.partition_right_1 = True
        self.splitter.opening_1_height = sn_unit.millimeter(float(props.top_drawer_front_height)) - sn_unit.inch(0.58)
        self.splitter.exterior_1 = frameless_exteriors.INSERT_1_Drawer()
        self.splitter.exterior_1.prompts = {'Half Overlay Bottom':True}
        self.splitter.exterior_2 = frameless_exteriors.INSERT_Base_Single_Door()
        self.splitter.exterior_2.sink_mounted = False
        self.splitter.exterior_2.prompts = {'Half Overlay Top':True}
        self.splitter.interior_2 = cabinet_interiors.INSERT_Shelves()
        self.splitter.interior_2.shelf_qty = int_props.base_adj_shelf_qty
        
class PRODUCT_1_Door_1_Drawer_Blind_Left_Corner_Base(cabinets.Blind_Corner):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = BLIND_CORNER_CATEGORY_NAME
        self.blind_side = "Left"
        self.width = props.base_width_blind
        self.height = props.base_cabinet_height
        self.depth = props.base_cabinet_depth
        self.carcass = carcass_simple.INSERT_Base_Carcass()
        self.splitter = frameless_splitters.INSERT_2_Vertical_Openings()
        self.splitter.partition_left_1 = True
        self.splitter.opening_1_height = sn_unit.millimeter(float(props.top_drawer_front_height)) - sn_unit.inch(0.58)
        self.splitter.exterior_1 = frameless_exteriors.INSERT_1_Drawer()
        self.splitter.exterior_1.prompts = {'Half Overlay Bottom':True}
        self.splitter.exterior_2 = frameless_exteriors.INSERT_Base_Single_Door()
        self.splitter.exterior_2.sink_mounted = False
        self.splitter.exterior_2.prompts = {'Half Overlay Top':True}
        self.splitter.interior_2 = cabinet_interiors.INSERT_Shelves()
        self.splitter.interior_2.shelf_qty = int_props.base_adj_shelf_qty
        
class PRODUCT_2_Door_2_Drawer_Blind_Right_Corner_Base(cabinets.Blind_Corner):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = BLIND_CORNER_CATEGORY_NAME
        self.blind_side = "Right"
        self.width = props.base_width_blind
        self.height = props.base_cabinet_height
        self.depth = props.base_cabinet_depth
        self.carcass = carcass_simple.INSERT_Base_Carcass()
        self.splitter = frameless_splitters.INSERT_2_Vertical_Openings()
        self.splitter.partition_right_1 = True
        self.splitter.opening_1_height = sn_unit.millimeter(float(props.top_drawer_front_height)) - sn_unit.inch(0.58)
        self.splitter.exterior_1 = frameless_exteriors.INSERT_Horizontal_Drawers()
        self.splitter.exterior_1.prompts = {'Half Overlay Bottom':True}
        self.splitter.exterior_2 = frameless_exteriors.INSERT_Base_Double_Door()
        self.splitter.exterior_2.sink_mounted = False
        self.splitter.exterior_2.prompts = {'Half Overlay Top':True}
        self.splitter.interior_2 = cabinet_interiors.INSERT_Shelves()
        self.splitter.interior_2.shelf_qty = int_props.base_adj_shelf_qty
        
class PRODUCT_2_Door_2_Drawer_Blind_Left_Corner_Base(cabinets.Blind_Corner):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = BLIND_CORNER_CATEGORY_NAME
        self.blind_side = "Left"
        self.width = props.base_width_blind
        self.height = props.base_cabinet_height
        self.depth = props.base_cabinet_depth
        self.carcass = carcass_simple.INSERT_Base_Carcass()
        self.splitter = frameless_splitters.INSERT_2_Vertical_Openings()
        self.splitter.partition_left_1 = True
        self.splitter.opening_1_height = sn_unit.millimeter(float(props.top_drawer_front_height)) - sn_unit.inch(0.58)
        self.splitter.exterior_1 = frameless_exteriors.INSERT_Horizontal_Drawers()
        self.splitter.exterior_1.prompts = {'Half Overlay Bottom':True}
        self.splitter.exterior_2 = frameless_exteriors.INSERT_Base_Double_Door()
        self.splitter.exterior_2.sink_mounted = False
        self.splitter.exterior_2.prompts = {'Half Overlay Top':True}
        self.splitter.interior_2 = cabinet_interiors.INSERT_Shelves()
        self.splitter.interior_2.shelf_qty = int_props.base_adj_shelf_qty

class PRODUCT_Pie_Cut_Corner_Base(cabinets.Inside_Corner):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = INSIDE_CORNER_CATEGORY_NAME
        self.width = props.base_inside_corner_size
        self.height = props.base_cabinet_height
        self.depth = props.base_inside_corner_size
        self.carcass = carcass_simple.INSERT_Base_Inside_Corner_Notched_Carcass()
        self.add_empty_opening = True
        self.exterior = frameless_exteriors.INSERT_Base_Pie_Cut_Door()
        self.interior = cabinet_interiors.INSERT_Shelves()
        self.interior.carcass_type = "Base"
        self.interior.carcass_shape = "NOTCHED"
        self.interior.shelf_qty = int_props.base_adj_shelf_qty
     
class PRODUCT_Pie_Cut_Corner_Upper(cabinets.Inside_Corner):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = INSIDE_CORNER_CATEGORY_NAME
        self.width = props.upper_inside_corner_size
        self.height = props.upper_cabinet_height
        self.depth = props.upper_inside_corner_size
        self.height_above_floor = props.height_above_floor
        self.mirror_z = True
        self.carcass = carcass_simple.INSERT_Upper_Inside_Corner_Notched_Carcass()
        self.add_empty_opening = True
        self.exterior = frameless_exteriors.INSERT_Upper_Pie_Cut_Door()
        self.interior = cabinet_interiors.INSERT_Shelves()
        self.interior.carcass_type = "Upper"
        self.interior.carcass_shape = "NOTCHED"
        self.interior.shelf_qty = int_props.upper_adj_shelf_qty
        
class PRODUCT_1_Door_Diagonal_Corner_Base(cabinets.Inside_Corner):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = INSIDE_CORNER_CATEGORY_NAME
        self.width = props.base_inside_corner_size
        self.height = props.base_cabinet_height
        self.depth = props.base_inside_corner_size
        self.carcass = carcass_simple.INSERT_Base_Inside_Corner_Diagonal_Carcass()
        self.add_empty_opening = True
        self.exterior = frameless_exteriors.INSERT_Base_Single_Door()
        self.exterior.sink_mounted = False
        self.exterior.prompts = {'Half Overlay Top':False}
        self.interior = cabinet_interiors.INSERT_Shelves()
        self.interior.carcass_type = "Base"
        self.interior.carcass_shape = "DIAGONAL"
        self.interior.shelf_qty = int_props.base_adj_shelf_qty
        
class PRODUCT_2_Door_Diagonal_Corner_Base(cabinets.Inside_Corner):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = INSIDE_CORNER_CATEGORY_NAME
        self.width = props.base_inside_corner_size
        self.height = props.base_cabinet_height
        self.depth = props.base_inside_corner_size
        self.carcass = carcass_simple.INSERT_Base_Inside_Corner_Diagonal_Carcass()
        self.add_empty_opening = True
        self.exterior = frameless_exteriors.INSERT_Base_Double_Door()
        self.exterior.sink_mounted = False
        self.exterior.prompts = {'Half Overlay Top':False}
        self.interior = cabinet_interiors.INSERT_Shelves()
        self.interior.carcass_type = "Base"
        self.interior.carcass_shape = "DIAGONAL"
        self.interior.shelf_qty = int_props.base_adj_shelf_qty
        
class PRODUCT_1_Door_Diagonal_Corner_Upper(cabinets.Inside_Corner):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = INSIDE_CORNER_CATEGORY_NAME
        self.width = props.upper_inside_corner_size
        self.height = props.upper_cabinet_height
        self.depth = props.upper_inside_corner_size
        self.height_above_floor = props.height_above_floor
        self.mirror_z = True
        self.carcass = carcass_simple.INSERT_Upper_Inside_Corner_Diagonal_Carcass()
        self.add_empty_opening = True
        self.exterior = frameless_exteriors.INSERT_Upper_Single_Door()
        self.exterior.sink_mounted = False
        self.interior = cabinet_interiors.INSERT_Shelves()
        self.interior.carcass_type = "Upper"
        self.interior.carcass_shape = "DIAGONAL"
        self.interior.shelf_qty = int_props.upper_adj_shelf_qty
        
class PRODUCT_2_Door_Diagonal_Corner_Upper(cabinets.Inside_Corner):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        int_props = cabinet_properties.get_scene_props().interior_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = INSIDE_CORNER_CATEGORY_NAME
        self.width = props.upper_inside_corner_size
        self.height = props.upper_cabinet_height
        self.depth = props.upper_inside_corner_size
        self.height_above_floor = props.height_above_floor
        self.mirror_z = True
        self.carcass = carcass_simple.INSERT_Upper_Inside_Corner_Diagonal_Carcass()
        self.add_empty_opening = True
        self.exterior = frameless_exteriors.INSERT_Upper_Double_Door()
        self.exterior.sink_mounted = False
        self.exterior.prompts = {'Half Overlay Top':False}
        self.interior = cabinet_interiors.INSERT_Shelves()
        self.interior.carcass_type = "Upper"
        self.interior.carcass_shape = "DIAGONAL"
        self.interior.shelf_qty = int_props.upper_adj_shelf_qty

class PRODUCT_Base_Starter(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = STARTER_CATEGORY_NAME
        self.width = props.width_1_door
        self.height = props.base_cabinet_height
        self.depth = props.base_cabinet_depth
        self.carcass = carcass_simple.INSERT_Base_Carcass()
        self.add_empty_opening = True
        self.exterior = None
        self.interior = None

class PRODUCT_Tall_Starter(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = STARTER_CATEGORY_NAME
        self.width = props.width_1_door
        self.height = props.tall_cabinet_height
        self.depth = props.tall_cabinet_depth
        self.carcass = carcass_simple.INSERT_Tall_Carcass()
        self.add_empty_opening = True
        self.exterior = None
        self.interior = None

class PRODUCT_Upper_Starter(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = STARTER_CATEGORY_NAME
        self.width = props.width_1_door
        self.height = props.upper_cabinet_height
        self.depth = props.upper_cabinet_depth
        self.mirror_z = True
        self.carcass = carcass_simple.INSERT_Upper_Carcass()
        self.add_empty_opening = True
        self.exterior = None
        self.interior = None
        self.height_above_floor = props.height_above_floor

class PRODUCT_Sink_Starter(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = STARTER_CATEGORY_NAME
        self.width = props.width_1_door
        self.height = props.sink_cabinet_height
        self.depth = props.sink_cabinet_depth
        self.carcass = carcass_simple.INSERT_Sink_Carcass()
        self.add_empty_opening = True
        self.exterior = None
        self.interior = None

class PRODUCT_Suspended_Starter(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = STARTER_CATEGORY_NAME
        self.width = props.width_1_door
        self.height = props.suspended_cabinet_height
        self.depth = props.suspended_cabinet_depth
        self.carcass = carcass_simple.INSERT_Suspended_Carcass()
        self.mirror_z = True
        self.add_empty_opening = True
        self.exterior = None
        self.interior = None
        self.height_above_floor = props.base_cabinet_height

class PRODUCT_Appliance_Base_Starter(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = STARTER_CATEGORY_NAME
        self.width = props.width_dishwasher
        self.height = props.base_cabinet_height
        self.depth = props.base_cabinet_depth
        self.carcass = carcass_simple.INSERT_Appliance_Carcass()
        self.add_empty_opening = True
        self.exterior = None

class PRODUCT_Tall_Oven_Starter(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = TALL_CATEGORY_NAME
        self.width = sn_unit.inch(30)
        self.height = props.tall_cabinet_height
        self.depth = props.tall_cabinet_depth
        self.carcass = carcass_simple.INSERT_Tall_Carcass()
        self.splitter = frameless_splitters.INSERT_3_Vertical_Openings()
        self.splitter.opening_2_height = sn_unit.inch(30.75)
        self.splitter.exterior_2 = appliance_inserts.INSERT_Wall_Oven_Generic()
        self.splitter.opening_3_height = sn_unit.inch(32.01)

class PRODUCT_Tall_Micowave_Starter(cabinets.Standard):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = TALL_CATEGORY_NAME
        self.width = sn_unit.inch(30)
        self.height = props.tall_cabinet_height
        self.depth = props.tall_cabinet_depth
        self.carcass = carcass_simple.INSERT_Tall_Carcass()
        self.splitter = frameless_splitters.INSERT_3_Vertical_Openings()
        self.splitter.opening_2_height = sn_unit.inch(19.41)
        self.splitter.exterior_2 = appliance_inserts.INSERT_Microwave_Generic()
        self.splitter.opening_3_height = sn_unit.inch(32.01)

class PRODUCT_Island_1_Opening(cabinets.Island):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = STARTER_CATEGORY_NAME
        self.width = props.island_cabinet_width
        self.height = props.island_cabinet_height
        self.depth = props.island_single_chase_depth + props.island_cabinet_depth
        self.carcass = carcass_simple.INSERT_Island_Carcass()
        self.carcass.opening_qty = 1

class PRODUCT_Island_1_Opening_Dbl(cabinets.Island):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = STARTER_CATEGORY_NAME
        self.width = props.island_cabinet_width
        self.height = props.island_cabinet_height
        self.depth = + props.island_double_chase_depth + props.island_cabinet_depth * 2 
        self.carcass = carcass_simple.INSERT_Island_Carcass()
        self.carcass.double_sided = True
        self.carcass.opening_qty = 2
        
class PRODUCT_Island_2_Opening(cabinets.Island):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = STARTER_CATEGORY_NAME
        self.width = props.island_cabinet_width * 2
        self.height = props.island_cabinet_height
        self.depth = props.island_single_chase_depth + props.island_cabinet_depth
        self.carcass = carcass_simple.INSERT_Island_Carcass()
        self.carcass.double_sided = False
        self.carcass.opening_qty = 2

class PRODUCT_Island_2_Opening_Dbl(cabinets.Island):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = STARTER_CATEGORY_NAME
        self.width = props.island_cabinet_width * 2
        self.height = props.island_cabinet_height
        self.depth = + props.island_double_chase_depth + props.island_cabinet_depth * 2 
        self.carcass = carcass_simple.INSERT_Island_Carcass()
        self.carcass.double_sided = True
        self.carcass.opening_qty = 4

class PRODUCT_Island_3_Opening(cabinets.Island):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = STARTER_CATEGORY_NAME
        self.width = props.island_cabinet_width * 3
        self.height = props.island_cabinet_height
        self.depth = props.island_single_chase_depth + props.island_cabinet_depth
        self.carcass = carcass_simple.INSERT_Island_Carcass()
        self.carcass.opening_qty = 3

class PRODUCT_Island_3_Opening_Dbl(cabinets.Island):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = STARTER_CATEGORY_NAME
        self.width = props.island_cabinet_width * 3
        self.height = props.island_cabinet_height
        self.depth = + props.island_double_chase_depth + props.island_cabinet_depth * 2 
        self.carcass = carcass_simple.INSERT_Island_Carcass()
        self.carcass.double_sided = True
        self.carcass.opening_qty = 6

class PRODUCT_Island_4_Opening(cabinets.Island):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = STARTER_CATEGORY_NAME
        self.width = props.island_cabinet_width * 4
        self.height = props.island_cabinet_height
        self.depth = props.island_single_chase_depth + props.island_cabinet_depth
        self.carcass = carcass_simple.INSERT_Island_Carcass()
        self.carcass.opening_qty = 4

class PRODUCT_Island_4_Opening_Dbl(cabinets.Island):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = STARTER_CATEGORY_NAME
        self.width = props.island_cabinet_width * 4
        self.height = props.island_cabinet_height
        self.depth = + props.island_double_chase_depth + props.island_cabinet_depth * 2 
        self.carcass = carcass_simple.INSERT_Island_Carcass()
        self.carcass.double_sided = True
        self.carcass.opening_qty = 8

class PRODUCT_Island_5_Opening(cabinets.Island):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = STARTER_CATEGORY_NAME
        self.width = props.island_cabinet_width * 5
        self.height = props.island_cabinet_height
        self.depth = props.island_single_chase_depth + props.island_cabinet_depth
        self.carcass = carcass_simple.INSERT_Island_Carcass()
        self.carcass.opening_qty = 5

class PRODUCT_Island_5_Opening_Dbl(cabinets.Island):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = STARTER_CATEGORY_NAME
        self.width = props.island_cabinet_width * 5
        self.height = props.island_cabinet_height
        self.depth = + props.island_double_chase_depth + props.island_cabinet_depth * 2 
        self.carcass = carcass_simple.INSERT_Island_Carcass()
        self.carcass.double_sided = True
        self.carcass.opening_qty = 10

class PRODUCT_Island_6_Opening(cabinets.Island):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = STARTER_CATEGORY_NAME
        self.width = props.island_cabinet_width * 6
        self.height = props.island_cabinet_height
        self.depth = props.island_single_chase_depth + props.island_cabinet_depth
        self.carcass = carcass_simple.INSERT_Island_Carcass()
        self.carcass.opening_qty = 6

class PRODUCT_Island_6_Opening_Dbl(cabinets.Island):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = STARTER_CATEGORY_NAME
        self.width = props.island_cabinet_width * 6
        self.height = props.island_cabinet_height
        self.depth = + props.island_double_chase_depth + props.island_cabinet_depth * 2 
        self.carcass = carcass_simple.INSERT_Island_Carcass()
        self.carcass.double_sided = True
        self.carcass.opening_qty = 12

class PRODUCT_Island_7_Opening(cabinets.Island):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = STARTER_CATEGORY_NAME
        self.width = props.island_cabinet_width * 7
        self.height = props.island_cabinet_height
        self.depth = props.island_single_chase_depth + props.island_cabinet_depth
        self.carcass = carcass_simple.INSERT_Island_Carcass()
        self.carcass.opening_qty = 7

class PRODUCT_Island_7_Opening_Dbl(cabinets.Island):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = STARTER_CATEGORY_NAME
        self.width = props.island_cabinet_width * 7
        self.height = props.island_cabinet_height
        self.depth = + props.island_double_chase_depth + props.island_cabinet_depth * 2 
        self.carcass = carcass_simple.INSERT_Island_Carcass()
        self.carcass.double_sided = True
        self.carcass.opening_qty = 14

class PRODUCT_Island_8_Opening(cabinets.Island):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = STARTER_CATEGORY_NAME
        self.width = props.island_cabinet_width * 8
        self.height = props.island_cabinet_height
        self.depth = props.island_single_chase_depth + props.island_cabinet_depth
        self.carcass = carcass_simple.INSERT_Island_Carcass()
        self.carcass.opening_qty = 8

class PRODUCT_Island_8_Opening_Dbl(cabinets.Island):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = STARTER_CATEGORY_NAME
        self.width = props.island_cabinet_width * 8
        self.height = props.island_cabinet_height
        self.depth = + props.island_double_chase_depth + props.island_cabinet_depth * 2 
        self.carcass = carcass_simple.INSERT_Island_Carcass()
        self.carcass.double_sided = True
        self.carcass.opening_qty = 16

class PRODUCT_Toe_Kick(cabinets.Toe_Kick):

    def __init__(self):
        props = cabinet_properties.get_scene_props()
        self.library_name = LIBRARY_NAME
        self.category_name = BASE_CATEGORY_NAME
        self.width = sn_unit.inch(18)
        self.height = props.carcass_defaults.toe_kick_height
        self.depth = sn_unit.inch(12)
        self.drop_id = cabinet_properties.LIBRARY_NAME_SPACE + ".place_toe_kick_assembly"





class PRODUCT_Classy_Hood_Tapered(cabinets.Hood):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = HOOD_CATEGORY_NAME
        self.hood_name = "Hood Cabinet Tapered"
        self.width = props.width_hood
        self.height = props.hood_cabinet_height
        self.depth = props.hood_cabinet_depth
        self.mirror_z = True
        self.resize_enabled = True

class PRODUCT_Classy_Hood_Angled(cabinets.Hood):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = HOOD_CATEGORY_NAME
        self.hood_name = "Hood Cabinet Angled"
        self.width = props.width_hood
        self.height = props.hood_cabinet_height
        self.depth = props.hood_cabinet_depth
        self.mirror_z = True
        self.resize_enabled = True

class PRODUCT_Classy_Hood_Straight_Shiplap(cabinets.Hood):
    
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = HOOD_CATEGORY_NAME
        self.hood_name = "Hood Cabinet Straight Shiplap"
        self.width = props.width_hood
        self.height = props.hood_cabinet_height
        self.depth = props.hood_cabinet_depth
        self.mirror_z = True
        self.resize_enabled = True

class PRODUCT_Classy_Hood_Curved(cabinets.Hood): 
        
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = HOOD_CATEGORY_NAME
        self.hood_name = "Hood Cabinet Curved"
        self.width = props.width_hood
        self.height = props.hood_cabinet_height
        self.depth = props.hood_cabinet_depth
        self.mirror_z = True
        self.resize_enabled = True  
 
class PRODUCT_Classy_Hood_Tapered_No_Trim(cabinets.Hood):
            
    def __init__(self):
        props = cabinet_properties.get_scene_props().size_defaults
        self.library_name = LIBRARY_NAME
        self.category_name = HOOD_CATEGORY_NAME
        self.hood_name = "Hood Cabinet Tapered No Trim"
        self.width = props.width_hood
        self.height = props.hood_cabinet_height
        self.depth = props.hood_cabinet_depth
        self.mirror_z = True
        self.resize_enabled = True
        