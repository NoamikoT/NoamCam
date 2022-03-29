import socket
import queue
import threading


class ClientComms:

    def __init__(self, server_ip, port, recv_q):

        self.my_socket = socket.socket()  # Initializing the client's socket

        self.server_ip = server_ip  # The server's IP
        self.port = port  # The server's port
        self.recv_q = recv_q  # The queue where messages get stored to and read
        self.running = False  # A boolean dictating whether the client is running or not

        # Connecting the client's socket to the server socket
        self.my_socket.connect((self.server_ip, self.port))

        # Starting the thread that runs the main loop constantly
        threading.Thread(target=self.__main_loop, ).start()

    def __main_loop(self):
        """
        The function connects to the server and listens, every new message gets put into recv_q
        """

        while self.running:
            # Receiving the length
            try:
                length = self.my_socket.recv(8).decode()

            except Exception as e:
                print(str(e))
                self.my_socket.close()
                break

            else:
                # If the connection is gone, closing the client
                if length == "":
                    self.my_socket.close()
                    break

                # Initializing the message as a byte array
                msg = bytearray()
                counter = 0

                # Receiving the message
                while counter < int(length):
                    if (int(length) - counter) > 1024:
                        try:
                            data = self.my_socket.recv(1024)

                        except Exception as e:
                            print(str(e))
                            self.my_socket.close()
                            break

                        else:
                            msg.extend(data)
                            counter += len(data)

                    else:
                        try:
                            data = self.my_socket.recv((int(length) - counter))

                        except Exception as e:
                            print(str(e))
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


    def send_file(self, code, file_path):

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
            print(str(e))
            self.my_socket.close()

    def start_client(self):
        """
        Starts the client
        """

        self.running = True

    def stop_client(self):
        """
        The function closes the client
        """

        self.running = False
