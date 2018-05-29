#! /usr/bin/python3

import globals as globals
import mqtt_conf 
import components_dictionary as component

import time, datetime, pytz, ciso8601
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
      self._thread.daemon = True
      self._thread.start()    

   def Start(self):
      self._logger.info("TTN client thread instanced")        
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
      print("Connected with result code:" + str(rc))
      # subscribe for all devices of user
      mqttc.subscribe('+/devices/+/up')    

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
            data['streams'].append({
                  "id": "SNR",
                  "value": raw['metadata']['gateways'][0]['snr'],
                  "unit": "dB",
                  "format": "float",
                  "subscribed": False,
                  "lastUpdate": raw['metadata']['time']       
            })                                          

            globals.queue.put(data)
            self._logger.info("Message received")     
      else:
            print("Message repeated")     

   def on_publish(self, mosq, obj, mid):
      print("mid: " + str(mid))

   def on_subscribe(self, mosq, obj, mid, granted_qos):
      print("Subscribed: " + str(mid) + " " + str(granted_qos))

   def on_log(self, mqttc,obj,level,buf):
      print("message:" + str(buf))
      print("userdata:" + str(obj))   

   def TearDown(self):               
      if (isinstance(self._active_timer, threading.Timer)):
         self._active_timer.cancel()