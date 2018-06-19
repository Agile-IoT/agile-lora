#################################################################
#   Copyright (C) 2018  
#   This program and the accompanying materials are made
#   available under the terms of the Eclipse Public License 2.0
#   which is available at https://www.eclipse.org/legal/epl-2.0/ 
#   SPDX-License-Identifier: EPL-2.0
#   Contributors: ATOS SPAIN S.A.
################################################################# 

import os
import sys
import globals as globals
import mqtt_conf 
import ttn_client
import loraserver_client
import logging

class MqttClient():
    def __init__(self):                        
        self._logger = logging.getLogger(globals.BUS_NAME)           
        # self._dbus = RecordNotifier()

        try:
            if (mqtt_conf.APP_SERVER == "TTN"):
                self._listener = ttn_client.TtnClient()        
            elif (mqtt_conf.APP_SERVER == "LoRaServer"):  
                self._listener = loraserver_client.LoRaServerClient()               
            else: 
                self._listener = None
                raise NameError("Application server not found - " + mqtt_conf.APP_SERVER)                
        except:                                
            raise RuntimeError("Something happened with the connection to the MQTT Server")                


    def TearDown(self):      

        # Tear down MQTT instances
        if (self._listener):
            self._listener.TearDown()    
        