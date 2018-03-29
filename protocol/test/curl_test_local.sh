#! /bin/sh


#################################################################
#   Copyright (C) 2018  
#   This program and the accompanying materials are made
#   available under the terms of the Eclipse Public License 2.0
#   which is available at https://www.eclipse.org/legal/epl-2.0/ 
#   SPDX-License-Identifier: EPL-2.0
#   Contributors: ATOS
################################################################# 

host="http://192.168.1.30:8080"
verbose=""
device="dummy001122334455"

protocol="LoRa"

echo "******DeviceManager******"

echo "----GET DEVICES----"
curl $verbose  GET "$host/api/devices" -H "accept: application/json"
echo


echo "******ProtocolManager******"
echo "----GET PROTOCOLS----"
curl $verbose  GET "$host/api/protocols" -H "accept: application/json"
echo 

echo "----REGISTER PROTOCOL----"
curl -v  -X POST "$host/api/protocols/$protocol" -H "accept: application/json"
echo 

echo "----DELETE PROTOCOL----"
curl $verbose  -X DELETE "$host/api/protocols/$protocol" -H "accept: application/json"
echo 