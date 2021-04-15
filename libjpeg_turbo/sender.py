import math
import socket
import threading
import time
import cv2
import d3dshot
import turbojpeg
from protocol import *
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
import numpy as np


def encode_jpeg(turbojpeg_inst, frame):
    return turbojpeg_inst.encode(frame, quality=50)


class FrameSegment(threading.Thread):
    """
    Object to break down image frame segment
    if the size of image exceed maximum datagram size
    """
    MAX_DGRAM = 2 ** 16
    MAX_IMAGE_DGRAM = MAX_DGRAM - 64  # extract 64 bytes in case UDP frame overflown
    JPEG = turbojpeg.TurboJPEG()

    def __init__(self, sock, addr, port, conn):
        threading.Thread.__init__(self)
        self.s = sock
        self.scn = FastScreenshots()
        # self.scn = QtScreenShot()
        self.signal = True
        self.seq = -1
        self.frame = -1
        self.addr = addr
        self.port = port
        self.scn.start()
        self.conn = conn

    def run(self):
        """
        Compress image and Break down
        into data segments
        """
        while self.signal:
            sucess, img = self.scn.get_latest_frame()
            self.frame += 1
            self.frame %= 256
            if img is not None:
                dat = encode_jpeg(self.JPEG, img)

                # print(len(dat))
                size = len(dat)
                count = math.ceil(size / self.MAX_IMAGE_DGRAM)
                array_pos_start = 0
                while count:
                    self.seq += 1
                    array_pos_end = min(size, array_pos_start + self.MAX_IMAGE_DGRAM)
                    header = GSPHeader(self.seq, GSP.DATA, GSP.NONE, 0, True if count == 1 else False, time.time())
                    send_data = bytes(header) + dat[array_pos_start:array_pos_end]
                    self.conn.send(send_data)
                    array_pos_start = array_pos_end
                    count -= 1
                    # time.sleep(10)
            else:
                # print("Sleeping...")
                time.sleep(0.01)

    def stop(self):
        self.signal = False
        self.scn.stop()
        send_data = GSPHeader(0, GSP.CONTROL, GSP.STOP, 0, True, time.time())
        self.conn.send(send_data)


class FastScreenshots:
    def __init__(self):
        self.d = d3dshot.create(capture_output='numpy', frame_buffer_size=90)

    def start(self):
        self.d.capture(target_fps=60)

    def get_latest_frame(self):
        frame = self.d.get_latest_frame()
        if frame is not None:
            return True, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        else:
            return False, None

    def stop(self):
        self.d.stop()


class QtScreenShot(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.sig = False
        self.screen = QtWidgets.QApplication.primaryScreen()
        self._array = QByteArray()
        self._buffer = QBuffer(self._array)
        self._buffer.open(QIODevice.WriteOnly)

    def run(self):
        while not self.sig:
            frame = self.screen.grabWindow(QtWidgets.QApplication.desktop().winId())
            frame = frame.scaled(1280, 720, transformMode=Qt.SmoothTransformation)
            frame.save(self._buffer, 'jpeg', quality=80)

    def get_latest_frame(self):
        pixData = self._buffer.data()
        self._array.clear()
        self._buffer.close()
        return False if pixData is None else True, pixData

    def stop(self):
        self.sig = not self.sig


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
        self.conn = None
        self.client_addr = None

    def run(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('', self.port))
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.listen(5)
        self.conn, self.client_addr = self.s.accept()
        """ implement three way handshake """
        # Wait for request
        while self.signal:
            recv = self.conn.recv(1024)
            recv = GSPHeader.from_buffer_copy(recv)
            if recv.type == 0 and recv.fn == 0:
                break

        # Got request, send response
        packet = GSPHeader(self.seq, 0, 1, 0, False, time.time())
        self.seq += 1
        self.conn.send(packet)

        # Wait for another response from client
        while self.signal:
            recv = self.conn.recv(1024)
            recv = GSPHeader.from_buffer_copy(recv)
            if recv.type == 0 and recv.fn == 2:
                break
        """ end of three way handshake """
        self.fs = FrameSegment(self.s, self.remote_host, self.remote_port, self.conn)
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
    pass


if __name__ == "__main__":
    main()
