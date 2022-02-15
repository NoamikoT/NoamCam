import cv2

# Load the cascade
# The cascade xml file is a set of input data that allows to detect faces in pictures
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Capturing video from the webcam
cap = cv2.VideoCapture(0)

# Using a video file instead:
# cap = cv2.VideoCapture('filename.mp4')

# Creating the video file to which the stream is being recorded
fourcc = cv2.VideoWriter_fourcc('X','V','I','D')
VideoWriter = cv2.VideoWriter('C:/Users/User/PycharmProjects/NoamCamCodeFromGit/video.avi', fourcc, 10.0, (640, 480))


while True:
    # Read the frame
    _, img = cap.read()

    # Converting to grayscale (The face detection only works with pictures in grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detecting faces in the frame
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    # Drawing a rectangle around detected faces
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 255, 0), 2)

    # Displaying the frame
    cv2.imshow('img', img)

    # Saving the frame to the video
    VideoWriter.write(img)

    # If the ESC key is pressed, the program stops
    k = cv2.waitKey(30) & 0xff
    if k==27:
        break

# Release the VideoCapture object
cap.release()

# Release the VideoWriter object
VideoWriter.release()
