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

    data = message[2:]

    unpacked_message = data

    if code == "01":
        if data == "0":
            unpacked_message = "Stop face recognition"
        elif data == "1":
            unpacked_message = "Continue face recognition"

    elif code == "02":
        unpacked_message = "Sound siren"

    elif code == "03":
        if data == "0":
            unpacked_message = "Stop stream"
        elif data == "1":
            unpacked_message = "Continue stream"

    elif code == "04":
        unpacked_message = "Shut off computer"

    return [code, unpacked_message]


def build_cam_status(status):

    """
    Builds a message with the status of the camera connected to the PC
    :param status: The status of the camera connected to the PC (0 - not connected, 1 - connected)
    :type status: String
    :return: The packed message ready to send
    :rtype: String
    """

    code = "03"

    packed_message = f"{code}{status}"

    return packed_message


def build_frame_send(frame_path):

    """
    Building a message containing a frame of the video
    :param frame_path: The path to the frame
    :type frame_path: String
    :return: The packed message ready to send
    :rtype: String
    """

    # with open(frame_path, 'r') as f:
    #     frame = f.read()
    #     f.close()

    code = "01"

    packed_message = f"{code}{frame_path}"

    return packed_message


def build_photo_send(photo_path):
    """
    Building a message containing a photo caught by face recognition
    :param photo_path: The path to the photo
    :type photo_path: String
    :return: The packed message ready to send
    :rtype: String
    """

    # with open(photo_path, 'r') as f:
    #     photo = f.read()
    #     f.close()

    code = "02"

    packed_message = f"{code}{photo_path}"

    return packed_message