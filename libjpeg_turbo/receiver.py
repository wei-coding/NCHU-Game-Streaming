import socket
import cv2
import turbojpeg
from protocol import *
import ctypes
import time
import traceback
import threading


MAX_DGRAM = 2 ** 16


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
        img = None
        dat = b''
        # dump_buffer(self.s)
        while not self.stop:
            cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
            # cv2.setWindowProperty('frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            try:
                seg, addr = self.s.recvfrom(MAX_DGRAM)
            except KeyboardInterrupt:
                break
            header = GSPHeader.from_buffer_copy(seg[:ctypes.sizeof(GSPHeader)])
            last = (header.last == 1)
            seq = header.seq
            '''print(f'seq: {seq}, self.seq: {self.seq}')
            if seq != self.seq + 1:
                self.seq += 1
                data = GSPHeader(seq=self.seq, type=GSP.CONTROL, fn=GSP.CONGESTION)
                self.s.sendto(data, (self.server_ip, self.port))
                continue'''
            self.stop = (header.fn == GSP.STOP)
            payload = seg[ctypes.sizeof(GSPHeader):]
            dat += payload
            if last:
                dat += payload

                try:
                    img = self.jpeg.decode(dat)
                except Exception:
                    traceback.print_exc()
                if img is not None:

                    cv2.imshow('frame', img)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                dat = b''
        if self.parent:
            self.parent.logs.appendHtml("stop connecttion")
            self.parent.signal_service.kill()
        else:
            print('Server has stopped.')
        cv2.destroyAllWindows()
        self.s.close()

    def kill(self):
        self.stop = True
        print('killed service')


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
    server_ip = '192.168.31.174'
    port = 12345
    receiver = Receiver(server_ip, port)
    receiver.start()
    receiver.join()


if __name__ == "__main__":
    main()
