import os
from snap import sn_unit
from . import appliance_types
from .appliance_paths import (
    WALL_APPLIANCE_PATH,
    WALL_OVEN_APPLIANCE_PATH,
    COOKTOP_APPLIANCE_PATH,
    RANGE_APPLIANCE_PATH,
    REFRIGERATOR_APPLIANCE_PATH,
    DISHWASHER_APPLIANCE_PATH,
    SINK_APPLIANCE_PATH,
    FAUCET_APPLIANCE_PATH,
    LAUNDRY_APPLIANCE_PATH,
    BATHTUB_APPLIANCE_PATH,
    TOILET_APPLIANCE_PATH
)


# ---------PRODUCT: PARAMETRIC APPLIANCES

# ---------PRODUCT: Refrigerators
class PRODUCT_Refrigerator_Generic(appliance_types.Parametric_Wall_Appliance):

    def __init__(self):
        self.category_name = "Appliances"
        self.assembly_name = "Refrigerator Generic"
        self.appliance_type = "Wall Appliance"
        self.appliance_subtype = "Refrigerator"
        self.resize_enabled = True
        self.width = sn_unit.inch(36)
        self.height = sn_unit.inch(84)
        self.depth = sn_unit.inch(27)
        self.appliance_path = os.path.join(REFRIGERATOR_APPLIANCE_PATH, "Refrigerator Generic.blend")
        super().__init__()

class PRODUCT_Refrigerator_Samsung(appliance_types.Parametric_Wall_Appliance):

    def __init__(self):
        self.category_name = "Appliances"
        self.assembly_name = "Refrigerator 36 Samsung"
        self.appliance_type = "Wall Appliance"
        self.appliance_subtype = "Refrigerator"
        self.resize_enabled = False
        self.width = sn_unit.inch(36)
        self.height = sn_unit.inch(84)
        self.depth = sn_unit.inch(27)
        self.appliance_path = os.path.join(REFRIGERATOR_APPLIANCE_PATH, "Refrigerator 36 Samsung.blend")
        super().__init__()

class PRODUCT_Refrigerator_42_Subzero(appliance_types.Parametric_Wall_Appliance):

    def __init__(self):
        self.category_name = "Appliances"
        self.assembly_name = "Refrigerator 42 Subzero"
        self.appliance_type = "Wall Appliance"
        self.appliance_subtype = "Refrigerator"
        self.resize_enabled = False
        self.width = sn_unit.inch(42)
        self.height = sn_unit.inch(84)
        self.depth = sn_unit.inch(27)
        self.appliance_path = os.path.join(REFRIGERATOR_APPLIANCE_PATH, "Refrigerator 42 Subzero.blend")
        super().__init__()

class PRODUCT_Refrigerator_48_Subzero(appliance_types.Parametric_Wall_Appliance):

    def __init__(self):
        self.category_name = "Appliances"
        self.assembly_name = "Refrigerator 48 Subzero"
        self.appliance_type = "Wall Appliance"
        self.appliance_subtype = "Refrigerator"
        self.resize_enabled = False
        self.width = sn_unit.inch(42)
        self.height = sn_unit.inch(84)
        self.depth = sn_unit.inch(27)
        self.appliance_path = os.path.join(REFRIGERATOR_APPLIANCE_PATH, "Refrigerator 48 Subzero.blend")
        super().__init__()

class PRODUCT_Wine_Cooler_Tall_Generic(appliance_types.Parametric_Wall_Appliance):

    def __init__(self):
        self.category_name = "Appliances"
        self.assembly_name = "Wine Cooler Generic"
        self.appliance_type = "Wall Appliance"
        self.appliance_subtype = "Refrigerator"
        self.resize_enabled = True
        self.width = sn_unit.inch(18)
        self.height = sn_unit.inch(84)
        self.depth = sn_unit.inch(24)
        self.appliance_path = os.path.join(REFRIGERATOR_APPLIANCE_PATH, "Wine Cooler Generic.blend")
        super().__init__()


# ---------PRODUCT: Ranges
class PRODUCT_Gas_Range_Generic(appliance_types.Parametric_Wall_Appliance):

    def __init__(self):
        self.category_name = "Appliances"
        self.assembly_name = "Gas Range Generic"
        self.appliance_type = "Wall Appliance"
        self.appliance_subtype = "Range"
        self.resize_enabled = True
        self.width = sn_unit.inch(30)
        self.height = sn_unit.inch(42)
        self.depth = sn_unit.inch(28)
        self.appliance_path = os.path.join(RANGE_APPLIANCE_PATH, "Gas Range Generic.blend")
        super().__init__()

class PRODUCT_Gas_Range_36_Monogram(appliance_types.Parametric_Wall_Appliance):

    def __init__(self):
        self.category_name = "Appliances"
        self.assembly_name = "Gas Range 36 Monogram"
        self.appliance_type = "Wall Appliance"
        self.appliance_subtype = "Range"
        self.resize_enabled = False
        self.width = sn_unit.inch(36)
        self.height = sn_unit.inch(42)
        self.depth = sn_unit.inch(28)
        self.appliance_path = os.path.join(RANGE_APPLIANCE_PATH, "Gas Range 36 Monogram.blend")
        super().__init__()

class PRODUCT_Gas_Range_48_Monogram(appliance_types.Parametric_Wall_Appliance):

    def __init__(self):
        self.category_name = "Appliances"
        self.assembly_name = "Gas Range 48 Monogram"
        self.appliance_type = "Wall Appliance"
        self.appliance_subtype = "Range"
        self.resize_enabled = False
        self.width = sn_unit.inch(36)
        self.height = sn_unit.inch(42)
        self.depth = sn_unit.inch(28)
        self.appliance_path = os.path.join(RANGE_APPLIANCE_PATH, "Gas Range 48 Monogram.blend")
        super().__init__()

class PRODUCT_Gas_Range_36_Wolf(appliance_types.Parametric_Wall_Appliance):

    def __init__(self):
        self.category_name = "Appliances"
        self.assembly_name = "Gas Range 36 Wolf"
        self.appliance_type = "Wall Appliance"
        self.appliance_subtype = "Range"
        self.resize_enabled = False
        self.width = sn_unit.inch(36)
        self.height = sn_unit.inch(42)
        self.depth = sn_unit.inch(28)
        self.appliance_path = os.path.join(RANGE_APPLIANCE_PATH, "Gas Range 36 Wolf.blend")
        super().__init__()

class PRODUCT_Gas_Range_48_Wolf(appliance_types.Parametric_Wall_Appliance):

    def __init__(self):
        self.category_name = "Appliances"
        self.assembly_name = "Gas Range 48 Wolf"
        self.appliance_type = "Wall Appliance"
        self.appliance_subtype = "Range"
        self.resize_enabled = False
        self.width = sn_unit.inch(36)
        self.height = sn_unit.inch(42)
        self.depth = sn_unit.inch(28)
        self.appliance_path = os.path.join(RANGE_APPLIANCE_PATH, "Gas Range 48 Wolf.blend")
        super().__init__()

# ---------PRODUCT: RANGE TOPS

class PRODUCT_Gas_Rangetop_36_Monogram(appliance_types.Parametric_Wall_Appliance):

    def __init__(self):
        self.category_name = "Appliances"
        self.assembly_name = "Gas Rangetop 36 Monogram"
        self.appliance_type = "Rangetop Appliance"
        self.appliance_subtype = "Rangetop"
        self.resize_enabled = False
        self.appliance_path = os.path.join(RANGE_APPLIANCE_PATH, "Gas Rangetop 36 Monogram.blend")
        super().__init__()

class PRODUCT_Gas_Rangetop_48_Monogram(appliance_types.Parametric_Wall_Appliance):

       def __init__(self):
        self.category_name = "Appliances"
        self.assembly_name = "Gas Rangetop 48 Monogram"
        self.appliance_type = "Rangetop Appliance"
        self.appliance_subtype = "Rangetop"
        self.resize_enabled = False
        self.appliance_path = os.path.join(RANGE_APPLIANCE_PATH, "Gas Rangetop 48 Monogram.blend")
        super().__init__()

# ---------PRODUCT: COOK TOPS
class PRODUCT_Wolf_CG152_Transitional_Gas_Cooktop(appliance_types.Parametric_Wall_Appliance):

    def __init__(self):
        self.category_name = "Appliances"
        self.appliance_type = "Countertop Appliance"
        self.appliance_subtype = "Cooktop"
        self.resize_enabled = False
        self.appliance_path = os.path.join(COOKTOP_APPLIANCE_PATH, "Wolf CG152 Transitional Gas Cooktop.blend")
        super().__init__()

# ---------PRODUCT: RANGE HOODS
class PRODUCT_Range_Hood_Generic_1(appliance_types.Parametric_Wall_Appliance):

    def __init__(self):
        self.category_name = "Appliances"
        self.assembly_name = "Range Hood Generic 1"
        self.appliance_type = "Wall Appliance"
        self.appliance_subtype = "Range Hood"
        self.resize_enabled = True
        self.width = sn_unit.inch(30)
        self.height = sn_unit.inch(14)
        self.depth = sn_unit.inch(12.5)
        self.appliance_path = os.path.join(WALL_APPLIANCE_PATH, "Wall Mounted Range Hood 01.blend")
        self.height_above_floor = sn_unit.inch(60)
        super().__init__()


class PRODUCT_Range_Hood_Generic_2(appliance_types.Parametric_Wall_Appliance):

    def __init__(self):
        self.category_name = "Appliances"
        self.assembly_name = "Range Hood Generic 2"
        self.appliance_type = "Wall Appliance"
        self.appliance_subtype = "Range Hood"
        self.resize_enabled = True
        self.width = sn_unit.inch(27.5)
        self.height = sn_unit.inch(48)
        self.depth = sn_unit.inch(12.5)
        self.appliance_path = os.path.join(WALL_APPLIANCE_PATH, "Designer Range Hood.blend")
        self.height_above_floor = sn_unit.inch(60)
        super().__init__()


# ---------PRODUCT: Dishwashers


class PRODUCT_Dishwasher_Generic(appliance_types.Parametric_Wall_Appliance):

    def __init__(self):
        self.category_name = "Appliances"
        self.assembly_name = "Dishwasher Generic"
        self.appliance_type = "Wall Appliance"
        self.appliance_subtype = "Dishwasher"
        self.resize_enabled = True
        self.width = sn_unit.inch(24)
        self.height = sn_unit.inch(34)
        self.depth = sn_unit.inch(23)
        self.appliance_path = os.path.join(DISHWASHER_APPLIANCE_PATH, "Dishwasher Generic.blend")
        super().__init__()

class PRODUCT_Dishwasher_Cove(appliance_types.Parametric_Wall_Appliance):

    def __init__(self):
        self.category_name = "Appliances"
        self.assembly_name = "Dishwasher Cove"
        self.appliance_type = "Wall Appliance"
        self.appliance_subtype = "Dishwasher"
        self.resize_enabled = False
        self.width = sn_unit.inch(24)
        self.height = sn_unit.inch(34)
        self.depth = sn_unit.inch(23)
        self.appliance_path = os.path.join(DISHWASHER_APPLIANCE_PATH, "Dishwasher Cove.blend")
        super().__init__()


# ---------PRODUCT: LAUNDRY

class PRODUCT_Washer_Generic(appliance_types.Parametric_Wall_Appliance):

    def __init__(self):
        self.category_name = "Appliances"
        self.appliance_type = "Wall Appliance"
        self.appliance_subtype = "Laundry Appliance"
        self.resize_enabled = True
        self.width = sn_unit.inch(27)
        self.height = sn_unit.inch(38)
        self.depth = sn_unit.inch(34)
        self.appliance_path = os.path.join(LAUNDRY_APPLIANCE_PATH, "Washer Generic.blend")
        super().__init__()


class PRODUCT_Dryer_Generic(appliance_types.Parametric_Wall_Appliance):

    def __init__(self):
        self.category_name = "Appliances"
        self.appliance_type = "Wall Appliance"
        self.appliance_subtype = "Laundry Appliance"
        self.resize_enabled = True
        self.width = sn_unit.inch(27)
        self.height = sn_unit.inch(38)
        self.depth = sn_unit.inch(34)
        self.appliance_path = os.path.join(LAUNDRY_APPLIANCE_PATH, "Dryer Generic.blend")
        super().__init__()


# ---------PRODUCT: SINKS
class PRODUCT_Sink_Bathroom_Kohler(appliance_types.Countertop_Appliance):

    def __init__(self):
        self.category_name = "Appliances"
        self.appliance_path = os.path.join(SINK_APPLIANCE_PATH, "Bathroom Sink.blend")
        super().__init__()


class PRODUCT_Sink_2_Basin_Generic(appliance_types.Countertop_Appliance):

    def __init__(self):
        self.category_name = "Appliances"
        self.appliance_path = os.path.join(SINK_APPLIANCE_PATH, "Double Basin Sink.blend")
        super().__init__()


class PRODUCT_Sink_1_Basin_Generic(appliance_types.Countertop_Appliance):

    def __init__(self):
        self.category_name = "Appliances"
        self.appliance_path = os.path.join(SINK_APPLIANCE_PATH, "Single Basin Sink.blend")
        super().__init__()

# ---------PRODUCT: BATHTUBS
class PRODUCT_Bathtub_Kohler_Dynametric(appliance_types.Parametric_Wall_Appliance):

    def __init__(self):
        self.category_name = "Appliances"
        self.appliance_type = "Wall Appliance"
        self.appliance_subtype = "Bathtub Appliance"
        self.resize_enabled = False
        self.width = sn_unit.inch(27)
        self.height = sn_unit.inch(38)
        self.depth = sn_unit.inch(34)
        self.appliance_path = os.path.join(BATHTUB_APPLIANCE_PATH, "Bathtub Kohler Dynametric.blend")
        super().__init__()

class PRODUCT_Bathtub_Kohler_Stargaze(appliance_types.Parametric_Wall_Appliance):

    def __init__(self):
        self.category_name = "Appliances"
        self.appliance_type = "Wall Appliance"
        self.appliance_subtype = "Bathtub Appliance"
        self.resize_enabled = False
        self.width = sn_unit.inch(27)
        self.height = sn_unit.inch(38)
        self.depth = sn_unit.inch(34)
        self.appliance_path = os.path.join(BATHTUB_APPLIANCE_PATH, "Bathtub Kohler Stargaze.blend")
        super().__init__()

class PRODUCT_Bathtub_Generic(appliance_types.Parametric_Wall_Appliance):

    def __init__(self):
        self.category_name = "Appliances"
        self.appliance_type = "Wall Appliance"
        self.appliance_subtype = "Bathtub Appliance"
        self.resize_enabled = True
        self.width = sn_unit.inch(27)
        self.height = sn_unit.inch(38)
        self.depth = sn_unit.inch(34)
        self.appliance_path = os.path.join(BATHTUB_APPLIANCE_PATH, "Bathtub Generic.blend")
        super().__init__()

# ---------PRODUCT: TOILETS
class PRODUCT_Toilet_Kohler_Cimarron(appliance_types.Parametric_Wall_Appliance):

    def __init__(self):
        self.category_name = "Appliances"
        self.appliance_type = "Wall Appliance"
        self.appliance_subtype = "Toilet Appliance"
        self.resize_enabled = False
        self.width = sn_unit.inch(27)
        self.height = sn_unit.inch(38)
        self.depth = sn_unit.inch(34)
        self.appliance_path = os.path.join(TOILET_APPLIANCE_PATH, "Toilet Kohler Cimarron.blend")
        super().__init__()

class PRODUCT_Toilet_Kohler_San_Souci(appliance_types.Parametric_Wall_Appliance):

    def __init__(self):
        self.category_name = "Appliances"
        self.appliance_type = "Wall Appliance"
        self.appliance_subtype = "Toilet Appliance"
        self.resize_enabled = False
        self.width = sn_unit.inch(27)
        self.height = sn_unit.inch(38)
        self.depth = sn_unit.inch(34)
        self.appliance_path = os.path.join(TOILET_APPLIANCE_PATH, "Toilet Kohler San Souci.blend")
        super().__init__()