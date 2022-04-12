import os
import cv2
import threading
import queue


class ClientCamera:

    def __init__(self, frame_q, face_q):
        """
        Constructor
        """

        self.frame_q = frame_q
        self.face_q = face_q
        self.cap = None
        self.face_cascade = None
        self.path = None
        self.count = 0
        self.camera_active = False
        self.detection_active = False

        self._init_camera()

        threading.Thread(target=self._operate_camera, ).start()

    def _init_camera(self):
        """
        Starting the camera
        """

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
        """
        Starting the camera
        """

        self.camera_active = True

    def stop_camera(self):
        """
        Stopping the camera
        """

        self.camera_active = False

        # Release the VideoCapture object
        self.cap.release()

    def _operate_camera(self):
        """
        The function handles the camera, takes frames and pushes them into the queue, calls face detection if needed
        """

        while True:
            while self.camera_active:
                # Read the frame
                _, img = self.cap.read()

                if self.detection_active:
                    img = self._face_detection(img)

                self.frame_q.put(img)

    def _face_detection(self, img):
        """
        The function gets an image (a frame) and detects human faces in it
        :param img: The frame to check for faces
        :type img: Numpy object
        :return: The image with a square around the face
        :rtype: Numpy object
        """

        # Converting to gray scale (The face detection only works with pictures in gray scale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Detecting faces in the frame
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

        # Drawing a rectangle around detected faces, and capturing a picture of the face
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (50, 50, 250), 2)

            # face = gray[y:y + h, x:x + w]
            # face_resize = cv2.resize(face, (500, 500))
            cv2.imwrite('% s/% s.png' % (self.path, self.count), img)
            self.face_q.put('% s/% s.png' % (self.path, self.count))

            self.count += 1
            print(str(type(img)))
            return img

    def start_detection(self):
        """
        Calling this function starts face detection
        :return:
        """

        self.detection_active = True

    def stop_detection(self):
        """
        Calling this function stops face detection
        :return:
        """

        self.detection_active = False


# Testing the ClientCamera Class
if __name__ == '__main__':

    frame_q = queue.Queue()

    face_q = queue.Queue()

    new_camera = ClientCamera(frame_q, face_q)

    new_camera.start_camera()

    while True:
        img = frame_q.get()

        if img is not None:
            # Displaying the frame
            cv2.imshow('img', img)

        # If the ESC key is pressed, the program stops
        k = cv2.waitKey(30) & 0xff
        if k == 27:
            print("ESC")
            new_camera.stop_camera()
            break

        # Keys to start and stop face detection

        # Ascii 8 = Backspace
        elif k == 8:
            new_camera.start_detection()

        # Ascii 10 = Enter
        elif k == 10:
            new_camera.stop_detection()
