import queue
import ServerComms
import ServerProtocol
import threading
import DB_Class
import ServerGraphics
import wx
import Setting

mac_ip_dict = {}

def handle_mac_address(ip, mac, server):
    """Handling the mac address of a user"""
    myDB = DB_Class.DB("myDB")

    print(mac)
    if myDB.mac_exist(mac):
        port = myDB.get_port_by_mac(mac)
        video_server_comms = ServerComms.ServerComms(port)
        stills_server_comms = ServerComms.ServerComms(port + 1)

        mac_message = ServerProtocol.ServerProtocol.build_send_port(port)

        server.send_message(ip, mac_message)

        mac_ip_dict[mac] = ip

    myDB.close()


# A dictionary of functions
operation_dic = {'05': handle_mac_address}


def handle_receive_message(recv_q, server):
    """Handling the received message"""
    while True:
        ip, code, data = recv_q.get()
        if code in operation_dic.keys():
            operation_dic[code](ip, data, server)



def handle_graphics_q(graphics_comms, server):
    """Handling the received message"""
    while True:
        message, mac = graphics_comms.get()
        print("Handle graphics queue", message)

        if mac in mac_ip_dict.keys():
            ip = mac_ip_dict[mac]

            if message == "start face detection":
                print("DETECTION ON", ip)
                message = ServerProtocol.ServerProtocol.build_face_recognition("1")
                server.send_message(ip, message)
            elif message == "stop face detection":
                print("DETECTION OFF", ip)
                message = ServerProtocol.ServerProtocol.build_face_recognition("0")
                server.send_message(ip, message)



if __name__ == '__main__':

    graphics_comms = queue.Queue()
    # Create a queue to receive the messages
    recv_q = queue.Queue()

    # Create a server object
    server = ServerComms.ServerComms(Setting.GENERAL_PORT, recv_q)

    # Create a thread to handle the received message in the background
    threading.Thread(target=handle_receive_message, args=(recv_q, server,)).start()

    threading.Thread(target=handle_graphics_q, args=(graphics_comms, server,)).start()

    # Launching the app (ServerGraphics - WXPython)
    app = wx.App(False)
    graphics = ServerGraphics.MainFrame(server,graphics_comms)
    app.MainLoop()
