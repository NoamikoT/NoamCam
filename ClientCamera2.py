import pickle
import sys
import threading
import cv2
import Setting
import ClientComms
import queue
from pubsub import pub
import Alarm


class ClientCamera:
    def __init__(self, video_comm, port):

        self.video_comm = video_comm
        self.stills_comm = ClientComms.ClientComms(port)
        self.running = False
        self.zoom = False
        self.siren_obj = Alarm.AlarmSound()

        self.siren = False
        self.play_on = False
        self.running_recognition = False

        self.encode_param = None
        self.cap = None

        pub.subscribe(self.close_camera, "CLOSE CAMERA")

        threading.Thread(target=self._init_camera, ).start()

    def start_camera(self):
        self.running = True

    def stop_camera(self):
        self.running = False

    def close_camera(self):
        print("Closed the camera")
        self.cap.release()

    def _init_camera(self):
        """
        Starting the camera
        """

        try:
            # Capturing video from the webcam
            self.cap = cv2.VideoCapture(cv2.CAP_DSHOW)
        except Exception:
            print("Couldn't connect to camera")
            sys.exit("Check camera")
        else:

            self.encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]

            # Load the cascade
            # The cascade xml file is a set of input data that allows to detect faces in pictures
            self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

            threading.Thread(target=self._operate_camera, ).start()

    def _operate_camera(self):
        """
        The function handles the camera, takes frames and pushes them into the queue, calls face detection if needed
        """
        while True:
            count = 0
            while self.running:
                # Read the frame
                ret, frame = self.cap.read()
                print(ret)
                if ret or frame is not None:
                    if self.zoom:
                        frame = cv2.resize(frame, dsize=(1600, 900), interpolation=cv2.INTER_AREA)
                    else:
                        frame = cv2.resize(frame, dsize=(600, 300), interpolation=cv2.INTER_AREA)
                    result, image = cv2.imencode('.jpg', frame, self.encode_param)
                    data = pickle.dumps(image, 0)

                    if count % 5 == 0:
                        if self.running_recognition:
                            frame = self._face_detection(frame)
                            result, image = cv2.imencode('.jpg', frame, self.encode_param)
                            data = pickle.dumps(image, 0)

                        self.video_comm.send_video(data)
                        count = 0
                    count += 1

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                else:
                    self.close_camera()
                    self.cap = cv2.VideoCapture(cv2.CAP_DSHOW)
                    print("Resetted the camera")

    def _face_detection(self, frame):
        """
        The function gets an image (a frame) and detects human faces in it
        :param frame: The frame to check for faces
        :type frame: Numpy object
        :return: The image with a square around the face
        :rtype: Numpy object
        """

        # Converting to gray scale (The face detection only works with pictures in gray scale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detecting faces in the frame
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

        # Drawing a rectangle around detected faces, and capturing a picture of the face
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (50, 50, 250), 2)

            face = gray[y:y + h, x:x + w]
            face_resize = cv2.resize(face, (500, 500))
            cv2.imwrite(f"{Setting.PIC_PATH}pic.png", face_resize)
            self.stills_comm.send_file(f"{Setting.PIC_PATH}pic.png")
            if self.siren and not self.play_on:
                self.siren_obj.play_alarm()
                self.play_on = True
            return frame
        if self.play_on:
            self.siren_obj.stop_alarm()
            self.play_on = False
        return frame

    def start_zoom(self):
        self.zoom = True

    def stop_zoom(self):
        self.zoom = False

    def set_siren_on(self):
        self.siren = True

    def set_siren_off(self):
        self.siren = False
        if self.play_on:
            self.siren_obj.stop_alarm()
            self.play_on = False

    def start_detection(self):
        """
        Calling this function starts face detection
        :return:
        """
        print("STARTING DETECTION")
        self.running_recognition = True

    def stop_detection(self):
        """
        Calling this function stops face detection
        :return:
        """
        print("STOPPING DETECTION")
        self.running_recognition = False

        if self.play_on:
            self.siren_obj.stop_alarm()
            self.play_on = False


if __name__ == '__main__':

    rcv_q = queue.Queue()
    client_video = ClientComms.ClientComms(Setting.VIDEO_PORT)
    # client_stills = ClientComms.ClientComms(Setting.STILLS_PORT)
    # client_command = ClientComms.ClientComms(Setting.GENERAL_PORT, rcv_q)

    client_camera = ClientCamera(client_video, None)

    client_camera.start_camera()
