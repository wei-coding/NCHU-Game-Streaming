# -*- coding: utf-8 -*-
"""
Created on Sat Mar  6 23:02:31 2021

@author: leo
"""
import socket
import threading
import traceback

from pynput import keyboard
from pynput import mouse

from libjpeg_turbo.protocol import *


class ServerSide(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        HOST = '0.0.0.0'
        PORT = port
        print("connecting")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((HOST, PORT))
        server.listen(10)
        self.conn, self.addr = server.accept()
        print("connect success")

        self.mouse_control = mouse.Controller()
        self.keyboard_control = keyboard.Controller()

    def run(self):
        while True:
            try:
                clientMessage = (self.conn.recv(1024))
                # signal = json.loads(clientMessage)
                signal = GSSPBody.from_buffer_copy(clientMessage)

                # print (clientMessage)
                print(signal)
                if signal.type == GSSP.MOUSE:
                    if signal.action == GSSP.M:
                        self.mmove(signal.x, signal.y)
                    elif signal.action == GSSP.P:
                        self.mpress()
                    elif signal.action == GSSP.R:
                        self.mrelease()
                    elif signal.action == GSSP.S:
                        self.mscroll(signal.x, signal.y)
                elif signal.type == GSSP.KEYBOARD:
                    if signal.action == GSSP.P:
                        if signal.special == GSSP.UP:
                            self.keyboard_control.press(keyboard.Key.up)
                        elif signal.special == GSSP.DOWN:
                            self.keyboard_control.press(keyboard.Key.down)
                        elif signal.special == GSSP.LEFT:
                            self.keyboard_control.press(keyboard.Key.left)
                            # pressing('left')
                        elif signal.special == GSSP.RIGHT:
                            self.keyboard_control.press(keyboard.Key.right)
                            # pressing('right')
                        elif signal.special == GSSP.ENTER:
                            self.keyboard_control.press(keyboard.Key.enter)
                            # pressing('enter')
                        else:
                            btn = signal.btn.decode("utf-8")
                            self.kpress(btn)
                        # kpress(signal['1'])
                    elif signal.action == GSSP.R:
                        if signal.special == GSSP.UP:
                            self.keyboard_control.release(keyboard.Key.up)
                            # check_if_press.remove('up')
                        elif signal.special == GSSP.DOWN:
                            self.keyboard_control.release(keyboard.Key.down)
                            # check_if_press.remove('down')
                        elif signal.special == GSSP.LEFT:
                            self.keyboard_control.release(keyboard.Key.left)
                            # check_if_press.remove('left')
                        elif signal.special == GSSP.RIGHT:
                            self.keyboard_control.release(keyboard.Key.right)
                            # check_if_press.remove('right')
                        elif signal.special == GSSP.ENTER:
                            self.keyboard_control.release(keyboard.Key.enter)
                            # check_if_press.remove('enter')
                        else:
                            btn = signal.btn.decode("utf-8")
                            self.krelease(btn)
            except:
                traceback.print_exc()

    def mmove(self, x, y):
        self.mouse_control.position = (x, y)
        print(self.mouse_control.position)
        # print(time.time())

    def mpress(self):
        self.mouse_control.press(mouse.Button.left)
        print('mouse has press')
        # print(time.time())

    def mrelease(self):
        self.mouse_control.release(mouse.Button.left)
        print('mouse has release')
        # print(time.time())
        # exit(1)

    def mscroll(self, x, y):
        self.mouse_control.scroll(x, y)
        print('mouse scroll')
        # print(time.time())

    def kpress(self, a):
        # keyboard.press(a)
        self.keyboard_control.press(a)
        print('keyboard press', a)

        # pressing(a)

    def krelease(self, a):
        self.keyboard_control.release(a)
        print('keyboard release', a)


# start the main
# socket connect


def mmove(mouse_control, x, y):
    mouse_control.position = (x, y)
    print(mouse_control.position)
    # print(time.time())


def mpress(mouse_control):
    mouse_control.press(mouse.Button.left)
    print('mouse has press')
    # print(time.time())


def mrelease(mouse_control):
    mouse_control.release(mouse.Button.left)
    print('mouse has release')
    # print(time.time())
    # exit(1)


def mscroll(mouse_control, x, y):
    mouse_control.scroll(x, y)
    print('mouse scroll')
    # print(time.time())


def kpress(keyboard_control, a):
    # keyboard.press(a)
    keyboard_control.press(a)
    print('keyboard press', a)


def krelease(keyboard_control, a):
    keyboard_control.release(a)
    print('keyboard release', a)


def main():
    HOST = '0.0.0.0'
    PORT = 8000
    print("connecting")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(10)
    conn, addr = server.accept()
    print("connect success")

    mouse_control = mouse.Controller()
    keyboard_control = keyboard.Controller()

    while True:
        try:
            clientMessage = (conn.recv(1024))
            # signal = json.loads(clientMessage)
            signal = GSSPBody.from_buffer_copy(clientMessage)

            # print (clientMessage)
            print(signal)
            if signal.type == GSSP.MOUSE:
                if signal.action == GSSP.M:
                    mmove(mouse_control, signal.x, signal.y)
                elif signal.action == GSSP.P:
                    mpress(mouse_control)
                elif signal.action == GSSP.R:
                    mrelease(mouse_control)
                elif signal.action == GSSP.S:
                    mscroll(mouse_control, signal.x, signal.y)
            elif signal.type == GSSP.KEYBOARD:
                if signal.action == GSSP.P:
                    if signal.special == GSSP.UP:
                        keyboard_control.press(keyboard.Key.up)
                    elif signal.special == GSSP.DOWN:
                        keyboard_control.press(keyboard.Key.down)
                    elif signal.special == GSSP.LEFT:
                        keyboard_control.press(keyboard.Key.left)
                        # pressing('left')
                    elif signal.special == GSSP.RIGHT:
                        keyboard_control.press(keyboard.Key.right)
                        # pressing('right')
                    elif signal.special == GSSP.ENTER:
                        keyboard_control.press(keyboard.Key.enter)
                        # pressing('enter')
                    else:
                        btn = signal.btn.decode("utf-8")
                        kpress(keyboard_control, btn)
                    # kpress(signal['1'])
                elif signal.action == GSSP.R:
                    if signal.special == GSSP.UP:
                        keyboard_control.release(keyboard.Key.up)
                        # check_if_press.remove('up')
                    elif signal.special == GSSP.DOWN:
                        keyboard_control.release(keyboard.Key.down)
                        # check_if_press.remove('down')
                    elif signal.special == GSSP.LEFT:
                        keyboard_control.release(keyboard.Key.left)
                        # check_if_press.remove('left')
                    elif signal.special == GSSP.RIGHT:
                        keyboard_control.release(keyboard.Key.right)
                        # check_if_press.remove('right')
                    elif signal.special == GSSP.ENTER:
                        keyboard_control.release(keyboard.Key.enter)
                        # check_if_press.remove('enter')
                    else:
                        btn = signal.btn.decode("utf-8")
                        krelease(keyboard_control, btn)
        except:
            traceback.print_exc()


if __name__ == '__main__':
    s = ServerSide(8000)
    s.start()
    s.join()
