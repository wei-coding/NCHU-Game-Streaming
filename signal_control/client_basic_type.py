# -*- coding: utf-8 -*-
"""
Created on Sat Mar  6 23:02:31 2021

@author: leo
"""
import json
import socket
from libjpeg_turbo.protocol import *
from threading import Thread

from pynput import keyboard
from pynput.mouse import Listener

HOST = '192.168.0.101'
PORT = 8001
clientMessage = GSSPBody(GSSP.KEYBOARD, GSSP.M, 0, 0, GSSP.NO_BTN, 0)
print(clientMessage)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
print("connet success")


def mouse_thread():

    def on_move(x, y):
        print('Pointer moved to {0}'.format((x, y)))
        data = GSSPBody(GSSP.MOUSE, GSSP.M, x, y, GSSP.NO_BTN, 0)
        client.send(data)

    def on_click(x, y, button, pressed):
        print('{0} at {1}'.format(
            'Pressed' if pressed else 'Released',
            (x, y)))
        print(button)
        data = GSSPBody(GSSP.MOUSE, GSSP.P, x, y, GSSP.NO_BTN, 0)
        client.send(data)
        if not pressed:
            data = GSSPBody(GSSP.MOUSE, GSSP.R, x, y, GSSP.NO_BTN, 0)
            client.send(data)

    def on_scroll(x, y, dx, dy):
        print('Scrolled ', x, y, dx, dy)
        data = GSSPBody(GSSP.MOUSE, GSSP.S, dx, dy, GSSP.NO_BTN, 0)
        client.send(data)

    # Collect events until released
    with Listener(
            on_move=on_move,
            on_click=on_click,
            on_scroll=on_scroll) as listener:
        listener.join()


# keyboard
# doc ={'get':[]}


def keyboard_thread():
    def on_press(key):
        try:
            print('alphanumeric key {0} pressed'.format(key.char))
            data = GSSPBody(GSSP.KEYBOARD, GSSP.P, 0, 0, bytes(key.char, encoding='utf-8'), 0)
            client.send(data)

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
            client.send(data)

    def on_release(key):
        try:
            data = GSSPBody(GSSP.KEYBOARD, GSSP.R, 0, 0, bytes(key.char, encoding='utf-8'), 0)
            client.send(data)
            print('get', key.char)
        except Exception:
            if key == keyboard.Key.esc:
                data = GSSPBody(GSSP.KEYBOARD, GSSP.R, 0, 0, GSSP.NO_BTN, GSSP.ESC)
                client.send(data)
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
            client.send(data)

    # Collect events until released
    with keyboard.Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        listener.join()


if __name__ == '__main__':
    p1 = Thread(target=mouse_thread, daemon=True)
    p1.start()
    p2 = Thread(target=keyboard_thread, daemon=True)
    p2.start()
    p1.join()
    p2.join()
