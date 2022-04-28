import ClientComms
import queue
import Setting
import threading
import ClientCamera2

quit_q = queue.Queue()
# client_camera = None

def open_video_stills_comms(port):
    video_client_comms = ClientComms.ClientComms(port)
    client_camera = ClientCamera2.ClientCamera(video_client_comms, None)
    client_camera.start_camera()
    # x = quit_q.get()
    # client_camera.stop_camera()
    # stills_clinet_comms = ClientComms.ClientComms(port + 1)


operation_dic = {}
operation_dic['06'] = open_video_stills_comms



def handle_msgs(rcv_q, quit_q):
    client_camera = None
    while True:
        code, data = rcv_q.get()
        print("Handlemsgs", code, data)
        if code == "06":
            # operation_dic[code](data)
            video_client_comms = ClientComms.ClientComms(data)
            client_camera = ClientCamera2.ClientCamera(video_client_comms, data+1)
            client_camera.start_camera()

        elif code == "01":      # Face rec protocol
            if client_camera:
                print("In client camera")
                if data == "Stop face recognition":
                    client_camera.stop_detection()
                elif data == "Start face recognition":
                    client_camera.start_detection()


        elif code == "QU":
            quit_q.put("CLOSE")








if __name__ == '__main__':
    rcv_q = queue.Queue()
    main_client = ClientComms.ClientComms(Setting.GENERAL_PORT, recv_q=rcv_q)
    threading.Thread(target=handle_msgs,args=(rcv_q,quit_q,)).start()







