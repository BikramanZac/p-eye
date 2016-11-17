import os
import picamera
import sys
import io
import select
import glob
import time
import RPi.GPIO as GPIO
import base64
import requests
import os
import json
import argparse
from bluetooth import *

counter = 0

def get_encode(image):
    """
    1. encode binary data(image) to printable ASCII characeters
    2. send the encoded data to the server using REST POST method
    3. get the result from the server and print out the label
    """

    with open(image, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    return encoded_string

def take_picture():
        photo_file = "image" + str(counter) + ".jpg"
        with picamera.PiCamera() as camera:
                camera.capture(photo_file)
                print(photo_file + " is just captured!")
	counter += 1
        return photo_file

def is_letter_input(letter):
        # Utility function to check if a specific character is available on stdin.
        # Comparison is case insensitive.
        if select.select([sys.stdin,],[],[],0.0)[0]:
                input_char = sys.stdin.read(1)
                return input_char.lower() == letter.lower()
        return False
   
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')



GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)


server_sock=BluetoothSocket( RFCOMM )
server_sock.bind(("",PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

advertise_service( server_sock, "AquaPiServer",
                   service_id = uuid,
                   service_classes = [ uuid, SERIAL_PORT_CLASS ],
                   profiles = [ SERIAL_PORT_PROFILE ], 
#                   protocols = [ OBEX_UUID ] 
                    )
while True:          
	print "Waiting for connection on RFCOMM channel %d" % port

	client_sock, client_info = server_sock.accept()
	print "Accepted connection from ", client_info

	try:
        	data = client_sock.recv(1024)
    		if len(data) == 0: break
       	        print "received [%s]" % data

		if data == 'takePicture':
			#take a picture function here!
			"""
			photo_file = take_picture()
			data = str(get_encode(photo_file)) + "!"
			"""
 
			data = str(get_encode("/home/pi/git/p-eye/greentext.jpg")) + "!"	
		elif data == 'volumeUp':
			GPIO.output(17,False)
			data = 'Volume up!'
		elif data == 'lightOff':
			GPIO.output(17,True)
			data = 'light off!'
		else:
			data = 'WTF!' 

	        client_sock.send(data)
		print "sending [%s]" % data
		print "number of letters" + str(len(data))
	except IOError:
		pass

	except KeyboardInterrupt:

		print "disconnected"

		client_sock.close()
		server_sock.close()
		print "all done"

		break
