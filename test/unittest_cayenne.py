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
sys.path.append("./utils/")
import unittest
import codecs
import base64
import cayenne_parser
import datetime
import pydash

class CayenneTest(unittest.TestCase):

    def test_Digital_In (self):
        payload = "010001"
        b64 = codecs.encode(codecs.decode(payload, 'hex'), 'base64')
        cayenne = cayenne_parser.CayenneParser()        
        out = cayenne.decodeCayenneLpp(b64, datetime.datetime.now())                                  
        hit = pydash.find (out, {"id": "Digital_In"})        
        self.assertTrue(hit)
        self.assertTrue(int(hit["value"]) == 1)

    def test_Digital_Out (self):
        payload = "010101"
        b64 = codecs.encode(codecs.decode(payload, 'hex'), 'base64')
        cayenne = cayenne_parser.CayenneParser()        
        out = cayenne.decodeCayenneLpp(b64, datetime.datetime.now())                     
        hit = pydash.find (out, {"id": "Digital_Out"})        
        self.assertTrue(hit)
        self.assertTrue(int(hit["value"]) == 1)

    def test_Analog_In (self):
        payload = "01020CAD"
        b64 = codecs.encode(codecs.decode(payload, 'hex'), 'base64')
        cayenne = cayenne_parser.CayenneParser()        
        out = cayenne.decodeCayenneLpp(b64, datetime.datetime.now())                     
        hit = pydash.find (out, {"id": "Analog_In"})        
        self.assertTrue(hit)        
        self.assertTrue(float(hit["value"]) == 32.45)

    def test_Analog_Out (self):
        payload = "01030CAD"
        b64 = codecs.encode(codecs.decode(payload, 'hex'), 'base64')
        cayenne = cayenne_parser.CayenneParser()        
        out = cayenne.decodeCayenneLpp(b64, datetime.datetime.now())                     
        hit = pydash.find (out, {"id": "Analog_Out"})        
        self.assertTrue(hit)        
        self.assertTrue(float(hit["value"]) == 32.45)

    def test_Illuminance (self):
        payload = "01650FFF"
        b64 = codecs.encode(codecs.decode(payload, 'hex'), 'base64')
        cayenne = cayenne_parser.CayenneParser()        
        out = cayenne.decodeCayenneLpp(b64, datetime.datetime.now())                    
        hit = pydash.find (out, {"id": "Illuminance"})             
        self.assertTrue(hit)
        self.assertTrue(int(hit["value"]) == 4095)

    def test_Presence (self):
        payload = "016601"
        b64 = codecs.encode(codecs.decode(payload, 'hex'), 'base64')
        cayenne = cayenne_parser.CayenneParser()        
        out = cayenne.decodeCayenneLpp(b64, datetime.datetime.now())             
        
        hit = pydash.find (out, {"id": "Presence"})        
        self.assertTrue(hit)
        self.assertTrue(hit["value"] == "True")

    def test_Temperature (self):
        payload = "0167FFD7"
        b64 = codecs.encode(codecs.decode(payload, 'hex'), 'base64')
        cayenne = cayenne_parser.CayenneParser()        
        out = cayenne.decodeCayenneLpp(b64, datetime.datetime.now())                    
        hit = pydash.find (out, {"id": "Temperature"})        
        self.assertTrue(hit)
        self.assertTrue(float(hit["value"]) == -4.1)

    def test_RelativeHumidity (self):
        payload = "016864"
        b64 = codecs.encode(codecs.decode(payload, 'hex'), 'base64')
        cayenne = cayenne_parser.CayenneParser()        
        out = cayenne.decodeCayenneLpp(b64, datetime.datetime.now())                    
        hit = pydash.find (out, {"id": "Relative_Humidity"})        
        self.assertTrue(hit)
        self.assertTrue(float(hit["value"]) == 50.0)

    def test_Accelerometer (self):
        payload = "017104D2FB2E0000"
        b64 = codecs.encode(codecs.decode(payload, 'hex'), 'base64')
        cayenne = cayenne_parser.CayenneParser()        
        out = cayenne.decodeCayenneLpp(b64, datetime.datetime.now())                   

        hit = pydash.find (out, {"id": "AccelerometerX"})        
        self.assertTrue(hit)
        self.assertAlmostEqual(float(hit["value"]), 1.234, delta=0.1)

        hit = pydash.find (out, {"id": "AccelerometerY"})        
        self.assertTrue(hit)
        self.assertAlmostEqual(float(hit["value"]), -1.234, delta=0.1)

        hit = pydash.find (out, {"id": "AccelerometerZ"})        
        self.assertTrue(hit)
        self.assertAlmostEqual(float(hit["value"]), 0.0, delta=0.1)

    def test_Barometer (self):
        payload = "017300BA"
        b64 = codecs.encode(codecs.decode(payload, 'hex'), 'base64')
        cayenne = cayenne_parser.CayenneParser()        
        out = cayenne.decodeCayenneLpp(b64, datetime.datetime.now())                     
        hit = pydash.find (out, {"id": "Barometric_Pressure"})                

        self.assertTrue(hit)
        self.assertTrue(float(hit["value"]) == 18.6)

    def test_Gyrometer (self):
        payload = "018604D2FB2E0000"
        b64 = codecs.encode(codecs.decode(payload, 'hex'), 'base64')
        cayenne = cayenne_parser.CayenneParser()        
        out = cayenne.decodeCayenneLpp(b64, datetime.datetime.now())              

        hit = pydash.find (out, {"id": "GyrometerX"})        
        self.assertTrue(hit)
        self.assertAlmostEqual(float(hit["value"]), 12.34, delta=0.1)

        hit = pydash.find (out, {"id": "GyrometerY"})        
        self.assertTrue(hit)
        self.assertAlmostEqual(float(hit["value"]), -12.34, delta=0.1)

        hit = pydash.find (out, {"id": "GyrometerZ"})        
        self.assertTrue(hit)
        self.assertAlmostEqual(float(hit["value"]), 0.0, delta=0.1)

    # def test_GPS (self):
    #     payload = "018806765ff2960a0003e8"
    #     b64 = codecs.encode(codecs.decode(payload, 'hex'), 'base64')
    #     cayenne = cayenne_parser.CayenneParser()        
    #     out = cayenne.decodeCayenneLpp(b64, datetime.datetime.now())                

    #     hit = pydash.find (out, {"id": "Longitude"})        
    #     self.assertTrue(hit)
    #     self.assertAlmostEqual(float(hit["value"]), -87.9094, delta=0.1)

    #     hit = pydash.find (out, {"id": "Latitude"})        
    #     self.assertTrue(hit)
    #     self.assertAlmostEqual(float(hit["value"]), 42.3519, delta=0.1)

    #     hit = pydash.find (out, {"id": "Altitude"})        
    #     self.assertTrue(hit)
    #     self.assertAlmostEqual(float(hit["value"]), 10.0, delta=0.1)

if __name__ == '__main__':
    unittest.main()