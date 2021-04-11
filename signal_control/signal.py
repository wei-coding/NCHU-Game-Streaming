import json
import socket
import threading
import time
import pynput.mouse, pynput.keyboard

def mmove(x, y):
    mouse.position = (x, y)
    print(mouse.position)


def mpress():
    mouse.press(Button.left)
    print('mouse has press')


def mrelease():
    mouse.release(Button.left)
    print('mouse has releae')


def mscroll(x, y):
    mouse.scroll(x, y)
    print('mouse scroll')


def kpress(a):
    # keyboard.press(a)
    keyboard_control.press(a)
    print('keyboard press', a)
    check_if_press['get'].append(a)
    p1 = Thread(target=press, args=(a, a))
    p1.start()


def krelease(a):
    keyboard_control.release(a)
    print('keyboard release', a)
    check_if_press['get'].remove(a)


class ServerService(threading.Thread):
    PORT = 8080

    def __init__(self):
        threading.Thread.__init__(self)
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('0.0.0.0', self.PORT))
        server.listen(10)
        self.conn, self.addr = server.accept()
        print('connect success')

    def run(self):
        while True:
            client_msg = self.conn.recv(1024)
            control = json.loads(client_msg)
            assert(control is dict)



def main():
    pass


if __name__ == '__main__':
    main()
