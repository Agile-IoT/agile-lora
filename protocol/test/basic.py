
#################################################################
#   Copyright (C) 2018  
#   This program and the accompanying materials are made
#   available under the terms of the Eclipse Public License 2.0
#   which is available at https://www.eclipse.org/legal/epl-2.0/ 
#   SPDX-License-Identifier: EPL-2.0
#   Contributors: ATOS
################################################################# 

#!/usr/bin/env python3

import sys
sys.path.append('../config/')
import globals as globals

import dbus
import dbus.service
import time
from queue import Queue
import threading

try:
  bus = dbus.SessionBus()
  eth0 = bus.get_object( globals.BUS_NAME, globals.BUS_PATH + "/LoRa")
  interface = dbus.Interface (eth0, "org.eclipse.agail.protocol")
  
  print ("---INTROSPECTION---")
  print (eth0.Introspect())
  print ("---Connect new device---")
  print (interface.Connect("3339343771356214"))
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

  print("---GET DATA---")
  print(interface.Data())

  print ("---GET DEVICES---")
  devices = interface.Devices()
  print(devices)
  
  # interface.connect_to_signal("Test", hello_signal_handler, dbus_interface="com.example.TestService", arg0="Hello")  
  
except Exception as err:
  print("Error -- {}".format(err))