#! /usr/bin/python3

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
sys.path.append('config/')
sys.path.append('mqtt/')
sys.path.append('utils/')

from gi.repository import GLib
import dbus
import dbus.service
import dbus.exceptions
import dbus.mainloop.glib
import threading

from config import globals as globals
from mqtt_client import MqttClient 
from dbus_protocols import lora as lora_protocol
import logging
# -----------------------

# --- Variables ---------
LOGLEVEL = logging.INFO       # DEBUG, INFO, WARNING, ERROR, CRITICAL
mainloop = GLib.MainLoop()
# -----------------------

# --- Functions ---------
def dbusLoop():   
   dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)     
   
   lora = lora_protocol.LoRaWAN()      
   mqtt = MqttClient()
   try:
      mainloop.run()
   except KeyboardInterrupt:      
      try:
         mqtt.TearDown()    
         lora.TearDown()   
         mainloop.quit()
      except dbus.exceptions.DBusException:
         pass
      endProgram(0)
   
def endProgram(status):
   print ("DBus service stopped")   

   sys.exit(status)
# -----------------------

# --- Main program ------
if __name__ == "__main__":   
   logging.basicConfig(
      filemode="a",
      format="%(asctime)s [%(levelname)s] [%(threadName)s] %(message)s",
      datefmt="%Y-%m-%d %H:%M:%S",
      level=LOGLEVEL
   )   
   dbusLoop()
  
   endProgram(0)
# -----------------------

