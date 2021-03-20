import socket
import cv2
import turbojpeg

from protocol import *
import ctypes
import time
import struct
import traceback

MAX_DGRAM = 2 ** 16
jpeg = turbojpeg.TurboJPEG()
img_buffer = []
server_ip = '192.168.31.174'
port = 12345


def dump_buffer(s):
    """ Emptying buffer frame """
    while True:
        seg, addr = s.recvfrom(MAX_DGRAM)
        data = seg[:struct.calcsize('!?')]
        if data:
            print("finish emptying buffer")
            break


def main():
    """ Getting image udp frame &
    concate before decode and output image """
    seq = 0
    # Set up socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        dat = create_datagram(seq=seq, frm=0, last=True, fn=0, timestamp=time.time_ns(), parity=0, payload=b'R')
        seq += 1
        s.sendto(dat, (server_ip, port))
        recv, addr = s.recvfrom(1024)
        header = DatagramHeader.from_buffer_copy(recv)
        if header.fn == 0 and get_payload(recv) == b'A':
            break
    dat = create_datagram(seq=seq, frm=0, last=True, fn=0, timestamp=time.time_ns(), parity=0, payload=b'A')
    seq += 1
    s.sendto(dat, (server_ip, port))
    previous_img = None
    img = None
    dat = b''
    dump_buffer(s)
    while True:
        seg, addr = s.recvfrom(MAX_DGRAM)
        payload = seg[struct.calcsize('!?'):]
        dat += payload
        if struct.unpack('!?', seg[:struct.calcsize('!?')]):
            try:
                img = jpeg.decode(dat)
            except Exception:
                traceback.print_exc()
            if img is not None:
                cv2.imshow('frame', img)
                previous_img = img
            elif previous_img is not None:
                cv2.imshow('frame', previous_img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            dat = b''

    # cap.release()
    cv2.destroyAllWindows()
    s.close()


if __name__ == "__main__":
    main()
