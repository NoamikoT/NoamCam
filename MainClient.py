import ClientComms
import queue
import Setting
import threading
import ClientCamera2

import atexit


def open_video_stills_comms(port):
    video_client_comms = ClientComms.ClientComms(port)
    client_camera = ClientCamera2.ClientCamera(video_client_comms, None)
    client_camera.start_camera()
    return client_camera

    # stills_clinet_comms = ClientComms.ClientComms(port + 1)


operation_dic = {}
operation_dic['06'] = open_video_stills_comms


def handle_msgs(rcv_q):
    client_camera = None
    atexit.register(exit_handler,client_camera)
    while True:
        code, data = rcv_q.get()
        if code in operation_dic.keys():
            if code == "06":
                client_camera=operation_dic[code](data)

        # elif code == "QU":
        #     print("hi")
        #     client_camera.stop_camera()
        #     client_camera.close_camera()
        #     break




def exit_handler(client_camera):
    print("end")
    client_camera.stop_camera()
    client_camera.close_camera()





if __name__ == '__main__':
    rcv_q = queue.Queue()
    main_client = ClientComms.ClientComms(Setting.GENERAL_PORT, recv_q=rcv_q)
    threading.Thread(target=handle_msgs,args=(rcv_q,)).start()







