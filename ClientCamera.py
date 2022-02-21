import os
import time

import cv2
import threading
import queue


class ClientCamera:

    def __init__(self, frame_q):
        """
        Constructor
        """

        self.frame_q = frame_q
        self.cap = None
        self.face_cascade = None
        self.path = None
        self.count = 0
        self.camera_active = False
        self.detection_active = False

        self._init_camera()

        threading.Thread(target=self._operate_camera, ).start()

    def _init_camera(self):

        # Capturing video from the webcam
        self.cap = cv2.VideoCapture(0)

        # Load the cascade
        # The cascade xml file is a set of input data that allows to detect faces in pictures
        self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

        datasets = 'datasets'
        sub_data = 'Noam'

        self.path = os.path.join(datasets, sub_data)
        if not os.path.isdir(self.path):
            os.mkdir(self.path)

    def start_camera(self):

        self.camera_active = True

    def stop_camera(self):

        self.camera_active = False

        # Release the VideoCapture object
        self.cap.release()

    def _operate_camera(self):

        while True:
            while self.camera_active:
                # Read the frame
                _, img = self.cap.read()

                self.frame_q.put(img)

                if self.detection_active:
                    self._face_detection(img)

                print(self.camera_active)

    def _face_detection(self, img):

        # Converting to gray scale (The face detection only works with pictures in gray scale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Detecting faces in the frame
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

        # Drawing a rectangle around detected faces, and capturing a picture of the face
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (50, 50, 250), 2)
            face = gray[y:y + h, x:x + w]
            face_resize = cv2.resize(face, (500, 500))
            cv2.imwrite('% s/% s.png' % (self.path, self.count), face_resize)
            self.count += 1

    def start_detection(self):

        self.detection_active = True

    def stop_detection(self):

        self.detection_active = False



if __name__ == '__main__':

    frame_q = queue.Queue()

    new_camera = ClientCamera(frame_q)

    new_camera.start_camera()

    while True:
        img = frame_q.get()

        if not img is None:
            # Displaying the frame
            cv2.imshow('img', img)

        # If the ESC key is pressed, the program stops
        k = cv2.waitKey(30) & 0xff
        if k == 27:
            print("ESC")
            new_camera.stop_camera()
            break

        # Make face detection