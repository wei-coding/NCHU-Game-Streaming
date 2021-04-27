# -*- coding: utf-8 -*-
"""
Created on Sat Mar  6 23:02:31 2021

@author: leo
"""
import socket
from libjpeg_turbo.protocol import *
import threading

from pynput import keyboard
from pynput.mouse import Listener


class ClientSide(threading.Thread):
    def __init__(self, server_ip, port, parent):
        threading.Thread.__init__(self)
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
        print('Pointer moved to {0}'.format((x, y)))
        data = GSSPBody(GSSP.MOUSE, GSSP.M, x, y, GSSP.NO_BTN, 0)
        self.parent.client.send(data)

    def on_click(self, x, y, button, pressed):
        print('{0} at {1}'.format(
            'Pressed' if pressed else 'Released',
            (x, y)))
        print(button)
        data = GSSPBody(GSSP.MOUSE, GSSP.P, x, y, GSSP.NO_BTN, 0)
        self.parent.client.send(data)
        if not pressed:
            data = GSSPBody(GSSP.MOUSE, GSSP.R, x, y, GSSP.NO_BTN, 0)
            self.parent.client.send(data)

    def on_scroll(self, x, y, dx, dy):
        print('Scrolled ', x, y, dx, dy)
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
            data = GSSPBody(GSSP.KEYBOARD, GSSP.P, 0, 0, bytes(key.char, encoding='utf-8'), 0)
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
            elif key == keyboard.Key.enter:
                action = GSSP.ENTER

            data = GSSPBody(GSSP.KEYBOARD, GSSP.P, 0, 0, 0, action)
            self.parent.client.send(data)

    def on_release(self, key):
        try:
            data = GSSPBody(GSSP.KEYBOARD, GSSP.R, 0, 0, bytes(key.char, encoding='utf-8'), 0)
            self.parent.client.send(data)
            print('get', key.char)
        except Exception:
            if key == keyboard.Key.esc:
                data = GSSPBody(GSSP.KEYBOARD, GSSP.R, 0, 0, GSSP.NO_BTN, GSSP.ESC)
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
            data = GSSPBody(GSSP.KEYBOARD, GSSP.R, 0, 0, 0, bytes(switch[key]))
            self.parent.client.send(data)
