#!/usr/bin/env python
# coding=utf-8
#
# Copyright © 2018 UnravelTEC
# Michael Maier <michael.maier+github@unraveltec.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# If you want to relicense this code under another license, please contact info+github@unraveltec.com.

from __future__ import print_function

# This module uses the services of the C pigpio library. pigpio must be running on the Pi(s) whose GPIO are to be manipulated. 
# cmd ref: http://abyz.me.uk/rpi/pigpio/python.html#i2c_write_byte_data
import pigpio # aptitude install python-pigpio
import time
import struct
import sys
import crcmod # aptitude install python-crcmod


def eprint(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)



PIGPIO_HOST = '::1'
PIGPIO_HOST = '127.0.0.1'

pi = pigpio.pi(PIGPIO_HOST)
if not pi.connected:
  eprint("no connection to pigpio daemon at " + PIGPIO_HOST + ".")
  exit(1)

I2C_SLAVE = 0x69
I2C_BUS = 1

try:
  pi.i2c_close(0)
except:
  if sys.exc_value and str(sys.exc_value) != "'unknown handle'":
    eprint("Unknown error: ", sys.exc_type, ":", sys.exc_value)

try:
	h = pi.i2c_open(I2C_BUS, I2C_SLAVE)
except:
	eprint("i2c open failed")
	exit(1)


f_crc8 = crcmod.mkCrcFun(0x131, 0xFF, False, 0x00)


def calcCRC(TwoBdataArray):
  byteData = ''.join(chr(x) for x in TwoBdataArray)
  return f_crc8(byteData)

# print(hex(calcCRC([0xBE,0xEF])))

def readNBytes(n):
  try:
    (count, data) = pi.i2c_read_device(h, n)
  except:
    eprint("error: i2c_read failed")
    exit(1)

  if count == n:
    return data
  else:
    eprint("error: read bytes didnt return " + str(n) + "B")
    return False

# takes an array of bytes (integer-array)
def i2cWrite(data):
  try:
    pi.i2c_write_device(h, data)
  except:
    eprint("error: i2c_write failed")
    return -1
  return True

def readFromAddr(LowB,HighB,nBytes):
  for amount_tries in range(3):
    i2cWrite([LowB, HighB])
    data = readNBytes(nBytes)
    if data:
      return data
    eprint("error in readFromAddr: " + hex(LowB) + hex(HighB) + " " + str(nBytes) + "B did return Nothing")
  return False

def readArticleCode():
  data = readFromAddr(0xD0,0x25,47)
  acode = ''
  crcs = ''
  for i in range(47):
    currentByte = data[i]
    if currentByte == 0:
      break;
    if (i % 3) != 2:
      acode += chr(currentByte) + '|'
    else:
      crcs += str(currentByte) + '.'
  eprint('Article code: "' + acode + '"')
 # print(crcs)

def readSerialNr():
  data = readFromAddr(0xD0,0x33,47)
  snr = ''
  for i in range(47):
    if (i % 3) != 2:
      currentByte = data[i]
      if currentByte == 0:
        break;
      if i != 0:
        snr += '-'
      snr += chr(currentByte)
  eprint('Serial number: ' + snr)

def readCleaningInterval():
  data = readFromAddr(0x80,0x04,6)
  if data and len(data):
    interval = calcInteger(data)
    eprint('cleaning interval:', str(interval), 's')

def startMeasurement():
  i2cWrite([0x00, 0x10, 0x03, 0x00, calcCRC([0x03,0x00])])

def stopMeasurement():
  i2cWrite([0x01, 0x04])

def readDataReady():
  data = readFromAddr(0x02, 0x02,3)
  if data[1]:
    #print ("data ready")
    return True
  else:
    #print ("data not ready")
    return False

def calcInteger(sixBArray):
  integer = sixBArray[4] + (sixBArray[3] << 8) + (sixBArray[1] << 16) + (sixBArray[0] << 24)
  return integer

def calcFloat(sixBArray):
  struct_float = struct.pack('>BBBB', sixBArray[0], sixBArray[1], sixBArray[3], sixBArray[4])
  float_values = struct.unpack('>f', struct_float)
  first = float_values[0]
  return first

def printPrometheus(data):
  print("pm0.5_count %f" % calcFloat(data[24:30]))
  print("pm1_ug %f" % calcFloat(data))
  print("pm2.5_ug %f" % calcFloat(data[6:12]))
  print("pm4_ug %f" % calcFloat(data[12:18]))
  print("pm10_ug %f" % calcFloat(data[18:24]))
  print("pm1_count %f" % calcFloat(data[30:36]))
  print("pm2.5_count %f" % calcFloat(data[36:42]))
  print("pm4_count %f" % calcFloat(data[42:48]))
  print("pm10_count %f" % calcFloat(data[48:54]))
  print("pm_typ %f" % calcFloat(data[54:60]))

def printHuman(data):
  print("pm0.5 count: %f" % calcFloat(data[24:30]))
  print("pm1   count: {0:.3f} ug: {1:.3f}".format( calcFloat(data[30:36]), calcFloat(data) ) )
  print("pm2.5 count: {0:.3f} ug: {1:.3f}".format( calcFloat(data[36:42]), calcFloat(data[6:12]) ) )
  print("pm4   count: {0:.3f} ug: {1:.3f}".format( calcFloat(data[42:48]), calcFloat(data[12:18]) ) )
  print("pm10  count: {0:.3f} ug: {1:.3f}".format( calcFloat(data[48:54]), calcFloat(data[18:24]) ) )
  print("pm_typ: %f" % calcFloat(data[54:60]))


def readPMValues():
  data = readFromAddr(0x03,0x00,59)
  #printHuman(data)
  printPrometheus(data)

readArticleCode()
readSerialNr()
readCleaningInterval()

startMeasurement()

for count in range(10):
  while not readDataReady():
    time.sleep(0.5)
  readPMValues()

stopMeasurement()

pi.i2c_close(h)

exit(1)
