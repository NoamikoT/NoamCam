class ClientProtocol:
    """A class unpacking and packing messages according to the protocol"""
    @staticmethod
    def unpack(message):
        """
        The function gets a packed message and returns it unpacked (According to its code)
        :param message: The message to be unpacked
        :type message: String
        :return: Returns the unpacked message
        :rtype: String
        """

        # The code is the first 2 characters of the message
        code = message[:2]

        # The data is everything after the code of the message
        data = message[2:]

        unpacked_message = data

        # 01 - Face detection on\off
        if code == "01":
            if data == "0":
                unpacked_message = "Stop face recognition"
            elif data == "1":
                unpacked_message = "Start face recognition"

        # 02 - Sound the siren
        elif code == "02":
            unpacked_message = "Sound siren"

        # 09 - Stop the siren
        elif code == "09":
            unpacked_message = "Sound off"

        # 03 - Stream status on\off
        elif code == "03":
            if data == "0":
                unpacked_message = "Stop stream"
            elif data == "1":
                unpacked_message = "Continue stream"

        # 04 - Shut down the computer
        elif code == "04":
            unpacked_message = "Shut off computer"

        # 06 - Port message
        elif code == "06":
            unpacked_message = int(data)

        # 07 - Request to zoom
        elif code == "07":
            unpacked_message = "Zoom"

        # 08 - Request to unzoom
        elif code == "08":
            unpacked_message = "Unzoom"

        return code, unpacked_message

    @staticmethod
    def build_cam_status(status):
        """
        The function builds a message with the status of the camera connected to the PC
        :param status: The status of the camera connected to the PC (0 - not connected, 1 - connected)
        :type status: String
        :return: The packed message ready to send
        :rtype: String
        """

        code = "03"

        packed_message = f"{code}{status}"

        return packed_message

    @staticmethod
    def build_frame_send(frame_path):
        """
        Building a message containing a path to a frame of the video
        :param frame_path: The path to the frame
        :type frame_path: String
        :return: The packed message ready to send
        :rtype: String
        """

        code = "01"

        packed_message = f"{code}{frame_path}"

        return packed_message

    @staticmethod
    def get_photo_code():
        """
        :return: The packed message ready to send
        :rtype: String
        """

        return "02"

    @staticmethod
    def build_mac_send(mac_address):
        """
        Building a message containing the MAC Address of the client
        :param mac_address: The mac address of the client
        :type mac_address: String
        :return: The packed message ready to send
        :rtype: String
        """

        code = "05"

        packed_message = f"{code}{mac_address}"

        return packed_message
