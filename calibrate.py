import serial
import time
import subprocess
#import slider_utils as slider
import getrpimodel

if getrpimodel.model() == "3 Model B":
  serial_dev = '/dev/ttyS0'
  stop_getty = 'sudo systemctl stop serial-getty@ttyS0.service'
  start_getty = 'sudo systemctl start serial-getty@ttyS0.service'
else:
  serial_dev = '/dev/ttyAMA0'
  stop_getty = 'sudo systemctl stop serial-getty@ttyAMA0.service'
  start_getty = 'sudo systemctl start serial-getty@ttyAMA0.service'


def calibrateZeroPoing():
  try:
    ser = serial.Serial(serial_dev,
                        baudrate=9600,
                        bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        timeout=1.0)
    while 1:
      result=ser.write("\xff\x01\x87\x00\x00\x00\x00\x00\x78")
      break
  except IOError:
    print IOError
    #slider.io_error_report()
  except:
    print "Unknown Error"
    #slider.unknown_error_report()

if __name__ == '__main__':
  calibrateZeroPoing()
  print "caribration zero point done."

