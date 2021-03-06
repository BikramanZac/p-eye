"""
This python script is run in Raspberry Pi zero for standard p-eye
a line of code is written in /etc/rc.local for this script to be run at boot
ex) sudo python /home/pi/git/p-eye/redpeye.py &

WHAT IT DOES
It keeps waiting until GPIO pin 25 is triggered. Pin 25 is set as an interrupt and once it is triggered 
it will run my_callback function that takes a picture, encodes the image as a string, 
sends the string to the web service deployed in AWS, gets the result back, and finally relays to users in audio format.

FYI pico2wave software is used for Text-to-speech 

"""
import select
import os
import sys
import picamera
import io
import RPi.GPIO as GPIO
import base64
import json
import argparse
import subprocess
import requests
from time import sleep  
import time
import math
GPIO.setmode(GPIO.BCM)
GPIO.setup(25, GPIO.IN, GPIO.PUD_UP)
time_stamp = time.time()

def my_callback(channel):  
	global time_stamp  
	time_now = time.time()
        print "falling edge detected on 25"
        #print("C is just pressed!")
        photo_file = "image.jpg"
        if(math.fabs(time_now - time_stamp)) >= 5:

		with picamera.PiCamera() as camera:
        	        camera.rotation = 270
        	        camera.capture(photo_file)
               	 	print(photo_file + " is just captured!")

        	try:        	        
        	        label = get_label(photo_file)
        	        print label
        	        subprocess.call("pico2wave -w test.wav "+'\"'+text+'\"' ,shell=True)
               		subprocess.call("aplay test.wav",shell=True)
                	os.system("sudo rm test.wav")
                
        	except:
                	print "Unexpected error ", sys.exc_info()[0]

        	os.system("sudo rm " + photo_file)  # remove existing jpeg files first
	time_stamp = time_now

# when a falling edge is detected on port 25, regardless of whatever   
# else is happening in the program, the function my_callback will be run   
GPIO.add_event_detect(25, GPIO.FALLING, callback=my_callback) 


def is_letter_input(letter):
        # Utility function to check if a specific character is available on stdin.
        # Comparison is case insensitive.
        if select.select([sys.stdin,],[],[],0.0)[0]:
                input_char = sys.stdin.read(1)
                return input_char.lower() == letter.lower()
        return False


def take_picture():
        photo_file = "image" + str(counter) + ".jpg"
        with picamera.PiCamera() as camera:
                camera.capture(photo_file)
                print(photo_file + " is just captured!")
        counter += 1                
        return photo_file

def get_label(image):
        with open(image, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())

        url= "http://ec2-52-88-62-32.us-west-2.compute.amazonaws.com/todo/api/v1.0/images"    
        data = {'encode' : encoded_string }
        headers = {'Content-Type': 'application/json'}

        # make sure that the data is json type because the server only allows json type
        r = requests.post(url, data = json.dumps(data), headers = headers)

        # r is json type. r.json() convert json type to dic type
        dic_label = r.json()
        #print dic_label.values()[0]
        text = dic_label.values()[0]
        return text


if __name__ == '__main__':

        os.system("sudo rm *.jpg")  # remove existing jpeg files first
        print("Deleting existing photos")
        print("Hello P-eye!!!!!!")

        counter = 0
        while True:

                sleep(0.5)
		
		#debugging purpose using Keyboard
                if is_letter_input('c'):
                        print("C is just pressed!")
                        photo_file = "image" + str(counter) + ".jpg"
                        with picamera.PiCamera() as camera:
                                camera.rotation = 270
                                camera.capture(photo_file)
                                print(photo_file + " is just captured!")

                        try:
                                #label = api.get_label(photo_file)  # using google vision api
                                label = get_label(photo_file)
                                print label
                                #subprocess.call("pico2wave -w test.wav "+'\"'+text+'\"' ,shell=True)
                                #subprocess.call("aplay test.wav",shell=True)
                                #os.system("sudo rm test.wav")
                                
                        except:
                                print "Unexpected error ", sys.exc_info()[0]

                        counter += 1

