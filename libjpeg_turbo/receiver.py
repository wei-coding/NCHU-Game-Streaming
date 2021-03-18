import socket
import cv2
import turbojpeg

from protocol import *

MAX_DGRAM = 2 ** 16
datagram_builder = DatagramBuilder('!I?')
jpeg = turbojpeg.TurboJPEG()
img_buffer = []
server_ip = '192.168.43.2'
port = 12345


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
    recv = None
    addr = None
    while recv != b'A':
        s.sendto(b'R', (server_ip, port))
        recv, addr = s.recvfrom(1024)
    s.sendto(b'A', (server_ip, port))
    previous_img = None
    img = None
    dat = b''
    dump_buffer(s)
    now_seq = 0
    while True:
        seg, addr = s.recvfrom(MAX_DGRAM)
        # print('Got packet.')
        (seq, last) = datagram_builder.unpack(seg)
        payload = seg[datagram_builder.packsize:]
        # print(seq,last,timestamp,payload)
        if not last:
            dat += payload
        else:
            dat += payload
            # img = cv2.imdecode(np.fromstring(dat, dtype=np.uint8), 1)
            try:
                img = jpeg.decode(dat)
            except Exception:
                pass
            if img is not None:
                cv2.imshow('frame', img)
                previous_img = img
            else:
                cv2.imshow('frame', previous_img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            dat = b''

    # cap.release()
    cv2.destroyAllWindows()
    s.close()


if __name__ == "__main__":
    main()
