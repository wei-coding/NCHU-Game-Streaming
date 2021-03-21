import math
import socket
import threading
import time
import cv2
import d3dshot
import turbojpeg
from protocol import *
import ctypes
import struct


class FrameSegment(threading.Thread):
    """
    Object to break down image frame segment
    if the size of image exceed maximum datagram size
    """
    MAX_DGRAM = 2 ** 16 - 64
    MAX_IMAGE_DGRAM = MAX_DGRAM - 64  # extract 64 bytes in case UDP frame overflown
    JPEG = turbojpeg.TurboJPEG()

    def __init__(self, sock, addr, port):
        threading.Thread.__init__(self)
        self.s = sock
        self.scn = FastScreenshots()
        self.signal = True
        self.seq = -1
        self.frame = -1
        self.addr = addr
        self.port = port
        self.scn.start()

    def run(self):
        """
        Compress image and Break down
        into data segments
        """
        while self.signal:
            img = self.scn.get_latest_frame()[1]
            self.frame += 1
            if img is not None:
                dat = self.JPEG.encode(img, quality=50)
                size = len(dat)
                count = math.ceil(size / self.MAX_IMAGE_DGRAM)
                array_pos_start = 0
                while count:
                    self.seq += 1
                    array_pos_end = min(size, array_pos_start + self.MAX_IMAGE_DGRAM)
                    # now = ctypes.c_double(time.time())
                    '''send_data = bytes(GSPHeader(
                        self.seq,
                        self.frame,
                        True if count == 1 else False,
                        now,
                    )) + dat[array_pos_start:array_pos_end]'''
                    send_data = struct.pack("!?", True if count == 1 else False) + dat[array_pos_start:array_pos_end]
                    self.s.sendto(send_data, (self.addr, self.port))
                    array_pos_start = array_pos_end
                    count -= 1
                    # time.sleep(10)
            else:
                # print("Sleeping...")
                time.sleep(0.01)

    def stop(self):
        self.signal = False
        self.scn.stop()


class FastScreenshots:
    def __init__(self):
        self.d = d3dshot.create(capture_output='pil', frame_buffer_size=3)

    def start(self):
        self.d.capture()

    def get_latest_frame(self):
        try:
            r = cv2.cvtColor(self.d.get_latest_frame(), cv2.COLOR_BGR2RGB)
        except cv2.error:
            return False, None
        return True, self.d.get_latest_frame()

    def stop(self):
        self.d.stop()


class StartServer(threading.Thread):
    def __init__(self, port: int = 12345, parent=None):
        threading.Thread.__init__(self)
        self.s = None
        self.fs = None
        self.signal = True
        self.remote_host = None
        self.remote_port = None
        self.port = port
        self.parent = parent
        self.seq = 0

    def run(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.s.bind(('', self.port))

        """ implement three way handshake """
        # Wait for request
        while self.signal:
            recv, (self.remote_host, self.remote_port) = self.s.recvfrom(1024)
            recv = GSCPHeader.from_buffer_copy(recv)
            if recv.type == b'I' and recv.fn == b'R':
                break

        # Got request, send response
        packet = GSCPHeader(self.seq, b'I', b'A', time.time())
        self.seq += 1
        self.s.sendto(packet, (self.remote_host, self.remote_port))

        # Wait for another response from client
        while self.signal:
            recv, (self.remote_host, self.remote_port) = self.s.recvfrom(1024)
            recv = GSCPHeader.from_buffer_copy(recv)
            if recv.type == b'I' and recv.fn == b'A':
                break
        """ end of three way handshake """
        self.fs = FrameSegment(self.s, self.remote_host, self.remote_port)
        self.fs.start()
        self.parent.start_sig.emit()
        self.parent.logs.appendPlainText('server is running.')
        while self.signal:
            time.sleep(2)
        self.parent.logs.appendPlainText('server is closing.')
        self.parent.stop_sig.emit()
        self.fs.stop()
        self.s.close()

    def stop(self):
        self.signal = False

    def get_addr(self):
        return self.remote_host


def main():
    """ Top level main function """
    # Set up UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    port = 12345
    s.bind(('', port))

    revcData, (remoteHost, remotePort) = s.recvfrom(1024)
    while revcData != b'R':
        revcData, (remoteHost, remotePort) = s.recvfrom(1024)
    s.sendto(b'A', (remoteHost, remotePort))
    revcData, (remoteHost, remotePort) = s.recvfrom(1024)
    while revcData != b'A':
        revcData, (remoteHost, remotePort) = s.recvfrom(1024)
    fs = FrameSegment(s, remoteHost, remotePort)
    fs.start()
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        fs.stop()
    s.close()


if __name__ == "__main__":
    main()
