#! /usr/bin/python3

#################################################################
#   Copyright (C) 2018  
#   This program and the accompanying materials are made
#   available under the terms of the Eclipse Public License 2.0
#   which is available at https://www.eclipse.org/legal/epl-2.0/ 
#   SPDX-License-Identifier: EPL-2.0
#   Contributors: ATOS
################################################################# 

import os
import sys
# sys.path.append('../config/')
import globals as globals
import mqtt_conf 
import dummy
import ttn_client
import loraserver_client
import logging

#There is some kind of issue with this dbus instance on a different thread than the original one
# class RecordNotifier(dbus.service.Object):
#     def __init(self):
#         try:
#             self._dbus_interface = dbus.Interface (dbus.SessionBus().get_object(globals.BUS_NAME, globals.BUS_PATH + '/LoRa' ), 
#              "org.eclipse.agail.protocol")  
#             super().__init__(dbus.SessionBus(), globals.BUS_PATH + "/LoRa")
#             self._dbus = dbus.service.BusName(globals.BUS_NAME, dbus.SessionBus(), do_not_queue=True) 
#         except dbus.exceptions.NameExistsException:
#             print("service is already running")
#             sys.exit(1)

#     def Send(self):
#         print(self._dbus.Name()) 

class MqttClient():
    def __init__(self):                        
        self._logger = logging.getLogger(globals.BUS_NAME)           
        # self._dbus = RecordNotifier()

        try:
            if (mqtt_conf.APP_SERVER == "TTN"):
                self._listener = ttn_client.TtnClient()        
            elif (mqtt_conf.APP_SERVER == "LoRaServer"):  
                self._listener = loraserver_client.LoRaServerClient()    
            elif (mqtt_conf.APP_SERVER == "Dummy"):            
                self._listener = dummy.DummyListener()    
            else: 
                self._listener = None
                raise KeyError("Application server not found - " + mqtt_conf.APP_SERVER)                
        except:                    
            pass


    def TearDown(self):      

        # Tear down MQTT instances
        if (self._listener):
            self._listener.TearDown()    
        