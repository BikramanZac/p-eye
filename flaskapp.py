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

counter = 0

def recompile_image(encoded):
    global counter
    # decode the encoded string of image
    data = base64.b64decode(request.json['encode'])  

    # assume data contains your decoded image  http://stackoverflow.com/a/3715530
    file_like = cStringIO.StringIO(data)
    pil_img = PIL.Image.open(file_like)
    photo_file = "pilpic" + str(counter) + ".jpg"
    pil_img.save(photo_file)
    counter += 1
    return photo_file

def delete_pictures_and_save_results(label):
    global counter
    #delete pictures that were saved
####os.system('rm pilpic*.jpg')
####os.system('rm cropped_pilpic*.jpg')

    # create a new dictionary that contains the generated label 
    image = {
        'id': images[-1]['id'] + 1,   # guarantee unique id 
        'label': label   # add a label that got the highest score from recognition
    }

    #append the created dictionary to the exisitng data
    images.append(image)

@app.route('/')
def hello_world():
    return 'Hello from Flask!'

@app.route('/todo/api/v1.0/images', methods=['GET'])
def get_images():
    return jsonify({'images': images})

# this POST request is only for wireless communication
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

    # decode and restore the image and save as "pilpic.jpg" and return this name     
    photo_file = recompile_image(request.json['encode'])       
    
    string = ""
    
    google = GoogleApi(photo_file)    
    
    # if there is a face in the picture
    if(google.is_face() == True):
    	string = "the facial expression is " + google.get_face() +" "    
	  
        # delete pictures that were saved and create a new dictionary that contains the generated label 
        delete_pictures_and_save_results(string)
            
        # return the label in json type       
        return jsonify({'Hi': string}), 201

    # if there is some text in the picture
    if(google.is_text() == True):       
    	text = "the text is " + google.get_text() 
	
      	# detect color and crop the picture then 
        # return 0, 1, 2 depending on the color recognition.three_color_detect_and_crop_image()
      	which_color = recognition.color_detect_and_crop_image(photo_file)
      	# if there is some text and a green contour	
      	if(which_color == 1):  # 1: green
      		  text = "the text is " + recognition.get_text(photo_file)

      	string = string + text

    string = string + "the object is " + recognition.get_label(photo_file)

    #strip '\n' in the string
    string = string.replace('\n',' ')

    # delete pictures that were saved and create a new dictionary that contains the generated label 
    delete_pictures_and_save_results(string)

    # return the label in json type
    return jsonify({'Hi': string}), 201



#these following POST requests are specifically for the android app
@app.route('/todo/api/v1.0/images/label', methods=['POST'])
def label_recognition():
    if not request.json or not 'encode' in request.json:
        abort(400)

    photo_file = recompile_image(request.json['encode'])         
    string = "the object is " + recognition.get_label(photo_file)    
    string = string.replace('\n',' ')    
    delete_pictures_and_save_results(string)    

    # return the label in json type       
    return jsonify({'Hi': string}), 201



@app.route('/todo/api/v1.0/images/text', methods=['POST'])
def text_recognition():
    if not request.json or not 'encode' in request.json:
        abort(400)

    photo_file = recompile_image(request.json['encode'])           
    google = GoogleApi(photo_file)
    string = "the text is " + google.get_text()  
    
    which_color = recognition.color_detect_and_crop_image(photo_file)    
    if(which_color == 1):  # 1: green
        string = "the text is " + recognition.get_text(photo_file)
        
    string = string.replace('\n',' ')    
    delete_pictures_and_save_results(string)
          
    return jsonify({'Hi': string}), 201

@app.route('/todo/api/v1.0/images/face', methods=['POST'])
def facial_expresion_recognition():
    if not request.json or not 'encode' in request.json:
        abort(400)

    photo_file = recompile_image(request.json['encode'])           
    google = GoogleApi(photo_file)

    string = "the facial expression is " + google.get_face() +" "    
    delete_pictures_and_save_results(string)  

    return jsonify({'Hi': string}), 201

if __name__ == '__main__':
  app.run(host='0.0.0.0', port = 6000)
