import pickle
import sys
import threading
import cv2
import Setting
import ClientComms
from pubsub import pub
import Alarm


class ClientCamera:
    """A class for using and controlling the camera"""
    def __init__(self, video_comm, port):

        # The communication objects with the server
        self.video_comm = video_comm
        self.stills_comm = ClientComms.ClientComms(port)

        # Whether the camera is running or not
        self.running = False

        # Whether the zoom in on or not
        self.zoom = False

        # Creating the alarm object, used to sound an alarm when a face is found
        self.siren_obj = Alarm.AlarmSound()

        # Whether an alarm should be played or not
        self.siren = False

        # Whether an alarm is playing
        self.play_on = False

        # Whether face recognition is on or off
        self.running_recognition = False

        # Parameters needed for using of the camera
        self.encode_param = None
        self.cap = None

        # Subscribing to a pubsub telling when to close the camera
        pub.subscribe(self.close_camera, "CLOSE CAMERA")

        # Initiating the camera in a thread
        threading.Thread(target=self._init_camera, ).start()

    def start_camera(self):
        """
        The function sets the state of running to True for it to run
        """
        self.running = True

    def stop_camera(self):
        """
        The function sets the state of running to False for it to stop
        """
        self.running = False

    def close_camera(self):
        """
        The function releases the capture object so that the camera would be free for next use
        """
        self.cap.release()

    def _init_camera(self):
        """
        Starting the camera
        """

        try:
            # Capturing video from the webcam
            self.cap = cv2.VideoCapture(cv2.CAP_DSHOW)
        except Exception as e:
            sys.exit("Check camera")
        else:

            self.encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]

            # Load the cascade
            # The cascade xml file is a set of input data that allows to detect faces in pictures
            self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

            # Running the function that gets a processes frames in a thread
            threading.Thread(target=self._operate_camera, ).start()

    def _operate_camera(self):
        """
        The function handles the camera, takes frames and pushes them into the queue, calls face detection if needed
        """
        while True:
            count = 0
            while self.running:
                # Reading the frame
                ret, frame = self.cap.read()
                # Checking that the frame isn't empty
                if ret or frame is not None:
                    # If the zoom is enabled, resizing the frame to 1600, 900
                    if self.zoom:
                        frame = cv2.resize(frame, dsize=(1600, 900), interpolation=cv2.INTER_AREA)
                    # If the zoom is disabled, resizing the frame to 600, 300 instead
                    else:
                        frame = cv2.resize(frame, dsize=(600, 300), interpolation=cv2.INTER_AREA)
                    # Encoding the image
                    result, image = cv2.imencode('.jpg', frame, self.encode_param)
                    data = pickle.dumps(image, 0)

                    # Sending a frame only every 5 frames
                    if count % 2 == 0:
                        # If face recognition is enabled running the frame through the face recognition
                        if self.running_recognition:
                            frame = self._face_detection(frame)
                            result, image = cv2.imencode('.jpg', frame, self.encode_param)
                            data = pickle.dumps(image, 0)

                        # Sending the frame to the server
                        self.video_comm.send_video(data)

                        # Resetting the count
                        count = 0
                    # Upping the count by 1
                    count += 1

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                else:
                    # If the frame is empty, there's a problem, so rebooting the camera
                    self.close_camera()
                    self.cap = cv2.VideoCapture(cv2.CAP_DSHOW)
                    print("Rebooted the camera")

    def _face_detection(self, frame):
        """
        The function gets an image (a frame) and detects human faces in it
        :param frame: The frame to check for faces
        :type frame: Numpy object
        :return: The same image with a square around the face
        :rtype: Numpy object
        """

        # Converting to gray scale (The face detection only works with pictures in gray scale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detecting faces in the frame
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

        # Drawing a rectangle around detected faces, and capturing a picture of the face (Only gets in the loop if faces were found)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (50, 50, 250), 2)

            face = gray[y:y + h, x:x + w]
            face_resize = cv2.resize(face, (500, 500))
            cv2.imwrite(f"{Setting.PIC_PATH}pic.png", face_resize)
            # Sending the picture to the server
            self.stills_comm.send_file(f"{Setting.PIC_PATH}pic.png")
            # (In here it means a face was detected) If the siren is supposed to be playing, and not playing yet, activating it
            if self.siren and not self.play_on:
                self.siren_obj.play_alarm()
                self.play_on = True
            # Returning the frame
            return frame

        # If it gets here, that means no faces were detected, so if the alarm is playing, turning it off
        if self.play_on:
            self.siren_obj.stop_alarm()
            self.play_on = False

        # Returning the frame
        return frame

    def start_zoom(self):
        """
        The function sets the zoom boolean to True
        """
        self.zoom = True

    def stop_zoom(self):
        """
        The function sets the zoom boolean to False
        """
        self.zoom = False

    def set_siren_on(self):
        """
        The function sets the siren boolean to True
        """
        self.siren = True

    def set_siren_off(self):
        """
        The function sets the siren boolean to False, and if it's playing, turning it off
        """
        self.siren = False
        if self.play_on:
            self.siren_obj.stop_alarm()
            self.play_on = False

    def start_detection(self):
        """
        Calling this function starts face detection
        """
        self.running_recognition = True

    def stop_detection(self):
        """
        Calling this function stops face detection
        :return:
        """
        self.running_recognition = False

        if self.play_on:
            self.siren_obj.stop_alarm()
            self.play_on = False
