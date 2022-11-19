from snap import sn_types, sn_unit
from os import path
import math
from .. import closet_props
from ..common import common_parts
import bpy


class White_Drawer_Box(sn_types.Assembly):

    type_assembly = "NONE"
    mirror_y = False

    def draw(self):
        print("Adding White Drawer Box")
        self.create_assembly()
        self.obj_bp.snap.export_as_subassembly = True

        props = bpy.context.scene.sn_closets
        defaults = props.closet_defaults

        obj_props = self.obj_bp.sn_closets
        obj_props.is_drawer_box_bp = True  # TODO: remove
        self.obj_bp["IS_BP_DRAWER_BOX"] = True

        self.add_prompt("Hide", 'CHECKBOX', False)
        self.add_prompt("Hide Drawer Sub Front", 'CHECKBOX', False)
        self.add_prompt("Drawer Side Thickness", 'DISTANCE', sn_unit.inch(.5))
        self.add_prompt("Front Back Thickness", 'DISTANCE', sn_unit.inch(.5))
        self.add_prompt("Drawer Bottom Thickness", 'DISTANCE', sn_unit.inch(.25))
        self.add_prompt("Drawer Box Bottom Dado Depth", 'DISTANCE', defaults.drawer_bottom_dado_depth)
        self.add_prompt("Drawer Bottom Z Location", 'DISTANCE', defaults.drawer_bottom_z_location)
        self.add_prompt("Applied Bottom", 'CHECKBOX', False)
        self.add_prompt("Applied Bottom Width Deduction", 'DISTANCE', 0)
        self.add_prompt("Applied Bottom Depth Deduction", 'DISTANCE', 0)
        self.add_prompt("Back Override Height", 'DISTANCE', 0)
        self.add_prompt("Override Height", 'DISTANCE', 0)
        self.add_prompt("Override Depth", 'DISTANCE', 0)
        self.add_prompt("Use Dovetail Construction", 'CHECKBOX', False)
        self.add_prompt("Four Hole", 'DISTANCE', sn_unit.millimeter(123.952))
        self.add_prompt("Five Hole", 'DISTANCE', sn_unit.millimeter(155.956))
        self.add_prompt("Six Hole", 'DISTANCE', sn_unit.millimeter(187.96))
        self.add_prompt("Seven Hole", 'DISTANCE', sn_unit.millimeter(219.964))
        self.add_prompt("Eight Hole", 'DISTANCE', sn_unit.millimeter(251.968))
        self.add_prompt("Nine Hole", 'DISTANCE', sn_unit.millimeter(283.972))
        self.add_prompt("Ten Hole", 'DISTANCE', sn_unit.millimeter(315.976))
        self.add_prompt("Drawer Front Height", 'DISTANCE', sn_unit.millimeter(91.948))
        # self.add_prompt("Slide Type", 'COMBOBOX', 0, ["Sidemount", "Undermount"])
        self.add_prompt("Box Type", 'COMBOBOX', 0, ['White Melamine', '3/4" Melamine', 'Dovetail'])

        Drawer_Width = self.obj_x.snap.get_var('location.x', 'Drawer_Width')
        Drawer_Depth = self.obj_y.snap.get_var('location.y', 'Drawer_Depth')
        Drawer_Height = self.obj_z.snap.get_var('location.z', 'Drawer_Height')
        Drawer_Side_Thickness = self.get_prompt('Drawer Side Thickness').get_var('Drawer_Side_Thickness')
        Front_Back_Thickness = self.get_prompt('Front Back Thickness').get_var('Front_Back_Thickness')
        Drawer_Bottom_Thickness = self.get_prompt('Drawer Bottom Thickness').get_var('Drawer_Bottom_Thickness')
        Override_Depth = self.get_prompt('Override Depth').get_var('Override_Depth')
        HSF = self.get_prompt('Hide Drawer Sub Front').get_var('HSF')
        Applied_Bottom = self.get_prompt('Applied Bottom').get_var('Applied_Bottom')
        Hide = self.get_prompt('Hide').get_var('Hide')
        Box_Type = self.get_prompt('Box Type').get_var('Box_Type')

        self.get_prompt('Drawer Side Thickness').set_value(value=sn_unit.inch(0.5))
        self.get_prompt('Front Back Thickness').set_value(value=sn_unit.inch(0.5))
        self.get_prompt('Drawer Bottom Thickness').set_value(value=sn_unit.inch(0.375))

        # White Melamine Boxes
        left_side = common_parts.add_drawer_side(self)
        left_side.set_name("Left Drawer Side")
        left_side.loc_x('0', [])
        left_side.loc_y('0', [])
        left_side.rot_x(value=math.radians(90))
        left_side.rot_z(value=math.radians(90))
        left_side.dim_x('IF(Override_Depth>0,Override_Depth,Drawer_Depth)', [Override_Depth, Drawer_Depth, Drawer_Depth])
        left_side.dim_y('Drawer_Height', [Drawer_Height])
        left_side.dim_z('Drawer_Side_Thickness', [Drawer_Side_Thickness])
        left_side.get_prompt('Hide').set_formula('Hide', [Hide])
        left_side.get_prompt('Box Type').set_formula('Box_Type', [Box_Type])

        right_side = common_parts.add_drawer_side(self)
        right_side.set_name("Right Drawer Side")
        right_side.loc_x('Drawer_Width', [Drawer_Width])
        right_side.loc_y('0', [])
        right_side.rot_x(value=math.radians(90))
        right_side.rot_z(value=math.radians(90))
        right_side.dim_x('IF(Override_Depth>0,Override_Depth,Drawer_Depth)', [Override_Depth, Drawer_Depth, Drawer_Depth])
        right_side.dim_y('Drawer_Height', [Drawer_Height])
        right_side.dim_z('-Drawer_Side_Thickness', [Drawer_Side_Thickness])
        right_side.get_prompt('Hide').set_formula('Hide', [Hide])
        right_side.get_prompt('Box Type').set_formula('Box_Type', [Box_Type])

        front = common_parts.add_drawer_sub_front(self)
        front.loc_x('Drawer_Side_Thickness', [Drawer_Side_Thickness])
        front.rot_x(value=math.radians(90))
        front.dim_x('Drawer_Width-(Drawer_Side_Thickness*2)', [Drawer_Width, Drawer_Side_Thickness])
        front.dim_y('Drawer_Height', [Drawer_Height])
        front.dim_z('-Front_Back_Thickness', [Front_Back_Thickness])
        front.get_prompt('Hide').set_formula('IF(HSF,True,Hide)', [HSF, Hide])
        front.get_prompt('Box Type').set_formula('Box_Type', [Box_Type])

        back = common_parts.add_drawer_back(self)
        back.loc_x('Drawer_Side_Thickness', [Drawer_Side_Thickness])
        back.loc_y('IF(Override_Depth>0,Override_Depth,Drawer_Depth)', [Override_Depth, Drawer_Depth])
        back.loc_z('IF(Applied_Bottom,Drawer_Bottom_Thickness,0)', [Applied_Bottom, Drawer_Bottom_Thickness])
        back.rot_x(value=math.radians(90))
        back.dim_x('Drawer_Width-(Drawer_Side_Thickness*2)', [Drawer_Width, Drawer_Side_Thickness])
        back.dim_y('Drawer_Height', [Drawer_Height])
        back.dim_z('Front_Back_Thickness', [Front_Back_Thickness])
        back.get_prompt('Hide').set_formula('Hide', [Hide])
        back.get_prompt('Box Type').set_formula('Box_Type', [Box_Type])

        bottom = common_parts.add_drawer_bottom(self)
        bottom.loc_x(value=0)
        bottom.loc_y(value=0)
        bottom.loc_z('-Drawer_Bottom_Thickness', [Drawer_Bottom_Thickness])
        bottom.rot_z(value=math.radians(90))
        bottom.dim_x('IF(Override_Depth>0,Override_Depth,Drawer_Depth)', [Override_Depth, Drawer_Depth])
        bottom.dim_y('(Drawer_Width+INCH(.05))*-1', [Drawer_Width])
        bottom.dim_z('Drawer_Bottom_Thickness', [Drawer_Bottom_Thickness])
        bottom.get_prompt('Hide').set_formula('Hide', [Hide])
        bottom.get_prompt('Box Type').set_formula('Box_Type', [Box_Type])

        # self.update()


class Melamine_Drawer_Box(sn_types.Assembly):

    type_assembly = "NONE"
    mirror_y = False

    def draw(self):
        print("Adding 3/4 Melamine Drawer Box")
        self.create_assembly()
        self.obj_bp.snap.export_as_subassembly = True

        props = bpy.context.scene.sn_closets
        defaults = props.closet_defaults

        obj_props = self.obj_bp.sn_closets
        obj_props.is_drawer_box_bp = True  # TODO: remove
        self.obj_bp["IS_BP_DRAWER_BOX"] = True

        self.add_prompt("Hide", 'CHECKBOX', False)
        self.add_prompt("Hide Drawer Sub Front", 'CHECKBOX', False)
        self.add_prompt("Drawer Side Thickness", 'DISTANCE', sn_unit.inch(.5))
        self.add_prompt("Front Back Thickness", 'DISTANCE', sn_unit.inch(.5))
        self.add_prompt("Drawer Bottom Thickness", 'DISTANCE', sn_unit.inch(.25))
        self.add_prompt("Drawer Box Bottom Dado Depth", 'DISTANCE', defaults.drawer_bottom_dado_depth)
        self.add_prompt("Drawer Bottom Z Location", 'DISTANCE', defaults.drawer_bottom_z_location)
        self.add_prompt("Applied Bottom", 'CHECKBOX', False)
        self.add_prompt("Applied Bottom Width Deduction", 'DISTANCE', 0)
        self.add_prompt("Applied Bottom Depth Deduction", 'DISTANCE', 0)
        self.add_prompt("Back Override Height", 'DISTANCE', 0)
        self.add_prompt("Override Height", 'DISTANCE', 0)
        self.add_prompt("Override Depth", 'DISTANCE', 0)
        self.add_prompt("Use Dovetail Construction", 'CHECKBOX', False)
        self.add_prompt("Four Hole", 'DISTANCE', sn_unit.millimeter(123.952))
        self.add_prompt("Five Hole", 'DISTANCE', sn_unit.millimeter(155.956))
        self.add_prompt("Six Hole", 'DISTANCE', sn_unit.millimeter(187.96))
        self.add_prompt("Seven Hole", 'DISTANCE', sn_unit.millimeter(219.964))
        self.add_prompt("Eight Hole", 'DISTANCE', sn_unit.millimeter(251.968))
        self.add_prompt("Nine Hole", 'DISTANCE', sn_unit.millimeter(283.972))
        self.add_prompt("Ten Hole", 'DISTANCE', sn_unit.millimeter(315.976))
        self.add_prompt("Drawer Front Height", 'DISTANCE', sn_unit.millimeter(91.948))
        # self.add_prompt("Slide Type", 'COMBOBOX', 0, ["Sidemount", "Undermount"])
        self.add_prompt("Box Type", 'COMBOBOX', 0, ['White Melamine', '3/4" Melamine', 'Dovetail'])

        Drawer_Width = self.obj_x.snap.get_var('location.x', 'Drawer_Width')
        Drawer_Depth = self.obj_y.snap.get_var('location.y', 'Drawer_Depth')
        Drawer_Height = self.obj_z.snap.get_var('location.z','Drawer_Height')
        Drawer_Side_Thickness = self.get_prompt('Drawer Side Thickness').get_var('Drawer_Side_Thickness')
        Front_Back_Thickness = self.get_prompt('Front Back Thickness').get_var('Front_Back_Thickness')
        Drawer_Bottom_Thickness = self.get_prompt('Drawer Bottom Thickness').get_var('Drawer_Bottom_Thickness')
        Override_Depth = self.get_prompt('Override Depth').get_var('Override_Depth')
        HSF = self.get_prompt('Hide Drawer Sub Front').get_var('HSF')
        Applied_Bottom = self.get_prompt('Applied Bottom').get_var('Applied_Bottom')
        Hide = self.get_prompt('Hide').get_var('Hide')
        Use_Dovetail_Construction = self.get_prompt('Use Dovetail Construction').get_var('Use_Dovetail_Construction')
        Four_Hole = self.get_prompt('Four Hole').get_var('Four_Hole')
        Five_Hole = self.get_prompt('Five Hole').get_var('Five_Hole')
        Six_Hole = self.get_prompt('Six Hole').get_var('Six_Hole')
        Seven_Hole = self.get_prompt('Seven Hole').get_var('Seven_Hole')
        Eight_Hole = self.get_prompt('Eight Hole').get_var('Eight_Hole')
        Nine_Hole = self.get_prompt('Nine Hole').get_var('Nine_Hole')
        Ten_Hole = self.get_prompt('Ten Hole').get_var('Ten_Hole')
        DFH = self.get_prompt('Drawer Front Height').get_var('DFH')
        # Slide_Type = self.get_prompt('Slide Type').get_var('Slide_Type')
        Box_Type = self.get_prompt("Box Type").get_var('Box_Type')

        self.get_prompt('Drawer Side Thickness').set_value(value=sn_unit.inch(0.75))
        self.get_prompt('Front Back Thickness').set_value(value=sn_unit.inch(0.75))
        self.get_prompt('Drawer Bottom Thickness').set_value(value=sn_unit.inch(0.75))

        # 3/4" Melamine Drawer Box
        left_side = common_parts.add_drawer_side(self)
        left_side.set_name("Left Drawer Side")
        left_side.loc_x(value=0)
        left_side.loc_y(value=0)
        left_side.rot_x(value=math.radians(90))
        left_side.rot_z(value=math.radians(90))
        left_side.dim_x('IF(Override_Depth>0,Override_Depth,Drawer_Depth)', [Override_Depth, Drawer_Depth])
        left_side.dim_y(
            'IF(DFH==Four_Hole,INCH(2.75),CHECK(DFH,Five_Hole,Six_Hole,Seven_Hole,Eight_Hole,Nine_Hole,Ten_Hole)-INCH(1.45))',
            [Drawer_Height, DFH, Four_Hole, Five_Hole, Six_Hole, Seven_Hole, Eight_Hole, Nine_Hole, Ten_Hole])
        left_side.dim_z('Drawer_Side_Thickness', [Drawer_Side_Thickness])
        left_side.get_prompt('Hide').set_formula('Hide', [Hide])
        left_side.get_prompt('Box Type').set_formula('Box_Type', [Box_Type])

        right_side = common_parts.add_drawer_side(self)
        right_side.set_name("Right Drawer Side")
        right_side.loc_x('Drawer_Width+INCH(0.375)/2', [Drawer_Width])
        right_side.loc_y(value=0)
        right_side.rot_x(value=math.radians(90))
        right_side.rot_z(value=math.radians(90))
        right_side.dim_x(
            'IF(Override_Depth>0,Override_Depth,Drawer_Depth)',
            [Override_Depth, Drawer_Depth, Drawer_Depth])
        right_side.dim_y(
            'IF(DFH==Four_Hole,INCH(2.75),CHECK(DFH,Five_Hole,Six_Hole,Seven_Hole,Eight_Hole,Nine_Hole,Ten_Hole)-INCH(1.45))',
            [Drawer_Height, DFH, Four_Hole, Five_Hole, Six_Hole, Seven_Hole, Eight_Hole, Nine_Hole, Ten_Hole])
        right_side.dim_z('-Drawer_Side_Thickness', [Drawer_Side_Thickness])
        right_side.get_prompt('Hide').set_formula('Hide', [Hide])
        right_side.get_prompt('Box Type').set_formula('Box_Type', [Box_Type])

        front = common_parts.add_drawer_sub_front(self)
        front.loc_x('Drawer_Side_Thickness', [Drawer_Side_Thickness])
        front.rot_x(value=math.radians(90))
        front.dim_x('Drawer_Width-(Drawer_Side_Thickness*2)', [Drawer_Width, Drawer_Side_Thickness])
        front.dim_y(
            'IF(DFH==Four_Hole,INCH(2.75),CHECK(DFH,Five_Hole,Six_Hole,Seven_Hole,Eight_Hole,Nine_Hole,Ten_Hole)-INCH(1.45))',
            [Drawer_Height, DFH, Four_Hole, Five_Hole, Six_Hole, Seven_Hole, Eight_Hole, Nine_Hole, Ten_Hole])
        front.dim_z('-Front_Back_Thickness', [Front_Back_Thickness])
        front.get_prompt('Hide').set_formula('IF(HSF,True,Hide)', [HSF, Hide])
        front.get_prompt('Box Type').set_formula('Box_Type', [Box_Type])

        back = common_parts.add_drawer_back(self)
        back.loc_x('Drawer_Side_Thickness', [Drawer_Side_Thickness])
        back.loc_y('IF(Override_Depth>0,Override_Depth,Drawer_Depth)', [Override_Depth, Drawer_Depth])
        back.loc_z('IF(Applied_Bottom,Drawer_Bottom_Thickness,0)', [Applied_Bottom, Drawer_Bottom_Thickness])
        back.rot_x(value=math.radians(90))
        back.dim_x('Drawer_Width-(Drawer_Side_Thickness*2)', [Drawer_Width, Drawer_Side_Thickness])
        back.dim_y(
            'IF(DFH==Four_Hole,INCH(2.75),CHECK(DFH,Five_Hole,Six_Hole,Seven_Hole,Eight_Hole,Nine_Hole,Ten_Hole)-INCH(1.45))',
            [Drawer_Height, DFH, Four_Hole, Five_Hole, Six_Hole, Seven_Hole, Eight_Hole, Nine_Hole, Ten_Hole])
        back.dim_z('Front_Back_Thickness', [Front_Back_Thickness])
        back.get_prompt('Hide').set_formula('Hide', [Hide])
        back.get_prompt('Box Type').set_formula('Box_Type', [Box_Type])

        bottom = common_parts.add_drawer_bottom(self)
        bottom.loc_x('Drawer_Side_Thickness/2', [Drawer_Side_Thickness])
        bottom.loc_y('Drawer_Side_Thickness/2', [Drawer_Side_Thickness])
        bottom.loc_z(value=0.001)
        bottom.rot_z(value=math.radians(90))
        bottom.dim_x(
            'IF(Override_Depth>0,Override_Depth,Drawer_Depth)-Drawer_Side_Thickness',
            [Override_Depth, Drawer_Depth, Drawer_Side_Thickness])
        bottom.dim_y(
            '(Drawer_Width-Drawer_Side_Thickness)*-1',
            [Drawer_Width, Drawer_Side_Thickness])
        bottom.dim_z(value=sn_unit.inch(0.375))
        bottom.get_prompt('Hide').set_formula('Hide', [Hide])
        bottom.get_prompt('Box Type').set_formula('Box_Type', [Box_Type])\



class Wood_Drawer_Box(sn_types.Assembly):

    type_assembly = "NONE"
    mirror_y = False

    def draw(self):
        print("Adding Dovetail Drawer Box")
        self.create_assembly()
        self.obj_bp.snap.export_as_subassembly = True

        props = bpy.context.scene.sn_closets
        defaults = props.closet_defaults

        obj_props = self.obj_bp.sn_closets
        obj_props.is_drawer_box_bp = True  # TODO: remove
        self.obj_bp["IS_BP_DRAWER_BOX"] = True

        self.add_prompt("Hide", 'CHECKBOX', False)
        self.add_prompt("Hide Drawer Sub Front", 'CHECKBOX', False)
        self.add_prompt("Drawer Side Thickness", 'DISTANCE', sn_unit.inch(.5))
        self.add_prompt("Front Back Thickness", 'DISTANCE', sn_unit.inch(.5))
        self.add_prompt("Drawer Bottom Thickness", 'DISTANCE', sn_unit.inch(.25))
        self.add_prompt("Drawer Box Bottom Dado Depth", 'DISTANCE', defaults.drawer_bottom_dado_depth)
        self.add_prompt("Drawer Bottom Z Location", 'DISTANCE', defaults.drawer_bottom_z_location)
        self.add_prompt("Applied Bottom", 'CHECKBOX', False)
        self.add_prompt("Applied Bottom Width Deduction", 'DISTANCE', 0)
        self.add_prompt("Applied Bottom Depth Deduction", 'DISTANCE', 0)
        self.add_prompt("Back Override Height", 'DISTANCE', 0)
        self.add_prompt("Override Height", 'DISTANCE', 0)
        self.add_prompt("Override Depth", 'DISTANCE', 0)
        self.add_prompt("Use Dovetail Construction", 'CHECKBOX', False)
        self.add_prompt("Four Hole", 'DISTANCE', sn_unit.millimeter(123.952))
        self.add_prompt("Five Hole", 'DISTANCE', sn_unit.millimeter(155.956))
        self.add_prompt("Six Hole", 'DISTANCE', sn_unit.millimeter(187.96))
        self.add_prompt("Seven Hole", 'DISTANCE', sn_unit.millimeter(219.964))
        self.add_prompt("Eight Hole", 'DISTANCE', sn_unit.millimeter(251.968))
        self.add_prompt("Nine Hole", 'DISTANCE', sn_unit.millimeter(283.972))
        self.add_prompt("Ten Hole", 'DISTANCE', sn_unit.millimeter(315.976))
        self.add_prompt("Drawer Front Height", 'DISTANCE', sn_unit.millimeter(91.948))
        # self.add_prompt("Slide Type", 'COMBOBOX', 0, ["Sidemount", "Undermount"])
        self.add_prompt("Box Type", 'COMBOBOX', 0, ['White Melamine', '3/4" Melamine', 'Dovetail'])

        Drawer_Width = self.obj_x.snap.get_var('location.x', 'Drawer_Width')
        Drawer_Depth = self.obj_y.snap.get_var('location.y', 'Drawer_Depth')
        Drawer_Height = self.obj_z.snap.get_var('location.z', 'Drawer_Height')
        Drawer_Side_Thickness = self.get_prompt('Drawer Side Thickness').get_var('Drawer_Side_Thickness')
        Front_Back_Thickness = self.get_prompt('Front Back Thickness').get_var('Front_Back_Thickness')
        Drawer_Bottom_Thickness = self.get_prompt('Drawer Bottom Thickness').get_var('Drawer_Bottom_Thickness')
        Override_Depth = self.get_prompt('Override Depth').get_var('Override_Depth')
        HSF = self.get_prompt('Hide Drawer Sub Front').get_var('HSF')
        Applied_Bottom = self.get_prompt('Applied Bottom').get_var('Applied_Bottom')
        Hide = self.get_prompt('Hide').get_var('Hide')
        Use_Dovetail_Construction = self.get_prompt('Use Dovetail Construction').get_var('Use_Dovetail_Construction')
        Four_Hole = self.get_prompt('Four Hole').get_var('Four_Hole')
        Five_Hole = self.get_prompt('Five Hole').get_var('Five_Hole')
        Six_Hole = self.get_prompt('Six Hole').get_var('Six_Hole')
        Seven_Hole = self.get_prompt('Seven Hole').get_var('Seven_Hole')
        Eight_Hole = self.get_prompt('Eight Hole').get_var('Eight_Hole')
        Nine_Hole = self.get_prompt('Nine Hole').get_var('Nine_Hole')
        Ten_Hole = self.get_prompt('Ten Hole').get_var('Ten_Hole')
        DFH = self.get_prompt('Drawer Front Height').get_var('DFH')
       # Slide_Type = self.get_prompt('Slide Type').get_var('Slide_Type')
        Box_Type = self.get_prompt("Box Type").get_var('Box_Type')

        self.get_prompt('Drawer Side Thickness').set_value(value=sn_unit.inch(0.5))
        self.get_prompt('Front Back Thickness').set_value(value=sn_unit.inch(0.5))
        self.get_prompt('Drawer Bottom Thickness').set_value(value=sn_unit.inch(0.375))

        # Dovetail Drawer Box
        left_side = common_parts.add_drawer_side(self)
        left_side.set_name("Left Drawer Side")
        left_side.loc_x('-INCH(0.375)/2', [])
        left_side.loc_y('INCH(.125)', [])
        left_side.rot_x(value=math.radians(90))
        left_side.rot_z(value=math.radians(90))
        left_side.dim_x('IF(Override_Depth>0,Override_Depth,Drawer_Depth)-INCH(.25)', [Override_Depth, Drawer_Depth])
        left_side.dim_y(
            'IF(DFH==Four_Hole,INCH(2.75),CHECK(DFH,Five_Hole,Six_Hole,Seven_Hole,Eight_Hole,Nine_Hole,Ten_Hole)-INCH(1.45))',
            [Drawer_Height, DFH, Four_Hole, Five_Hole, Six_Hole, Seven_Hole, Eight_Hole, Nine_Hole, Ten_Hole])
        left_side.dim_z('Drawer_Side_Thickness', [Drawer_Side_Thickness])
        left_side.get_prompt('Hide').set_formula('Hide', [Hide])
        left_side.get_prompt('Use Dovetail Construction').set_formula('Use_Dovetail_Construction', [Use_Dovetail_Construction])
        left_side.get_prompt('Box Type').set_formula('Box_Type', [Box_Type])

        right_side = common_parts.add_drawer_side(self)
        right_side.set_name("Right Drawer Side")
        right_side.loc_x('Drawer_Width+INCH(0.375)/2', [Drawer_Width])
        right_side.loc_y('INCH(.125)', [])
        right_side.rot_x(value=math.radians(90))
        right_side.rot_z(value=math.radians(90))
        right_side.dim_x(
            'IF(Override_Depth>0,Override_Depth,Drawer_Depth)-INCH(.25)',
            [Override_Depth, Drawer_Depth, Drawer_Depth])
        right_side.dim_y(
            'IF(DFH==Four_Hole,INCH(2.75),CHECK(DFH,Five_Hole,Six_Hole,Seven_Hole,Eight_Hole,Nine_Hole,Ten_Hole)-INCH(1.45))',
            [Drawer_Height, DFH, Four_Hole, Five_Hole, Six_Hole, Seven_Hole, Eight_Hole, Nine_Hole, Ten_Hole])
        right_side.dim_z('-Drawer_Side_Thickness', [Drawer_Side_Thickness])
        right_side.get_prompt('Hide').set_formula('Hide', [Hide])
        right_side.get_prompt('Use Dovetail Construction').set_formula('Use_Dovetail_Construction', [Use_Dovetail_Construction])
        right_side.get_prompt('Box Type').set_formula('Box_Type', [Box_Type])

        front = common_parts.add_drawer_sub_front(self)
        front.loc_x('-INCH(0.375)/2',
                    [Drawer_Side_Thickness])
        front.rot_x(value=math.radians(90))
        front.dim_x('Drawer_Width+INCH(0.375)',
                    [Drawer_Width, Drawer_Side_Thickness])
        front.dim_y('IF(DFH==Four_Hole,INCH(2.75),CHECK(DFH,Five_Hole,Six_Hole,Seven_Hole,Eight_Hole,Nine_Hole,Ten_Hole)-INCH(1.45))',
                    [Drawer_Height, DFH, Four_Hole, Five_Hole, Six_Hole, Seven_Hole, Eight_Hole, Nine_Hole, Ten_Hole])
        front.dim_z('-Front_Back_Thickness', [Front_Back_Thickness])
        front.get_prompt('Hide').set_formula('IF(HSF,True,Hide)', [HSF, Hide])
        front.get_prompt('Use Dovetail Construction').set_formula('Use_Dovetail_Construction', [Use_Dovetail_Construction])
        front.get_prompt('Box Type').set_formula('Box_Type', [Box_Type])

        back = common_parts.add_drawer_back(self)
        back.loc_x('-INCH(0.375)/2', [Drawer_Side_Thickness])
        back.loc_y('IF(Override_Depth>0,Override_Depth,Drawer_Depth)', [Override_Depth, Drawer_Depth])
        back.loc_z('IF(Applied_Bottom,Drawer_Bottom_Thickness,0)', [Applied_Bottom, Drawer_Bottom_Thickness])
        back.rot_x(value=math.radians(90))
        back.dim_x('Drawer_Width+INCH(0.375)', [Drawer_Width, Drawer_Side_Thickness])
        back.dim_y(
            'IF(DFH==Four_Hole,INCH(2.75),CHECK(DFH,Five_Hole,Six_Hole,Seven_Hole,Eight_Hole,Nine_Hole,Ten_Hole)-INCH(1.45))',
            [Drawer_Height, DFH, Four_Hole, Five_Hole, Six_Hole, Seven_Hole, Eight_Hole, Nine_Hole, Ten_Hole])
        back.dim_z('Front_Back_Thickness', [Front_Back_Thickness])
        back.get_prompt('Hide').set_formula('Hide', [Hide])
        back.get_prompt('Use Dovetail Construction').set_formula('Use_Dovetail_Construction', [Use_Dovetail_Construction])
        back.get_prompt('Box Type').set_formula('Box_Type', [Box_Type])

        bottom = common_parts.add_drawer_bottom(self)
        bottom.loc_x(value=sn_unit.inch(.3375))
        bottom.loc_y(value=sn_unit.inch(.3375))
        bottom.loc_z(value=sn_unit.inch(.5))
        bottom.rot_z(value=math.radians(90))
        bottom.dim_x(
            'IF(Override_Depth>0,Override_Depth,Drawer_Depth)-INCH(.625)',
            [Override_Depth, Drawer_Depth])
        bottom.dim_y(
            '(Drawer_Width+INCH(0.375)-INCH(.625))*-1',
            [Drawer_Width])
        bottom.dim_z('INCH(0.25)', [])
        bottom.get_prompt('Hide').set_formula('Hide', [Hide])
        bottom.get_prompt('Use Dovetail Construction').set_formula('Use_Dovetail_Construction', [Use_Dovetail_Construction])
        bottom.get_prompt('Box Type').set_formula('Box_Type', [Box_Type])
