import os
import PIL

def unpack(message):

    """
    Gets a packed messages and returns it unpacked (According to its code)
    :param message: The message
    :type message: String
    :return: Returns the unpacked message
    :rtype: String
    """

    code = message[:2]

    unpacked_message = ""

    data = message[2:]

    return unpacked_message


def build_cam_status(status):

    """
    Builds a message with the status of the camera connected to the PC
    :param status: The status of the camera connected to the PC (0 - not connected, 1 - connected)
    :type status: String
    :return: The packed message ready to send
    :rtype: String
    """

    code = "03"

    packed_message = code + status

    return packed_message


def build_frame_send(frame_path):

    """
    Building a message containing a frame of the video
    :param frame_path: The path to the frame
    :type frame_path: String
    :return: The packed message ready to send
    :rtype: String
    """

    with open(frame_path, 'r') as f:
        frame = f.read()
        f.close()

    frame_length = os.path.getsize(frame_path)

    frame_length = frame_length.zfill(10)

    code = "001"

    packed_message = code + frame_length + frame

    return packed_message


def build_photo_send(photo_path):
    """
    Building a message containing a photo caught by face recognition
    :param photo_path: The path to the photo
    :type photo_path: String
    :return: The packed message ready to send
    :rtype: String
    """

    with open(photo_path, 'r') as f:
        photo = f.read()
        f.close()

    photo_length = os.path.getsize(photo_path)

    photo_length= photo_length.zfill(10)

    code = "002"

    packed_message = code + photo_length + photo

    return packed_message