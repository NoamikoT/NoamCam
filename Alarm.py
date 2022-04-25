import winsound


class AlarmSound():
    """A class for sounding an alarm"""

    def __init__(self, duration):

        self.duration = duration

    def play_sound(self):
        winsound.Beep(500, self.duration)
