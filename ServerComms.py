import socket
import threading
import select


class ServerComms:

    def __init__(self, port, recv_q):

        self.server_socket = socket.socket()  # Initializing the server's socket

        self.open_clients = {}  # A dictionary socket -> ip
        self.file_num = 0

        self.port = port  # The server's port
        self.recv_q = recv_q  # The queue where messages get stored to and read

        # Starting the thread that runs the main loop constantly
        threading.Thread(target=self._main_loop, ).start()

    def _main_loop(self):
        """
        The function creates the server, connects new clients, every new message gets put into recv_q
        """

        # Binding the server's socket
        self.server_socket.bind(("0.0.0.0", self.port))
        self.server_socket.listen(5)

        while True:

            rlist, wlist, xlist = select.select(list(self.open_clients.keys()) + [self.server_socket], [], [], 0.5)

            for current_socket in rlist:
                if current_socket is self.server_socket:
                    # When a new client connects
                    client, address = self.server_socket.accept()
                    print(address[0], "- CONNECTED")

                    # Adding the new client to the dictionaries
                    self.open_clients[client] = address[0]

                else:
                    # Getting messages from a client
                    try:
                        # Receiving the length of the message
                        length = int(current_socket.recv(8).decode())
                        data = current_socket.recv(length).decode()

                    except Exception as e:
                        print(str(e))
                        self.disconnect(current_socket)

                    else:
                        # Checking the data isn't empty
                        if len(data) > 0:
                            code = data[0:2]
                            # 01/02 means media file
                            if code in ["01", "02"]:
                                file_len = int(data[2:])
                                self._recv_file(current_socket, code, file_len)
                            elif code in ["03"]:
                                self.recv_q.put((self.open_clients[current_socket], code, data[2:]))

    def _recv_file(self, soc, code, file_len):
        """
        The function gets a socket to receive the file from, the code (01 - frame, 02 - photo), and the length of the file, and receives the file
        :param soc: The socket to receive from
        :type soc: Socket
        :param code: The kind of media (01 - Frame, 02 - Photo)
        :type code: String
        :param file_len: The length of the file needed to receive
        :type file_len: Integer
        :return: Doesn't return anything, but opens and writes the file received
        """

        # Initiating the message as a byte array
        msg = bytearray()
        # Receiving the message
        while len(msg) < file_len:
            size = file_len - len(msg)
            if size > 1024:
                msg.extend(soc.recv(1024))
            else:
                msg.extend(soc.recv(size))
                break
        file_name = f"Pic{str(self.file_num)}.png"
        self.file_num += 1
        with open(file_name, "wb") as f:
            f.write(msg)

        self.recv_q.put((self.open_clients[soc], code, file_name))

    def send(self, ip, message):
        """
        Sends a message to a client
        :param ip: The IP of the client
        :type ip: String
        :param message: The message to be sent
        :type message: String
        """

        soc = self._find_socket_by_ip(ip)

        if soc:
            if type(message) == str:
                message = message.encode()
            length = str(len(message)).zfill(8).encode()
            try:
                soc.send(length + message)
            except Exception as e:
                print(str(e))
                self.disconnect(soc)

    def _find_socket_by_ip(self, ip):
        """
        The function gets an ip, and returns the corresponding socket of that ip
        :param ip: The ip to find the socket for
        :type ip: String
        :return: The socket of the ip
        :rtype: Socket
        """

        ret_soc = None
        for soc in self.open_clients.keys():
            if self.open_clients[soc] == ip:
                ret_soc = soc
                break
        return ret_soc

    def disconnect(self, soc):
        """
        The function disconnects a socket of the corresponding ip from the server
        :param soc: The socket that needs to eb disconnected
        :type soc: Socket
        """

        if soc in self.open_clients.keys():
            print(f"Disconnected {self.open_clients[soc]}")
            del self.open_clients[soc]