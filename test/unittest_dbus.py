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
sys.path.append('./utils/')
import globals as globals

import unittest
import dbus
import dbus.service
import time
from queue import Queue
import threading
import struct
import logging

import codecs
import base64
import cayenne_parser
import datetime
import pydash


class DbusTest(unittest.TestCase):  

  def test_session_bus(self):
    bus = dbus.SessionBus()  
    eth0 = bus.get_object( globals.BUS_NAME, globals.OPATH)
    interface = dbus.Interface (eth0, "org.eclipse.agail.Protocol")       
    self.assertTrue(1)    
  
  def test_protocol_name(self):
    bus = dbus.SessionBus()  
    eth0 = bus.get_object( globals.BUS_NAME, globals.OPATH)
    interface = dbus.Interface (eth0, "org.eclipse.agail.Protocol")      
    self.assertEqual(interface.Name(), "LoRa")

  def test_driver_name(self):
    bus = dbus.SessionBus()  
    eth0 = bus.get_object( globals.BUS_NAME, globals.OPATH)
    interface = dbus.Interface (eth0, "org.eclipse.agail.Protocol")       
    self.assertEqual(interface.Driver(), "LoRa")

  def test_discovery(self):
    bus = dbus.SessionBus()  
    eth0 = bus.get_object( globals.BUS_NAME, globals.OPATH)
    interface = dbus.Interface (eth0, "org.eclipse.agail.Protocol")      
    self.assertIsNone(interface.StartDiscovery())
    self.assertEqual(interface.DiscoveryStatus(), "RUNNING")
    self.assertIsNone(interface.StopDiscovery())
    self.assertEqual(interface.DiscoveryStatus(), "NONE")  
  
  def test_lastvalue(self):
    bus = dbus.SessionBus()  
    eth0 = bus.get_object( globals.BUS_NAME, globals.OPATH)
    interface = dbus.Interface (eth0, "org.eclipse.agail.Protocol")      
    self.assertIsNotNone(interface.Data())


if __name__ == '__main__':
    unittest.main()

