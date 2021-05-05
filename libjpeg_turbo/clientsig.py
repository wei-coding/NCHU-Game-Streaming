# -*- coding: utf-8 -*-
"""
Created on Sat Mar  6 23:02:31 2021

@author: leo
"""
import socket
from libjpeg_turbo.protocol import *
import threading
from PyQt5.QtWidgets import QApplication

from pynput import keyboard
from pynput.mouse import Listener,Button


class ClientSide(threading.Thread):
    def __init__(self, server_ip, port, parent):
        threading.Thread.__init__(self)
        self.daemon = True
        self.server_ip = server_ip
        self.port = port
        self.parent = parent
        self.mouse_thread = MouseThread(self)
        self.keyboard_thread = KeyboardThread(self)
        self.client = None

    def run(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.server_ip, self.port))
        self.mouse_thread.start()
        self.keyboard_thread.start()
        self.mouse_thread.join()
        self.keyboard_thread.join()

    def kill(self):
        self.join(0)
        exit(0)


class MouseThread(threading.Thread):
    def __init__(self, parent):
        threading.Thread.__init__(self)
        self.daemon = True
        self.parent = parent

    def run(self):
        with Listener(
                on_move=self.on_move,
                on_click=self.on_click,
                on_scroll=self.on_scroll) as listener:
            listener.join()

    def on_move(self, x, y):
        # print('Pointer moved to {0}'.format((x, y)))
        x = x * 1680 // 1920
        y = y * 1050 // 1080
        data = GSSPBody(GSSP.MOUSE, GSSP.M, x, y, GSSP.NO_BTN, 0)
        self.parent.client.send(data)

    def on_click(self, x, y, button, pressed):
        x = x * 1680 // 1920
        y = y * 1050 // 1080
        print('{0} at {1}'.format(pressed, (x, y)))
        # print(button)
        if not pressed:
            if button == Button.left:
                data = GSSPBody(GSSP.MOUSE, GSSP.RL, x, y, GSSP.NO_BTN, 0)
                self.parent.client.send(data)
            else :
                data = GSSPBody(GSSP.MOUSE, GSSP.RR, x, y, GSSP.NO_BTN, 0)
                self.parent.client.send(data)
        else:
            if button == Button.left:
                data = GSSPBody(GSSP.MOUSE, GSSP.PL, x, y, GSSP.NO_BTN, 0)
                self.parent.client.send(data)
            else :
                data = GSSPBody(GSSP.MOUSE, GSSP.PR, x, y, GSSP.NO_BTN, 0)
                self.parent.client.send(data)

    def on_scroll(self, x, y, dx, dy):
        # print('Scrolled ', x, y, dx, dy)
        data = GSSPBody(GSSP.MOUSE, GSSP.S, dx, dy, GSSP.NO_BTN, 0)
        self.parent.client.send(data)


class KeyboardThread(threading.Thread):
    def __init__(self, parent):
        threading.Thread.__init__(self)
        self.daemon = True
        self.parent = parent

    def run(self):
        with keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release) as listener:
            listener.join()

    def on_press(self, key):
        try:
            print('alphanumeric key {0} pressed'.format(key.char))
            data = GSSPBody(GSSP.KEYBOARD, GSSP.PR, 0, 0, bytes(key.char, encoding='utf-8'), 0)
            self.parent.client.send(data)
        except AttributeError:
            print('special key {0} pressed'.format(key))
            print(key)
            action = 0
            if key == keyboard.Key.up:
                action = GSSP.UP
            elif key == keyboard.Key.down:
                action = GSSP.DOWN
            elif key == keyboard.Key.left:
                action = GSSP.LEFT
            elif key == keyboard.Key.right:
                action = GSSP.RIGHT
            else:
                action = GSSP.ENTER

            data = GSSPBody(GSSP.KEYBOARD, GSSP.PR, 0, 0, 0, action)
            self.parent.client.send(data)

    def on_release(self, key):
        try:
            data = GSSPBody(GSSP.KEYBOARD, GSSP.RR, 0, 0, bytes(key.char, encoding='utf-8'), 0)
            self.parent.client.send(data)
            print('{0} released'.format(key.char))
        except Exception:
            if key == keyboard.Key.esc:
                data = GSSPBody(GSSP.KEYBOARD, GSSP.RR, 0, 0, GSSP.NO_BTN, GSSP.ESC)
                self.parent.client.send(data)
                exit(1)
            print('{0} released'.format(key))

            switch = {
                keyboard.Key.up: GSSP.UP,
                keyboard.Key.down: GSSP.DOWN,
                keyboard.Key.left: GSSP.LEFT,
                keyboard.Key.right: GSSP.RIGHT,
                keyboard.Key.enter: GSSP.ENTER,
            }
            data = GSSPBody(GSSP.KEYBOARD, GSSP.RR, 0, 0, 0, switch[key])
            self.parent.client.send(data)
