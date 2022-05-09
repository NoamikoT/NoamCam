import os
import cv2


class ServerCamera:
    def __init__(self, path, id):

        self.fourcc = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')
        self.path = path
        self.id = id

        self._check_path()

        self.video_writer = cv2.VideoWriter(f'{path}/video{id}.avi', self.fourcc, 10.0, (640, 480))

    def _check_path(self):
        if not os.path.isdir(self.path):
            os.mkdir(self.path)

    def add_frame(self, img):
        self.video_writer.write(img)

    def show_video(self, img):
        cv2.imshow("img", img)
