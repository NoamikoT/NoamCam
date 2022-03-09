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
        The function connects to the server and listens, every new message gets put into recv_q
        :return:
        """

        while self.running:
            # Receiving the length
            try:
                length = self.__sock.recv(8).decode()
            except Exception as e:
                print(str(e))
                self.my_socket.close()
                break
            else:
                # If the connection is gone, closing the client
                if length == "":
                    self.my_socket.close()
                    break

                # initialize the msg
                msg = bytearray()
                counter = 0

                # receive the data
                while counter < int(length):
                    if (int(length) - counter) > 1024:

                        try:
                            data = self.my_socket.recv(1024)
                        except Exception as e:
                            print(e)
                            self.my_socket.close()
                            break
                        else:
                            msg.extend(data)
                            counter += len(data)
                            # got full msg
                    else:
                        try:
                            data = self.my_socket.recv((int(length) - counter))
                        except Exception as e:
                            print(e, 55)
                            self.my_socket.close()
                            break
                        else:
                            msg.extend(data)
                            counter += len(data)

                self.recv_q.put(msg)

    def send(self, message):
        """
        Sends a message
        :param message: The message to be sent
        :return:
        """

        # Getting the length of the message
        if type(message) == str:
            message = message.encode()
        message_length = str(len(message)).zfill(8).encode()

        try:
            self.my_socket.send(message_length + message)
        except Exception as e:
            print(str(e))
            self.my_socket.close()

    def open_client(self):
        """
        Starts the client
        """

        self.running = True

    def close_client(self):
        """
        The function closes the client
        """

        self.running = False