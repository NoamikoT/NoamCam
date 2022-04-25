import winsound


class AlarmSound():
    """A class for sounding an alarm"""

    def __init__(self, duration):

        self.duration = duration

    def play_alert(self):
        import winsound

        winsound.PlaySound('Sound.wav', winsound.SND_FILENAME)

    def play_beep(self):
        winsound.Beep(500, self.duration)
