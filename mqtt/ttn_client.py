#################################################################
#   Copyright (C) 2018  
#   This program and the accompanying materials are made
#   available under the terms of the Eclipse Public License 2.0
#   which is available at https://www.eclipse.org/legal/epl-2.0/ 
#   SPDX-License-Identifier: EPL-2.0
#   Contributors: ATOS SPAIN S.A.
################################################################# 

import globals as globals
import components_dictionary as component

import os, sys
import time, datetime, pytz
from queue import Queue
import paho.mqtt.client as mqtt
import threading
import logging
import json

class TtnClient (threading.Thread):
   
   def __init__(self):      
      
      self._logger = logging.getLogger(globals.BUS_NAME)         

      self._active_timer = {}      
      self._thread = threading.Thread(target=self.Start, name="Ttn_thread")

      self.ttn_topic = '+/devices/+/up'
      self._thread.daemon = True
      self._thread.start()    

   def Start(self):
      self._logger.info("TTN client thread instanced")        
      self._mqttc = mqtt.Client()      
      
      # Assign event callbacks
      self._mqttc.on_connect = self.on_connect
      self._mqttc.on_message = self.on_message
      self._mqttc.on_subscribe = self.on_subscribe      

      self._mqttc.username_pw_set(os.environ.get('LORAWAN_APPID'), os.environ.get('LORAWAN_PSW'))      
      self._mqttc.connect(os.environ.get('LORAWAN_MQTT_URL'), \
            int(1883 if not(os.environ.get('LORAWAN_MQTT_PORT')) else os.environ.get('LORAWAN_MQTT_PORT')), 60)            

      # and listen to server
      run = True
      while run:
         self._mqttc.loop()

   def on_connect (self, mqttc, mosq, obj, rc):      
      if rc == 0:
         self._logger.info("Connected to MQTT Broker - " + os.environ.get('LORAWAN_MQTT_URL'))
      else:
         self._logger.error("Connection error to MQTT Broker - " + os.environ.get('LORAWAN_MQTT_URL'))

      # subscribe for all devices of user
      mqttc.subscribe(self.ttn_topic)    

   def on_message (self, mqttc,obj,msg):       
      raw = json.loads(msg.payload.decode())    
      if (raw['payload_raw'] != None):
            data = {
                  "deviceID": raw["dev_id"],
                  "hardwareID": raw["hardware_serial"],            
                  "streams": [
                  ],
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
                        "lastUpdate": raw['metadata']['time']
                        }
                  aux = key.split("_")
                  temp['id'] = '_'.join(aux[0:len(aux)-1]).title()
                  
                  #Asserts needed here
                  temp['unit']= component.dictionary[temp['id']]['unit']
                  temp['format']= component.dictionary[temp['id']]['format']        
                  data['streams'].append(temp)    
            
            # More data that can be parsed 
            if "snr" in raw['metadata']['gateways'][0]:                  
                  data['streams'].append({
                        "id": "SNR",
                        "value": raw['metadata']['gateways'][0]['snr'],
                        "unit": "dB",
                        "format": "float",
                        "subscribed": False,
                        "lastUpdate": str(raw['metadata']['time'])})           
            if "rssi" in raw['metadata']['gateways'][0]:          
                  data['streams'].append ({
                        "format": component.dictionary["RSSI"]["format"],
                        "subscribed": False,
                        "value": raw['metadata']['gateways'][0]['rssi'],
                        "id": "RSSI",
                        "unit": component.dictionary["RSSI"]["unit"],
                        "lastUpdate": str(raw['metadata']['time'])}) 
            if "latitude" in raw['metadata']['gateways'][0]:
                  data['streams'].append ({
                        "format": component.dictionary["Latitude"]["format"],
                        "subscribed":False,
                        "value": raw['metadata']['gateways'][0]["latitude"],
                        "id": "Latitude",
                        "unit": component.dictionary["Latitude"]["unit"],
                        "lastUpdate": str(raw['metadata']['time'])}) 
            if "longitude" in raw['metadata']['gateways'][0]:
                  data['streams'].append ({
                        "format": component.dictionary["Longitude"]["format"],
                        "subscribed":False,
                        "value": raw['metadata']['gateways'][0]["longitude"],
                        "id": "Longitude",
                        "unit": component.dictionary["Longitude"]["unit"],
                        "lastUpdate": str(raw['metadata']['time'])}) 
            if "altitude" in raw['metadata']['gateways'][0]:
                  data['streams'].append ({
                        "format": component.dictionary["Altitude"]["format"],
                        "subscribed":False,
                        "value": raw['metadata']['gateways'][0]["altitude"],
                        "id": "Altitude",
                        "unit": component.dictionary["Altitude"]["unit"],
                        "lastUpdate": str(raw['metadata']['time'])}) 

            self._logger.debug("Message received - " + data['hardwareID'])   
            globals.queue.put(data)
                      

   def on_publish(self, mosq, obj, mid):      
      self._logger.info("mid: " + str(mid))          

   def on_subscribe(self, mosq, obj, mid, granted_qos):      
      self._logger.info("Subscribed to topic " + self.ttn_topic)          


   def on_unsubscribe(self, client, userdata, mid):      
      self._logger.info("UnSubscribed: " + str(client) + " " + str(granted_qos))                  

   def on_log(self, mqttc,obj,level,buf):
      self._logger.info("message:" + str(buf))          
      self._logger.info("userdata:" + str(obj))           

   def TearDown(self):  
      try: 
         if (self._mqttc):
            self._mqttc.unsubscribe(self.ttn_topic)
         if (isinstance(self._active_timer, threading.Timer)):
            self._active_timer.cancel()
      except:         
         sys.exit("Error on closing TTN client")