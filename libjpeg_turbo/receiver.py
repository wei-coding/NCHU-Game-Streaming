import socket
import cv2
import turbojpeg
from protocol import *
from ctypes import *
import time
import traceback
import threading
import struct
import numpy as np
from concurrent.futures import ThreadPoolExecutor


MAX_DGRAM = GSP.PACKET_SIZE


class Receiver(threading.Thread):
    def __init__(self, server_ip, port, parent=None):
        threading.Thread.__init__(self)
        self.parent = parent
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.stop = False
        self.seq = 0
        self.server_ip = server_ip
        self.port = port
        self.jpeg = turbojpeg.TurboJPEG()
        self.geo = None
        self.show_img = ShowImage(10)

    def run(self):
        """ implement three way handshake """
        print('trying connect 0')
        while True:
            # send request message
            packet = GSPHeader(self.seq, GSP.CONTROL, GSP.RQST_CONN, 0, 0, time.time())
            self.s.sendto(packet, (self.server_ip, self.port))
            # wait for ACK
            print('trying connect 1')
            recv, addr = self.s.recvfrom(MAX_DGRAM)
            recv = GSPHeader.from_buffer_copy(recv)
            if recv.type == 0 and recv.fn == 1:
                break
        # send ACK to server
        print('trying connect 2')
        packet = GSPHeader(self.seq, GSP.CONTROL, GSP.ACK, 0, 0, time.time())
        self.s.sendto(packet, (self.server_ip, self.port))
        if self.parent:
            self.parent.logs.appendHtml('handshake to {}:{} success. start transmittimg...'.format(addr[0], addr[1]))
        else:
            print('handshake to {}:{} success. start transmittimg...'.format(addr[0], addr[1]))
        """ end of three way handshake """
        """ res """
        while True:
            recv, addr = self.s.recvfrom(GSP.PACKET_SIZE)
            header = GSPHeader.from_buffer_copy(recv[:sizeof(GSPHeader)])
            if header.type == GSP.RES:
                self.geo = struct.unpack('II', recv[sizeof(GSPHeader):])
                print(self.geo)
                break
        packet = GSPHeader(type=GSP.RES_ACK)
        self.s.sendto(string_at(addressof(packet), sizeof(packet)), (self.server_ip, self.port))
        """ end of res """
        img = None
        dat = b''
        dump_buffer(self.s)
        self.show_img.start()
        while not self.stop:
            try:
                seg, addr = self.s.recvfrom(GSP.PACKET_SIZE)
            except KeyboardInterrupt:
                break
            header = GSPHeader()
            # print('sizeof(GSPHeader) = {}'.format(sizeof(GSPHeader)))
            memmove(addressof(header), seg[:sizeof(GSPHeader)], sizeof(GSPHeader))
            self.stop = (header.fn == GSP.STOP)
            dat += seg[sizeof(GSPHeader):]
            if header.last == 1:
                try:
                    img = self.jpeg.decode(dat)
                    if img is not None:
                        self.show_img.push_img(img)
                except Exception:
                    traceback.print_exc()
                dat = b''
        if self.parent:
            self.parent.logs.appendHtml("stop connecttion")
            self.parent.signal_service.kill()
        else:
            print('Server has stopped.')
        self.show_img.kill()
        self.s.close()

    def kill(self):
        self.stop = True
        print('killed service')


class ShowImage(threading.Thread):
    def __init__(self, size=100):
        threading.Thread.__init__(self)
        self.show = True
        self.buf = np.zeros(size, dtype=bytearray)
        self.size = size
        self.front = -1
        self.rear = -1
        self.last_frame = None

    def run(self):
        while self.show:
            try:
                cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
                # cv2.setWindowProperty('frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                # cv2.setWindowProperty('frame', cv2.WND_PROP_OPENGL, 1)
                cv2.imshow('frame', self.pop_img())
                cv2.waitKey(1)
            except:
                time.sleep(0.01)

    def push_img(self, img):
        self.rear = (self.rear + 1) % self.size
        if self.rear == self.front:
            return
        self.buf[self.rear] = img

    def pop_img(self):
        if self.front == self.rear:
            return self.last_frame
        self.front = (self.front + 1) % self.size
        self.last_frame = self.buf[self.front]
        return self.last_frame

    def kill(self):
        self.show = False
        cv2.destroyAllWindows()


def dump_buffer(s):
    """ Emptying buffer frame """
    while True:
        seg, addr = s.recvfrom(MAX_DGRAM)
        last = GSPHeader.from_buffer_copy(seg).last
        if last:
            print("finish emptying buffer")
            break


def main():
    """ Getting image udp frame &
    concate before decode and output image """
    server_ip = '192.168.0.101'
    port = 12345
    receiver = Receiver(server_ip, port)
    receiver.start()
    receiver.join()


if __name__ == "__main__":
    main()
