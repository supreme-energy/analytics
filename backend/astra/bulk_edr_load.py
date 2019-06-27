# -*- coding: utf-8 -*-
"""
@author: BrianBlackwell
"""
# Pandas for data management
import pandas as pd
from pandas.io import gbq

#numpy for number management
import numpy as np
from numpy import cumsum, inf
import scipy as sy
from scipy.stats import linregress

# os methods for manipulating paths
import os
from os.path import dirname, join
os.chdir(os.getcwd())
# Bokeh basics 
from bokeh.plotting import figure, gridplot, output_file, show
from bokeh.models import LinearAxis, Range1d, CategoricalColorMapper, LabelSet, Label, ColumnDataSource, CDSView, BooleanFilter, HoverTool
from bokeh.io import export_png, curdoc
from bokeh.layouts import widgetbox, row, column
from bokeh.models.widgets import DataTable, DateFormatter, TableColumn ,CheckboxGroup, RangeSlider, Toggle, Tabs
from bokeh.util.browser import view
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

#time management
from datetime import datetime,date
import time
from dbconnect import connection

#math symbols
from math import pi,radians,ceil,floor,tan,sin

#calculate runtime
start_time = time.time()
#c,conn,engine= connection()




#define gloabal variables to be calculated by analyzer
global WellName,WellNum,OpName, County, State, enddate, PIZ, VSPlane, WellType, maggrav_idx
WellName ="Apollo 2-11-4N 12H"
welln=1000989
#opn =100006

#WellName = pd.read_sql_query("SELECT name FROM WELLS WHERE (well_id) = (%s)",conn,params=(welln,))
#WellName = str(WellName.loc[0,'name'])

pdate=date.today()
# load scripts
#from main import runthatshit
from scripts.edr_mapper import edrMapper
#from scripts.live_cleaner import Phase2
from scripts.edr_cleaner import cleanitup,simpleclean
from scripts.drilldata import drillitup, Tourism, SlipNSlide, Roundwego,SlideSheet,AstraArrays

from scripts.astra_plots import fw_astra,param_astra,param_astra2,fw_astra_RS
from scripts.cxns import connectit
from scripts.surveys_mc import Min_Curve
from scripts.Fancy_Charts import PFancy3,PFancy4
from scripts.formation_plots import formplots,formplots2
from scripts.p_lateral import Lat_Plots
from scripts.bp_SVR import SVR
from scripts.TF_Bokeh import TF_Plot,TF_Seg


#change directory to current working directory
os.chdir(os.getcwd())
#runthatshit(welln,opn,pdate)
#import current well data from CSVS
edrastra = pd.read_csv(join(dirname(__file__), 'data/'+WellName,"EDR_Data.csv"))
EDR_Key=1
"""
try:
    edrdata = pd.read_sql_query("SELECT * FROM ASTRAEDR WHERE (well_id,active) = (%s,%s)",conn,params=(welln,1))
    if len(edrdata)<1:
        print("No EDR Data Was Found!")
        EDR_Key=0
except:
    print("No EDR Data Was Found!")
    EDR_Key=0
"""    
edrastra = pd.read_csv(join(dirname(__file__), 'data/'+WellName,"EDR_Data.csv"))
edrdata=edrMapper(edrastra)

