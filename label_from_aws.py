import base64
import cStringIO
import PIL.Image
import requests
import os
import json
import argparse
from espeak import ESpeak

def get_label(image):
    """
    1. encode binary data(image) to printable ASCII characeters
    2. send the encoded data to the server using REST POST method
    3. get the result from the server and print out the label
    """

    with open(image, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

        #print type(encoded_string)

    converts = base64.b64decode(encoded_string)
    file_like = cStringIO.StringIO(converts)     #for testing
    img = PIL.Image.open(file_like)

    url= "http://ec2-52-88-62-32.us-west-2.compute.amazonaws.com/todo/api/v1.0/images"    
    data = {'encode' : encoded_string }
    headers = {'Content-Type': 'application/json'}
    
    # make sure that the data is json type because the server only allows json type
    r = requests.post(url, data = json.dumps(data), headers = headers)

    # r is json type. r.json() convert json type to dic type
    dic_label = r.json()
    #print dic_label.values()[0]
    text = dic_label.values()[0]
    print text
    #es = ESpeak(word_gap=17 ,speed=160, voice='en-us+f8')
    #es.say(dic_label.values()[0])
    subprocess.call("pico2wave -w test.wav "+'\"'+text+'\"' ,shell=True)
    subprocess.call("aplay test.wav",shell=True)

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('image_file', help='The image you\'d like to label.')
    args = parser.parse_args()
    get_label(args.image_file)

    #get_label("pinklabel.jpg")

    #r = requests.get("http://localhost:5000/todo/api/v1.0/images/01.jpg")
    #r = requests.get("http://localhost:5000/todo/api/v1.0/images")


    
