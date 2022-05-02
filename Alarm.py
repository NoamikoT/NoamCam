from pygame import mixer


class AlarmSound():
    """A class for sounding an alarm"""

    def __init__(self):
        mixer.init()
        mixer.music.load("Siren.mp3")

    def play_alarm(self):
        mixer.music.play(loops=-1)

    def stop_alarm(self):
        mixer.music.stop()

if __name__ == '__main__':
    x = AlarmSound()

    x.play_alarm()

    input("G")
    x.stop_alarm()

    # mixer.init()
    # mixer.music.load("Siren.mp3")
    # mixer.music.play(loops=-1)
    # input("G")
    # mixer.music.stop()