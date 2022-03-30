import socket
import threading


class ClientComms:

    def __init__(self, server_ip, port, recv_q):

        self.my_socket = socket.socket()  # Initializing the client's socket

        self.server_ip = server_ip  # The server's IP
        self.port = port  # The server's port
        self.recv_q = recv_q  # The queue where messages get stored to and read

        # Starting the thread that runs the main loop constantly
        threading.Thread(target=self._main_loop, ).start()

    def _main_loop(self):
        """
        The function connects to the server and listens, every new message gets put into recv_q
        """

        try:
            # Connecting the client's socket to the server socket
            self.my_socket.connect((self.server_ip, self.port))
            print("CONNECTED")
        except Exception as e:
            print(str(e))
            self.my_socket.close()

        while True:
            # Receiving the length and data
            try:
                length = self.my_socket.recv(8).decode()
                data = self.my_socket.recv(length).decode()

            except Exception as e:
                print(str(e))
                self.my_socket.close()

            else:
                # Checking the data isn't empty
                if len(data) > 0:
                    code = data[0:2]
                    if code in ["01", "02", "03", "04"]:
                        self.recv_q.put((code, data[2:]))

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

