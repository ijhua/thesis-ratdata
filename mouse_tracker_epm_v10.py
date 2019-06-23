# USAGE: open cmd line and navigate to filepath
# use command: python mouse_tracker_epm_v10.py 

# import the necessary packages
from collections import deque
import numpy as np
import argparse
import imutils
import cv2
from pandas import DataFrame, read_csv
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib
import tkinter as tk
from tkinter import filedialog

#creates filedialog to pick video file
root = tk.Tk()
root.withdraw()
dir_path = filedialog.askopenfilename(title = 'Select Video')

#requests user input for pixel boundaries of center square for EPM
top = int(input("Enter Y coordinate (pixels) of the top of the center square:  "))
bottom = int(input("Enter Y coordinate (pixels) of the bottom of the center square:  "))
left = int(input("Enter X coordinate (pixels) of the left side of the center square:  "))
right = int(input("Enter X coordinate (pixels) of the right side of the center square:  "))

#initializes list to store output data for pandas
c_data = []
#initializes frame counter
counter = 0

#defines the lower and upper boundaries of the mouse color range in HSV color space
#you may need to adjust these depending on lighting or mouse color
mouseLowerRange = (100,100,100)
mouseUpperRange = (200,200,200)

#initialize video capture based on filepath provided by user
camera = cv2.VideoCapture(dir_path)

#loops through frames until there are no more
while True:
    #retrieve the current frame
    (grabbed, frame) = camera.read()
    
    #checks if there are no more frames i.e. we have reached the end of video
    if dir_path and not grabbed:
        break
    
    #converts color formate from BGR to HSV.  Arguments are (image, conversion method)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    #constructs a binary mask converting all pixels within mouse color range to white
    #and all others to black
    mask = cv2.inRange(hsv, mouseLowerRange, mouseUpperRange)
    
    #runs mask through series of erosions and dialations to reduce noise on edges of mask
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    
    #find contours in the mask and initializes center of mouse
    #cnts is a numpy array
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None
    
    #checks that at least one contour was found
    if len(cnts) > 0:
        #finds the contour with the largest ares in mask and computes
        #the minimum enclosing circle and centroid
        c = max(cnts, key=cv2.contourArea)
        ((x,y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        
        #checks that radius is a minimum size before drawing circle
        if radius > 10:
            #draws circle and centroid in frame
            cv2.circle(frame, (int(x), int(y)), int(radius), (0,255,255),2)
            cv2.circle(frame, center, 5, (0,0,255), -1)
    
    #draws text showing current frame number
    cv2.putText(frame, "frame: {}".format(counter), (10,frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0,0,255), 1)
    
    #displays the frame and increments the frame counter
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    #converts mouse coordinate tuple into a list
    coord = list((x,y))
    
    #determines if the mouse center of mass is in the center, open, or closed arm based on input parameters
    if (coord[0] < left or coord[0] > right) and coord[1] > top and coord[1] < bottom:
        epm = "open_arm"
    elif coord[1] < top or coord[1] > bottom:
        epm = "closed_arm"
    else:
        epm = "center"
    
    #calculates the velocity over the last 10 frames and the distance from the last frame
    if (counter - 10) > 0:
        velocity = np.sqrt(((abs(coord[0] - (c_data[counter - 10][0]))**2) + (abs(coord[1] - (c_data[counter - 10][1]))**2)))
        distance = np.sqrt(((abs(coord[0] - (c_data[counter - 1][0]))**2) + (abs(coord[1] - (c_data[counter - 1][1]))**2)))
    else:
        velocity = 0
        distance = 0
        
    #adds the XY coordinates, frame number, radius of circle, velocity, distance, and EPM area to the c_data list
    c_data.append([coord[0],coord[1],counter,radius,velocity,distance,epm])
    print (c_data[counter])
    counter += 1
    
    #if user presses 'q' key, the loop ends
    if key == ord("q"):
        break
        
#uses pandas to write the mouse data to a csv
data_frame = pd.DataFrame(data = c_data, columns=['X','Y','frame','radius','velocity per 10 frames',"distance","location"])
data_frame.to_csv('mouse_data.csv',index=False,header=True)

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
    