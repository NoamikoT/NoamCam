import winsound
import threading
import time


class AlarmSound():
    """A class for sounding an alarm"""

    def __init__(self):
        self.play_now = False

        self.alarm_thread = threading.Thread(target=self.play_alert, ).start()

    def play_alert(self):

        while True:
            if self.play_now == True:
                winsound.PlaySound('Sound.wav', winsound.SND_FILENAME)
                self.play_now = False
            time.sleep(3)

    def play_beep(self):
        winsound.Beep(500, 4000)
