#!/usr/local/bin/python3.6

import datetime
import time
import os
import sys
import json
import requests
from configparser import ConfigParser

#https://az-doh-airqual-registerdevice.azurewebsites.net/api/Register?code=ZiaXVqHCrU6aKwA1ixphiH0Blq8z5U6xTOYII8hEaHD6LG1/sJaMfA==&query=4
cfgfile = 'AzHubReader.ini'

class SiteMonitor:    
    def __init__(self,SiteMonitor_Id, Monitor_Id, Site_Id, Deployment_BeginDate, Deployment_EndDate, DeployedBy, Deployment_Notes, Sensor_station_id, IPAddress, IsEnabledForSync):
        self.SiteMonitor_Id =  SiteMonitor_Id
        self.Monitor_Id =  Monitor_Id
        self.Site_Id =  Site_Id
        self.Deployment_BeginDate =  Deployment_BeginDate
        self.Deployment_EndDate =  Deployment_EndDate
        self.DeployedBy =  DeployedBy
        self.Deployment_Notes =  Deployment_Notes
        self.Sensor_station_id =  Sensor_station_id
        self.IPAddress =  IPAddress
        self.IsEnabledForSync = IsEnabledForSync

def jsondata( j):
    device = SiteMonitor(j[0]['SiteMonitor_Id'],  \
                         j[0]['Monitor_Id'],  \
                         j[0]['Site_Id'],  \
                         j[0]['Deployment_BeginDate'],  \
                         j[0]['Deployment_EndDate'],  \
                         j[0]['DeployedBy'],  \
                         j[0]['Deployment_Notes'],  \
                         j[0]['Sensor_station_id'],  \
                         j[0]['IPAddress'],  \
                         j[0]['IsEnabledForSync'])
    return device

def openini():
    config = ConfigParser()
    config.read(cfgfile)
    locationid = config.get('location', 'locationid')
    hostid = config.get('host', 'hostid')
    deviceid = config.get('device', 'deviceid')
    return ( locationid, hostid, deviceid )
    
def register( device, locationid, hostid):
   r = device
   config = ConfigParser()
   config.read('AzHubReader.ini')
   config['Registration'] = {'SiteMonitor_Id' : r.SiteMonitor_Id,  \
       'Monitor_Id' :  r.Monitor_Id,  \
       'Site_Id' :  r.Site_Id,  \
       'Deployment_BeginDate' :  r.Deployment_BeginDate, \
       'Deployment_EndDate' :  r.Deployment_EndDate, \
       'DeployedBy' :  r.DeployedBy,  \
       'Deployment_Notes' :  r.Deployment_Notes,  \
       'Sensor_station_id' :  r.Sensor_station_id,  \
       'IPAddress' :  r.IPAddress,  \
       'IsEnabledForSync' :  r.IsEnabledForSync }
   sensorid = r.Sensor_station_id
   loc = sensorid.split('-')
   locid = loc[2]
   config['location'] = { 'locationid' : locid }
   with open(cfgfile, 'w') as configfile:
       config.write(configfile)

def httprequest(devid):
    apiuri = 'https://doh-airqual-registerdevice-api.azurewebsites.net/api/Register?'
    apikey = 'code=msVsIgP1UZW7Hg1gWvBy8MhA7q7KRI4cEl1ERaoeCzEYWPos1rsJpw=='
    apiGET = apiuri + apikey
    return requests.get(apiGET, params=devid)

def main():
    hosttpl = openini()
    locationid, hostid, deviceid = hosttpl
    devid = {'query': deviceid}
    resp = httprequest(devid)
    j = json.loads(resp.content.decode('utf-8'))
    sitemonitordata = jsondata(j)
    register(sitemonitordata, locationid, hostid)

if __name__ == "__main__":
    main()

