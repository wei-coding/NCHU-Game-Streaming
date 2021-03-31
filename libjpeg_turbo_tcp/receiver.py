import socket
import cv2
import turbojpeg

from protocol import *
import ctypes
import struct
import time
import traceback

MAX_DGRAM = 2 ** 16 - 64
jpeg = turbojpeg.TurboJPEG()
img_buffer = []
server_ip = '192.168.31.174'
port = 12345


def dump_buffer(s):
    """ Emptying buffer frame """
    while True:
        seg = s.recv(MAX_DGRAM)
        last = GSPHeader.from_buffer_copy(seg).last
        if last:
            print("finish emptying buffer")
            break


def main():
    """ Getting image udp frame &
    concate before decode and output image """
    seq = 0
    # Set up socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_ip, port))
    img = None
    dat = b''
    dump_buffer(s)
    while True:
        try:
            seg = s.recv(MAX_DGRAM)
        except KeyboardInterrupt:
            break
        last = struct.unpack("!?", seg[:struct.calcsize('?')])[0]
        print(last)
        payload = seg[struct.calcsize('?'):]
        if not last:
            dat += payload
        else:
            dat += payload
            try:
                img = jpeg.decode(dat)
            except Exception:
                traceback.print_exc()
            if img is not None:
                cv2.imshow('frame', img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            dat = b''
    # cap.release()
    cv2.destroyAllWindows()
    s.close()


if __name__ == "__main__":
    main()
