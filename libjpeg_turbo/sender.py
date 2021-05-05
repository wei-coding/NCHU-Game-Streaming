import math
import socket
import threading
import time
import cv2
import d3dshot
import turbojpeg
import traceback
from protocol import *
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
import struct
import select


class FrameSegment(threading.Thread):
    """
    Object to break down image frame segment
    if the size of image exceed maximum datagram size
    """
    MAX_DGRAM = GSP.PACKET_SIZE
    MAX_IMAGE_DGRAM = MAX_DGRAM - sizeof(GSPHeader)
    JPEG = turbojpeg.TurboJPEG()
    QUALITY = 50

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
        self.quality_checker = QualityChecker(self)
        self.scn.start()

    def run(self):
        """
        Compress image and Break down
        into data segments
        """
        self.quality_checker.start()
        while self.signal:
            sucess, img = self.scn.get_latest_frame()
            self.frame += 1
            self.frame %= 256
            if img is not None:
                dat = self.JPEG.encode(img, quality=self.QUALITY)
                size = len(dat)
                # print(size)
                count = math.ceil(size / self.MAX_IMAGE_DGRAM)
                array_pos_start = 0
                # print(count)
                while count:
                    self.seq += 1
                    array_pos_end = min(size, array_pos_start + self.MAX_IMAGE_DGRAM)
                    header = GSPHeader(self.seq, GSP.DATA, GSP.NONE, 0, count, time.time())
                    send_data = bytes(header) + dat[array_pos_start:array_pos_end]
                    self.s.sendto(send_data, (self.addr, self.port))
                    array_pos_start = array_pos_end
                    count -= 1
            else:
                time.sleep(0.01)
            try:
                print('trying get packet')
                packet = self.s.recvfrom(GSP.PACKET_SIZE)
                packet = GSPHeader.from_buffer_copy(packet)
                if packet.type == GSP.CONTROL:
                    if packet.fn == GSP.CONGESTION:
                        print('got congestion, decrease quality')
                        self.QUALITY -= 2
                    elif packet.fn == GSP.RECOVER:
                        print('got recover, increase quality')
                        self.QUALITY += 1
            except:
                traceback.print_exc()

    def stop(self):
        self.signal = False
        self.scn.stop()
        send_data = GSPHeader(0, GSP.CONTROL, GSP.STOP, 0, 1, time.time())
        self.s.sendto(send_data, (self.addr, self.port))


class QualityChecker(threading.Thread):
    def __init__(self, parent: FrameSegment):
        threading.Thread.__init__(self)
        self.parent = parent

    def run(self):
        while True:
            ready_r, _, _ = select.select([self.parent.s], [], [], 1)
            for sck in ready_r:
                sck.setblocking(0)
                packet = sck.recv(GSP.PACKET_SIZE)
                self.handle_recv(packet)

    def handle_recv(self, packet):
        packet = GSPHeader.from_buffer_copy(packet)
        if packet.type == GSP.CONTROL:
            if packet.fn == GSP.CONGESTION:
                # print('got congestion, decrease quality')
                self.parent.QUALITY -= 2
            elif packet.fn == GSP.RECOVER:
                # print('got recover, increase quality')
                self.parent.QUALITY += 1
        if self.parent.QUALITY < 20:
            self.parent.QUALITY = 20
        elif self.parent.QUALITY > 50:
            self.parent.QUALITY = 50



class BufferClearService(threading.Thread):
    def __init__(self, buffer):
        threading.Thread.__init__(self)
        self.buffer = buffer
        self.sig = False

    def run(self):
        while not self.sig:
            time.sleep(0.5)
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
        packet = GSPHeader(self.seq, 0, 1, 0, 0, time.time())
        self.seq += 1
        self.s.sendto(packet, (self.remote_host, self.remote_port))

        # Wait for another response from client
        while self.signal:
            recv, (self.remote_host, self.remote_port) = self.s.recvfrom(1024)
            recv = GSPHeader.from_buffer_copy(recv)
            if recv.type == 0 and recv.fn == 2:
                break
        """ end of three way handshake """
        """ send screen resolution """
        geo = QtWidgets.QApplication.desktop().screenGeometry()
        packet = bytes(GSPHeader(type=GSP.RES)) + struct.pack('II', geo.width(), geo.height())
        self.s.sendto(packet, (self.remote_host, self.remote_port))
        print("finish sending")
        """ screen resolution """
        while self.signal:
            recv, (self.remote_host, self.remote_port) = self.s.recvfrom(1024)
            recv = GSPHeader.from_buffer_copy(recv)
            if recv.type == GSP.RES_ACK:
                break
        """ end of resolution check """
        self.s.setblocking(False)
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
