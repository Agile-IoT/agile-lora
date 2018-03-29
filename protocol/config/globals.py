
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

#Global variables
BUS_NAME = "org.eclipse.agail.protocol"
BUS_PATH = "/org/eclipse/agail/protocol"

NEW_DEVICE_SIGNAL_PATH = "/org/eclipse/agail/NewDevice"
NEW_RECORD_SIGNAL_PATH = "/org/eclipse/agail/NewRecord"

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
    AVAILABLE = 2

class DISCOVERY_STATUS(enum.Enum):
   RUNNING = 1
   NONE= 2

