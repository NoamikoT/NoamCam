import socket
import queue
import threading
import select
import pip

class ServerComms():

    def __init__(self, port, recv_q):

        self.my_socket = None
        self.port = port
        self.recv_q = recv_q
        self.open_clients = None
        self.running = False

        threading.Thread(target=self._main_loop, ).start()

    def _main_loop(self):
        """
        The function creates the client, connects new clients, every new message gets put into recv_q
        :return:
        """
        return

    def send(self, ip, message):
        """
        Sends a message to a client
        :param ip: The IP of the client
        :type ip: String
        :param message: The message to be sent
        :type message: String
        :return:
        """
        return

    def _find_socket_by_ip(self, ip):
        """
        The function gets an ip, and returns the corresponding socket of that ip
        :param ip: The ip to find the socket for
        :type ip: String
        :return: The socket of the ip
        :rtype: Socket
        """
        return self.open_clients.get(ip, default = None)