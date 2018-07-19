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
import ttn_client
import loraserver_client
import logging

class MqttClient():
    def __init__(self):                        
        self._logger = logging.getLogger(globals.BUS_NAME)    
        self._listener = None
        
        if os.environ.get('LORAWAN_APP_SERVER'):
            try:
                if (os.environ.get('LORAWAN_APP_SERVER') == "TTN"):
                    self._listener = ttn_client.TtnClient()        
                elif (os.environ.get('LORAWAN_APP_SERVER') == "LoRaServer"):  
                    self._listener = loraserver_client.LoRaServerClient()               
                else: 
                    self._listener = None                    
                    logging.error("Application server not found")                                                       
            except:                                                
                sys.exit("Wrong application server")
        else:
            logging.error("Application server not found - Please configure .env file")


    def TearDown(self):      
        # Tear down MQTT instances        
        if (self._listener):
            self._listener.TearDown()    
        
        
        