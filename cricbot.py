import urllib.request
import cv2
import numpy as np
import time
import imutils
import argparse
from collections import deque
from imutils.video import VideoStream


import serial
print("Start")
port="/dev/rfcomm6" 	#This will be different for various devices. 
bluetooth=serial.Serial(port, 9600)	#Start communications with the bluetooth 
print("Connected")
bluetooth.flushInput() 


# Replace the URL with your own IPwebcam shot.jpg IP:port
url = 'http://[2401:4900:2322:fa9:4faf:f37d:b50d:be5e]:8080/shot.jpg'

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
                help="http://10.42.0.20:8080/video")
ap.add_argument("-b", "--buffer", type=int, default=64,
                help="max buffer size")
args = vars(ap.parse_args())

#ballColors
ballLowerColor = (140, 100, 140)
ballUpperColor = (230, 230, 230)
pts = deque(maxlen=args["buffer"])



while True:
    imgResp = urllib.request.urlopen(url)
    imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
    frame = cv2.imdecode(imgNp, -1)
    
# grab the current frame
    # frame = vs.read()
# handle the frame from VideoCapture or VideoStream
# frame = frame[1] if args.get(l, False) else frame
# if we are viewing a video and we did not grab a frame,
# then we have reached the end of the video
# if frame is None:
    # break
# resize the frame, blur it, and convert it to the HSV
# color space

    frame = imutils.resize(frame, width=600)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    

# a series of dilations and erosions to remove any small
# blobs left in the mask
    mask = cv2.inRange(hsv, ballLowerColor, ballUpperColor)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)


# find contours in the mask and initialize the current
# (x, y) center of the ball

    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None
    
# only proceed if at least one contour was found
    if len(cnts) > 0:
	# find the largest contour in the mask, then use
	# it to compute the minimum enclosing circle and
	# centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
	#output center of the circle to terminal
	
        i=center[0]
        j=center[1]
        radius=int(radius)
        print('{:0>3}'.format(center[0]),'{:0>3}'.format(center[1]),'{:0>3}'.format(radius))
        
        #syntax: bluetooth.write(str.encode(str(center[0])))
        i=6
        
        bluetooth.write(b"X"+str.encode(str('{:0>3}'.format(center[0])))+b"Y"+str.encode(str('{:0>3}'.format(center[1])))+b"R"+str.encode(str('{:0>3}'.format(radius))))
        time.sleep(1)
        
        
	#delay the output of the printing accordingly
	#time.sleep(1)
	# only proceed if the radius meets a minimum size
	
        if radius > 10:
       	# draw the circle and centroid on the frame,
       	# then update the list of tracked points
            cv2.circle(frame, (int(x), int(y)), int(radius),
                       (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
	# update the points queue
    pts.appendleft(center)

# loop over the set of tracked points
    for i in range(1, len(pts)):
	# if either of the tracked points are None, ignore
	# them
        if pts[i - 1] is None or pts[i] is None:
            continue
	# otherwise, compute the thickness of the line and
	# draw the connecting lines
        thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)

	#program to draw line of trajectory
        cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
	# show the frame to our screen
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    
# if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break
# if we are not using a video file, stop the camera video stream
if not args.get(l, False):
    vs.stop()
# otherwise, release the camera
else:
    vs.release()
# close all windows

bluetooth.close() 
print("Done")
cv2.destroyAllWindows()
