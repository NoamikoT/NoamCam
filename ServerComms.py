import os
import pickle
import socket
import threading
import select
import struct
import wx
import cv2
import DB_Class
import Setting
import queue
import ServerProtocol
from datetime import datetime
from pubsub import pub



class ServerComms:

    def __init__(self, port, recv_q=None):

        self.server_socket = socket.socket()  # Initializing the server's socket

        self.myDB = DB_Class.DB("myDB")

        self.open_clients = {}  # A dictionary socket -> ip
        self.file_num = 0

        self.port = port  # The server's port
        self.recv_q = recv_q  # The queue where messages get stored to and read

        self.video_q = queue.Queue()
        self.stills_q = queue.Queue()

        self.payload_size = struct.calcsize(">L")
        self.path = None

        # Starting the thread that runs the main loop constantly
        threading.Thread(target=self._main_loop, ).start()


        if self.port != Setting.GENERAL_PORT:

            threading.Thread(target=self.handle_video_rec, ).start()

            threading.Thread(target=self.handle_stills, ).start()


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

                    if self.port != Setting.GENERAL_PORT:

                        self.path = self.get_path()
                        print(self.get_path(),"ServerComms.py:73")

                else:
                    if self.port == Setting.GENERAL_PORT:

                        # Getting messages from a client
                        try:
                            # Receiving the length of the message
                            length = int(current_socket.recv(8).decode())
                            data = current_socket.recv(length).decode()

                        except Exception as e:
                            print(str(e))
                            self.disconnect(current_socket)

                        else:
                            print("IN SERVER DATA:", data)
                            # Checking the data isn't empty
                            if len(data) > 0:
                                code, message = ServerProtocol.ServerProtocol.unpack(data)
                                # 01/02 means media file
                                if code in ["01", "02"]:
                                    file_len = int(data[2:])
                                    self._recv_file(current_socket, code, file_len)
                                else:
                                    self.recv_q.put((self.open_clients[current_socket], code, message))

                            else:
                                self.disconnect(current_socket)

                    else:
                        data = b""
                        try:
                            while len(data) < self.payload_size:
                                data += current_socket.recv(4096)

                        except Exception as e:
                            print("Line 81:", str(e))
                            self.disconnect(current_socket)

                        else:

                            if self.port%2 == 0:        # Making sure it's the video port

                                # receive image row data form client socket
                                packed_msg_size = data[:self.payload_size]
                                data = data[self.payload_size:]
                                msg_size = struct.unpack(">L", packed_msg_size)[0]
                                try:
                                    while len(data) < msg_size:
                                        data += current_socket.recv(4096)
                                except Exception as e:
                                    print("Line 94:", str(e))
                                    self.disconnect(current_socket)
                                else:
                                    frame_data = data[:msg_size]
                                    data = data[msg_size:]
                                    # unpack image using pickle
                                    frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
                                    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

                                    # TODO: Update view of frame
                                    print("server comm before pub sub", self.port)
                                    wx.CallAfter(pub.sendMessage, f"update frame-{self.port}", video_frame=frame)
                                    #cv2.imshow('server', frame)
                                    #cv2.waitKey(1)
                                    self.video_q.put(frame)

                            else:       # Stills port
                                self.stills_q.put(data)

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

    def send_message(self, ip, message):
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
            soc.close()
            del self.open_clients[soc]



    def get_path(self):

        if self.port % 2 == 0:  # Making sure it's the video port
            dir_name = "Video"
        else:
            dir_name = "Stills"

        myDB = DB_Class.DB("myDB")


        mac = myDB.get_mac_by_port(self.port)

        myDB.close()

        mac = mac.replace(":", "_")

        date = datetime.today().strftime('%Y_%m_%d')

        path = f"{os.getcwd()}\\Server\\{dir_name}\\{mac}_{date}"

        if not os.path.exists(path):
            os.mkdir(path)
        print(path)
        return path



    def handle_video_rec(self):
        print("HANDLEVIDEO")
        # Creating the video file to which the stream is being recorded
        fourcc = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')

        hour = datetime.today().strftime('%H_%M_%S')

        while self.path is None:
            pass

        VideoWriter = cv2.VideoWriter(f"{self.path}\\{hour}.avi", fourcc, 5.0, (530, 300))


        while True:

            frame = self.video_q.get()
            # Saving the frame to the video
            VideoWriter.write(frame)

    def handle_stills(self):

        count = 1

        while True:
            pic = self.stills_q.get()

            with open(f"{self.path}\\pic_{count}", "wb") as f:
                f.write(pic)

            count+=1

if __name__ == '__main__':
    server = ServerComms(Setting.VIDEO_PORT)