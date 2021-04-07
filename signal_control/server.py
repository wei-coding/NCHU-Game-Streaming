# -*- coding: utf-8 -*-
"""
Created on Tue Mar  2 20:49:32 2021

@author: leo
"""

# -*- coding: utf-8 -*-
#import sys
import json
import socket
HOST = '192.168.56.1'
PORT = 8000 

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(10)
conn, addr = server.accept()
print(conn,addr,"hellohello")
while True:

    clientMessage =conn.recv(1024)
    
    #signal=['','','']
    """while(i<len(clientMessage)):
        if clientMessage[i]!=',':           
            signal[j]+=(clientMessage[i])
        else:
            j+=1
        i+=1"""
    #print('Client message is:',signal)
    
    print(clientMessage)
    a=json.loads(clientMessage)
    print(a)
    #serverMessage = 'I\'m here!'
    #conn.sendall(serverMessage.encode())
    
    conn.close()        