# -*- coding: utf-8 -*-
"""
Created on Sun Jun  2 21:27:17 2019

@author: BrianBlackwell
"""

# Pandas for data management
import pandas as pd
from pandas.io import gbq

#numpy for number management
import numpy as np
from numpy import cumsum, inf
import scipy as sy

# os methods for manipulating paths
import os

from os.path import dirname, join


livecalcs = pd.DataFrame([])
livedrill = pd.DataFrame([])
#livecalcs.columns =['data_gap','day_num', 'day_night','drlg_status','slip_status','block_status','pump_status','trip_status','trip_status2','rig_activity','rig_activity2','clean_1','clean_2','clean_3','tq_variance','bit_variance','normalized_tf','slide_count','rot_count','stand_count','astra_mse','slide_value_tf','drilled_ft','bit_rpm_t']
slip_status=0
pump_status=0
bit_status=0
prev_time_elapsed=0
prev_block_height=10
prev_stand_number=0
prev_data_gap=0
clean_1 =0
clean_2=0
clean_3=0
startdate=edrdata.ix[0,'rig_time'].replace(hour=0, minute=0, second=0, microsecond=0)
edrdata['pump_status']=0
edrdata['rot_sli']=0
edrdata['data_gap']=0
hole_size=8
motor_rpg =0.33
edrdata=edrdata[35000:42000]

for i in edrdata.index:
    if i > 35000:
        
        """ From EDR Processed Table"""
        prev_slip_status = slip_status
        prev_pump_status = pump_status
        prev_bit_status = bit_status

        """ From EDRRAW Table"""
        rig_time=edrdata.loc[i,'rig_time']
        prev_rig_time=edrdata.loc[i-1,'rig_time']
        prev_hole_depth=edrdata.loc[i-1,'hole_depth']
        prev_bit_depth=edrdata.loc[i-1,'bit_depth']
        hole_depth=edrdata.loc[i,'hole_depth']
        bit_depth=edrdata.loc[i,'bit_depth']
        rop_i=edrdata.loc[i,'rop_i']
        hookload=edrdata.loc[i,'hookload']
        block_height=edrdata.loc[i,'block_height']
        td_rpm=edrdata.loc[i,'td_rpm']
        flow_in=edrdata.loc[i,'flow_in']
        wob = edrdata.loc[i,'wob']
        td_torque = edrdata.loc[i,'td_torque']
        try:
            oscillator=edrdata.loc[i,'oscillator']
        except:
            oscillator = 0
            """ if more than 20 total points have been collected on the well: start updated at the 10th point"""
        if i > 35020:
            min20_hole_depth = edrdata.loc[i-10:i+10,'hole_depth'].min()
            prev_data_gap = edrdata.loc[i-1,'data_gap']
        else:
            min20_hole_depth = hole_depth
        x =phase2(startdate,rig_time,prev_rig_time,hole_depth,prev_hole_depth,bit_depth,prev_bit_depth,rop_i,hookload,block_height,prev_block_height,td_rpm,oscillator,flow_in,prev_bit_status, prev_slip_status, prev_pump_status, prev_time_elapsed,min20_hole_depth,prev_data_gap,i)   
        """ x =(day_num,day_night,bit_status,slip_status,block_status,pump_status,rot_sli,time_elapsed,data_gap,trip_status,rig_activity,clean_2) """
        
        df = pd.DataFrame(x).T
        livecalcs = livecalcs.append(df)
        edrdata.loc[i,'pump_status']= x[5]
        edrdata.loc[i,'rot_sli']= x[6]
        edrdata.loc[i,'datagap']= x[8]
        edrdata.loc[i,'clean_2']= x[12]
        if x[11]==0 and x[13] == 0:
               z1 = drillitup2(rig_time,prev_rig_time,hole_depth,prev_hole_depth,block_height,prev_block_height,prev_stand_number,rop_i,wob,td_torque, flow_in, hole_size, motor_rpg,td_rpm)
               dz1 = pd.DataFrame(z1).T
               livedrill = livedrill.append(dz1)
               
               prev_stand_number = z1[2]
               print("drilled")
        
        """ if more than 100 total points have been collected on the well: start updated at the 50th point"""
        
        if i> 35100: 
            j = i -50
            max100_hole_depth = edrdata.loc[j-50:j+50,'hole_depth'].max()
            min20_hole_depth = edrdata.loc[j-10:j+10,'hole_depth'].min()
            max100_bit_depth = edrdata.loc[j-50:j+50,'bit_depth'].max()
            min100_bit_depth = edrdata.loc[j-50:j+50,'bit_depth'].min()
            avg100_bit_depth = edrdata.loc[j-50:i+50,'bit_depth'].mean()
            avg50_bit_depth = edrdata.loc[j-25:j+25,'bit_depth'].mean()
            avg30_pump_status = edrdata.loc[j-15:j+15,'pump_status'].mean()
            avg30_rot_sli = edrdata.loc[j-15:j+15,'rot_sli'].mean()
            max100_clean_2 = edrdata.loc[j-50:j+50,'clean_2'].max()
            prev_data_gap = edrdata.loc[j-1,'data_gap']
            clean_2 = edrdata.loc[j,'clean_2']
            
            rig_time=edrdata.loc[j,'rig_time']
            prev_rig_time=edrdata.loc[j-1,'rig_time']
            prev_hole_depth=edrdata.loc[j-1,'hole_depth']
            prev_bit_depth=edrdata.loc[j-1,'bit_depth']
            hole_depth=edrdata.loc[j,'hole_depth']
            bit_depth=edrdata.loc[j,'bit_depth']
            rop_i=edrdata.loc[j,'rop_i']
            hookload=edrdata.loc[j,'hookload']
            block_height=edrdata.loc[j,'block_height']
            td_rpm=edrdata.loc[j,'td_rpm']
            flow_in=edrdata.loc[j,'flow_in']
            wob = edrdata.loc[j,'wob']
            td_rpm = edrdata.loc[j,'td_rpm']
            td_torque = edrdata.loc[j,'td_torque']
            flow_in = edrdata.loc[j,'flow_in']

            
            
            
            y = phase100(rig_time,hole_depth,prev_hole_depth,max100_hole_depth,min20_hole_depth,bit_depth,prev_bit_depth,max100_bit_depth,min100_bit_depth, avg100_bit_depth,avg50_bit_depth,avg30_rot_sli,avg30_pump_status,flow_in,max100_clean_2,clean_2,prev_data_gap,j)
            df = pd.DataFrame(x).T
            livecalcs = livecalcs.append(df)
            if y[0]==0 and y[1] == 0:
               z1 = drillitup2(rig_time,prev_rig_time,hole_depth,prev_hole_depth,block_height,prev_block_height,prev_stand_number,rop_i,wob,td_torque, flow_in, hole_size, motor_rpg,td_rpm,j)
               dz1 = pd.DataFrame(z1).T
               livedrill = livedrill.append(dz1)
               
               prev_stand_number = y[2]
               #z2 = drillitup20(rop_i,avg20_rop_i,rop_a,avg20_rop_a,tf_grav,var20_tf_grav,tf_mag,var20_tf_mag,astra_mse, avg20_astra_mse,VSPlane, rot_sli,l5_rot_sli,next_rot_sli,prev_rot_sli,drilled_ft,bha,prev_bha,stand_number,prev_stand_number,j)
            """y= (clean_1,clean_3,bit_variance,trip_status2,rig_activity2)*need to add bit variance here or above."""
        
        slip_status=x[3]
        block_status=x[4]
        pump_status=x[5]