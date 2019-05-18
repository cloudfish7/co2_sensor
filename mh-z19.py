# http://eleparts.co.kr/data/design/product_file/SENSOR/gas/MH-Z19_CO2%20Manual%20V2.pdf
import sys
import serial
import time
import subprocess
import getrpimodel
import datetime
from time import sleep 

import RPi.GPIO as GPIO

CO2_DATA_FILE='/opt/co2log/co2data_'

if getrpimodel.model() == "3 Model B":
  serial_dev = '/dev/ttyS0'
  stop_getty = 'sudo systemctl stop serial-getty@ttyS0.service'
  start_getty = 'sudo systemctl start serial-getty@ttyS0.service'
else:
  serial_dev = '/dev/ttyAMA0'
  stop_getty = 'sudo systemctl stop serial-getty@ttyAMA0.service'
  start_getty = 'sudo systemctl start serial-getty@ttyAMA0.service'


def mh_z19():
  ser = serial.Serial(serial_dev,
                      baudrate=9600,
                      bytesize=serial.EIGHTBITS,
                      parity=serial.PARITY_NONE,
                      stopbits=serial.STOPBITS_ONE,
                      timeout=1.0)
  while 1:
    result=ser.write("\xff\x01\x86\x00\x00\x00\x00\x00\x79")
    s=ser.read(9)
    print("--------------------------")
    print(result)
    print(len(s))
    print("--------------------------")
    if len(s)!=0 and  s[0] == "\xff" and s[1] == "\x86":
      return {'co2': ord(s[2])*256 + ord(s[3])}
      break

def sound(loop):
   pinSound = 38

   GPIO.setmode(GPIO.BOARD)
   GPIO.setup(pinSound, GPIO.OUT)

   for idx in range(1, loop+1):
       GPIO.output(pinSound, True)
       time.sleep(0.1)
       GPIO.output(pinSound, False)
       time.sleep(0.1)

def write_data(file_div,data):
  print data
  with open(CO2_DATA_FILE + file_div + '.txt', mode='a') as f:
     f.write('\n' + data)

def main():
   args = sys.argv
   file_div=''
   if(args[1] == 'minutes'):
      file_div='1m'
   elif(args[1] == 'hour'):
      file_div='1h'
   else:
    print('Args Error!!')

#  while 1:
   subprocess.call(stop_getty, stdout=subprocess.PIPE, shell=True)
   now = datetime.datetime.now()
   now_ymdhms = "{0:%Y/%m/%d %H:%M:%S}".format(now)

   value = mh_z19()
   co2 = value["co2"]

   data = now_ymdhms + "," + str(co2)
   write_data(file_div,data)

   #if( co2 > 400):
   #  sound(5)
   subprocess.call(start_getty, stdout=subprocess.PIPE, shell=True)
#    sleep(5)

if __name__ == '__main__':
   main()

