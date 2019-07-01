import numpy as np
import cv2

file = "cut.MP4"

cap = cv2.VideoCapture(file)
fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()

counter = 0

while True:
    ret, frame = cap.read()

    fgmask = fgbg.apply(frame)

    cv2.imshow('frame',fgmask)
    k = cv2.waitKey(30) & 0xff
    k=5
    if k == 27:
        break
        
    counter +=1

cap.release()
cv2.destroyAllWindows()