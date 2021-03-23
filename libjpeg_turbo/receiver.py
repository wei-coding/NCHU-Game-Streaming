import socket
import cv2
import turbojpeg

from protocol import *
import ctypes
import struct
import time
import traceback
from measurement import Measure

MAX_DGRAM = 2 ** 16 - 64
jpeg = turbojpeg.TurboJPEG()
img_buffer = []
server_ip = '192.168.31.174'
port = 12345


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
    seq = 0
    # Set up socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    measure1 = Measure("decode time =")
    measure2 = Measure("show time =")
    measure1.start()
    measure2.start()

    """ implement three way handshake """
    while True:
        # send request message
        packet = GSCPHeader(seq, b'I', b'R', time.time())
        s.sendto(packet, (server_ip, port))
        # wait for ACK
        recv, addr = s.recvfrom(MAX_DGRAM)
        recv = GSCPHeader.from_buffer_copy(recv)
        if recv.type == b'I' and recv.fn == b'A':
            break
    # send ACK to server
    packet = GSCPHeader(seq, b'I', b'A', time.time())
    s.sendto(packet, (server_ip, port))
    print('handshake to {}:{} success. start transmittimg...'.format(addr[0], addr[1]))
    """ end of three way handshake """
    previous_img = None
    img = None
    dat = b''
    # dump_buffer(s)
    while True:
        try:
            seg, addr = s.recvfrom(MAX_DGRAM)
        except KeyboardInterrupt:
            break
        # print('Got packet.')
        last = struct.unpack("!?", seg[:struct.calcsize('!?')])[0]
        # print(last)
        payload = seg[struct.calcsize('!?'):]
        # header = GSPHeader.from_buffer_copy(seg)
        # last = header.last
        # payload = seg[sizeof(GSPHeader):]
        # print(seq,last,timestamp,payload)
        # print('timestamp = {}'.format(header.timestamp))
        dat += payload
        if last:
            dat += payload
            # img = cv2.imdecode(np.fromstring(dat, dtype=np.uint8), 1)
            try:
                now = time.time()
                img = jpeg.decode(dat)
                decode_time = time.time() - now
                measure1.add(decode_time)
            except Exception:
                traceback.print_exc()
            if img is not None:
                now = time.time()
                cv2.imshow('frame', img)
                im_time = time.time() - now
                measure2.add(im_time)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            dat = b''
    # cap.release()
    cv2.destroyAllWindows()
    s.close()


if __name__ == "__main__":
    main()
