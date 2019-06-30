import os
from os.path import dirname, join
import pandas as pd
import sqlite3
from datetime import date
os.chdir(os.getcwd())

from edr_mapper import edrmapper
from edr_bulk_cleaner import cleanitup,trippedit
from edr_bulk_drilling import drillitup,SlideSheet,finish_bhas
from cxns import connectit

import time
start = time.time()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
con =sqlite3.connect(os.path.join(BASE_DIR, 'astra\db.sqlite3'))


pdate = date.today() 

#rom edr_loader import edrloads
DATA_FREQUENCY = 10
RIG_NAME = "Rig 1"
WELL_UID="6ab0ff9b-de84-412b-a69c-e784ea3a7951"
WellName="Clydesdale 3H"
job_ID = "1"
VSPlane =181


def sql_fetch(con):
    cursorObj = con.cursor()
    
    cursorObj.execute("SELECT * FROM jobs_job WHERE id = (?)", (job_ID,))
    
    job = cursorObj.fetchall()
    if job:
        print("we found a job")
        cursorObj.execute("SELECT * FROM jobs_wellconnector WHERE uid = (?)", (WELL_UID,))
        wellconnector = cursorObj.fetchall()
    
        if not wellconnector:
            print("New Well Connection")
            cursorObj.execute("INSERT INTO jobs_wellconnector (uid, well_name, rig_name, data_frequency, job_id) VALUES (?, ?, ?, ?, ?)", 
                              (WELL_UID,WellName,RIG_NAME,DATA_FREQUENCY,job_ID))
            con.commit()
        else:
            print("This Data Feed Exists")
        
    else:
        print("New Job Created")
        #Load New Job to Database
        cursorObj.execute("INSERT INTO jobs_job (name, sses_id, creation_date) VALUES (?, ?, ?)", 
                          (WellName,job_ID, pdate))
        con.commit() 
        #Job Connection to EDR Data
        cursorObj.execute("INSERT INTO jobs_wellconnector (uid, well_name, rig_name, data_frequency, job_id) VALUES (?, ?, ?, ?, ?)", 
                          (WELL_UID,WellName,RIG_NAME,DATA_FREQUENCY,job_ID))
        con.commit()   

    cursorObj.execute("SELECT id,name,start_depth,end_depth,hole_size FROM jobs_interval WHERE job_id = (?)", (job_ID,))
    intervals = pd.DataFrame(cursorObj.fetchall(),columns = ['id','name','start_depth','end_depth','hole_size'])

    cursorObj.execute("SELECT id,bha_number,bha_length,depth_in,depth_out,time_in,time_out,hole_size FROM bhas_bha WHERE job_id = (?)", (job_ID,))
    bhas = pd.DataFrame(cursorObj.fetchall(),columns=['id','bha_number','bha_length','depth_in','depth_out','time_in','time_out','hole_size'])
    
    return(intervals,bhas)
    
def sql_loadraw(con,edrdata):
    cursorObj = con.cursor()
    
    cursorObj.execute("SELECT * FROM edrs_edrraw WHERE uid = (?)", (WELL_UID,))
    well_edrraw = cursorObj.fetchall()
    edrdata= edrdata[['job_id','uid','creation_date','active','rig_time', 'hole_depth', 'wob', 'td_rpm', 'td_torque', 'rop_a', 'diff_press', 'flow_in', 'pump_press', 'edr_mse', 'bit_depth', 'block_height', 'gamma_ray', 'hookload', 'mud_ti', 'mud_to', 'mud_wi', 'mud_wo', 'overpull', 'strokes_total', 'rop_i', 'svy_azi', 'svy_inc', 'tf_grav', 'tf_mag', 'tvd', 'flow_out', 'ann_press', 'back_press', 'edr_RS1', 'edr_RS2', 'edr_RS3', 'edr_slips', 'oscillator']]
       
    if not well_edrraw:
        edrdata.to_sql(con=con, name='edrs_edrraw', if_exists='append', index=False, chunksize =1000)
        con.commit()
    
        print("Loaded Raw Data")

        
    else:
        print("Raw Data already exists")
        
        
    cursorObj.execute("SELECT id,rig_time FROM edrs_edrraw WHERE uid = (?)", (WELL_UID,))
    rawid = pd.DataFrame(cursorObj.fetchall(),columns = ['edr_raw_id','rig_time'])
    try:
        edrdata=pd.merge(edrdata,rawid, on='rig_time')
    except:
        rawid['rig_time']=pd.to_datetime(rawid['rig_time'])
        edrdata=pd.merge(edrdata,rawid, on='rig_time')


    return edrdata

def sql_loadproc(con,processed_data):
    cursorObj = con.cursor()
    
    cursorObj.execute("SELECT * FROM edrs_edrprocessed WHERE uid = (?)", (WELL_UID,))
    well_edrproc = cursorObj.fetchall()
    processed_data= processed_data[['uid','creation_date','edr_raw_id','data_gap', 'time_elapsed', 'day_num', 'day_night', 'bit_status', 'slip_status', 'block_status', 'pump_status', 'trip_status', 'trip_status2', 'rot_sli', 'rig_activity', 'rig_activity2', 'clean_1', 'clean_2', 'clean_3','trip_in_number','trip_out_number','cxn_count','bit_variance']]

    
    if not well_edrproc:
        processed_data.to_sql(con=con, name='edrs_edrprocessed', if_exists='append', index=False, chunksize =1000)
        con.commit()
    
        print("Loaded Processed Data")

        
    else:
        print("Processed Data already exists")
        
def sql_loadtrip(con,tripping):
    cursorObj = con.cursor()
    
    cursorObj.execute("SELECT * FROM edrs_edrtrip WHERE uid = (?)", (WELL_UID,))
    well_trip = cursorObj.fetchall()
    tripping= tripping[['uid','creation_date','trip_direction','depth','start_time','end_time','total_time','bha_time', 'trip_count','casing','bha_id','interval_id','edr_raw_id']]
    
    
    if not well_trip:
        tripping.to_sql(con=con, name='edrs_edrtrip', if_exists='append', index=False, chunksize =1)
        con.commit()
    
        print("Loaded Trip Data")

        
    else:
        print("Trip Data already exists")        
def sql_loaddrill(con,drill_data):
    cursorObj = con.cursor()
    cursorObj.execute("SELECT * FROM edrs_edrdrilled WHERE uid = (?)", (WELL_UID,))
    well_edrdrill = cursorObj.fetchall()
    drill_data= drill_data[['uid','creation_date','edr_raw_id','drilled_ft', 'bit_rpm', 'normalized_tf', 'slide_count','slide_status', 'rot_status', 'rot_count', 'astra_mse', 'slide_value_tf', 'rop_i', 'rop_a', 'stand_count']]
    #drill_data= drill_data[['uid','creation_date','edr_raw_id','drilled_ft', 'bit_rpm', 'slide_status', 'rot_status','slide_count', 'rot_count', 'rop_i', 'rop_a', 'stand_count']]
    
    if not well_edrdrill:
        drill_data.to_sql(con=con, name='edrs_edrdrilled', if_exists='append', index=False, chunksize =1000)
        con.commit()
    
        print("Loaded Drill Data")

        
    else:
        print("Drill Data already exists")
        

def sql_loadcxn(con,connections):
    cursorObj = con.cursor()
    
    cursorObj.execute("SELECT * FROM edrs_edrcxn WHERE uid = (?)", (WELL_UID,))
    well_edrcxn = cursorObj.fetchall()
    connections= connections[['uid','creation_date','cxn_count','day_night', 'total_time', 'btm_slips', 'slips_slips', 'slips_btm', 'pump_cycles','pumps_pumps','edr_raw_id']]
    
    
    if not well_edrcxn:
        connections.to_sql(con=con, name='edrs_edrcxn', if_exists='append', index=False, chunksize =1000)
        con.commit()
    
        print("Loaded Connections Data")

        
    else:
        print("Connections already exists")

intervals,bhas=sql_fetch(con)

edrastra = pd.read_csv(join(dirname(__file__), 'data/',WELL_UID+".csv"))
print("--- %s seconds to open ---" % (time.time() - start))
edrdata=edrmapper(edrastra)
#edrdata.replace(-999.25, None)

edrdata['creation_date']=pdate
edrdata['job_id']=job_ID
edrdata['uid']=WELL_UID
edrdata['active']=True

edrdata= sql_loadraw(con,edrdata)

edrdata['hole_size']=None
if len(intervals)>0:
    edrdata['interval_id']=None
    for i in range(len(intervals)): 
        iuid=intervals.loc[i,'id']
        ihs=intervals.loc[i,'hole_size']
        minmd =intervals.loc[i,'start_depth']
        if i < len(intervals)-1:
            maxmd =intervals.loc[i,'end_depth']
        else:
            maxmd =edrdata['hole_depth'].max()

        edrdata['interval_id']= list(map(lambda x,y: (iuid if x>= minmd and x<=maxmd else y),edrdata['hole_depth'],edrdata['interval_id']))
        edrdata['hole_size']= list(map(lambda x,y: (ihs if x>= minmd and x<=maxmd else y),edrdata['hole_depth'],edrdata['hole_size']))

if len(bhas)>0:
    edrdata['bha_id']=None
    for i in range(len(bhas)): 
        bhaid=bhas.loc[i,'id']
        bhahs=bhas.loc[i,'hole_size']
        minmd =bhas.loc[i,'depth_in']
        if i < len(bhas)-1:
            maxmd =bhas.loc[i,'depth_out']
        else:
            maxmd =edrdata['hole_depth'].max()

        edrdata['bha_id']= list(map(lambda x,y: (bhaid if x>= minmd and x<=maxmd else y),edrdata['hole_depth'],edrdata['bha_id']))
        edrdata['hole_size']= list(map(lambda x,y: (bhahs if x>= minmd and x<=maxmd else y),edrdata['hole_depth'],edrdata['hole_size']))



edrdata['td_torque']=edrdata['td_torque'].astype('float64')
edrdata['flow_out']=edrdata['flow_out'].astype('float64')

processed_data= cleanitup(edrdata,DATA_FREQUENCY)
connections,processed_data = connectit(processed_data,)
connections['creation_date']=pdate
connections['job_id']=job_ID
connections['uid']=WELL_UID

sql_loadcxn(con,connections)
print("processed")
print("--- %s seconds ---" % (time.time() - start))
tripping,bhas,processed_data = trippedit(processed_data,DATA_FREQUENCY,bhas,intervals)
tripping['creation_date']=pdate
tripping['job_id']=job_ID
tripping['uid']=WELL_UID

sql_loadproc(con,processed_data)
sql_loadtrip(con,tripping)
print("--- %s seconds ---" % (time.time() - start))


drilling_data= drillitup(processed_data,VSPlane)
print("drilled")
print("--- %s seconds ---" % (time.time() - start))
drilling_data=SlideSheet(drilling_data)
print("slid")
print("--- %s seconds ---" % (time.time() - start))
sql_loaddrill(con,drilling_data)






