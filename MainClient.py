import ClientComms
import queue
import Setting
import threading
import ClientCamera2

quit_q = queue.Queue()

def open_video_stills_comms(port):
    video_client_comms = ClientComms.ClientComms(port)
    client_camera = ClientCamera2.ClientCamera(video_client_comms, None)
    client_camera.start_camera()
    x = quit_q.get()
    client_camera.stop_camera()
    # stills_clinet_comms = ClientComms.ClientComms(port + 1)


operation_dic = {}
operation_dic['06'] = open_video_stills_comms


def handle_msgs(rcv_q, quit_q):
    while True:
        code, data = rcv_q.get()
        if code in operation_dic.keys():
            operation_dic[code](data)

        elif code == "QU":
            quit_q.put("CLOSE")






if __name__ == '__main__':
    rcv_q = queue.Queue()
    main_client = ClientComms.ClientComms(Setting.GENERAL_PORT, recv_q=rcv_q)
    threading.Thread(target=handle_msgs,args=(rcv_q,quit_q,)).start()







