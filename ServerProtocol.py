class ServerProtocol:
    """A class unpacking and packing messages according to the protocol"""
    @staticmethod
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

        # 03 - Cam status
        if code == "03":
            if data == "0":
                unpacked_message = "Camera is not connected"
            elif data == "1":
                unpacked_message = "Camera is connected"

        # 05 - MAC
        elif code == "05":
            unpacked_message = data

        return [code, unpacked_message]

    @staticmethod
    def build_face_recognition(status):

        """
        Gets the wanted status for the face recognition, creates the message with the face recognition code and returns it
        :param status: The wanted status for the face recognition (0 = turn off, 1 = turn on)
        :type status: String
        :return: The packed message ready to send
        :rtype: String
        """

        code = "01"

        packed_message = f"{code}{status}"

        return packed_message

    @staticmethod
    def build_siren_on(mac):

        """
        Building a message saying to activate the siren
        :return: The packed message ready to send
        :rtype: String
        """

        code = f"02{mac}"

        return code

    @staticmethod
    def build_siren_off(mac):

        """
        Building a message saying to deactivate the siren
        :return: The packed message ready to send
        :rtype: String
        """

        code = f"09{mac}"

        return code

    @staticmethod
    def build_stream_status(status):

        """
        Gets the wanted status for the stream, creates the message with the stream status code and returns it
        :param status: The wanted status for the stream (0 = stop stream, 1 = start stream)
        :type status: String
        :return: The packed message ready to send
        :rtype: String
        """

        code = "03"

        packed_message = f"{code}{status}"

        return packed_message

    @staticmethod
    def build_turn_off():

        """
        Building a message telling the computer to turn off
        :return: The packed message ready to send
        :rtype: String
        """

        code = "04"

        return code

    @staticmethod
    def build_send_port(port):

        """
        Building a message with the port
        :return: The packed message ready to send
        :rtype: String
        """

        code = "06"

        packed_message = f"{code}{port}"

        return packed_message

    @staticmethod
    def build_zoom(mac):

        """
        Building a message telling the client that zoom is enabled
        :return: The packed message ready to send
        :rtype: String
        """

        code = "07"

        packed_message = f"{code}{mac}"

        return packed_message

    @staticmethod
    def build_unzoom(mac):

        """
        Building a message telling the client that zoom is disabled
        :return: The packed message ready to send
        :rtype: String
        """

        code = "08"

        packed_message = f"{code}{mac}"

        return packed_message
