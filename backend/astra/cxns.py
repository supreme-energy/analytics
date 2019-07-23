# -*- coding: utf-8 -*-
"""
@author: BrianBlackwell
"""
import numpy as np

import pandas as pd


from os.path import dirname, join
#************************* CONSTANTS   ********************************c*********************************8
WellName ="Sanchez_Well2"
#Define EDR Data Triggers
ROTATE_THRESH = 25
BLOCK_THRESH = 15
BITTHRESH = 1
HOOKLOAD_THRESH = 55
FLOW_THRESH = 30
TRIP_THRESH = 150
CXN_THRESH = 30

def connectit(edrdata):
    global Connections
    """Reduce data set to potential connection trigger points"""
    CXNStart = edrdata[edrdata['bit_status'] == -1]; CXNStart = CXNStart[['rig_time']]; CXNStart.index = CXNStart.index.astype(int)#; CXNStart['StartIndex']=CXNStart.index
    CXNSin = edrdata[edrdata['slip_status'] == 2]; CXNSin = CXNSin[['rig_time']]; CXNSin.index = CXNSin.index.astype(int)#; CXNSin['SlipInIndex']=CXNSin.index
    CXNPoff = edrdata[edrdata['pump_status'] == -1]; CXNPoff = CXNPoff[['rig_time']]; CXNPoff.index = CXNPoff.index.astype(int)#;  CXNPoff['PumpsOnIndex']=CXNPoff.index
    CXNSout = edrdata[edrdata['slip_status'] == -1]; CXNSout = CXNSout[['rig_time']]; CXNSout.index = CXNSout.index.astype(int)#; CXNSout['SlipOutIndex']=CXNSout.index
    CXNPon = edrdata[edrdata['pump_status'] == 2]; CXNPon = CXNPon[['rig_time']]; CXNPon.index = CXNPon.index.astype(int)#; CXNPon['PumpsOnIndex']=CXNPon.index
    CXNEnd = edrdata[edrdata['bit_status'] == 2]; CXNEnd = CXNEnd[['rig_time']]; CXNEnd.index = CXNEnd.index.astype(int)#; CXNEnd['EndIndex']=CXNEnd.index
    """Concatenate all Connection points into single dataframe"""
    #Connections = pd.concat([CXNStart, CXNSin, CXNPoff, CXNSout, CXNPoff, CXNEnd], axis=1,sort=True)
    #Connections.columns = ['CXN Start', 'Slips In', 'Pumps Off', 'Slips Out', 'Pumps On', 'CXN End']
    #Connections =pd.DataFrame(columns =['cxn_count','depth','day_night', 'total_time', 'Full CXN Time2', 'btm_slips', 'slips_slips', 'slips_btm', 'pump_cycles','pump_pump', 'CXN Start', 'Slips In', 'Pumps Off', 'Slips Out', 'Pumps On', 'CXN End'])
    Connections =pd.DataFrame(columns =['cxn_count','depth','day_night', 'total_time', 'btm_slips', 'slips_slips', 'slips_btm', 'pump_cycles','pumps_pumps','edr_raw_id'])
 
                                            
    """Find Acctual Connections by finding closest start trigger less than an end trigger
        Variables:  S = Connection Start Index Row
                    E = Connection End Index Row
                    PoffC = Count of Pumps off
                    PonC = Count of Pumps on
                    PoffS = First Pumps off event
                    PonE = Last Event of Pumps on
                    SinC = count of slips in
                    SoutC = count of slips out
                    CXNC = Count of Connections
                    FCXCT = Full Connection Time (off BTM to On BTM)
                    OBTS = Off Bottom to Slips
                    STS = Slips to Slips
                    STOB = SLips to on Bottom
                    PCC = Pump Cyle Count
                    PTP = Pump to Pump
                    Tour = Day or night Connection
                    TCXN = Total Connection Time
                    ACXNTS = Average Connection Time (Combined Avearages)
                    DACXNs = Day Average Connection Time (Combined Avearages)
                    NACXNs = Night Average Connection Time (Combined Avearages)
                    ACXNT = Average Connection Time
                    DACXN = Day Average Connection Time
                    NACXN = Night Average Connection Time
                    FCXN  =  Fastest Connection Time
                    FWACT = Full Well Average Connection Time
                    FWFCT = Full Well Fastest Connection Time
                    
                    DACT = Day Average Connection Time
                    NACT = Night Average Connection Time
                    NOSAT
                    
    """
    edrdata['cxn_count']=0
    S=E=CXNC=PoffC=PoffS=SinS=SoutE=PonE=PonC=0
    for E in CXNEnd.index:
       SS = CXNStart.index[CXNStart.index < E].max()
       if SS>S:
           S= SS
           MDS =float(edrdata.loc[S, 'hole_depth'])
           MDE = float(edrdata.loc[E, 'hole_depth'])
           DTS =edrdata.loc[S, 'rig_time']
           DTE = edrdata.loc[E, 'rig_time']
           PonC = np.logical_and(CXNPon.index>S, CXNPon.index<E).sum()
           SinC = np.logical_and(CXNSin.index>S, CXNSin.index<E).sum()
           SoutC = np.logical_and(CXNSout.index>S, CXNSout.index<E).sum()
           PoffC = np.logical_and(CXNPoff.index>S, CXNPoff.index<E).sum()
           if PoffC > 0 and PonC > 0 and SinC > 0 and SoutC > 0:
               PoffS = CXNPoff.index[CXNPoff.index > S].min()
               PonE = CXNPon.index[CXNPon.index < E].max()
               SinS = CXNSin.index[CXNSin.index > S].min()
               SoutE = CXNSout.index[CXNSout.index < E].max()
               FXCT = (edrdata.loc[E, "rig_time"] - edrdata.loc[S, "rig_time"])/np.timedelta64(1, 'm')
               OBTS = (edrdata.loc[SinS, "rig_time"] - edrdata.loc[S, "rig_time"])/np.timedelta64(1, 'm')
               STS = (edrdata.loc[SoutE, "rig_time"] - edrdata.loc[SinS, "rig_time"])/np.timedelta64(1, 'm')
               STOB = (edrdata.loc[E, "rig_time"] - edrdata.loc[SoutE, "rig_time"])/np.timedelta64(1, 'm')
               CDepth = edrdata.loc[S, "hole_depth"]
               edr_raw = edrdata.loc[S, 'edr_raw_id']
               FXCT2 = OBTS+STS+STOB
               PCC = min(PoffC,PonC)
               PTP = (edrdata.loc[PonE, "rig_time"] - edrdata.loc[PoffS, "rig_time"])/np.timedelta64(1, 'm')
               Tour = False
               if edrdata.loc[S,"rig_time"].hour >= 6 and edrdata.loc[S,"rig_time"].hour < 18:
                   Tour = True
               if FXCT2 <  CXN_THRESH: 
                   edrdata.iloc[S:E,edrdata.columns.get_loc('rig_activity2')]= int(9)
                   CXNC += 1
                   #arow2 =[CXNC,CDepth, Tour,FXCT,FXCT2,OBTS,STS,STOB,PCC,PTP,S,PoffS,SinS,SoutE,PonE,E]
                   arow2 =[CXNC,CDepth,Tour,FXCT,OBTS,STS,STOB,PCC,PTP,edr_raw]
                   Connections.loc[len(Connections)] = arow2
                   edrdata['cxn_count']= list(map(lambda x,y: (y if x< DTS else CXNC if x>=DTS and x<=DTE else 0),edrdata['rig_time'],edrdata['cxn_count']))
               
     
    #print(Connections)              
    Connections['total_time']=Connections['total_time'].round(decimals = 3)
    Connections['btm_slips']=Connections['btm_slips'].round(decimals = 3)
    Connections['slips_slips']=Connections['slips_slips'].round(decimals = 3)
    Connections['slips_btm']=Connections['slips_btm'].round(decimals = 3)
    Connections['pumps_pumps']=Connections['pumps_pumps'].round(decimals = 3)
    return Connections, edrdata