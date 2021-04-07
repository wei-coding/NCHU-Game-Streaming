# -*- coding: utf-8 -*-
"""
Created on Sat Mar  6 23:02:31 2021

@author: leo
"""
from pynput.mouse import Listener

import socket
import time
HOST = '192.168.31.174'
PORT = 8000
clientMessage = ['mp',6,89]
print(clientMessage)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
print("connet success")

#client.close()

import json
ax=0
bx=0
def mouse_Thread():
    #from pynput.mouse import Listener
    
    def on_move(x, y):
        print('Pointer moved to {0}'.format(
            (x, y)))
        #print(type(x))
        if(ax!=x and bx!=y):        
            tojson={'0':'mm','1':x,'2':y}       
            #print(time.time())
            tojson=json.dumps(tojson)
            print(tojson)
            client.send(tojson.encode())
    def on_click(x, y, button, pressed):
        print('{0} at {1}'.format(
            'Pressed' if pressed else 'Released',
            (x, y)))
        print(button)
        print(type(button),type(pressed))
        tojson={'0':'mp','1':x,'2':y}       
        print(tojson)
        tojson=json.dumps(tojson)
        print(tojson)
        client.send(tojson.encode())
        if not pressed:
            # Stop listener
            tojson={'0':'mr','1':x,'2':y}       
            print(tojson)
            tojson=json.dumps(tojson)
            print(tojson)
            client.send(tojson.encode())
            return False
    def on_scroll(x, y, dx, dy):
        print('Scrolled ',x,y,dx,dy)
        tojson={'0':'mm','1':dx,'2':dy}       
        print(tojson)
        tojson=json.dumps(tojson)
        print(tojson)
        client.send(tojson.encode())
    # Collect events until released
    with Listener(
            on_move=on_move,
            on_click=on_click,
            on_scroll=on_scroll) as listener:
        listener.join()
#keyboard   
check_if_press ={'get':[]}
from pynput import keyboard
def keyboard_Thread():
    
    def on_press(key):
        try:
            print('alphanumeric key {0} pressed'.format(
                key.char))
            #print(type(key),key)
            if(key.char not in check_if_press['get']):
                check_if_press['get'].append(key.char)
                a={'0':'kp','1':key.char,'2':5}       
                b=json.dumps(a)
                print('inside',b)
                client.send(b.encode())
                
            else:
                print('is pressed',key.char)
            
            
            
        except AttributeError:
            print('special key {0} pressed'.format(
                key))
            print(key)
            #sepcial key
            if key == keyboard.Key.esc:
            # Stop listener
                return False
            if(key==keyboard.Key.up):
                a={'0':'kp','1':'up','2':0}
            elif(key==keyboard.Key.down):
                a={'0':'kp','1':'down','2':0}
            elif(key==keyboard.Key.left):
                a={'0':'kp','1':'left','2':0}
            elif(key==keyboard.Key.right):
                a={'0':'kp','1':'right','2':0}
            elif(key==keyboard.Key.enter):
                a={'0':'kp','1':'enter','2':0}
         
            #a={'0':'kp','1':key.char,'2':0}      
            #print(a)
            b=json.dumps(a)
            print(b)
            client.send(b.encode())
    def on_release(key):
        try:            
            print('{0} released'.format(key))
            if(key.char in check_if_press['get']):
                check_if_press['get'].remove(key.char)
                a={'0':'kr','1':key.char,'2':5}       
                #print(a)
                b=json.dumps(a)
                print(b)
                client.send(b.encode())
                print('get',key.char)
            else:
                print('is used',key.char)
            
        except Exception:
            print('{0} released'.format(key))
            if(key==keyboard.Key.up):
                a={'0':'kr','1':'up','2':0}
            elif(key==keyboard.Key.down):
                a={'0':'kr','1':'down','2':0}
            elif(key==keyboard.Key.left):
                a={'0':'kr','1':'left','2':0}
            elif(key==keyboard.Key.right):
                a={'0':'kr','1':'right','2':0}
            elif(key==keyboard.Key.enter):
                a={'0':'kr','1':'enter','2':0}
            #print(a)
            b=json.dumps(a)
            print(b)
            client.send(b.encode())
        if key == keyboard.Key.esc:
            # Stop listener
            return False
    
    # Collect events until released
    with keyboard.Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        listener.join()

from threading import Thread
def f():
    print('a')
    st=time.time()
    while 1:
        if time.time()-st>0.2:
            check_if_press['get'].clear()
            st=time.time()
        
        
if __name__ == '__main__':
    p1= Thread(target=mouse_Thread)
    p1.start()
    p2=Thread(target=f)
    p2.start()
    p1.join()
    p2.join()
    