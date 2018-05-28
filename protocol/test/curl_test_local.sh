#! /bin/sh

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