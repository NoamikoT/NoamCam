import ClientComms
import queue
import Setting
import threading
import ClientCamera

quit_q = queue.Queue()


def open_video_stills_comms(port):
    video_client_comms = ClientComms.ClientComms(port)
    client_camera = ClientCamera.ClientCamera(video_client_comms, None)
    client_camera.start_camera()


operation_dic = {'06': open_video_stills_comms}


def handle_msgs(rcv_q, quit_q):
    client_camera = None
    while True:
        code, data = rcv_q.get()
        print("Handlemsgs", code, data)
        if code == "06":
            # operation_dic[code](data)
            video_client_comms = ClientComms.ClientComms(data)
            client_camera = ClientCamera.ClientCamera(video_client_comms, data+1)
            client_camera.start_camera()

        elif code == "01":      # Face rec protocol
            if client_camera:
                print("In client camera")
                if data == "Stop face recognition":
                    client_camera.stop_detection()
                elif data == "Start face recognition":
                    client_camera.start_detection()
        elif code == "07":      # Zoom protocol
            print("IN ZOOM")
            client_camera.start_zoom()
        elif code == "08":      # Unzoom protocol
            print("IN UNZOOM")
            client_camera.stop_zoom()

        elif code == "02":
            print("ALERTING")
            client_camera.set_siren_on()

        elif code == "09":
            print("STOP ALERTING")
            client_camera.set_siren_off()

        elif code == "QU":
            quit_q.put("CLOSE")


if __name__ == '__main__':
    rcv_q = queue.Queue()
    main_client = ClientComms.ClientComms(Setting.GENERAL_PORT, recv_q=rcv_q)
    threading.Thread(target=handle_msgs, args=(rcv_q, quit_q,)).start()
