import time

import pyautogui
import threading
import keyboard


class WaitInputs:
    def __init__(self):
        self.space = False
        self.q = False
        self.w = False

        threading.Thread(target=self.wait_for_space, ).start()
        threading.Thread(target=self.wait_for_q, ).start()
        threading.Thread(target=self.wait_for_w, ).start()
        threading.Thread(target=self.print_booleans, ).start()

    def wait_for_space(self):
        while True:
            keyboard.wait('space')
            print('Space was pressed')
            self.space = not self.space

    def wait_for_q(self):
        while True:
            keyboard.wait('q')
            print('q was pressed')
            self.q = not self.q

    def wait_for_w(self):
        while True:
            keyboard.wait('w')
            print('w was pressed')
            self.w = not self.w

    def print_booleans(self):
        while True:
            keyboard.wait('p')
            print(f"Space is {self.space}, Q is {self.q}, W is {self.w}")


if __name__ == '__main__':
    wait_inputs_mine = WaitInputs()

    while True:
        time.sleep(1)
