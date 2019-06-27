# -*- coding: utf-8 -*-
"""
@author: BrianBlackwell
"""

# Pandas for data management
import pandas as pd
from pandas.io import gbq

# numpy for number management
import numpy as np
import scipy as sy
from math import pi, radians, ceil, floor, cos, sin, acos, degrees, tan, atan


def survey_mc(previous_survey, inc, azi, md):
    """All of these values need pulled from the previous survey in the data base let If this is best formatted differently we can work through that."""
    md_1 = float(previous_survey.md)
    inc_1 = float(previous_survey.inc)
    azi_1 = float(previous_survey.azi)
    tvd_1 = float(previous_survey.tvd)
    north_1 = float(previous_survey.north)
    east_1 = float(previous_survey.east)
    v_sect_1 = float(previous_survey.vertical_section)
    lds_1 = float(previous_survey.dogleg)
    brate_1 = float(previous_survey.build_rate)
    trate_1 = float(previous_survey.turn_rate)
    stepout_1 = float(previous_survey.step_out)

    """These values come from the associated plan file to the job"""
    VSPlane = 181  # VSPlane is the azi of the last entry of the active plan
    # VSPlan is the azi value of the closest (but smaller) entry to the md of the added survey
    VSPlan = 180

    # """ These are the added values from the input required for the calculations"""
    inc = float(inc)
    azi = float(azi)
    md = float(md)

    """Calculations to get the rest of the survey values"""

    dla = (acos(cos(radians(inc) - radians(inc_1)) - sin(radians(inc_1)) *
                sin(radians(inc)) * (1 - cos(radians(azi) - radians(azi_1)))))
    dls = 0 if (md - md_1) == 0 else (degrees(acos(cos(radians(inc) - radians(inc_1)) - sin(radians(inc_1))
                                                   * sin(radians(inc)) * (1 - cos(radians(azi) - radians(azi_1))))) / (md - md_1) * 100)
    if dla == 0:
        RF = 1
    else:
        RF = (2 / dla) * tan(dla / 2)

    north = north_1 + ((md - md_1) / 2 * (sin(radians(inc)) * cos(radians(azi)
                                                                  ) + sin(radians(inc_1)) * cos(radians(azi_1))) * RF)
    east = east_1 + ((md - md_1) / 2 * (sin(radians(inc)) * sin(radians(azi)) +
                                        sin(radians(inc_1)) * sin(radians(azi_1))) * RF)
    tvd = tvd_1 + ((md - md_1) / 2 *
                   (cos(radians(inc)) + cos(radians(inc_1))) * RF)
    build_rate = 0 if (md - md_1) == 0 else ((inc_1 - inc) / (md - md_1) * 100)
    turn_rate = 0 if (md - md_1) == 0 else ((azi_1 - azi) / (md - md_1) * 100)
    calculated_tf = degrees(atan((east))) if north == 0 or north is None else degrees(atan((east) / (north))) if VSPlan >= 0 and VSPlan < 90 else 180 + degrees(atan(
        (east) / (north))) if VSPlan >= 90 and VSPlan < 180 else 180 - degrees(atan((east) / (north))) if VSPlan >= 180 and VSPlan < 270 else 360 - degrees(atan((east) / (north)))
    calculated_ang = degrees(atan((east))) if north == 0 or north is None else degrees(atan(
        (east) / (north))) if VSPlan >= 0 and VSPlan < 90 else 180 + degrees(atan((east) / (north)))
    step_out = stepout_1 + ((md - md_1) * sin(radians(VSPlane - azi)) if VSPlane >
                            90 and VSPlane < 180 else (md - md_1) * sin(radians(azi - VSPlane)))

    return north, east, tvd, build_rate, turn_rate, calculated_tf, calculated_ang, step_out, dls
