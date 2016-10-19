#export GOOGLE_APPLICATION_CREDENTIALS=Google_vision_api-6f831dbb290a.json
import base64
import cStringIO
import PIL.Image
import urllib2 as urllib
import io
#import cv2
import numpy
#import imutils
import os
import sys
import argparse

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

"""
IT STARTS OFF WITH GOOGLE API RESPONSE

"""
class GoogleAPI(object):
    def __init__(self, photo_file):        
        self.bool_text = False
        self.bool_face = False

        credentials = GoogleCredentials.get_application_default()
        service = discovery.build('vision', 'v1', credentials=credentials)
        # [END authenticate]

        # [START construct_request]
        with open(photo_file, 'rb') as image:
            image_content = base64.b64encode(image.read())
            service_request = service.images().annotate(body={
                'requests': [{
                    'image': {
                        'content': image_content.decode('UTF-8')
                    },
                    "features":[
                        {
                          "type":"FACE_DETECTION",
                          "maxResults":1
                        },
                        {
                          "type":"LABEL_DETECTION",
                          "maxResults":1
                        },
                        {
                          "type":"TEXT_DETECTION",
                          "maxResults":1
                        }
                    ]
                }]
            })
            # [END construct_request]
            # [START parse_response]
            response = service_request.execute()
            #label = response['responses'][0]['labelAnnotations'][0]['description']
            label = response['responses'][0]
            #print "textAnnotations" in label
            self.bool_text = "textAnnotations" in label
            self.bool_face = "faceAnnotations" in label
            
            print('Found label: %s for %s' % (label, photo_file))
           
             
    def is_face(self):
        return self.bool_face
    def is_text(self):
        return self.bool_text
    
    def get_text(self):
        return ""

    def get_face(self):
        return ""

    def get_label(self):
        return ""


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('image_file', help='The image you\'d like to label.')
    args = parser.parse_args()
    google = GoogleAPI(args.image_file)
    print google.is_face()
    print google.is_text()
