import socket
import sys
import threading
import Setting
import struct
import ClientProtocol
from uuid import getnode
import AESCipher


class ClientComms:
    """A class for communicating from the client to the server"""

    def __init__(self, port, recv_q=None):

        # Initializing the client's socket
        self.my_socket = socket.socket()

        # The server's IP
        self.server_ip = Setting.IP_SERVER
        # The server's port
        self.port = port
        # The queue where messages get stored to and read
        self.recv_q = recv_q

        # Whether the system is running or not
        self.running = True

        self.server_running = False

        # Getting the client (self) MAC Address
        self.mac = self.get_mac_address()

        self.myAES = None

        # Starting the thread that runs the main loop constantly
        threading.Thread(target=self._main_loop, ).start()

    def _main_loop(self):
        """
        The function connects to the server and listens, every new message gets put into recv_q
        """

        try:
            # Connecting the client's socket to the server socket
            self.my_socket.connect((self.server_ip, self.port))
            # If its the commands comms
            if self.port == Setting.GENERAL_PORT:
                self.myAES = AESCipher.AESCipher("CATDOGMOUSE1029")

                message = ClientProtocol.ClientProtocol.build_mac_send(self.mac)
                self.send_msg(message)
            self.server_running = True
        except Exception as e:
            self.my_socket.close()
            self.recv_q.put(("QU", "QU"))
            sys.exit("Can't connect")

        # If its the commands comms, only receiving commands
        if self.port == Setting.GENERAL_PORT:
            while self.running:
                # Receiving the length and data
                try:
                    length = self.my_socket.recv(8).decode()
                    data = self.my_socket.recv(int(length)).decode()

                except Exception as e:
                    self.my_socket.close()
                    self.recv_q.put(("QU", "QU"))
                    sys.exit()

                else:
                    # Checking the data isn't empty
                    if len(data) > 0:
                        if self.myAES:
                            data = self.myAES.decrypt(data)
                        # Letting the protocol unpack the data, and putting it in the queue for the MainClient to handle it
                        code, data = ClientProtocol.ClientProtocol.unpack(data)
                        self.recv_q.put((code, data))

    def send_msg(self, message):
        """
        The function sends a message to the server
        :param message: The message to be sent to the server
        :type message: String
        """
        # Getting the length of the message

        if self.myAES:
            message = self.myAES.encrypt(message)

        if type(message) == str:
            message = message.encode()

        message_length = str(len(message)).zfill(8).encode()

        try:
            self.my_socket.send(message_length + message)

        except Exception as e:
            self.my_socket.close()

    def send_file(self, file_path):
        """
        The function sends a file to the server
        :param file_path: The path to the file that needs to be sent
        :type file_path: String
        """

        # Reading the file data
        with open(file_path, 'rb') as f:
            file = f.read()
            f.close()

        # Creating the message
        message = f"{ClientProtocol.ClientProtocol.get_photo_code()}{str(len(file))}"
        message_length = str(len(message)).zfill(8).encode()

        try:
            self.my_socket.send(message_length + message.encode())
            self.my_socket.send(file)

        except Exception as e:
            self.my_socket.close()

    def start_client(self):
        """
        The function starts running the client
        """
        self.running = True

    def stop_client(self):
        """
        The function stops running the client
        """
        self.running = False

    def send_video(self, data):
        """
        The function sends a video (frame) to the server
        :param data: The frame to be sent
        :type data: Numpy Object
        """
        try:
            size = len(data)

            self.my_socket.sendall(struct.pack(">L", size) + data)
        except Exception as e:
            pass

    def get_mac_address(self):
        """The function returns the MAC Address of the client"""
        return ':'.join(['{:02x}'.format((getnode() >> i) & 0xff) for i in range(0, 8 * 6, 8)][::-1])
