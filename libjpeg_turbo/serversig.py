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
    def __init__(self, port, parent=None):
        threading.Thread.__init__(self)
        self.parent = parent
        self.port = port
        self.stop = False

    def run(self):
        self.parent.logs.appendPlainText("Keyboard/Mouse system connecting")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('0.0.0.0', self.port))
        server.listen(10)
        self.conn, self.addr = server.accept()

        self.parent.logs.appendPlainText("Keyboard/Mouse connect success")
        self.mouse_control = mouse.Controller()
        self.keyboard_control = keyboard.Controller()
        while not self.stop:
            signal = None
            try:
                clientMessage = (self.conn.recv(1024))
                # signal = json.loads(clientMessage)
                signal = GSSPBody.from_buffer_copy(clientMessage)
            except:
                traceback.print_exc()
                exit(-1)
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
                    elif signal.special == GSSP.RIGHT:
                        self.keyboard_control.press(keyboard.Key.right)
                    elif signal.special == GSSP.ENTER:
                        self.keyboard_control.press(keyboard.Key.enter)
                    else:
                        btn = signal.btn.decode("utf-8")
                        self.kpress(btn)
                elif signal.action == GSSP.R:
                    if signal.special == GSSP.UP:
                        self.keyboard_control.release(keyboard.Key.up)
                    elif signal.special == GSSP.DOWN:
                        self.keyboard_control.release(keyboard.Key.down)
                    elif signal.special == GSSP.LEFT:
                        self.keyboard_control.release(keyboard.Key.left)
                    elif signal.special == GSSP.RIGHT:
                        self.keyboard_control.release(keyboard.Key.right)
                    elif signal.special == GSSP.ENTER:
                        self.keyboard_control.release(keyboard.Key.enter)
                    else:
                        btn = signal.btn.decode("utf-8")
                        self.krelease(btn)

    def mmove(self, x, y):
        self.mouse_control.position = (x, y)
        self.parent.logs.appendPlainText(f'Keyboard/Mouse: {self.mouse_control.position}')

    def mpress(self):
        self.mouse_control.press(mouse.Button.left)
        self.parent.logs.appendPlainText('Keyboard/Mouse: mouse has press')

    def mrelease(self):
        self.mouse_control.release(mouse.Button.left)
        self.parent.logs.appendPlainText('Keyboard/Mouse: mouse has release')

    def mscroll(self, x, y):
        self.mouse_control.scroll(x, y)
        self.parent.logs.appendPlainText('Keyboard/Mouse: mouse scroll')

    def kpress(self, a):
        self.keyboard_control.press(a)
        self.parent.logs.appendPlainText(f'Keyboard/Mouse: keyboard press {a}')

    def krelease(self, a):
        self.keyboard_control.release(a)
        self.parent.logs.appendPlainText(f'Keyboard/Mouse: keyboard release {a}')

    def kill(self):
        self.stop = True
