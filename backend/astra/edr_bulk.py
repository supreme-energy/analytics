import os
from os.path import dirname, join
import pandas as pd
from datetime import datetime

os.chdir(os.getcwd())

from totco_mapper import edrmapper
from edr_loader import edrloads

RIG_ID = 6419
DATA_FREQUENCY = 5
RIG_NAME = "H&P 625"
ANIMO_RIGID = 6
WELL_UID="A9ebf6c8b-4f5a-4acc-a732-0ada2a08bb8"
WellName="Apollo 2-11-4N 12H"
job_ID = ""

edrastra = pd.read_csv(join(dirname(__file__), 'data/',WELL_UID+".csv"))
edrdata=edrmapper(edrastra)
edrdata['rig_time']=edrdata['rig_time']+"-05:00"
edrdata['td_torque']=edrdata['td_torque'].astype('float64')
edrdata['flow_out']=edrdata['flow_out'].astype('float64')
edrloads(WELL_UID,edrdata, WellName, job_ID)
