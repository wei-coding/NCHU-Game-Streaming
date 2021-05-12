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
import pydirectinput
pydirectinput.PAUSE=0
from protocol import *


class ServerSide(threading.Thread):
    def __init__(self, port, parent=None):
        threading.Thread.__init__(self)
        self.parent = parent
        self.port = port
        self.stop = False
        self.keyboard_control = None
        self.mouse_control = None

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
            next_signal = None
            signal = None
            try:
                clientMessage = (self.conn.recv(8))
                signal = GSSPBody.from_buffer_copy(clientMessage)
                print(clientMessage)
            except:
                traceback.print_exc()
                exit(-1)
            if signal.type == GSSP.MOUSE:
                if signal.action == GSSP.M:
                    self.mmove(signal.x, signal.y)
                elif signal.action == GSSP.PL:
                    self.mpress(1)
                elif signal.action == GSSP.RL:
                    self.mrelease(1)
                elif signal.action == GSSP.PR:
                    self.mpress(0)
                elif signal.action == GSSP.RR:
                    self.mrelease(0)
                elif signal.action == GSSP.S:
                    self.mscroll(signal.x, signal.y)
            elif signal.type == GSSP.KEYBOARD:
                if signal.action == GSSP.PR:
                    if signal.special == GSSP.UP:
                        pydirectinput.keyDown("up")
                    elif signal.special == GSSP.DOWN:
                        pydirectinput.keyDown("down")
                    elif signal.special == GSSP.LEFT:
                        pydirectinput.keyDown("left")
                    elif signal.special == GSSP.RIGHT:
                        pydirectinput.keyDown("right")
                    elif signal.special == GSSP.ENTER:
                        pydirectinput.keyDown("enter")
                    elif signal.special == GSSP.SPACE:
                        pydirectinput.keyDown("space")
                    elif signal.special == GSSP.CT:
                        pydirectinput.keyDown("ctrl")
                    elif signal.special == GSSP.SHIFT:
                        pydirectinput.keyDown("shift")
                    else:
                        btn = signal.btn.decode("utf-8")
                        self.kpress(btn)
                elif signal.action == GSSP.RR:
                    if signal.special == GSSP.UP:
                        pydirectinput.keyUp("up")
                    elif signal.special == GSSP.DOWN:
                        pydirectinput.keyUp("down")
                    elif signal.special == GSSP.LEFT:
                        pydirectinput.keyUp("left")
                    elif signal.special == GSSP.RIGHT:
                        pydirectinput.keyUp("right")
                    elif signal.special == GSSP.ENTER:
                        pydirectinput.keyUp("enter")
                    elif signal.special == GSSP.SPACE:
                        pydirectinput.keyDown("space")
                    elif signal.special == GSSP.CT:
                        pydirectinput.keyDown("ctrl")
                    elif signal.special == GSSP.SHIFT:
                        pydirectinput.keyDown("shift")
                    else:
                        btn = signal.btn.decode("utf-8")
                        print("call release", btn)
                        self.krelease(btn)

    def mmove(self, x, y):
        # self.mouse_control.position = (x, y)
        pydirectinput.moveTo(x, y)
        # self.parent.logs.appendPlainText(f'Keyboard/Mouse: {self.mouse_control.position}')

    def mpress(self, left):
        if left == 1:
            # self.mouse_control.press(mouse.Button.left)
            pydirectinput.mouseDown()
            print('Keyboard/Mouse_left: mouse has press')
        elif left == 0:
            # self.mouse_control.press(mouse.Button.right)
            pydirectinput.mouseDown(button='right')
            print('Keyboard/Mouse_right: mouse has press')
        # self.parent.logs.appendPlainText('Keyboard/Mouse: mouse has press')
        # print('Keyboard/Mouse: mouse has press')

    def mrelease(self, left):
        if left==1 :
            # self.mouse_control.release(mouse.Button.left)
            pydirectinput.mouseUp()
            print('Keyboard/Mouse_left: mouse has release')
        if left==0 :
            # self.mouse_control.release(mouse.Button.right)
            pydirectinput.mouseUp(button='right')
            print('Keyboard/Mouse_right: mouse has release')
        # self.parent.logs.appendPlainText('Keyboard/Mouse: mouse has release')
        print('Keyboard/Mouse: mouse has release')

    def mscroll(self, x, y):
        self.mouse_control.scroll(x, y)
        # self.parent.logs.appendPlainText('Keyboard/Mouse: mouse scroll',x,y)

    def kpress(self, a):
        # self.keyboard_control.press(a)
        pydirectinput.keyDown(a)
        # self.parent.logs.appendPlainText(f'Keyboard/Mouse: keyboard press {a}')
        print(f'Keyboard/Mouse: keyboard press {a}')

    def krelease(self, a):
        #self.keyboard_control.release(a)
        pydirectinput.keyUp(a)
        # self.parent.logs.appendPlainText(f'Keyboard/Mouse: keyboard release {a}')
        print(f'Keyboard/Mouse: keyboard release {a}')

    def kill(self):
        self.stop = True


