# -*- coding: utf-8 -*-
"""
Created on Sat April 21 14:53:57 2018

@author: BrianBlackwell
"""
import numpy as np
from numpy import cumsum, inf
import scipy as sy
import os
import pandas as pd
from datetime import datetime, date
import time
from math import sin, cos, pi, radians


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


def drillitup2(hole_depth, prev_hole_depth, block_height, prev_block_height, prev_stand_number, rop_i, wob, td_torque, flow_rate, hole_size, motor_rpg, td_rpm):
    # data_gap = (rig_time-prev_rig_time)/ np.timedelta64(1, 's')
    drilled_ft = hole_depth - prev_hole_depth
    stand_count = (1 if block_height - prev_block_height > BLOCK_THRESH else 0) + prev_stand_number
    bit_rpm = td_rpm + flow_rate*motor_rpg
    astra_mse = 0 if hole_size == 0 or rop_i == 0 else ropwob / (pi * hole_size * hole_size / 4) + (120 * pi * bit_rpm * td_torque) / (pi * hole_size * hole_size * rop_i / 4)

    # drilldata['Lat_L']=drilldata['Hole_Depth']-Curve_Thresh

    return (drilled_ft, data_gap, stand_count, astra_mse, bit_rpm)


def drillitup20(rop_i,avg20_rop_i,rop_a,avg20_rop_a,tf_grav,var20_tf_grav,tf_mag,var20_tf_mag,astra_mse, avg20_astra_mse,VSPlane, rot_sli,l5_rot_sli,next_rot_sli,prev_rot_sli,drilled_ft,bha,prev_bha,stand_number,prev_stand_number,j   ):
    normalized_tf = tf_grav if var20_tf_grav> var20_tf_mag else tf_mag-VSPlane
    slide_value_tf= (None if rot_sli==1 else (drilled_ft)*cos(radians(normalized_tf)))
    rop_i = (0 if rop_i< 0 else avg20_rop_i if rop_i>avg20_rop_i*3 else w)
    rop_a = (0 if rop_a< 0 else avg20_rop_a if rop_a>avg20_rop_a*3 else w)
    astra_mse= (0 if astra_mse< 0 else avg20_astra_mse if astra_mse>avg20_astra_mse*2 else 0 if astra_mse==np.inf else astra_mse)

    slide_start=(1 if next_rot_sli!=rot_sli and l5_rot_sli ==0 and bha==prev_bha and stand_number==prev_stand_number else 1 if ((bha != prev_bha or stand_number != prev_stand_number) and next_rot_sli == rot_sli == prev_rot_sli==0) else 0)
    slide_end=(-1 if next_rot_sli!=rot_sli and l5_rot_sli ==1 and bha == prev_bha and stand_number == prev_stand_number else -1 if (bha != prev_bha or stand_number != prev_stand_number) and next_rot_sli == rot_sli == prev_rot_sli==0 else 0)
    """ if slide_end equals -1 then go update slide number code needed still"""
    rot_start=(1 if next_rot_sli!=rot_sli and rot_sli==1 else 1 if bha != prev_bha and next_rot_sli==rot_sli==prev_rot_sli==1 else 1 if stand_number != prev_stand_number and next_rot_sli==rot_sli==prev_rot_sli==1 else 0)
    rot_end=(-1 if next_rot_sli!=rot_sli and rot_sli==prev_rot_sli==0 else -1 if bha != prev_bha and next_rot_sli==rot_sli==prev_rot_sli==1 else -1 if stand_number != prev_stand_number and next_rot_sli==rot_sli==prev_rot_sli==1 else 0)
   
    return (normalized_tf,slide_value_tf,rop_i,rop_a,astra_mse, slide_start, slide_end, rot_start, rot_end,j)

def Tourism(drilldata):
    #Tour Analysis
    TourData = drilldata.sort_values('Hole_Depth', ascending=True).drop_duplicates(['A_DayNum'], keep='first').reset_index(drop=False)
    TourData1 = drilldata.sort_values('Hole_Depth', ascending=True).drop_duplicates(['A_DayNum'], keep='last').reset_index(drop=False)
    TourData.rename(columns={"index": "Full EDR Start","Date_Time": "Date_Time Start","Hole_Depth": "Hole_Depth Start", "Bit_Depth": "Hole_Depth End", "Block_Height": "Footage Drilled","TVD": "TVD Start"},inplace=True)

    TourData.insert(0, 'Array Code', 7)
    TourData.insert(1, 'A_interval_code', 0)
    TourData.insert(3, 'Full EDR End', TourData1['index'])
    TourData.insert(5, 'Date_Time End', TourData1['Date_Time'])
    TourData['Hole_Depth End'] = TourData1['Hole_Depth']
    #TourData['TVD End'] = TourData1['TVD']
    return (TourData)   
    #analyzer2.columns = ['ROP Avg (Rotating)','	WOB Avg (Rotating)','TD_RPM Avg (Rotating)','bit rpm Avg (Rotating)','Diff_Pressure Avg (Rotating)','Flow Rate Avg (Rotating)','Pump_Press (Rotating) ','TD_Torque Avg (Rotating) ','ROP Ratio	Max ROP','Best ROP','Above AVG ROP','Below AVG ROP','Min ROP','Max WOB	Best WOB','Above AVG WOB','Below AVG WOB','Min WOB','Max Differential pressure','Best Differential pressure','Above AVG Differential pressure','Below AVG Differential pressure','Min Differential pressure','Max bit rpms','Best bit rpms','Above AVG bit rpms','Below AVG bit rpms','Min bit rpms']


def SlideSheet(drilldata, welln):
    pdate = date.today()
    c,conn, engine = connection()
    S_THRESH =10
    act=1
    
    slidesheet =pd.DataFrame(columns =['Slide Number','Rotation Number','Start Depth','End Depth','Length','ROP', 'Effective TF'])
    drilldata['Slide Start']=list(map(lambda w0,w1,w2,x0,x1,x2,y0,y1,y2,y3,y4,y5,y6,z: (1 if z!=y0 and y0==y1==y2==y3==y4==y5==0 and (w1 == w2) and (x1==x2) else 1 if x0 != x1 and z==y0==y1==0 else 1 if w0 != w1 and z==y0==y1==0 else 0), drilldata['A_bha_num'].shift(1),drilldata['A_bha_num'],drilldata['A_bha_num'].shift(-1),drilldata['Stand Number'].shift(1),drilldata['Stand Number'],drilldata['Stand Number'].shift(-1),drilldata['A_Rot_Sli'],drilldata['A_Rot_Sli'].shift(-1),drilldata['A_Rot_Sli'].shift(-2),drilldata['A_Rot_Sli'].shift(-3),drilldata['A_Rot_Sli'].shift(-4),drilldata['A_Rot_Sli'].shift(-5),drilldata['A_Rot_Sli'].shift(-6),drilldata['A_Rot_Sli'].shift(1)))
    drilldata['Slide End']=list(map(lambda w0,w1,x0,x1,y0,y1,y2,y3,y4,y5,y6,z: (-1 if z!=y0 and y0==y1==y2==y3==y4==y5==1 and (w0 == w1) and (x0==x1) else -1 if x0 != x1 and z==y0==y1==0 else -1 if w0 != w1 and z==y0==y1==0 else 0), drilldata['A_bha_num'].shift(-1),drilldata['A_bha_num'],drilldata['Stand Number'].shift(-1),drilldata['Stand Number'],drilldata['A_Rot_Sli'],drilldata['A_Rot_Sli'].shift(-1),drilldata['A_Rot_Sli'].shift(-2),drilldata['A_Rot_Sli'].shift(-3),drilldata['A_Rot_Sli'].shift(-4),drilldata['A_Rot_Sli'].shift(-5),drilldata['A_Rot_Sli'].shift(-6),drilldata['A_Rot_Sli'].shift(1)))
    
    sstart=drilldata[drilldata['Slide Start']==1]
    send=drilldata[drilldata['Slide End']==-1]
    BT="Slides"
    
    Q=I=snum=0
    for I in send.index:
       SS = sstart.index[sstart.index < I].max()
       if SS>Q:
           Q= SS
           MDS =float(drilldata.loc[Q, 'Hole_Depth'])
           MDE = float(drilldata.loc[I, 'Hole_Depth'])
           FD =float(MDE-MDS)
           if FD >  S_THRESH:  
                WID = int(welln)
                AC = int(17)
                IC= int(drilldata.loc[Q,'A_interval_code'])
                BHAN = int(drilldata.loc[Q, 'A_bha_num'])
                DN = int(drilldata.loc[Q, 'A_DayNum'])
                WSN = int(drilldata.loc[Q,'Stand Number'])
                TVDS= float(drilldata.loc[Q,'TVD'])
                TVDE= float(drilldata.loc[I,'TVD'])
                INCS= float(drilldata.loc[Q,'Svy_Inc'])
                INCE= float(drilldata.loc[I,'Svy_Inc'])
                FIS= int(drilldata.loc[Q,'edrindex'])
                FIE= int(drilldata.loc[I,'edrindex'])
                DIS= int(drilldata.loc[Q,'dedrindex'])
                DIE= int(drilldata.loc[I,'dedrindex'])
                idata =  drilldata[ drilldata['Hole_Depth'] <= MDS]; idata =  drilldata[ drilldata['Hole_Depth'] > MDE]
                DTS=(drilldata['Date_Time'].iloc[1]).strftime("%Y-%m-%d %H:%M:%S")
                DTE=(drilldata['Date_Time'].iloc[-1]).strftime("%Y-%m-%d %H:%M:%S")
                TT=None
                ROPA= int(idata['ROP_I'].mean())
                DT=float(drilldata.loc[DIE, 'A_Time_Elapsed'] - drilldata.loc[DIS, 'A_Time_Elapsed'])
                FSLI =idata[idata['A_Rot_Sli']==0]
                RPCT=0
                SPCT=1
                SlidFT = float(FSLI['A_Drill_FT'].sum())
                TFE=float(FSLI['A_TF_Slide_Value'].sum()/SlidFT*100)
                if SlidFT > S_THRESH:
                    RPCTD=0
                    SPCTD = 1
                    RROPA=None
                    RWOBA=None
                    RTQA=None
                    RDPA=None
                    RPPA=None
                    RTRPMA=None
                    RBRPMA=None
                    RFRA=None
                    try:
                        SROPA=int(FSLI['ROP_A'].mean())
                        SWOBA=int(FSLI['WOB'].mean())
                        STQA=int(FSLI['TD_Torque'].mean())
                        SDPA=int(FSLI['Diff_Press'].mean())
                        SPPA=int(FSLI['Pump_Press'].mean())
                        STRPMA=int(FSLI['TD_RPM'].mean())
                        SBRPMA=int(FSLI['A_bit_rpm_t'].mean())
                        SFRA=int(FSLI['Flow_In'].mean())
                    except:
                        SROPA=None
                        SWOBA=None
                        STQA=None
                        SDPA=None
                        SPPA=None
                        STRPMA=None
                        SBRPMA=None
                        SFRA=None
                    
                    c.execute("INSERT INTO ASTRA_ARRAYS (WELL_ID,ARRAY_CODE,INTERVAL_CODE,BHA_NUM,DAY_NUM,WELL_STAND_NUM, HOLE_DEPTH_START, HOLE_DEPTH_END,FOOTAGE_DRILLED,TVD_START, TVD_END,FEDR_I_START,FEDR_I_End,DEDR_I_START,DEDR_I_End,DT_START,DT_End,Total_Hours,D_Hours,ROP_AVG,TOOLFACE_EFFICIENCY_PCT,SLIDING_FOOTAGE,SLIDE_PCT_T,SubmitDate,active,ROP_AVG_SLIDING, WOB_AVG_SLIDING, TOP_DRIVE_RPM_AVG_SLIDING, BIT_RPM_AVG_SLIDING, FLOW_RATE_AVG_SLIDING, DIFF_PRESSURE_AVG_SLIDING, PUMP_PRESSURE_SLIDING, TOP_DRIVE_TORQUE_AVG_SLIDING,ROP_AVG_ROTATING, WOB_AVG_ROTATING, TOP_DRIVE_RPM_AVG_ROTATING, BIT_RPM_AVG_ROTATING, DIFF_PRESSURE_AVG_ROTATING, FLOW_RATE_AVG_ROTATING, PUMP_PRESSURE_ROTATING, TOP_DRIVE_TORQUE_AVG_ROTATING,SLIDE_PCT_D,SVY_INC_START,SVY_INC_End,BreakdownType) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(WID,AC,IC,BHAN,DN,WSN,MDS,MDE,FD,TVDS,TVDE,FIS,FIE,DIS,DIE,DTS,DTE,TT,DT,ROPA,TFE,SlidFT,SPCT,pdate,1,SROPA,SWOBA,STRPMA,SBRPMA,SFRA,SDPA,SPPA,STQA,RROPA,RWOBA,RTRPMA,RBRPMA,RFRA,RDPA,RPPA,RTQA,SPCTD,INCS,INCE,BT))
                    conn.commit()
                    snum += 1
                    arow2 =[snum,"",MDS,  MDE, FD,ROPA,0]
                    slidesheet.loc[len(slidesheet)] = arow2             
    

    drilldata['Rotate Start']=list(map(lambda w0,w1,x0,x1,y0,y1,y2,y3,y4,y5,y6,z: (1 if z!=y0 and y0==1 else 1 if x0 != x1 and z==y0==y1==1 else 1 if w0 != w1 and z==y0==y1==1 else 0), drilldata['A_bha_num'].shift(1),drilldata['A_bha_num'],drilldata['Stand Number'].shift(1),drilldata['Stand Number'],drilldata['A_Rot_Sli'],drilldata['A_Rot_Sli'].shift(1),drilldata['A_Rot_Sli'].shift(-2),drilldata['A_Rot_Sli'].shift(-3),drilldata['A_Rot_Sli'].shift(-4),drilldata['A_Rot_Sli'].shift(-5),drilldata['A_Rot_Sli'].shift(-6),drilldata['A_Rot_Sli'].shift(1)))
    drilldata['Rotate End']=list(map(lambda w0,w1,x0,x1,y0,y1,y2,y3,y4,y5,y6,z: (-1 if z!=y0 and y0==y1==0 else -1 if x0 != x1 and z==y0==y1==1 else -1 if w0 != w1 and z==y0==y1==1 else 0), drilldata['A_bha_num'].shift(-1),drilldata['A_bha_num'],drilldata['Stand Number'].shift(-1),drilldata['Stand Number'],drilldata['A_Rot_Sli'],drilldata['A_Rot_Sli'].shift(-1),drilldata['A_Rot_Sli'].shift(-2),drilldata['A_Rot_Sli'].shift(-3),drilldata['A_Rot_Sli'].shift(-4),drilldata['A_Rot_Sli'].shift(-5),drilldata['A_Rot_Sli'].shift(-6),drilldata['A_Rot_Sli'].shift(1)))
    rstart=drilldata[drilldata['Rotate Start']==1]
    rend=drilldata[drilldata['Rotate End']==-1]
    Q=I=rnum=0
    BT ="Rotations"
    for I in rend.index:
       SS = rstart.index[rstart.index < I].max()
       if SS>Q:
           Q= int(SS)
           MDS= float(drilldata.loc[Q, 'Hole_Depth'])
           MDE= float(drilldata.loc[I, 'Hole_Depth'])
           FD =float(MDE-MDS)
           if FD >  S_THRESH: 
                WID = int(welln)
                AC = int(18)
                IC= int(drilldata.loc[Q,'A_interval_code'])
                BHAN = int(drilldata.loc[Q, 'A_bha_num'])
                DN = int(drilldata.loc[Q, 'A_DayNum'])
                WSN = int(drilldata.loc[Q,'Stand Number'])

                idata =  drilldata[ drilldata['Hole_Depth'] <= MDS]; idata =  drilldata[ drilldata['Hole_Depth'] > MDE]
                TVDS= float(drilldata.loc[Q,'TVD'])
                TVDE= float(drilldata.loc[I,'TVD'])
                INCS= float(drilldata.loc[Q,'Svy_Inc'])
                INCE= float(drilldata.loc[I,'Svy_Inc'])
                FIS= int(drilldata.loc[Q,'edrindex'])
                FIE= int(drilldata.loc[I,'edrindex'])
                DIS= int(drilldata.loc[Q,'dedrindex'])
                DIE= int(drilldata.loc[I,'dedrindex'])
                DTS=(drilldata['Date_Time'].iloc[1]).strftime("%Y-%m-%d %H:%M:%S")
                DTE=(drilldata['Date_Time'].iloc[-1]).strftime("%Y-%m-%d %H:%M:%S")
                TT=float((drilldata.loc[DIE, 'Date_Time'] - drilldata.loc[DIS, 'Date_Time'])/np.timedelta64(1, 'h'))
                DT =float(drilldata.loc[DIE, 'A_Time_Elapsed'] - drilldata.loc[DIS, 'A_Time_Elapsed'])
                ROPA= int(idata['ROP_A'].mean())
                
                FROT =idata[idata['A_Rot_Sli']==1]
                RPCT=1
                SPCT=0
                SlidFT = None
                TFE=None
                
                RPCTD=1
                SPCTD = 0
                RROPA=int(FROT['ROP_A'].mean())
                RWOBA=int(FROT['WOB'].mean())
                RTQA=int(FROT['TD_Torque'].mean())
                RDPA=int(FROT['Diff_Press'].mean())
                RPPA=int(FROT['Pump_Press'].mean())
                RTRPMA=int(FROT['TD_RPM'].mean())
                RBRPMA=int(FROT['A_bit_rpm_t'].mean())
                RFRA=int(FROT['Flow_In'].mean())
                
                SROPA=None
                SWOBA=None
                STQA=None
                SDPA=None
                SPPA=None
                STRPMA=None
                SBRPMA=None
                SFRA=None

                c.execute("INSERT INTO ASTRA_ARRAYS (WELL_ID,ARRAY_CODE,INTERVAL_CODE,BHA_NUM,DAY_NUM,WELL_STAND_NUM, HOLE_DEPTH_START, HOLE_DEPTH_END,FOOTAGE_DRILLED,TVD_START, TVD_END,FEDR_I_START,FEDR_I_End,DEDR_I_START,DEDR_I_End,DT_START,DT_End,Total_Hours,D_Hours,ROP_AVG,TOOLFACE_EFFICIENCY_PCT,SLIDING_FOOTAGE,SLIDE_PCT_T,SubmitDate,active,ROP_AVG_SLIDING, WOB_AVG_SLIDING, TOP_DRIVE_RPM_AVG_SLIDING, BIT_RPM_AVG_SLIDING, FLOW_RATE_AVG_SLIDING, DIFF_PRESSURE_AVG_SLIDING, PUMP_PRESSURE_SLIDING, TOP_DRIVE_TORQUE_AVG_SLIDING,ROP_AVG_ROTATING, WOB_AVG_ROTATING, TOP_DRIVE_RPM_AVG_ROTATING, BIT_RPM_AVG_ROTATING, DIFF_PRESSURE_AVG_ROTATING, FLOW_RATE_AVG_ROTATING, PUMP_PRESSURE_ROTATING, TOP_DRIVE_TORQUE_AVG_ROTATING,SLIDE_PCT_D,SVY_INC_START,SVY_INC_End,BreakdownType) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(WID,AC,IC,BHAN,DN,WSN,MDS,MDE,FD,TVDS,TVDE,FIS,FIE,DIS,DIE,DTS,DTE,TT,DT,ROPA,TFE,SlidFT,SPCT,pdate,1,SROPA,SWOBA,STRPMA,SBRPMA,SFRA,SDPA,SPPA,STQA,RROPA,RWOBA,RTRPMA,RBRPMA,RFRA,RDPA,RPPA,RTQA,SPCTD,INCS,INCE,BT))
                conn.commit()
                rnum += 1
                arow2 =["",rnum,MDS,  MDE, FD,ROPA,0]
                slidesheet.loc[len(slidesheet)] = arow2
     #, FOOTAGE_DRILLED, TVD_START, TVD_END, FEDR_I_START, FEDR_I_END, DEDR_I_START, DEDR_I_END, DT_START, DT_END, TOTAL_HOURS, D_HOURS, DC_HOURS, NON_DRILLING_TIME, RT_TIME, SVY_INC_START, SVY_INC_END, SVY_INC_CHANGE, SVY_AZI_START, SVY_AZI_END, SVY_ROW_START, SVY_ROW_END, SVY_VERTICAL_SECTION_START, SVY_VERTICAL_SECTION_END, TVD_CHANGE, PLAN_NORTHING, PLAN_EASTING, STEP_OUT, PLAN_INC_START, PLAN_INC_END, PLAN_INC_CHANGE, PLAN_AZI_START, PLAN_AZI_END, PLAN_ROW_START, PLAN_ROW_END, PLAN_VERTICAL_SECTION_START, PLAN_VERTICAL_SECTION_END, PLAN_TVD_START, PLAN_TVD_END, PLAN_STEP_OUT, DIRECTIONAL_DIFFICULTY, DIRECTION, PERCENT_IN_ZONE, PLANNED_BURS, YIELDED_BURS, PLANNED_DLR, YIELDED_DLR, YIELD_RATIO, PLANNED_COURSE_LENGTH, COURSE_LENGTH, COURSE_LENGTH_DEVIATION, UP_DOWN, RIGHT_LEFT, AHEAD_BEHIND, TOOLFACE_EFFICIENCY_PCT, MOTOR_BUR_YIELD, MOTOR_DLS_YIELD, ROP_AVG, WOB_AVG, TOP_DRIVE_RPM_AVG, BIT_RPM_AVG, DIFF_PRESSURE_AVG, FLOW_RATE_AVG, PRESSURE_AVG, TOP_DRIVE_TORQUE_AVG, NUM_OF_SLIDES, SLIDING_FOOTAGE, AVG_SLIDE_LENGTH, SLIDE_PCT_D, SLIDE_PCT_T, ROP_AVG_SLIDING, WOB_AVG_SLIDING, TOP_DRIVE_RPM_AVG_SLIDING, BIT_RPM_AVG_SLIDING, FLOW_RATE_AVG_SLIDING, DIFF_PRESSURE_AVG_SLIDING, PUMP_PRESSURE_SLIDING, TOP_DRIVE_TORQUE_AVG_SLIDING, SIDES_UP_HIGHSIDE_NORTH, SLIDES_RIGHT_EAST, SLIDES_DOWN_LOWSIDE_SOUTH, SLIDES_LEFT_WEST, ROTATING_FOOTAGE, ROTATE_PCT_D, ROTATE_PCT_T, ROP_AVG_ROTATING, WOB_AVG_ROTATING, TOP_DRIVE_RPM_AVG_ROTATING, BIT_RPM_AVG_ROTATING, DIFF_PRESSURE_AVG_ROTATING, FLOW_RATE_AVG_ROTATING, PUMP_PRESSURE_ROTATING, TOP_DRIVE_TORQUE_AVG_ROTATING, ROP_RATIO, MAX_ROP, BEST_ROP, ABOVE_AVG_ROP, BELOW_AVG_ROP, MIN_ROP, MAX_WOB, BEST_WOB, ABOVE_AVG_WOB, BELOW_AVG_WOB, MIN_WOB, MAX_DIFF_PRESSURE, BEST_DIFF_PRESSURE, ABOVE_AVG_DIFF_PRESSURE, BELOW_AVG_DIFF_PRESSURE, MIN_DIFF_PRESSURE, MAX_BIT_RPMS, BEST_BIT_RPMS, ABOVE_AVG_BIT_RPMS, BELOW_AVG_BIT_RPMS, MIN_BIT_RPMS, ASTRA_ARRAYScol, SubmitDate, active              
    slidesheet = slidesheet.sort_values(['Start Depth'], ascending=[1])
    slidesheet=slidesheet.reset_index(drop = True)
    
    c.close
    return (slidesheet)                   

 
def SurveySlideSheet(drilldata,surveydata):  
    #SurveySlide Sheet Analysis
    for i in range(1,len(surveydata)-1): 
        SVRSURVEY = drilldata[drilldata['survey number']== i]
        SVYft =SVRSURVEY['A_Drill_FT'].sum()
        Slidesurvey =SVRSURVEY[SVRSURVEY['A_Rot_Sli']==0]
        Rotatesurvey =SVRSURVEY[SVRSURVEY['A_Rot_Sli']==1]
        #sliTF =
        slift = Slidesurvey['A_Drill_FT'].sum()
        slipct =slift/SVYft
        slistart = Slidesurvey['Hole_Depth'].min()
        slistart = Slidesurvey['Hole_Depth'].max()
        
        rotft =Rotatesurvey['A_Drill_FT'].sum()
        rotpct =rotft/SVYft
        rottart =Rotateurvey['Hole_Depth'].min()
        rotstart = Rotateurvey['Hole_Depth'].max()
        
        arow2 =[CXNC,CDepth, Tour,FXCT,FXCT2,OBTS,STS,STOB,PCC,PTP,S,PoffS,SinS,SoutE,PonE,E]
        Connections.loc[len(Connections)] = arow2
    SURVData1 = drilldata.sort_values('Hole_Depth', ascending=True).drop_duplicates(['Stand Number'], keep='first')
    SURVData = drilldata.sort_values('Hole_Depth', ascending=True).drop_duplicates(['Stand Number'], keep='last')
    return (StandData)    

def SlipNSlide(drilldata):     
    #Slide Data
    SlideData =drilldata.copy()
    SlideData.loc[SlideData['A_Rot_Sli']==1] = np.nan
    return (SlideData)

def Roundwego(drilldata):    
    RotateData =drilldata.copy()
    RotateData.loc[RotateData['A_Rot_Sli']==0] = np.nan
    return (RotateData)



def AstraArrays(drilldata,edrdata,welln):
    #sets todays date to verify when the analyzer was run to be compared to version control.
    pdate = date.today()
    c,conn, engine = connection()
    Arraydata =pd.DataFrame(columns =['WELL_ID','ARRAY_CODE','A_interval_CODE','BHA_NUM','DAY_NUM','WELL_STAND_NUM', 'HOLE_DEPTH_START', 'HOLE_DEPTH_END','FOOTAGE_DRILLED','TVD_START', 'TVD_END','FEDR_I_START','FEDR_I_End','DEDR_I_START','DEDR_I_End','DT_START','DT_End','Total_Hours','D_Hours','ROP_AVG','TOOLFACE_EFFICIENCY_PCT','SLIDING_FOOTAGE','SLIDE_PCT_D','SubmitDate'])
    
    # checks to see if this well already has been run by tha analyzer
    y =c.execute("SELECT * FROM ASTRA_ARRAYS WHERE (WELL_ID,active) = (%s,%s)", (welln,1))
    if int(y) > 0:
        c.execute("UPDATE ASTRA_ARRAYS SET active='0' WHERE WELL_ID= (%s)", (welln))
    
    #sets todays date to verify when the analyzer was run to be compared to version control.
    WID = int(welln)
    AC = int(13)
    IC= None
    BT="Full Well"
    BHAN = int(drilldata['A_bha_num'].max())
    DN = int(drilldata['A_DayNum'].max())
    WSN = int(drilldata['Stand Number'].max())
    MDS= float(drilldata['Hole_Depth'].min())
    MDE= float(drilldata['Hole_Depth'].max())
    FD =float(MDE-MDS)
    TVDS= float(drilldata['TVD'].min())
    TVDE= float(drilldata['TVD'].max())
    INCS= float(drilldata['Svy_Inc'].min())
    INCE= float(drilldata['Svy_Inc'].max())
    FIS= int(drilldata['edrindex'].iloc[1])
    FIE= int(drilldata['edrindex'].iloc[-1])
    DIS= int(drilldata['dedrindex'].iloc[1])
    DIE= int(drilldata['dedrindex'].iloc[-1])
    DTS=(drilldata['Date_Time'].iloc[1]).strftime("%Y-%m-%d %H:%M:%S")
    DTE=(drilldata['Date_Time'].iloc[-1]).strftime("%Y-%m-%d %H:%M:%S")
    DT =float(drilldata.loc[DIE, 'A_Time_Elapsed'] - drilldata.loc[DIS, 'A_Time_Elapsed'])
    TT=float(edrdata.loc[FIE, 'A_Time_Elapsed'] - edrdata.loc[FIS, 'A_Time_Elapsed'])
    ROPA= int(drilldata['ROP_A'].mean())
    FSLI =drilldata[drilldata['A_Rot_Sli']==0]
    FROT =drilldata[drilldata['A_Rot_Sli']==1]
    RPCT=float(len(FROT.index)/len(drilldata.index))
    SPCT=float(1-RPCT)
    SlidFT = float(FSLI['A_Drill_FT'].sum())
    if SlidFT <5:
        TFE=None
    else:
        TFE=float(FSLI['A_TF_Slide_Value'].sum()/SlidFT*100)
    
    RPCTD=int(FROT['A_Drill_FT'].sum())/FD
    SPCTD = 1-RPCTD
    RROPA=int(FROT['ROP_A'].mean())
    RWOBA=int(FROT['WOB'].mean())
    RTQA=int(FROT['TD_Torque'].mean())
    RDPA=int(FROT['Diff_Press'].mean())
    RPPA=int(FROT['Pump_Press'].mean())
    RTRPMA=int(FROT['TD_RPM'].mean())
    RBRPMA=int(FROT['A_bit_rpm_t'].mean())
    RFRA=int(FROT['Flow_In'].mean())
    
    SROPA=int(FSLI['ROP_A'].mean())
    SWOBA=int(FSLI['WOB'].mean())
    STQA=int(FSLI['TD_Torque'].mean())
    SDPA=int(FSLI['Diff_Press'].mean())
    SPPA=int(FSLI['Pump_Press'].mean())
    STRPMA=int(FSLI['TD_RPM'].mean())
    SBRPMA=int(FSLI['A_bit_rpm_t'].mean())
    SFRA=int(FSLI['Flow_In'].mean())
    

    arow2 =[WID,AC,IC,BHAN,DN,WSN,MDS,MDE,FD,TVDS,TVDE,FIS,FIE,DIS,DIE,DTS,DTE,TT,DT,ROPA,TFE,SlidFT,SPCT,pdate]
    Arraydata.loc[len(Arraydata)] = arow2

    c.execute("INSERT INTO ASTRA_ARRAYS (WELL_ID,ARRAY_CODE,INTERVAL_CODE,BHA_NUM,DAY_NUM,WELL_STAND_NUM, HOLE_DEPTH_START, HOLE_DEPTH_END,FOOTAGE_DRILLED,TVD_START, TVD_END,FEDR_I_START,FEDR_I_End,DEDR_I_START,DEDR_I_End,DT_START,DT_End,Total_Hours,D_Hours,ROP_AVG,TOOLFACE_EFFICIENCY_PCT,SLIDING_FOOTAGE,SLIDE_PCT_T,SubmitDate,active,ROP_AVG_SLIDING, WOB_AVG_SLIDING, TOP_DRIVE_RPM_AVG_SLIDING, BIT_RPM_AVG_SLIDING, FLOW_RATE_AVG_SLIDING, DIFF_PRESSURE_AVG_SLIDING, PUMP_PRESSURE_SLIDING, TOP_DRIVE_TORQUE_AVG_SLIDING,ROP_AVG_ROTATING, WOB_AVG_ROTATING, TOP_DRIVE_RPM_AVG_ROTATING, BIT_RPM_AVG_ROTATING, DIFF_PRESSURE_AVG_ROTATING, FLOW_RATE_AVG_ROTATING, PUMP_PRESSURE_ROTATING, TOP_DRIVE_TORQUE_AVG_ROTATING,SLIDE_PCT_D,SVY_INC_START,SVY_INC_End,BreakdownType) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(WID,AC,IC,BHAN,DN,WSN,MDS,MDE,FD,TVDS,TVDE,FIS,FIE,DIS,DIE,DTS,DTE,TT,DT,ROPA,TFE,SlidFT,SPCT,pdate,1,SROPA,SWOBA,STRPMA,SBRPMA,SFRA,SDPA,SPPA,STQA,RROPA,RWOBA,RTRPMA,RBRPMA,RFRA,RDPA,RPPA,RTQA,SPCTD,INCS,INCE,BT))
    conn.commit()

    BHADataS = drilldata.sort_values('Hole_Depth', ascending=True).drop_duplicates(['A_bha_num'], keep='first').reset_index(drop=True)
    BHADataE = drilldata.sort_values('Hole_Depth', ascending=True).drop_duplicates(['A_bha_num'], keep='last').reset_index(drop=True)
    
    for R in BHADataS.index:
        AC = int(14)
        BT="BHAs"

        IC= int(BHADataS.loc[R,'A_interval_code'])
        BHAN = int(BHADataS.loc[R, 'A_bha_num'])
        if BHAN > 0:
            idata = drilldata[drilldata['A_bha_num'] == BHAN]
            DN = int(BHADataS.loc[R, 'A_DayNum'])
            WSN = int(BHADataS.loc[R,'Stand Number'])
            MDS= float(BHADataS.loc[R, 'Hole_Depth'])
            MDE= float(BHADataE.loc[R, 'Hole_Depth'])
            FD =float(MDE-MDS)
            TVDS= float(BHADataS.loc[R,'TVD'])
            TVDE= float(BHADataE.loc[R,'TVD'])
            INCS =float(BHADataS.loc[R,'Svy_Inc'])
            INCE =float(BHADataE.loc[R,'Svy_Inc'])
            FIS= int(BHADataS.loc[R,'edrindex'])
            FIE= int(BHADataE.loc[R,'edrindex'])
            DIS= int(BHADataS.loc[R,'dedrindex'])
            DIE= int(BHADataE.loc[R,'dedrindex'])
            DTS=(BHADataS.loc[R,'Date_Time']).strftime("%Y-%m-%d %H:%M:%S")
            DTE=(BHADataE.loc[R,'Date_Time']).strftime("%Y-%m-%d %H:%M:%S")
            DT =float(drilldata.loc[DIE, 'A_Time_Elapsed'] - drilldata.loc[DIS, 'A_Time_Elapsed'])
            TT=float(edrdata.loc[FIE, 'A_Time_Elapsed'] - edrdata.loc[FIS, 'A_Time_Elapsed'])
            ROPA= int(idata['ROP_A'].mean())
            FSLI =idata[idata['A_Rot_Sli']==0]
            FROT =idata[idata['A_Rot_Sli']==1]
            RPCT=float(len(FROT.index)/len(idata.index))
            SPCT=float(1-RPCT)
            SlidFT = float(FSLI['A_Drill_FT'].sum())
            ROTFT = float(FROT['A_Drill_FT'].sum())
            if SlidFT <5:
                TFE=None
            else:
                TFE=float(FSLI['A_TF_Slide_Value'].sum()/SlidFT*100)
            RPCTD=int(FROT['A_Drill_FT'].sum())/FD
            SPCTD = 1-RPCTD    
            if SlidFT <5:
                SFRA=SBRPMA=STRPMA=SPPA=SDPA=STQA=SWOBA=SROPA=TFE=None
            else:
                TFE=float(FSLI['A_TF_Slide_Value'].sum()/SlidFT*100)
                SROPA=int(FSLI['ROP_A'].mean())
                SWOBA=int(FSLI['WOB'].mean())
                STQA=int(FSLI['TD_Torque'].mean())
                SDPA=int(FSLI['Diff_Press'].mean())
                SPPA=int(FSLI['Pump_Press'].mean())
                STRPMA=int(FSLI['TD_RPM'].mean())
                SBRPMA=int(FSLI['A_bit_rpm_t'].mean())
                SFRA=int(FSLI['Flow_In'].mean())
                
            if ROTFT <5:
                RFRA=RBRPMA=RTRPMA=RPPA=RDPA=RTQA=RWOBA=RROPA=None
            else:
                RROPA=int(FROT['ROP_A'].mean())
                RWOBA=int(FROT['WOB'].mean())
                RTQA=int(FROT['TD_Torque'].mean())
                RDPA=int(FROT['Diff_Press'].mean())
                RPPA=int(FROT['Pump_Press'].mean())
                RTRPMA=int(FROT['TD_RPM'].mean())
                RBRPMA=int(FROT['A_bit_rpm_t'].mean())
                RFRA=int(FROT['Flow_In'].mean())
            
            
            arow2 =[WID,AC,IC,BHAN,DN,WSN,MDS,MDE,FD,TVDS,TVDE,FIS,FIE,DIS,DIE,DTS,DTE,TT,DT,ROPA,TFE,SlidFT,SPCT,pdate]
            Arraydata.loc[len(Arraydata)] = arow2
            c.execute("INSERT INTO ASTRA_ARRAYS (WELL_ID,ARRAY_CODE,INTERVAL_CODE,BHA_NUM,DAY_NUM,WELL_STAND_NUM, HOLE_DEPTH_START, HOLE_DEPTH_END,FOOTAGE_DRILLED,TVD_START, TVD_END,FEDR_I_START,FEDR_I_End,DEDR_I_START,DEDR_I_End,DT_START,DT_End,Total_Hours,D_Hours,ROP_AVG,TOOLFACE_EFFICIENCY_PCT,SLIDING_FOOTAGE,SLIDE_PCT_T,SubmitDate,active,ROP_AVG_SLIDING, WOB_AVG_SLIDING, TOP_DRIVE_RPM_AVG_SLIDING, BIT_RPM_AVG_SLIDING, FLOW_RATE_AVG_SLIDING, DIFF_PRESSURE_AVG_SLIDING, PUMP_PRESSURE_SLIDING, TOP_DRIVE_TORQUE_AVG_SLIDING,ROP_AVG_ROTATING, WOB_AVG_ROTATING, TOP_DRIVE_RPM_AVG_ROTATING, BIT_RPM_AVG_ROTATING, DIFF_PRESSURE_AVG_ROTATING, FLOW_RATE_AVG_ROTATING, PUMP_PRESSURE_ROTATING, TOP_DRIVE_TORQUE_AVG_ROTATING,SLIDE_PCT_D,SVY_INC_START,SVY_INC_End,BreakdownType) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(WID,AC,IC,BHAN,DN,WSN,MDS,MDE,FD,TVDS,TVDE,FIS,FIE,DIS,DIE,DTS,DTE,TT,DT,ROPA,TFE,SlidFT,SPCT,pdate,1,SROPA,SWOBA,STRPMA,SBRPMA,SFRA,SDPA,SPPA,STQA,RROPA,RWOBA,RTRPMA,RBRPMA,RFRA,RDPA,RPPA,RTQA,SPCTD,INCS,INCE,BT))
            conn.commit()
    INTDataS = drilldata.sort_values('Hole_Depth', ascending=True).drop_duplicates(['A_interval'], keep='first').reset_index(drop=True)
    INTDataE = drilldata.sort_values('Hole_Depth', ascending=True).drop_duplicates(['A_interval'], keep='last').reset_index(drop=True)
    
    for R in INTDataS.index:
        AC = int(15)
        BT="Intervals"
        IC= int(INTDataS.loc[R,'A_interval_code'])
        if IC >0:
            BHAN = int(INTDataE.loc[R, 'A_bha_num']-INTDataS.loc[R, 'A_bha_num']+1)
            idata = drilldata[drilldata['A_interval_code'] == IC]
            DN = int(INTDataS.loc[R, 'A_DayNum'])
            WSN = int(INTDataS.loc[R,'Stand Number'])
            MDS= float(INTDataS.loc[R, 'Hole_Depth'])
            MDE= float(INTDataE.loc[R, 'Hole_Depth'])
            FD =float(MDE-MDS)
            TVDS= float(INTDataS.loc[R,'TVD'])
            TVDE= float(INTDataE.loc[R,'TVD'])
            INCS =float(INTDataS.loc[R,'Svy_Inc'])
            INCE =float(INTDataE.loc[R,'Svy_Inc'])
            FIS= int(INTDataS.loc[R,'edrindex'])
            FIE= int(INTDataE.loc[R,'edrindex'])
            DIS= int(INTDataS.loc[R,'dedrindex'])
            DIE= int(INTDataE.loc[R,'dedrindex'])
            DTS=(INTDataS.loc[R,'Date_Time']).strftime("%Y-%m-%d %H:%M:%S")
            DTE=(INTDataE.loc[R,'Date_Time']).strftime("%Y-%m-%d %H:%M:%S")
            DT =float(drilldata.loc[DIE, 'A_Time_Elapsed'] - drilldata.loc[DIS, 'A_Time_Elapsed'])
            TT=float(edrdata.loc[FIE, 'A_Time_Elapsed'] - edrdata.loc[FIS, 'A_Time_Elapsed'])
            ROPA= int(idata['ROP_A'].mean())
            FSLI =idata[idata['A_Rot_Sli']==0]
            FROT =idata[idata['A_Rot_Sli']==1]
            RPCT=float(len(FROT.index)/len(idata.index))
            SPCT=float(1-RPCT)
            SlidFT = float(FSLI['A_Drill_FT'].sum())
            ROTFT = float(FROT['A_Drill_FT'].sum())
            if SlidFT <5:
                TFE=None
            else:
                TFE=float(FSLI['A_TF_Slide_Value'].sum()/SlidFT*100)
            
            RPCTD=int(FROT['A_Drill_FT'].sum())/FD
            SPCTD = 1-RPCTD            
            if SlidFT <5:
                SFRA=SBRPMA=STRPMA=SPPA=SDPA=STQA=SWOBA=SROPA=TFE=None
            else:
                TFE=float(FSLI['A_TF_Slide_Value'].sum()/SlidFT*100)
                SROPA=int(FSLI['ROP_A'].mean())
                SWOBA=int(FSLI['WOB'].mean())
                STQA=int(FSLI['TD_Torque'].mean())
                SDPA=int(FSLI['Diff_Press'].mean())
                SPPA=int(FSLI['Pump_Press'].mean())
                STRPMA=int(FSLI['TD_RPM'].mean())
                SBRPMA=int(FSLI['A_bit_rpm_t'].mean())
                SFRA=int(FSLI['Flow_In'].mean())
                
            if ROTFT <5:
                RFRA=RBRPMA=RTRPMA=RPPA=RDPA=RTQA=RWOBA=RROPA=None
            else:
                RROPA=int(FROT['ROP_A'].mean())
                RWOBA=int(FROT['WOB'].mean())
                RTQA=int(FROT['TD_Torque'].mean())
                RDPA=int(FROT['Diff_Press'].mean())
                RPPA=int(FROT['Pump_Press'].mean())
                RTRPMA=int(FROT['TD_RPM'].mean())
                RBRPMA=int(FROT['A_bit_rpm_t'].mean())
                RFRA=int(FROT['Flow_In'].mean())
            
            RPCTD=int(FROT['A_Drill_FT'].sum())/FD
            SPCTD = 1-RPCTD  
            
            
            arow2 =[WID,AC,IC,BHAN,DN,WSN,MDS,MDE,FD,TVDS,TVDE,FIS,FIE,DIS,DIE,DTS,DTE,TT,DT,ROPA,TFE,SlidFT,SPCT,pdate]
            Arraydata.loc[len(Arraydata)] = arow2
            c.execute("INSERT INTO ASTRA_ARRAYS (WELL_ID,ARRAY_CODE,INTERVAL_CODE,BHA_NUM,DAY_NUM,WELL_STAND_NUM, HOLE_DEPTH_START, HOLE_DEPTH_END,FOOTAGE_DRILLED,TVD_START, TVD_END,FEDR_I_START,FEDR_I_End,DEDR_I_START,DEDR_I_End,DT_START,DT_End,Total_Hours,D_Hours,ROP_AVG,TOOLFACE_EFFICIENCY_PCT,SLIDING_FOOTAGE,SLIDE_PCT_T,SubmitDate,active,ROP_AVG_SLIDING, WOB_AVG_SLIDING, TOP_DRIVE_RPM_AVG_SLIDING, BIT_RPM_AVG_SLIDING, FLOW_RATE_AVG_SLIDING, DIFF_PRESSURE_AVG_SLIDING, PUMP_PRESSURE_SLIDING, TOP_DRIVE_TORQUE_AVG_SLIDING,ROP_AVG_ROTATING, WOB_AVG_ROTATING, TOP_DRIVE_RPM_AVG_ROTATING, BIT_RPM_AVG_ROTATING, DIFF_PRESSURE_AVG_ROTATING, FLOW_RATE_AVG_ROTATING, PUMP_PRESSURE_ROTATING, TOP_DRIVE_TORQUE_AVG_ROTATING,SLIDE_PCT_D,SVY_INC_START,SVY_INC_End,BreakdownType) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(WID,AC,IC,BHAN,DN,WSN,MDS,MDE,FD,TVDS,TVDE,FIS,FIE,DIS,DIE,DTS,DTE,TT,DT,ROPA,TFE,SlidFT,SPCT,pdate,1,SROPA,SWOBA,STRPMA,SBRPMA,SFRA,SDPA,SPPA,STQA,RROPA,RWOBA,RTRPMA,RBRPMA,RFRA,RDPA,RPPA,RTQA,SPCTD,INCS,INCE,BT))
            conn.commit()
        
        
    FormDataS = drilldata.sort_values('Hole_Depth', ascending=True).drop_duplicates(['A_formations'], keep='first').reset_index(drop=True)
    FormDataE = drilldata.sort_values('Hole_Depth', ascending=True).drop_duplicates(['A_formations'], keep='last').reset_index(drop=True)
    
    for R in FormDataS.index:
        AC = int(42)
        BT="Formations"
        IC= int(FormDataS.loc[R,'A_interval_code'])
        FN =FormDataS.loc[R,'A_formations']
        BHAN = int(FormDataE.loc[R, 'A_bha_num']-FormDataS.loc[R, 'A_bha_num']+1)
        
        idata = drilldata[drilldata['A_formations'] == FN]
        DN = int(FormDataS.loc[R, 'A_DayNum'])
        WSN = int(FormDataS.loc[R,'Stand Number'])
        MDS= float(FormDataS.loc[R, 'Hole_Depth'])
        MDE= float(FormDataE.loc[R, 'Hole_Depth'])
        FD =float(MDE-MDS)
        TVDS= float(FormDataS.loc[R,'TVD'])
        TVDE= float(FormDataE.loc[R,'TVD'])
        INCS =float(FormDataS.loc[R,'Svy_Inc'])
        INCE =float(FormDataE.loc[R,'Svy_Inc'])
        FIS= int(FormDataS.loc[R,'edrindex'])
        FIE= int(FormDataE.loc[R,'edrindex'])
        DIS= int(FormDataS.loc[R,'dedrindex'])
        DIE= int(FormDataE.loc[R,'dedrindex'])
        DTS=(FormDataS.loc[R,'Date_Time']).strftime("%Y-%m-%d %H:%M:%S")
        DTE=(FormDataE.loc[R,'Date_Time']).strftime("%Y-%m-%d %H:%M:%S")
        DT =float(drilldata.loc[DIE, 'A_Time_Elapsed'] - drilldata.loc[DIS, 'A_Time_Elapsed'])
        TT=float(edrdata.loc[FIE, 'A_Time_Elapsed'] - edrdata.loc[FIS, 'A_Time_Elapsed'])
        ROPA= int(idata['ROP_A'].mean())
        FSLI =idata[idata['A_Rot_Sli']==0]
        FROT =idata[idata['A_Rot_Sli']==1]
        RPCT=float(len(FROT.index)/len(idata.index))
        SPCT=float(1-RPCT)
        SlidFT = float(FSLI['A_Drill_FT'].sum())
        ROTFT = float(FROT['A_Drill_FT'].sum())
        if SlidFT <5:
            TFE=None
        else:
            TFE=float(FSLI['A_TF_Slide_Value'].sum()/SlidFT*100)
        
        RPCTD=int(FROT['A_Drill_FT'].sum())/FD
        SPCTD = 1-RPCTD            
        if SlidFT <5:
            SFRA=SBRPMA=STRPMA=SPPA=SDPA=STQA=SWOBA=SROPA=TFE=None
        else:
            TFE=float(FSLI['A_TF_Slide_Value'].sum()/SlidFT*100)
            SROPA=int(FSLI['ROP_A'].mean())
            SWOBA=int(FSLI['WOB'].mean())
            STQA=int(FSLI['TD_Torque'].mean())
            SDPA=int(FSLI['Diff_Press'].mean())
            SPPA=int(FSLI['Pump_Press'].mean())
            STRPMA=int(FSLI['TD_RPM'].mean())
            SBRPMA=int(FSLI['A_bit_rpm_t'].mean())
            SFRA=int(FSLI['Flow_In'].mean())
            
        if ROTFT <5:
            RFRA=RBRPMA=RTRPMA=RPPA=RDPA=RTQA=RWOBA=RROPA=None
        else:
            RROPA=int(FROT['ROP_A'].mean())
            RWOBA=int(FROT['WOB'].mean())
            RTQA=int(FROT['TD_Torque'].mean())
            RDPA=int(FROT['Diff_Press'].mean())
            RPPA=int(FROT['Pump_Press'].mean())
            RTRPMA=int(FROT['TD_RPM'].mean())
            RBRPMA=int(FROT['A_bit_rpm_t'].mean())
            RFRA=int(FROT['Flow_In'].mean())
        
        RPCTD=int(FROT['A_Drill_FT'].sum())/FD
        SPCTD = 1-RPCTD  
        
        
        arow2 =[WID,AC,IC,BHAN,DN,WSN,MDS,MDE,FD,TVDS,TVDE,FIS,FIE,DIS,DIE,DTS,DTE,TT,DT,ROPA,TFE,SlidFT,SPCT,pdate]
        Arraydata.loc[len(Arraydata)] = arow2
        c.execute("INSERT INTO ASTRA_ARRAYS (WELL_ID,ARRAY_CODE,INTERVAL_CODE,BHA_NUM,DAY_NUM,WELL_STAND_NUM, HOLE_DEPTH_START, HOLE_DEPTH_END,FOOTAGE_DRILLED,TVD_START, TVD_END,FEDR_I_START,FEDR_I_End,DEDR_I_START,DEDR_I_End,DT_START,DT_End,Total_Hours,D_Hours,ROP_AVG,TOOLFACE_EFFICIENCY_PCT,SLIDING_FOOTAGE,SLIDE_PCT_T,SubmitDate,active,ROP_AVG_SLIDING, WOB_AVG_SLIDING, TOP_DRIVE_RPM_AVG_SLIDING, BIT_RPM_AVG_SLIDING, FLOW_RATE_AVG_SLIDING, DIFF_PRESSURE_AVG_SLIDING, PUMP_PRESSURE_SLIDING, TOP_DRIVE_TORQUE_AVG_SLIDING,ROP_AVG_ROTATING, WOB_AVG_ROTATING, TOP_DRIVE_RPM_AVG_ROTATING, BIT_RPM_AVG_ROTATING, DIFF_PRESSURE_AVG_ROTATING, FLOW_RATE_AVG_ROTATING, PUMP_PRESSURE_ROTATING, TOP_DRIVE_TORQUE_AVG_ROTATING,SLIDE_PCT_D,SVY_INC_START,SVY_INC_End,BreakdownType) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(WID,AC,IC,BHAN,DN,WSN,MDS,MDE,FD,TVDS,TVDE,FIS,FIE,DIS,DIE,DTS,DTE,TT,DT,ROPA,TFE,SlidFT,SPCT,pdate,1,SROPA,SWOBA,STRPMA,SBRPMA,SFRA,SDPA,SPPA,STQA,RROPA,RWOBA,RTRPMA,RBRPMA,RFRA,RDPA,RPPA,RTQA,SPCTD,INCS,INCE,BT))
        conn.commit()
        
        
    StandDataS = drilldata.sort_values('Hole_Depth', ascending=True).drop_duplicates(['Stand Number'], keep='first').reset_index(drop=True)
    StandDataE = drilldata.sort_values('Hole_Depth', ascending=True).drop_duplicates(['Stand Number'], keep='last').reset_index(drop=True)
    
    for R in StandDataS.index:
        AC = int(16)
        BT = "Stands"
        IC= int(StandDataS.loc[R,'A_interval_code'])
        BHAN = int(StandDataS.loc[R, 'A_bha_num'])
        DN = int(StandDataS.loc[R, 'A_DayNum'])
        WSN = int(StandDataS.loc[R,'Stand Number'])
        idata = drilldata[drilldata['Stand Number'] == WSN]
        MDS= float(StandDataS.loc[R, 'Hole_Depth'])
        MDE= float(StandDataE.loc[R, 'Hole_Depth'])
        FD =float(MDE-MDS)
        TVDS= float(StandDataS.loc[R,'TVD'])
        TVDE= float(StandDataE.loc[R,'TVD'])
        INCS =float(StandDataS.loc[R,'Svy_Inc'])
        INCE =float(StandDataE.loc[R,'Svy_Inc'])
        FIS= int(StandDataS.loc[R,'edrindex'])
        FIE= int(StandDataE.loc[R,'edrindex'])
        DIS= int(StandDataS.loc[R,'dedrindex'])
        DIE= int(StandDataE.loc[R,'dedrindex'])
        DTS=(StandDataS.loc[R,'Date_Time']).strftime("%Y-%m-%d %H:%M:%S")
        DTE=(StandDataE.loc[R,'Date_Time']).strftime("%Y-%m-%d %H:%M:%S")
        DT =float(drilldata.loc[DIE, 'A_Time_Elapsed'] - drilldata.loc[DIS, 'A_Time_Elapsed'])
        TT=float(edrdata.loc[FIE, 'A_Time_Elapsed'] - edrdata.loc[FIS, 'A_Time_Elapsed'])
        ROPA= int(idata['ROP_I'].mean())
        FSLI =idata[idata['A_Rot_Sli']==0]
        FROT =idata[idata['A_Rot_Sli']==1]
        RPCT=float(len(FROT.index)/len(idata.index))
        SPCT=float(1-RPCT)
        SlidFT = float(FSLI['A_Drill_FT'].sum())
        ROTFT = float(FROT['A_Drill_FT'].sum())
        if SlidFT <5:
            SFRA=SBRPMA=STRPMA=SPPA=SDPA=STQA=SWOBA=SROPA=TFE=None
        else:
            TFE=float(FSLI['A_TF_Slide_Value'].sum()/SlidFT*100)
            SROPA=int(FSLI['ROP_A'].mean())
            SWOBA=int(FSLI['WOB'].mean())
            STQA=int(FSLI['TD_Torque'].mean())
            SDPA=int(FSLI['Diff_Press'].mean())
            SPPA=int(FSLI['Pump_Press'].mean())
            STRPMA=int(FSLI['TD_RPM'].mean())
            SBRPMA=int(FSLI['A_bit_rpm_t'].mean())
            SFRA=int(FSLI['Flow_In'].mean())
            
        if ROTFT <5:
            RFRA=RBRPMA=RTRPMA=RPPA=RDPA=RTQA=RWOBA=RROPA=None
        else:
            RROPA=int(FROT['ROP_A'].mean())
            RWOBA=int(FROT['WOB'].mean())
            RTQA=int(FROT['TD_Torque'].mean())
            RDPA=int(FROT['Diff_Press'].mean())
            RPPA=int(FROT['Pump_Press'].mean())
            RTRPMA=int(FROT['TD_RPM'].mean())
            RBRPMA=int(FROT['A_bit_rpm_t'].mean())
            RFRA=int(FROT['Flow_In'].mean())
            
        RPCTD=int(FROT['A_Drill_FT'].sum())/FD
        SPCTD = 1-RPCTD      


        
        arow2 =[WID,AC,IC,BHAN,DN,WSN,MDS,MDE,FD,TVDS,TVDE,FIS,FIE,DIS,DIE,DTS,DTE,TT,DT,ROPA,TFE,SlidFT,SPCT,pdate]
        Arraydata.loc[len(Arraydata)] = arow2
        c.execute("INSERT INTO ASTRA_ARRAYS (WELL_ID,ARRAY_CODE,INTERVAL_CODE,BHA_NUM,DAY_NUM,WELL_STAND_NUM, HOLE_DEPTH_START, HOLE_DEPTH_END,FOOTAGE_DRILLED,TVD_START, TVD_END,FEDR_I_START,FEDR_I_End,DEDR_I_START,DEDR_I_End,DT_START,DT_End,Total_Hours,D_Hours,ROP_AVG,TOOLFACE_EFFICIENCY_PCT,SLIDING_FOOTAGE,SLIDE_PCT_T,SubmitDate,active,ROP_AVG_SLIDING, WOB_AVG_SLIDING, TOP_DRIVE_RPM_AVG_SLIDING, BIT_RPM_AVG_SLIDING, FLOW_RATE_AVG_SLIDING, DIFF_PRESSURE_AVG_SLIDING, PUMP_PRESSURE_SLIDING, TOP_DRIVE_TORQUE_AVG_SLIDING,ROP_AVG_ROTATING, WOB_AVG_ROTATING, TOP_DRIVE_RPM_AVG_ROTATING, BIT_RPM_AVG_ROTATING, DIFF_PRESSURE_AVG_ROTATING, FLOW_RATE_AVG_ROTATING, PUMP_PRESSURE_ROTATING, TOP_DRIVE_TORQUE_AVG_ROTATING,SLIDE_PCT_D,SVY_INC_START,SVY_INC_End,BreakdownType) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(WID,AC,IC,BHAN,DN,WSN,MDS,MDE,FD,TVDS,TVDE,FIS,FIE,DIS,DIE,DTS,DTE,TT,DT,ROPA,TFE,SlidFT,SPCT,pdate,1,SROPA,SWOBA,STRPMA,SBRPMA,SFRA,SDPA,SPPA,STQA,RROPA,RWOBA,RTRPMA,RBRPMA,RFRA,RDPA,RPPA,RTQA,SPCTD,INCS,INCE,BT))
        conn.commit()
    
    TourDataS = drilldata.sort_values('Hole_Depth', ascending=True).drop_duplicates(['A_DayNum'], keep='first').reset_index(drop=True)
    TourDataE = drilldata.sort_values('Hole_Depth', ascending=True).drop_duplicates(['A_DayNum'], keep='last').reset_index(drop=True)
    
    for R in TourDataS.index:
        AC = int(19)
        BT = "Tours"
        IC= int(TourDataS.loc[R,'A_interval_code'])
        BHAN = int(TourDataS.loc[R, 'A_bha_num'])
        DN = int(TourDataS.loc[R, 'A_DayNum'])
        WSN = int(TourDataS.loc[R,'Stand Number'])
        idata = drilldata[drilldata['A_DayNum'] == DN]
        MDS= float(TourDataS.loc[R, 'Hole_Depth'])
        MDE= float(TourDataE.loc[R, 'Hole_Depth'])
        FD =float(MDE-MDS)
        TVDS= float(TourDataS.loc[R,'TVD'])
        TVDE= float(TourDataE.loc[R,'TVD'])
        INCS =float(TourDataS.loc[R,'Svy_Inc'])
        INCE =float(TourDataE.loc[R,'Svy_Inc'])
        FIS= int(TourDataS.loc[R,'edrindex'])
        FIE= int(TourDataE.loc[R,'edrindex'])
        DIS= int(TourDataS.loc[R,'dedrindex'])
        DIE= int(TourDataE.loc[R,'dedrindex'])
        DTS=(TourDataS.loc[R,'Date_Time']).strftime("%Y-%m-%d %H:%M:%S")
        DT =float(drilldata.loc[DIE, 'A_Time_Elapsed'] - drilldata.loc[DIS, 'A_Time_Elapsed'])
        TT=float(edrdata.loc[FIE, 'A_Time_Elapsed'] - edrdata.loc[FIS, 'A_Time_Elapsed'])
        ROPA= int(idata['ROP_A'].mean())
        FSLI =idata[idata['A_Rot_Sli']==0]
        FROT =idata[idata['A_Rot_Sli']==1]
        RPCT=float(len(FROT.index)/len(idata.index))
        SPCT=float(1-RPCT)
        #RPCTD = FROT()
        SlidFT = float(FSLI['A_Drill_FT'].sum())
        INS= float(TourDataS.loc[R, 'Svy_Inc'])
        INE= float(TourDataE.loc[R, 'Svy_Inc'])
        ROTFT = float(FROT['A_Drill_FT'].sum())
        if SlidFT <5:
            SFRA=SBRPMA=STRPMA=SPPA=SDPA=STQA=SWOBA=SROPA=TFE=None
        else:
            TFE=float(FSLI['A_TF_Slide_Value'].sum()/SlidFT*100)
            SROPA=int(FSLI['ROP_A'].mean())
            SWOBA=int(FSLI['WOB'].mean())
            STQA=int(FSLI['TD_Torque'].mean())
            SDPA=int(FSLI['Diff_Press'].mean())
            SPPA=int(FSLI['Pump_Press'].mean())
            STRPMA=int(FSLI['TD_RPM'].mean())
            SBRPMA=int(FSLI['A_bit_rpm_t'].mean())
            SFRA=int(FSLI['Flow_In'].mean())
            
        if ROTFT <5:
            RFRA=RBRPMA=RTRPMA=RPPA=RDPA=RTQA=RWOBA=RROPA=None
        else:
            RROPA=int(FROT['ROP_A'].mean())
            RWOBA=int(FROT['WOB'].mean())
            RTQA=int(FROT['TD_Torque'].mean())
            RDPA=int(FROT['Diff_Press'].mean())
            RPPA=int(FROT['Pump_Press'].mean())
            RTRPMA=int(FROT['TD_RPM'].mean())
            RBRPMA=int(FROT['A_bit_rpm_t'].mean())
            RFRA=int(FROT['Flow_In'].mean())
        
        arow2 =[WID,AC,IC,BHAN,DN,WSN,MDS,MDE,FD,TVDS,TVDE,FIS,FIE,DIS,DIE,DTS,DTE,TT,DT,ROPA,TFE,SlidFT,SPCT,pdate]
        Arraydata.loc[len(Arraydata)] = arow2
        c.execute("INSERT INTO ASTRA_ARRAYS (WELL_ID,ARRAY_CODE,INTERVAL_CODE,BHA_NUM,DAY_NUM,WELL_STAND_NUM, HOLE_DEPTH_START, HOLE_DEPTH_END,FOOTAGE_DRILLED,TVD_START, TVD_END,FEDR_I_START,FEDR_I_End,DEDR_I_START,DEDR_I_End,DT_START,DT_End,Total_Hours,D_Hours,ROP_AVG,TOOLFACE_EFFICIENCY_PCT,SLIDING_FOOTAGE,SLIDE_PCT_T,SubmitDate,active,ROP_AVG_SLIDING, WOB_AVG_SLIDING, TOP_DRIVE_RPM_AVG_SLIDING, BIT_RPM_AVG_SLIDING, FLOW_RATE_AVG_SLIDING, DIFF_PRESSURE_AVG_SLIDING, PUMP_PRESSURE_SLIDING, TOP_DRIVE_TORQUE_AVG_SLIDING,ROP_AVG_ROTATING, WOB_AVG_ROTATING, TOP_DRIVE_RPM_AVG_ROTATING, BIT_RPM_AVG_ROTATING, DIFF_PRESSURE_AVG_ROTATING, FLOW_RATE_AVG_ROTATING, PUMP_PRESSURE_ROTATING, TOP_DRIVE_TORQUE_AVG_ROTATING,SLIDE_PCT_D,SVY_INC_START,SVY_INC_End,BreakdownType) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(WID,AC,IC,BHAN,DN,WSN,MDS,MDE,FD,TVDS,TVDE,FIS,FIE,DIS,DIE,DTS,DTE,TT,DT,ROPA,TFE,SlidFT,SPCT,pdate,1,SROPA,SWOBA,STRPMA,SBRPMA,SFRA,SDPA,SPPA,STQA,RROPA,RWOBA,RTRPMA,RBRPMA,RFRA,RDPA,RPPA,RTQA,SPCTD,INCS,INCE,BT))
        conn.commit()
        c.close
    return(Arraydata)
    


        