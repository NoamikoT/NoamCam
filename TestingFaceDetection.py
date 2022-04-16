import os
import cv2

# Loading the cascade
# The cascade xml file is a set of input data that allows to detect faces in pictures
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Capturing video from the webcam
cap = cv2.VideoCapture(1)


# Creating the video file to which the stream is being recorded
fourcc = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')
VideoWriter = cv2.VideoWriter('video.avi', fourcc, 10.0, (640, 480))

datasets = 'datasets'
sub_data = 'Noam'

count = 0

path = os.path.join(datasets, sub_data)
if not os.path.isdir(path):
    os.mkdir(path)

while True:
    # Read the frame
    _, img = cap.read()

    # Converting to gray scale (The face detection only works with pictures in gray scale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detecting faces in the frame
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    # Drawing a rectangle around detected faces, and capturing a picture of the face
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (50, 50, 250), 2)
        face = gray[y:y + h, x:x + w]
        face_resize = cv2.resize(face, (500, 500))
        cv2.imwrite('% s/% s.png' % (path, count), face_resize)
        count += 1

    # Displaying the frame
    cv2.imshow('img', img)

    # Saving the frame to the video
    VideoWriter.write(img)

    # If the ESC key is pressed, the program stops
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

# Release the VideoCapture object
cap.release()

# Release the VideoWriter object
VideoWriter.release()
