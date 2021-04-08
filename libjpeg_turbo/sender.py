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
from numba import jit


@jit
def encode_jpeg(turbojpeg_inst, frame):
    return turbojpeg_inst.encode(frame, quality=50)


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
            sucess, img = self.scn.get_latest_frame()
            self.frame += 1
            if img is not None:
                dat = encode_jpeg(self.JPEG, img)
                size = len(dat)
                count = math.ceil(size / self.MAX_IMAGE_DGRAM)
                array_pos_start = 0
                now = time.time()
                while count:
                    self.seq += 1
                    array_pos_end = min(size, array_pos_start + self.MAX_IMAGE_DGRAM)
                    send_data = struct.pack("!??", True if count == 1 else False, False) + dat[array_pos_start:array_pos_end]
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
        send_data = struct.pack("!??", False, True)
        self.s.sendto(send_data, (self.addr, self.port))


class FastScreenshots:
    def __init__(self):
        self.d = d3dshot.create(capture_output='numpy', frame_buffer_size=15)

    def start(self):
        self.d.capture(target_fps=45)

    def get_latest_frame(self):
        frame = self.d.get_latest_frame()
        if frame is not None:
            return True, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        else:
            return False, None

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
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind(('', self.port))
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

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
