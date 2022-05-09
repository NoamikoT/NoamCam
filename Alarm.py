from pygame import mixer


class AlarmSound:
    """A class for sounding an alarm"""

    def __init__(self):
        mixer.init()
        mixer.music.load("Siren.mp3")

    def play_alarm(self):
        mixer.music.play(loops=-1)

    def stop_alarm(self):
        mixer.music.stop()
