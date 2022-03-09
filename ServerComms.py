import socket
import queue
import threading
import select


class ServerComms:

    def __init__(self, port, recv_q):

        self.server_socket = socket.socket()  # Initializing the server's socket

        self.open_clients = {}  # A dictionary
        self.user_dict = {}  # A dictionary that saves all of the the connected users (clients) - Socket : (ip, port)

        self.port = port  # The server's port
        self.recv_q = recv_q  # The queue where messages get stored to and read
        self.running = False  # A boolean dictating whether the client is running or not

        # Binding the server's socket
        self.server_socket.bind(("0.0.0.0", port))
        self.server_socket.listen(5)

        # Starting the thread that runs the main loop constantly
        threading.Thread(target=self.__main_loop, ).start()

    def __main_loop(self):
        """
        The function creates the server, connects new clients, every new message gets put into recv_q
        """

        while self.running:
            try:
                rlist, wlist, xlist = select.select(list(self.user_dict.keys()) + [self.server_socket], [], [], 0.5)

            except Exception as e:
                print(str(e))

            else:
                for current_socket in rlist:
                    if current_socket is self.server_socket:
                        # When a new client connects
                        client, address = self.server_socket.accept()
                        print(address, "- CONNECTED")

                        # Adding the new client to the dictionaries
                        self.user_dict[client] = address
                        self.open_clients[address[0]] = client

                    else:
                        # Getting messages from a client
                        try:
                            # Receiving the length of the message
                            length = current_socket.recv(8).decode()

                        except Exception as e:
                            print(str(e))
                            if current_socket in self.user_dict.keys():
                                self.disconnect(self.user_dict[current_socket][0])
                                return
                            break

                        else:
                            # If the connection is gone, closing the client
                            if length == '':
                                self.disconnect(self.user_dict[current_socket][0])

                            else:
                                # Initiating the message as a byte array
                                msg = bytearray()
                                count = 0

                                # Receiving the message
                                while count < int(length):
                                    if (int(length) - count) > 1024:
                                        try:
                                            data = current_socket.recv(1024)

                                        except Exception as e:
                                            print(str(e))
                                            self.disconnect(self.user_dict[current_socket][0])

                                        else:
                                            if data == b'':
                                                self.disconnect(self.user_dict[current_socket][0])
                                                msg = b''
                                                break

                                            else:
                                                msg.extend(data)
                                                count += len(data)

                                    else:
                                        try:
                                            data = current_socket.recv((int(length) - count))

                                        except Exception as e:
                                            print(str(e))
                                            self.disconnect(self.user_dict[current_socket][0])

                                        else:
                                            if data == b'':
                                                self.disconnect(self.user_dict[current_socket][0])
                                                msg = b''
                                                break

                                            else:
                                                msg.extend(data)
                                                count += len(data)

                                if msg != b'':
                                    self.recv_q.put((self.user_dict[current_socket][0], msg))

    def send(self, ip, message):
        """
        Sends a message to a client
        :param ip: The IP of the client
        :type ip: String
        :param message: The message to be sent
        :type message: String
        """

        if ip in self.open_clients.keys():
            sock = self.open_clients[ip]
            if type(message) == str:
                message = message.encode()
            length = str(len(message)).zfill(8).encode()
            try:
                sock.send(length+message)
            except Exception as e:
                print(str(e))
                self.disconnect(ip)

    def __find_socket_by_ip(self, ip):
        """
        The function gets an ip, and returns the corresponding socket of that ip
        :param ip: The ip to find the socket for
        :type ip: String
        :return: The socket of the ip
        :rtype: Socket
        """

        return self.open_clients.get(ip, default=None)

    def disconnect(self, ip):
        """
        The function disconnects a socket of the corresponding ip from the server
        :param ip: ip address
        :type ip: String
        """

        if ip in self.open_clients.keys():
            print(f"Disconnected {self.user_dict[self.open_clients[ip]]}")
            self.open_clients[ip].close()

            try:
                del self.user_dict[self.open_clients[ip]]
                del self.open_clients[ip]

            except Exception as e:
                print(str(e))

    def start_server(self):
        """
        The function starts the server
        """

        self.running = True

    def stop_server(self):
        """
        The function stops the server
        """

        self.running = False
