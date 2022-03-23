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


def build_face_recognition(status):

    """
    Gets the wanted status for the face recognition, creates the message with the face recognition code and returns it
    :param status: The wanted status for the face recognition (0 = turn off, 1 = turn on)
    :type status: String
    :return: The packed message ready to send
    :rtype: String
    """

    code = "01"

    packed_message = code + status

    return packed_message


def build_siren():

    """
    Building a message saying to activate the siren
    :return: The packed message ready to send
    :rtype: String
    """

    code = "020"

    return code


def build_stream_status(status):

    """
    Gets the wanted status for the stream, creates the message with the stream status code and returns it
    :param status: The wanted status for the stream (0 = stop stream, 1 = start stream)
    :type status: String
    :return: The packed message ready to send
    :rtype: String
    """

    code = "03"

    packed_message = code + status

    return packed_message


def build_turn_off():

    """
    Building a message telling the computer to turn off
    :return: The packed message ready to send
    :rtype: String
    """

    code = "040"

    return code


def build_frame_send(frame_path):

    """
    Building a message containing a frame of the video
    :param frame_path: The path to the frame
    :type frame_path: String
    :return: The packed message ready to send
    :rtype: String
    """

    with open(frame_path, 'rb') as f:
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

    with open(photo_path, 'rb') as f:
        photo = f.read()
        f.close()

    photo_length = os.path.getsize(photo_path)

    photo_length= photo_length.zfill(10)

    code = "001"

    packed_message = code + photo_length + photo

    return packed_message