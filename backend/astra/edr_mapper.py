# -*- coding: utf-8 -*-
"""
Created on Fri Dec 14 07:52:26 2018

@author: BrianBlackwell

This Script will map:
    
    1 Totco
    2 Pason
    3 MyWells
    
    Data into common channels to be calculated by the analyzer and loaded into the Astra Database for future use.
    
    The minimum required channels are:
        Date_Time	Hole_Depth	TVD	Bit_Depth	WOB	TD_RPM	TD_Torque	Diff_Press	ROP_A	Flow_In	Pump_Press	Total_SPM	Block_Height	Hookload	Overpull	Gamma_Ray	TF_Grav	TF_Mag	Svy_Azi	Svy_Inc
    
    The Currently Accepted "extra" Channels are:
        ROP_I	Flow_Out	Ann_Press	Back_Press	Oscillator	TF_ACC	Live_Inc	MSE_EDR	AD_ROP	AD_WOB	AD_DP	AD_TQ	Mud_TI	 Mud_TO Mud_WI Mud_WO EDR_RS1	EDR_RS2	EDR_RS3	EDR_SLIPS

data type if not supplied is determined by the value and naming convention of the date column. This may change as 
"""
import pandas as pd

def edrmapper(edrdata):
    if 'Date Time' in edrdata.columns:
        edrdata=edrdata.rename(index=str, columns={'Date Time':'rig_time', 'Hole Depth':'hole_depth', 'TVD':'tvd', 'Bit Position':'bit_depth', 'Bit Weight':'wob', 'Top Drive RPM':'td_rpm', 'Top Drive Torque':'td_torque', 'Diff Press':'diff_press', 'ROP - Average':'rop_a', 'Flow In Rate':'flow_in', 'Pump Pressure':'pump_press', 'Pump SPM - Total':'strokes_total', 'Block Height':'block_height', 'Hook Load':'hookload', 'Overpull':'overpull', 'Gamma Ray':'gamma_ray', 'Toolface Grav':'tf_grav', 'Toolface Mag':'tf_mag', 'Svy Azimuth':'svy_azi', 'Svy Inclination':'svy_inc'})
        try:
            edrdata=edrdata.rename(columns={'ROP - Fast':'rop_i'})
        except:
            pass
        
        edrdata=edrdata.rename(columns={'Flow Out Rate':'flow_out'})
        if 'flow_out' in edrdata.columns:
           pass 
        else:
            edrdata['flow_out']=None
        edrdata=edrdata.rename(columns={'Ann Pressure':'ann_press'})
        if 'ann_press' in edrdata.columns:
           pass 
        else:
            edrdata['ann_press']=None

        edrdata=edrdata.rename(columns={'Back Pressure':'back_press'})
        if 'back_press' in edrdata.columns:
           pass 
        else:
            edrdata['back_press']=None
        try:
            edrdata=edrdata.rename(columns={'Live Inc':'live_inc'})
        except:
            pass
        edrdata=edrdata.rename(columns={'Basic MSE':'edr_mse'})
        if 'edr_mse' in edrdata.columns:
           pass 
        else:
            edrdata['edr_mse']=None
        try:   
             edrdata=edrdata.rename(columns={'ROP - Auto Driller':'AD_ROP'})
        except:
            pass
        try:
            edrdata=edrdata.rename(columns={'Bit Wt. - Auto Driller':'AD_WOB'})
        except:
            pass

        edrdata=edrdata.rename(columns={'Mud Temp In':'mud_ti'})
        if 'mud_ti' in edrdata.columns:
           pass 
        else:
            edrdata['mud_ti']=None
        edrdata=edrdata.rename(columns={'Mud Temp Out':'mud_to'})
        if 'mud_to' in edrdata.columns:
           pass 
        else:
            edrdata['mud_to']=None
        edrdata=edrdata.rename(columns={'Mud Weight In':'mud_wi'})
        if 'mud_wi' in edrdata.columns:
           pass 
        else:
            edrdata['mud_wi']=None
        edrdata=edrdata.rename(columns={'Mud Weight Out':'mud_wo'})
        if 'mud_wo' in edrdata.columns:
           pass 
        else:
            edrdata['mud_wo']=None
            
        edrdata=edrdata.rename(columns={'Rig Activity':'edr_RS1'})
        if 'edr_RS1' in edrdata.columns:
           pass 
        else:
            edrdata['edr_RS1']=None
        edrdata=edrdata.rename(columns={'Rig Activity Code':'edr_RS2'})
        if 'edr_RS2' in edrdata.columns:
           pass 
        else:
            edrdata['edr_RS2']=None
        edrdata=edrdata.rename(columns={'Rig Activity SubCode':'edr_RS3'})
        if 'edr_RS3' in edrdata.columns:
           pass 
        else:
            edrdata['edr_RS3']=None
        edrdata=edrdata.rename(columns={'Slip Status':'edr_slips'})
        if 'edr_slips' in edrdata.columns:
           pass 
        else:
            edrdata['edr_slips']=False
            
        if 'oscillator' in edrdata.columns:
           pass 
        else:
            edrdata['oscillator']=False
            
            
    if 'YYYY/MM/DD' in edrdata.columns:

        edrdata['rig_time']= (edrdata['YYYY/MM/DD']+'T'+edrdata['HH:MM:SS'])
        edrdata['rig_time']=pd.to_datetime(edrdata['rig_time'])
        edrdata=edrdata.rename(index=str, columns={'Hole Depth (feet)':'hole_depth', 'True Vertical Depth (feet)':'tvd', 'Bit Depth (feet)':'bit_depth', 'Weight on Bit (klbs)':'wob', 'Rotary RPM (RPM)':'td_rpm', 'Rotary Torque (unitless)':'td_torque', 'Differential Pressure (psi)':'diff_press', 'Overall ROP (ft_per_hr)':'rop_a', 'Total Pump Output (gal_per_min)':'flow_in', 'Standpipe Pressure (psi)':'pump_press', 'Pump Total Strokes Rate (SPM)':'strokes_total', 'Block Height (feet)':'block_height', 'Hook Load (klbs)':'hookload', 'Over Pull (klbs)':'overpull', 'Gamma (api)':'gamma_ray', 'Gravity Toolface (degrees)':'tf_grav', 'Magnetic Toolface (degrees)':'tf_mag', 'Azimuth (degrees)':'svy_azi', 'Inclination (degrees)':'svy_inc'})
        try:
            edrdata=edrdata.rename(columns={'EDR Instantaneous ROP (ft_per_hr)':'rop_i'})
        except:
            pass
        edrdata=edrdata.rename(columns={'Flow Out Rate':'flow_out'})
        if 'flow_out' in edrdata.columns:
           pass 
        else:
            edrdata['flow_out']=None
        edrdata=edrdata.rename(columns={'Ann Pressure':'ann_press'})
        if 'ann_press' in edrdata.columns:
           pass 
        else:
            edrdata['ann_press']=None

        edrdata=edrdata.rename(columns={'Back Pressure':'back_press'})
        if 'back_press' in edrdata.columns:
           pass 
        else:
            edrdata['back_press']=None
        try:
            edrdata=edrdata.rename(columns={'Live Inc':'live_inc'})
        except:
            pass
        
        edrdata=edrdata.rename(columns={'Relative MSE (unitless)':'edr_mse'})
        if 'edr_mse' in edrdata.columns:
           pass 
        else:
            edrdata['edr_mse']=None
        try:
            edrdata=edrdata.rename(columns={'ROP - Auto Driller':'AD_ROP'})
        except:
            pass
        try:
            edrdata=edrdata.rename(columns={'Bit Wt. - Auto Driller':'AD_WOB'})
        except:
            pass

        edrdata=edrdata.rename(columns={'Mud Temp In':'mud_ti'})
        if 'mud_ti' in edrdata.columns:
           pass 
        else:
            edrdata['mud_ti']=None
        edrdata=edrdata.rename(columns={'Mud Temp Out':'mud_to'})
        if 'mud_to' in edrdata.columns:
           pass 
        else:
            edrdata['mud_to']=None
        edrdata=edrdata.rename(columns={'Mud Weight In':'mud_wi'})
        if 'mud_wi' in edrdata.columns:
           pass 
        else:
            edrdata['mud_wi']=None
        edrdata=edrdata.rename(columns={'Mud Weight Out':'mud_wo'})
        if 'mud_wo' in edrdata.columns:
           pass 
        else:
            edrdata['mud_wo']=None
            
        edrdata=edrdata.rename(columns={'Rig Activity':'edr_RS1'})
        if 'edr_RS1' in edrdata.columns:
           pass 
        else:
            edrdata['edr_RS1']=None
        edrdata=edrdata.rename(columns={'Rig Activity Code':'edr_RS2'})
        if 'edr_RS2' in edrdata.columns:
           pass 
        else:
            edrdata['edr_RS2']=None
        edrdata=edrdata.rename(columns={'Rig Activity SubCode':'edr_RS3'})
        if 'edr_RS3' in edrdata.columns:
           pass 
        else:
            edrdata['edr_RS3']=None
        edrdata=edrdata.rename(columns={'Slip Status':'edr_slips'})
        if 'edr_slips' in edrdata.columns:
           pass 
        else:
            edrdata['edr_slips']=False
            
        if 'oscillator' in edrdata.columns:
           pass 
        else:
            edrdata['oscillator']=False


    return edrdata