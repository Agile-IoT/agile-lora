#################################################################
#   Copyright (C) 2018  
#   This program and the accompanying materials are made
#   available under the terms of the Eclipse Public License 2.0
#   which is available at https://www.eclipse.org/legal/epl-2.0/ 
#   SPDX-License-Identifier: EPL-2.0
#   Contributors: ATOS Spain S.A.
################################################################# 

import globals as globals
import mqtt_conf 
import components_dictionary as component
import cayenne_parser

import time, datetime, pytz
from queue import Queue
import paho.mqtt.client as mqtt
import mqtt_conf 
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
      # self._thread = threading.Thread(target=self.Start, name="LoRaServer_thread")
      self._thread = threading.Thread(target=self.TestParser, name="LoRaServer_thread")
      self._thread.daemon = True
      self._thread.start()    

   def TestParser(self):             
      
      self._active_timer = threading.Timer(6, self.TestParser)                              
      self._active_timer.start()
      
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

   def on_connect (self, mqttc, mosq, obj, rc):      
      self._logger.info("Connected with result code:" + str(rc))          
      
      # subscribe for all devices of user (tailor to every MQTT Broker)
      mqttc.subscribe('+/devices/+/up')    

   def on_message (self, mqttc,obj,msg):      
      
      raw = json.loads(msg.payload.decode())                        

      data = {
         "deviceID": raw["dev_id"],
         "hardwareID": raw["hardware_serial"],                     
         "streams": [
         ],
         "connected": False,
         "status": globals.STATUS_TYPE['AVAILABLE'].name               
      }   

      if mqtt_conf.PAYLOAD == "clear":
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

            
      elif mqtt_conf.PAYLOAD == "base64":            
            streams = self._cayenne.decodeCayenneLpp(raw["data"], str(raw["rxInfo"][0]["time"]))                 
            data["streams"] = streams 
      else:    
            raise ValueError('Payload type ' + mqtt_conf.PAYLOAD + ' not valid')

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
      if (isinstance(self._active_timer, threading.Timer)):
         self._active_timer.cancel()