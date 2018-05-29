#! /bin/sh

# host="http://192.168.1.30:8080"
host="http://localhost:8080"
verbose=""

device="dummy001122334455"

protocol="LoRa"

echo "******DeviceManager******"

echo "----GET DEVICES (Registered)----"
curl $verbose "$host/api/devices" -H "accept: application/json"
echo

echo "----GET DEVICES (Discovered)----"
curl $verbose "$host/api/protocols/devices" -H "accept: application/json"
echo

echo "******ProtocolManager******"
echo "----GET PROTOCOLS----"
curl $verbose "$host/api/protocols" -H "accept: application/json"
echo 

# echo "----REGISTER PROTOCOL----"
# curl  -X POST "$host/api/protocols/$protocol" -H "accept: application/json"
# echo 

echo "----GET PROTOCOL----"
curl $verbose  "$host/api/protocols" -H "accept: application/json"
echo 