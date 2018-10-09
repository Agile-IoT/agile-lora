#################################################################
#   Copyright (C) 2018
#   This program and the accompanying materials are made
#   available under the terms of the Eclipse Public License 2.0
#   which is available at https://www.eclipse.org/legal/epl-2.0/
#   SPDX-License-Identifier: EPL-2.0
#   Contributors: ATOS SPAIN S.A.
#################################################################

# --- Imports -----------
import os
import sys
import globals as globals
import json
import threading

from queue import Queue
import dbus
import dbus.service
import logging
import threading
import pydash
import struct
import time, datetime
import requests


# --- Module-specific variables ---------
PROTOCOL_NAME = "LoRa"
DRIVER_NAME = "LoRa"

OPATH = "/org/eclipse/agail/protocol/LoRa"
IFACE = "org.eclipse.agail.Protocol"
BUS_NAME = "org.eclipse.agail.protocol.LoRa"


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

      self._AGILE_API_BASE = os.getenv('AGILE_API_BASE','agile')
      print("AGILE_API_BASE = " + self._AGILE_API_BASE)

      # Thread init
      self._thread = threading.Thread(target=self.startDbus, name="DBUS_thread")
      self._thread.start()
      self._thread_id = str(self._thread.ident)

      # Protocol Manager
      self._protocol_manager = ProtocolManager()
      self._thread_pm = threading.Thread(target=self._protocol_manager.startDbus, name="DBUS_thread")
      self._thread_pm.start()
      self._thread_pm_id = str(self._thread.ident)

      # Timers and tasks
      self._task_discovery = {}
      # Until we do not solve the DBUS multithreading issue, we will periodically poll the queue in order
      self._queue_check = threading.Timer(1.0, self.ParseQueue)
      self._queue_check.start()

   def startDbus(self):
      self._logger.info("LoRa protocol instanced")

      ## DBus init (Legacy)
      #dbus.service.Object.__init__(self, dbus.SessionBus(), OPATH)

      # DBus init (alternative)
      bus = dbus.SessionBus()
      bus.request_name(globals.BUS_NAME)
      bus_name = dbus.service.BusName(globals.BUS_NAME, bus=bus)
      dbus.service.Object.__init__(self, bus_name, globals.OPATH)

      self.AutoStartDiscovery()

   def AutoStartDiscovery(self):
      def delayedStartDiscovery():
        time.sleep(5)
        uri = 'http://'+self._AGILE_API_BASE+':8080/api/protocols/discovery'
        self._logger.debug('Auto Starting Discovery, uri: ' + uri)
        r = requests.post(uri, json={})

      thread = threading.Thread(target=delayedStartDiscovery, args=())
      thread.daemon = True
      thread.start()

   def AutoRegisterDevice(self, item):
      def delayedRegisterDevice():
        for attempt in range(3):
          time.sleep(3)
          uri = 'http://'+self._AGILE_API_BASE+':8080/api/devices'
          self._logger.info("Auto Registering, uri: ' + uri + ', device: " + json.dumps(item))
          r = requests.post(uri, json={
            "overview": {
              "name": item["deviceID"],
              "protocol": "org.eclipse.agail.protocol.LoRa",
              "id": item["hardwareID"],
              "status": item["status"]
            },
            "type": "LoRa"
          })
          if r.ok:
            time.sleep(1)
            for stream in item['streams']:
              self.AutoSubscribeItem(item['hardwareID'], stream)
            break
          else:
            self._logger.error('Failed to register device')

      thread = threading.Thread(target=delayedRegisterDevice, args=())
      thread.daemon = True
      thread.start()

   def AutoSubscribeItem(self, hardwareID, item):
      uri = 'http://'+self._AGILE_API_BASE+':8080/api/device/lora'+hardwareID+'/'+item['id']+'/subscribe'
      self._logger.debug('Auto Subscribe, uri: ' + uri + ', item:' + hardwareID + ', id:' + item['id'])
      r = requests.post(uri, json={})
      def forceSubscription():
        time.sleep(2)
        self.Subscribe(hardwareID, { "id": item['id'] })

      thread = threading.Thread(target=forceSubscription, args=())
      thread.daemon = True
      thread.start()

   # Override DBus object methods
   ### GENERIC METHODS
   @dbus.service.method(globals.IFACE, in_signature="", out_signature="s")
   def Status(self):
      #self._logger.debug("Status")
      return ""

   @dbus.service.method(globals.IFACE, in_signature="", out_signature="s")
   def Name(self):
      #self._logger.debug("Name")
      return self._protocol_name

   ### DRIVER
   @dbus.service.method(globals.IFACE, in_signature="", out_signature="s")
   def Driver(self):
      #self._logger.debug("Driver")
      return self._driver_name

   ### START DISCOVERY
   @dbus.service.method(globals.IFACE, in_signature="", out_signature="")
   def StartDiscovery(self):
      #self._logger.debug("StartDiscovery")
      if (self._discovery_status.name == "NONE"):
         self._discovery_status = globals.DISCOVERY_STATUS["RUNNING"]
         self._logger.debug("LoRa StartDiscovery - " + self._discovery_status.name)
         self.Discovery()
      else:
         self._logger.debug("Protocol discovery already on")

   ### STOP DISCOVERY
   @dbus.service.method(globals.IFACE, in_signature="", out_signature="")
   def StopDiscovery(self):
      #self._logger.debug("StopDiscovery")
      if (self._discovery_status.name == "RUNNING"):
         if (isinstance(self._task_discovery, threading.Timer)):
            self._task_discovery.cancel()
         self._discovery_status = globals.DISCOVERY_STATUS["NONE"]
         self._logger.debug("LoRa StopDiscovery - " + self._discovery_status.name)
      else:
          self._logger.debug("Protocol discovery already off")

   ### DISCOVERY STATUS
   @dbus.service.method(globals.IFACE, in_signature="", out_signature="s")
   def DiscoveryStatus(self):
      #self._logger.debug("DiscoveryStatus")
      return self._discovery_status.name

   #Returns list discovered protocol devicesdevices
   @dbus.service.method(globals.IFACE, in_signature="", out_signature="a(ssss)")
   def Devices(self):
      #self._logger.debug("Devices")
      out = []
      if len(self._devices_list):
         for dev in self._devices_list:
            out.append([dev["hardwareID"], globals.IFACE + ".LoRa", dev["deviceID"], dev["status"]])

      return out

   ### CONNECT
   @dbus.service.method(globals.IFACE, in_signature="s", out_signature="")
   def Connect(self,device_id):
      #self._logger.debug("Connect")
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
   @dbus.service.method(globals.IFACE, in_signature="s", out_signature="")
   def Disconnect(self, device_id):
      #self._logger.debug("Disconnect")
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
   @dbus.service.method(globals.IFACE, in_signature="sa{ss}", out_signature="ay")
   def Read(self, device_id, profile):
      self._logger.debug("Read")
      hit_1 = pydash.find(self._devices_list, {"hardwareID": device_id})
      if (hit_1 != None):
            hit_2 = pydash.find(hit_1["streams"], {"id": profile["id"]})
            if (hit_2 != None):
                  self._logger.debug('Read sensor: hardwareID=' + device_id + ', ' + profile['id'] + '=' + hit_2['value'])
                  return self.SerializeValue(hit_2["format"], hit_2["value"])
            else:
                  ProtocolException("Component not found (subscription to device ID) " + device_id)
                  return bytearray([])
      else:
            ProtocolException("Component not found (subscription to device ID) " + device_id)
            return bytearray([])

   ### WRITE (return last observation)
   @dbus.service.method(globals.IFACE, in_signature="sa{ss}ay", out_signature="")
   def Write(self, device_id, profile, payload):
      #self._logger.debug("Write")
      pass

   ### DATA (return last observation)
   @dbus.service.method(globals.IFACE, in_signature="", out_signature="ay")
   def Data(self):
      #self._logger.debug("Data")
      return self.GetLastRecordValue()

   ### DEVICE STATUS
   @dbus.service.method(globals.IFACE, in_signature="s", out_signature="s")
   def DeviceStatus(self, device_id):
      #self._logger.debug("DeviceStatus")
      hit = pydash.find(self._devices_list, {"hardwareID": device_id})
      if (hit):
         return hit["status"]
      else:
         return globals.DEVICE_STATUS["ERROR"].name

   # Need to be fixed (DBUS multi-threading)
   @dbus.service.method(globals.IFACE, in_signature="", out_signature="")
   def NewRecordNotification(self):
      self._logger.debug("NewRecordNotification")
      self.ParseQueue()

   @dbus.service.method(globals.IFACE, in_signature="sa{ss}", out_signature="")
   def Subscribe(self, device_id, profile):
      hit_1 = pydash.find(self._devices_list, {"hardwareID": device_id})
      if (hit_1 != None):
            hit_2 = pydash.find(hit_1["streams"], {"id": profile["id"]})
            if (hit_2 != None):
                  hit_2["subscribed"] = True
                  self._logger.info("Subscribed to " + device_id + " - " + profile['id'])

                  value = self.SerializeValue(hit_2["format"], hit_2["value"])
                  self.NewRecordSignal(value, device_id, profile)
            else:
                  ProtocolException("Component " + profile['id']+ " not found (subscription to device ID) " + device_id)
      else:
            ProtocolException("Component not found (subscription to device ID) " + device_id)

   @dbus.service.method(globals.IFACE, in_signature="sa{ss}", out_signature="")
   def Unsubscribe(self, device_id, profile):
      hit_1 = pydash.find(self._devices_list, {"hardwareID": device_id})
      if (hit_1 != None):
            hit_2 = pydash.find(hit_1["streams"], {"id": profile["id"]})
            if (hit_2 != None):
                  hit_2["subscribed"] = False
                  self._logger.info("Unsubscribed from " + device_id + " - " + profile['id'])
            else:
                  ProtocolException("Component not found (subscription to device ID) " + device_id)
      else:
            ProtocolException("Component not found (subscription to device ID) " + device_id)

   # Signal handlers
   @dbus.service.signal(globals.IFACE, signature="aysa{ss}")
   def NewRecordSignal(self, value, id, profile):
      self._logger.debug("NewRecordSignal: hardwareID=" + id + ', ' + profile['id'])
      pass

   ###### Non-DBUS methods (discovery, etc.) ######
   def Discovery(self):
      #Discovery tasks - First version -> Discover all devices
      if (self._discovery_status == globals.DISCOVERY_STATUS["RUNNING"]):

            # Need to get the list of discovered devices and send the signal only in case of a new one
            self._protocol_manager.GetDevices()

            # Send signal only in case of a new device
            for item in self._devices_list:
               if (self._protocol_manager.DeviceDiscovered(item["hardwareID"]) < 0):
                  self._protocol_manager.FoundNewDeviceSignal([item["hardwareID"], globals.BUS_NAME, item["deviceID"], item["status"]])
                  # Auto register device
                  self.AutoRegisterDevice(item)

      self._task_discovery = threading.Timer(10.0, self.Discovery)
      self._task_discovery.start()

   def ParseQueue(self):
      if (not globals.queue.empty()):
         while (not globals.queue.empty()):
            item = globals.queue.get(block=False)

            hit = pydash.find(self._devices_list, {"hardwareID": item["hardwareID"]})
            if (hit):
               #self._logger.debug("Update observation - lora" + item["hardwareID"])
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
               #self._logger.info("New item - lora" + item["hardwareID"])
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
      self._queue_check = threading.Timer(1.0, self.ParseQueue)
      self._queue_check.start()

   def ManageRecordSignal(self, id, item):
      hit_1 = pydash.find(self._devices_list, {"hardwareID": id})
      if (hit_1 != None):
            hit_2 = pydash.find(hit_1["streams"], {"id": item["id"]})
            if (hit_2 != None):
                  if (hit_2["subscribed"] == True):  # Change to True after testing
                        value = self.SerializeValue(item["format"], item["value"])
                        self.NewRecordSignal(value, id, {"id": item["id"]})
                  else:
                        self._logger.debug('ManageRecordSignal, not subscribed - ' + id)
                        self.AutoSubscribeItem(id, item)

   def SaveLastRecordObject(self, record, component):
      self._last_record = {
         "deviceID": record["hardwareID"],
         "componentID": component["id"],
         "value": component["value"],
         "unit": component["unit"],
         "format": component["format"],
         "lastUpdate": component["lastUpdate"]
      }

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

   def SerializeValue(self, value_type, value):
      if (value_type == "integer"):
            output = bytearray((value).to_bytes(4, int(value)))
      elif (value_type == "float"):
            output = bytearray(struct.pack(">f", float(value)))
      elif (value_type == "string"):
            output = value.encode()
      else:
            ProtocolException("Format value not compatible (choose between integer, float or string")
      return output

   def TearDown(self):
      #self._logger.debug("TearDown")
      if (isinstance(self._task_discovery, threading.Timer)):
          self._task_discovery.cancel()
      if (isinstance(self._queue_check, threading.Timer)):
          self._queue_check.cancel()


# We need another object path to handle the FoundNewDeviceSignal
class ProtocolManager(dbus.service.Object):
   def __init__(self):
      self._logger = logging.getLogger(globals.PM_BUS_NAME)
      # Interface
      self._devices = []

   def startDbus(self):
      self._logger.info("Protocol manager instanced")
      pm_bus = dbus.SessionBus()
      pm_bus.request_name(globals.PM_BUS_NAME)
      pm_bus_name = dbus.service.BusName(globals.PM_BUS_NAME, bus=pm_bus)
      dbus.service.Object.__init__(self, pm_bus_name, globals.PM_OPATH)
      temp = pm_bus.get_object( "org.eclipse.agail.ProtocolManager", "/org/eclipse/agail/ProtocolManager")
      self._interface = dbus.Interface (temp, "org.eclipse.agail.ProtocolManager")

   def GetDevices(self):
      #self._logger.debug("GetDevices")
      if (len(self._devices)):
         self._devices = []

      temp = self._interface.Devices()
      for dev in temp:
         self._devices.append(str(dev[0]))

   # Check whether a device has been already "seen" by the DeviceManager
   def DeviceDiscovered(self, id):
      #self._logger.debug("DeviceDiscovered")
      return pydash.arrays.find_index(self._devices, lambda x: x == id)

   @dbus.service.signal(globals.PM_IFACE, signature="(ssss)")
   def FoundNewDeviceSignal(self, device_description):
      #self._logger.debug("FoundNewDeviceSignal")
      pass

class ProtocolException(dbus.DBusException):
   def __init__(self, protocol_name, msg=""):
      if msg == "":
         super().__init__("Exception")
      else:
         super().__init__(msg)
      self._dbus_error_name = globals.BUS_NAME
