"""
WHAT IS DOES

it handles cropping images and finding contours using OpenCV for object and text recognition.
those functions are called from flaskapp.py which is run in virtual linux server deployed in Amazon Web service
"""
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
import math


from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

# define the lower and upper boundaries of the "green"
# ball in the HSV color space

# still available
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)

# text detection
orangeLower = (0, 140, 118)
orangeUpper = (10, 235, 195)

# still available
redLower = (160, 117, 0)
redUpper = (192, 255, 255)

# still available
blueLower = (99, 70, 0)
blueUpper= (119, 255, 255)

# it finds a orange colored contour(currently) and crops the image based on the position of the centor of the contour
# this function is used for text recognition
def color_detect_and_crop_image(photo_file):
    frame = cv2.imread(photo_file)
    frame = imutils.resize(frame, width=500)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask_green = cv2.inRange(hsv, orangeLower, orangeUpper)
    mask_green = cv2.erode(mask_green, None, iterations=2)
    mask_green = cv2.dilate(mask_green, None, iterations=2)

    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts_green = cv2.findContours(mask_green.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
    cnts_green = cnts_green[0] if imutils.is_cv2() else cnts_green[1]

    if len(cnts_green) > 0:
        print "a green contour is found!!"
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
        #crop_img = frame[cY/10:(cY), (cX):(width-cX/2)]
        crop_img = frame[(height-cY/2):(cY), (cX):(width-cX/2)]  #original cropping
        # Crop from x, y, w, h -> 100, 200, 300, 400
        # NOTE: its img[y: y + h, x: x + w] and *not* img[x: x + w, y: y + h]
        #print crop_img.shape    
        cv2.imwrite("cropped_"+ photo_file, crop_img) 
        return 1
    return 0


# once the cropping is done it will send a request to Google API with the cropped image. 
# then get the response back and return the text
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
        return " not found "


# crop images focusing on the center of the image in certain ratio 
# and send those images to Google Vision API to get the label
def get_label(photo_file):
    """Run a label request on a single image"""

    # [START authenticate]
    credentials = GoogleCredentials.get_application_default()
    service = discovery.build('vision', 'v1', credentials=credentials)
    # [END authenticate]

    # [START image cropping]
    image = cv2.imread(photo_file)
    #frame.shape = (rows, colomn, color)
    
    width = image.shape[1]
    height = image.shape[0]
    centerX = width/2
    centerY = height/2
    shortest_cY = centerY
    shortest_cX = centerX
    shortest = 9999

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]

    # find contours in the thresholded image
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]
	
    try:
	    # loop over the contours
    	for c in cnts:
    		# compute the center of the contour
    		M = cv2.moments(c)
    		cX = int(M["m10"] / M["m00"])
    		cY = int(M["m01"] / M["m00"])

    		# compute distance between center of image and center of objects
    		dist = math.hypot(centerX - cX, centerY - cY)		
    		if(shortest > dist):		
    			shortest = dist
    			shortest_cY = cY
    			shortest_cX = cX
    except:
	    pass
    
    parameter = 0.7	# decrease the number to crop more space 
    x = shortest_cX - (width-shortest_cX)*parameter
    y = shortest_cY - (height-shortest_cY)*parameter

    w = (width-shortest_cX)*parameter*2  
    h = (height-shortest_cY)*parameter*3 
    crop_img = image[y : y + h, x : x + w]
    cv2.imwrite("cropped_"+ photo_file, crop_img)
    # [END image cropping]

    photo_file = "cropped_"+ photo_file  
    string = ""
    maxresults = 3
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
                        'maxResults': maxresults
                    }]
                }]
            })
            # [END construct_request]
            # [START parse_response]
            response = service_request.execute()
            #label = response['responses'][0]['labelAnnotations'][0]['description']
            
            for key in response['responses'][0]['labelAnnotations']:
                #print key                
                string = string + key['description'] + " or "                           

            print('Found labels: %s for %s' % (string, photo_file))
            return string[0:-3]
            
            
            
    except:
        return "not found "


def old_get_label(photo_file):
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
    parameter = 0.8	# decrease the number to crop more space 
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
        return "not found "


# no longer used
def three_color_detect_and_crop_image(photo_file):
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
	

	
    
    # only proceed if at least one red contour was found
    if len(cnts_red) > 0:
        print "a red contour is found!!"
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
        print "a blue contour is found!!"
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
        print "a green contour is found!!"
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



"""    
def detect_face(photo_file):
    

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
"""



"""
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

"""    
