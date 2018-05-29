#! /usr/bin/python3

import sys
sys.path.append('../config/')
import globals as globals

import dbus
import dbus.service
import time
from queue import Queue
import threading
import struct

try:
  bus = dbus.SessionBus() 
  
  eth0 = bus.get_object( globals.BUS_NAME, globals.OPATH)
  interface = dbus.Interface (eth0, "org.eclipse.agail.Protocol")
  
  print ("---INTROSPECTION---")
  print (eth0.Introspect())
  print ("---Connect new device---")
  print (eth0.Connect("3339343771356214"))
  print ("---Get Devices---")
  print (interface.Devices())
  print ("---Get Protocol Name---")
  print (interface.Name())
  print ("---Get Driver---")
  print(interface.Driver())
  print(interface.DiscoveryStatus())  
  print ("---Start Discovery---")
  interface.StartDiscovery()
  print(interface.DiscoveryStatus())
  print ("---Stop Discovery---")
  interface.StopDiscovery()
  print ("---Get Discovery Status---")
  print(interface.DiscoveryStatus())
  print("---GET LAST RECORD---")
  print(interface.Data())
  print ("---GET DEVICES---")  
  print(interface.Devices()) 
  print ("---GET DEVICE STATUS---")  
  print(interface.DeviceStatus("3339343771356214"))   
  print ("---GET LAST VALUE FROM A PARTICULAR DEVICE---")  
  temp = interface.Read("3339343771356214", {"id": "Temperature"})
  print("Temperature = " + str(temp))
  print (struct.unpack('f', bytes(temp)))
  print ("---Subscribe---")  
  print (interface.Subscribe("3339343771356214", {"id": "Temperature"}))
  print ("---Unsubscribe---")  
  print (interface.Unsubscribe("3339343771356214", {"id": "Temperature"}))    
  
except Exception as err:
  print("Error -- {}".format(err))