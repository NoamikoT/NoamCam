import pickle
import struct
import sys
import threading
import cv2
import os
import Setting
import ClientComms
import imutils
import queue
from pubsub import pub


class ClientCamera():
    def __init__(self, video_comm, stills_comm):

        self.video_comm = video_comm
        self.stills_comm = stills_comm
        self.running = False

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

            # datasets = 'datasets'
            # sub_data = 'Noam'

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
                if ret or frame!=None:
                    frame = cv2.resize(frame, dsize=(530, 300), interpolation=cv2.INTER_AREA)
                    # frame = cv2.flip(frame, 180)
                    result, image = cv2.imencode('.jpg', frame, self.encode_param)
                    data = pickle.dumps(image, 0)

                    if count%5 == 0:
                        self.video_comm.send_video(data)
                        count = 0
                    count+=1

                    # if img_counter % 10 == 0:
                    # img_counter += 1

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                else:
                    self.close_camera()
                    self.cap = cv2.VideoCapture(cv2.CAP_DSHOW)
                    print("Resetted the camera")

if __name__ == '__main__':

    rcv_q = queue.Queue()
    client_video = ClientComms.ClientComms(Setting.VIDEO_PORT)
    # client_stills = ClientComms.ClientComms(Setting.STILLS_PORT)
    # client_command = ClientComms.ClientComms(Setting.GENERAL_PORT, rcv_q)

    client_camera = ClientCamera(client_video, None)

    client_camera.start_camera()