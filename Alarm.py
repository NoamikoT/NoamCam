from pygame import mixer


class AlarmSound:
    """A class for sounding an alarm"""

    def __init__(self):
        """Creating the mixer and loading the music"""
        mixer.init()
        mixer.music.load("Siren.mp3")

    def play_alarm(self):
        """
        The function plays an alarm infinitely
        """
        mixer.music.play(loops=-1)

    def stop_alarm(self):
        """
        The function stops the alarm
        """
        mixer.music.stop()
