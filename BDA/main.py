from apds9960.const import *
from apds9960 import APDS9960
import RPi.GPIO as GPIO
import smbus
from time import sleep
import math
import time
import datetime
from demo_opts import get_device
from luma.core.render import canvas
from KY040.KY040 import KY040
import os
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from luma.core.interface.serial import spi
from luma.oled.device import ssd1351
import sys
from TTTField import TTTField
import requests
import json
from flask import Flask,make_response
import configparser
from urllib.request import urlopen
import xmltodict 
from requests.structures import CaseInsensitiveDict
import imaplib
import email
from email.header import decode_header
import webbrowser
import Adafruit_DHT


app = Flask(__name__)

# Sensortype and GPIO for the temperaturesensor
sensor = Adafruit_DHT.DHT22
pin = '4'

# Initialization of the display
serial= spi(device=0, port=0)
device = ssd1351(serial_interface=serial, width=128, height=128, rotate=2, framebuffer=None, h_offset=0, v_offset=0, bgr=True)



# URL to the tomtom api
apiURL      = "https://api.tomtom.com/routing/1/calculateRoute/"
# apiKey
apiKey      = "insert your created TomTom API key"





# Variables for the volume app
muted = False
inVolumeApp = False
pressedCounter = 0
volumeCounter = 20



# this is used for the app menue, to keep track when a new app should be displayed and which
oldState = True 
counterPictures = 0 

# this is used for TicTacToe to keep track of what we should display
counterField = 0 
oldField = True 
xMarker = True 
movedField = True 
counterMarked = 0

# Variables used to keep track what we should display in each app
weatherCounter = 0
weatherOldState = True
trafficCounter = 0
trafficOldState = True
coronaCounter = 0
coronaOldState = True
mailCounter = 0
mailOldState = True
jokeCounter = 0
jokeOldState = True
calendarCounter = 0
calendarOldState = True
trainCounter = 0
trainOldState = True

# account credentials
username = "aliuetest99@gmail.com"
password = "#!test!#"

# Initialization of the motion sensor , every motion we use, we use inverted since our motion sensor is mounted on its head on our BDA, so left is right etc.
port = 1
bus = smbus.SMBus(port)
apds = APDS9960(bus)

# fields for our TicTacToe App
Field1 = TTTField(1,1,1,False,"")
Field2 = TTTField(41,1,2,False,"")
Field3 = TTTField(81,1,3,False,"")
Field4 = TTTField(1,41,4,False,"")
Field5 = TTTField(41,41,5,False,"")
Field6 = TTTField(81,41,6,False,"")
Field7 = TTTField(1,81,7,False,"")
Field8 = TTTField(41,81,8,False,"")
Field9 = TTTField(81,81,9,False,"")

# our Image Variable which we use everywhere with different pictures
frameSize = (128,128)
im = Image.new('RGB', (frameSize), 'black')


# pictures for the applicationss
def pictureOne():
    global im
    im = Image.open("/home/pi/BDA/zimmertemperatur.jpg")
    device.display(im)
def pictureTwo():
    global im
    im = Image.open("/home/pi/BDA/calendar.jpg")
    device.display(im)
def pictureThree():
    global im
    im = Image.open("/home/pi/BDA/mailed.jpg")
    device.display(im)
def pictureFour():
    global im
    im = Image.open("/home/pi/BDA/cars.jpg")
    device.display(im)
def pictureFive():
    global im
    im = Image.open("/home/pi/BDA/TTTicon.jpg")
    device.display(im)
def pictureSix():
    global im
    im = Image.open("/home/pi/BDA/computer.jpg")
    device.display(im)
def pictureSeven():
    global im
    im = Image.open("/home/pi/BDA/train.jpg")
    device.display(im)
def pictureEight():
    global im
    im = Image.open("/home/pi/BDA/weather.jpg")
    device.display(im)
def pictureNine():
    global im
    im = Image.open("/home/pi/BDA/corona.jpg")
    device.display(im)
def pictureTen():
    global im
    im = Image.open("/home/pi/BDA/jokeApp.jpg")
    device.display(im)

# pictures for the weatherapp
def weatherClearSky():
    global im
    im = Image.open("/home/pi/BDA/weatherClearSky.jpg")
def weatherBrokenClouds():
    global im
    im = Image.open("/home/pi/BDA/weatherBrokenClouds.jpg")
def weatherFewClouds():
    global im
    im = Image.open("/home/pi/BDA/weatherFewClouds.jpg")
def weatherMist():
    global im
    im = Image.open("/home/pi/BDA/weatherMist.jpg")
def weatherRain():
    global im
    im = Image.open("/home/pi/BDA/weatherRain.jpg")
def weatherScatteredClouds():
    global im
    im = Image.open("/home/pi/BDA/weatherScatteredClouds.jpg")
def weatherShowerRain():
    global im
    im = Image.open("/home/pi/BDA/weatherShowerRain.jpg")
def weatherSnow():
    global im
    im = Image.open("/home/pi/BDA/weatherSnow.jpg")
def weatherThunderstorm():
    global im
    im = Image.open("/home/pi/BDA/weatherThunderstorm.jpg")


def switchPressed(status): # everytime you press the button of the Rotary Encoder this will happen, in our case two times because it sends a signal when going down and going up, so we needed to account for that
     global counterPictures
     global im
     global muted 
     global pressedCounter
     global volumeCounter 
     pressedCounter += 1 # used to catch the second signal when the button is going up
     xCoordinate = 6 # is used to dynamic create the volume display. it counts in 6 pixel increments to move the rectangles we create
   
     if (inVolumeApp): # is only accessed when we are in the volume app, since it can always listen for interrupts we need to stop it from potentialy doing things when not in the right app
      if (muted and pressedCounter == 1):
       url = "#your-ip-adress/volume/unmute" # your target needs to host the EP which you can find under "Volume App Code for the PC" in this Repo 
       response = requests.get(url)                     # this url is the app adress of that host with the path to unmute the host, below are the paths to mute and for the volume control
       muted = False
       im = Image.new('RGB', (frameSize), 'black') # rest is used to create the volume display 
       draw = ImageDraw.Draw(im)    
       font = ImageFont.truetype("FreeMonoBold.ttf", 10)
       draw.text((15,5), "Volume Controller" , fill="white", font=font)
       font = ImageFont.truetype("FreeMonoBold.ttf", 15)
       draw.text((55,55), str(volumeCounter*5) , fill="white", font=font)
       draw.text((35,80), "Unmuted" , fill="white", font=font)
       draw.rectangle([(5,25),(125,45)],outline="white",fill= None,width=1)
       for x in range(volumeCounter):    
        draw.rectangle([(xCoordinate,26),(xCoordinate+5,44)],outline="white",fill= "red",width=1)
        xCoordinate += 6 
       device.display(im)            
      elif (not muted and pressedCounter == 1):
       url = "#your-ip-adress/volume/mute"
       response = requests.get(url)
       muted = True  
       im = Image.new('RGB', (frameSize), 'black')
       draw = ImageDraw.Draw(im)    
       font = ImageFont.truetype("FreeMonoBold.ttf", 10)
       draw.text((15,5), "Volume Controller" , fill="white", font=font)
       font = ImageFont.truetype("FreeMonoBold.ttf", 15)
       draw.text((55,55), str(volumeCounter*5) , fill="white", font=font)
       draw.text((35,80), "Muted" , fill="white", font=font)
       draw.rectangle([(5,25),(125,45)],outline="white",fill= None,width=1)
       for x in range(volumeCounter):    
        draw.rectangle([(xCoordinate,26),(xCoordinate+5,44)],outline="white",fill= "red",width=1) 
        xCoordinate += 6        
       device.display(im)       
     if ( pressedCounter == 2): # is used to catch the second signal when the button is going up
       pressedCounter = 0
     if counterPictures == 5: # if we are in the TicTacToe app this button marks instead the fields with X and O
      if status == 13:
        markingTTT()

def rotaryChange(direction): # everytime you rotate the Rotary Encoder this will be accessed
  global im
  global volumeCounter
  global muted
  xCoordinate = 6 # same as in switchedPressed
  if (inVolumeApp): # is only accessed when we are in the volume app, since it can always listen for interrupts we need to stop it from potentialy doing things when not in the right app
    im = Image.new('RGB', (frameSize), 'black')
    draw = ImageDraw.Draw(im)    
    font = ImageFont.truetype("FreeMonoBold.ttf", 10)
    draw.text((15,5), "Volume Controller" , fill="white", font=font)
    font = ImageFont.truetype("FreeMonoBold.ttf", 15)
    if muted:
     draw.text((35,80), "Muted" , fill="white", font=font)
    else :
     draw.text((35,80), "Unmuted" , fill="white", font=font)   
    draw.rectangle([(5,25),(125,45)],outline="white",fill= None,width=1)    
    if ( direction == 0):
      url = "#your-ip-adress/volume/down" # same as above, only this is the url to regulate the volume down in 5% steps
      response = requests.get(url) 
      if (volumeCounter > 0):
       volumeCounter -= 1
      draw.text((55,55), str(volumeCounter*5) , fill="white", font=font)
      if (volumeCounter != 0):
       for x in range(volumeCounter):    
        draw.rectangle([(xCoordinate,26),(xCoordinate+5,44)],outline="white",fill= "red",width=1)     
        xCoordinate += 6 
      device.display(im)        
      sleep(0.2)
    if ( direction == 1):
      url = "#your-ip-adress/volume/up" # same as above, only this is the url to regulate the volume up in 5% steps
      response = requests.get(url)      
      if (volumeCounter < 20):
       volumeCounter += 1
      else : 
        volumeCounter = 20 
      draw.text((55,55), str(volumeCounter*5) , fill="white", font=font)        
      for x in range(volumeCounter):    
        draw.rectangle([(xCoordinate,26),(xCoordinate+5,44)],outline="white",fill= "red",width=1)     
        xCoordinate += 6 
      device.display(im)  
      sleep(0.2)     
 

def makeFieldTTT():
    global Field1,Field2,Field3,Field4,Field5,Field6,Field7,Field8,Field9
    global im
    im = Field1.whiteField(im)
    im = Field2.whiteField(im)
    im = Field3.whiteField(im)
    im = Field4.whiteField(im)
    im = Field5.whiteField(im)
    im = Field6.whiteField(im)
    im = Field7.whiteField(im)
    im = Field8.whiteField(im)
    im = Field9.whiteField(im)
    device.display(im)

def resetTTT():
    global counterMarked
    global Field1,Field2,Field3,Field4,Field5,Field6,Field7,Field8,Field9
    Field1 = TTTField(1,1,1,False,"")
    Field2 = TTTField(41,1,2,False,"")
    Field3 = TTTField(81,1,3,False,"")
    Field4 = TTTField(1,41,4,False,"")
    Field5 = TTTField(41,41,5,False,"")
    Field6 = TTTField(81,41,6,False,"")
    Field7 = TTTField(1,81,7,False,"")
    Field8 = TTTField(41,81,8,False,"")
    Field9 = TTTField(81,81,9,False,"")
    counterMarked = 0

def markingTTT(): 
       global im
       global xMarker
       global movedField
       global counterField
       global counterMarked
       # we hardcoded this step to be able to see each marked field
       if counterField == 0:
        if xMarker == True and movedField == True and Field1.marked == False:
         im = Field1.setMarker("X",im)
         counterMarked += 1
         xMarker = False
         movedField = False
        elif xMarker == False and movedField == True and Field1.marked == False:
         im = Field1.setMarker("O",im)
         counterMarked += 1
         xMarker = True
         movedField = False
       elif counterField == 1:
        if xMarker == True and movedField == True and Field2.marked == False:
         im = Field2.setMarker("X",im)
         counterMarked += 1
         xMarker = False
         movedField = False
        elif xMarker == False and movedField == True and Field2.marked == False:
         im = Field2.setMarker("O",im)
         counterMarked += 1
         xMarker = True
         movedField = False
       elif counterField == 2:
        if xMarker == True and movedField == True and Field3.marked == False:
         im = Field3.setMarker("X",im)
         counterMarked += 1
         xMarker = False
         movedField = False
        elif xMarker == False and movedField == True and Field3.marked == False:
         im = Field3.setMarker("O",im)
         counterMarked += 1
         xMarker = True
         movedField = False
       elif counterField == 3:
        if xMarker == True and movedField == True and Field4.marked == False:
         im = Field4.setMarker("X",im)
         counterMarked += 1
         xMarker = False
         movedField = False
        elif xMarker == False and movedField == True and Field4.marked == False:
         im = Field4.setMarker("O",im)
         counterMarked += 1
         xMarker = True
         movedField = False
       elif counterField == 4:
        if xMarker == True and movedField == True and Field5.marked == False:
         im = Field5.setMarker("X",im)
         counterMarked += 1
         xMarker = False
         movedField = False
        elif xMarker == False and movedField == True and Field5.marked == False:
         im = Field5.setMarker("O",im)
         counterMarked += 1
         xMarker = True
         movedField = False
       elif counterField == 5:
        if xMarker == True and movedField == True and Field6.marked == False:
         im = Field6.setMarker("X",im)
         counterMarked += 1
         xMarker = False
         movedField = False
        elif xMarker == False and movedField == True and Field6.marked == False:
         im = Field6.setMarker("O",im)
         counterMarked += 1
         xMarker = True
         movedField = False
       elif counterField == 6:
        if xMarker == True and movedField == True and Field7.marked == False:
         im = Field7.setMarker("X",im)
         counterMarked += 1
         xMarker = False
         movedField = False
        elif xMarker == False and movedField == True and Field7.marked == False:
         im = Field7.setMarker("O",im)
         counterMarked += 1
         xMarker = True
         movedField = False
       elif counterField == 7:
        if xMarker == True and movedField == True and Field8.marked == False:
         im = Field8.setMarker("X",im)
         counterMarked += 1
         xMarker = False
         movedField = False
        elif xMarker == False and movedField == True and Field8.marked == False:
         im = Field8.setMarker("O",im)
         counterMarked += 1
         xMarker = True
         movedField = False
       elif counterField == 8:
        if xMarker == True and movedField == True and Field9.marked == False:
         im = Field9.setMarker("X",im)
         counterMarked += 1
         xMarker = False
         movedField = False
        elif xMarker == False and movedField == True and Field9.marked == False:
         im = Field9.setMarker("O",im)
         counterMarked += 1
         xMarker = True
         movedField = False

def gameTTT():
    # is used everywhere to be able to look into terminal to see what move the movement sensor registered
    dirs = { 
    APDS9960_DIR_NONE: "none",
    APDS9960_DIR_LEFT: "left",
    APDS9960_DIR_RIGHT: "right",
    APDS9960_DIR_UP: "up",
    APDS9960_DIR_DOWN: "down",
    APDS9960_DIR_NEAR: "near",
    APDS9960_DIR_FAR: "far",
 }
    global im
    global counterField
    global oldField
    global Field1,Field2,Field3,Field4,Field5,Field6,Field7,Field8,Field9
    global appLeft
    global movedField
    im = Image.new('RGB', (frameSize), 'black')
    makeFieldTTT()

    while True:
      if apds.isGestureAvailable():  # when the movement sensor registers a move it gets set to  true 
         motion = apds.readGesture() # returns integers, 0 = none, 1 = left, 2 = right , 3 = up, 4 = down, 5 = near , 6 = far . 
         print (motion)              # every motion we use is used inverted since our motion sensor is mounted on its head on our BDA, so left is right etc.
         print ("Gesture={}".format(dirs.get(motion, "unknown")))
         if motion == 2:             # we hard code each field that is to be marked and we also hard coded when the game is over via a win or a tie 
          movedField = True               
          if counterField > 0:
           counterField -= 1
           oldField = False
          else:
           counterField = 8
           oldField = False
         elif motion == 1:
          movedField = True
          if counterField < 8:
           counterField += 1
           oldField = False
          else:
           counterField = 0
           oldField = False
         elif motion == 4:
          movedField = True
          if counterField == 0:
           counterField = 6
           oldField = False
          elif counterField == 1:
           counterField = 7
           oldField = False
          elif counterField == 2:
           counterField = 8
           oldField = False
          elif counterField == 3:
            counterField = 0
            oldField = False
          elif counterField == 4:
            counterField = 1
            oldField = False
          elif counterField == 5:
            counterField = 2
            oldField = False
          elif counterField == 6:
            counterField = 3
            oldField = False
          elif counterField == 7:
            counterField = 4
            oldField = False
          elif counterField == 8:
            counterField = 5
            oldField = False
         elif motion == 3:
          movedField = True
          if counterField == 0:
           counterField = 3
           oldField = False
          elif counterField == 1:
           counterField = 4
           oldField = False
          elif counterField == 2:
           counterField = 5
           oldField = False
          elif counterField == 3:
            counterField = 6
            oldField = False
          elif counterField == 4:
            counterField = 7
            oldField = False
          elif counterField == 5:
            counterField = 8
            oldField = False
          elif counterField == 6:
            counterField = 0
            oldField = False
          elif counterField == 7:
            counterField = 1
            oldField = False
          elif counterField == 8:
            counterField = 2
            oldField = False
      if oldField == False:
       if counterField == 0:
        Field2.whiteField(im)
        Field4.whiteField(im)
        Field7.whiteField(im)
        Field9.whiteField(im)
        Field1.redField(im)
       elif counterField == 1:
        Field1.whiteField(im)
        Field3.whiteField(im)
        Field5.whiteField(im)
        Field8.whiteField(im)
        Field2.redField(im)
       elif counterField == 2:
        Field2.whiteField(im)
        Field4.whiteField(im)
        Field6.whiteField(im)
        Field9.whiteField(im)
        Field3.redField(im)
       elif counterField == 3:
        Field3.whiteField(im)
        Field5.whiteField(im)
        Field1.whiteField(im)
        Field7.whiteField(im)
        Field4.redField(im)
       elif counterField == 4:
        Field4.whiteField(im)
        Field6.whiteField(im)
        Field2.whiteField(im)
        Field8.whiteField(im)
        Field5.redField(im)
       elif counterField == 5:
        Field5.whiteField(im)
        Field7.whiteField(im)
        Field3.whiteField(im)
        Field9.whiteField(im)
        Field6.redField(im)
       elif counterField == 6:
        Field4.whiteField(im)
        Field6.whiteField(im)
        Field8.whiteField(im)
        Field1.whiteField(im)
        Field7.redField(im)
       elif counterField == 7:
        Field5.whiteField(im)
        Field7.whiteField(im)
        Field9.whiteField(im)
        Field2.whiteField(im)
        Field8.redField(im)
       elif counterField == 8:
        Field1.whiteField(im)
        Field3.whiteField(im)
        Field6.whiteField(im)
        Field8.whiteField(im)
        Field9.redField(im)
       oldField = True
      device.display(im)
      Field1Winner = getattr(Field1, 'winner')
      Field2Winner = getattr(Field2, 'winner')
      Field3Winner = getattr(Field3, 'winner')
      Field4Winner = getattr(Field4, 'winner')
      Field5Winner = getattr(Field5, 'winner')
      Field6Winner = getattr(Field6, 'winner')
      Field7Winner = getattr(Field7, 'winner')
      Field8Winner = getattr(Field8, 'winner')
      Field9Winner = getattr(Field9, 'winner')
      if Field1Winner == "X" and Field2Winner == "X" and Field3Winner == "X":
       im = Image.open("/home/pi/BDA/trophyX.jpg")
       device.display(im)
       sleep (3)
       resetTTT()
       return
      elif Field4Winner == "X" and Field5Winner == "X" and Field6Winner == "X":
       im = Image.open("/home/pi/BDA/trophyX.jpg")
       device.display(im)
       sleep (3)
       resetTTT()
       return
      elif Field7Winner == "X" and Field8Winner == "X" and Field9Winner == "X":
       im = Image.open("/home/pi/BDA/trophyX.jpg")
       device.display(im)
       sleep (3)
       resetTTT()
       return
      elif Field1Winner == "X" and Field4Winner == "X" and Field7Winner == "X":
       im = Image.open("/home/pi/BDA/trophyX.jpg")
       device.display(im)
       sleep (3)
       resetTTT()
       return
      elif Field2Winner == "X" and Field5Winner == "X" and Field8Winner == "X":
       im = Image.open("/home/pi/BDA/trophyX.jpg")
       device.display(im)
       sleep (3)
       resetTTT()
       return
      elif Field3Winner == "X" and Field6Winner == "X" and Field9Winner == "X":
       im = Image.open("/home/pi/BDA/trophyX.jpg")
       device.display(im)
       sleep (3)
       resetTTT()
       return
      elif Field1Winner == "X" and Field5Winner == "X" and Field9Winner == "X":
       im = Image.open("/home/pi/BDA/trophyX.jpg")
       device.display(im)
       sleep (3)
       resetTTT()
       return
      elif Field3Winner == "X" and Field5Winner == "X" and Field7Winner == "X":
       im = Image.open("/home/pi/BDA/trophyX.jpg")
       device.display(im)
       sleep (3)
       resetTTT()
       return
      elif Field1Winner == "O" and Field2Winner == "O" and Field3Winner == "O":
       im = Image.open("/home/pi/BDA/trophyO.jpg")
       device.display(im)
       sleep (3)
       resetTTT()
       return
      elif Field4Winner == "O" and Field5Winner == "O" and Field6Winner == "O":
       im = Image.open("/home/pi/BDA/trophyO.jpg")
       device.display(im)
       sleep (3)
       resetTTT()
       return
      elif Field7Winner == "O" and Field8Winner == "O" and Field9Winner == "O":
       im = Image.open("/home/pi/BDA/trophyO.jpg")
       device.display(im)
       sleep (3)
       resetTTT()
       return
      elif Field1Winner == "O" and Field4Winner == "O" and Field7Winner == "O":
       im = Image.open("/home/pi/BDA/trophyO.jpg")
       device.display(im)
       sleep (3)
       resetTTT()
       return
      elif Field2Winner == "O" and Field5Winner == "O" and Field8Winner == "O":
       resetTTT()
       im = Image.open("/home/pi/BDA/trophyO.jpg")
       device.display(im)
       sleep (3)
       return
      elif Field3Winner == "O" and Field6Winner == "O" and Field9Winner == "O":
       im = Image.open("/home/pi/BDA/trophyO.jpg")
       device.display(im)
       sleep (3)
       resetTTT()
       return
      elif Field1Winner == "O" and Field5Winner == "O" and Field9Winner == "O":
       im = Image.open("/home/pi/BDA/trophyO.jpg")
       device.display(im)
       sleep (3)
       resetTTT()
       return
      elif Field3Winner == "O" and Field5Winner == "O" and Field7Winner == "O":
       im = Image.open("/home/pi/BDA/trophyO.jpg")
       device.display(im)
       sleep (3)
       resetTTT()
      elif counterMarked == 9:
       im = Image.open("/home/pi/BDA/tie.jpg")
       device.display(im)
       sleep (3)
       resetTTT()
       return

# we used the clock from the examples which come with the tutorial we linked with the display (https://www.bluetin.io/displays/oled-display-raspberry-pi-ssd1331/)
# we only integreted the motion sensor into the clock to move through it to the next app
def posn(angle, arm_length):
    dx = int(math.cos(math.radians(angle)) * arm_length)
    dy = int(math.sin(math.radians(angle)) * arm_length)
    return (dx, dy)

def clock():
 dirs = {
    APDS9960_DIR_NONE: "none",
    APDS9960_DIR_LEFT: "left",
    APDS9960_DIR_RIGHT: "right",
    APDS9960_DIR_UP: "up",
    APDS9960_DIR_DOWN: "down",
    APDS9960_DIR_NEAR: "near",
    APDS9960_DIR_FAR: "far",
 }
 today_last_time = "Unknown"
 global counterPictures
 global oldState
 global im
 while True:
        if apds.isGestureAvailable():
         motion = apds.readGesture()
         print (motion)
         print ("Gesture={}".format(dirs.get(motion, "unknown")))
         if motion == 2:  # if we swipe to the right, which is left as above mentioned in our case, we leave the clock with this code and go to the next app
          im = Image.open("/home/pi/BDA/jokeApp.jpg")
          draw = ImageDraw.Draw(im)
          device.display(im)
          counterPictures = 10
          oldState = True
          return
         if motion == 1:  # if we swipe to the left, which is right as above mentioned in our case, we leave the clock with this code and go to the next app
          im = Image.open("/home/pi/BDA/zimmertemperatur.jpg")
          draw = ImageDraw.Draw(im)
          device.display(im)
          counterPictures = 1
          oldState = True
          return
        now = datetime.datetime.now()
        today_date = now.strftime("%d %b %y")
        today_time = now.strftime("%H:%M:%S")
        if today_time != today_last_time:
            today_last_time = today_time
            with canvas(device) as draw:
                now = datetime.datetime.now()
                today_date = now.strftime("%d %b %y")

                margin = 4

                cx = 30
                cy = min(device.height, 64) / 2

                left = cx - cy
                right = cx + cy

                hrs_angle = 270 + (30 * (now.hour + (now.minute / 60.0)))
                hrs = posn(hrs_angle, cy - margin - 7)

                min_angle = 270 + (6 * now.minute)
                mins = posn(min_angle, cy - margin - 2)

                sec_angle = 270 + (6 * now.second)
                secs = posn(sec_angle, cy - margin - 2)

                draw.ellipse((left + margin, margin, right - margin, min(device.height, 64) - margin), outline="white")
                draw.line((cx, cy, cx + hrs[0], cy + hrs[1]), fill="white")
                draw.line((cx, cy, cx + mins[0], cy + mins[1]), fill="white")
                draw.line((cx, cy, cx + secs[0], cy + secs[1]), fill="red")
                draw.ellipse((cx - 2, cy - 2, cx + 2, cy + 2), fill="white", outline="white")
                draw.text((2 * (cx + margin), cy - 8), today_date, fill="yellow")
                draw.text((2 * (cx + margin), cy), today_time, fill="yellow")
        time.sleep(0.1)


@app.route("/weather/<name>/")
def weather(name):
   # switcher for the images of the weathericons
    switcher = {
   "01": weatherClearSky,
   "02": weatherFewClouds,
   "03": weatherScatteredClouds,
   "04": weatherBrokenClouds,
   "09": weatherShowerRain,
   "10": weatherRain,
   "11": weatherThunderstorm,
   "13": weatherSnow,
   "50": weatherMist
}
    global im
    # we use the openweathermap-api for more details that you can also check out in their documentation 
    # you can genereate your own api_key on their website
    api_key = # you can paste your created api_key here
    url = "https://api.openweathermap.org/data/2.5/weather?q=%s&units=metric&appid=%s" %(name,api_key)
    # here we use the normal flask procedure
    response = requests.get(url)
    data = response.json()
    if data["cod"] != "404":
        # we extract the information we want from the JSON-Object
        y = data["main"]
        z = data["weather"]
        cityName = "City: " + str(data["name"])
        weather_description =  str(z[0]["description"])
        weather_icon =  str(z[0]["icon"])
        weather_icon = weather_icon.replace("d","")
        weather_icon = weather_icon.replace("n","")
        current_temperature = "Temperature: " + str (y["temp"]) + " °C"
        func = switcher.get(weather_icon, lambda: "01")
        func()
        font = ImageFont.truetype("FreeMonoBold.ttf", 10)
        draw = ImageDraw.Draw(im)
        draw.text((0,64), cityName , fill="white", font=font)
        draw.text((0,84), current_temperature , fill="white", font=font)
        draw.text((0,104), "Weather Description:" , fill="white", font=font)
        draw.text((0,114), weather_description , fill="white", font=font)
    return 

def weatherApp():
    dirs = {
    APDS9960_DIR_NONE: "none",
    APDS9960_DIR_LEFT: "left",
    APDS9960_DIR_RIGHT: "right",
    APDS9960_DIR_UP: "up",
    APDS9960_DIR_DOWN: "down",
    APDS9960_DIR_NEAR: "near",
    APDS9960_DIR_FAR: "far",
 }
    global counterPictures
    global weatherCounter
    global weatherOldState
    global im
    
    # these variables are used in the apps to generate the menu list
    yHeight = 5 
    counterRedWhite = 0
    
    im = Image.new('RGB', (frameSize), 'black')
    font = ImageFont.truetype("FreeMonoBold.ttf", 15)
    draw = ImageDraw.Draw(im)
    
    # we generate our menu from this list 
    menu = []
    menu.append("Köln")
    menu.append("Gummersbach")
    menu.append("Kierspe")
    menu.append("Bonn")
    menu.append("Dortmund")
    menu.append("Düsseldorf")
    menu.append("Leverkusen")
    menu.append("Hagen")
    weatherOldState = False
    while True:
     if apds.isGestureAvailable():
      motion = apds.readGesture()
      print (motion)
      print ("Gesture={}".format(dirs.get(motion, "unknown")))
      # motion 3 and 4 are used to navigate through the menu where the citys are listed, both motions are again used in reverse as written in the beginning
      if motion == 4:
       if weatherCounter > 0:
        weatherCounter -= 1
        weatherOldState = False
       else:
        weatherCounter = 7
        weatherOldState = False
      elif motion == 3:
       if weatherCounter < 7:
        weatherCounter += 1
        weatherOldState = False
       else:
        weatherCounter = 0
        weatherOldState = False
      # when you swipe to the "right" you get the weatherinformation of the current red marked city 
      elif motion == 1:
        # the depiction methods take care of displaying the information of the selected menu item
        weatherDepiction()
        weatherOldState = False
      # when you swipe to the "left" you leave the app and you are again in the app menu
      elif motion == 2:
        return
     # everytime you swipe up and down through the menu we generate a new menu with the current marked menuitem 
     if weatherOldState == False:
      im = Image.new('RGB', (frameSize), 'black')
      draw = ImageDraw.Draw(im)
      for menuData in menu:
        if counterRedWhite == weatherCounter:
         draw.text((5,yHeight), menuData , fill="red", font=font)
         yHeight += 15
         counterRedWhite += 1
        else:
         draw.text((5,yHeight), menuData , fill="white", font=font)
         yHeight += 15
         counterRedWhite += 1
     device.display(im)
     weatherOldState = True
     counterRedWhite = 0
     yHeight = 5
     sleep(0.1)

def weatherDepiction():
    dirs = {
    APDS9960_DIR_NONE: "none",
    APDS9960_DIR_LEFT: "left",
    APDS9960_DIR_RIGHT: "right",
    APDS9960_DIR_UP: "up",
    APDS9960_DIR_DOWN: "down",
    APDS9960_DIR_NEAR: "near",
    APDS9960_DIR_FAR: "far",
 }
    switcher = {
   "01": weatherClearSky,
   "02": weatherFewClouds,
   "03": weatherScatteredClouds,
   "04": weatherBrokenClouds,
   "09": weatherShowerRain,
   "10": weatherRain,
   "11": weatherThunderstorm,
   "13": weatherSnow,
   "50": weatherMist
}
    global im
    global weatherCounter
    im = Image.new('RGB', (frameSize), 'black')
    font = ImageFont.truetype("FreeMonoBold.ttf", 10)
    # weatherCounter is used to determine which string is used for the url  
    if weatherCounter == 0:
     weather("Köln,de")
    elif weatherCounter == 1:
     weather("Gummersbach,de")
    elif weatherCounter == 2:
     weather("Kierspe,de")
    elif weatherCounter == 3:
     weather("Bonn,de")
    elif weatherCounter == 4:
     weather("Dortmund,de")
    elif weatherCounter == 5:
     weather("Düsseldorf,de")
    elif weatherCounter == 6:
     weather("Leverkusen,de")
    elif weatherCounter == 7:
     weather("Hagen,de")
    device.display(im)
    # this while-loop is used everywhere to stay with the displayed image until you swipe to the "left" to get to the previous menupoint
    while True:
        if apds.isGestureAvailable():
         motion = apds.readGesture()
         print (motion)
         print ("Gesture={}".format(dirs.get(motion, "unknown")))
         if motion == 2:
          return
         sleep(0.1)


def coronaApp():
    dirs = {
    APDS9960_DIR_NONE: "none",
    APDS9960_DIR_LEFT: "left",
    APDS9960_DIR_RIGHT: "right",
    APDS9960_DIR_UP: "up",
    APDS9960_DIR_DOWN: "down",
    APDS9960_DIR_NEAR: "near",
    APDS9960_DIR_FAR: "far",
 }
    global im
    global coronaCounter
    global coronaOldState
    yHeight = 5
    counterRedWhite = 0
    im = Image.new('RGB', (frameSize), 'black')
    font = ImageFont.truetype("FreeMonoBold.ttf", 15)
    draw = ImageDraw.Draw(im)
    menu = []
    menu.append("Deutschland")
    menu.append("NRW")
    menu.append("Rheinland-P.")
    menu.append("Bayern")
    menu.append("Hessen")
    menu.append("Berlin")
    menu.append("Schleswig-H.")
    menu.append("Niedersachsen")
    coronaOldState = False
    while True:
     if apds.isGestureAvailable():
      motion = apds.readGesture()
      print (motion)
      print ("Gesture={}".format(dirs.get(motion, "unknown")))
      if motion == 4:
       if coronaCounter > 0:
        coronaCounter -= 1
        coronaOldState = False   
       else:
        coronaCounter = 7
        coronaOldState = False
      elif motion == 3:
       if coronaCounter < 7:
        coronaCounter += 1
        coronaOldState = False
       else:
        coronaCounter = 0
        coronaOldState = False
      elif motion == 1:
        coronaDepiction()
        coronaOldState = False
      elif motion == 2:
        return
     if coronaOldState == False:
      im = Image.new('RGB', (frameSize), 'black')
      draw = ImageDraw.Draw(im)
      for menuData in menu:
        if counterRedWhite == coronaCounter:
         draw.text((5,yHeight), menuData , fill="red", font=font)
         yHeight += 15
         counterRedWhite += 1
        else:
         draw.text((5,yHeight), menuData , fill="white", font=font)
         yHeight += 15
         counterRedWhite += 1
     device.display(im)
     coronaOldState = True
     counterRedWhite = 0
     yHeight = 5
     sleep(0.1)

def coronaDepiction():
    dirs = {
    APDS9960_DIR_NONE: "none",
    APDS9960_DIR_LEFT: "left",
    APDS9960_DIR_RIGHT: "right",
    APDS9960_DIR_UP: "up",
    APDS9960_DIR_DOWN: "down",
    APDS9960_DIR_NEAR: "near",
    APDS9960_DIR_FAR: "far",
 }
    global im
    global coronaCounter
    name = ""
    # we use the api of arcgis.com you can follow this german tutorial for more information : https://arcgis.esri.de/nutzung-der-api-des-rki-covid-19-dashboard/
    # AdmUnit chart : https://www.arcgis.com/home/item.html?id=c093fe0ef8fd4707beeb3dc0c02c3381&sublayer=0&view=list&sortOrder=desc&sortField=defaultFSOrder#data
    url = "https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/rki_key_data_v/FeatureServer/0/query?"
    if coronaCounter == 0:
     lk_id = 0 # ID for Germany after the AdmUnit chart
     name = "Deutschland"
    elif coronaCounter == 1:
     lk_id = 5 # ID for NRW after the AdmUnit chart
     name = "NRW"
    elif coronaCounter == 2:
     lk_id = 7 # ID for Rheinland-Pfalz after the AdmUnit chart
     name = "Rheinland-P."
    elif coronaCounter == 3:
     lk_id = 9 # ID for Bayern after the AdmUnit chart
     name = "Bayern"
    elif coronaCounter == 4:
     lk_id = 6 # ID for Hessen after the AdmUnit chart
     name = "Hessen"
    elif coronaCounter == 5:
     lk_id = 7 # ID for Berlin after the AdmUnit chart
     name = "Berlin"
    elif coronaCounter == 6:
     lk_id = 1 # ID for Schleswig-Holstein after the AdmUnit chart
     name = "Schleswig-Holstein"
    elif coronaCounter == 7:
     lk_id = 5 # ID for Niedersachsen after the AdmUnit chart
     name = "Niedersachsen"

    parameter = {
    'referer':'https://www.mywebapp.com',
    'user-agent':'python-requests/2.9.1',
    'where': f'AdmUnitId = {lk_id}', # Which region we recive
    'outFields': '*', # Return of all fields
    'returnGeometry': False, # No Geometry
    'f':'json', # return format is JSON
    'cacheHint': True # Request access over CDN
    }
    result = requests.get(url=url, params=parameter) #Make the request
    resultjson = json.loads(result.text) 


    inz7T = resultjson['features'][0]['attributes']['Inz7T']
    anzAktivNeu = resultjson['features'][0]['attributes']['AnzAktivNeu']
    anzFall7T = resultjson['features'][0]['attributes']['AnzFall7T']
    anzTodesfallNeu = resultjson['features'][0]['attributes']['AnzTodesfallNeu']

    im = Image.new('RGB', (frameSize), 'black')
    font = ImageFont.truetype("FreeMonoBold.ttf", 10)
    draw = ImageDraw.Draw(im)
    draw.text((5,5), name , fill="white", font=font)
    draw.text((5,15), "7 Tage Inzidenz:", fill="white", font=font)
    draw.text((5,25), str(inz7T), fill="white", font=font)
    draw.text((5,35), "Anzahl Akitv Neu:" , fill="white", font=font)
    draw.text((5,45), str(anzAktivNeu) , fill="white", font=font)
    draw.text((5,55), "Fälle 7 Tage:" , fill="white", font=font)
    draw.text((5,65), str(anzFall7T) , fill="white", font=font)
    draw.text((5,75), "Neue Todesfälle:" , fill="white", font=font)
    draw.text((5,85), str(anzTodesfallNeu) , fill="white", font=font)
    device.display(im)
    while True:
        if apds.isGestureAvailable():
         motion = apds.readGesture()
         print (motion)
         print ("Gesture={}".format(dirs.get(motion, "unknown")))
         if motion == 2:
          return
         sleep(0.1)


def trafficjamApp():
    dirs = {
    APDS9960_DIR_NONE: "none",
    APDS9960_DIR_LEFT: "left",
    APDS9960_DIR_RIGHT: "right",
    APDS9960_DIR_UP: "up",
    APDS9960_DIR_DOWN: "down",
    APDS9960_DIR_NEAR: "near",
    APDS9960_DIR_FAR: "far",
 }
    global im
    global trafficCounter
    global trafficOldState
    yHeight = 5
    counterRedWhite = 0
    im = Image.new('RGB', (frameSize), 'black')
    font = ImageFont.truetype("FreeMonoBold.ttf", 15)
    draw = ImageDraw.Draw(im)
    menu = []
    menu.append("Köln")
    menu.append("Gummersbach")
    menu.append("Kierspe")
    menu.append("Bonn")
    menu.append("Dortmund")
    menu.append("Düsseldorf")
    menu.append("Leverkusen")
    menu.append("Hagen")
    trafficOldState = False
    while True:
     if apds.isGestureAvailable():
      motion = apds.readGesture()
      print (motion)
      print ("Gesture={}".format(dirs.get(motion, "unknown")))
      if motion == 4:
       if trafficCounter > 0:
        trafficCounter -= 1
        trafficOldState = False
       else:
        trafficCounter = 7
        trafficOldState = False
      elif motion == 3:
       if trafficCounter < 7:
        trafficCounter += 1
        trafficOldState = False
       else:
        trafficCounter = 0
        trafficOldState = False
      elif motion == 1:
        trafficDepiction()
        trafficOldState = False
      elif motion == 2:
        return
     if trafficOldState == False:
      im = Image.new('RGB', (frameSize), 'black')
      draw = ImageDraw.Draw(im)
      for menuData in menu:
        if counterRedWhite == trafficCounter:
         draw.text((5,yHeight), menuData , fill="red", font=font)
         yHeight += 15
         counterRedWhite += 1
        else:
         draw.text((5,yHeight), menuData , fill="white", font=font)
         yHeight += 15
         counterRedWhite += 1
     device.display(im)
     trafficOldState = True
     counterRedWhite = 0
     yHeight = 5
     sleep(0.1)

def trafficDepiction():
    dirs = {
    APDS9960_DIR_NONE: "none",
    APDS9960_DIR_LEFT: "left",
    APDS9960_DIR_RIGHT: "right",
    APDS9960_DIR_UP: "up",
    APDS9960_DIR_DOWN: "down",
    APDS9960_DIR_NEAR: "near",
    APDS9960_DIR_FAR: "far",
 }
    global im
    global trafficCounter
    global apiURL
    global apiKey

    # each displayable city has its own URL
    # you need to create your own API key on the TomTom API website and paste it into the "your API key" section
    if trafficCounter == 0:
       trafficLink = 'https://api.tomtom.com/traffic/services/5/incidentDetails?bbox=6.77253%2C50.830449%2C7.162028%2C51.084974&fields=%7Bincidents%7Btype%2Cproperties%7Bid%2Cevents%7Bdescription%2Ccode%7D%2CstartTime%2CendTime%2Cfrom%2Cto%2Clength%2Caci%7BprobabilityOfOccurrence%7D%7D%7D%7D&language=de-DE&timeValidityFilter=present&key="your API key"'
    elif trafficCounter == 1:
       trafficLink = 'https://api.tomtom.com/traffic/services/5/incidentDetails?bbox=7.505057%2C51.001856%2C7.627966%2C51.053895&fields=%7Bincidents%7Btype%2Cproperties%7Bid%2Cevents%7Bdescription%2Ccode%7D%2CstartTime%2CendTime%2Cfrom%2Cto%2Clength%2Caci%7BprobabilityOfOccurrence%7D%7D%7D%7D&language=de-DE&timeValidityFilter=present&key="your API key"'
    elif trafficCounter == 2:
       trafficLink = 'https://api.tomtom.com/traffic/services/5/incidentDetails?bbox=7.547244%2C51.08891%2C7.699336%2C51.153558&fields=%7Bincidents%7Btype%2Cproperties%7Bid%2Cevents%7Bdescription%2Ccode%7D%2CstartTime%2CendTime%2Cfrom%2Cto%2Clength%2Caci%7BprobabilityOfOccurrence%7D%7D%7D%7D&language=de-DE&timeValidityFilter=present&key="your API key"'
    elif trafficCounter == 3:
       trafficLink = 'https://api.tomtom.com/traffic/services/5/incidentDetails?bbox=7.030089%2C50.712525%2C7.168791%2C50.770099&fields=%7Bincidents%7Btype%2Cproperties%7Bid%2Cevents%7Bdescription%2Ccode%7D%2CstartTime%2CendTime%2Cfrom%2Cto%2Clength%2Caci%7BprobabilityOfOccurrence%7D%7D%7D%7D&language=de-DE&timeValidityFilter=present&key="your API key"'
    elif trafficCounter == 4:
       trafficLink = 'https://api.tomtom.com/traffic/services/5/incidentDetails?bbox=7.385842%2C51.475385%2C7.561623%2C51.559133&fields=%7Bincidents%7Btype%2Cproperties%7Bid%2Cevents%7Bdescription%2Ccode%7D%2CstartTime%2CendTime%2Cfrom%2Cto%2Clength%2Caci%7BprobabilityOfOccurrence%7D%7D%7D%7D&language=de-DE&timeValidityFilter=present&key="your API key"'
    elif trafficCounter == 5:
       trafficLink = 'https://api.tomtom.com/traffic/services/5/incidentDetails?bbox=6.739505%2C51.209353%2C6.832889%2C51.248911&fields=%7Bincidents%7Btype%2Cproperties%7Bid%2Cevents%7Bdescription%2Ccode%7D%2CstartTime%2CendTime%2Cfrom%2Cto%2Clength%2Caci%7BprobabilityOfOccurrence%7D%7D%7D%7D&language=de-DE&timeValidityFilter=present&key="your API key"'
    elif trafficCounter == 6:
       trafficLink = 'https://api.tomtom.com/traffic/services/5/incidentDetails?bbox=6.948915%2C51.021562%2C7.036805%2C51.052434&fields=%7Bincidents%7Btype%2Cproperties%7Bid%2Cevents%7Bdescription%2Ccode%7D%2CstartTime%2CendTime%2Cfrom%2Cto%2Clength%2Caci%7BprobabilityOfOccurrence%7D%7D%7D%7D&language=de-DE&timeValidityFilter=present&key="your API key"'
    elif trafficCounter == 7:
       trafficLink = 'https://api.tomtom.com/traffic/services/5/incidentDetails?bbox=7.415996%2C51.345218%2C7.526546%2C51.385516&fields=%7Bincidents%7Btype%2Cproperties%7Bid%2Cevents%7Bdescription%2Ccode%7D%2CstartTime%2CendTime%2Cfrom%2Cto%2Clength%2Caci%7BprobabilityOfOccurrence%7D%7D%7D%7D&language=de-DE&timeValidityFilter=present&key="your API key"'        

    # we open the URL and save it as a JSON file
    getData = urlopen(trafficLink).read()
    jsonData = json.loads(getData)
   
    
    try:
      # we filter the JSON file into needed variables
      startTime = jsonData["incidents"][0]["properties"]["startTime"]
      startPoint = jsonData["incidents"][0]["properties"]["from"]
      endPoint = jsonData["incidents"][0]["properties"]["to"]
      description = jsonData["incidents"][0]["properties"]["events"][0]["description"]
      length = jsonData["incidents"][0]["properties"]["length"]
    except:
      # empty incident lists are being intercepted with a error message
      im = Image.new('RGB', (frameSize), 'black')
      font = ImageFont.truetype("FreeMonoBold.ttf", 7)    
      draw = ImageDraw.Draw(im)
      draw.text((5,35), "Aktuell keine Meldungen.", fill="white", font=font)
      device.display(im) 
      sleep(3)
      return  

     
    im = Image.new('RGB', (frameSize), 'black')
    font = ImageFont.truetype("FreeMonoBold.ttf", 10)    
    draw = ImageDraw.Draw(im)
    # we refilter the JSON file and display the variables on the display with the draw.text() function  
    startTime = jsonData["incidents"][0]["properties"]["startTime"]
    startPoint = jsonData["incidents"][0]["properties"]["from"]
    endPoint = jsonData["incidents"][0]["properties"]["to"]
    description = jsonData["incidents"][0]["properties"]["events"][0]["description"]
    length = jsonData["incidents"][0]["properties"]["length"]
    draw.text((5,5), "Startzeit:", fill="white", font=font)
    draw.text((5,15), str(startTime) , fill="white", font=font)
    draw.text((5,25), "Startort:", fill="white", font=font)
    draw.text((5,35), str(startPoint) , fill="white", font=font)
    draw.text((5,45), "Endort:", fill="white", font=font)
    draw.text((5,55), str(endPoint) , fill="white", font=font)
    draw.text((5,65), "Beschreibung:", fill="white", font=font)
    draw.text((5,75), str(description) , fill="white", font=font)
    draw.text((5,85), "Länge:", fill="white", font=font)
    draw.text((5,95), str(length) + " Meter" , fill="white", font=font)
    device.display(im)
    while True:
        if apds.isGestureAvailable():
         motion = apds.readGesture()
         print (motion)
         print ("Gesture={}".format(dirs.get(motion, "unknown")))
         if motion == 2:
          return
         sleep(0.1)


@app.route("/bahn")
def trainApp ():
    dirs = {
    APDS9960_DIR_NONE: "none",
    APDS9960_DIR_LEFT: "left",
    APDS9960_DIR_RIGHT: "right",
    APDS9960_DIR_UP: "up",
    APDS9960_DIR_DOWN: "down",
    APDS9960_DIR_NEAR: "near",
    APDS9960_DIR_FAR: "far",
 }
    global im
    global trainCounter
    global trainOldState
    yHeight = 5
    counterRedWhite = 0
    im = Image.new('RGB', (frameSize), 'black')
    font = ImageFont.truetype("FreeMonoBold.ttf", 10)
    draw = ImageDraw.Draw(im)
    menu = []
    menu.append("Köln Messe Deutz")
    menu.append("Gummersbach")
    menu.append("Trimbornstraße")
    menu.append("Köln Hbf")
    trainOldState = False
    while True:
     if apds.isGestureAvailable():
      motion = apds.readGesture()
      print (motion)
      print ("Gesture={}".format(dirs.get(motion, "unknown")))
      if motion == 4:
       if trainCounter > 0:
        trainCounter -= 1
        trainOldState = False
       else:
        trainCounter = 3
        trainOldState = False
      elif motion == 3:
       if trainCounter < 3:
        trainCounter += 1
        trainOldState = False
       else:
        trainCounter = 0
        trainOldState = False
      elif motion == 1:
        trainDepiction()
        trainOldState = False
      elif motion == 2:
        return
     if trainOldState == False:
      im = Image.new('RGB', (frameSize), 'black')
      draw = ImageDraw.Draw(im)
      for menuData in menu:
        if counterRedWhite == trainCounter:
         draw.text((5,yHeight), menuData , fill="red", font=font)
         yHeight += 15
         counterRedWhite += 1
        else:
         draw.text((5,yHeight), menuData , fill="white", font=font)
         yHeight += 15
         counterRedWhite += 1
     device.display(im)
     trainOldState = True
     counterRedWhite = 0
     yHeight = 5
     sleep(0.1)

def trainDepiction():
  dirs = {
    APDS9960_DIR_NONE: "none",
    APDS9960_DIR_LEFT: "left",
    APDS9960_DIR_RIGHT: "right",
    APDS9960_DIR_UP: "up",
    APDS9960_DIR_DOWN: "down",
    APDS9960_DIR_NEAR: "near",
    APDS9960_DIR_FAR: "far",
 }
  global im
  global trainCounter
  evaNumber = 0
  yHeight = 5
  yHeightCounter = 0
  idCheck = False
  im = Image.new('RGB', (frameSize), 'black')
  font = ImageFont.truetype("FreeMonoBold.ttf", 10)
  draw = ImageDraw.Draw(im)
  draw.text((5,5), "Train" , fill="white", font=font)
  draw.text((45,5), "PF" , fill="white", font=font)
  draw.text((65,5), "Time" , fill="white", font=font)
  with app.app_context():
    # we use the Timetables - v1 api from the https://developer.deutschebahn.com/ its for the German railwaysystem from the DB
    # on that website you need to create an account to get your own API-Key
    # trainCounter determines which evaNumber we use for the url, each evaNumber correspondes with a train station
    # you can get the evaNumber with the API-Console on the website 
    
    if trainCounter == 0:
      evaNumber = 8003368
    elif trainCounter == 1:
      evaNumber = 8002462
    elif trainCounter == 2:
      evaNumber = 8003320
    elif trainCounter == 3:
      evaNumber = 8000207    

    # we format the date and time to be able to use it for the url
    # it needs to be in the following format :  YYMMDD and HH
    dateAndTime = datetime.datetime.now()
    dateAndTime = str(dateAndTime)
    dateAndTimeArray = dateAndTime.split()

    date = dateAndTimeArray[0].replace("-","")

    date = date[2 :  : ]
    time = dateAndTimeArray[1]
    time = time[:-13:]
    
    
    # here we use the evaNumber, the date and the time                           YYMMDD HH
    url = "https://api.deutschebahn.com/timetables/v1/plan/%s/%s/%s" %(evaNumber,date,time)

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/xml"
    headers["Authorization"] =  # this is used for your own key for example : "Bearer ......Random....."


    resp = requests.get(url, headers=headers)
    
    # here we get a XML response and we need to change it into text to be able to work with it further
    response = make_response(resp.text,200)
    response.mimetype="text/plain"
    
    # here we format the string to be able to work with it further, you are able to format the string to your needs 
    splitedResponse = response.data.split()
    fullReturn = ""
    for element in splitedResponse:
      stringElement = str(element)
      if stringElement.find("id=") != -1:
        idTrain = stringElement
        idTrain = idTrain.replace("b", "")
        idTrain = idTrain.replace("'", "")
        idTrain = idTrain.replace("=", "")
        idTrain = idTrain.replace(">", "")
        idTrain = idTrain.replace("<", "")
        idTrain = idTrain.replace("tl", "")
        idTrain = idTrain.replace('"', "")
        fullReturn = fullReturn + idTrain +" "
      if(stringElement.find("c=")) != -1:
         nameTrain1 = stringElement
         nameTrain1 = nameTrain1.replace("'", "")
         nameTrain1 = nameTrain1.replace("b", "")
         nameTrain1 = nameTrain1.replace("=", "")
         nameTrain1 = nameTrain1.replace('"', "")
         fullReturn = fullReturn + nameTrain1+" "
      if(stringElement.find("pt=")) != -1:
          arrivalTime = stringElement
          arrivalTime = arrivalTime.replace("'", "")
          arrivalTime = arrivalTime.replace("b", "")
          arrivalTime = arrivalTime.replace("=", "")
          arrivalTime = arrivalTime.replace('"', "")
          fullReturn = fullReturn + arrivalTime+" "
      if(stringElement.find("pp=")) != -1:
          arrivalTrack = stringElement
          arrivalTrack = arrivalTrack.replace("'", "")
          arrivalTrack = arrivalTrack.replace("b", "")
          arrivalTrack = arrivalTrack.replace("=", "")
          arrivalTrack = arrivalTrack.replace('"', "")
          fullReturn = fullReturn + arrivalTrack+" "
      if(stringElement.find("l=")) != -1:
          nameTrain2 = stringElement
          nameTrain2 = nameTrain2.replace("'", "")
          nameTrain2 = nameTrain2.replace("b", "")
          nameTrain2 = nameTrain2.replace("=", "")
          nameTrain2 = nameTrain2.replace('"', "")
          fullReturn = fullReturn + nameTrain2+" "

        
    # after replacing everything we dont want, we make a second array from which we can display the informations in the manner we want
    stationDataArray = fullReturn.split() 
    endData = []
    for data in stationDataArray:
      if data.find("id") != -1:
        idCheck = True
        trainName = ""
        plannedArrivalTime = ""
        platform = ""
      elif data.find("c") != -1 and idCheck == True:
        trainName = data
      elif data.find("l") != -1 and idCheck == True:
        data = data.replace("l","")
        trainName = " ".join((trainName,data))
        endData.append(trainName)
        idCheck = False
      elif data.find("pt") != -1 and idCheck == True:
        plannedArrivalTime = data
        endData.append(plannedArrivalTime)
      elif data.find("pp") != -1 and idCheck == True:
        platform = data
        endData.append(platform)
        
    yHeight = 15
    for data in endData:
      yHeightCounter += 1
      if data.find("c") != -1:
        data = data.replace("c","")
        draw.text((5,yHeight), data , fill="white", font=font)
      elif data.find("pp") != -1:
        data = data.replace("pp","")
        draw.text((45,yHeight), data , fill="white", font=font)
      elif data.find("pt") != -1:
        data = data.replace("pt","")
        data = data[-4: :]
        data = data[:2] + ":" + data[2:]
        draw.text((65,yHeight), data , fill="white", font=font)
        
      if yHeightCounter == 3:
        yHeight += 10
        yHeightCounter = 0
        if yHeight > 115:
          break

    device.display(im) 
    while True:
        if apds.isGestureAvailable():
         motion = apds.readGesture()
         print (motion)
         print ("Gesture={}".format(dirs.get(motion, "unknown")))
         if motion == 2:
          return
         sleep(0.1)
    return fullReturn


def cleanMail(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)

def mailApp():
    dirs = {
    APDS9960_DIR_NONE: "none",
    APDS9960_DIR_LEFT: "left",
    APDS9960_DIR_RIGHT: "right",
    APDS9960_DIR_UP: "up",
    APDS9960_DIR_DOWN: "down",
    APDS9960_DIR_NEAR: "near",
    APDS9960_DIR_FAR: "far",
 }
    global username
    global password
    global im
    global mailCounter
    global mailOldState
    # create an IMAP4 class with SSL 
    # Gmail Server
    # IMAP Server (Incoming Messages) 	imap.gmail.com 
    # Outlook.com Server
    # IMAP Server (Incoming Messages) 	imap-mail.outlook.com
    # GMX.com Server
    # IMAP Server (Incoming Messages) 	imap.gmx.com
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    # authenticate
    imap.login(username, password)
    status, messages = imap.select("INBOX")
    # number of top emails to fetch
    N = 3
    # total number of emails
    messages = int(messages[0])
    
    unreadMessages = imap.status('INBOX', "(UNSEEN)")
    unreadMessages = str(unreadMessages)
    unreadMessages = unreadMessages.replace("UNSEEN","")
    unreadMessages = unreadMessages.replace("OK","")
    unreadMessages = unreadMessages.replace("INBOX","")
    unreadMessages = unreadMessages.replace("b","")
    unreadMessages = unreadMessages.replace("(","")
    unreadMessages = unreadMessages.replace(")","")
    unreadMessages = unreadMessages.replace("[","")
    unreadMessages = unreadMessages.replace("]","")
    unreadMessages = unreadMessages.replace("'","")
    unreadMessages = unreadMessages.replace('"',"")
    unreadMessages = unreadMessages.replace(",","")
    unreadMessages = unreadMessages.replace(" ","")

    
    im = Image.new('RGB', (frameSize), 'black')
    font = ImageFont.truetype("FreeMonoBold.ttf", 15)
    draw = ImageDraw.Draw(im)
    draw.text((0,27), "Unread E-Mails" , fill="white", font=font)
    draw.text((55,52),unreadMessages,fill="white", font=font)
    device.display(im)
    sleep(3)
    subjectsAndFroms = []
    messageText = []
    #dann 3 mails mit from und subject als text:
    for i in range(messages, messages-N, -1):
     # fetch the email message by ID
     res, msg = imap.fetch(str(i), "(RFC822)")
     for response in msg:
        if isinstance(response, tuple):
            # parse a bytes email into a message object
            msg = email.message_from_bytes(response[1])
            # decode the email subject
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                # if it's a bytes, decode to str
                subject = subject.decode(encoding)
            # decode email sender
            From, encoding = decode_header(msg.get("From"))[0]
            if isinstance(From, bytes):
                From = From.decode(encoding)
            print("Subject:", subject)
            print("From:", From)
            subjectsAndFroms.append(subject)
            subjectsAndFroms.append(From)
            # if the email message is multipart
            if msg.is_multipart():
                # iterate over email parts
                for part in msg.walk():
                    # extract content type of email
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    try:
                        # get the email body
                        body = part.get_payload(decode=True).decode()
                    except:
                        pass
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        # print text/plain emails and skip attachments
                        print(body)
                        messageText.append(body)
                    elif "attachment" in content_disposition:
                        # download attachment
                        filename = part.get_filename()
                        if filename:
                            folder_name = cleanMail(subject)
                            if not os.path.isdir(folder_name):
                                # make a folder for this email (named after the subject)
                                os.mkdir(folder_name)
                            filepath = os.path.join(folder_name, filename)
                            # download attachment and save it
                            open(filepath, "wb").write(part.get_payload(decode=True))
            else:
                # extract content type of email
                content_type = msg.get_content_type()
                # get the email body
                body = msg.get_payload(decode=True).decode()
                if content_type == "text/plain":
                    # print only text email parts
                    print(body)
                    messageText.append(body)
            if content_type == "text/html":
                # if it's HTML, create a new HTML file and open it in browser
                folder_name = cleanMail(subject)
                if not os.path.isdir(folder_name):
                    # make a folder for this email (named after the subject)
                    os.mkdir(folder_name)
                filename = "index.html"
                filepath = os.path.join(folder_name, filename)
                # write the file
                open(filepath, "w").write(body)
                # open in the default browser
                webbrowser.open(filepath)
            print("="*100)
    # close the connection and logout
    imap.close()
    imap.logout()
    subjectOne = subjectsAndFroms[0]
    fromOne = subjectsAndFroms[1]
    subjectTwo = subjectsAndFroms[2]
    fromTwo = subjectsAndFroms[3]
    subjectThree = subjectsAndFroms[4]
    fromThree = subjectsAndFroms[5]
    messageTextOne = messageText[0]
    messageTextTwo = messageText[1]
    messageTextThree = messageText[2]

    fromOneArray = fromOne.split()
    fromTwoArray = fromTwo.split()
    fromThreeArray = fromThree.split()



    im = Image.new('RGB', (frameSize), 'black')
    font = ImageFont.truetype("FreeMonoBold.ttf", 10)
    draw = ImageDraw.Draw(im)
    draw.text((5,5),  "Subject: " + subjectOne , fill="red", font=font)
    draw.text((5,15), "From: " + fromOneArray[0] + " " + fromOneArray[1] , fill="red", font=font)
    draw.text((5,25), fromOneArray[2] , fill="red", font=font)
    draw.text((5,35),  "Subject: " + subjectTwo , fill="white", font=font)
    draw.text((5,45), "From: " + fromTwoArray[0] + " " + fromTwoArray[1] , fill="white", font=font)
    draw.text((5,55), fromTwoArray[2] , fill="white", font=font)
    draw.text((5,65),  "Subject: " + subjectThree , fill="white", font=font)
    draw.text((5,75), "From: " + fromThreeArray[0] + " " + fromThreeArray[1] , fill="white", font=font)
    draw.text((5,85), fromThreeArray[2] , fill="white", font=font)
    device.display(im)
    while True:
      if apds.isGestureAvailable():
        motion = apds.readGesture()
        print (motion)
        print ("Gesture={}".format(dirs.get(motion, "unknown")))
        if motion == 4: 
         if mailCounter > 0:
          mailCounter -= 1
          mailOldState = False
         else:
          mailCounter = 2
          mailOldState = False
        elif motion == 3:
         if mailCounter < 2:
          mailCounter += 1
          mailOldState = False
         else:
          mailCounter = 0
          mailOldState = False
        elif motion == 1:
         if mailCounter == 0:
           mailDepiction(messageTextOne)
           mailOldState = False
         elif mailCounter == 1:
           mailDepiction(messageTextTwo)
           mailOldState = False
         elif mailCounter == 2:
           mailDepiction(messageTextThree)
           mailOldState = False
        elif motion == 2:
         return
        if mailOldState == False:
         if mailCounter == 0:
           im = Image.new('RGB', (frameSize), 'black')
           draw = ImageDraw.Draw(im)
           draw.text((5,5),  "Subject: " + subjectOne , fill="red", font=font)
           draw.text((5,15), "From: " + fromOneArray[0] + " " + fromOneArray[1] , fill="red", font=font)
           draw.text((5,25), fromOneArray[2] , fill="red", font=font)
           draw.text((5,35),  "Subject: " + subjectTwo , fill="white", font=font)
           draw.text((5,45), "From: " + fromTwoArray[0] + " " + fromTwoArray[1] , fill="white", font=font)
           draw.text((5,55), fromTwoArray[2] , fill="white", font=font)
           draw.text((5,65),  "Subject: " + subjectThree , fill="white", font=font)
           draw.text((5,75), "From: " + fromThreeArray[0] + " " + fromThreeArray[1] , fill="white", font=font)
           draw.text((5,85), fromThreeArray[2] , fill="white", font=font)
         elif mailCounter == 1:
           im = Image.new('RGB', (frameSize), 'black')
           draw = ImageDraw.Draw(im)
           draw.text((5,5),  "Subject: " + subjectOne , fill="white", font=font)
           draw.text((5,15), "From: " + fromOneArray[0] + " " + fromOneArray[1] , fill="white", font=font)
           draw.text((5,25), fromOneArray[2] , fill="white", font=font)
           draw.text((5,35),  "Subject: " + subjectTwo , fill="red", font=font)
           draw.text((5,45), "From: " + fromTwoArray[0] + " " + fromTwoArray[1] , fill="red", font=font)
           draw.text((5,55), fromTwoArray[2] , fill="red", font=font)
           draw.text((5,65),  "Subject: " + subjectThree , fill="white", font=font)
           draw.text((5,75), "From: " + fromThreeArray[0] + " " + fromThreeArray[1] , fill="white", font=font)
           draw.text((5,85), fromThreeArray[2] , fill="white", font=font)
         elif mailCounter == 2:
           im = Image.new('RGB', (frameSize), 'black')
           draw = ImageDraw.Draw(im)
           draw.text((5,5),  "Subject: " + subjectOne , fill="white", font=font)
           draw.text((5,15), "From: " + fromOneArray[0] + " " + fromOneArray[1] , fill="white", font=font)
           draw.text((5,25), fromOneArray[2] , fill="white", font=font)
           draw.text((5,35),  "Subject: " + subjectTwo , fill="white", font=font)
           draw.text((5,45), "From: " + fromTwoArray[0] + " " + fromTwoArray[1] , fill="white", font=font)
           draw.text((5,55), fromTwoArray[2] , fill="white", font=font)
           draw.text((5,65),  "Subject: " + subjectThree , fill="red", font=font)
           draw.text((5,75), "From: " + fromThreeArray[0] + " " + fromThreeArray[1] , fill="red", font=font)
           draw.text((5,85), fromThreeArray[2] , fill="red", font=font)
         device.display(im)
      mailOldState = True   
      sleep(0.1)
     
def mailDepiction(messageText):
    dirs = {
    APDS9960_DIR_NONE: "none",
    APDS9960_DIR_LEFT: "left",
    APDS9960_DIR_RIGHT: "right",
    APDS9960_DIR_UP: "up",
    APDS9960_DIR_DOWN: "down",
    APDS9960_DIR_NEAR: "near",
    APDS9960_DIR_FAR: "far",
 }
    global im
    
    # is used to generate line breaks
    newMailWordLength = 0
    lineString = ""
    yHeight = 5
    
    im = Image.new('RGB', (frameSize), 'black')
    font = ImageFont.truetype("FreeMonoBold.ttf", 8)
    draw = ImageDraw.Draw(im) 
    # this code generates line breaks
    mailArray = messageText.split()
    for mailWord in mailArray:
      newMailWordLength = len(mailWord) + newMailWordLength + 1
      print(lineString)
      if  newMailWordLength < 20:
        lineString = " ".join((lineString,mailWord))
      else:
        draw.text((5,yHeight), lineString , fill="white", font=font)
        yHeight += 10
        newMailWordLength = len(mailWord)
        lineString = mailWord
    draw.text((5,yHeight), lineString , fill="white", font=font)




    device.display(im)
    while True:
        if apds.isGestureAvailable():
         motion = apds.readGesture()
         print (motion)
         print ("Gesture={}".format(dirs.get(motion, "unknown")))
         if motion == 2:
          return
         sleep(0.1)


def jokeApp():
    dirs = {
    APDS9960_DIR_NONE: "none",
    APDS9960_DIR_LEFT: "left",
    APDS9960_DIR_RIGHT: "right",
    APDS9960_DIR_UP: "up",
    APDS9960_DIR_DOWN: "down",
    APDS9960_DIR_NEAR: "near",
    APDS9960_DIR_FAR: "far",
 }
    global im
    global jokeCounter
    global jokeOldState
    im = Image.new('RGB', (frameSize), 'black')
    font = ImageFont.truetype("FreeMonoBold.ttf", 15)
    draw = ImageDraw.Draw(im)
    # display the main text in the app
    draw.text((0,65), "Tell me a Joke!" , fill="white", font=font)
    device.display(im)
    while True:
     if apds.isGestureAvailable():
      motion = apds.readGesture()
      print (motion)
      print ("Gesture={}".format(dirs.get(motion, "unknown")))
      if motion == 1:
        jokeDepiction()
        jokeOldState = False
      elif motion == 2:
        return
     if jokeOldState == False:
        im = Image.new('RGB', (frameSize), 'black')
        draw = ImageDraw.Draw(im)
        draw.text((0,65), "Tell me a Joke!" , fill="white", font=font)

     jokeOldState = True
     device.display(im)

def jokeDepiction():
    dirs = {
    APDS9960_DIR_NONE: "none",
    APDS9960_DIR_LEFT: "left",
    APDS9960_DIR_RIGHT: "right",
    APDS9960_DIR_UP: "up",
    APDS9960_DIR_DOWN: "down",
    APDS9960_DIR_NEAR: "near",
    APDS9960_DIR_FAR: "far",
 }
    global im
    global jokeCounter
    
     # used to generate line breaks
    newJokeWordLength = 0
    lineString = ""
    yHeight = 5

    # save the JSON file from the joke-URL as a variable 
    url = 'https://witzapi.de/api/joke'
    json_data = requests.get(url).json()
    # filter the text of the JSON file 
    formatted_joke = json_data[0]['text']
    formatted_joke = str(formatted_joke)
    # after the formatting we use the split() method to turn our formatted joke into a array
    jokeArray = formatted_joke.split()
    im = Image.new('RGB', (frameSize), 'black')
    font = ImageFont.truetype("FreeMonoBold.ttf", 10)
    draw = ImageDraw.Draw(im)


    # this code generates line breaks
    for jokeWord in jokeArray:
    
      newJokeWordLength = len(jokeWord) + newJokeWordLength + 1
      if  newJokeWordLength < 20:
        lineString = " ".join((lineString,jokeWord))
      else:
        draw.text((5,yHeight), lineString , fill="white", font=font)
        yHeight += 10
        newJokeWordLength = len(jokeWord)
        lineString = jokeWord
    draw.text((5,yHeight), lineString , fill="white", font=font)



    device.display(im)
    while True:
        if apds.isGestureAvailable():
         motion = apds.readGesture()
         print (motion)
         print ("Gesture={}".format(dirs.get(motion, "unknown")))
         if motion == 2:
          return
         sleep(0.1)


def calendarApp():
    dirs = {
    APDS9960_DIR_NONE: "none",
    APDS9960_DIR_LEFT: "left",
    APDS9960_DIR_RIGHT: "right",
    APDS9960_DIR_UP: "up",
    APDS9960_DIR_DOWN: "down",
    APDS9960_DIR_NEAR: "near",
    APDS9960_DIR_FAR: "far",
 }
    global im
    global calendarCounter
    global calendarOldState
    # we open our JSON-file with saved events and load it into a variable
    with open('events.json', 'r') as fileobj:
      c_data = json.load(fileobj)
    
    yHeight = 5
    counterRedWhite = 0
    im = Image.new('RGB', (frameSize), 'black')
    font = ImageFont.truetype("FreeMonoBold.ttf", 10)
    draw = ImageDraw.Draw(im)
    menu = []
    # we print out the titles of the calendar events on the display
    menu.append(str(c_data[0]['title']))
    menu.append(str(c_data[1]['title']))
    menu.append(str(c_data[2]['title']))
    menu.append(str(c_data[3]['title']))
    menu.append(str(c_data[4]['title']))
    menu.append(str(c_data[5]['title']))
    menu.append(str(c_data[6]['title']))
    menu.append(str(c_data[7]['title']))
    calendarOldState = False

    device.display(im)
    while True:
     if apds.isGestureAvailable():
      motion = apds.readGesture()
      print (motion)
      print ("Gesture={}".format(dirs.get(motion, "unknown")))
      if motion == 4:
       if calendarCounter > 0:
        calendarCounter -= 1
        calendarOldState = False
       else:
        calendarCounter = 7
        calendarOldState = False
      elif motion == 3:
       if calendarCounter < 7:
        calendarCounter += 1
        calendarOldState = False
       else:
        calendarCounter = 0
        calendarOldState = False
      elif motion == 1:
        calendarDepiction()
        calendarOldState = False
      elif motion == 2:
        return
     if calendarOldState == False:
      im = Image.new('RGB', (frameSize), 'black')
      draw = ImageDraw.Draw(im)
      for menuData in menu:
        if counterRedWhite == calendarCounter:
         draw.text((5,yHeight), menuData , fill="red", font=font)
         yHeight += 15
         counterRedWhite += 1
        else:
         draw.text((5,yHeight), menuData , fill="white", font=font)
         yHeight += 15
         counterRedWhite += 1
     device.display(im)
     calendarOldState = True
     counterRedWhite = 0
     yHeight = 5
     sleep(0.1)
     
def calendarDepiction():
    dirs = {
    APDS9960_DIR_NONE: "none",
    APDS9960_DIR_LEFT: "left",
    APDS9960_DIR_RIGHT: "right",
    APDS9960_DIR_UP: "up",
    APDS9960_DIR_DOWN: "down",
    APDS9960_DIR_NEAR: "near",
    APDS9960_DIR_FAR: "far",
 }
    global im
    global calendarCounter


    with open('events.json', 'r') as fileobj:
     c_data2 = json.load(fileobj)

    # depending on the selected calendar event we save the title, start date and end date of that event 
    if calendarCounter == 0:
       title1 = c_data2[0]['title']
       start1 = c_data2[0]['start']
       end1   = c_data2[0]['end']
    elif calendarCounter == 1:
       title1 = c_data2[1]['title']
       start1 = c_data2[1]['start']
       end1   = c_data2[1]['end']
    elif calendarCounter == 2:
       title1 = c_data2[2]['title']
       start1 = c_data2[2]['start']
       end1   = c_data2[2]['end']
    elif calendarCounter == 3:
       title1 = c_data2[3]['title']
       start1 = c_data2[3]['start']
       end1   = c_data2[3]['end']
    elif calendarCounter == 4:
       title1 = c_data2[4]['title']
       start1 = c_data2[4]['start']
       end1   = c_data2[4]['end']
    elif calendarCounter == 5:
       title1 = c_data2[5]['title']
       start1 = c_data2[5]['start']
       end1   = c_data2[5]['end']
    elif calendarCounter == 6:
       title1 = c_data2[6]['title']
       start1 = c_data2[6]['start']
       end1   = c_data2[6]['end']
    elif calendarCounter == 7:
       title1 = c_data2[7]['title']
       start1 = c_data2[7]['start']
       end1   = c_data2[7]['end']

    # we display the title, start date and end date of the selected calendar event
    im = Image.new('RGB', (frameSize), 'black')
    font = ImageFont.truetype("FreeMonoBold.ttf", 10)    
    draw = ImageDraw.Draw(im)
    draw.text((5,5), "Titel:", fill="white", font=font)
    draw.text((5,15), str(title1) , fill="white", font=font)
    draw.text((5,25), "Startzeit:", fill="white", font=font)
    draw.text((5,35), str(start1) , fill="white", font=font)
    draw.text((5,45), "Endzeit:", fill="white", font=font)
    draw.text((5,55), str(end1) , fill="white", font=font)
    device.display(im)
    while True:
        if apds.isGestureAvailable():
         motion = apds.readGesture()
         print (motion)
         print ("Gesture={}".format(dirs.get(motion, "unknown")))
         if motion == 2:
          return
         sleep(0.1)   


def temperatureApp():
    dirs = {
    APDS9960_DIR_NONE: "none",
    APDS9960_DIR_LEFT: "left",
    APDS9960_DIR_RIGHT: "right",
    APDS9960_DIR_UP: "up",
    APDS9960_DIR_DOWN: "down",
    APDS9960_DIR_NEAR: "near",
    APDS9960_DIR_FAR: "far",
 }
    global gpio
    global sensor
    # we get the temperature and humidity from the sensor and display it
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    im = Image.new('RGB', (frameSize), 'black')
    font = ImageFont.truetype("FreeMonoBold.ttf", 10)
    draw = ImageDraw.Draw(im)
    draw.text((5,5), "Temperature App" , fill="white", font=font)
    draw.text((5,25), "Temperature: ", fill="white", font=font)
    draw.text((5,35), str(temperature) , fill="white", font=font)
    draw.text((5,55), "Humidity: ", fill="white", font=font)
    draw.text((5,65), str(humidity) , fill="white", font=font)
    device.display(im)
    while True:
        if apds.isGestureAvailable():
         motion = apds.readGesture()
         print (motion)
         print ("Gesture={}".format(dirs.get(motion, "unknown")))
         if motion == 2:
          return
         sleep(0.1)


def volumeApp():
    dirs = {
    APDS9960_DIR_NONE: "none",
    APDS9960_DIR_LEFT: "left",
    APDS9960_DIR_RIGHT: "right",
    APDS9960_DIR_UP: "up",
    APDS9960_DIR_DOWN: "down",
    APDS9960_DIR_NEAR: "near",
    APDS9960_DIR_FAR: "far",
 }  
    
    # here we only display the starting volume display once and switch inVolumeApp to false once we leave the app 
    global inVolumeApp
    global volumeCounter
    xCoordinate = 6
    im = Image.new('RGB', (frameSize), 'black')
    draw = ImageDraw.Draw(im)    
    font = ImageFont.truetype("FreeMonoBold.ttf", 10)
    draw.text((15,5), "Volume Controller" , fill="white", font=font)
    font = ImageFont.truetype("FreeMonoBold.ttf", 15)
    draw.text((55,55), str(volumeCounter*5) , fill="white", font=font)
    draw.text((35,80), "Unmuted" , fill="white", font=font)
    draw.rectangle([(5,25),(125,45)],outline="white",fill= None,width=1)
    for x in range(volumeCounter):    
      draw.rectangle([(xCoordinate,26),(xCoordinate+5,44)],outline="white",fill= "red",width=1)
      xCoordinate += 6
    device.display(im)
    while True:
        if apds.isGestureAvailable():
         motion = apds.readGesture()
         print (motion)
         print ("Gesture={}".format(dirs.get(motion, "unknown")))
         if motion == 2:
          inVolumeApp = False
          return
         sleep(0.1) 


def main():
 dirs = {
    APDS9960_DIR_NONE: "none",
    APDS9960_DIR_LEFT: "left",
    APDS9960_DIR_RIGHT: "right",
    APDS9960_DIR_UP: "up",
    APDS9960_DIR_DOWN: "down",
    APDS9960_DIR_NEAR: "near",
    APDS9960_DIR_FAR: "far",
 }
#switcher for the apps of the app menu
 switcher = {
   0: clock,
   1: pictureOne,
   2: pictureTwo,
   3: pictureThree,
   4: pictureFour,
   5: pictureFive,
   6: pictureSix,
   7: pictureSeven,
   8: pictureEight,
   9: pictureNine,
   10: pictureTen,
 }
 try:

     global oldState
     global counterPictures
     global inVolumeApp
     im = Image.open("/home/pi/BDA/bda.jpg")
     draw = ImageDraw.Draw(im)
     device.display(im)
     sleep (3)
     func = switcher.get(counterPictures, lambda: 0)
     func()
     while True:
        if apds.isGestureAvailable():
         motion = apds.readGesture()
         print (motion)
         print ("Gesture={}".format(dirs.get(motion, "unknown")))
        # with left and right swiping you can go through the apps and with the motion "up" (down here since its inverted as wrote) you go into the app until you leave it
         if motion == 2:
          if counterPictures > 0:
           counterPictures -= 1
           oldState = False
          else:
           counterPictures = 10
           oldState = False
         elif motion == 1:
          if counterPictures < 10:
           counterPictures += 1
           oldState = False
          else:
           counterPictures = 0
           oldState = False
         elif motion == 4:
          if counterPictures == 1:
            temperatureApp()
            oldState = False
          elif counterPictures == 2:
             calendarApp()
             oldState = False
          elif counterPictures == 3:
             mailApp()
             oldState = False   
          elif counterPictures ==4:
             trafficjamApp()
             oldState = False
          elif counterPictures == 5:
             gameTTT()
             oldState = False
          elif counterPictures == 6:
             inVolumeApp = True
             volumeApp()
             oldState = False   
          elif counterPictures == 7:
             trainApp()
             oldState = False
          elif counterPictures == 8:
             weatherApp()
             oldState = False
          elif counterPictures == 9:
             coronaApp()
             oldState = False
          elif counterPictures == 10:
             jokeApp()
             oldState = False
            #with oldState we only need to display an new image when its necessary
        if oldState == False:
          print ("hier ist der Counter:" + str(counterPictures))
          func = switcher.get(counterPictures, lambda: 0)
          func()
        oldState = True
        sleep(0.1)

 finally:
    ky040.stop()
    GPIO.cleanup()
    print("Bye")

if __name__ == "__main__":
    try:
        print("hello world, im the BDA")
        
        CLOCKPIN = 5
        DATAPIN = 6
        SWITCHPIN = 13

        
        
        GPIO.setmode(GPIO.BCM)
        
        # Initialization of the rotary Encoder
        ky040 = KY040(CLOCKPIN, DATAPIN, SWITCHPIN, rotaryChange, switchPressed)
        ky040.start()

        # Initialization of the movement sensor
        # returns integers, 0 = none, 1 = left, 2 = right , 3 = up, 4 = down, 5 = near , 6 = far 
        apds.setProximityIntLowThreshold(50)
        apds.setGestureGain(0)
        apds.enableGestureSensor()
        
        main()
    except KeyboardInterrupt:
        pass
