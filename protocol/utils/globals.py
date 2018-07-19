#################################################################
#   Copyright (C) 2018  
#   This program and the accompanying materials are made
#   available under the terms of the Eclipse Public License 2.0
#   which is available at https://www.eclipse.org/legal/epl-2.0/ 
#   SPDX-License-Identifier: EPL-2.0
#   Contributors: ATOS
################################################################# 

import enum
from queue import Queue

# LoRa Protocol
OPATH = "/org/eclipse/agail/protocol/LoRa"
IFACE = "org.eclipse.agail.Protocol"
BUS_NAME = "org.eclipse.agail.protocol.LoRa"

# Protocol Manager signal emitter
PM_OPATH = "/org/eclipse/agail/NewDevice"
PM_IFACE = "org.eclipse.agail.ProtocolManager"
PM_BUS_NAME = "org.eclipse.agail.ProtocolManager"

# Queue
queue = Queue()

# States
class DEVICE_STATUS(enum.Enum):
    CONNECTED = 1
    DISCONNECTED = 2
    ON = 3
    OFF = 4
    ERROR = 5

class STATUS_TYPE(enum.Enum):
    CONNECTED = 1
    DISCONNECTED = 2
    AVAILABLE = 3

class DISCOVERY_STATUS(enum.Enum):
   RUNNING = 1
   NONE= 2

