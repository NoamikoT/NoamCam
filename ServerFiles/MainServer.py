import queue
import ServerComms
import ServerProtocol
import threading
import DB_Class
import ServerGraphics
import wx
import Setting
import Email


mac_ip_dict = {}


def handle_mac_address(ip, mac, server, mail_q):
    """Handling the mac address of a user"""
    myDB = DB_Class.DB("myDB")

    # Printing the MAC Addresses to add them to the database
    print("MAC - ", mac)
    if myDB.mac_exist(mac):
        port = myDB.get_port_by_mac(mac)
        video_server_comms = ServerComms.ServerComms(port)
        stills_server_comms = ServerComms.ServerComms(port + 1, mail_q=mail_q)

        mac_message = ServerProtocol.ServerProtocol.build_send_port(port)

        server.send_message(ip, mac_message)

        mac_ip_dict[mac] = ip

    myDB.close()


# A dictionary of functions
operation_dic = {'05': handle_mac_address}


def handle_receive_message(recv_q, server, mail_q):
    """Handling the received message"""
    while True:
        ip, code, data = recv_q.get()
        if code in operation_dic.keys():
            operation_dic[code](ip, data, server, mail_q)


def handle_mail(mail_q):
    myDB = DB_Class.DB("myDB")
    managers_mails = myDB.get_managers_mails()
    managers_names = myDB.get_managers_names()
    myDB.close()
    email_obj = Email.EmailClass('PythonCameraAlert@gmail.com', 'ALERTWASFOUND')
    while True:
        file = mail_q.get()
        for manager in range(len(managers_mails)):
            email_obj.send_mail(file, managers_mails[manager], managers_names[manager])


def handle_graphics_q(graphics_comms, server):
    """Handling the received message"""
    while True:
        message, mac = graphics_comms.get()

        if mac in mac_ip_dict.keys():
            ip = mac_ip_dict[mac]

            if message == "start face detection":
                message = ServerProtocol.ServerProtocol.build_face_recognition("1")
                server.send_message(ip, message)
            elif message == "stop face detection":
                message = ServerProtocol.ServerProtocol.build_face_recognition("0")
                server.send_message(ip, message)
            elif message == "Zoom":
                message = ServerProtocol.ServerProtocol.build_zoom(mac)
                server.send_message(ip, message)

            elif message == "Unzoom":
                message = ServerProtocol.ServerProtocol.build_unzoom(mac)
                server.send_message(ip, message)

            elif message == "ALERT ON":
                message = ServerProtocol.ServerProtocol.build_siren_on(mac)
                server.send_message(ip, message)

            elif message == "ALERT OFF":
                message = ServerProtocol.ServerProtocol.build_siren_off(mac)
                server.send_message(ip, message)


if __name__ == '__main__':


    graphics_comms = queue.Queue()
    # Create a queue to receive the messages
    recv_q = queue.Queue()
    mail_q = queue.Queue()

    # Create a server object
    server = ServerComms.ServerComms(Setting.GENERAL_PORT, recv_q, mail_q)

    # Create a thread to handle the received message in the background
    threading.Thread(target=handle_receive_message, args=(recv_q, server, mail_q, )).start()

    threading.Thread(target=handle_graphics_q, args=(graphics_comms, server,)).start()

    threading.Thread(target=handle_mail, args=(mail_q,)).start()

    # Launching the app (ServerGraphics - WXPython)
    app = wx.App(False)
    graphics = ServerGraphics.MainFrame(server, graphics_comms)
    app.MainLoop()
