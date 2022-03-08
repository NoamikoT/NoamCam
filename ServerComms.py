import socket
import queue
import threading
import select
import pip


class ServerComms:

    def __init__(self, port, recv_q):

        self.__server_socket = socket.socket()
        self.__server_socket.bind(("0.0.0.0", port))
        self.__server_socket.listen(5)
        self.__open_clients = {}
        self.__user_dict = {} # Socket : (ip, port)

        self.__port = port
        self.__recv_q = recv_q
        self.__running = True

        threading.Thread(target=self._main_loop, ).start()

    def __main_loop(self):
        """
        The function creates the server, connects new clients, every new message gets put into recv_q
        :return:
        """

        while self.__running:
            try:
                rlist, wlist, xlist = select.select(list(self.__user_dict.keys()) + [self.__server_socket], [], [], 0.3)
            except:
                pass
            else:
                for current_socket in rlist:
                    if current_socket is self.__server_socket:
                        # new client
                        client, address = self.__server_socket.accept()
                        print(address, "- CONNECTED")

                        # add to dictionary
                        self.__user_dict[client] = address
                        self.__open_clients[address[0]] = client
                    else:
                        # receive info
                        try:
                            # receive length of msg
                            length = current_socket.recv(8).decode()
                        except Exception as e:
                            print(e)
                            if current_socket in self.__user_dict.keys():
                                self.disconnect(self.__user_dict[current_socket][0])
                                return
                            break

                        else:
                            # disconnected
                            if length == '':
                                self.disconnect(self.__user_dict[current_socket][0])
                            else:
                                # initiate msg
                                msg = bytearray()
                                count = 0
                                # receive the msg
                                while count < int(length):
                                    if (int(length) - count) > 1024:
                                        try:
                                            data = current_socket.recv(1024)
                                        except Exception as e:
                                            print(e)
                                            self.disconnect(self.__user_dict[current_socket][0])
                                        else:
                                            if data == b'':
                                                self.disconnect(self.__user_dict[current_socket][0])
                                                msg = b''
                                                break
                                            else:
                                                msg.extend(data)
                                                count += len(data)

                                    else:
                                        try:
                                            data = current_socket.recv((int(length) - count))
                                        except Exception as e:
                                            print(e)
                                            self.disconnect(self.__user_dict[current_socket][0])
                                        else:
                                            if data == b'':
                                                self.disconnect(self.__user_dict[current_socket][0])
                                                msg = b''
                                                break
                                            else:
                                                msg.extend(data)
                                                count += len(data)
                                if msg != b'':
                                    self.__recv_q.put((self.__user_dict[current_socket][0], msg))


    def send(self, ip, message):
        """
        Sends a message to a client
        :param ip: The IP of the client
        :type ip: String
        :param message: The message to be sent
        :type message: String
        :return:
        """

        if ip in self.__open_clients.keys():
            sock = self.__open_clients[ip]
            if type(message) == str:
                message = message.encode()
            length = str(len(message)).zfill(8).encode()
            try:
                sock.send(length+message)
            except Exception as e:
                print(e,1)
                self.disconnect(ip)

    def __find_socket_by_ip(self, ip):
        """
        The function gets an ip, and returns the corresponding socket of that ip
        :param ip: The ip to find the socket for
        :type ip: String
        :return: The socket of the ip
        :rtype: Socket
        """
        return self.__open_clients.get(ip, default=None)

    def disconnect(self, ip):
        """
        The function disconnects a socket of the corresponding ip from the server
        :param ip: ip address
        :type ip: String
        """
        if ip in self.__open_clients.keys():
            print(f"{self.__user_dict[self.__open_clients[ip]]} disconnected")
            self.__open_clients[ip].close()
            try:
                del self.__user_dict[self.__open_clients[ip]]
                del self.__open_clients[ip]
            except:
                pass
            else:
                print("DC, IP-", ip)
                self.__recv_q.put((ip, f"dc"))