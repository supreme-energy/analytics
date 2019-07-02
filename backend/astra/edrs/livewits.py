# -*- coding: utf-8 -*-
"""
Created on Tue Sep 18 21:52:19 2018
Updated on Mon May 27 23:26:00 2019
@author: BrianBlackwell
"""

import pandas as pd
import numpy as np
import csv
import xml.etree.ElementTree as ET
import os
from os.path import dirname, join
import time
import re
from locale import atof
from os.path import basename
from urllib.parse import urljoin
from lxml import html, etree
import requests
import urllib.request
import urllib
import bs4
import base64
import suds
import psutil
from django.utils.dateparse import parse_datetime

# calculate runtime
start_time = time.time()

data_frequency = 10

username = 'sses_us'
password = 'PolarisTexas'
url = 'http://witsml.polarisguidance.com:8081/services/polarisWMLS'
uidWell ='6ab0ff9b-de84-412b-a69c-e784ea3a7951'
uidWellbore="65f6cccc-4351-437e-be8c-c2244d7abb55"
date = parse_datetime("1970-05-26T05:25:18-05:00")

def edrdata(uidWell, date, data_frequency,url,username,password):
    headers = {'content-type': 'text/xml; charset=utf-8',
               'Content-Length': '8'}
    # print("uidWell = ", uidWell)
    # print("uidWellbore = ", uidWellbore)
    # print("well_name = ", well_name)
    # print("rig_name = ", rig_name)

    rig_body = """
      <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/" xmlns:tns="http://www.witsml.org/wsdl/120" xmlns:types="http://www.witsml.org/wsdl/120/encodedTypes" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
      <soap:Body soap:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
        <q1:WMLS_GetFromStore xmlns:q1="http://www.witsml.org/message/120">
          <WMLtypeIn xsi:type="xsd:string">log</WMLtypeIn>
          <QueryIn xsi:type="xsd:string">&lt;logs xmlns="http://www.witsml.org/schemas/131" version="1.3.1.1"&gt;
      &lt;log uidWell="%s" uidWellbore="65f6cccc-4351-437e-be8c-c2244d7abb55" uid="DATETIME_LOG"&gt;
        &lt;nameWell /&gt;
        &lt;nameWellbore /&gt;
        &lt;name /&gt;
        &lt;objectGrowing /&gt;
        &lt;dataRowCount /&gt;
        &lt;serviceCompany /&gt;
        &lt;runNumber /&gt;
        &lt;bhaRunNumber /&gt;
        &lt;pass /&gt;
        &lt;creationDate /&gt;
        &lt;description /&gt;
        &lt;indexType /&gt;
        &lt;startIndex uom="332" /&gt;
        &lt;endIndex uom="400" /&gt;
        &lt;stepIncrement uom="" numerator="" denominator="" /&gt;
        &lt;startDateTimeIndex&gt;%s&lt;/startDateTimeIndex&gt;
        &lt;endDateTimeIndex /&gt;
        &lt;direction /&gt;
        &lt;indexCurve columnIndex="" /&gt;
        &lt;nullValue /&gt;
        &lt;logParam index="" name="" uom="" description="" /&gt;
        &lt;logCurveInfo uid=""&gt;
          &lt;mnemonic /&gt;
          &lt;classWitsml /&gt;
          &lt;unit /&gt;
          &lt;mnemAlias /&gt;
          &lt;nullValue /&gt;
          &lt;alternateIndex /&gt;
          &lt;wellDatum uidRef="" /&gt;
          &lt;minIndex uom="" /&gt;
          &lt;maxIndex uom="" /&gt;
          &lt;minDateTimeIndex /&gt;
          &lt;maxDateTimeIndex /&gt;
          &lt;columnIndex /&gt;
          &lt;curveDescription /&gt;
          &lt;sensorOffset uom="" /&gt;
          &lt;dataSource /&gt;
          &lt;densData uom="" /&gt;
          &lt;traceState /&gt;
          &lt;traceOrigin /&gt;
          &lt;typeLogData /&gt;
          &lt;axisDefinition uid=""&gt;
            &lt;order /&gt;
            &lt;count /&gt;
            &lt;name /&gt;
            &lt;propertyType /&gt;
            &lt;uom /&gt;
            &lt;doubleValues /&gt;
            &lt;stringValues /&gt;
          &lt;/axisDefinition&gt;
        &lt;/logCurveInfo&gt;
        &lt;logData&gt;
          &lt;data /&gt;
        &lt;/logData&gt;
        &lt;commonData&gt;
          &lt;sourceName /&gt;
          &lt;dTimCreation /&gt;
          &lt;dTimLastChange /&gt;
          &lt;itemState /&gt;
          &lt;comments /&gt;
        &lt;/commonData&gt;
        &lt;customData /&gt;
      &lt;/log&gt;
    &lt;/logs&gt;</QueryIn>
          <OptionsIn xsi:type="xsd:string">returnElements=requested</OptionsIn>
        </q1:WMLS_GetFromStore>
      </soap:Body>
    </soap:Envelope>
    """ % (uidWell, date)

    response = requests.post(
        url, data=rig_body, headers=headers, auth=(username, password))

    root = ET.fromstring(response.text)

    xml_content = ET.fromstring(root.find(".//XMLout").text)
    
    mnemonic = xml_content.findall(
        ".//{http://www.witsml.org/schemas/131}mnemonic")
    data = xml_content.findall(".//{http://www.witsml.org/schemas/131}data")
    log_curve_info = xml_content.findall(
        ".//{http://www.witsml.org/schemas/131}logCurveInfo")
    
    header_names = []

    for i in range(len(mnemonic)):
        header_names += [mnemonic[i].text]

    witsheader = pd.DataFrame([])

    for i in range(len(data)):
        x = re.split(r',', data[i].text)

        df = pd.DataFrame(x).T
        witsheader = witsheader.append(df)

    witsheader.columns = header_names

    # print(witsheader)
    ''' this is the order of columns animo wants to map into to allow for merge into edr_raw table'''
    animo_headers = ['rig_time', 'ann_press', 'rop_a', 'back_press', 'edr_mse', 'bit_depth', 'block_height', 'mud_wi', 'mud_wo', 'diff_press',
                     'rop_i', 'pump_press', 'flow_in', 'flow_out', 'gamma_ray', 'edr_RS1', 'edr_RS2', 'edr_RS3', 'overpull', 'edr_slips',
                     'svy_azi', 'tf_grav', 'svy_inc', 'tf_mag', 'hookload', 'td_rpm', 'td_torque', 'mud_ti', 'mud_to', 'hole_depth', 'total_spm',
                     'strokes_total', 'tvd', 'wob']
        
    ''' MISSING SOME NEEDED INFO FOR ANIMO TO RUN FROM LIVE SERVER WHEN FULL LIST IS INTRODUCED THESE MUST MATCH THE ORDER OF EQUIVALENCE TO animo_headers'''
    sses_headers = [['DateTime', 'GPM', 'GR', 'GAMA', 'TVD', 'SLIDEINDICATOR', 'RPS2R', 'VS', 'RES', 'GTOTAL', 'BITDEPTH', 'FLOWOUT', 'SPP', 'DIP', 'RPM', 'GAS', 'RAD4R', 'TEMP', 'TEMPERATURE', 'CONFIDENCE', 'PULSEAMP', 'TRQ', 'HOOKLOAD', 'RPD2R', 'GTF', 'MTF', 'TRT', 'WOB', 'DEP', 'PMPP', 'INC', 'BLOCKHEIGHT', 'AZM', 'ROP']]
    
    ''' TOTCO Headers   
    edrraw = witsheader[['RIGTIME', 'ANN_PRESSURE', 'AVG_ROP_FT_HR', 'Back Pressure', 'Basic MSE', 'BIT_DEPTH', 'BLOCK_POS', 'DENS_IN', 'DENS_OUT',
                         'DIFF_PRESS', 'FAST_ROP_FT_HR', 'Flow Pressure', 'FLOW_IN', 'FLOW_OUT', 'GAMMA_RAY', 'IADC_RIG_ACTIVITY', 'IADC_RIG_ACTIVITY2',
                         'IADC_RIG_ACTIVITY3', 'Overpull', 'SLIPS_STAT', 'SRV_AZI', 'SRV_GRA_TF', 'SRV_INC', 'SRV_MAG_TF', 'STRING_WEIGHT', 'TD_SPEED',
                         'TD_TORQUE', 'TEMP_IN', 'TEMP_OUT', 'TOT_DPT_MD', 'TOT_SPM', 'TOT_STK', 'TVD', 'WOB']]

    '''
    edrraw.columns = animo_headers

    return (edrraw)


def timeremarks(rig_id):
    url, headers, username, password, uidWell, uidWellbore, well_name, rig_name = connect(
        rig_id)

    remarks_body = """
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/" xmlns:tns="http://www.witsml.org/wsdl/120" xmlns:types="http://www.witsml.org/wsdl/120/encodedTypes" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
      <soap:Body soap:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
        <q1:WMLS_GetFromStore xmlns:q1="http://www.witsml.org/message/120">
          <WMLtypeIn xsi:type="xsd:string">log</WMLtypeIn>
          <QueryIn xsi:type="xsd:string">&lt;logs xmlns="http://www.witsml.org/schemas/131" version="1.3.1.1"&gt;
      &lt;log uidWell="%s" uidWellbore="%s" uid="Time_Remarks"&gt;
        &lt;nameWell /&gt;
        &lt;nameWellbore /&gt;
        &lt;name /&gt;
        &lt;objectGrowing /&gt;
        &lt;dataRowCount /&gt;
        &lt;serviceCompany /&gt;
        &lt;runNumber /&gt;
        &lt;bhaRunNumber /&gt;
        &lt;pass /&gt;
        &lt;creationDate /&gt;
        &lt;description /&gt;
        &lt;indexType /&gt;
        &lt;startIndex uom="" /&gt;
        &lt;endIndex uom="" /&gt;
        &lt;stepIncrement uom="" numerator="" denominator="" /&gt;
        &lt;startDateTimeIndex /&gt;
        &lt;endDateTimeIndex /&gt;
        &lt;direction /&gt;
        &lt;indexCurve columnIndex="" /&gt;
        &lt;nullValue /&gt;
        &lt;logParam index="" name="" uom="" description="" /&gt;
        &lt;logCurveInfo uid=""&gt;
          &lt;mnemonic /&gt;
          &lt;classWitsml /&gt;
          &lt;unit /&gt;
          &lt;mnemAlias /&gt;
          &lt;nullValue /&gt;
          &lt;alternateIndex /&gt;
          &lt;wellDatum uidRef="" /&gt;
          &lt;minIndex uom="" /&gt;
          &lt;maxIndex uom="" /&gt;
          &lt;minDateTimeIndex /&gt;
          &lt;maxDateTimeIndex /&gt;
          &lt;columnIndex /&gt;
          &lt;curveDescription /&gt;
          &lt;sensorOffset uom="" /&gt;
          &lt;dataSource /&gt;
          &lt;densData uom="" /&gt;
          &lt;traceState /&gt;
          &lt;traceOrigin /&gt;
          &lt;typeLogData /&gt;
          &lt;axisDefinition uid=""&gt;
            &lt;order /&gt;
            &lt;count /&gt;
            &lt;name /&gt;
            &lt;propertyType /&gt;
            &lt;uom /&gt;
            &lt;doubleValues /&gt;
            &lt;stringValues /&gt;
          &lt;/axisDefinition&gt;
        &lt;/logCurveInfo&gt;
        &lt;logData&gt;
          &lt;data /&gt;
        &lt;/logData&gt;
        &lt;commonData&gt;
          &lt;sourceName /&gt;
          &lt;dTimCreation /&gt;
          &lt;dTimLastChange /&gt;
          &lt;itemState /&gt;
          &lt;comments /&gt;
        &lt;/commonData&gt;
        &lt;customData /&gt;
      &lt;/log&gt;
    &lt;/logs&gt;</QueryIn>
          <OptionsIn xsi:type="xsd:string">returnElements=requested</OptionsIn>
        </q1:WMLS_GetFromStore>
      </soap:Body>
    </soap:Envelope>
    """ % (uidWell, uidWellbore)

    response = requests.post(
        url, data=remarks_body, headers=headers, auth=(username, password))

    root = ET.fromstring(response.text)

    xml_content = ET.fromstring(root.find(".//XMLout").text)

    mnemonic = xml_content.findall(
        ".//{http://www.witsml.org/schemas/131}mnemonic")

    data = xml_content.findall(".//{http://www.witsml.org/schemas/131}data")

    header_names = ['rig_time', 'comments']

    witsheader = pd.DataFrame([])

    for i in range(len(data)):
        x = re.split(r',', data[i].text)

        df = pd.DataFrame(x).T
        witsheader = witsheader.append(df)

    witsheader.columns = header_names

    edrraw = witsheader[['rig_time', 'comments']]

    return (edrraw, uidWell, uidWellbore, well_name, rig_name)


def surveys(rig_id):
    url, headers, username, password, uidWell, uidWellbore, well_name, rig_name = connect(
        rig_id)

    survey_body = """
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/" xmlns:tns="http://www.witsml.org/wsdl/120" xmlns:types="http://www.witsml.org/wsdl/120/encodedTypes" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
      <soap:Body soap:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
        <q1:WMLS_GetFromStore xmlns:q1="http://www.witsml.org/message/120">
          <WMLtypeIn xsi:type="xsd:string">trajectory</WMLtypeIn>
          <QueryIn xsi:type="xsd:string">&lt;trajectorys xmlns="http://www.witsml.org/schemas/131" version="1.3.1.1"&gt;
      &lt;trajectory uidWell="%s" uidWellbore="%s" uid="Connect-Surveys"&gt;
        &lt;nameWell /&gt;
        &lt;nameWellbore /&gt;
        &lt;name /&gt;
        &lt;objectGrowing /&gt;
        &lt;parentTrajectory&gt;
          &lt;trajectoryReference uidRef="" /&gt;
          &lt;wellboreParent uidRef="" /&gt;
        &lt;/parentTrajectory&gt;
        &lt;dTimTrajStart /&gt;
        &lt;dTimTrajEnd /&gt;
        &lt;mdMn uom="" datum="" /&gt;
        &lt;mdMx uom="" datum="" /&gt;
        &lt;serviceCompany /&gt;
        &lt;magDeclUsed uom="" /&gt;
        &lt;gridCorUsed uom="" /&gt;
        &lt;aziVertSect uom="" /&gt;
        &lt;dispNsVertSectOrig uom="" /&gt;
        &lt;dispEwVertSectOrig uom="" /&gt;
        &lt;definitive /&gt;
        &lt;memory /&gt;
        &lt;finalTraj /&gt;
        &lt;aziRef /&gt;
        &lt;trajectoryStation uid=""&gt;
          &lt;target uidRef="" /&gt;
          &lt;dTimStn /&gt;
          &lt;typeTrajStation /&gt;
          &lt;typeSurveyTool /&gt;
          &lt;md uom="" datum="" /&gt;
          &lt;tvd uom="" datum="" /&gt;
          &lt;incl uom="" /&gt;
          &lt;azi uom="" /&gt;
          &lt;mtf uom="" /&gt;
          &lt;gtf uom="" /&gt;
          &lt;dispNs uom="" /&gt;
          &lt;dispEw uom="" /&gt;
          &lt;vertSect uom="" /&gt;
          &lt;dls uom="" /&gt;
          &lt;rateTurn uom="" /&gt;
          &lt;rateBuild uom="" /&gt;
          &lt;mdDelta uom="" datum="" /&gt;
          &lt;tvdDelta uom="" datum="" /&gt;
          &lt;modelToolError /&gt;
          &lt;gravTotalUncert uom="" /&gt;
          &lt;dipAngleUncert uom="" /&gt;
          &lt;magTotalUncert uom="" /&gt;
          &lt;gravAccelCorUsed /&gt;
          &lt;magXAxialCorUsed /&gt;
          &lt;sagCorUsed /&gt;
          &lt;magDrlstrCorUsed /&gt;
          &lt;gravTotalFieldReference uom="" /&gt;
          &lt;magTotalFieldReference uom="" /&gt;
          &lt;magDipAngleReference uom="" /&gt;
          &lt;magModelUsed /&gt;
          &lt;magModelValid /&gt;
          &lt;geoModelUsed /&gt;
          &lt;statusTrajStation /&gt;
          &lt;rawData&gt;
            &lt;gravAxialRaw uom="" /&gt;
            &lt;gravTran1Raw uom="" /&gt;
            &lt;gravTran2Raw uom="" /&gt;
            &lt;magAxialRaw uom="" /&gt;
            &lt;magTran1Raw uom="" /&gt;
            &lt;magTran2Raw uom="" /&gt;
          &lt;/rawData&gt;
          &lt;corUsed&gt;
            &lt;gravAxialAccelCor uom="" /&gt;
            &lt;gravTran1AccelCor uom="" /&gt;
            &lt;gravTran2AccelCor uom="" /&gt;
            &lt;magAxialDrlstrCor uom="" /&gt;
            &lt;magTran1DrlstrCor uom="" /&gt;
            &lt;magTran2DrlstrCor uom="" /&gt;
            &lt;sagIncCor uom="" /&gt;
            &lt;sagAziCor uom="" /&gt;
            &lt;stnMagDeclUsed uom="" /&gt;
            &lt;stnGridCorUsed uom="" /&gt;
            &lt;dirSensorOffset uom="" /&gt;
          &lt;/corUsed&gt;
          &lt;valid&gt;
            &lt;magTotalFieldCalc uom="" /&gt;
            &lt;magDipAngleCalc uom="" /&gt;
            &lt;gravTotalFieldCalc uom="" /&gt;
          &lt;/valid&gt;
          &lt;matrixCov&gt;
            &lt;varianceNN uom="" /&gt;
            &lt;varianceNE uom="" /&gt;
            &lt;varianceNVert uom="" /&gt;
            &lt;varianceEE uom="" /&gt;
            &lt;varianceEVert uom="" /&gt;
            &lt;varianceVertVert uom="" /&gt;
            &lt;biasN uom="" /&gt;
            &lt;biasE uom="" /&gt;
            &lt;biasVert uom="" /&gt;
          &lt;/matrixCov&gt;
          &lt;location uid=""&gt;
            &lt;wellCRS uidRef="" /&gt;
            &lt;latitude uom="" /&gt;
            &lt;longitude uom="" /&gt;
            &lt;easting uom="" /&gt;
            &lt;northing uom="" /&gt;
            &lt;westing uom="" /&gt;
            &lt;southing uom="" /&gt;
            &lt;projectedX uom="" /&gt;
            &lt;projectedY uom="" /&gt;
            &lt;localX uom="" /&gt;
            &lt;localY uom="" /&gt;
            &lt;original /&gt;
            &lt;description /&gt;
          &lt;/location&gt;
          &lt;sourceStation&gt;
            &lt;stationReference /&gt;
            &lt;trajectoryParent uidRef="" /&gt;
            &lt;wellboreParent uidRef="" /&gt;
          &lt;/sourceStation&gt;
          &lt;commonData&gt;
            &lt;sourceName /&gt;
            &lt;dTimCreation /&gt;
            &lt;dTimLastChange /&gt;
            &lt;itemState /&gt;
            &lt;comments /&gt;
          &lt;/commonData&gt;
        &lt;/trajectoryStation&gt;
        &lt;commonData&gt;
          &lt;sourceName /&gt;
          &lt;dTimCreation /&gt;
          &lt;dTimLastChange /&gt;
          &lt;itemState /&gt;
          &lt;comments /&gt;
        &lt;/commonData&gt;
        &lt;customData /&gt;
      &lt;/trajectory&gt;
    &lt;/trajectorys&gt;</QueryIn>
          <OptionsIn xsi:type="xsd:string">returnElements=requested</OptionsIn>
        </q1:WMLS_GetFromStore>
      </soap:Body>
    </soap:Envelope>
    """ % (uidWell, uidWellbore)

    response = requests.post(
        url, data=survey_body, headers=headers, auth=(username, password))

    # print(response)
    root = ET.fromstring(response.text)

    xml_content = ET.fromstring(root.find(".//XMLout").text)

    md = xml_content.findall(".//{http://www.witsml.org/schemas/131}md")
    dTimStn = xml_content.findall(".//{http://www.witsml.org/schemas/131}dTimStn")
    tvd = xml_content.findall(".//{http://www.witsml.org/schemas/131}tvd")
    incl = xml_content.findall(".//{http://www.witsml.org/schemas/131}incl")
    azi = xml_content.findall(".//{http://www.witsml.org/schemas/131}azi")
    dispNs = xml_content.findall(
        ".//{http://www.witsml.org/schemas/131}dispNs")
    dispEw = xml_content.findall(
        ".//{http://www.witsml.org/schemas/131}dispEw")
    dls = xml_content.findall(".//{http://www.witsml.org/schemas/131}dls")

    md_content = []
    dTimStn_content = []
    tvd_content = []
    incl_content = []
    azi_content = []
    dispNs_content = []
    dispEw_content = []
    dls_content = []

    for i in range(len(dTimStn)):
        md_content.append(md[i].text)
        dTimStn_content.append(dTimStn[i].text)
        tvd_content.append(tvd[i].text)
        incl_content.append(incl[i].text)
        azi_content.append(azi[i].text)
        dispNs_content.append(dispNs[i].text)
        dispEw_content.append(dispEw[i].text)
        dls_content.append(dls[i].text)

    witsheader = pd.DataFrame([])

    witsheader = witsheader.assign(md=md_content)
    witsheader = witsheader.assign(rig_time=dTimStn_content)
    witsheader = witsheader.assign(tvd=tvd_content)
    witsheader = witsheader.assign(incl=incl_content)
    witsheader = witsheader.assign(azi=azi_content)
    witsheader = witsheader.assign(dispNs=dispNs_content)
    witsheader = witsheader.assign(dispEw=dispEw_content)
    witsheader = witsheader.assign(dls=dls_content)

    return (witsheader, uidWell, uidWellbore, well_name, rig_name)


edrdata(uidWell, date, data_frequency,url,username,password)