#!/usr/bin/env python

from __future__ import division

import socket
import threading

import cv2
import turbojpeg

from Protocol import *

MAX_DGRAM = 2 ** 16
datagram_builder = DatagramBuilder('!I?')
jpeg = turbojpeg.TurboJPEG()
img_buffer = []


def dump_buffer(s):
    """ Emptying buffer frame """
    while True:
        seg, addr = s.recvfrom(MAX_DGRAM)
        (seq, last) = datagram_builder.unpack(seg)
        # print(last)
        if last:
            print("finish emptying buffer")
            break


def main():
    """ Getting image udp frame &
    concate before decode and output image """

    # Set up socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('127.0.0.1', 12345))
    dat = b''
    dump_buffer(s)
    now_seq = 0
    while True:
        seg, addr = s.recvfrom(MAX_DGRAM)
        (seq, last) = datagram_builder.unpack(seg)
        payload = seg[datagram_builder.packsize:]
        # print(seq,last,timestamp,payload)
        if not last:
            dat += payload
        else:
            dat += payload
            # img = cv2.imdecode(np.fromstring(dat, dtype=np.uint8), 1)
            img = jpeg.decode(dat)
            if img is not None:
                cv2.imshow('frame', img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            dat = b''

    # cap.release()
    cv2.destroyAllWindows()
    s.close()


if __name__ == "__main__":
    main_thread = threading.Thread(target=main)
    main_thread.start()
