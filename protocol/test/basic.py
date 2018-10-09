#! /usr/bin/python3

#################################################################
#   Copyright (C) 2018  
#   This program and the accompanying materials are made
#   available under the terms of the Eclipse Public License 2.0
#   which is available at https://www.eclipse.org/legal/epl-2.0/ 
#   SPDX-License-Identifier: EPL-2.0
#   Contributors: ATOS SPAIN S.A.
################################################################# 

import sys
sys.path.append('utils')
import globals as globals

import dbus
import dbus.service
import time
from queue import Queue
import threading
import struct
import logging


try:  

  if __name__ == "__main__":   
    logging.basicConfig(
        filemode="a",
        format="%(asctime)s [%(levelname)s] [%(threadName)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.DEBUG
    )    

  bus = dbus.SessionBus() 
  
  eth0 = bus.get_object( globals.BUS_NAME, globals.OPATH)
  interface = dbus.Interface (eth0, "org.eclipse.agail.Protocol")
  
  logging.info ("---INTROSPECTION---")
  logging.info (eth0.Introspect())
  logging.info ("---Connect new device---")
  logging.info (eth0.Connect("3339343771356214"))
  logging.info ("---Get Devices---")
  logging.info (interface.Devices())
  logging.info ("---Get Protocol Name---")
  logging.info (interface.Name())
  logging.info ("---Get Driver---")
  logging.info(interface.Driver())
  logging.info(interface.DiscoveryStatus())  
  logging.info ("---Start Discovery---")
  interface.StartDiscovery()
  logging.info(interface.DiscoveryStatus())
  logging.info ("---Stop Discovery---")
  interface.StopDiscovery()
  logging.info ("---Get Discovery Status---")
  logging.info(interface.DiscoveryStatus())
  logging.info("---GET LAST RECORD---")
  logging.info(interface.Data())
  logging.info ("---GET DEVICES---")  
  logging.info(interface.Devices()) 
  logging.info ("---GET DEVICE STATUS---")  
  logging.info(interface.DeviceStatus("3339343771356214"))   
  logging.info ("---GET LAST VALUE FROM A PARTICULAR DEVICE---")  
  temp = interface.Read("3339343771356214", {"id": "Temperature"})
  logging.info("Temperature = " + str(temp))
  logging.info (struct.unpack('f', bytes(temp)))
  logging.info ("---Subscribe---")  
  logging.info (interface.Subscribe("3339343771356214", {"id": "Temperature"}))
  logging.info ("---Unsubscribe---")  
  logging.info (interface.Unsubscribe("3339343771356214", {"id": "Temperature"}))    
  
except Exception as err:
  logging.info("Error -- {}".format(err))
