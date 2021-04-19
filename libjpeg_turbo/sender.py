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


class FrameSegment(threading.Thread):
    """
    Object to break down image frame segment
    if the size of image exceed maximum datagram size
    """
    MAX_DGRAM = 2 ** 16
    MAX_IMAGE_DGRAM = MAX_DGRAM >> 6  # extract 64 bytes in case UDP frame overflown
    JPEG = turbojpeg.TurboJPEG()

    def __init__(self, sock, addr, port):
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
                dat = self.JPEG.encode(img, quality=75)

                size = len(dat)
                count = math.ceil(size / self.MAX_IMAGE_DGRAM)
                array_pos_start = 0
                while count:
                    self.seq += 1
                    array_pos_end = min(size, array_pos_start + self.MAX_IMAGE_DGRAM)
                    header = GSPHeader(self.seq, GSP.DATA, GSP.NONE, 0, True if count == 1 else False, time.time())
                    send_data = bytes(header) + dat[array_pos_start:array_pos_end]
                    self.s.sendto(send_data, (self.addr, self.port))
                    array_pos_start = array_pos_end
                    count -= 1
            else:
                time.sleep(0.01)

    def stop(self):
        self.signal = False
        self.scn.stop()
        send_data = GSPHeader(0, GSP.CONTROL, GSP.STOP, 0, True, time.time())
        self.s.sendto(send_data, (self.addr, self.port))


class BufferClearService(threading.Thread):
    def __init__(self, buffer):
        threading.Thread.__init__(self)
        self.buffer = buffer
        self.sig = False

    def run(self):
        while not self.sig:
            time.sleep(1)
            self.buffer.clear()

    def stop(self):
        self.sig = not self.sig


class FastScreenshots:
    def __init__(self):
        self.d = d3dshot.create(capture_output='numpy', frame_buffer_size=90)
        self.clear_service = BufferClearService(self.d.frame_buffer)

    def start(self):
        self.d.capture(target_fps=60)
        self.clear_service.start()

    def get_latest_frame(self):
        frame = self.d.get_latest_frame()
        if frame is not None:
            return True, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        else:
            return False, None

    def stop(self):
        self.d.stop()
        self.clear_service.stop()


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

    def run(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind(('', self.port))
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        """ implement three way handshake """
        # Wait for request
        while self.signal:
            recv, (self.remote_host, self.remote_port) = self.s.recvfrom(1024)
            recv = GSPHeader.from_buffer_copy(recv)
            if recv.type == 0 and recv.fn == 0:
                break

        # Got request, send response
        packet = GSPHeader(self.seq, 0, 1, 0, False, time.time())
        self.seq += 1
        self.s.sendto(packet, (self.remote_host, self.remote_port))

        # Wait for another response from client
        while self.signal:
            recv, (self.remote_host, self.remote_port) = self.s.recvfrom(1024)
            recv = GSPHeader.from_buffer_copy(recv)
            if recv.type == 0 and recv.fn == 2:
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
    pass


if __name__ == "__main__":
    main()
