import socket
import cv2
import turbojpeg
from protocol import *
import struct
import time
import traceback
import threading


MAX_DGRAM = 2 ** 16 - 64


class Receiver(threading.Thread):
    def __init__(self, server_ip, port):
        threading.Thread.__init__(self)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.stop = False
        self.seq = 0
        self.server_ip = server_ip
        self.port = port
        self.jpeg = turbojpeg.TurboJPEG()
        dump_buffer(self.s)

    def run(self):

        """ implement three way handshake """
        while True:
            # send request message
            packet = GSCPHeader(self.seq, b'I', b'R', time.time())
            self.s.sendto(packet, (self.server_ip, self.port))
            # wait for ACK
            recv, addr = self.s.recvfrom(MAX_DGRAM)
            recv = GSCPHeader.from_buffer_copy(recv)
            if recv.type == b'I' and recv.fn == b'A':
                break
        # send ACK to server
        packet = GSCPHeader(self.seq, b'I', b'A', time.time())
        self.s.sendto(packet, (self.server_ip, self.port))
        print('handshake to {}:{} success. start transmittimg...'.format(addr[0], addr[1]))
        """ end of three way handshake """
        img = None
        dat = b''
        dump_buffer(self.s)
        while not self.stop:
            try:
                seg, addr = self.s.recvfrom(MAX_DGRAM)
            except KeyboardInterrupt:
                break
            header = struct.unpack("!??", seg[:struct.calcsize('!??')])
            last = header[0]
            self.stop = header[1]
            payload = seg[struct.calcsize('!??'):]
            dat += payload
            if last:
                dat += payload
                try:
                    img = self.jpeg.decode(img)
                except Exception:
                    traceback.print_exc()
                if img is not None:
                    cv2.imshow('frame', img)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                dat = b''
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
        # last = seg[:struct.calcsize('!?')]
        # print(last)
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
