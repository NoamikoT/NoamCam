import os
import cv2


class NoamCamera:

    def __init__(self, video_dir):
        """
        Constructor
        """

        self.video_dir = video_dir

    def get_video_dir(self):
        """
        Getting the saved video directory

        :return: The current directory of the saved video
        :rtype: String
        """

        return self.video_dir

    def set_video_dir(self, video_dir):
        """
        Setting the saved video directory

        :param video_dir: A directory for the saved video
        :return: Nothing
        """

        self.video_dir = video_dir