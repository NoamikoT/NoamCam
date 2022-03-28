

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

    unpacked_message = ""

    # 03 - Cam status
    if code == "03":
        if data == "0":
            unpacked_message = "Camera is not connected"

        else:
            unpacked_message = "Camera is connected"

    elif code == "00":
        code = message[:3]

        data = message[3:]

        if code == "001":
            frame_length = data[:10]
            frame = data[10:]

            unpacked_message = "Frame received: " + frame_path

        elif code == "002":
            photo_length = data[:10]
            photo = data[10:]



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
