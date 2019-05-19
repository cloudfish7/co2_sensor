# http://eleparts.co.kr/data/design/product_file/SENSOR/gas/MH-Z19_CO2%20Manual%20V2.pdf
import sys
import serial
import time
import subprocess
import getrpimodel
import datetime
from time import sleep 
import RPi.GPIO as GPIO

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


CO2_DATA_FILE='/opt/co2log/co2data_'

if getrpimodel.model() == "3 Model B":
  serial_dev = '/dev/ttyS0'
  stop_getty = 'sudo systemctl stop serial-getty@ttyS0.service'
  start_getty = 'sudo systemctl start serial-getty@ttyS0.service'
else:
  serial_dev = '/dev/ttyAMA0'
  stop_getty = 'sudo systemctl stop serial-getty@ttyAMA0.service'
  start_getty = 'sudo systemctl start serial-getty@ttyAMA0.service'


def display(data):
   # Raspberry Pi pin configuration:
   RST = None     # on the PiOLED this pin isnt used
   DC = 23
   SPI_PORT = 0
   SPI_DEVICE = 0
   disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

   disp.begin()
   
   # Clear display.
   disp.clear()
   disp.display()
   width = disp.width
   height = disp.height
   image = Image.new('1', (width, height))
   
   # Get drawing object to draw on image.
   draw = ImageDraw.Draw(image)

   # Draw a black filled box to clear the image.
   draw.rectangle((0,0,width,height), outline=0, fill=0)
   
   # Draw some shapes.
   # First define some constants to allow easy resizing of shapes.
   padding = -2
   top = padding
   bottom = height-padding
   # Move left to right keeping track of the current x position for drawing shapes.
   x = 0

   # Load default font.
   #font_ip = ImageFont.load_default()

   #font_ttf = "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf"
   font_ttf = "/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf"
   font_co2 = ImageFont.truetype(font_ttf, 20)
   font_ip = ImageFont.truetype(font_ttf, 10)

   # Draw a black filled box to clear the image.
   draw.rectangle((0,0,width,height), outline=0, fill=0)
   
   cmd = "hostname -I | cut -d\' \' -f1"
   IP = subprocess.check_output(cmd, shell = True )
  
   # Write two lines of text.
   draw.text((x, top+2),      "CO2:" + str(data) + "ppm" , font=font_co2, fill=255)
   draw.text((x, top+25),     "IP: " + str(IP),  font=font_ip, fill=255)
  
   # Display image.
   disp.image(image)
   disp.display()

def alarm():

   SOUNDER = 21
   GPIO.setmode(GPIO.BCM)
   GPIO.setup(SOUNDER, GPIO.OUT, initial = GPIO.LOW)
   
   p = GPIO.PWM(SOUNDER, 6500)
   p.start(50)
   time.sleep(0.5)
   p.stop()

   GPIO.cleanup()

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
    print(len(s))
    print(s)
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

   # Get Data
   value = mh_z19()
   co2 = value["co2"]

   data = now_ymdhms + "," + str(co2)
   write_data(file_div,data)

   #check
   if( co2 > 900):
       alarm()

   subprocess.call(start_getty, stdout=subprocess.PIPE, shell=True)

   display(co2)

if __name__ == '__main__':
   main()

