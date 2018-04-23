#! /usr/bin/python3

#################################################################
#   Copyright (C) 2018  
#   This program and the accompanying materials are made
#   available under the terms of the Eclipse Public License 2.0
#   which is available at https://www.eclipse.org/legal/epl-2.0/ 
#   SPDX-License-Identifier: EPL-2.0
#   Contributors: ATOS
################################################################# 

import os
import sys
sys.path.append('../config/')
import globals as globals
import mqtt_conf 
import components_dictionary as component

import time, datetime, pytz, ciso8601
from queue import Queue
import paho.mqtt.client as mqtt
import threading
import logging
import random
import json
import base64
from pydash import py_
import dbus
import dbus.service
import dbus.exceptions

#There is some kind of issue with this dbus instance on a different thread than the original one
class RecordNotifier(dbus.service.Object):
    def __init(self):
        try:
            self._dbus_interface = dbus.Interface (dbus.SessionBus().get_object(globals.BUS_NAME, globals.BUS_PATH + '/LoRa' ), 
             "org.eclipse.agail.protocol")  
            super().__init__(dbus.SessionBus(), globals.BUS_PATH + "/LoRa")
            self._dbus = dbus.service.BusName(globals.BUS_NAME, dbus.SessionBus(), do_not_queue=True) 
        except dbus.exceptions.NameExistsException:
            print("service is already running")
            sys.exit(1)

    def Send(self):
        print(self._dbus.Name()) 

class MqttClient(threading.Thread):
    def __init__(self):                        
        self._logger = logging.getLogger(globals.BUS_NAME)           
        self._dbus = RecordNotifier()

        # Temporal solution
        self._task_data = {}        

        # MQTT Connection
        # self._thread = threading.Thread(target=self.TtnConnect, name="MQTT_thread")
        # Dummy data
        self._thread = threading.Thread(target=self.SendDummyData, name="Dummy_thread")
        self._thread.daemon = True
        self._thread.start()     

    def TtnConnect(self):

        self._logger.info("MQTT thread instanced")        
        mqttc = mqtt.Client()
        # Assign event callbacks
        mqttc.on_connect = self.on_connect
        mqttc.on_message = self.on_message
        mqttc.on_subscribe = self.on_subscribe

        mqttc.username_pw_set(mqtt_conf.APPID, mqtt_conf.PSW)
        mqttc.connect(mqtt_conf.URL, 1883, 60)        

        # and listen to server
        run = True
        while run:
            mqttc.loop()
    
    def SendDummyData(self):              

        print(datetime.datetime.now(), "Dummy data sent")
        self._task_data = threading.Timer(10.0, self.SendDummyData)                              
        self._task_data.start()

        last_record = {  
            "hardwareID":"3339343771356214",
            "status":   "AVAILABLE",
            "deviceID":"lora_n_003",            
            "streams":[  
                {  
                    "subscribed":False,
                    "id":"Temperature",
                    "value": str(random.uniform(0.0, 30.0)),
                    "format":"float",
                    "unit":"Degree celsius (°C)",
                    "lastUpdate": datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(),                    
                },
                {  
                    "subscribed":False,
                    "id":"Digital_In",
                    "value": str(random.uniform(0.0, 100.0)),
                    "format":"float",
                    "unit":"%",
                    "lastUpdate": datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()                    
                },
                {  
                    "subscribed":False,
                    "id":"Relative_Humidity",
                    "value": str(random.uniform(0.0, 30.0)),
                    "format":"float",
                    "unit":"%",
                    "lastUpdate": datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
                },
                {  
                    "subscribed":False,
                    "id":"Digital_Out",
                    "value": str(random.uniform(0.0, 30.0)),
                    "format":"float",
                    "unit":"%",
                    "lastUpdate": datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()                    
                },
                {  
                    "subscribed":False,
                    "id":"Barometric_Pressure",
                    "value":  str(random.uniform(0.0, 500.0)),
                    "format":"float",
                    "unit":"Pascals",
                    "lastUpdate": datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
                },
                {  
                    "subscribed":False,
                    "id":"SNR",
                    "value":  str(random.uniform(0.0, 70.0)),
                    "format":"float",
                    "unit":"dB",
                    "lastUpdate": datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()                    
                }
            ]            
        }             
        
        #Temporal notification -- invoke a DBUS method
        globals.queue.put(last_record)    

    def on_connect (self, mqttc, mosq, obj, rc):
       print("Connected with result code:" + str(rc))
       # subscribe for all devices of user
       mqttc.subscribe('+/devices/+/up')    

    def on_message (self, mqttc,obj,msg):
        
        raw = json.loads(msg.payload.decode())                        

        data = {
            "deviceID": raw["dev_id"],
            "hardwareID": raw["hardware_serial"],                        
            "streams": [],
            "connected": False,
            "status": globals.STATUS_TYPE['AVAILABLE'].name
        }    

        # Parse the payload field 
        for key in raw['payload_fields']:  
            temp = {
                "id": "",
                "value": str(raw['payload_fields'][key]),
                "unit": "",
                "format": "",
                "subscribed": False,
                "lastUpdate": raw['metadata']['time'],
                }
            aux = key.split("_")
            temp['id'] = '_'.join(aux[0:len(aux)-1]).title()
            
            #Asserts needed here
            temp['unit']= component.dictionary[temp['id']]['unit']
            temp['format']= component.dictionary[temp['id']]['format']        
            data['streams'].append(temp)    
            
        # More data that can be parsed 
        data['streams'].append({
                "id": "SNR",
                "value": raw['metadata']['gateways'][0]['snr'],
                "unit": "dB",
                "format": "float",
                "subscribed": False            
            }
        )                                                           

        globals.queue.put(data)
        self._logger.info("Message received")          

    def on_publish(self, mosq, obj, mid):
        print("mid: " + str(mid))

    def on_subscribe(self, mosq, obj, mid, granted_qos):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    def on_log(self, mqttc,obj,level,buf):
        print("message:" + str(buf))
        print("userdata:" + str(obj))

    def TearDown(self):      
       
       if (isinstance(self._task_data, threading.Timer)):
          self._task_data.cancel()
