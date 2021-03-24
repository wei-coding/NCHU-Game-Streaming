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

    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.conn = conn
        self.scn = FastScreenshots()
        self.signal = True
        self.seq = -1
        self.frame = -1
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
                dat = self.JPEG.encode(img, quality=50)
                size = len(dat)
                count = math.ceil(size / self.MAX_IMAGE_DGRAM)
                array_pos_start = 0
                now = time.time()
                while count:
                    self.seq += 1
                    array_pos_end = min(size, array_pos_start + self.MAX_IMAGE_DGRAM)
                    send_data = struct.pack("!?", True if count == 1 else False) + dat[array_pos_start:array_pos_end]
                    self.conn.send(send_data)
                    array_pos_start = array_pos_end
                    count -= 1
                    # time.sleep(10)
                send_time = time.time() - now
                print('send time=', send_time)
            else:
                # print("Sleeping...")
                time.sleep(0.01)

    def stop(self):
        self.signal = False
        self.scn.stop()


class FastScreenshots:
    def __init__(self):
        self.d = d3dshot.create(capture_output='numpy', frame_buffer_size=3)

    def start(self):
        self.d.capture(target_fps=30)

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
        self.port = port
        self.parent = parent
        self.seq = 0

    def run(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('', self.port))
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.listen(5)
        while True:
            print('waiting for connection')
            conn, addr = self.s.accept()
            if addr is not None:
                print(f'{conn} is connected')
                self.remote_host = addr[0]
                break
        self.fs = FrameSegment(conn)
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
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 12345
    s.bind(('', port))
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.listen(5)
    fs = FrameSegment(s)
    fs.start()
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        fs.stop()
    s.close()


if __name__ == "__main__":
    main()
