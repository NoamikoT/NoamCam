import socket
import queue
import threading


class ClientComms:

    def __init__(self, server_IP, port, recv_q):

        self.my_socket = None
        self.server_IP = server_IP
        self.port = port
        self.recv_q = recv_q
        self.running = False

    def __main_loop(self):
        """
        The function creates the client, connects to the server and listens, every new message gets put into recv_q
        :return:
        """
        return

    def send(self, message):
        """
        Sends a message
        :param message: The message to be sent
        :return:
        """
        return