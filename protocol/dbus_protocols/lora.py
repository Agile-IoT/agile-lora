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
sys.path.append('../config/')
import globals as globals

from queue import Queue

import dbus
import dbus.service
import logging
import threading
import pydash


# --- Module-specific variables ---------
PROTOCOL_NAME = "LoRa"
DRIVER_NAME = "LoRaLAN"

# --- Classes -----------
class LoRaWAN(dbus.service.Object):   
   def __init__(self):      

      # Generic variables     
      self._logger = logging.getLogger(globals.BUS_NAME)           

      # Properties
      self._protocol_name = PROTOCOL_NAME
      self._driver_name = DRIVER_NAME
      self._discovery_status = globals.DISCOVERY_STATUS['NONE']   
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
      self._bus = dbus.service.BusName(globals.BUS_NAME, dbus.SessionBus(), do_not_queue=True)   

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
         self._discovery_status = globals.DISCOVERY_STATUS['RUNNING'] 
         self.Discovery()           
      else: 
         print("Discovery status already on")   

   ### STOP DISCOVERY
   @dbus.service.method(globals.BUS_NAME, in_signature="", out_signature="")
   def StopDiscovery(self):  
      self._logger.info("Discovery stopped")      
      if (self._discovery_status.name == "RUNNING"):   
         print ("ERTRT")      
         self._task_discovery.cancel()
         self._discovery_status = globals.DISCOVERY_STATUS['NONE']
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
            out.append([dev['hardwareID'], globals.BUS_NAME + ".LoRa", dev['deviceID'], dev['status']])
      
      return out   

   ### CONNECT
   @dbus.service.method(globals.BUS_NAME, in_signature="s", out_signature="s")
   def Connect(self,device_id):    
      hit = pydash.find(self._devices_list, {
            "name": device_id
            })
      if (hit):
            self._logger.info("Device " + device_id + " already connected")      
            return "Device connected"
      else:            
           ProtocolException("LoRa", "Device " + device_id + "not found" )   
           return "Error - Device not found"

   ### DISCONNECT
   @dbus.service.method(globals.BUS_NAME, in_signature="", out_signature="")
   def Disconnect(self):
      self._logger.info("Disconnected")

   ### DATA (return last observation)
   @dbus.service.method(globals.BUS_NAME, in_signature="", out_signature="ays")
   def Data(self):      
      return bytearray([b'\x13\xff\x00\x00\x08\x00', 'adlkjasd'])

   ### DEVICE STATUS
   @dbus.service.method(globals.BUS_NAME, in_signature="s", out_signature="s")
   def DeviceStatus(self, device_id):      
      self._logger.info("DeviceStatus")     
      hit = pydash.find(self._devices_list, {"deviceID": device_id})
      if (hit):
         return hit['status']
      else: 
         return globals.DEVICE_STATUS['ERROR'].name      

   # Need to be fixed (DBUS multi-threading)
   @dbus.service.method(globals.BUS_NAME, in_signature="", out_signature="")
   def NewRecordNotification(self):            
      self.ParseQueue()   

   @dbus.service.method(globals.BUS_NAME, in_signature="a{sv}", out_signature="")
   def Subscribe(self, args):
      print("Subscribed")
      self.Test(args)

   @dbus.service.method(globals.BUS_NAME, in_signature="a{sv}", out_signature="")
   def Unsubscribe(self, args):
      pass

   #SIGNALS
#    @dbus.service.signal(globals.BUS_NAME, signature="(sssssx)")
   @dbus.service.signal(globals.BUS_NAME, signature="ayss")
   def NewRecordSignal(self, id, value, profile):
      pass
      
   @dbus.service.signal(globals.BUS_NAME, signature="(ssss)")   
   def NewDeviceSignal(self, device_description):
      pass

   # Non-DBUS methods (discovery, etc.)
   def Discovery(self):
      self._logger.info("Device Discovery")  
      #Discovery tasks (basically, add new devices)

      self._task_discovery = threading.Timer(5.0, self.Discovery)
      self._task_discovery.start()  

   #Parse MQTT queue
   def ParseQueue(self):                  

      if (not globals.queue.empty()):
         while (not globals.queue.empty()):
            item = globals.queue.get(block=False)
            # print("-----ITEM-----")
            # print(item)            
            # print("----------")
            
            hit = pydash.find(self._devices_list, {"deviceID": item['deviceID']})
            if (hit):
               self._logger.info("Existing item")  
               if (self._discovery_status == globals.DISCOVERY_STATUS['RUNNING']):
                  self.NewDeviceSignal([item['hardwareID'], globals.BUS_NAME + ".LoRa", item['deviceID'], item['status']])          
            
            else: #Update obsevation data
               self._logger.info("New item " + item['deviceID'])  
               self._devices_list.append(item)                    

               if (self._discovery_status == globals.DISCOVERY_STATUS['RUNNING']):
                  self.NewDeviceSignal([item['hardwareID'], globals.BUS_NAME + ".LoRa", item['deviceID'], item['status']])          
      
         # Manage subscriptions
         self.ManageRecord(item)     

         # The last one will be saved as the last record
         self.SaveLastRecordObject(item, item['streams'][-1])
      else:
         pass
      
      # Restart timer
      self._queue_check = threading.Timer(5.0, self.ParseQueue)
      self._queue_check.start()

   def ManageRecord(self, record,): 
      #TBC
      pass

   def SaveLastRecordObject(self, record, component):
      self._last_record = {
         "deviceID": record['hardwareID'],
         "componentID": component['id'],
         "value": component['value'],
         "unit": component['unit'],
         "format": component['format'],
         "lastUpdate": record['lastUpdateTs']
      }      
      # print(list(self._last_record.values()))
      #Signal test
      print (bytes([0x13, 0x00, 0x00, 0x00, 0x08, 0x00]))
      # print (b'\x13\0\0\0\x08\0')
      self.NewRecordSignal(bytes([0x1, 0x02]), self._last_record['deviceID'], 'ss' )

   def SendRecord(self, record):
      pass

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