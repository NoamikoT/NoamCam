import time

import cv2
from datetime import datetime

cap = cv2.VideoCapture(cv2.CAP_DSHOW)

# cap.set(cv2.CAP_PROP_FRAME_WIDTH,1920)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT,1080)

fourcc = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')
videoWriter = cv2.VideoWriter('video5.avi', fourcc, 20.0, (600, 300))


# Check if the webcam is opened correctly
if not cap.isOpened():
    raise IOError("Cannot open webcam")

# font
font = cv2.FONT_HERSHEY_PLAIN

# org
org = (10, 280)

# fontScale
fontScale = 1

# Blue color in BGR
color = (255, 0, 0)

# Line thickness of 2 px
thickness = 1


while True:
    ret, frame = cap.read()
    frame = cv2.resize(frame, None, fx=1, fy=1, interpolation=cv2.INTER_AREA)
    if ret:

        # Using cv2.putText() method
        frame = cv2.putText(frame, datetime.now().strftime("%H:%M:%S"), org, font, fontScale, color, thickness, cv2.LINE_AA)

        cv2.imshow('Video', frame)
        videoWriter.write(frame)
    c = cv2.waitKey(1)
    if c == 27:
        break

cap.release()
videoWriter.release()
cv2.destroyAllWindows()
