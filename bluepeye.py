<<<<<<< HEAD:bluepeye.py
import os
import picamera
import sys
import io
import select
import glob
import time
import base64
import os
import argparse
from bluetooth import *

def get_encode(image):
    """
    1. encode binary data(image) to printable ASCII characeters
    2. send the encoded data to the server using REST POST method
    3. get the result from the server and print out the label
    """

    with open(image, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    return encoded_string

def take_picture(counter):
        photo_file = "image" + str(counter) + ".jpg"
        with picamera.PiCamera() as camera:
                camera.capture(photo_file)
                print(photo_file + " is just captured!")
	
        return photo_file

server_sock=BluetoothSocket( RFCOMM )
server_sock.bind(("",PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

advertise_service( server_sock, "raspberrypi",
                   service_id = uuid,
                   service_classes = [ uuid, SERIAL_PORT_CLASS ],
                   profiles = [ SERIAL_PORT_PROFILE ], 
#                   protocols = [ OBEX_UUID ] 
                    )
                   
print("Waiting for connection on RFCOMM channel %d" % port)



while True:
	client_sock, client_info = server_sock.accept()
	print("Accepted connection from ", client_info)
	print("waiting for data")
	total = 0

	while True:
		try:
        	    data = client_sock.recv(1024)
      		except Exception, e:
		    print e
          	    break
       		if len(data) == 0: break
        	total += len(data)
        	print("total byte read: %d" % total)

       	 	if data == 'i':
        		data = str(get_encode("/home/pi/git/p-eye/fruits.png")) + "i!"
        		print "image reception"
        	elif data == 'f':			
			data = str(get_encode("/home/pi/git/p-eye/face.jpg")) + "f!"
			print "face reception"
		elif data == 't':			
			data = str(get_encode("/home/pi/git/p-eye/greentext.jpg")) + "t!"
			print "text reception"
		else:
			data = 'OMG SOMETHING WENT WRONG!' 
		client_sock.send(data)
		print "number of letters" + str(len(data))

    	client_sock.close()

        print("connection closed")

server_sock.close()

=======
import os
import picamera
import sys
import io
import select
import glob
import time
import base64
import os
import argparse
from bluetooth import *

def get_encode(image):
    """
    1. encode binary data(image) to printable ASCII characeters
    2. send the encoded data to the server using REST POST method
    3. get the result from the server and print out the label
    """

    with open(image, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    return encoded_string

def take_picture(counter):
        photo_file = "image" + str(counter) + ".jpg"
        with picamera.PiCamera() as camera:
                camera.capture(photo_file)
                print(photo_file + " is just captured!")
	
        return photo_file

server_sock=BluetoothSocket( RFCOMM )
server_sock.bind(("",PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

advertise_service( server_sock, "raspberrypi",
                   service_id = uuid,
                   service_classes = [ uuid, SERIAL_PORT_CLASS ],
                   profiles = [ SERIAL_PORT_PROFILE ], 
#                   protocols = [ OBEX_UUID ] 
                    )
                   
print("Waiting for connection on RFCOMM channel %d" % port)



while True:
	client_sock, client_info = server_sock.accept()
	print("Accepted connection from ", client_info)
	print("waiting for data")
	total = 0

	while True:
        try:
            data = client_sock.recv(1024)
        except bluetooth.BluetoothError as e:
            break
        if len(data) == 0: break
        total += len(data)
        print("total byte read: %d" % total)

        if data == 'imageRecognition':
        	data = str(get_encode("/home/pi/git/p-eye/fruits.png")) + "!"
        	print "image reception"
        elif data == 'faceRecognition':			
			data = str(get_encode("/home/pi/git/p-eye/face.jpg")) + "!"
			print "face reception"
		elif data == 'textRecognition':			
			data = str(get_encode("/home/pi/git/p-eye/greentext.jpg")) + "!"
			print "text reception"
		else:
			data = 'OMG SOMETHING WENT WRONG!' 
		client_sock.send(data)
		print "number of letters" + str(len(data))

    client_sock.close()

    print("connection closed")

server_sock.close()
>>>>>>> 05f8ed93e1af802495e8ea6fdcee2f7096e07337:newblootoothtest.py
