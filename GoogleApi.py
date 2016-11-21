#export GOOGLE_APPLICATION_CREDENTIALS=Google_vision_api-6f831dbb290a.json
import base64
import cStringIO
import urllib2 as urllib
import os
import sys
import argparse

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

"""
GoogleApi Class
    it gets a string of a photo name to create an object.
    then sends a HTTP request to Google Cloud API for image recognitions 
    (mainly the purpose is to figure out whether the picture has some text or faces in it.)   
"""
class GoogleApi(object):
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
                          "maxResults":1            # doesn't need it
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
            self.label = label
            #print "textAnnotations" in label
            self.bool_text = "textAnnotations" in label
            self.bool_face = "faceAnnotations" in label
            
            #print('Found label: %s for %s' % (label, photo_file))
           
             
    def is_face(self):
        return self.bool_face

    def is_text(self):
        return self.bool_text
    
    def get_text(self):
        #self.label = response['responses'][0]
        """
        if not self.bool_text:
            return None
        """
        return self.label['textAnnotations'][0]['description']

    def get_face(self):
        #self.label = response['responses'][0]
        """
        if not self.bool_face:
            return None
        """
        dictionary = self.label['faceAnnotations'][0]                       

        for e in dictionary.keys():
            if (dictionary[e] == "VERY_LIKELY"):
                emotion = e                     

        #print ("VERY_LIKELY" in dictionary.values())
        return emotion
    """
    def get_label(self):
        #self.label = response['responses'][0]
        return self.label['labelAnnotations'][0]['description']
    """

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('image_file', help='The image you\'d like to label.')
    args = parser.parse_args()
    google = GoogleApi(args.image_file)
    print google.is_face()
    print google.get_text()
    print google.is_text()    
    print google.get_face()
    print google.get_label()
