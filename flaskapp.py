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

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
"""
RESTful API Service  available method : GET, POST

1. GET : return a list of image containing a lable, an encoded image string, id 
   ex. r = requests.get("http://localhost:5000/todo/api/v1.0/images")

2. POST : get encoded binary data(image) and decode such the encoding back to binary data
          regenerate the image and save it then open the file as OpenCV picture
          start Image cropping and send the cropped picture to Google Vision API
          get the text from API and generate a json file that contains the text
          return the text in json type
   ex. url = "http://localhost:5000/todo/api/v1.0/images"
       data = {'encode' : encoded_string }
       headers = {'Content-Type': 'application/json'}
       r = requests.post(url, data = json.dumps(data), headers = headers)
"""


app = Flask(__name__)


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
def get_image_text():
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
    
    which_color = recognition.color_detect(photo_file)

    # 0 is red, 1 is green, 2 is blue
    if(which_color == 0 ):  # red
        text = "" + recognition.get_label(photo_file)

    if(which_color == 1):   # green
        text = "" + recognition.get_text(photo_file)

    """
    if(which_color == 2):
        text = something
    """

    #cv2.imshow('yes', imcv)
    #cv2.waitKey(0)
    
    os.system('rm pilpic.jpg')
    # create a new dictionary that contains the generated label 
    image = {
        'id': images[-1]['id'] + 1,   # guarantee unique id 
        'encode': request.json['encode'],
        'text': text   # add a label that got the highest score from recognition
    }

    #gl_img.show() # this can be used for debugging

    #append the created dictionary to the exisitng data
    images.append(image)

    # return the label in json type       
    return jsonify({'text': text}), 201



if __name__ == '__main__':
  app.run()

