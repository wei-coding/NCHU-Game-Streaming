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

HOST = 'localhost'
PORT = 8000
clientMessage = GSSPBody(GSSP.KEYBOARD, GSSP.M, 0, 0, GSSP.NO_BTN, 0)
print(clientMessage)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
print("connet success")
ax = 0
bx = 0


def mouse_thread():
    # from pynput.mouse import Listener

    def on_move(x, y):
        print('Pointer moved to {0}'.format((x, y)))
        # tojson = {'0': 'mm', '1': x, '2': y}
        # tojson = json.dumps(tojson)
        data = GSSPBody(GSSP.MOUSE, GSSP.M, x, y, GSSP.NO_BTN, 0)
        # print(tojson)
        client.send(data)

    def on_click(x, y, button, pressed):
        print('{0} at {1}'.format(
            'Pressed' if pressed else 'Released',
            (x, y)))
        print(button)
        # print(type(button),type(pressed))
        # tojson = {'0': 'mp', '1': x, '2': y}
        # tojson = json.dumps(tojson)
        # print(tojson)
        data = GSSPBody(GSSP.MOUSE, GSSP.P, x, y, GSSP.NO_BTN, 0)
        client.send(data)
        if not pressed:
            # Stop listener
            # tojson = {'0': 'mr', '1': x, '2': y}
            # print(tojson)
            # tojson = json.dumps(tojson)
            # print(tojson)
            data = GSSPBody(GSSP.MOUSE, GSSP.R, x, y, GSSP.NO_BTN, 0)
            client.send(data)
            # return False

    def on_scroll(x, y, dx, dy):
        print('Scrolled ', x, y, dx, dy)
        # tojson = {'0': 'ms', '1': dx, '2': dy}
        # print(tojson)
        # tojson = json.dumps(tojson)
        # print(tojson)
        data = GSSPBody(GSSP.MOUSE, GSSP.S, x, y, GSSP.NO_BTN, 0)
        client.send(data)
        # client.send(tojson.encode())

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
            print('alphanumeric key {0} pressed'.format(
                key.char))

            # a = {'0': 'kp', '1': key.char, '2': 5}
            # b = json.dumps(a)
            # print('inside', b)
            data = GSSPBody(GSSP.KEYBOARD, GSSP.P, 0, 0, bytes(key.char), 0)
            client.send(data)

        except AttributeError:
            print('special key {0} pressed'.format(key))
            print(key)
            switch = {
                keyboard.Key.up: GSSP.UP,
                keyboard.Key.down: GSSP.DOWN,
                keyboard.Key.left: GSSP.LEFT,
                keyboard.Key.right: GSSP.RIGHT,
                keyboard.Key.enter: GSSP.ENTER,
            }

            data = GSSPBody(GSSP.KEYBOARD, GSSP.P, 0, 0, switch[key], 0)

            # a={'0':'kp','1':key.char,'2':0}
            # print(a)
            # b = json.dumps(a)
            # print(b)
            client.send(data)
            # client.sendall(key)

    def on_release(key):
        try:
            data = GSSPBody(GSSP.KEYBOARD, GSSP.R, 0, 0, bytes(key.char), 0, 0)
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

            # a={'0':'kr','1':'a','2':0}
            # b = json.dumps(a)
            # print(b)
            data = GSSPBody(GSSP.KEYBOARD, GSSP.R, 0, 0, bytes(switch[key]), 0)
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
