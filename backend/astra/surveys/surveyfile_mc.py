# -*- coding: utf-8 -*-
"""

@author: BrianBlackwell
"""

#from passlib import sha256_crypt
# import pymysql
import numpy as np
from datetime import date
import os
from os.path import dirname, join
import pandas as pd
import numpy as np

#math symbols
import math
from math import pi,radians,ceil,floor,cos,sin,acos,degrees,tan,atan

def surveyfile_mc(survey_file, active_plan_file, active_survey):
    print("in surveyfile_mc")

    if(active_survey.count() != 0):
        # print("there is an active survey")
        print(active_survey)
        md0=float(active_survey[0].md)
        inc0 = float(active_survey[0].inc)
        azi0 = float(active_survey[0].azi)
        tvd0 = float(active_survey[0].tvd)
        north0 = float(active_survey[0].north)
        east0 = float(active_survey[0].east)
    else:
        print("no survey")
        md0 = 0
        inc0 = 0
        azi0 = 0
        tvd0 = 0
        north0 = 0
        east0 = 0

    if(active_plan_file.count() != 0):
        print("there is a active_plan_file", )
        plan_KOP = float(active_plan_file[0].plan_kop)
        VSPlane = float(active_plan_file[0].vsplane)
    else:
        print("no active_plan_file")
        plan_KOP = 0
        VSPlane = 0

    #change directory to current working directory
    'This File Will be loaded from the front end and then read'
    os.chdir(os.getcwd())

    # fline=open(survey_file, encoding="cp1252").readline().rstrip()
    # # [l for l in (line.strip() for line in f) if l]
    
    # for i in fline:
    
    fline = []
    
    # Remove blank lines
    with open(survey_file, encoding="cp1252") as f_in:
        fline = list(line for line in (l.strip() for l in f_in) if line)

    if fline[0] == "H":
        print('Hawkeye file')
        SurveyData= pd.read_csv(survey_file,sep=r"\s+",comment='H',header=None,names = ["md", "inc", "azi", "tvd", "north", "east"])
    elif fline[0] == "u":
        print('winsurve file')
        SurveyData= pd.read_csv(survey_file,sep=r"\s+",comment='u',header=None,names = ["md", "inc", "azi"])
    else:
        try: 
            print('drakewell file')
            SurveyData= pd.read_csv(survey_file,sep=r"\s+",comment='u',header=None,names = ["md", "inc", "azi"], usecols=["md", "inc", "azi"])
            SurveyData= SurveyData[pd.to_numeric(SurveyData['md'], errors='coerce').notnull()]


        except:
            print('We are not allowing this file type yet')
    
    SurveyData['inc']=SurveyData['inc'].astype(float)
    SurveyData['md']=SurveyData['md'].astype(float)
    SurveyData['azi']=SurveyData['azi'].astype(float)

    SurveyData=SurveyData.reset_index(drop = True)
    SurveyData['dedrindex'] = SurveyData.index.astype(int)
    SurveyData['active']=True

    
    if VSPlane is None:
        VSPlane =  SurveyData['azi'].tail(1)
    print(SurveyData.index[0])



    SurveyData['DLA_A']= list(map(lambda index,I1,I2,A1,A2: (acos(cos(radians(I2)-radians(I1))-sin(radians(I1))*sin(radians(I2))*(1-cos(radians(A2)-radians(A1))))) if index != 0 else (acos(cos(radians(I2)-radians(inc0))-sin(radians(inc0))*sin(radians(I2))*(1-cos(radians(A2)-radians(azi0))))) , SurveyData.index,SurveyData['inc'].shift(1),SurveyData['inc'], SurveyData['azi'].shift(1),SurveyData['azi']))
    SurveyData['dogleg']= list(map(lambda index,D1,D2,I1,I2,A1,A2: 0 if ((D2-D1) == 0 or (D2-md0) == 0) else (degrees(acos(cos(radians(I2)-radians(I1))-sin(radians(I1))*sin(radians(I2))*(1-cos(radians(A2)-radians(A1)))))/(D2-D1)*100) if D1> 0 and index != 0 else (degrees(acos(cos(radians(I2)-radians(inc0))-sin(radians(inc0))*sin(radians(I2))*(1-cos(radians(A2)-radians(azi0)))))/(D2-md0)*100), SurveyData.index,SurveyData['md'].shift(1),SurveyData['md'],SurveyData['inc'].shift(1),SurveyData['inc'], SurveyData['azi'].shift(1),SurveyData['azi']))
    SurveyData['RF'] = list(map(lambda B: 1 if B==0 else (2/B)*tan(B/2), SurveyData['DLA_A']))
    #SurveyData['TVD_I']= list(map(lambda index,D1,D2,I1,I2,RF: ((D2-D1)/2*(cos(radians(I1))+cos(radians(I2)))*RF) if D1> 0 and index != 0 else I2, SurveyData.index, SurveyData['md'].shift(1),SurveyData['md'],SurveyData['inc'].shift(1),SurveyData['inc'],SurveyData['RF']))
    SurveyData['TVD_I']= list(map(lambda index,D1,D2,I1,I2,RF: ((D2-D1)/2*(cos(radians(I1))+cos(radians(I2)))*RF) if index != 0 else (((D2-md0)/2*(cos(radians(inc0))+cos(radians(I2)))*RF)+tvd0), SurveyData.index, SurveyData['md'].shift(1),SurveyData['md'],SurveyData['inc'].shift(1),SurveyData['inc'],SurveyData['RF']))
    SurveyData['tvd']=SurveyData['TVD_I'].cumsum()
    SurveyData['North_I'] = list(map(lambda index,D1,D2,I1,I2,A1,A2,RF: ((D2-D1)/2*(sin(radians(I1))*cos(radians(A1))+sin(radians(I2))*cos(radians(A2)))*RF) if index != 0 else ((D2-md0)/2*(sin(radians(inc0))*cos(radians(azi0))+sin(radians(I2))*cos(radians(A2)))*RF)+north0, SurveyData.index,SurveyData['md'].shift(1),SurveyData['md'],SurveyData['inc'].shift(1),SurveyData['inc'], SurveyData['azi'].shift(1),SurveyData['azi'],SurveyData['RF']))
    SurveyData['north']=SurveyData['North_I'].cumsum()
    SurveyData['East_I']= list(map(lambda index,D1,D2,I1,I2,A1,A2,RF: ((D2-D1)/2*(sin(radians(I1))*sin(radians(A1))+sin(radians(I2))*sin(radians(A2)))*RF) if index != 0 else ((D2-md0)/2*(sin(radians(inc0))*sin(radians(azi0))+sin(radians(I2))*sin(radians(A2)))*RF)+east0, SurveyData.index,SurveyData['md'].shift(1),SurveyData['md'],SurveyData['inc'].shift(1),SurveyData['inc'], SurveyData['azi'].shift(1),SurveyData['azi'],SurveyData['RF']))
    SurveyData['east']=SurveyData['East_I'].cumsum()
    SurveyData['build_rate'] = list(map(lambda index,D1,D2,I1,I2,A1,A2,RF: 0 if ((D2-D1) == 0 or (D2-md0) == 0) else ((I2-I1)/(D2-D1)*100) if index != 0 else ((I2-inc0)/(D2-md0)*100), SurveyData.index,SurveyData['md'].shift(1),SurveyData['md'],SurveyData['inc'].shift(1),SurveyData['inc'], SurveyData['azi'].shift(1),SurveyData['azi'],SurveyData['RF']))
    SurveyData['turn_rate']= list(map(lambda index,D1,D2,I1,I2,A1,A2,RF: 0 if ((D2-D1) == 0 or (D2-md0) == 0) else  ((A2-A1)/(D2-D1)*100) if index != 0 else ((A2-azi0)/(D2-md0)*100), SurveyData.index,SurveyData['md'].shift(1),SurveyData['md'],SurveyData['inc'].shift(1),SurveyData['inc'], SurveyData['azi'].shift(1),SurveyData['azi'],SurveyData['RF']))
    SurveyData['calculated_ang']=list(map(lambda NS1,EW1: (((EW1)**2+(NS1)**2)**.5), SurveyData['north'],SurveyData['east']))
    SurveyData['calculated_tf']=list(map(lambda NS1,EW1,VSPlan: degrees(atan(EW1)) if NS1 is None or NS1 == 0 else degrees(atan((EW1)/(NS1))) if VSPlan >= 0 and VSPlan < 90 else 180 + degrees(atan((EW1)/(NS1))) if VSPlan >= 90 and VSPlan < 180 else 180 - degrees(atan((EW1)/(NS1))) if VSPlan >= 180 and VSPlan < 270 else 360 - degrees(atan((EW1)/(NS1))) , SurveyData['north'],SurveyData['east'],SurveyData['azi'].shift(-1)))
    SurveyData['vertical_section']=list(map(lambda N,E,CA: N*cos(radians(VSPlane))+E*sin(radians(VSPlane)), SurveyData['north'],SurveyData['east'], SurveyData['calculated_tf']))
    SurveyData['A_StepOut'] = list(map(lambda md,md1,AZ: 0 if math.isnan(md1) else ((md-md1)*sin(radians(VSPlane-AZ)) if VSPlane > 90 and VSPlane < 180 else (md-md1)*sin(radians(AZ-VSPlane))) if md< plan_KOP else 0,SurveyData['md'],SurveyData['md'].shift(1), SurveyData['azi'])) 

    SurveyData['step_out']=SurveyData['A_StepOut'].cumsum()

    SurveyData = SurveyData[['md','inc','azi','tvd','north','east','vertical_section','dogleg','build_rate','turn_rate', 'calculated_ang', 'calculated_tf','step_out' ]]

    min_survey_md = SurveyData['md'].min()
    max_survey_md = SurveyData['md'].max()

    print("survey - all surveys saved")
    return SurveyData, min_survey_md, max_survey_md