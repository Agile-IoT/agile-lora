
`LoRaWAN protocol implementation for the AGILE gateway`

# Work in progress
## Current branching

- 1-lora-mqtt-cayenne &rarr; Base version of the DBUS LoRaWAN protocol compatible with the AGILE stack that works together with a basic MQTT client plus a Cayenne adapter


## LoRa highlights (documentation and wiki ongoing)

## DBus interface
- Bus name: *org.eclipse.agail.protocol.LoRa*
- Bus path: */org/eclipse/agail/protocol/LoRa*
- Interface: *org.eclipse.agail.protocol*

## DBus methods and signals

- Setup
- Connect 
- Disconnect
- Connected
- Driver
- DiscoveryStatus
- StartDiscovery
- EndDiscovery
- Send
- Receive
- Status
- Devices
- DeviceStatus
- Data
- Unsubscribe
- Create
- Delete


## Installation

Before running the server and the subsequent protocol instance, some libraries must be installed: 

`sudo apt-get install libdbus-1-dev libdbus-glib-1-dev python3-gi`

Moreover, some other libraries have to be installed too; in this case, through an explicit requirements file

`sudo python3 -m pip install -r requirements.txt`

## Usage

For this first and unplugged version (not connected to the AGILE stack yet), we can run the server and check that the bus and its underlying methods work accordingly

`python3 dbus_server.py`

## Docker 

As this is a preliminar version that, besides, has to be merged with a LoRaWAN AS, we have not paid much attention yet to the "dockerization" of the process

## Debugging

A good tool to see what is happening on DBUS (both system and session buses) is [D-feet](https://github.com/GNOME/d-feet) (for Linux systems). With it, we can graphically introspect the interface we are defined, as well as play around with the available methods in a mush easier way rather than e.g. the legacy *dbus-send* CLI commands.