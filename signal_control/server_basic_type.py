# -*- coding: utf-8 -*-
"""
Created on Sat Mar  6 23:02:31 2021

@author: leo
"""
import json
from libjpeg_turbo.protocol import *
import socket

from pynput import keyboard
from pynput import mouse

mouse_control = mouse.Controller()
keyboard_control = keyboard.Controller()


def mmove(x, y):
    mouse_control.position = (x, y)
    print(mouse_control.position)
    # print(time.time())


def mpress():
    mouse_control.press(mouse.Button.left)
    print('mouse has press')
    # print(time.time())


def mrelease():
    mouse_control.release(mouse.Button.left)
    print('mouse has release')
    # print(time.time())
    # exit(1)


def mscroll(x, y):
    mouse_control.scroll(x, y)
    print('mouse scroll')
    # print(time.time())


def kpress(a):
    # keyboard.press(a)
    keyboard_control.press(a)
    print('keyboard press', a)

    # pressing(a)


def krelease(a):
    keyboard_control.release(a)
    print('keyboard release', a)


# start the main
# socket connect


HOST = '0.0.0.0'
PORT = 8000
print("connecting")
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(10)
conn, addr = server.accept()
print("connect success")

while True:
    try:
        clientMessage = (conn.recv(1024))
        # signal = json.loads(clientMessage)
        signal = GSSPBody.from_buffer_copy(clientMessage)

        # print (clientMessage)
        print(signal)
        if signal.type == GSSP.MOUSE:
            if signal.action == GSSP.M:
                mmove(signal.x, signal.y)
            elif signal.action == GSSP.P:
                mpress()
            elif signal.action == GSSP.R:
                mrelease()
            elif signal.action == GSSP.S:
                mscroll(signal.x, signal.y)
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
                    kpress(btn)
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
                    krelease(btn)
    except:
        pass
