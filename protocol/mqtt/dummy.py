#! /usr/bin/python3

import globals as globals
import sys
sys.path.append('utils/')
# import components_dictionary as component
import time, datetime, pytz, ciso8601
from queue import Queue
import struct
import threading
import logging
import random
import json
import base64
from pydash import py_

class DummyListener (threading.Thread):
   
   def __init__(self):            
      self._logger = logging.getLogger(globals.BUS_NAME)       
      self._active_timer = {}      
      self._thread = threading.Thread(target=self.SendDummyData, name="Dummy_thread")
      self._thread.daemon = True
      self._thread.start() 

   def SendDummyData(self):                   
      
      self._active_timer = threading.Timer(1.0, self.SendDummyData)                              
      self._active_timer.start()

      last_record = {  
         "hardwareID": str(random.randint(1,10)),
         "status":   "AVAILABLE",
         # "componentID":"Temperature",
         # "connected":False,
         "deviceID":"lora_n_003",
         # "lastUpdate":"2018-03-29T08:11:49.061595272Z",
         # "lastUpdateTs": int(time.mktime(ciso8601.parse_datetime("2018-03-29T08:11:49.061595272Z").timetuple()))
         "streams":[  
               {  
                  "subscribed":False,
                  "id":"Temperature",
                  "value": str(random.uniform(0.0, 30.0)),
                  "format":"float",
                  "unit":"Degree celsius (°C)",
                  "lastUpdate": datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(),
                  # "lastUpdateTs": int(time.mktime(ciso8601.parse_datetime("2018-03-29T08:11:49.061595272Z").timetuple()))
               },
               {  
                  "subscribed":False,
                  "id":"Digital_In",
                  "value": str(random.uniform(0.0, 100.0)),
                  "format":"float",
                  "unit":"%",
                  "lastUpdate": datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(),
                  # "lastUpdateTs": int(time.mktime(ciso8601.parse_datetime("2018-03-29T08:11:49.061595272Z").timetuple()))
               },
               {  
                  "subscribed":False,
                  "id":"Relative_Humidity",
                  "value": str(random.uniform(0.0, 30.0)),
                  "format":"float",
                  "unit":"%",
                  "lastUpdate": datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(),
                  # "lastUpdateTs": int(time.mktime(ciso8601.parse_datetime("2018-03-29T08:11:49.061595272Z").timetuple()))
               },
               {  
                  "subscribed":False,
                  "id":"Digital_Out",
                  "value": str(random.uniform(0.0, 30.0)),
                  "format":"float",
                  "unit":"%",
                  "lastUpdate": datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(),
                  # "lastUpdateTs": int(time.mktime(ciso8601.parse_datetime("2018-03-29T08:11:49.061595272Z").timetuple()))
               },
               {  
                  "subscribed":False,
                  "id":"Barometric_Pressure",
                  "value":  str(random.uniform(0.0, 500.0)),
                  "format":"float",
                  "unit":"Pascals",
                  "lastUpdate": datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(),
                  # "lastUpdateTs": int(time.mktime(ciso8601.parse_datetime("2018-03-29T08:11:49.061595272Z").timetuple()))
               },
               {  
                  "subscribed":False,
                  "id":"SNR",
                  "value":  str(random.uniform(0.0, 70.0)),
                  "format":"float",
                  "unit":"dB",
                  "lastUpdate": datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(),
                  # "lastUpdateTs": int(time.mktime(ciso8601.parse_datetime("2018-03-29T08:11:49.061595272Z").timetuple()))
               }
         ]            
      }       

      # #BASE 64 handling (for Cayenne payload)
      # print("-----")
      # c = base64.b64decode("AmcA7QNoTw==")

      # print (c.hex())
      
      # out = struct.unpack_from('HHH', c, 0)
      # print (out)

      # for b in c:
      #    # print (hex(b))
      #    print(b)
         
      # print("-----")
      # print (c[5])
        
        #Temporal notification -- invoke a DBUS method
      globals.queue.put(last_record)    

   def TearDown(self):               
      if (isinstance(self._active_timer, threading.Timer)):
         self._active_timer.cancel()