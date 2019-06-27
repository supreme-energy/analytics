# -*- coding: utf-8 -*-
"""
@author: BrianBlackwell
"""

# Pandas for data management
import pandas as pd


# numpy for number management
import numpy as np
import scipy as sy
from math import pi, radians, ceil, floor, cos, sin, acos, degrees, tan, atan


def bitproj_mc(previous_bitproj, calculated_tf, my, sli_length, bitto_sensor):
    """All of these values need pulled from the previous bit projection in the data base let If this is best formatted differently we can work through that."""
    md_1 = float(previous_bitproj.md)
    inc_1 = float(previous_bitproj.inc)
    azi_1 = float(previous_bitproj.azi)
    tvd_1 = float(previous_bitproj.tvd)
    north_1 = float(previous_bitproj.north)
    east_1 = float(previous_bitproj.east)
    v_sect_1 = float(previous_bitproj.vertical_section)
    lds_1 = float(previous_bitproj.dogleg)
    brate_1 = float(previous_bitproj.build_rate)
    trate_1 = float(previous_bitproj.turn_rate)

    """These values come from the associated plan file to the job"""
    VSPlane = 181  # VSPlane is the azi of the last entry of the active plan
    # VSPlan is the azi value of the closest (but smaller) entry to the md of the added bit projection
    VSPlan = 180

    """ These are the added values from the input required for the calculations"""
    calculated_tf = float(calculated_tf)
    my = float(my)
    sli_length = float(sli_length)
    projdist = float(bitto_sensor)

    """ first line of calculations done to get rest of projection values"""
    md = md_1 + projdist
    inc = inc_1 + my * sli_length / 100 * cos(calculated_tf)
    azi = azi_1 + my * sli_length / 100 * sin(calculated_tf)

    """Calculations to get the rest of the values"""

    dla = (acos(cos(radians(inc) - radians(inc_1)) - sin(radians(inc_1))
                * sin(radians(inc)) * (1 - cos(radians(azi) - radians(azi_1)))))
    dls = (degrees(acos(cos(radians(inc) - radians(inc_1)) - sin(radians(inc_1)) *
                        sin(radians(inc)) * (1 - cos(radians(azi) - radians(azi_1))))) / (md - md_1) * 100)
    if dla == 0:
        RF = 1
    else:
        RF = (2 / dla) * tan(dla / 2)

    north = north_1 + ((md - md_1) / 2 * (sin(radians(inc)) *
                                          cos(radians(azi)) + sin(radians(inc_1)) * cos(radians(azi_1))) * RF)
    east = east_1 + ((md - md_1) / 2 * (sin(radians(inc)) *
                                        sin(radians(azi)) + sin(radians(inc_1)) * sin(radians(azi_1))) * RF)
    tvd = tvd_1 + ((md - md_1) / 2 *
                   (cos(radians(inc)) + cos(radians(inc_1))) * RF)
    build_rate = ((inc_1 - inc) / (md - md_1) * 100)
    turn_rate = ((azi_1 - azi) / (md - md_1) * 100)
    calculated_tf = degrees(atan((east) / (north))) if VSPlan >= 0 and VSPlan < 90 else 180 + degrees(atan((east) / (north))
                                                                                                      ) if VSPlan >= 90 and VSPlan < 180 else 180 - degrees(atan((east) / (north))) if VSPlan >= 180 and VSPlan < 270 else 360 - degrees(atan((east) / (north)))
    calculated_ang = degrees(atan(
        (east) / (north))) if VSPlan >= 0 and VSPlan < 90 else 180 + degrees(atan((east) / (north)))

    return north, east, tvd, build_rate, turn_rate, calculated_tf, dls, md, inc, azi
