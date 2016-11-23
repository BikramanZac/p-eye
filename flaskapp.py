from flask import Flask, jsonify, request, abort
import base64
import cStringIO
import PIL.Image
import urllib2 as urllib
import io
import cv2
import numpy
import imutils
import os
import recognition
from GoogleApi import GoogleApi

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
"""
RESTful API Service  available method : GET, POST

  GET : return a list of image containing a lable, an encoded image string, id 
   ex. r = requests.get("http://localhost:5000/todo/api/v1.0/images")

  POST : Get encoded binary data(image) and decode such the encoding back to binary data
         Regenerate the image and save it then open the file as OpenCV picture
         Start Image cropping and send the cropped picture to Google Vision API
         Get the label from API and generate a json file that contains this label
         Send it back to client(Pi) in json type
   
   HOW TO USE
   ex. url = "http://localhost:5000/todo/api/v1.0/images"
       data = {'encode' : encoded_string }
       headers = {'Content-Type': 'application/json'}
       r = requests.post(url, data = json.dumps(data), headers = headers)
"""


app = Flask(__name__)

# a default list
images = [
	{
		'id' : 1,
		'encode' : u'EXAMPLE OF ENCODE BINARY',
		'label' : "hey"
	}
]



@app.route('/')
def hello_world():
  return 'Hello from Flask!'

@app.route('/todo/api/v1.0/images', methods=['GET'])
def get_images():
    return jsonify({'images': images})

@app.route('/todo/api/v1.0/images', methods=['POST'])
def get_image_and_produce_label():
    """
    reconpile the received picture and save it then
    openCV will start detecting the color and start cropping
    
    if there is a face in the picture --> return emotion        
    elif there is some text in the picture  --> return text
    	and if there is a green contour --> crop the picture then return text
    else  --> crop the picture return label
    
    """
    # the type of the data should be json and have to have key 'encode'
    # otherwise I will just abort with 400    
    if not request.json or not 'encode' in request.json:
        abort(400)

    # decode the encoded string of image
    data = base64.b64decode(request.json['encode'])  

    # assume data contains your decoded image  http://stackoverflow.com/a/3715530
    file_like = cStringIO.StringIO(data)
    pil_img = PIL.Image.open(file_like)
    photo_file = "pilpic.jpg"
    pil_img.save(photo_file)       
    
    text = ""
    
    google = GoogleApi(photo_file)    
    
    # if there is a face in the picture
    if(google.is_face() == True):
        text = text + "the facial expression is " + google.get_face() + " "    
	
    # if there is some text in the picture
    if(google.is_text() == True):       
        text = "the text is " + google.get_text()
	
	# detect color and crop the picture then 
        # return 0, 1, 2 depending on the color 
	which_color = recognition.color_detect_and_crop_image(photo_file)
	# if there is some text and a green contour
	if(which_color == 1):  # 1: green
		text = "the text is " + recognition.get_text(photo_file) + " "			
        
    text = text + "the object is " + recognition.get_label(photo_file)
    
    #cv2.imshow('yes', imcv)
    #cv2.waitKey(0)
    
    #delete pictures that were saved
    os.system('rm pilpic.jpg')
    os.system('rm cropped_pilpic.jpg')

    # create a new dictionary that contains the generated label 
    image = {
        'id': images[-1]['id'] + 1,   # guarantee unique id 
        'encode': request.json['encode'],
        'text': text   # add a label that got the highest score from recognition
    }

    #append the created dictionary to the exisitng data
    images.append(image)

    # return the label in json type       
    return jsonify({'Hello we found ': text}), 201



if __name__ == '__main__':
  app.run(host='0.0.0.0', port = 6000)
