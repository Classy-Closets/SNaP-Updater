import math

from snap import sn_types, sn_unit, sn_utils
from os import path
from snap.libraries.closets import closet_paths
from . import cabinet_properties

LIBRARY_NAME_SPACE = "sn_kitchen_bath"

ROOT_DIR = path.dirname(__file__)
COUNTERTOP_PARTS_DIR = path.join(ROOT_DIR,"assets","Kitchen Bath Assemblies")
CTOP = path.join(COUNTERTOP_PARTS_DIR, "Countertop Part.blend")
BACKSPLASH_PART = path.join(COUNTERTOP_PARTS_DIR, "Countertop Part.blend")
WATERFALL_PART = path.join(COUNTERTOP_PARTS_DIR, "Countertop Part.blend")
NOTCHED_CTOP = path.join(COUNTERTOP_PARTS_DIR, "Corner Notch Part.blend")
DIAGONAL_CTOP = path.join(COUNTERTOP_PARTS_DIR, "Chamfered Part.blend")


def add_part(assembly, path):
    part_bp = assembly.add_assembly_from_file(path)
    part = sn_types.Assembly(part_bp)
    part.obj_bp["IS_BP_CABINET_COUNTERTOP"] = True
    return part

#---------PRODUCT: COUNTERTOPS

class PRODUCT_Straight_Countertop(sn_types.Assembly):
    
    def __init__(self):
        self.library_name = "Countertops"
        self.category_name = "Countertops"
        self.assembly_name = "Straight Countertop"

        self.type_assembly = 'INSERT'
        self.placement_type = "EXTERIOR"
        self.id_prompt = cabinet_properties.LIBRARY_NAME_SPACE + ".frameless_cabinet_prompts"

        self.width = sn_unit.inch(30)
        self.height = sn_unit.inch(5.5)
        self.depth = sn_unit.inch(24)
        self.height_above_floor = sn_unit.inch(34.1)

        self.double_sided = False
        self.section_qty = 1
        
    def draw(self):
        self.create_assembly()
        self.obj_bp["IS_BP_CABINET_COUNTERTOP"] = True
        
        self.add_prompt("Add Backsplash",'CHECKBOX',True)
        self.add_prompt("Add Left Backsplash",'CHECKBOX',False)
        self.add_prompt("Add Right Backsplash",'CHECKBOX',False)
        self.add_prompt("Add Left Waterfall",'CHECKBOX',False)
        self.add_prompt("Add Right Waterfall",'CHECKBOX',False)
        self.add_prompt("Splash Height", 'DISTANCE',sn_unit.inch(4))
        self.add_prompt("Side Splash Setback",'DISTANCE',sn_unit.inch(0))
        self.add_prompt("Deck Thickness",'DISTANCE',sn_unit.inch(1.5))
        self.add_prompt("Splash Thickness",'DISTANCE',sn_unit.inch(.75))
        self.add_prompt("Waterfall Thickness",'DISTANCE',sn_unit.inch(1.5))
        
        Product_Width = self.obj_x.snap.get_var('location.x','Product_Width')
        Product_Depth =  self.obj_y.snap.get_var('location.y','Product_Depth')
        Add_Backsplash = self.get_prompt('Add Backsplash').get_var()
        Add_Left_Backsplash = self.get_prompt('Add Left Backsplash').get_var()
        Add_Right_Backsplash = self.get_prompt('Add Right Backsplash').get_var()
        Add_Left_Waterfall = self.get_prompt('Add Left Waterfall').get_var()
        Add_Right_Waterfall = self.get_prompt('Add Right Waterfall').get_var()
        Splash_Height = self.get_prompt('Splash Height').get_var()
        Side_Splash_Setback = self.get_prompt('Side Splash Setback').get_var()
        Deck_Thickness = self.get_prompt('Deck Thickness').get_var()
        Splash_Thickness = self.get_prompt('Splash Thickness').get_var()
        Waterfall_Thickness = self.get_prompt("Waterfall Thickness").get_var()

        for section_nbr in range(1, self.section_qty+1):
            deck = add_part(self, CTOP)
            if self.section_qty == 1:
                deck.set_name("Countertop Deck")
            else:
                deck.set_name("Countertop Deck " + str(section_nbr))
            deck.obj_bp["IS_BP_COUNTERTOP_DECK"] = True
            deck.obj_bp["OPENING_NBR"] = section_nbr
            deck.loc_x('IF(Add_Left_Waterfall,-Waterfall_Thickness,0)',[Add_Left_Waterfall,Waterfall_Thickness])
            deck.dim_x('Product_Width+IF(Add_Left_Waterfall,Waterfall_Thickness,0)+IF(Add_Right_Waterfall,Waterfall_Thickness,0)',
                    [Product_Width,Add_Left_Waterfall,Add_Right_Waterfall,Waterfall_Thickness])
            deck.dim_y("Product_Depth",[Product_Depth])
            deck.dim_z("Deck_Thickness",[Deck_Thickness])

        splash = add_part(self, BACKSPLASH_PART)
        splash.set_name("Backsplash")
        splash.obj_bp['IS_BP_BACKSPLASH'] = True
        splash.loc_x('IF(Add_Left_Waterfall,-Waterfall_Thickness,0)',[Add_Left_Waterfall,Waterfall_Thickness])
        splash.loc_z('Deck_Thickness',[Deck_Thickness])
        splash.rot_x(value=math.radians(90))
        splash.dim_x('Product_Width+IF(Add_Left_Waterfall,Waterfall_Thickness,0)+IF(Add_Right_Waterfall,Waterfall_Thickness,0)',
                   [Product_Width,Add_Left_Waterfall,Add_Right_Waterfall,Waterfall_Thickness])
        splash.dim_y("Splash_Height",[Splash_Height])
        splash.dim_z("Splash_Thickness",[Splash_Thickness]) 
        splash.get_prompt("Hide").set_formula("IF(Add_Backsplash,False,True)",[Add_Backsplash])

        left_splash = add_part(self, BACKSPLASH_PART)
        left_splash.set_name("Left Backsplash")
        left_splash.obj_bp['IS_BP_LEFT_BACKSPLASH'] = True
        left_splash.loc_x('IF(Add_Left_Waterfall,-Waterfall_Thickness,0)',[Add_Left_Waterfall,Waterfall_Thickness])
        left_splash.loc_y("IF(Add_Backsplash,-Splash_Thickness,0)",[Splash_Thickness,Add_Backsplash])
        left_splash.loc_z('Deck_Thickness',[Deck_Thickness])
        left_splash.rot_x(value=math.radians(90))
        left_splash.rot_z(value=math.radians(-90))
        left_splash.dim_x("fabs(Product_Depth)-Side_Splash_Setback-Splash_Thickness",[Product_Depth,Side_Splash_Setback,Splash_Thickness])
        left_splash.dim_y("Splash_Height",[Splash_Height])
        left_splash.dim_z("-Splash_Thickness",[Splash_Thickness])
        left_splash.get_prompt("Hide").set_formula("IF(Add_Left_Backsplash,False,True)",[Add_Left_Backsplash])

        right_splash = add_part(self, BACKSPLASH_PART)
        right_splash.set_name("Right Backsplash")
        right_splash.obj_bp['IS_BP_RIGHT_BACKSPLASH'] = True
        right_splash.loc_x('Product_Width+IF(Add_Right_Waterfall,Waterfall_Thickness,0)',
                   [Product_Width,Add_Right_Waterfall,Waterfall_Thickness])
        right_splash.loc_y("IF(Add_Backsplash,-Splash_Thickness,0)",[Splash_Thickness,Add_Backsplash])
        right_splash.loc_z('Deck_Thickness',[Deck_Thickness])
        right_splash.rot_x(value=math.radians(90))
        right_splash.rot_z(value=math.radians(-90))
        right_splash.dim_x("fabs(Product_Depth)-Side_Splash_Setback-Splash_Thickness",[Product_Depth,Side_Splash_Setback,Splash_Thickness])
        right_splash.dim_y("Splash_Height",[Splash_Height])
        right_splash.dim_z("Splash_Thickness",[Splash_Thickness])
        right_splash.get_prompt("Hide").set_formula("IF(Add_Right_Backsplash,False,True)",[Add_Right_Backsplash])

        left_waterfall = add_part(self, WATERFALL_PART)
        left_waterfall.set_name("Left Waterfall")
        left_waterfall.obj_bp['IS_BP_WATERFALL'] = True
        left_waterfall.loc_x('-Waterfall_Thickness',[Waterfall_Thickness])
        left_waterfall.loc_z('-Deck_Thickness-Waterfall_Thickness',[Deck_Thickness,Waterfall_Thickness])
        left_waterfall.rot_x(value=math.radians(90))
        left_waterfall.rot_z(value=math.radians(-90))
        left_waterfall.dim_x("fabs(Product_Depth)",[Product_Depth])
        left_waterfall.dim_y("Waterfall_Thickness+Deck_Thickness",[Waterfall_Thickness,Deck_Thickness]) 
        left_waterfall.dim_z("-Waterfall_Thickness",[Waterfall_Thickness])
        left_waterfall.get_prompt("Hide").set_formula("IF(Add_Left_Waterfall,False,True)",[Add_Left_Waterfall])
        
        right_waterfall = add_part(self, WATERFALL_PART)
        right_waterfall.set_name("Right Waterfall")
        right_waterfall.obj_bp['IS_BP_WATERFALL'] = True
        right_waterfall.loc_x('fabs(Product_Width)',[Product_Width])
        right_waterfall.loc_z('-Deck_Thickness-Waterfall_Thickness',[Deck_Thickness,Waterfall_Thickness])
        right_waterfall.rot_x(value=math.radians(90))
        right_waterfall.rot_z(value=math.radians(-90))
        right_waterfall.dim_x("fabs(Product_Depth)",[Product_Depth])
        right_waterfall.dim_y("Waterfall_Thickness+Deck_Thickness",[Waterfall_Thickness,Deck_Thickness]) 
        right_waterfall.dim_z("-Waterfall_Thickness",[Waterfall_Thickness])
        right_waterfall.get_prompt("Hide").set_formula("IF(Add_Right_Waterfall,False,True)",[Add_Right_Waterfall])

        self.update()

class Corner_Countertop(sn_types.Assembly):

    type_assembly = 'INSERT'
    placement_type = "EXTERIOR"
    id_prompt = cabinet_properties.LIBRARY_NAME_SPACE + ".frameless_cabinet_prompts"
    corner_type = "Notched"

    def update(self):
        super().update()
        self.obj_bp["IS_BP_CABINET_COUNTERTOP"] = True

        self.obj_bp.location.z = self.height_above_floor
        self.obj_x.location.x = self.width
        self.obj_y.location.y = self.depth
        self.obj_z.location.z = self.height
    
    def draw(self):
        self.create_assembly()

        self.add_prompt("Left Side Depth", 'DISTANCE', sn_unit.inch(24.0))
        self.add_prompt("Right Side Depth", 'DISTANCE', sn_unit.inch(24.0))
        self.add_prompt("Add Left Rear Backsplash", 'CHECKBOX', True)
        self.add_prompt("Add Right Rear Backsplash", 'CHECKBOX', True)
        self.add_prompt("Add Left Backsplash", 'CHECKBOX', False)
        self.add_prompt("Add Right Backsplash", 'CHECKBOX', False)
        self.add_prompt("Splash Height", 'DISTANCE',sn_unit.inch(4))
        self.add_prompt("Side Splash Setback", 'DISTANCE', sn_unit.inch(0))
        self.add_prompt("Deck Thickness", 'DISTANCE', sn_unit.inch(1.5))
        self.add_prompt("Splash Thickness", 'DISTANCE', sn_unit.inch(.75))

        Product_Width = self.obj_x.snap.get_var('location.x', 'Product_Width')
        Product_Depth = self.obj_y.snap.get_var('location.y', 'Product_Depth')
        Left_Side_Depth = self.get_prompt('Left Side Depth').get_var()
        Right_Side_Depth = self.get_prompt('Right Side Depth').get_var()
        Add_Left_Backsplash = self.get_prompt('Add Left Backsplash').get_var()
        Add_Right_Backsplash = self.get_prompt('Add Right Backsplash').get_var()
        Add_Left_Rear_Backsplash = self.get_prompt('Add Left Rear Backsplash').get_var()
        Add_Right_Rear_Backsplash = self.get_prompt('Add Right Rear Backsplash').get_var()
        Splash_Height = self.get_prompt('Splash Height').get_var()
        Side_Splash_Setback = self.get_prompt('Side Splash Setback').get_var()
        Deck_Thickness = self.get_prompt('Deck Thickness').get_var()
        Splash_Thickness = self.get_prompt('Splash Thickness').get_var()
        
        if self.corner_type == 'Notched':
            deck = add_part(self, NOTCHED_CTOP)
        else:
            deck = add_part(self, DIAGONAL_CTOP)
        deck.set_name("Countertop Deck")
        deck.dim_x("Product_Width",[Product_Width])
        deck.dim_y("Product_Depth",[Product_Depth])
        deck.dim_z("Deck_Thickness",[Deck_Thickness])
        deck.get_prompt("Left Depth").set_formula("Left_Side_Depth",[Left_Side_Depth])
        deck.get_prompt("Right Depth").set_formula("Right_Side_Depth",[Right_Side_Depth])
        
        rear_left_splash = add_part(self, BACKSPLASH_PART)
        rear_left_splash.set_name("Left Rear Backsplash")
        rear_left_splash.obj_bp['IS_BP_REAR_LEFT_BACKSPLASH'] = True
        rear_left_splash.loc_z('Deck_Thickness',[Deck_Thickness])
        rear_left_splash.rot_x(value=math.radians(90)) 
        rear_left_splash.rot_z(value=math.radians(-90))
        rear_left_splash.dim_x("fabs(Product_Depth)",[Product_Depth])
        rear_left_splash.dim_y("Splash_Height",[Splash_Height]) 
        rear_left_splash.dim_z("-Splash_Thickness",[Splash_Thickness])
        rear_left_splash.get_prompt("Hide").set_formula("IF(Add_Left_Rear_Backsplash,False,True)",[Add_Left_Rear_Backsplash])
        
        rear_rear_splash = add_part(self, BACKSPLASH_PART)
        rear_rear_splash.set_name("Right Rear Backsplash")
        rear_rear_splash.obj_bp['IS_BP_REAR_REAR_BACKSPLASH'] = True
        rear_rear_splash.loc_x('IF(Add_Left_Rear_Backsplash,Splash_Thickness,0)',[Splash_Thickness,Add_Left_Rear_Backsplash])
        rear_rear_splash.loc_z('Deck_Thickness',[Deck_Thickness])
        rear_rear_splash.rot_x(value=math.radians(90)) 
        rear_rear_splash.dim_x("Product_Width-IF(Add_Left_Rear_Backsplash,Splash_Thickness,0)",[Product_Width,Add_Left_Rear_Backsplash,Splash_Thickness])
        rear_rear_splash.dim_y("Splash_Height",[Splash_Height]) 
        rear_rear_splash.dim_z("Splash_Thickness",[Splash_Thickness])
        rear_rear_splash.get_prompt("Hide").set_formula("IF(Add_Right_Rear_Backsplash,False,True)",[Add_Right_Rear_Backsplash])
        
        left_splash = add_part(self, BACKSPLASH_PART)
        left_splash.set_name("Left Backsplash")
        left_splash.obj_bp['IS_BP_LEFT_BACKSPLASH'] = True
        left_splash.loc_x('IF(Add_Left_Rear_Backsplash,Splash_Thickness,0)',[Add_Left_Rear_Backsplash,Splash_Thickness])
        left_splash.loc_y("Product_Depth",[Product_Depth])
        left_splash.loc_z('Deck_Thickness',[Deck_Thickness])
        left_splash.rot_x(value=math.radians(90))
        left_splash.dim_x("Left_Side_Depth-Side_Splash_Setback-Splash_Thickness",[Left_Side_Depth,Side_Splash_Setback,Splash_Thickness])
        left_splash.dim_y("Splash_Height",[Splash_Height]) 
        left_splash.dim_z("-Splash_Thickness",[Splash_Thickness])
        left_splash.get_prompt("Hide").set_formula("IF(Add_Left_Backsplash,False,True)",[Add_Left_Backsplash])
        
        right_splash = add_part(self, BACKSPLASH_PART) 
        right_splash.set_name("Rear Backsplash")
        right_splash.obj_bp['IS_BP_RIGHT_BACKSPLASH'] = True
        right_splash.loc_x("Product_Width",[Product_Width])
        right_splash.loc_y("IF(Add_Right_Rear_Backsplash,-Splash_Thickness,0)",[Splash_Thickness,Add_Right_Rear_Backsplash])
        right_splash.loc_z('Deck_Thickness',[Deck_Thickness])
        right_splash.rot_x(value=math.radians(90))
        right_splash.rot_z(value=math.radians(-90))
        right_splash.dim_x("Right_Side_Depth-Side_Splash_Setback-Splash_Thickness",[Right_Side_Depth,Side_Splash_Setback,Splash_Thickness])
        right_splash.dim_y("Splash_Height",[Splash_Height]) 
        right_splash.dim_z("Splash_Thickness",[Splash_Thickness])
        right_splash.get_prompt("Hide").set_formula("IF(Add_Right_Backsplash,False,True)",[Add_Right_Backsplash])
        
        self.update()

class PRODUCT_Notched_Corner_Countertop(Corner_Countertop):
    
    def __init__(self):
        self.library_name = "Countertops"
        self.category_name = "Countertops"
        self.assembly_name = "Notched Corner Countertop"
        self.placement_type = "Corner"
        self.corner_type = "Notched"
        self.id_prompt = cabinet_properties.LIBRARY_NAME_SPACE + ".frameless_cabinet_prompts"
        self.width = sn_unit.inch(36)
        self.height = sn_unit.inch(5.5)
        self.depth = sn_unit.inch(36)
        self.height_above_floor = sn_unit.inch(34.1)        
        
class PRODUCT_Diagonal_Corner_Countertop(Corner_Countertop):
    
    def __init__(self):
        self.library_name = "Countertops"
        self.category_name = "Countertops"
        self.assembly_name = "Diagonal Corner Countertop"
        self.placement_type = "Corner"
        self.corner_type = "Diagonal"
        self.id_prompt = cabinet_properties.LIBRARY_NAME_SPACE + ".frameless_cabinet_prompts"
        self.width = sn_unit.inch(36)
        self.height = sn_unit.inch(5.5)
        self.depth = sn_unit.inch(36)
        self.height_above_floor = sn_unit.inch(34.1)           

        
