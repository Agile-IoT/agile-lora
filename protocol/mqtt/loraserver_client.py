#################################################################
#   Copyright (C) 2018  
#   This program and the accompanying materials are made
#   available under the terms of the Eclipse Public License 2.0
#   which is available at https://www.eclipse.org/legal/epl-2.0/ 
#   SPDX-License-Identifier: EPL-2.0
#   Contributors: ATOS Spain S.A.
################################################################# 

import globals as globals
import components_dictionary as component
import cayenne_parser

import os, sys
import time, datetime, pytz
from queue import Queue
import paho.mqtt.client as mqtt
import threading
import logging
import json
import random

# Testing
import base64

class LoRaServerClient (threading.Thread):
   
   def __init__(self):      
      self._logger = logging.getLogger(globals.BUS_NAME)       
      self._cayenne =   cayenne_parser.CayenneParser()
      self._active_timer = {}      
      self._thread = threading.Thread(target=self.Start, name="LoRaServer_thread")
      # self._thread = threading.Thread(target=self.TestParser, name="LoRaServer_thread")
      self._thread.daemon = True
      self._thread.start()    

   def TestParser(self):            
      
      self._active_timer = threading.Timer(6, self.TestParser)                              
      self._active_timer.start()

      self._mqttc = mqtt.Client() 
      
      raw = {
            "applicationID": "1",
            "applicationName": "my-app",
            "deviceName": "Seeduino",
            "devEUI": "3339343771356214",
            "rxInfo": [
                  {
                        "mac": "0000000000010203",
                        "time": "2018-04-17T09:23:26.441513Z",
                        "rssi": -49,
                        "loRaSNR": 10,
                        "name": "0000000000010203",
                        "latitude": 10,
                        "longitude": 20,
                        "altitude": -1
                  }
            ],
            "txInfo": {
                  "frequency": 868100000,
                  "dataRate": {
                        "modulation": "LORA",
                        "bandwidth": 125,
                        "spreadFactor": 7
                  },
                  "adr": True,
                  "codeRate": "4/5"
            },
            "fCnt": 73,
            "fPort": 8,
            "data": "AmcA7QNoTw=="
      }    
      
      data = {
         "deviceID": raw["deviceName"],
         "hardwareID": raw["devEUI"],            
         "streams": [
         ],
         "connected": False,
         "status": globals.STATUS_TYPE['AVAILABLE'].name         
      } 
      streams = self._cayenne.decodeCayenneLpp(raw["data"], str(raw["rxInfo"][0]["time"]))                 

      # Append data from the message (overhead) - static process
      # i.e., SNR, RSSI, Latitude, Longitude, Altitude
      streams.append ({
         "format": component.dictionary["RSSI"]["format"],
         "subscribed":False,
      #    "value": raw["rxInfo"][0]["rssi"],
         "value": random.uniform(-60,-40),
         "id": "RSSI",
         "unit": component.dictionary["RSSI"]["unit"],
         "lastUpdate": str(raw["rxInfo"][0]["time"])}
      )
      streams.append ({
         "format": component.dictionary["SNR"]["format"],
         "subscribed":False,
      #    "value": raw["rxInfo"][0]["loRaSNR"],
         "value": random.uniform(0,20),
         "id": "SNR",
         "unit": component.dictionary["SNR"]["unit"],
         "lastUpdate": str(raw["rxInfo"][0]["time"])}
      )
      streams.append ({
         "format": component.dictionary["Latitude"]["format"],
         "subscribed":False,
         "value": raw["rxInfo"][0]["latitude"],
         "id": "Latitude",
         "unit": component.dictionary["Latitude"]["unit"],
         "lastUpdate": str(raw["rxInfo"][0]["time"])}
      )
      streams.append ({
         "format": component.dictionary["Longitude"]["format"],
         "subscribed":False,
         "value": raw["rxInfo"][0]["longitude"],
         "id": "Longitude",
         "unit": component.dictionary["Longitude"]["unit"],
         "lastUpdate": str(raw["rxInfo"][0]["time"])}
      )
      streams.append ({
         "format": component.dictionary["Altitude"]["format"],
         "subscribed":False,
         "value": raw["rxInfo"][0]["altitude"],
         "id": "Altitude",
         "unit": component.dictionary["Altitude"]["unit"],
         "lastUpdate": str(raw["rxInfo"][0]["time"])}
      )

      data["streams"] = streams   
      globals.queue.put(data)
      
      self._logger.info("Message received - " + json.dumps(data))          

   def Start(self):
      self._logger.info("LoRaServer client thread instanced")        
      self._mqttc = mqtt.Client()      
           
      # Assign event callbacks
      self._mqttc.on_connect = self.on_connect
      self._mqttc.on_message = self.on_message
      self._mqttc.on_subscribe = self.on_subscribe
      
      self._mqttc.username_pw_set(os.environ.get('LORAWAN_APPID'), os.environ.get('LORAWAN_PSW'))
      self._mqttc.connect(os.environ.get('LORAWAN_MQTT_URL'), int(os.environ.get('LORAWAN_MQTT_PORT')), 60) 


      # and listen to server
      run = True
      while run:
         self._mqttc.loop()

   def on_connect (self, mqttc, mosq, obj, rc):      
      if rc == 0:
         self._logger.info("Connected to MQTT Broker - " + os.environ.get('LORAWAN_MQTT_URL'))
      else:
         self._logger.error("Connection error to MQTT Broker - " + os.environ.get('LORAWAN_MQTT_URL'))        
      
      # subscribe for all devices of user (tailor to every MQTT Broker)
      mqttc.subscribe(os.environ.get('LORAWAN_MQTT_TOPIC'))  

   def on_message (self, mqttc,obj,msg):      
      
      raw = json.loads(msg.payload.decode())                        

      data = {
         "deviceID": raw["deviceName"],
         "hardwareID": raw["devEUI"],                  
         "streams": [
         ],
         "connected": False,
         "status": globals.STATUS_TYPE['AVAILABLE'].name               
      }   

      # Cayenne payload parsing
      streams = self._cayenne.decodeCayenneLpp(raw["data"], str(raw["rxInfo"][0]["time"]))                 
      data["streams"] = streams    

       # Append data from the message (overhead) - static process
      # i.e., SNR, RSSI, Latitude, Longitude, Altitude
      data["streams"].append ({
         "format": component.dictionary["RSSI"]["format"],
         "subscribed": False,
         "value": raw["rxInfo"][0]["rssi"],
         "id": "RSSI",
         "unit": component.dictionary["RSSI"]["unit"],
         "lastUpdate": str(raw["rxInfo"][0]["time"])}
      )
      data["streams"].append ({
         "format": component.dictionary["SNR"]["format"],
         "subscribed": False,
         "value": raw["rxInfo"][0]["loRaSNR"],
         "id": "SNR",
         "unit": component.dictionary["SNR"]["unit"],
         "lastUpdate": str(raw["rxInfo"][0]["time"])}
      )
      data["streams"].append ({
         "format": component.dictionary["Latitude"]["format"],
         "subscribed": False,
         "value": raw["rxInfo"][0]["latitude"],
         "id": "Latitude",
         "unit": component.dictionary["Latitude"]["unit"],
         "lastUpdate": str(raw["rxInfo"][0]["time"])}
      )
      data["streams"].append ({
         "format": component.dictionary["Longitude"]["format"],
         "subscribed": False,
         "value": raw["rxInfo"][0]["longitude"],
         "id": "Longitude",
         "unit": component.dictionary["Longitude"]["unit"],
         "lastUpdate": str(raw["rxInfo"][0]["time"])}
      )
      data["streams"].append ({
         "format": component.dictionary["Altitude"]["format"],
         "subscribed": False,
         "value": raw["rxInfo"][0]["altitude"],
         "id": "Altitude",
         "unit": component.dictionary["Altitude"]["unit"],
         "lastUpdate": str(raw["rxInfo"][0]["time"])}
      )
                    
      globals.queue.put(data)
      self._logger.debug("Message received")          

   def on_publish(self, mosq, obj, mid):
      self._logger.debug("mid: " + str(mid))      

   def on_subscribe(self, mosq, obj, mid, granted_qos):
      self._logger.debug("Subscribed: " + str(mid) + " " + str(granted_qos))      

   def on_log(self, mqttc,obj,level,buf):
      self._logger.debugrint("message:" + str(buf))
      self._logger.debug("userdata:" + str(obj))         

   def TearDown(self):               
      try: 
         if (self._mqttc):
            self._mqttc.unsubscribe(os.environ.get('LORAWAN_MQTT_TOPIC'))
         if (isinstance(self._active_timer, threading.Timer)):
            self._active_timer.cancel()
      except:         
         sys.exit("Error when closing TTN client")