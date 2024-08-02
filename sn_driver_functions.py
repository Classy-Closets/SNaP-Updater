def IF(statement, true, false):
    """ Returns true if statement is true Returns false if statement is false:
        statement - conditional statement
        true - value to return if statement is True
        false - value to return if statement is False
    """
    if statement:
        return true
    else:
        return false


def OR(*vars):
    """ Returns True if ONE parameter is true
    """
    for var in vars:
        if var:
            return True
    return False


def AND(*vars):
    """ Returns True if ALL parameters are true
    """
    for var in vars:
        if not var:
            return False
    return True


def INCH(value):
    """ Converts value to meters: expecing value in inches
    """
    return value * .0254


def MILLIMETER(value):
    """ Converts value to meters: expecting value in millimeter
    """
    return value * .001


def LIMIT(val, val_min, val_max):
    """ Returns par1 if value is between min and max else
        the minimum or maximum value value will be returned
    """
    if val > val_max:
        return val_max
    elif val < val_min:
        return val_min
    else:
        return val


def PERCENTAGE(value, min, max):
    """ Returns Percentage amount based on the min and max values
    """
    return (value - min) / (max - min)


def CHECK(value, *vars):
    """ 
    """
    from . import sn_unit
    val = 0

    for var in vars:
        if round(sn_unit.meter_to_inch(value), 2) >= sn_unit.meter_to_inch(var):
            if var > val:
                val = var
    return val


def DOORHC(value):
    """ Returns the given value as the next closest door hole count
    """

    from .libraries.closets.common import common_lists as common_lists
    for index, height in enumerate(common_lists.DOOR_OPENING_HEIGHTS):
        door_height = round(value * 1000, 3)
        if not door_height > float(height[0]):
            return float(common_lists.DOOR_OPENING_HEIGHTS[index][0])/1000
