import socket
import sys
import threading

import wx

import Setting
import pickle
import struct
import ClientProtocol
from pubsub import pub
from uuid import getnode




class ClientComms:

    def __init__(self, port, recv_q=None):

        self.my_socket = socket.socket()  # Initializing the client's socket

        self.server_ip = Setting.IP_SERVER  # The server's IP
        self.port = port  # The server's port
        self.recv_q = recv_q  # The queue where messages get stored to and read

        self.running = False
        self.mac = self.get_macAddress()

        # Starting the thread that runs the main loop constantly
        threading.Thread(target=self._main_loop, ).start()

    def _main_loop(self):
        """
        The function connects to the server and listens, every new message gets put into recv_q
        """

        try:
            # Connecting the client's socket to the server socket
            self.my_socket.connect((self.server_ip, self.port))
            if self.port == Setting.GENERAL_PORT:
                print(self.mac)

                message = ClientProtocol.ClientProtocol.build_mac_send(self.mac)
                self.send_msg(message)
            print("CONNECTED")
        except Exception as e:
            print(str(self.port), "CLIENT COMMS LINE 34" + str(e))
            self.my_socket.close()
            self.recv_q.put(("QU", "QU"))
            sys.exit("Can't connect")

        if self.port == Setting.GENERAL_PORT:
            while True:
                print("IN WHILE")
                # Receiving the length and data
                try:
                    length = self.my_socket.recv(8).decode()
                    data = self.my_socket.recv(int(length)).decode()

                except Exception as e:
                    print("CLIENT COMMS LINE 45" + str(e))
                    self.my_socket.close()
                    self.recv_q.put(("QU", "QU"))
                    sys.exit()

                else:
                    print("CLIENT COMM DATA:", data)
                    # Checking the data isn't empty
                    if len(data) > 0:
                        code, data = ClientProtocol.ClientProtocol.unpack(data)
                        self.recv_q.put((code, data))
                    else:
                        print("CLIENT COMMS LINE 74")
                        self.my_socket.close()
                        self.recv_q.put(("QU", "QU"))
                        sys.exit()

    def send_msg(self, message):
        """
        The function sends a message to the server
        :param message: The message to be sent to the server
        :type message: String
        """
        print("SEND MESSAGE CLIENT COMMS:", message)
        # Getting the length of the message
        if type(message) == str:
            message = message.encode()

        message_length = str(len(message)).zfill(8).encode()

        try:
            self.my_socket.send(message_length + message)

        except Exception as e:
            print("CLIENT COMMS LINE 72" + str(e))
            self.my_socket.close()

    def send_file(self, code, file_path):
        """
        The function sends a file to the server
        :param code: The type of file (01 - Frame, 02 - Photo)
        :type code; String
        :param file_path: The path to the file that needs to be sent
        :type file_path: String
        """

        # read the file data
        with open(file_path, 'rb') as f:
            file = f.read()
            f.close()

        message = f"{code}{str(len(file))}"
        message_length = str(len(message)).zfill(8).encode()

        try:
            self.my_socket.send(message_length + message.encode())
            self.my_socket.send(file)

        except Exception as e:
            print("CLIENT COMMS LINE 97" + str(e))
            self.my_socket.close()

    def start_client(self):
        self.running = True

    def stop_client(self):
        self.running = False

    def send_video(self, data):
        try:
            size = len(data)

            # if img_counter % 10 == 0:
            self.my_socket.sendall(struct.pack(">L", size) + data)
        except:
            pass

    def get_macAddress(self):
        """ returns  mac address"""
        return ':'.join(['{:02x}'.format((getnode() >> i) & 0xff) for i in range(0, 8 * 6, 8)][::-1])
