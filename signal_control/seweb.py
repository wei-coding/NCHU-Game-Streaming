# -*- coding: utf-8 -*-
"""
Created on Sat Mar  6 23:02:31 2021

@author: leo
"""
import time
from pynput.keyboard import Key, Controller
keyboard_control = Controller()
from pynput import keyboard

from  pynput.mouse import Button,Controller 
mouse = Controller() 
def mmove(x,y):
    mouse.position=(x,y)
    print(mouse.position)
    #print(time.time())
def mpress():
    mouse.press(Button.left)
    print('mouse has press')
    #print(time.time())
def mrelease():
    mouse.release(Button.left)
    print('mouse has releae')
    #print(time.time())
    exit(1)
def mscroll(x,y):
    mouse.scroll(x,y)
    print('mouse scroll')
    #print(time.time())
def kpress(a):
    #keyboard.press(a)
    keyboard_control.press(a)
    print('keyboard press',a)
def krelease(a):
    keyboard_control.release(a)
    print('keyboard release',a)
import json
import socket
HOST = '192.168.31.207'
PORT = 8000 
print("connecting")
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(10)
conn, addr = server.accept()
print("connect success")
#count=0
while True:
    #count+=1
    #print(time.time())
    clientMessage = (conn.recv(1024))
    signal=json.loads(clientMessage)
    #print (clientMessage)
    print(signal)
    if signal['0']=='mm':
        mmove(int(signal['1']),int(signal['2']))
    elif signal['0']=='mp':
        mpress()
    elif signal['0']=='mr':
        mrelease()
    elif signal['0']=='ms':
        mscroll(int(signal['1']), int(signal['2']))
    elif signal['0']=='kp':
        if signal['1']=='up':
            keyboard_control.press(keyboard.Key.up)
        elif signal['1']=='down':
            keyboard_control.press(keyboard.Key.down)
        elif signal['1']=='left':
            keyboard_control.press(keyboard.Key.left)
        elif signal['1']=='right':
            keyboard_control.press(keyboard.Key.right)
        elif signal['1']=='enter':
            keyboard_control.press(keyboard.Key.enter)
        else :   
            kpress(signal['1'])
        #kpress(signal['1'])            
    elif signal['0']=='kr':
        if signal['1']=='up':
            keyboard_control.release(keyboard.Key.up)
        elif signal['1']=='down':
            keyboard_control.release(keyboard.Key.down)
        elif signal['1']=='left':
            keyboard_control.release(keyboard.Key.left)
        elif signal['1']=='right':
            keyboard_control.release(keyboard.Key.right)
        elif signal['1']=='enter':
            keyboard_control.release(keyboard.Key.enter)
        else:
            krelease((signal['1']))
    """i=0
    j=0
    signal=['','','']
    while(i<len(clientMessage)):
        if clientMessage[i]!=',':           `
            signal[j]+=(clientMessage[i])
        else:
            j+=1
        i+=1"""
        
    #print('Client message is:',signal)
    #print('message is ',clientMessage)
    #serverMessage = 'I\'m here!'
    #conn.sendall(serverMessage.encode())
    
    #conn.close()      