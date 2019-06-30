# -*- coding: utf-8 -*-
"""
Created on Sat April 21 14:53:57 2018

@author: BrianBlackwell
"""
import numpy as np
from numpy import cumsum, inf
import scipy as sy
import pylab as pyl
import os
import pandas as pd
from pandas.io import gbq
from datetime import datetime
import time
from decimal import *

from statistics import variance
from scipy.stats import linregress
from scipy.ndimage import gaussian_filter
from scipy.signal import savgol_filter

from datetime import datetime,date
import math
from math import sin,cos,pi,radians
#************************* CONSTANTS   ********************************c*********************************8

#Define EDR Data Triggers
ROTATE_THRESH = 25
BLOCK_THRESH = 15
BITTHRESH = 1
HOOKLOAD_THRESH = 55
FLOW_THRESH = 30

#Define EDR Data Columns
"""Define what kind of a data source is being brought in Pason or totco
Will need to update this based on feed type to properly understand channels and how they are calculated/ signal quality and accuracy calculations

"""

def drillitup(edrdata,VSPlane):

    #create dataframe from only drilling data
    drilldata =  edrdata[edrdata['clean_1'] == 0]
    drilldata =  drilldata[drilldata['clean_3'] == 0]
    drilldata['edrindex'] = drilldata.index.astype(int)
    drilldata=drilldata.reset_index(drop = True)
    drilldata['dedrindex'] = drilldata.index.astype(int)
    #drilldata = drilldata.reset_index(drop=False)
    maxdepth = sy.maximum.accumulate(drilldata['hole_depth'])

    #drilldata['clean_2'] = list(map(lambda w,x: w-x, drilldata['rig_time'],drilldata['rig_time'].shift(1)))
    drilldata['bit_rpm']=drilldata['td_rpm']
    drilldata['normalized_tf'] = list(map(lambda w,x,y,z: (y if w>= x else 0 if z<-900 else z-VSPlane),drilldata['tf_grav'].rolling(20).var(),drilldata['tf_mag'].rolling(20).var(),drilldata['tf_grav'],drilldata['tf_mag']))
    drilldata['rop_i'] = list(map(lambda w,y: (0 if w< 0 else y if w>y*3 else w),drilldata['rop_i'],drilldata['rop_i'].rolling(50).mean()))
    drilldata['rop_a'] = list(map(lambda w,y: (0 if w< 0 else y if w>y*3 else w),drilldata['rop_i'],drilldata['rop_i'].rolling(50).mean()))
    drilldata['drilled_ft'] = list(map(lambda w,y: 0 if y is None or math.isnan(y) else w-y, drilldata['hole_depth'],drilldata['hole_depth'].shift(1)))
    drilldata['stand_count'] = list(map(lambda w,x: (1 if w-x > BLOCK_THRESH else 0), drilldata['block_height'],drilldata['block_height'].shift(1)))
    drilldata['stand_count']= list(cumsum(drilldata['stand_count'])+1)
    drilldata['svygol']=savgol_filter(drilldata['svy_inc'], window_length=3, polyorder=2, deriv=1)
  #drilldata['time_elapsed'] = list(map(lambda w,x: (w-x)/ np.timedelta64(1, 'h'), drlldata['rig_time'],drilldata['rig_time'].shift(1)))
    #drilldata['Toolface_Norm']= list(map(lambda w,x: (w-x)/ np.timedelta64(1, 'h'), drilldata['rig_time'],drilldata['rig_time'].shift(1)))
    #Cells(E, normalized_tf_C).FormulaR1C1 = "=IF(RC" & Mag_TF_Indicator & "=1, IF(R[-1]C" & Magnetic_TF_C & ">RC" & SVYS_AZI_C & ",R[-1]C" & Magnetic_TF_C & "-RC" & SVYS_AZI_C & ",360+R[-1]C" & Magnetic_TF_C & "-RC" & SVYS_AZI_C & "), R[-1]C" & Gravity_TF_C & ")"
    drilldata['time_elapsed'] = drilldata['time_elapsed'].cumsum()
    drilldata['astra_mse']= list(map(lambda hs,wob,tq,brpm,ropi: None if hs == 0 or hs is None or ropi == 0 or ropi is None or brpm is None else wob/(pi*hs*hs/4)+(120*pi*brpm*tq)/(pi*hs*hs*ropi/4),drilldata['hole_size'],drilldata['wob'],drilldata['td_torque'],drilldata['bit_rpm'],drilldata['rop_i']))
    drilldata['astra_mse'] = list(map(lambda w,y,z: (0 if w< 0 else y if w>y*2 else 0 if w==np.inf else w),drilldata['astra_mse'],drilldata['astra_mse'].rolling(20).mean(),drilldata['astra_mse'].shift(-1)))
    drilldata['flow_in'] = list(map(lambda w,y,z: (0 if w< 0 else y if w>y*2 else 0 if w==np.inf else w),drilldata['flow_in'],drilldata['flow_in'].rolling(20).mean(),drilldata['flow_in'].shift(-1)))
    
    drilldata['slide_value_tf']= list(map(lambda w,x2,x1,y: (0 if w==1 or math.isnan(x1) else (x2-x1)*cos(radians(y))), drilldata['rot_sli'],drilldata['hole_depth'],drilldata['hole_depth'].shift(1), drilldata['normalized_tf']))
    #drilldata['Lat_L']=drilldata['hole_depth']-Curve_Thresh
    #drilldata['A_interval_code']= list(map(lambda y: (1 if y =="Surface" or y =="surface" or y =="surf" or y =="S" else 2 if y =="Intermediate" or y =="intermediate" or y =="int" or y =="I" else 3 if y =="Curve" or y =="curve" or y =="c" or y =="C" else 4 if y =="Lateral" or y =="lateral" or y =="lat" or y =="L" else 7 if y =="Vertical" or y =="vertical" or y =="vert" or y =="V" else 8 if y =="Drillout" or y =="drillout" or y =="drill out" or y =="DO" else 11), drilldata['A_interval']))
    # Cells(2, Directional_Info + 14).FormulaR1C1 = "=IFERROR(ABS(INDIRECT(""Drill_Only!CF""&RC" & Basics + 8 & ")-INDIRECT(""Drill_Only!CF""&RC" & Basics + 7 & "))/RC" & Param_Sliding + 1 & ",0)"
    
    drilldata['normalized_tf']=drilldata['normalized_tf'].round(decimals = 3)
    drilldata['rop_a']=drilldata['rop_a'].round(decimals = 3)
    drilldata['rop_i']=drilldata['rop_i'].round(decimals = 3)
    drilldata['astra_mse']=drilldata['astra_mse'].round(decimals = 3)
    drilldata['drilled_ft']=drilldata['drilled_ft'].round(decimals = 3)
    drilldata['slide_value_tf']=drilldata['slide_value_tf'].round(decimals = 3)
    return (drilldata)

def finish_bhas(drilldata,bhas,DATA_FREQUENCY):
    bhas_drilled =pd.DataFrame(columns =['id', 'drill_depth_in', 'drill_depth_out', 'total_rop', 'sliding_rop', 'rotating_rop','footage_drilled','feet_slid','feet_rotated', 'sliding_hrs', 'rotating_hrs','drilling_hrs'])
   
    for i in drilldata['bha_id'].unique():
        current_bha =drilldata[drilldata['bha_id']==i]
        total_rop = drilldata['rop_a'].mean()
        rotating = current_bha[current_bha['rot_sli']==1]
        rotating_ft = rotating['drilled_ft'].sum()
        rotating_rop = rotating['rop_a'].mean()
        rotating_hrs =len(rotating)*DATA_FREQUENCY/(3600)
        
        drill_time_start = current_bha['rig_time'].min()
        drill_time_end = current_bha['rig_time'].max()
        drill_depth_start = current_bha['hole_depth'].min()
        drill_depth_end = current_bha['hole_depth'].max()
        footage_drilled = drill_depth_end-drill_depth_start
        drilling_hrs =len(current_bha)*DATA_FREQUENCY/(3600)
        
        sliding = current_bha[current_bha['rot_sli']==0]
        sliding_ft = footage_drilled-rotating_ft #sliding['drilled_ft'].sum()
        sliding_rop = sliding['rop_a'].mean()
        sliding_hrs =drilling_hrs - rotating_hrs #len(sliding)*DATA_FREQUENCY/(3600)
        
        arow =[ i, drill_depth_start, drill_depth_end, total_rop, sliding_rop, rotating_rop,footage_drilled,sliding_ft,rotating_ft,sliding_hrs,rotating_hrs,drilling_hrs]
        bhas_drilled.loc[len(bhas_drilled)] = arow
        
        #bhas=pd.merge(bhas,bhas_drilled, on='id')
    
    return(bhas_drilled)

def Tourism(drilldata):
    #Tour Analysis
    TourData = drilldata.sort_values('hole_depth', ascending=True).drop_duplicates(['day_num'], keep='first').reset_index(drop=False)
    TourData1 = drilldata.sort_values('hole_depth', ascending=True).drop_duplicates(['day_num'], keep='last').reset_index(drop=False)
    TourData.rename(columns={"index": "Full EDR Start","rig_time": "rig_time Start","hole_depth": "hole_depth Start", "bit_depth": "hole_depth End", "block_height": "Footage Drilled","tvd": "tvd Start"},inplace=True)

    TourData.insert(0, 'Array Code', 7)
    TourData.insert(1, 'A_interval_code', 0)
    TourData.insert(3, 'Full EDR End', TourData1['index'])
    TourData.insert(5, 'rig_time End', TourData1['rig_time'])
    TourData['hole_depth End'] = TourData1['hole_depth']
    #TourData['tvd End'] = TourData1['tvd']
    return (TourData)   
    #analyzer2.columns = ['ROP Avg (Rotating)','	wob Avg (Rotating)','td_rpm Avg (Rotating)','bit rpm Avg (Rotating)','diff_pressure Avg (Rotating)','Flow Rate Avg (Rotating)','pump_press (Rotating) ','td_torque Avg (Rotating) ','ROP Ratio	Max ROP','Best ROP','Above AVG ROP','Below AVG ROP','Min ROP','Max wob	Best wob','Above AVG wob','Below AVG wob','Min wob','Max Differential pressure','Best Differential pressure','Above AVG Differential pressure','Below AVG Differential pressure','Min Differential pressure','Max bit rpms','Best bit rpms','Above AVG bit rpms','Below AVG bit rpms','Min bit rpms']


def SlideSheet(drilldata):
    drilldata['slide_count']=0
    drilldata['rot_count']=0
    pdate = date.today()
    #c,conn, engine = connection()
    S_THRESH =10
    act=1
    
    slidesheet =pd.DataFrame(columns =['Slide Number','Rotation Number','Start Depth','End Depth','Length','ROP', 'Effective TF'])
    drilldata['Slide Start']=list(map(lambda w0,w1,w2,x0,x1,x2,y0,y1,y2,y3,y4,y5,y6,z: (1 if z!=y0 and y0==y1==y2==y3==y4==y5==0 and (w1 == w2) and (x1==x2) else 1 if x0 != x1 and z==y0==y1==0 else 1 if w0 != w1 and z==y0==y1==0 else 0), drilldata['A_bha_num'].shift(1),drilldata['A_bha_num'],drilldata['A_bha_num'].shift(-1),drilldata['stand_count'].shift(1),drilldata['stand_count'],drilldata['stand_count'].shift(-1),drilldata['rot_sli'],drilldata['rot_sli'].shift(-1),drilldata['rot_sli'].shift(-2),drilldata['rot_sli'].shift(-3),drilldata['rot_sli'].shift(-4),drilldata['rot_sli'].shift(-5),drilldata['rot_sli'].shift(-6),drilldata['rot_sli'].shift(1)))
    drilldata['Slide End']=list(map(lambda w0,w1,x0,x1,y0,y1,y2,y3,y4,y5,y6,z: (-1 if z!=y0 and y0==y1==y2==y3==y4==y5==1 and (w0 == w1) and (x0==x1) else -1 if x0 != x1 and z==y0==y1==0 else -1 if w0 != w1 and z==y0==y1==0 else 0), drilldata['A_bha_num'].shift(-1),drilldata['A_bha_num'],drilldata['stand_count'].shift(-1),drilldata['stand_count'],drilldata['rot_sli'],drilldata['rot_sli'].shift(-1),drilldata['rot_sli'].shift(-2),drilldata['rot_sli'].shift(-3),drilldata['rot_sli'].shift(-4),drilldata['rot_sli'].shift(-5),drilldata['rot_sli'].shift(-6),drilldata['rot_sli'].shift(1)))
    
    sstart=drilldata[drilldata['Slide Start']==1]
    send=drilldata[drilldata['Slide End']==-1]
    BT="Slides"
    
    Q=I=snum=0
    for I in send.index:
       SS = sstart.index[sstart.index < I].max()
       if SS>Q:
           Q= SS
           MDS =float(drilldata.loc[Q, 'hole_depth'])
           MDE = float(drilldata.loc[I, 'hole_depth'])
           FD =float(MDE-MDS)
           if FD >  S_THRESH:  
                WID = 1
                AC = int(17)
                IC= int(drilldata.loc[Q,'A_interval_code'])
                BHAN = int(drilldata.loc[Q, 'A_bha_num'])
                DN = int(drilldata.loc[Q, 'day_num'])
                WSN = int(drilldata.loc[Q,'stand_count'])

                idata =  drilldata[ drilldata['hole_depth'] <= MDS]; idata =  drilldata[ drilldata['hole_depth'] > MDE]

                FSLI =idata[idata['rot_sli']==0]
                DTS=(idata['rig_time'].iloc[1])
                DTE=(idata['rig_time'].iloc[-1])
                SlidFT = float(FSLI['drilled_ft'].sum())
                TFE=float(FSLI['slide_value_tf'].sum()/SlidFT*100)
                if SlidFT > S_THRESH:

                    
                    #c.execute("INSERT INTO ASTRA_ARRAYS (WELL_ID,ARRAY_CODE,INTERVAL_CODE,BHA_NUM,DAY_NUM,WELL_STAND_NUM, hole_depth_START, hole_depth_END,FOOTAGE_DRILLED,tvd_START, tvd_END,FEDR_I_START,FEDR_I_End,DEDR_I_START,DEDR_I_End,DT_START,DT_End,Total_Hours,D_Hours,rop_aVG,TOOLFACE_EFFICIENCY_PCT,SLIDING_FOOTAGE,SLIDE_PCT_T,SubmitDate,active,rop_aVG_SLIDING, wob_AVG_SLIDING, TOP_DRIVE_RPM_AVG_SLIDING, BIT_RPM_AVG_SLIDING, FLOW_RATE_AVG_SLIDING, diff_pressURE_AVG_SLIDING, pump_pressURE_SLIDING, TOP_DRIVE_TORQUE_AVG_SLIDING,rop_aVG_ROTATING, wob_AVG_ROTATING, TOP_DRIVE_RPM_AVG_ROTATING, BIT_RPM_AVG_ROTATING, diff_pressURE_AVG_ROTATING, FLOW_RATE_AVG_ROTATING, pump_pressURE_ROTATING, TOP_DRIVE_TORQUE_AVG_ROTATING,SLIDE_PCT_D,svy_inc_START,svy_inc_End,BreakdownType) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(WID,AC,IC,BHAN,DN,WSN,MDS,MDE,FD,tvdS,tvdE,FIS,FIE,DIS,DIE,DTS,DTE,TT,DT,ROPA,TFE,SlidFT,SPCT,pdate,1,SROPA,SwobA,STRPMA,SBRPMA,SFRA,SDPA,SPPA,STQA,RROPA,RwobA,RTRPMA,RBRPMA,RFRA,RDPA,RPPA,RTQA,SPCTD,INCS,INCE,BT))
                    #conn.commit()
                    drilldata['slide_count']= list(map(lambda x,y: (snum if x>=DTS and x<=DTE else y),drilldata['rig_time'],drilldata['slide_count']))
                    snum += 1
           
    

    drilldata['Rotate Start']=list(map(lambda w0,w1,x0,x1,y0,y1,y2,y3,y4,y5,y6,z: (1 if z!=y0 and y0==1 else 1 if x0 != x1 and z==y0==y1==1 else 1 if w0 != w1 and z==y0==y1==1 else 0), drilldata['A_bha_num'].shift(1),drilldata['A_bha_num'],drilldata['stand_count'].shift(1),drilldata['stand_count'],drilldata['rot_sli'],drilldata['rot_sli'].shift(1),drilldata['rot_sli'].shift(-2),drilldata['rot_sli'].shift(-3),drilldata['rot_sli'].shift(-4),drilldata['rot_sli'].shift(-5),drilldata['rot_sli'].shift(-6),drilldata['rot_sli'].shift(1)))
    drilldata['Rotate End']=list(map(lambda w0,w1,x0,x1,y0,y1,y2,y3,y4,y5,y6,z: (-1 if z!=y0 and y0==y1==0 else -1 if x0 != x1 and z==y0==y1==1 else -1 if w0 != w1 and z==y0==y1==1 else 0), drilldata['A_bha_num'].shift(-1),drilldata['A_bha_num'],drilldata['stand_count'].shift(-1),drilldata['stand_count'],drilldata['rot_sli'],drilldata['rot_sli'].shift(-1),drilldata['rot_sli'].shift(-2),drilldata['rot_sli'].shift(-3),drilldata['rot_sli'].shift(-4),drilldata['rot_sli'].shift(-5),drilldata['rot_sli'].shift(-6),drilldata['rot_sli'].shift(1)))
    rstart=drilldata[drilldata['Rotate Start']==1]
    rend=drilldata[drilldata['Rotate End']==-1]
    Q=I=rnum=0
    BT ="Rotations"
    for I in rend.index:
       SS = rstart.index[rstart.index < I].max()
       if SS>Q:
           Q= int(SS)
           MDS= float(drilldata.loc[Q, 'hole_depth'])
           MDE= float(drilldata.loc[I, 'hole_depth'])
           FD =float(MDE-MDS)
           if FD >  S_THRESH: 
                AC = int(18)
                IC= int(drilldata.loc[Q,'A_interval_code'])
                BHAN = int(drilldata.loc[Q, 'A_bha_num'])
                DN = int(drilldata.loc[Q, 'day_num'])
                WSN = int(drilldata.loc[Q,'stand_count'])

                idata =  drilldata[ drilldata['hole_depth'] <= MDS]; idata =  drilldata[ drilldata['hole_depth'] > MDE]
                DTS=(idata['rig_time'].iloc[1])
                DTE=(idata['rig_time'].iloc[-1]) #.strftime("%Y-%m-%d %H:%M:%S")


                #c.execute("INSERT INTO ASTRA_ARRAYS (WELL_ID,ARRAY_CODE,INTERVAL_CODE,BHA_NUM,DAY_NUM,WELL_STAND_NUM, hole_depth_START, hole_depth_END,FOOTAGE_DRILLED,tvd_START, tvd_END,FEDR_I_START,FEDR_I_End,DEDR_I_START,DEDR_I_End,DT_START,DT_End,Total_Hours,D_Hours,rop_aVG,TOOLFACE_EFFICIENCY_PCT,SLIDING_FOOTAGE,SLIDE_PCT_T,SubmitDate,active,rop_aVG_SLIDING, wob_AVG_SLIDING, TOP_DRIVE_RPM_AVG_SLIDING, BIT_RPM_AVG_SLIDING, FLOW_RATE_AVG_SLIDING, diff_pressURE_AVG_SLIDING, pump_pressURE_SLIDING, TOP_DRIVE_TORQUE_AVG_SLIDING,rop_aVG_ROTATING, wob_AVG_ROTATING, TOP_DRIVE_RPM_AVG_ROTATING, BIT_RPM_AVG_ROTATING, diff_pressURE_AVG_ROTATING, FLOW_RATE_AVG_ROTATING, pump_pressURE_ROTATING, TOP_DRIVE_TORQUE_AVG_ROTATING,SLIDE_PCT_D,svy_inc_START,svy_inc_End,BreakdownType) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(WID,AC,IC,BHAN,DN,WSN,MDS,MDE,FD,tvdS,tvdE,FIS,FIE,DIS,DIE,DTS,DTE,TT,DT,ROPA,TFE,SlidFT,SPCT,pdate,1,SROPA,SwobA,STRPMA,SBRPMA,SFRA,SDPA,SPPA,STQA,RROPA,RwobA,RTRPMA,RBRPMA,RFRA,RDPA,RPPA,RTQA,SPCTD,INCS,INCE,BT))
                #conn.commit()
                drilldata['rot_count']= list(map(lambda x,y: (rnum if x>=DTS and x<=DTE else y),drilldata['rig_time'],drilldata['rot_count']))
                rnum += 1

     #, FOOTAGE_DRILLED, tvd_START, tvd_END, FEDR_I_START, FEDR_I_END, DEDR_I_START, DEDR_I_END, DT_START, DT_END, TOTAL_HOURS, D_HOURS, DC_HOURS, NON_DRILLING_TIME, RT_TIME, svy_inc_START, svy_inc_END, svy_inc_CHANGE, SVY_AZI_START, SVY_AZI_END, SVY_ROW_START, SVY_ROW_END, SVY_VERTICAL_SECTION_START, SVY_VERTICAL_SECTION_END, tvd_CHANGE, PLAN_NORTHING, PLAN_EASTING, STEP_OUT, PLAN_INC_START, PLAN_INC_END, PLAN_INC_CHANGE, PLAN_AZI_START, PLAN_AZI_END, PLAN_ROW_START, PLAN_ROW_END, PLAN_VERTICAL_SECTION_START, PLAN_VERTICAL_SECTION_END, PLAN_tvd_START, PLAN_tvd_END, PLAN_STEP_OUT, DIRECTIONAL_DIFFICULTY, DIRECTION, PERCENT_IN_ZONE, PLANNED_BURS, YIELDED_BURS, PLANNED_DLR, YIELDED_DLR, YIELD_RATIO, PLANNED_COURSE_LENGTH, COURSE_LENGTH, COURSE_LENGTH_DEVIATION, UP_DOWN, RIGHT_LEFT, AHEAD_BEHIND, TOOLFACE_EFFICIENCY_PCT, MOTOR_BUR_YIELD, MOTOR_DLS_YIELD, rop_aVG, wob_AVG, TOP_DRIVE_RPM_AVG, BIT_RPM_AVG, diff_pressURE_AVG, FLOW_RATE_AVG, PRESSURE_AVG, TOP_DRIVE_TORQUE_AVG, NUM_OF_SLIDES, SLIDING_FOOTAGE, AVG_SLIDE_LENGTH, SLIDE_PCT_D, SLIDE_PCT_T, rop_aVG_SLIDING, wob_AVG_SLIDING, TOP_DRIVE_RPM_AVG_SLIDING, BIT_RPM_AVG_SLIDING, FLOW_RATE_AVG_SLIDING, diff_pressURE_AVG_SLIDING, pump_pressURE_SLIDING, TOP_DRIVE_TORQUE_AVG_SLIDING, SIDES_UP_HIGHSIDE_NORTH, SLIDES_RIGHT_EAST, SLIDES_DOWN_LOWSIDE_SOUTH, SLIDES_LEFT_WEST, ROTATING_FOOTAGE, ROTATE_PCT_D, ROTATE_PCT_T, rop_aVG_ROTATING, wob_AVG_ROTATING, TOP_DRIVE_RPM_AVG_ROTATING, BIT_RPM_AVG_ROTATING, diff_pressURE_AVG_ROTATING, FLOW_RATE_AVG_ROTATING, pump_pressURE_ROTATING, TOP_DRIVE_TORQUE_AVG_ROTATING, ROP_RATIO, MAX_ROP, BEST_ROP, ABOVE_AVG_ROP, BELOW_AVG_ROP, MIN_ROP, MAX_wob, BEST_wob, ABOVE_AVG_wob, BELOW_AVG_wob, MIN_wob, MAX_diff_pressURE, BEST_diff_pressURE, ABOVE_AVG_diff_pressURE, BELOW_AVG_diff_pressURE, MIN_diff_pressURE, MAX_BIT_RPMS, BEST_BIT_RPMS, ABOVE_AVG_BIT_RPMS, BELOW_AVG_BIT_RPMS, MIN_BIT_RPMS, ASTRA_ARRAYScol, SubmitDate, active              
    slidesheet = slidesheet.sort_values(['Start Depth'], ascending=[1])
    slidesheet=slidesheet.reset_index(drop = True)
    
    return (drilldata)                   

 
def SurveySlideSheet(drilldata,surveydata):  
    #SurveySlide Sheet Analysis
    for i in range(1,len(surveydata)-1): 
        SVRSURVEY = drilldata[drilldata['survey number']== i]
        SVYft =SVRSURVEY['drilled_ft'].sum()
        Slidesurvey =SVRSURVEY[SVRSURVEY['rot_sli']==0]
        Rotatesurvey =SVRSURVEY[SVRSURVEY['rot_sli']==1]
        #sliTF =
        slift = Slidesurvey['drilled_ft'].sum()
        slipct =slift/SVYft
        slistart = Slidesurvey['hole_depth'].min()
        slistart = Slidesurvey['hole_depth'].max()
        
        rotft =Rotatesurvey['drilled_ft'].sum()
        rotpct =rotft/SVYft
        rottart =Rotateurvey['hole_depth'].min()
        rotstart = Rotateurvey['hole_depth'].max()
        
        arow2 =[CXNC,CDepth, Tour,FXCT,FXCT2,OBTS,STS,STOB,PCC,PTP,S,PoffS,SinS,SoutE,PonE,E]
        Connections.loc[len(Connections)] = arow2
    SURVData1 = drilldata.sort_values('hole_depth', ascending=True).drop_duplicates(['stand_count'], keep='first')
    SURVData = drilldata.sort_values('hole_depth', ascending=True).drop_duplicates(['stand_count'], keep='last')
    return (StandData)    

def SlipNSlide(drilldata):     
    #Slide Data
    SlideData =drilldata.copy()
    SlideData.loc[SlideData['rot_sli']==1] = np.nan
    return (SlideData)

def Roundwego(drilldata):    
    RotateData =drilldata.copy()
    RotateData.loc[RotateData['rot_sli']==0] = np.nan
    return (RotateData)



def AstraArrays(drilldata,edrdata,welln):
    #sets todays date to verify when the analyzer was run to be compared to version control.
    pdate = date.today()
    c,conn, engine = connection()
    Arraydata =pd.DataFrame(columns =['WELL_ID','ARRAY_CODE','A_interval_CODE','BHA_NUM','DAY_NUM','WELL_STAND_NUM', 'hole_depth_START', 'hole_depth_END','FOOTAGE_DRILLED','tvd_START', 'tvd_END','FEDR_I_START','FEDR_I_End','DEDR_I_START','DEDR_I_End','DT_START','DT_End','Total_Hours','D_Hours','rop_aVG','TOOLFACE_EFFICIENCY_PCT','SLIDING_FOOTAGE','SLIDE_PCT_D','SubmitDate'])
    
    # checks to see if this well already has been run by tha analyzer
    y =c.execute("SELECT * FROM ASTRA_ARRAYS WHERE (WELL_ID,active) = (%s,%s)", (welln,1))
    if int(y) > 0:
        c.execute("UPDATE ASTRA_ARRAYS SET active='0' WHERE WELL_ID= (%s)", (welln))
    
    #sets todays date to verify when the analyzer was run to be compared to version control.
    WID = 12
    AC = int(13)
    IC= None
    BT="Full Well"
    BHAN = int(drilldata['A_bha_num'].max())
    DN = int(drilldata['day_num'].max())
    WSN = int(drilldata['stand_count'].max())
    MDS= float(drilldata['hole_depth'].min())
    MDE= float(drilldata['hole_depth'].max())
    FD =float(MDE-MDS)
    tvdS= float(drilldata['tvd'].min())
    tvdE= float(drilldata['tvd'].max())
    INCS= float(drilldata['svy_inc'].min())
    INCE= float(drilldata['svy_inc'].max())
    FIS= int(drilldata['edrindex'].iloc[1])
    FIE= int(drilldata['edrindex'].iloc[-1])
    DIS= int(drilldata['dedrindex'].iloc[1])
    DIE= int(drilldata['dedrindex'].iloc[-1])
    DTS=(drilldata['rig_time'].iloc[1]).strftime("%Y-%m-%d %H:%M:%S")
    DTE=(drilldata['rig_time'].iloc[-1]).strftime("%Y-%m-%d %H:%M:%S")
    DT =float(drilldata.loc[DIE, 'time_elapsed'] - drilldata.loc[DIS, 'time_elapsed'])
    TT=float(edrdata.loc[FIE, 'time_elapsed'] - edrdata.loc[FIS, 'time_elapsed'])
    ROPA= int(drilldata['rop_a'].mean())
    FSLI =drilldata[drilldata['rot_sli']==0]
    FROT =drilldata[drilldata['rot_sli']==1]
    RPCT=float(len(FROT.index)/len(drilldata.index))
    SPCT=float(1-RPCT)
    SlidFT = float(FSLI['drilled_ft'].sum())
    if SlidFT <5:
        TFE=None
    else:
        TFE=float(FSLI['slide_value_tf'].sum()/SlidFT*100)
    
    RPCTD=int(FROT['drilled_ft'].sum())/FD
    SPCTD = 1-RPCTD
    RROPA=int(FROT['rop_a'].mean())
    RwobA=int(FROT['wob'].mean())
    RTQA=int(FROT['td_torque'].mean())
    RDPA=int(FROT['diff_press'].mean())
    RPPA=int(FROT['pump_press'].mean())
    RTRPMA=int(FROT['td_rpm'].mean())
    RBRPMA=int(FROT['bit_rpm'].mean())
    RFRA=int(FROT['flow_in'].mean())
    
    SROPA=int(FSLI['rop_a'].mean())
    SwobA=int(FSLI['wob'].mean())
    STQA=int(FSLI['td_torque'].mean())
    SDPA=int(FSLI['diff_press'].mean())
    SPPA=int(FSLI['pump_press'].mean())
    STRPMA=int(FSLI['td_rpm'].mean())
    SBRPMA=int(FSLI['bit_rpm'].mean())
    SFRA=int(FSLI['flow_in'].mean())
    

    arow2 =[WID,AC,IC,BHAN,DN,WSN,MDS,MDE,FD,tvdS,tvdE,FIS,FIE,DIS,DIE,DTS,DTE,TT,DT,ROPA,TFE,SlidFT,SPCT,pdate]
    Arraydata.loc[len(Arraydata)] = arow2

    c.execute("INSERT INTO ASTRA_ARRAYS (WELL_ID,ARRAY_CODE,INTERVAL_CODE,BHA_NUM,DAY_NUM,WELL_STAND_NUM, hole_depth_START, hole_depth_END,FOOTAGE_DRILLED,tvd_START, tvd_END,FEDR_I_START,FEDR_I_End,DEDR_I_START,DEDR_I_End,DT_START,DT_End,Total_Hours,D_Hours,rop_aVG,TOOLFACE_EFFICIENCY_PCT,SLIDING_FOOTAGE,SLIDE_PCT_T,SubmitDate,active,rop_aVG_SLIDING, wob_AVG_SLIDING, TOP_DRIVE_RPM_AVG_SLIDING, BIT_RPM_AVG_SLIDING, FLOW_RATE_AVG_SLIDING, diff_pressURE_AVG_SLIDING, pump_pressURE_SLIDING, TOP_DRIVE_TORQUE_AVG_SLIDING,rop_aVG_ROTATING, wob_AVG_ROTATING, TOP_DRIVE_RPM_AVG_ROTATING, BIT_RPM_AVG_ROTATING, diff_pressURE_AVG_ROTATING, FLOW_RATE_AVG_ROTATING, pump_pressURE_ROTATING, TOP_DRIVE_TORQUE_AVG_ROTATING,SLIDE_PCT_D,svy_inc_START,svy_inc_End,BreakdownType) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(WID,AC,IC,BHAN,DN,WSN,MDS,MDE,FD,tvdS,tvdE,FIS,FIE,DIS,DIE,DTS,DTE,TT,DT,ROPA,TFE,SlidFT,SPCT,pdate,1,SROPA,SwobA,STRPMA,SBRPMA,SFRA,SDPA,SPPA,STQA,RROPA,RwobA,RTRPMA,RBRPMA,RFRA,RDPA,RPPA,RTQA,SPCTD,INCS,INCE,BT))
    conn.commit()

    BHADataS = drilldata.sort_values('hole_depth', ascending=True).drop_duplicates(['A_bha_num'], keep='first').reset_index(drop=True)
    BHADataE = drilldata.sort_values('hole_depth', ascending=True).drop_duplicates(['A_bha_num'], keep='last').reset_index(drop=True)
    
    for R in BHADataS.index:
        AC = int(14)
        BT="BHAs"

        IC= int(BHADataS.loc[R,'A_interval_code'])
        BHAN = int(BHADataS.loc[R, 'A_bha_num'])
        if BHAN > 0:
            idata = drilldata[drilldata['A_bha_num'] == BHAN]
            DN = int(BHADataS.loc[R, 'day_num'])
            WSN = int(BHADataS.loc[R,'stand_count'])
            MDS= float(BHADataS.loc[R, 'hole_depth'])
            MDE= float(BHADataE.loc[R, 'hole_depth'])
            FD =float(MDE-MDS)
            tvdS= float(BHADataS.loc[R,'tvd'])
            tvdE= float(BHADataE.loc[R,'tvd'])
            INCS =float(BHADataS.loc[R,'svy_inc'])
            INCE =float(BHADataE.loc[R,'svy_inc'])
            FIS= int(BHADataS.loc[R,'edrindex'])
            FIE= int(BHADataE.loc[R,'edrindex'])
            DIS= int(BHADataS.loc[R,'dedrindex'])
            DIE= int(BHADataE.loc[R,'dedrindex'])
            DTS=(BHADataS.loc[R,'rig_time']).strftime("%Y-%m-%d %H:%M:%S")
            DTE=(BHADataE.loc[R,'rig_time']).strftime("%Y-%m-%d %H:%M:%S")
            DT =float(drilldata.loc[DIE, 'time_elapsed'] - drilldata.loc[DIS, 'time_elapsed'])
            TT=float(edrdata.loc[FIE, 'time_elapsed'] - edrdata.loc[FIS, 'time_elapsed'])
            ROPA= int(idata['rop_a'].mean())
            FSLI =idata[idata['rot_sli']==0]
            FROT =idata[idata['rot_sli']==1]
            RPCT=float(len(FROT.index)/len(idata.index))
            SPCT=float(1-RPCT)
            SlidFT = float(FSLI['drilled_ft'].sum())
            ROTFT = float(FROT['drilled_ft'].sum())
            if SlidFT <5:
                TFE=None
            else:
                TFE=float(FSLI['slide_value_tf'].sum()/SlidFT*100)
            RPCTD=int(FROT['drilled_ft'].sum())/FD
            SPCTD = 1-RPCTD    
            if SlidFT <5:
                SFRA=SBRPMA=STRPMA=SPPA=SDPA=STQA=SwobA=SROPA=TFE=None
            else:
                TFE=float(FSLI['slide_value_tf'].sum()/SlidFT*100)
                SROPA=int(FSLI['rop_a'].mean())
                SwobA=int(FSLI['wob'].mean())
                STQA=int(FSLI['td_torque'].mean())
                SDPA=int(FSLI['diff_press'].mean())
                SPPA=int(FSLI['pump_press'].mean())
                STRPMA=int(FSLI['td_rpm'].mean())
                SBRPMA=int(FSLI['bit_rpm'].mean())
                SFRA=int(FSLI['flow_in'].mean())
                
            if ROTFT <5:
                RFRA=RBRPMA=RTRPMA=RPPA=RDPA=RTQA=RwobA=RROPA=None
            else:
                RROPA=int(FROT['rop_a'].mean())
                RwobA=int(FROT['wob'].mean())
                RTQA=int(FROT['td_torque'].mean())
                RDPA=int(FROT['diff_press'].mean())
                RPPA=int(FROT['pump_press'].mean())
                RTRPMA=int(FROT['td_rpm'].mean())
                RBRPMA=int(FROT['bit_rpm'].mean())
                RFRA=int(FROT['flow_in'].mean())
            
            
            arow2 =[WID,AC,IC,BHAN,DN,WSN,MDS,MDE,FD,tvdS,tvdE,FIS,FIE,DIS,DIE,DTS,DTE,TT,DT,ROPA,TFE,SlidFT,SPCT,pdate]
            Arraydata.loc[len(Arraydata)] = arow2
            c.execute("INSERT INTO ASTRA_ARRAYS (WELL_ID,ARRAY_CODE,INTERVAL_CODE,BHA_NUM,DAY_NUM,WELL_STAND_NUM, hole_depth_START, hole_depth_END,FOOTAGE_DRILLED,tvd_START, tvd_END,FEDR_I_START,FEDR_I_End,DEDR_I_START,DEDR_I_End,DT_START,DT_End,Total_Hours,D_Hours,rop_aVG,TOOLFACE_EFFICIENCY_PCT,SLIDING_FOOTAGE,SLIDE_PCT_T,SubmitDate,active,rop_aVG_SLIDING, wob_AVG_SLIDING, TOP_DRIVE_RPM_AVG_SLIDING, BIT_RPM_AVG_SLIDING, FLOW_RATE_AVG_SLIDING, diff_pressURE_AVG_SLIDING, pump_pressURE_SLIDING, TOP_DRIVE_TORQUE_AVG_SLIDING,rop_aVG_ROTATING, wob_AVG_ROTATING, TOP_DRIVE_RPM_AVG_ROTATING, BIT_RPM_AVG_ROTATING, diff_pressURE_AVG_ROTATING, FLOW_RATE_AVG_ROTATING, pump_pressURE_ROTATING, TOP_DRIVE_TORQUE_AVG_ROTATING,SLIDE_PCT_D,svy_inc_START,svy_inc_End,BreakdownType) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(WID,AC,IC,BHAN,DN,WSN,MDS,MDE,FD,tvdS,tvdE,FIS,FIE,DIS,DIE,DTS,DTE,TT,DT,ROPA,TFE,SlidFT,SPCT,pdate,1,SROPA,SwobA,STRPMA,SBRPMA,SFRA,SDPA,SPPA,STQA,RROPA,RwobA,RTRPMA,RBRPMA,RFRA,RDPA,RPPA,RTQA,SPCTD,INCS,INCE,BT))
            conn.commit()
    INTDataS = drilldata.sort_values('hole_depth', ascending=True).drop_duplicates(['A_interval'], keep='first').reset_index(drop=True)
    INTDataE = drilldata.sort_values('hole_depth', ascending=True).drop_duplicates(['A_interval'], keep='last').reset_index(drop=True)
    
    for R in INTDataS.index:
        AC = int(15)
        BT="Intervals"
        IC= int(INTDataS.loc[R,'A_interval_code'])
        if IC >0:
            BHAN = int(INTDataE.loc[R, 'A_bha_num']-INTDataS.loc[R, 'A_bha_num']+1)
            idata = drilldata[drilldata['A_interval_code'] == IC]
            DN = int(INTDataS.loc[R, 'day_num'])
            WSN = int(INTDataS.loc[R,'stand_count'])
            MDS= float(INTDataS.loc[R, 'hole_depth'])
            MDE= float(INTDataE.loc[R, 'hole_depth'])
            FD =float(MDE-MDS)
            tvdS= float(INTDataS.loc[R,'tvd'])
            tvdE= float(INTDataE.loc[R,'tvd'])
            INCS =float(INTDataS.loc[R,'svy_inc'])
            INCE =float(INTDataE.loc[R,'svy_inc'])
            FIS= int(INTDataS.loc[R,'edrindex'])
            FIE= int(INTDataE.loc[R,'edrindex'])
            DIS= int(INTDataS.loc[R,'dedrindex'])
            DIE= int(INTDataE.loc[R,'dedrindex'])
            DTS=(INTDataS.loc[R,'rig_time']).strftime("%Y-%m-%d %H:%M:%S")
            DTE=(INTDataE.loc[R,'rig_time']).strftime("%Y-%m-%d %H:%M:%S")
            DT =float(drilldata.loc[DIE, 'time_elapsed'] - drilldata.loc[DIS, 'time_elapsed'])
            TT=float(edrdata.loc[FIE, 'time_elapsed'] - edrdata.loc[FIS, 'time_elapsed'])
            ROPA= int(idata['rop_a'].mean())
            FSLI =idata[idata['rot_sli']==0]
            FROT =idata[idata['rot_sli']==1]
            RPCT=float(len(FROT.index)/len(idata.index))
            SPCT=float(1-RPCT)
            SlidFT = float(FSLI['drilled_ft'].sum())
            ROTFT = float(FROT['drilled_ft'].sum())
            if SlidFT <5:
                TFE=None
            else:
                TFE=float(FSLI['slide_value_tf'].sum()/SlidFT*100)
            
            RPCTD=int(FROT['drilled_ft'].sum())/FD
            SPCTD = 1-RPCTD            
            if SlidFT <5:
                SFRA=SBRPMA=STRPMA=SPPA=SDPA=STQA=SwobA=SROPA=TFE=None
            else:
                TFE=float(FSLI['slide_value_tf'].sum()/SlidFT*100)
                SROPA=int(FSLI['rop_a'].mean())
                SwobA=int(FSLI['wob'].mean())
                STQA=int(FSLI['td_torque'].mean())
                SDPA=int(FSLI['diff_press'].mean())
                SPPA=int(FSLI['pump_press'].mean())
                STRPMA=int(FSLI['td_rpm'].mean())
                SBRPMA=int(FSLI['bit_rpm'].mean())
                SFRA=int(FSLI['flow_in'].mean())
                
            if ROTFT <5:
                RFRA=RBRPMA=RTRPMA=RPPA=RDPA=RTQA=RwobA=RROPA=None
            else:
                RROPA=int(FROT['rop_a'].mean())
                RwobA=int(FROT['wob'].mean())
                RTQA=int(FROT['td_torque'].mean())
                RDPA=int(FROT['diff_press'].mean())
                RPPA=int(FROT['pump_press'].mean())
                RTRPMA=int(FROT['td_rpm'].mean())
                RBRPMA=int(FROT['bit_rpm'].mean())
                RFRA=int(FROT['flow_in'].mean())
            
            RPCTD=int(FROT['drilled_ft'].sum())/FD
            SPCTD = 1-RPCTD  
            
            
            arow2 =[WID,AC,IC,BHAN,DN,WSN,MDS,MDE,FD,tvdS,tvdE,FIS,FIE,DIS,DIE,DTS,DTE,TT,DT,ROPA,TFE,SlidFT,SPCT,pdate]
            Arraydata.loc[len(Arraydata)] = arow2
            c.execute("INSERT INTO ASTRA_ARRAYS (WELL_ID,ARRAY_CODE,INTERVAL_CODE,BHA_NUM,DAY_NUM,WELL_STAND_NUM, hole_depth_START, hole_depth_END,FOOTAGE_DRILLED,tvd_START, tvd_END,FEDR_I_START,FEDR_I_End,DEDR_I_START,DEDR_I_End,DT_START,DT_End,Total_Hours,D_Hours,rop_aVG,TOOLFACE_EFFICIENCY_PCT,SLIDING_FOOTAGE,SLIDE_PCT_T,SubmitDate,active,rop_aVG_SLIDING, wob_AVG_SLIDING, TOP_DRIVE_RPM_AVG_SLIDING, BIT_RPM_AVG_SLIDING, FLOW_RATE_AVG_SLIDING, diff_pressURE_AVG_SLIDING, pump_pressURE_SLIDING, TOP_DRIVE_TORQUE_AVG_SLIDING,rop_aVG_ROTATING, wob_AVG_ROTATING, TOP_DRIVE_RPM_AVG_ROTATING, BIT_RPM_AVG_ROTATING, diff_pressURE_AVG_ROTATING, FLOW_RATE_AVG_ROTATING, pump_pressURE_ROTATING, TOP_DRIVE_TORQUE_AVG_ROTATING,SLIDE_PCT_D,svy_inc_START,svy_inc_End,BreakdownType) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(WID,AC,IC,BHAN,DN,WSN,MDS,MDE,FD,tvdS,tvdE,FIS,FIE,DIS,DIE,DTS,DTE,TT,DT,ROPA,TFE,SlidFT,SPCT,pdate,1,SROPA,SwobA,STRPMA,SBRPMA,SFRA,SDPA,SPPA,STQA,RROPA,RwobA,RTRPMA,RBRPMA,RFRA,RDPA,RPPA,RTQA,SPCTD,INCS,INCE,BT))
            conn.commit()
        
        
    FormDataS = drilldata.sort_values('hole_depth', ascending=True).drop_duplicates(['A_formations'], keep='first').reset_index(drop=True)
    FormDataE = drilldata.sort_values('hole_depth', ascending=True).drop_duplicates(['A_formations'], keep='last').reset_index(drop=True)
    
    for R in FormDataS.index:
        AC = int(42)
        BT="Formations"
        IC= int(FormDataS.loc[R,'A_interval_code'])
        FN =FormDataS.loc[R,'A_formations']
        BHAN = int(FormDataE.loc[R, 'A_bha_num']-FormDataS.loc[R, 'A_bha_num']+1)
        
        idata = drilldata[drilldata['A_formations'] == FN]
        DN = int(FormDataS.loc[R, 'day_num'])
        WSN = int(FormDataS.loc[R,'stand_count'])
        MDS= float(FormDataS.loc[R, 'hole_depth'])
        MDE= float(FormDataE.loc[R, 'hole_depth'])
        FD =float(MDE-MDS)
        tvdS= float(FormDataS.loc[R,'tvd'])
        tvdE= float(FormDataE.loc[R,'tvd'])
        INCS =float(FormDataS.loc[R,'svy_inc'])
        INCE =float(FormDataE.loc[R,'svy_inc'])
        FIS= int(FormDataS.loc[R,'edrindex'])
        FIE= int(FormDataE.loc[R,'edrindex'])
        DIS= int(FormDataS.loc[R,'dedrindex'])
        DIE= int(FormDataE.loc[R,'dedrindex'])
        DTS=(FormDataS.loc[R,'rig_time']).strftime("%Y-%m-%d %H:%M:%S")
        DTE=(FormDataE.loc[R,'rig_time']).strftime("%Y-%m-%d %H:%M:%S")
        DT =float(drilldata.loc[DIE, 'time_elapsed'] - drilldata.loc[DIS, 'time_elapsed'])
        TT=float(edrdata.loc[FIE, 'time_elapsed'] - edrdata.loc[FIS, 'time_elapsed'])
        ROPA= int(idata['rop_a'].mean())
        FSLI =idata[idata['rot_sli']==0]
        FROT =idata[idata['rot_sli']==1]
        RPCT=float(len(FROT.index)/len(idata.index))
        SPCT=float(1-RPCT)
        SlidFT = float(FSLI['drilled_ft'].sum())
        ROTFT = float(FROT['drilled_ft'].sum())
        if SlidFT <5:
            TFE=None
        else:
            TFE=float(FSLI['slide_value_tf'].sum()/SlidFT*100)
        
        RPCTD=int(FROT['drilled_ft'].sum())/FD
        SPCTD = 1-RPCTD            
        if SlidFT <5:
            SFRA=SBRPMA=STRPMA=SPPA=SDPA=STQA=SwobA=SROPA=TFE=None
        else:
            TFE=float(FSLI['slide_value_tf'].sum()/SlidFT*100)
            SROPA=int(FSLI['rop_a'].mean())
            SwobA=int(FSLI['wob'].mean())
            STQA=int(FSLI['td_torque'].mean())
            SDPA=int(FSLI['diff_press'].mean())
            SPPA=int(FSLI['pump_press'].mean())
            STRPMA=int(FSLI['td_rpm'].mean())
            SBRPMA=int(FSLI['bit_rpm'].mean())
            SFRA=int(FSLI['flow_in'].mean())
            
        if ROTFT <5:
            RFRA=RBRPMA=RTRPMA=RPPA=RDPA=RTQA=RwobA=RROPA=None
        else:
            RROPA=int(FROT['rop_a'].mean())
            RwobA=int(FROT['wob'].mean())
            RTQA=int(FROT['td_torque'].mean())
            RDPA=int(FROT['diff_press'].mean())
            RPPA=int(FROT['pump_press'].mean())
            RTRPMA=int(FROT['td_rpm'].mean())
            RBRPMA=int(FROT['bit_rpm'].mean())
            RFRA=int(FROT['flow_in'].mean())
        
        RPCTD=int(FROT['drilled_ft'].sum())/FD
        SPCTD = 1-RPCTD  
        
        
        arow2 =[WID,AC,IC,BHAN,DN,WSN,MDS,MDE,FD,tvdS,tvdE,FIS,FIE,DIS,DIE,DTS,DTE,TT,DT,ROPA,TFE,SlidFT,SPCT,pdate]
        Arraydata.loc[len(Arraydata)] = arow2
        c.execute("INSERT INTO ASTRA_ARRAYS (WELL_ID,ARRAY_CODE,INTERVAL_CODE,BHA_NUM,DAY_NUM,WELL_STAND_NUM, hole_depth_START, hole_depth_END,FOOTAGE_DRILLED,tvd_START, tvd_END,FEDR_I_START,FEDR_I_End,DEDR_I_START,DEDR_I_End,DT_START,DT_End,Total_Hours,D_Hours,rop_aVG,TOOLFACE_EFFICIENCY_PCT,SLIDING_FOOTAGE,SLIDE_PCT_T,SubmitDate,active,rop_aVG_SLIDING, wob_AVG_SLIDING, TOP_DRIVE_RPM_AVG_SLIDING, BIT_RPM_AVG_SLIDING, FLOW_RATE_AVG_SLIDING, diff_pressURE_AVG_SLIDING, pump_pressURE_SLIDING, TOP_DRIVE_TORQUE_AVG_SLIDING,rop_aVG_ROTATING, wob_AVG_ROTATING, TOP_DRIVE_RPM_AVG_ROTATING, BIT_RPM_AVG_ROTATING, diff_pressURE_AVG_ROTATING, FLOW_RATE_AVG_ROTATING, pump_pressURE_ROTATING, TOP_DRIVE_TORQUE_AVG_ROTATING,SLIDE_PCT_D,svy_inc_START,svy_inc_End,BreakdownType) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(WID,AC,IC,BHAN,DN,WSN,MDS,MDE,FD,tvdS,tvdE,FIS,FIE,DIS,DIE,DTS,DTE,TT,DT,ROPA,TFE,SlidFT,SPCT,pdate,1,SROPA,SwobA,STRPMA,SBRPMA,SFRA,SDPA,SPPA,STQA,RROPA,RwobA,RTRPMA,RBRPMA,RFRA,RDPA,RPPA,RTQA,SPCTD,INCS,INCE,BT))
        conn.commit()
        
        
    StandDataS = drilldata.sort_values('hole_depth', ascending=True).drop_duplicates(['stand_count'], keep='first').reset_index(drop=True)
    StandDataE = drilldata.sort_values('hole_depth', ascending=True).drop_duplicates(['stand_count'], keep='last').reset_index(drop=True)
    
    for R in StandDataS.index:
        AC = int(16)
        BT = "Stands"
        IC= int(StandDataS.loc[R,'A_interval_code'])
        BHAN = int(StandDataS.loc[R, 'A_bha_num'])
        DN = int(StandDataS.loc[R, 'day_num'])
        WSN = int(StandDataS.loc[R,'stand_count'])
        idata = drilldata[drilldata['stand_count'] == WSN]
        MDS= float(StandDataS.loc[R, 'hole_depth'])
        MDE= float(StandDataE.loc[R, 'hole_depth'])
        FD =float(MDE-MDS)
        tvdS= float(StandDataS.loc[R,'tvd'])
        tvdE= float(StandDataE.loc[R,'tvd'])
        INCS =float(StandDataS.loc[R,'svy_inc'])
        INCE =float(StandDataE.loc[R,'svy_inc'])
        FIS= int(StandDataS.loc[R,'edrindex'])
        FIE= int(StandDataE.loc[R,'edrindex'])
        DIS= int(StandDataS.loc[R,'dedrindex'])
        DIE= int(StandDataE.loc[R,'dedrindex'])
        DTS=(StandDataS.loc[R,'rig_time']).strftime("%Y-%m-%d %H:%M:%S")
        DTE=(StandDataE.loc[R,'rig_time']).strftime("%Y-%m-%d %H:%M:%S")
        DT =float(drilldata.loc[DIE, 'time_elapsed'] - drilldata.loc[DIS, 'time_elapsed'])
        TT=float(edrdata.loc[FIE, 'time_elapsed'] - edrdata.loc[FIS, 'time_elapsed'])
        ROPA= int(idata['rop_i'].mean())
        FSLI =idata[idata['rot_sli']==0]
        FROT =idata[idata['rot_sli']==1]
        RPCT=float(len(FROT.index)/len(idata.index))
        SPCT=float(1-RPCT)
        SlidFT = float(FSLI['drilled_ft'].sum())
        ROTFT = float(FROT['drilled_ft'].sum())
        if SlidFT <5:
            SFRA=SBRPMA=STRPMA=SPPA=SDPA=STQA=SwobA=SROPA=TFE=None
        else:
            TFE=float(FSLI['slide_value_tf'].sum()/SlidFT*100)
            SROPA=int(FSLI['rop_a'].mean())
            SwobA=int(FSLI['wob'].mean())
            STQA=int(FSLI['td_torque'].mean())
            SPPA=int(FSLI['pump_press'].mean())
            STRPMA=int(FSLI['td_rpm'].mean())
            SBRPMA=int(FSLI['bit_rpm'].mean())
            SFRA=int(FSLI['flow_in'].mean())
            
        if ROTFT <5:
            RFRA=RBRPMA=RTRPMA=RPPA=RDPA=RTQA=RwobA=RROPA=None
        else:
            RROPA=int(FROT['rop_a'].mean())
            RwobA=int(FROT['wob'].mean())
            RTQA=int(FROT['td_torque'].mean())
            RDPA=int(FROT['diff_press'].mean())
            RPPA=int(FROT['pump_press'].mean())
            RTRPMA=int(FROT['td_rpm'].mean())
            RBRPMA=int(FROT['bit_rpm'].mean())
            RFRA=int(FROT['flow_in'].mean())
            
        RPCTD=int(FROT['drilled_ft'].sum())/FD
        SPCTD = 1-RPCTD      


        
        arow2 =[WID,AC,IC,BHAN,DN,WSN,MDS,MDE,FD,tvdS,tvdE,FIS,FIE,DIS,DIE,DTS,DTE,TT,DT,ROPA,TFE,SlidFT,SPCT,pdate]
        Arraydata.loc[len(Arraydata)] = arow2
        c.execute("INSERT INTO ASTRA_ARRAYS (WELL_ID,ARRAY_CODE,INTERVAL_CODE,BHA_NUM,DAY_NUM,WELL_STAND_NUM, hole_depth_START, hole_depth_END,FOOTAGE_DRILLED,tvd_START, tvd_END,FEDR_I_START,FEDR_I_End,DEDR_I_START,DEDR_I_End,DT_START,DT_End,Total_Hours,D_Hours,rop_aVG,TOOLFACE_EFFICIENCY_PCT,SLIDING_FOOTAGE,SLIDE_PCT_T,SubmitDate,active,rop_aVG_SLIDING, wob_AVG_SLIDING, TOP_DRIVE_RPM_AVG_SLIDING, BIT_RPM_AVG_SLIDING, FLOW_RATE_AVG_SLIDING, diff_pressURE_AVG_SLIDING, pump_pressURE_SLIDING, TOP_DRIVE_TORQUE_AVG_SLIDING,rop_aVG_ROTATING, wob_AVG_ROTATING, TOP_DRIVE_RPM_AVG_ROTATING, BIT_RPM_AVG_ROTATING, diff_pressURE_AVG_ROTATING, FLOW_RATE_AVG_ROTATING, pump_pressURE_ROTATING, TOP_DRIVE_TORQUE_AVG_ROTATING,SLIDE_PCT_D,svy_inc_START,svy_inc_End,BreakdownType) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(WID,AC,IC,BHAN,DN,WSN,MDS,MDE,FD,tvdS,tvdE,FIS,FIE,DIS,DIE,DTS,DTE,TT,DT,ROPA,TFE,SlidFT,SPCT,pdate,1,SROPA,SwobA,STRPMA,SBRPMA,SFRA,SDPA,SPPA,STQA,RROPA,RwobA,RTRPMA,RBRPMA,RFRA,RDPA,RPPA,RTQA,SPCTD,INCS,INCE,BT))
        conn.commit()
    
    TourDataS = drilldata.sort_values('hole_depth', ascending=True).drop_duplicates(['day_num'], keep='first').reset_index(drop=True)
    TourDataE = drilldata.sort_values('hole_depth', ascending=True).drop_duplicates(['day_num'], keep='last').reset_index(drop=True)
    
    for R in TourDataS.index:
        AC = int(19)
        BT = "Tours"
        IC= int(TourDataS.loc[R,'A_interval_code'])
        BHAN = int(TourDataS.loc[R, 'A_bha_num'])
        DN = int(TourDataS.loc[R, 'day_num'])
        WSN = int(TourDataS.loc[R,'stand_count'])
        idata = drilldata[drilldata['day_num'] == DN]
        MDS= float(TourDataS.loc[R, 'hole_depth'])
        MDE= float(TourDataE.loc[R, 'hole_depth'])
        FD =float(MDE-MDS)
        tvdS= float(TourDataS.loc[R,'tvd'])
        tvdE= float(TourDataE.loc[R,'tvd'])
        INCS =float(TourDataS.loc[R,'svy_inc'])
        INCE =float(TourDataE.loc[R,'svy_inc'])
        FIS= int(TourDataS.loc[R,'edrindex'])
        FIE= int(TourDataE.loc[R,'edrindex'])
        DIS= int(TourDataS.loc[R,'dedrindex'])
        DIE= int(TourDataE.loc[R,'dedrindex'])
        DTS=(TourDataS.loc[R,'rig_time']).strftime("%Y-%m-%d %H:%M:%S")
        DT =float(drilldata.loc[DIE, 'time_elapsed'] - drilldata.loc[DIS, 'time_elapsed'])
        TT=float(edrdata.loc[FIE, 'time_elapsed'] - edrdata.loc[FIS, 'time_elapsed'])
        ROPA= int(idata['rop_a'].mean())
        FSLI =idata[idata['rot_sli']==0]
        FROT =idata[idata['rot_sli']==1]
        RPCT=float(len(FROT.index)/len(idata.index))
        SPCT=float(1-RPCT)
        #RPCTD = FROT()
        SlidFT = float(FSLI['drilled_ft'].sum())
        INS= float(TourDataS.loc[R, 'svy_inc'])
        INE= float(TourDataE.loc[R, 'svy_inc'])
        ROTFT = float(FROT['drilled_ft'].sum())
        if SlidFT <5:
            SFRA=SBRPMA=STRPMA=SPPA=SDPA=STQA=SwobA=SROPA=TFE=None
        else:
            TFE=float(FSLI['slide_value_tf'].sum()/SlidFT*100)
            SROPA=int(FSLI['rop_a'].mean())
            SwobA=int(FSLI['wob'].mean())
            STQA=int(FSLI['td_torque'].mean())
            SDPA=int(FSLI['diff_press'].mean())
            SPPA=int(FSLI['pump_press'].mean())
            STRPMA=int(FSLI['td_rpm'].mean())
            SBRPMA=int(FSLI['bit_rpm'].mean())
            SFRA=int(FSLI['flow_in'].mean())
            
        if ROTFT <5:
            RFRA=RBRPMA=RTRPMA=RPPA=RDPA=RTQA=RwobA=RROPA=None
        else:
            RROPA=int(FROT['rop_a'].mean())
            RwobA=int(FROT['wob'].mean())
            RTQA=int(FROT['td_torque'].mean())
            RDPA=int(FROT['diff_press'].mean())
            RPPA=int(FROT['pump_press'].mean())
            RTRPMA=int(FROT['td_rpm'].mean())
            RBRPMA=int(FROT['bit_rpm'].mean())
            RFRA=int(FROT['flow_in'].mean())
        
        arow2 =[WID,AC,IC,BHAN,DN,WSN,MDS,MDE,FD,tvdS,tvdE,FIS,FIE,DIS,DIE,DTS,DTE,TT,DT,ROPA,TFE,SlidFT,SPCT,pdate]
        Arraydata.loc[len(Arraydata)] = arow2
        c.execute("INSERT INTO ASTRA_ARRAYS (WELL_ID,ARRAY_CODE,INTERVAL_CODE,BHA_NUM,DAY_NUM,WELL_STAND_NUM, hole_depth_START, hole_depth_END,FOOTAGE_DRILLED,tvd_START, tvd_END,FEDR_I_START,FEDR_I_End,DEDR_I_START,DEDR_I_End,DT_START,DT_End,Total_Hours,D_Hours,rop_aVG,TOOLFACE_EFFICIENCY_PCT,SLIDING_FOOTAGE,SLIDE_PCT_T,SubmitDate,active,rop_aVG_SLIDING, wob_AVG_SLIDING, TOP_DRIVE_RPM_AVG_SLIDING, BIT_RPM_AVG_SLIDING, FLOW_RATE_AVG_SLIDING, diff_pressURE_AVG_SLIDING, pump_pressURE_SLIDING, TOP_DRIVE_TORQUE_AVG_SLIDING,rop_aVG_ROTATING, wob_AVG_ROTATING, TOP_DRIVE_RPM_AVG_ROTATING, BIT_RPM_AVG_ROTATING, diff_pressURE_AVG_ROTATING, FLOW_RATE_AVG_ROTATING, pump_pressURE_ROTATING, TOP_DRIVE_TORQUE_AVG_ROTATING,SLIDE_PCT_D,svy_inc_START,svy_inc_End,BreakdownType) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(WID,AC,IC,BHAN,DN,WSN,MDS,MDE,FD,tvdS,tvdE,FIS,FIE,DIS,DIE,DTS,DTE,TT,DT,ROPA,TFE,SlidFT,SPCT,pdate,1,SROPA,SwobA,STRPMA,SBRPMA,SFRA,SDPA,SPPA,STQA,RROPA,RwobA,RTRPMA,RBRPMA,RFRA,RDPA,RPPA,RTQA,SPCTD,INCS,INCE,BT))
        conn.commit()
        c.close
    return(Arraydata)
    


        