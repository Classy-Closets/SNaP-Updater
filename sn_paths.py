import bpy
import os

BLENDER_VER = "{}.{}".format(str(bpy.app.version[0]), str(bpy.app.version[1]))
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BL_DIR = os.path.dirname(bpy.app.binary_path)
SNAP_CONFIG_DIR = os.path.join(ROOT_DIR, "config")
STARTUP_FILE_PATH = os.path.join(SNAP_CONFIG_DIR, "sn_startup.blend")
PREFS_PATH = os.path.join(SNAP_CONFIG_DIR, "sn_userpref.blend")
SNAP_THEME_NAME = "snap_theme.xml"
SNAP_THEME_PATH = os.path.join(SNAP_CONFIG_DIR, SNAP_THEME_NAME)
CONFIG_PATH = os.path.join(BL_DIR, BLENDER_VER, "config")
THEMES_DIR = os.path.join(BL_DIR, BLENDER_VER, "scripts/presets/interface_theme")
ASSET_DIR = os.path.join(ROOT_DIR, "assets")
FONT_DIR = os.path.join(ASSET_DIR, "fonts")
APP_TEMPLATE_PATH = os.path.join(BL_DIR, BLENDER_VER, "scripts/startup/bl_app_templates_system/snap")
LIBRARY_ROOT = os.path.join(ROOT_DIR, 'libraries')
DOORS_AND_WINDOWS_ROOT = os.path.join(LIBRARY_ROOT, "doors_and_windows")
DOORS_AND_WINDOWS_THUMB_DIR = os.path.join(DOORS_AND_WINDOWS_ROOT, "products")
CLOSET_ROOT = os.path.join(LIBRARY_ROOT, "closets")
CLOSET_THUMB_DIR = os.path.join(CLOSET_ROOT, "products")
KITCHEN_BATH_ROOT = os.path.join(LIBRARY_ROOT, "kitchen_bath")
KITCHEN_BATH_THUMB_DIR = os.path.join(KITCHEN_BATH_ROOT, "products")
KITCHEN_BATH_ASSETS = os.path.join(KITCHEN_BATH_ROOT, "assets")
KITCHEN_BATH_ASSEMBLIES = os.path.join(KITCHEN_BATH_ASSETS, "Kitchen Bath Assemblies")
DEFAULT_KITCHEN_BATH_CATEGORY = "Base Cabinets"
DEFAULT_CATEGORY = "Products - Partitions"
APPLIANCE_DIR = os.path.join(LIBRARY_ROOT, "appliances")
APPLIANCE_THUMB_DIR = os.path.join(APPLIANCE_DIR, 'products')
OBJECT_DIR = os.path.join(LIBRARY_ROOT, "objects")
MATERIAL_DIR = os.path.join(LIBRARY_ROOT, "materials")
CLOSET_MATERIAL_DIR = os.path.join(MATERIAL_DIR, "Closet Materials")
COUNTERTOP_MATERIAL_DIR = os.path.join(MATERIAL_DIR, "Countertop Materials")
WORLD_DIR = os.path.join(LIBRARY_ROOT, "worlds")
ICON_DIR = os.path.join(ROOT_DIR, "icons")
DB_PATH = os.path.join(ROOT_DIR, "Snap.db")
CSV_DIR_PATH = os.path.join(ROOT_DIR, "db_init")
CSV_PATH = os.path.join(CSV_DIR_PATH, "CCItems_PHX.csv")
EDGE_TYPES_CSV_PATH = os.path.join(CSV_DIR_PATH, "EdgeTypes.csv")
MAT_TYPES_CSV_PATH = os.path.join(CSV_DIR_PATH, "MaterialTypes.csv")
FIVE_PIECE_DOOR_COLORS_CSV_PATH = os.path.join(CSV_DIR_PATH, "FivePieceDoorColors.csv")
OS_MAT_COLORS_CSV_PATH = os.path.join(CSV_DIR_PATH, "OversizeMaterialColors.csv")
CT_DIR = os.path.join(CSV_DIR_PATH, "Countertops")
GLAZE_COLORS_CSV_PATH = os.path.join(CSV_DIR_PATH, "GlazeColors.csv")
GLAZE_STYLES_CSV_PATH = os.path.join(CSV_DIR_PATH, "GlazeStyles.csv")
DOOR_COLORS_CSV_PATH = os.path.join(CSV_DIR_PATH, "ModernoDoorColors.csv")
GLASS_COLORS_CSV_PATH = os.path.join(CSV_DIR_PATH, "GlassColors.csv")
SLIDE_TYPES_CSV_PATH = os.path.join(CSV_DIR_PATH, "DrawerSlideTypes.csv")
DRAWER_SLIDE_DIR = os.path.join(CSV_DIR_PATH, "Drawer Slides")
