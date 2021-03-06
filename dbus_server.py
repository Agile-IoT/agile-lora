#! /usr/bin/python3

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
sys.path.append('mqtt/')
sys.path.append('utils/')

import logging
from gi.repository import GLib
import dbus
import dbus.service
import dbus.exceptions
import dbus.mainloop.glib
import threading

from os.path import join, dirname
from dotenv import load_dotenv

import globals as globals
from mqtt_client import MqttClient 
from dbus_protocols import lora as lora_protocol
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
   logging.debug("DBus service stopped")
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
 
   # Check whether .env file exists (otherwise, we will assume that they will be already set)
   if (os.path.exists('.env')):
      logging.info (".env file found")
      load_dotenv(join(dirname(__file__), '.env'))     

   # Set of environment variables that are needed to successfully run the protocol
   if ((os.environ.get('LORAWAN_APP_SERVER') is not None) and \
       (os.environ.get('LORAWAN_APPID') is not None) and \
       (os.environ.get('LORAWAN_PSW') is not None) and \
       (os.environ.get('LORAWAN_MQTT_URL') is not None)):          
      dbusLoop()  
   else:
      logging.error('Needed environment variables not found - closing')

   endProgram(0)
# -----------------------

