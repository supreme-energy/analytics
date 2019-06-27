# -*- coding: utf-8 -*-
"""
@author: BrianBlackwell
"""
import numpy as np
from numpy import cumsum
import scipy as sy
import pylab as pyl
import os
import pandas as pd
from pandas.io import gbq
from datetime import datetime
import time
from statistics import variance
from scipy.stats import linregress
from scipy.ndimage import gaussian_filter
from scipy.signal import savgol_filter
import bisect

import time
start = time.time()
#Define EDR Data Triggers
ROTATE_THRESH = 25
BLOCK_THRESH = 15
BITTHRESH = 1
hookload_THRESH = 55
FLOW_THRESH = 30
TRIP_THRESH = 150
CXN_THRESH = 30
Surface_Thresh=200
Vertical_Thresh=5600
Curve_Thresh=6900
data_gap =5
#ActiveCell.FormulaR1C1 = "=IFERROR(,IF(AND((RC" & HoleDepth_C & "-R[-1]C" & HoleDepth_C & ")=0,(RC" & Overpull_C & ")>0), 5,IF(R[-1]C" & HoleDepth_C & "=0,1,IF(R[-1]C" & HoleDepth_C & "-MAX(R[-198]C" & HoleDepth_C & ":R[-1]C" & HoleDepth_C & ")<0,6,IF(RC" & Date_C & "=0,1,0)))))),9)"
#datesandtimes= [datetime.strptime(x, "%Y-%m-%d %H:%M:%S") for x in edrdata['rig_time']]

def cleanitup(edrdata,DATA_FREQUENCY):
    #edrdata = edrdata[edrdata['hole_depth']>0]
    edrdata.index = edrdata.index.astype(int)
    try:
        pd.to_datetime(edrdata['rig_time'], errors='raise', dayfirst=False, yearfirst=True, utc=None, box=True, format="%Y-%m-%d %H:%M:%S", exact=True, unit=None, infer_datetime_format=True, origin='unix', cache=False)
        edrdata['rig_time']= [datetime.strptime(x, "%Y-%m-%d %H:%M:%S") for x in edrdata['rig_time']]
    except:
        edrdata['rig_time'] = pd.to_datetime(edrdata['rig_time'])
    
    startdate=edrdata['rig_time'].min()
    edrdata.fillna(-999.25, inplace=True)
    edrdata['A_bha_num']=1
    edrdata['A_interval_code']=1
    #edrdata['bit RPM']= list(map(lambda x: (1 if x >= 6 and x < 18 else 2), pd.DatetimeIndex(edrdata['rig_time']).hour.astype(int)))
    edrdata['day_num'] = list(map(lambda x: int((x-startdate)/np.timedelta64(1, 'D'))+1, edrdata['rig_time']))
    edrdata['day_night'] = list(map(lambda x: (1 if x >= 6 and x < 18 else 2), pd.DatetimeIndex(edrdata['rig_time']).hour.astype(int)))
    edrdata['bit_status']= list(map(lambda w,x,z: (1 if (w-x < BITTHRESH and w>0 and x>0 and  z > 0) else 0), edrdata['hole_depth'],edrdata['bit_depth'],edrdata['rop_i']))
    edrdata['bit_status']= list(map(lambda w,x,y,z: (2 if (w-x < BITTHRESH and w>0 and x>0 and  z > 0 and y <1 ) else (1 if (w-x < BITTHRESH and w>0 and x>0 and  z > 0 ) else (-1 if y > 0 else 0))), edrdata['hole_depth'],edrdata['bit_depth'],edrdata['bit_status'].shift(1),edrdata['rop_i']))
    edrdata['slip_status'] = list(map(lambda w,x: (1 if w<1 and x < hookload_THRESH else 0), edrdata['bit_status'],edrdata['hookload']))
    edrdata['slip_status'] = list(map(lambda w,x,y: (2 if (w<1 and x < hookload_THRESH and y <1) else (1 if (w<1 and x < hookload_THRESH and y > 0) else (-1 if y > 0 else 0))), edrdata['bit_status'],edrdata['hookload'],edrdata['slip_status'].shift(1)))
    edrdata['block_status']= list(map(lambda x,y: (1 if (x > y) else (-1 if (x < y) else 0)), edrdata['block_height'],edrdata['block_height'].shift(1)))
    edrdata['pump_status']= 0
    edrdata['pump_status']= list(map(lambda w: (1 if (w > FLOW_THRESH) else 0), edrdata['flow_in']))
    edrdata['pump_status']= list(map(lambda w,x: (2 if (w > FLOW_THRESH and x <1) else 1 if w > FLOW_THRESH else (-1 if x >0 else 0)), edrdata['flow_in'],edrdata['pump_status'].shift(1)))
    try:
        edrdata['rot_sli'] = list(map(lambda x,w: (0 if x>0 else 1 if w > ROTATE_THRESH else 0), edrdata['oscillator'],edrdata['td_rpm']))
    except:
        edrdata['rot_sli'] = list(map(lambda w: (1 if w > ROTATE_THRESH else 0), edrdata['td_rpm']))

    #edrdata['A_TQ_Var'] = edrdata['td_torque'].rolling(5).var()
    edrdata['trip_status'] = list(map(lambda w,x,y,z: (5 if w>0 else (4 if x-y>TRIP_THRESH else (1 if y>z else (-1 if z>y else 0)))), edrdata['bit_status'],edrdata['hole_depth'],edrdata['bit_depth'],edrdata['bit_depth'].shift(1)))
    edrdata['rig_activity'] = list(map(lambda P0,P1,SR0: (0 if P0 ==0 or P1 ==0 or P0 ==2 and SR0==0 else 1 if P0 ==0 or P1 ==0 or P0 ==2 and SR0==1 else 2 if P0 == 1 and SR0==0 else 3), edrdata['pump_status'],edrdata['pump_status'].shift(1),edrdata['rot_sli']))
    edrdata['time_elapsed'] = list(map(lambda w,x: (w-x)/ np.timedelta64(1, 'h') if (w-x)/ np.timedelta64(1, 'h') < 5 else 0, edrdata['rig_time'],edrdata['rig_time'].shift(1)))
    edrdata['time_elapsed'] = edrdata['time_elapsed'].cumsum()
    edrdata['data_gap'] = list(map(lambda w,x: (w-x)/ np.timedelta64(1, 's'), edrdata['rig_time'],edrdata['rig_time'].shift(1)))

    
    """Cleaning Algorithms to reduce data to determine a drilling only data set for drilling analytics processing"""
    edrdata['clean_1'] = 0
    edrdata['clean_1'] = list(map(lambda w,x,y,z,a,b,d : (2 if w-x > 2 else (3 if (a-b <= 0) else (4 if y <100 else(6 if a-d < 0 else (1 if z ==0 else 0))))) , edrdata['hole_depth'].astype(int),edrdata['bit_depth'].astype(int),edrdata['flow_in'],edrdata['rig_time'],edrdata['hole_depth'],edrdata['hole_depth'].shift(1),edrdata['hole_depth'].rolling(1000).max()))
    edrdata['clean_2'] = 0
    edrdata['clean_2'] = list(map(lambda w,x,y,z: (x if w== 0 and z > 60 else (-2 if y > w else 0)), edrdata['clean_2'].rolling(20).max(),edrdata['hole_depth'],edrdata['hole_depth'].shift(-1),edrdata['data_gap'].shift(-1)))
    clean_2 =edrdata['clean_2'][::-1].rolling(100).min()
    clean_2 =clean_2[::-1]
    
    edrdata['clean_3'] = list(map(lambda w,a,x,y,z: (9 if x==y and z > 11 else (8 if w > 10 and a==-2 else 0)), edrdata['clean_2'].rolling(100).max(),clean_2,edrdata['hole_depth'],edrdata['hole_depth'].shift(1),edrdata['data_gap'].shift(-1)))
    edrdata['bit_variance']=list(map(lambda M1,M2,b1,b3: (M1-M2) if (b1-b3) == 0 else (M1-M2)*(b1-b3)/(abs(b1-b3)), edrdata['bit_depth'].rolling(100).max(),edrdata['bit_depth'].rolling(100).min(),edrdata['bit_depth'],edrdata['bit_depth'].rolling(30).mean()))
    edrdata['savgol']=savgol_filter(edrdata['bit_depth'], window_length=49, polyorder=2, deriv=1)
    edrdata['trip_status2']= list(map(lambda p: (4 if p < -1.8 and p >-12 else 6 if p > 2.2 and p < 12 else 0), edrdata['savgol']))
    edrdata['rig_activity2']= list(map(lambda p,r,b100,b1,b3,h,c1,c3: (5 if (c1==0 and c3==0) else 3 if ((h-b1)>TRIP_THRESH and p>0.95 and r> 0.95) else 2 if ((h-b1)>TRIP_THRESH and p> 0.95) else 4 if ((h-b1)>TRIP_THRESH) and (b1-b100) <-0.25 else  6 if ((h-b1)>TRIP_THRESH) and (b1-b100) >0.25 else 7 if ((h-b1)>TRIP_THRESH and b1<1000) else 1 if ((b1-b3) <-0.2) else -1 if ((b1-b3) >0.2) else 3 if  (p>0.05 and r> 0.05) else 2 if (p> 0.05) else 0), edrdata['pump_status'].rolling(10).mean(), edrdata['rot_sli'].rolling(10).mean(),edrdata['bit_depth'].rolling(50).mean(),edrdata['bit_depth'],edrdata['bit_depth'].rolling(250).mean(),edrdata['hole_depth'], edrdata['clean_1'], edrdata['clean_3']))

    return edrdata

def trippedit(edrdata,DATA_FREQUENCY,bhas,intervals):
    tripout = edrdata[edrdata['trip_status2'] == 4]
    tripout['trip_number'] = list(map(lambda h0,h1,w,x: (0 if h1 ==h0 and (w-x)/ np.timedelta64(1, 'h') < 2 else 1),tripout['hole_depth'],tripout['hole_depth'].shift(1),tripout['rig_time'],tripout['rig_time'].shift(1)))
    tripout['trip_number']= list(cumsum(tripout['trip_number'])+1)
    tripin = edrdata[edrdata['trip_status2'] == 6]
    tripin['trip_number'] = list(map(lambda h0,h1,w,x: (0 if h1 ==h0 and (w-x)/ np.timedelta64(1, 'h') < 2 else 1),tripin['hole_depth'],tripin['hole_depth'].shift(1),tripin['rig_time'],tripin['rig_time'].shift(1)))
    tripin['trip_number']= list(cumsum(tripin['trip_number'])+1)

    mindrill = edrdata[edrdata['rig_activity2'] == 5].min()
    mintrip_depth =mindrill['hole_depth']
    maxdepth = edrdata["hole_depth"].max()

    mintrip =tripin
    mintrip_time = mintrip['rig_time'].min()
    #print(mintrip_time, mintrip_depth, mindrill)
    j=1
    prev_depth =0
    bhaid = None
    intervalid = None
    tripping =pd.DataFrame(columns =['trip_direction','depth','start_time','end_time', 'trip_points', 'trip_count', 'trip_style','casing','bha_id','interval_id','bha_time','edr_proc_id'])
    bhas_trips =pd.DataFrame(columns =['status', 'bha_number', 'depth_in', 'depth_out', 'time_in', 'time_out','is_template','objective'])
    edrdata["trip_in_number"]=0
    edrdata["trip_out_number"]=0      
    for i in tripin['trip_number'].unique():
        dist1 = 500
        bhaid = None
        intervalid = None
        intervalid1 = None
        intervalid2 = None
        casing = False
        current_trip =tripin[tripin['trip_number']==i]
        if len(current_trip) > 360 or (current_trip["hole_depth"].min() < 2000 and len(current_trip) > 60): 
            direction= True
            depth=current_trip["hole_depth"].min()
            edr_raw = current_trip['edr_raw_id'].min()
            bha_len = min(depth/10, 1000)
            if len(bhas)>0:
                for i in range(len(bhas)):
                    dist = abs(depth -bhas.loc[i,'depth_out'])
                    if dist< dist1:
                        bhaid_dist=bhas.loc[i,'id']
                        dist1 =dist
                    if abs(depth -bhas.loc[i,'depth_in'])<30:
                        bhaid=bhas.loc[i,'id']
                        bha_len = bhas.loc[i,'bha_length']
                        if bha_len is None:
                            bha_len = min(depth/10, 1000)
                    if bhaid is None:
                        bhaid = bhaid_dist
            bha_trip = current_trip[current_trip['bit_depth'] <= bha_len]
            
            bha_time = bha_trip['rig_time'].max()
            if len(intervals)>0:
                for i in range(len(intervals)):
                    if depth >= intervals.loc[i,'start_depth']-100 and depth <= intervals.loc[i,'end_depth']+100:
                        intervalid=intervals.loc[i,'id']
                    if abs(depth-intervals.loc[i,'start_depth'])<30:
                        intervalid1=intervals.loc[i,'id']
                        if prev_depth == depth:
                            intervalid2=intervals.loc[i-1,'id']
                        
            start_time=current_trip["rig_time"].min()
            end_time =current_trip["rig_time"].max()
            trip_points = len(current_trip)
            trip_number=j
            if current_trip["bit_depth"].min()< .1*depth:
                trip_style = "Full Trip"
            else: 
                trip_style="Short Trip"
            j =j+1
            if prev_depth == depth:
                tripping.loc[len(tripping)-1,'trip_style']="Casing"
                tripping.loc[len(tripping)-1,'casing']=True
                tripping.loc[len(tripping)-1,'bha_id']=None
                tripping.loc[len(tripping)-1,'bha_time']=None
                if intervalid2 is not None:
                    tripping.loc[len(tripping)-1,'interval_id']=intervalid2
                
            if abs(maxdepth - depth) < 50:
                trip_style="Casing"
                casing = True
                bhaid = None
                bha_time = None
            prev_depth = depth
            
                        
            if intervalid1 is not None:
                intervalid =intervalid1
            
            arow2 =[direction,depth,start_time,end_time,trip_points,trip_number, trip_style,casing,bhaid,intervalid,bha_time,edr_raw]
            tripping.loc[len(tripping)] = arow2
            edrdata['trip_in_number']= list(map(lambda x,y: (trip_number if x>=start_time and x<=end_time else y),edrdata['rig_time'],edrdata['trip_in_number']))
            
        
    j=1
    
    for i in tripout['trip_number'].unique():
        dist1 = 500
        bhaid = None
        intervalid = None
        intervalid1 = None
        casing = False
        current_trip =tripout[tripout['trip_number']==i]
        if len(current_trip) > 360 or (current_trip["hole_depth"].min() < 2000 and len(current_trip) > 60): 
            direction= False
            depth=current_trip["hole_depth"].min()
            edr_raw = current_trip['edr_raw_id'].min()
            bha_len = min(depth/10, 1000)
            if len(bhas)>0:
                for i in range(len(bhas)):
                    dist = abs(depth -bhas.loc[i,'depth_out'])
                    if dist< dist1:
                        bhaid_dist=bhas.loc[i,'id']
                        dist1 =dist
                    if abs(depth -bhas.loc[i,'depth_out'])<30:
                        bhaid=bhas.loc[i,'id']
                        bha_len = bhas.loc[i,'bha_length']
                        if bha_len is None:
                            bha_len = min(depth/10, 1000)
                if bhaid is None:
                    bhaid = bhaid_dist
            bha_trip = current_trip[current_trip['bit_depth'] <= bha_len]
            bha_time =bha_trip["rig_time"].min()
            
            if len(intervals)>0:
                for i in range(len(intervals)):
                    if depth >= intervals.loc[i,'start_depth']-100 and depth <= intervals.loc[i,'end_depth']+100:
                        intervalid=intervals.loc[i,'id']
                    if abs(depth-intervals.loc[i,'end_depth'])<30:
                        intervalid1=intervals.loc[i,'id']
            start_time=current_trip["rig_time"].min()
            end_time =current_trip["rig_time"].max()
            trip_points = len(current_trip)
            trip_number=j
            if intervalid1 is not None:
                intervalid =intervalid1
            if current_trip["bit_depth"].min()< .1*depth:
                trip_style = "Full Trip"
            else: 
                trip_style="Short Trip"
            j =j+1
            
            arow2 =[direction,depth,start_time,end_time,trip_points,trip_number, trip_style,casing,bhaid,intervalid,bha_time,edr_raw]
            tripping.loc[len(tripping)] = arow2
            edrdata['trip_out_number']= list(map(lambda x,y: (trip_number if x>=start_time and x<=end_time else y),edrdata['rig_time'],edrdata['trip_out_number']))
    
    tripping.bha_time = tripping.bha_time.apply(lambda x : None if x=="NaT" else x)
    tripping = tripping.sort_values(["start_time"]).reset_index(drop = True)

    
    
    
    is_template =False
    objective = "Drill Baby Drill"
    status = "Complete"
    bha_number =1
    start_depth = 0
    
    if len(bhas)==0:
        for row in tripping.index:
            if row == 0 and tripping.loc[row,'trip_direction']==False:
                start_time=mintrip_time
                end_time=tripping.loc[row,'end_time']
                start_depth=mintrip_depth
                end_depth= tripping.loc[row,'hole_depth']
                
                arow =[ status, bha_number, start_depth, end_depth, start_time, end_time,is_template,objective,]
                bhas_trips.loc[len(bhas_trips)] = arow
                
                edrdata['A_bha_num']= list(map(lambda x,y: (bha_number if x>=start_time and x<=end_time else y),edrdata['rig_time'],edrdata['A_bha_num']))
    
                         
                bha_number = bha_number +1
            
            elif tripping.loc[row,'trip_direction']==True:
                start_time = tripping.loc[row,'start_time']
                start_depth= tripping.loc[row,'hole_depth']
                
            elif tripping.loc[row,'trip_direction']=="Out" and start_depth > 0:
                end_time=tripping.loc[row,'end_time']
                end_depth= tripping.loc[row,'hole_depth']
            
                arow =[ status, bha_number, start_depth, end_depth, start_time, end_time,is_template,objective,]
                bhas_trips.loc[len(bhas_trips)] = arow
                edrdata['A_bha_num']= list(map(lambda x,y: (bha_number if x>=start_time and x<=end_time else y),edrdata['rig_time'],edrdata['A_bha_num']))
                bha_number = bha_number +1
        bhas = bhas_trips
    
    
    return tripping,bhas, edrdata