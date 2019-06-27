# -*- coding: utf-8 -*-
"""
@author: BrianBlackwell
"""
import numpy as np
from numpy import cumsum
import scipy as sy
# import pylab as pyl
import os
import pandas as pd
from pandas.io import gbq
from datetime import datetime, timedelta
import time
from statistics import variance
from math import sin, cos, pi, radians


# Define EDR Data Triggers
ROTATE_THRESH = 25
BLOCK_THRESH = 15
BITTHRESH = 1
HOOKLOAD_THRESH = 55
FLOW_THRESH = 30
TRIP_THRESH = 150
CXN_THRESH = 30
Surface_Thresh = 200
Vertical_Thresh = 5600
Curve_Thresh = 6900


def phase2(startdate, rig_time, prev_rig_time, hole_depth, prev_hole_depth, bit_depth, prev_bit_depth, rop_i, hookload, block_height, prev_block_height, td_rpm, oscillator, flow_in, prev_bit_status, prev_slip_status, prev_pump_status, prev_time_elapsed, min20_hole_depth, prev_data_gap, DATA_FREQUENCY):
    day_num = None if rig_time is None or startdate is None else (
        startdate - rig_time).days + 1
    day_night = None if rig_time is None else 1 if (
        rig_time).hour >= 6 and (rig_time).hour < 18 else 2
    bit_status = 0 if hole_depth is None or bit_depth is None or rop_i is None else (2 if (float(hole_depth) - float(bit_depth) < BITTHRESH and float(hole_depth) > 0 and float(bit_depth) > 0 and float(rop_i) > 0 and int(
        int(prev_bit_status)) < 1) else (1 if (float(hole_depth) - float(bit_depth) < BITTHRESH and float(hole_depth) > 0 and float(bit_depth) > 0 and float(rop_i) > 0) else (-1 if int(int(prev_bit_status)) > 0 else 0)))
    slip_status = 0 if hookload is None else (2 if (int(bit_status) < 1 and float(hookload) < HOOKLOAD_THRESH and int(prev_slip_status) < 1) else (
        1 if (int(bit_status) < 1 and float(hookload) < HOOKLOAD_THRESH and int(prev_slip_status) > 0) else (-1 if int(prev_slip_status) > 0 else 0)))
    block_status = 0 if block_height is None or prev_block_height is None else 1 if (float(block_height) > float(
        prev_block_height)) else (-1 if (float(block_height) < float(prev_block_height)) else 0)
    pump_status = 0 if float(flow_in) is None else(2 if (float(flow_in) > FLOW_THRESH and int(
        prev_pump_status) < 1) else 1 if float(flow_in) > FLOW_THRESH else (-1 if int(prev_pump_status) > 0 else 0))
    rot_sli = 3 if td_rpm is None else(
        0 if oscillator > 0 else 1 if float(td_rpm) > ROTATE_THRESH else 0)
    time_elapsed = 0 if rig_time is None or prev_rig_time is None else (rig_time - prev_rig_time + timedelta(
        hours=float(prev_time_elapsed))) if (rig_time - prev_rig_time) < timedelta(hours=5) else timedelta(hours=float(prev_time_elapsed))
    data_gap = None if rig_time is None or prev_rig_time is None else (
        rig_time - prev_rig_time).total_seconds()
    trip_status = 0 if bit_depth is None or prev_bit_depth is None else (5 if int(bit_status) > 0 else (4 if float(hole_depth) - float(
        bit_depth) > TRIP_THRESH else (1 if float(bit_depth) > float(prev_bit_depth) else (-1 if float(prev_bit_depth) > float(bit_depth) else 0))))
    rig_activity = (0 if int(pump_status) == 0 or int(prev_pump_status) == 0 or int(pump_status) == 2 and rot_sli == 0 else 1 if int(
        pump_status) == 0 or int(prev_pump_status) == 0 or int(pump_status) == 2 and rot_sli == 1 else 2 if int(pump_status) == 1 and rot_sli == 0 else 3)
    clean_2 = 0 if hole_depth is None or prev_data_gap is None or prev_hole_depth is None or min20_hole_depth is None else float(
        hole_depth) if float(min20_hole_depth) == 0 and prev_data_gap > 60 else (-2 if float(prev_hole_depth) > float(min20_hole_depth) else 0)
    clean_1 = 2 if hole_depth is None or bit_depth is None or flow_in is None or rig_time is None else (2 if int(float(hole_depth)) - int(float(
        bit_depth)) > 2 else (3 if (float(hole_depth) - float(prev_hole_depth) <= 0) else (4 if float(flow_in) < 100 else(1 if rig_time == 0 else 0))))
    clean_3 = 9 if hole_depth is None or prev_hole_depth is None else 9 if float(
        hole_depth) == float(prev_hole_depth) and prev_data_gap > (DATA_FREQUENCY + 1) else 0

    return (day_num, day_night, bit_status, slip_status, block_status, pump_status, rot_sli, time_elapsed, data_gap, trip_status, rig_activity, clean_1, clean_2, clean_3)


def phase100(hole_depth, prev_hole_depth, max100_hole_depth, min20_hole_depth, bit_depth, prev_bit_depth, max100_bit_depth, min100_bit_depth, avg100_bit_depth, avg50_bit_depth, avg30_rot_sli, avg30_pump_status, flow_in, clean_2, max100_clean_2, prev_data_gap,savgol50):
    """Cleaning Algorithms to reduce data to determine a drilling only data set for drilling analytics processing"""
    clean_1 = 99 if hole_depth is None or prev_hole_depth is None or bit_depth is None or flow_in is None or max100_hole_depth is None else (2 if int(hole_depth) - int(
        bit_depth) > 2 else (3 if (float(hole_depth) - float(prev_hole_depth) <= 0) else (4 if flow_in < 100 else(6 if float(hole_depth) - float(max100_hole_depth) < 0 else 0))))
    clean_3 = 99 if hole_depth is None or prev_hole_depth is None else (9 if float(hole_depth) == float(
        prev_hole_depth) and prev_data_gap > 11 else (8 if max100_clean_2 > 10 and clean_2 == -2 else 0))
    bit_variance = (float(max100_bit_depth) - float(min100_bit_depth))
    # print(hole_depth, hole_depth, avg30_pump_status, avg30_rot_sli)
    trip_status2 = 4 if savgol50 > 2 and savgol50 < 12 else 6 if savgol50 < -2 and savgol50 > -12 else 0
    rig_activity2 = 0 if hole_depth is None or bit_depth is None else (5 if (clean_1 == 0 and clean_3 == 0) else 3 if ((float(hole_depth) - float(bit_depth)) > TRIP_THRESH and float(avg30_pump_status) > 0.95 and float(avg30_rot_sli) > 0.95) else 2 if ((float(hole_depth) - float(bit_depth)) > TRIP_THRESH and float(avg30_pump_status) > 0.95) else 4 if ((float(hole_depth) - float(bit_depth)) > TRIP_THRESH) and (float(bit_depth) - float(avg100_bit_depth)) < -0.25 else 6 if ((float(hole_depth) -
                                                                                                                                                                                                                                                                                                                                                                                                                                          float(bit_depth)) > TRIP_THRESH) and (float(bit_depth) - float(avg100_bit_depth)) > 0.25 else 7 if ((float(hole_depth) - float(bit_depth)) > TRIP_THRESH and float(bit_depth) < 1000) else 1 if ((float(bit_depth) - float(avg50_bit_depth)) < -0.2) else -1 if ((float(bit_depth) - float(avg50_bit_depth)) > 0.2) else 3 if (float(avg30_pump_status) > 0.05 and float(avg30_rot_sli) > 0.05) else 2 if (float(avg30_pump_status) > 0.05) else 0)
    # trip_out_number = None if rig_activity2 != 4 else prev_trip_out_number if hole_depth == prev_hole_depth and (rig_time - prev_trip_out).hours < timedelta(hours=10) else prev_trip_out_number + 1

    return (clean_1, clean_3, bit_variance, trip_status2, rig_activity2)


def drillitup2(hole_depth, prev_hole_depth, block_height, prev_block_height, prev_stand_number, rop_i, wob, td_torque, flow_rate, hole_size, motor_rpg, td_rpm):
    drilled_ft = 0 if hole_depth is None or prev_hole_depth is None else (
        float(hole_depth) - float(prev_hole_depth))
    stand_count = float(prev_stand_number) if block_height is None or prev_block_height is None else (
        1 if float(block_height) - float(prev_block_height) > BLOCK_THRESH else 0) + float(prev_stand_number)
    bit_rpm = 0 if td_rpm is None or flow_rate is None or motor_rpg is None else (
        float(td_rpm) + float(flow_rate) * float(motor_rpg))
    astra_mse = None if hole_size is None or rop_i is None or rop_i is None or td_torque is None else (0 if hole_size == 0 or float(rop_i) == 0 else float(
        wob) / (pi * hole_size * hole_size / 4) + (120 * pi * bit_rpm * float(td_torque)) / (pi * hole_size * hole_size * float(rop_i) / 4))

    return (drilled_ft, stand_count, astra_mse, bit_rpm)


def drillitup20(rop_i, avg20_rop_i, rop_a, avg20_rop_a, tf_grav, var20_tf_grav, tf_mag, var20_tf_mag, astra_mse, avg20_astra_mse, VSPlane, rot_sli, l5_rot_sli, next_rot_sli, prev_rot_sli, drilled_ft, bha, prev_bha, stand_number, prev_stand_number):
    normalized_tf = None if VSPlane is None or var20_tf_grav == var20_tf_mag == 0 or tf_mag is None or tf_grav is None else tf_grav if var20_tf_grav > var20_tf_mag else float(
        tf_mag) - float(VSPlane)
    slide_value_tf = None if drilled_ft is None or rot_sli == 1 or normalized_tf is None else (
        float(drilled_ft) * cos(radians(normalized_tf)))
    rop_i = None if rop_i is None or avg20_rop_i is None else (0 if float(rop_i) < 0 else float(
        avg20_rop_i) if float(rop_i) > float(avg20_rop_i) * 3 else float(rop_i))
    rop_a = None if rop_a is None or avg20_rop_a is None else (0 if float(rop_a) < 0 else float(
        avg20_rop_a) if float(rop_a) > float(avg20_rop_a) * 3 else float(rop_a))
    astra_mse = None if astra_mse is None else (0 if float(astra_mse) < 0 else float(avg20_astra_mse) if float(
        astra_mse) > float(avg20_astra_mse) * 2 else 0 if float(astra_mse) == np.inf else float(astra_mse))

    slide_status = (1 if float(next_rot_sli) != float(rot_sli) and float(l5_rot_sli) == 0 and bha == prev_bha and stand_number == prev_stand_number else 1 if ((bha != prev_bha or stand_number != prev_stand_number) and float(next_rot_sli) == float(rot_sli) == float(prev_rot_sli == 0))
                    else -1 if float(next_rot_sli) != float(rot_sli) and float(l5_rot_sli) == 1 and bha == prev_bha and stand_number == prev_stand_number else - 1 if (bha != prev_bha or stand_number != prev_stand_number) and float(next_rot_sli) == float(rot_sli) == float(prev_rot_sli) == 0 else 0)
    rot_status = (1 if float(next_rot_sli) != float(rot_sli) and float(rot_sli) == 1 else 1 if bha != prev_bha and float(next_rot_sli) == float(rot_sli) == float(prev_rot_sli) == 1 else 1 if stand_number != prev_stand_number and float(next_rot_sli) == float(rot_sli) == float(prev_rot_sli) == 1 else -
                  1 if float(next_rot_sli) != float(rot_sli) and float(rot_sli) == float(prev_rot_sli) == 0 else -1 if bha != prev_bha and float(next_rot_sli) == float(rot_sli) == float(prev_rot_sli) == 1 else -1 if stand_number != prev_stand_number and float(next_rot_sli) == float(rot_sli) == float(prev_rot_sli) == 1 else 0)

    return (normalized_tf, slide_value_tf, rop_i, rop_a, astra_mse, slide_status, rot_status)
