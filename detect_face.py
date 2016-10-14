#!/usr/bin/env python


# [START import_libraries]
import argparse
import base64
import time
import cv2
import imutils
#import crop_image
import sys
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
# [END import_libraries]


def main(photo_file):
    """Run a label request on a single image"""

    # [START authenticate]
    credentials = GoogleCredentials.get_application_default()
    service = discovery.build('vision', 'v1', credentials=credentials)
    # [END authenticate]

    try:
        with open(photo_file, 'rb') as image:
            image_content = base64.b64encode(image.read())
            service_request = service.images().annotate(body={
                'requests': [{
                    'image': {
                        'content': image_content.decode('UTF-8')
                    },
                    'features': [{
                        'type': 'FACE_DETECTION',
                        'maxResults': 4
                    }]
                }]
            })
            # [END construct_request]
            # [START parse_response]
            response = service_request.execute()
            dictionary = response['responses'][0]['faceAnnotations'][0]
            
            emotion = ['joyLikehood','sorrowLikehood','surpriseLikehood',
            'angerLikelihood']
            likelihood = []

            for e in dictionary.keys():
                if (dictionary[e] == "VERY_LIKELY"):
                    print "highly "+ e 
            #print ("VERY_LIKELY" in dictionary.values())
            return "highly "+ e 
            #print('Found label: %s for %s' % (dictionary, photo_file))
            # [END parse_response]
            #print dictionary.keys()
            
    except:
        return 0
        #print "Unexpected error", sys.exc_info()[0]
        #return "something wrong!"




# [START run_application]
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('image_file', help='The image you\'d like to label.')
    args = parser.parse_args()
    main(args.image_file)
# [END run_application]