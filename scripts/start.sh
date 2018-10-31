#!/bin/sh
#-------------------------------------------------------------------------------
# Copyright (C) 2017 Create-Net / FBK.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License 2.0
# which accompanies this distribution, and is available at
# https://www.eclipse.org/legal/epl-2.0/
#
# SPDX-License-Identifier: EPL-2.0
# 
# Contributors:
#     Create-Net / FBK - initial API and implementation
#-------------------------------------------------------------------------------


MODULE=${1:-all}
# DEPS=`realpath ./deps` 

# if [ ! -e "$DEPS" ]; then
#   echo "Installing dependencies" 
#   ./scripts/install-deps.sh
# fi

TOEXPORT=""

# if [ ! -z "$DISPLAY" ]; then
#   echo ">> DISPLAY available, reusing current display"
# else
#   export DISPLAY=:0
#   TOEXPORT="\n$TOEXPORT\nexport DISPLAY=$DISPLAY"
# fi

ME=`whoami`



if [ ! -z "$DBUS_SESSION_BUS_ADDRESS" ]; then
  echo ">> DBUS_SESSION_BUS_ADDRESS available, reusing current instance"
else

  if [ `pgrep -U $ME dbus-daemon -c` -gt 0 ]; then

    echo ">> DBus session available"

    MID=`sed "s/\n//" /var/lib/dbus/machine-id`
    DISPLAYID=`echo $DISPLAY | sed "s/://"`
    SESSFILEPATH="/home/$ME/.dbus/session-bus/$MID-$DISPLAYID"

    if [ -e $SESSFILEPATH ]; then
      echo ">> Loading DBus session instance address from local file"
      echo ">> Source: $SESSFILEPATH"
      . "$SESSFILEPATH"
    else
      echo "Cannot get Dbus session address. Panic!"
    fi

  else
    export `dbus-launch`
    sleep 2
    echo "++ Started a new DBus session instance"
  fi

fi

export AGILE_STACK=../agile-stack
export AGILE_HOST=localhost
export AGILE_ARCH=armv7l

unset DOCKER_HOST
# export DATA=$HOME/.agile
export DATA=/usr/src/app/.agile
export DOCKER_API_VERSION=1.22

export DBUS_SYSTEM_SOCKET=/var/run/dbus/system_bus_socket
export DBUS_SESSION_SOCKET_DIR=$DATA/agile_bus
export DBUS_SESSION_SOCKET_NAME=agile_bus_socket
export DBUS_SESSION_SOCKET=$DBUS_SESSION_SOCKET_DIR/$DBUS_SESSION_SOCKET_NAME
export DBUS_SESSION_BUS_ADDRESS=unix:path=$DBUS_SESSION_SOCKET

TOEXPORT="\n$TOEXPORT\nexport DBUS_SESSION_BUS_ADDRESS=$DBUS_SESSION_BUS_ADDRESS"

if [ -z "$DBUS_SESSION_BUS_ADDRESS" ]; then
  echo "!! Cannot export DBUS_SESSION_BUS_ADDRESS. Exit"
  exit 1
fi

# export DBUS_SESSION_BUS_ADDRESS



# if [ $MODULE = 'all' ] || [ $MODULE = 'LoRA' ]; then
#   ./scripts/stop.sh "protocol.LoRa"

  # wait for ProtocolManager to initialize
  # while `! qdbus org.eclipse.agail.ProtocolManager > /dev/null`; do
  #   echo "waiting for ProtocolManager to initialize";
  #   sleep 1;
  # done

  # Register LoRa in ProtocolManager
  qdbus org.eclipse.agail.ProtocolManager /org/eclipse/agail/ProtocolManager org.eclipse.agail.ProtocolManager.Add LoRa

  python3 ./dbus_server.py
  echo "Started AGILE LoRa protocol"
# fi


echo "Module launched use these variables in the shell:"
echo $TOEXPORT
echo ""

wait