import socket
import queue
import threading


class ServerLogic:

    def __init__(self, recv_q):

        self.recv_q = recv_q
        self.running = False

