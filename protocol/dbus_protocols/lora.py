#################################################################
#   Copyright (C) 2018  
#   This program and the accompanying materials are made
#   available under the terms of the Eclipse Public License 2.0
#   which is available at https://www.eclipse.org/legal/epl-2.0/ 
#   SPDX-License-Identifier: EPL-2.0
#   Contributors: ATOS
################################################################# 

# --- Imports -----------
import sys

# sys.path.append("../config/")
import globals as globals

import dbus
import dbus.service
import logging
import threading
import pydash
import struct 
import time, datetime, ciso8601
from queue import Queue

# --- Module-specific variables ---------
PROTOCOL_NAME = "LoRa"
DRIVER_NAME = "LoRa"

# --- Classes -----------
class LoRaWAN(dbus.service.Object):   
   def __init__(self):      

      # Generic variables     
      self._logger = logging.getLogger(globals.BUS_NAME)           

      # Properties
      self._protocol_name = PROTOCOL_NAME
      self._driver_name = DRIVER_NAME
      self._discovery_status = globals.DISCOVERY_STATUS["NONE"]   
      self._devices_list = []
      self._subscribed_devices = []
      self._last_record = {}   

      # Thread init                        
      self._thread = threading.Thread(target=self.startDbus, name="DBUS_thread")
      self._thread.start()
      self._thread_id = str(self._thread.ident)    

      # Timers and tasks
      self._task_discovery = {}
      # Until we do not solve the DBUS multithreading issue, we will periodically poll the queue in order       
      self._queue_check = threading.Timer(1.0, self.ParseQueue)
      self._queue_check.start()    

   def startDbus(self):                  
      self._logger.info("LoRa protocol instanced") 
      # Bus init
      super().__init__(dbus.SessionBus(), globals.BUS_PATH + "/" +  self._protocol_name)
      self._bus = dbus.service.BusName(globals.BUS_NAME + "." +  self._protocol_name, dbus.SessionBus(), do_not_queue=True)   

   # Override DBus object methods     
   ### GENERIC METHODS      
   @dbus.service.method(globals.BUS_NAME, in_signature="", out_signature="s")
   def Status(self):            
      return ""

   @dbus.service.method(globals.BUS_NAME, in_signature="", out_signature="s")
   def Name(self):    
      return self._protocol_name

   ### DRIVER
   @dbus.service.method(globals.BUS_NAME, in_signature="", out_signature="s")
   def Driver(self):      
      return self._driver_name

   ### START DISCOVERY
   @dbus.service.method(globals.BUS_NAME, in_signature="", out_signature="")
   def StartDiscovery(self):      
      
      if (self._discovery_status.name == "NONE"):
         print("Discovery status ON")
         self._discovery_status = globals.DISCOVERY_STATUS["RUNNING"] 
         self.Discovery()           
      else: 
         print("Discovery status already on")   

   ### STOP DISCOVERY
   @dbus.service.method(globals.BUS_NAME, in_signature="", out_signature="")
   def StopDiscovery(self):  
      self._logger.info("Discovery stopped")      
      if (self._discovery_status.name == "RUNNING"):         
         self._task_discovery.cancel()
         self._discovery_status = globals.DISCOVERY_STATUS["NONE"]
      else:
          self._logger.info("Discovery already off")      

   ### DISCOVERY STATUS
   @dbus.service.method(globals.BUS_NAME, in_signature="", out_signature="s")
   def DiscoveryStatus(self):          
      self._logger.info("Discovery status " + self._discovery_status.name)
      return self._discovery_status.name

   #Returns list discovered protocol devicesdevices
   @dbus.service.method(globals.BUS_NAME, in_signature="", out_signature="a(ssss)")
   def Devices(self):            
      out = []
      if len(self._devices_list):       
         for dev in self._devices_list:
            out.append([dev["hardwareID"], globals.BUS_NAME + ".LoRa", dev["deviceID"], dev["status"]])
      
      return out   

   ### CONNECT
   @dbus.service.method(globals.BUS_NAME, in_signature="s", out_signature="")
   def Connect(self,device_id):    
      hit = pydash.find(self._devices_list, {
            "hardwareID": device_id
            })
      if (hit):
            if (hit["connected"] == False):
               self._logger.info("Device " + device_id + " CONNECTED")
               hit["connected"] = True                  
      else:            
           ProtocolException("CONNECT", "Device " + device_id + "not found" )              

   ### DISCONNECT
   @dbus.service.method(globals.BUS_NAME, in_signature="s", out_signature="")
   def Disconnect(self, device_id):
      hit = pydash.find(self._devices_list, {
            "hardwareID": device_id
            })
      if (hit):
            if (hit["connected"] == True):
               self._logger.info("Device " + device_id + " DISCONNECTED")
               hit["connected"] = False                              
      else:            
           ProtocolException("DISCONNECT", "Device " + device_id + "not found" ) 
      

   ### READ (return last observation of a particular sensor)
   @dbus.service.method(globals.BUS_NAME, in_signature="sa{ss}", out_signature="ay")
   def Read(self, device_id, profile):

      hit_1 = pydash.find(self._devices_list, {"hardwareID": device_id})
      if (hit_1 != None):
            hit_2 = pydash.find(hit_1["streams"], {"id": profile["id"]})
            if (hit_2 != None):
                  return self.SerializeValue(hit_2["format"], hit_2["value"])
            else:
                  ProtocolException("Component not found (subscription to device ID) " + device_id)   
                  return bytearray([])
      else:
            ProtocolException("Component not found (subscription to device ID) " + device_id)   
            return bytearray([])

   ### WRITE (return last observation)
   @dbus.service.method(globals.BUS_NAME, in_signature="sa{ss}ay", out_signature="")
   def Write(self, device_id, profile, payload):
      pass

   ### DATA (return last observation)
   @dbus.service.method(globals.BUS_NAME, in_signature="", out_signature="ay")
   def Data(self): 
      return self.GetLastRecordValue()

   ### DEVICE STATUS
   @dbus.service.method(globals.BUS_NAME, in_signature="s", out_signature="s")
   def DeviceStatus(self, device_id):             
      hit = pydash.find(self._devices_list, {"hardwareID": device_id})
      if (hit):
         return hit["status"]
      else: 
         return globals.DEVICE_STATUS["ERROR"].name      

   # Need to be fixed (DBUS multi-threading)
   @dbus.service.method(globals.BUS_NAME, in_signature="", out_signature="")
   def NewRecordNotification(self):            
      self.ParseQueue()   

   @dbus.service.method(globals.BUS_NAME, in_signature="sa{ss}", out_signature="")
   def Subscribe(self, device_id, profile):
      hit_1 = pydash.find(self._devices_list, {"hardwareID": device_id})
      if (hit_1 != None):
            print("FSDF")
            hit_2 = pydash.find(hit_1["streams"], {"id": profile["id"]})
            if (hit_2 != None):
                  hit_2["subscribed"] = True        
                  self._logger.info("Subscribed to " + device_id)  
            else:                  
                  ProtocolException("Component " + profile['id']+ " not found (subscription to device ID) " + device_id)                     
      else:
            ProtocolException("Component not found (subscription to device ID) " + device_id)                 

   @dbus.service.method(globals.BUS_NAME, in_signature="sa{ss}", out_signature="")
   def Unsubscribe(self, device_id, profile):
      hit_1 = pydash.find(self._devices_list, {"hardwareID": device_id})
      if (hit_1 != None):
            hit_2 = pydash.find(hit_1["streams"], {"id": profile["id"]})
            if (hit_2 != None):
                  hit_2["subscribed"] = False      
            else:
                  ProtocolException("Component not found (subscription to device ID) " + device_id)   
      else:
            ProtocolException("Component not found (subscription to device ID) " + device_id)   

   #SIGNALS
   @dbus.service.signal(globals.NEW_RECORD_SIGNAL_NAME, signature="aysa{ss}")   
   def NewRecordSignal(self, value, id, profile):
      pass
      
   @dbus.service.signal(globals.NEW_DEVICE_SIGNAL_NAME, signature="(ssss)")   
   def NewDeviceSignal(self, device_description):
      pass

   ###### Non-DBUS methods (discovery, etc.) ######
   def Discovery(self):
      self._logger.info("Device discovery")  
      
      #Discovery tasks - First version -> Discover all devices
      if (self._discovery_status == globals.DISCOVERY_STATUS["RUNNING"]):           
            for item in self._devices_list:            
                  self.NewDeviceSignal([item["hardwareID"], globals.BUS_NAME + ".LoRa", item["deviceID"], item["status"]])      

      self._task_discovery = threading.Timer(5.0, self.Discovery)
      self._task_discovery.start()  
   
   def ParseQueue(self):                  

      if (not globals.queue.empty()):
         while (not globals.queue.empty()):
            item = globals.queue.get(block=False)
            # print ("----- Received item -----")
            # print(item)            
            
            hit = pydash.find(self._devices_list, {"hardwareID": item["hardwareID"]})
            if (hit):
               self._logger.info("Existing item")  
               # Update obsevation data
               for i in item["streams"]:
                     hit_phenomenon = pydash.find (hit["streams"], {"id": i["id"]})
                     if (hit_phenomenon):      #Update values                       
                              hit_phenomenon["value"] = i["value"]
                              hit_phenomenon["lastUpdate"] = i["lastUpdate"]                              
                           
                     else:    # New phenomenon
                           hit["streams"].append({
                                 "id": i["id"],
                                 "value": i["value"],
                                 "unit": i["unit"],
                                 "lastUpdate": i["lastUpdate"],
                                 "format": i["format"],
                                 "subscribed": False
                           })
                     # Record signal handler
                     self.ManageRecordSignal(item["hardwareID"], i)
            
            else: 
               self._logger.info("New item - lora" + item["hardwareID"])  
               # Default option - connected = False
               item["connected"] = False
               self._devices_list.append(item)                    
               for i in item["streams"]:
                     self.ManageRecordSignal(item["hardwareID"], i)         

         # The last one will be saved as the last record
         self.SaveLastRecordObject(item, item["streams"][-1])
      else:
         pass
      
      # Restart timer
      self._queue_check = threading.Timer(5.0, self.ParseQueue)
      self._queue_check.start()

   def ManageRecordSignal(self, id, item):   
      hit_1 = pydash.find(self._devices_list, {"hardwareID": id})
      if (hit_1 != None):
            hit_2 = pydash.find(hit_1["streams"], {"id": item["id"]})
            if (hit_2 != None):      
                  if (hit_2["subscribed"] == True):  # Change to True after testing                           
                        value = self.SerializeValue(item["format"], item["value"])
                        self.NewRecordSignal(value, id, {"id": item["id"]})

   def SaveLastRecordObject(self, record, component):

      self._last_record = {
         "deviceID": record["hardwareID"],
         "componentID": component["id"],
         "value": component["value"],
         "unit": component["unit"],
         "format": component["format"],
         "lastUpdate": component["lastUpdate"]
      }      

   def SerializeValue(self, value_type, value):
      if (value_type == "integer"):
            output = bytearray((value).to_bytes(4, "big"))            
      elif (value_type == "float"):            
            output = bytearray(struct.pack("f", float(value))) 
      elif (value_type == "string"):
            output = value.encode()
      else:
            ProtocolException("Format value not compatible (choose between integer, float or string")   
      
      return output

   def GetLastRecordValue(self):     

      if (len(self._last_record)):    
            if (self._last_record["format"] == "integer"):
                  output = bytearray((self._last_record["value"]).to_bytes(4, "big"))            
            elif (self._last_record["format"] == "float"):            
                  output = bytearray(struct.pack("f", float(self._last_record["value"]))) 
            elif (self._last_record["format"] == "string"):
                  output = self._last_record["value"].encode()
            elif (self._last_record["format"] == "boolean"):
                  output = bytearray(struct.pack("?", bool(self._last_record["value"]))) 
            else:
                  ProtocolException("Format value not compatible (choose between integer, float or string")         
            return output
      else:
            output = bytearray([])
      return output

   def TearDown(self):
      if (isinstance(self._task_discovery, threading.Timer)):
          self._task_discovery.cancel()
      if (isinstance(self._queue_check, threading.Timer)):
          self._queue_check.cancel()
          
class ProtocolException(dbus.DBusException):

   def __init__(self, protocol_name, msg=""):
      if msg == "":         
         super().__init__("Exception")
      else:
         super().__init__(msg)
      self._dbus_error_name = globals.BUS_NAME + "." + protocol_name  