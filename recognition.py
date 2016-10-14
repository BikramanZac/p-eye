
import base64
import cStringIO
import PIL.Image
import urllib2 as urllib
import io
import cv2
import numpy
import imutils
import os
import sys


from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

# define the lower and upper boundaries of the "green"
# ball in the HSV color space

# text detection
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)

# still available
redLower = (160, 117, 0)
redUpper = (192, 255, 255)

# still available
blueLower = (99, 70, 0)
blueUpper= (119, 255, 255)

# For Text detection
def color_detect_and_crop_image(photo_file):
    frame = cv2.imread(photo_file)
    frame = imutils.resize(frame, width=500)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask_green = cv2.inRange(hsv, greenLower, greenUpper)
    mask_green = cv2.erode(mask_green, None, iterations=2)
    mask_green = cv2.dilate(mask_green, None, iterations=2)
 	
    
    mask_red = cv2.inRange(hsv, redLower, redUpper)
    mask_red = cv2.erode(mask_red, None, iterations=2)
    mask_red = cv2.dilate(mask_red, None, iterations=2)

    mask_blue = cv2.inRange(hsv, blueLower, blueUpper)
    mask_blue = cv2.erode(mask_blue, None, iterations=2)
    mask_blue = cv2.dilate(mask_blue, None, iterations=2) 
	
    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts_green = cv2.findContours(mask_green.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
    cnts_green = cnts_green[0] if imutils.is_cv2() else cnts_green[1]
    
    
    cnts_red = cv2.findContours(mask_red.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
    cnts_red = cnts_red[0] if imutils.is_cv2() else cnts_red[1]

    cnts_blue = cv2.findContours(mask_blue.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
    cnts_blue = cnts_blue[0] if imutils.is_cv2() else cnts_blue[1]
	

<<<<<<< HEAD
	
    
=======
>>>>>>> 917edba5e4e0cabb88f3b6b582fe8f71e8370ae3
    # only proceed if at least one red contour was found
    if len(cnts_red) > 0:
        print "a contour is found!!"
        c = max(cnts_red, key=cv2.contourArea)
        #((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        cX = int(M["m10"] / M["m00"]) 
        cY = int(M["m01"] / M["m00"]) 

        #frame.shape rows, colomn, color
        #print frame.shape
        width = frame.shape[1]
        height = frame.shape[0]
        
        #some parms are multiplied or devided for preserving texts in the picture
        #they still might need to be twicked little bit
        crop_img = frame[cY/10:(cY), (cX):(width-cX/2)]
        # crop_img = frame[(height-cY):(cY), (cX):(width-cX)]  #original cropping
        # Crop from x, y, w, h -> 100, 200, 300, 400
        # NOTE: its img[y: y + h, x: x + w] and *not* img[x: x + w, y: y + h]
        #print crop_img.shape    
        cv2.imwrite("cropped_"+ photo_file, crop_img) 

        return 0       
    
    # only proceed if at least one blue contour was found
    if len(cnts_blue) > 0:
=======
        return 0
    
    # only proceed if at least one green contour was found
    if len(cnts_green) > 0:

        print "a contour is found!!"
        c = max(cnts_blue, key=cv2.contourArea)
        #((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        cX = int(M["m10"] / M["m00"]) 
        cY = int(M["m01"] / M["m00"]) 

        #frame.shape rows, colomn, color
        #print frame.shape
        width = frame.shape[1]
        height = frame.shape[0]
        
        #some parms are multiplied or devided for preserving texts in the picture
        #they still might need to be twicked little bit
        crop_img = frame[cY/10:(cY), (cX):(width-cX/2)]
        # crop_img = frame[(height-cY):(cY), (cX):(width-cX)]  #original cropping
        # Crop from x, y, w, h -> 100, 200, 300, 400
        # NOTE: its img[y: y + h, x: x + w] and *not* img[x: x + w, y: y + h]
        #print crop_img.shape    
        cv2.imwrite("cropped_"+ photo_file, crop_img) 

        return 2    

	# only proceed if at least one green contour was found
    if len(cnts_green) > 0:

        return 1
    
    # only proceed if at least one blue contour was found
    if len(cnts_blue) > 0:

        print "a contour is found!!"
        c = max(cnts_green, key=cv2.contourArea)
        #((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        cX = int(M["m10"] / M["m00"]) 
        cY = int(M["m01"] / M["m00"]) 

        #frame.shape rows, colomn, color
        #print frame.shape
        width = frame.shape[1]
        height = frame.shape[0]
        
        #some parms are multiplied or devided for preserving texts in the picture
        #they still might need to be twicked little bit
        crop_img = frame[cY/10:(cY), (cX):(width-cX/2)]
        # crop_img = frame[(height-cY):(cY), (cX):(width-cX)]  #original cropping
        # Crop from x, y, w, h -> 100, 200, 300, 400
        # NOTE: its img[y: y + h, x: x + w] and *not* img[x: x + w, y: y + h]
        #print crop_img.shape    
        cv2.imwrite("cropped_"+ photo_file, crop_img) 
        return 1

    
# open the photo and send a request to Google API. then get the response return the text
def get_text(photo_file):
    """Run a label request on a single image"""

    # [START authenticate]
    credentials = GoogleCredentials.get_application_default()
    service = discovery.build('vision', 'v1', credentials=credentials)
    # [END authenticate]

    #crop_image(photo_file)  #no longer needed

    photo_file = "cropped_"+ photo_file
    # [START construct_request]
    try:
        with open(photo_file, 'rb') as image:
            image_content = base64.b64encode(image.read())
            service_request = service.images().annotate(body={
                'requests': [{
                    'image': {
                        'content': image_content.decode('UTF-8')
                    },
                    'features': [{
                        'type': 'TEXT_DETECTION',
                        'maxResults': 1
                    }]
                }]
            })
            # [END construct_request]
            # [START parse_response]
            response = service_request.execute()
            text = response['responses'][0]['textAnnotations'][0]['description']

            print('Found label: %s for %s' % (text, photo_file))
            # [END parse_response]
            return text
    except:
        return "sth wrong with text"


            print('Found label: %s for %s' % (label, photo_file))
            # [END parse_response]
            return text
    except:
        return "couldn't find any text!"


def get_label(photo_file):
    """Run a label request on a single image"""

    # [START authenticate]
    credentials = GoogleCredentials.get_application_default()
    service = discovery.build('vision', 'v1', credentials=credentials)
    # [END authenticate]

    # [START image cropping]
    frame = cv2.imread(photo_file)
    #frame.shape = (rows, colomn, color)
    
    width = frame.shape[1]
    height = frame.shape[0]

    cX = width/2 
    cY = height/2
    parameter = 0.55	# decrease the number to narrow the picture down
    x = cX - (width-cX)*parameter
    y = cY - (height-cY)*parameter

    w = (width-cX)*parameter*2
    h = (height-cY)*parameter*2

    # the parameter is set to 0.6. It works fine but 
    # it still might need some twicks
    crop_img = frame[y : y + h, x : x + w]
    # Crop from x, y, w, h -> 100, 200, 300, 400
    # NOTE: its img[y: y + h, x: x + w] and *not* img[x: x + w, y: y + h]
     
    cv2.imwrite("cropped_"+ photo_file, crop_img) 
    # [END image cropping]

    photo_file = "cropped_"+ photo_file  

    # [START construct_request]
    try:
        with open(photo_file, 'rb') as image:
            image_content = base64.b64encode(image.read())
            service_request = service.images().annotate(body={
                'requests': [{
                    'image': {
                        'content': image_content.decode('UTF-8')
                    },
                    'features': [{
                        'type': 'LABEL_DETECTION',
                        'maxResults': 1
                    }]
                }]
            })
            # [END construct_request]
            # [START parse_response]
            response = service_request.execute()
            label = response['responses'][0]['labelAnnotations'][0]['description']
            print('Found label: %s for %s' % (label, photo_file))
            # [END parse_response]
            return label
    except:

        return "something wrong with recognizting objects"
    
def detect_face(photo_file):
    """Run a label request on a single image"""

    # [START authenticate]
    credentials = GoogleCredentials.get_application_default()
    service = discovery.build('vision', 'v1', credentials=credentials)
    # [END authenticate]
        
    # [START construct_request]
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
                        'maxResults': 1
                    }]
                }]
            })
            # [END construct_request]
            # [START parse_response]
            response = service_request.execute()
            dictionary = response['responses'][0]['faceAnnotations'][0]                       

            for e in dictionary.keys():
                if (dictionary[e] == "VERY_LIKELY"):
                	emotion = e                     

            #print ("VERY_LIKELY" in dictionary.values())
            return emotion
           
    # If there is no face in the picture, it throws an keyError error     
    except:
        return 0



        return "couldn't find a label!"



def crop_image(photo_file):   

    # grab the next frame from the video stream, resize the
    # frame, and convert it to the HSV color space
    frame = cv2.imread(photo_file)
    frame = imutils.resize(frame, width=500)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    
    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)


    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]
    center = None

    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
            
        print "a contour is found!!"
        c = max(cnts, key=cv2.contourArea)
        #((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        cX = int(M["m10"] / M["m00"]) 
        cY = int(M["m01"] / M["m00"]) 

        #frame.shape rows, colomn, color
        #print frame.shape
        width = frame.shape[1]
        height = frame.shape[0]
        
        #some parms are multiplied or devided for preserving texts in the picture
        #they still might need to be twicked little bit
        crop_img = frame[cY/10:(cY), (cX):(width-cX/2)]
        # crop_img = frame[(height-cY):(cY), (cX):(width-cX)]  #original cropping
        # Crop from x, y, w, h -> 100, 200, 300, 400
        # NOTE: its img[y: y + h, x: x + w] and *not* img[x: x + w, y: y + h]
        #print crop_img.shape    
        cv2.imwrite("cropped_"+ photo_file, crop_img) 


    

