import d3dshot
import cv2
import win32gui
import win32ui
from ctypes import windll
from PIL import Image
import threading


class FastScreenshots:
    def __init__(self):
        self.d = d3dshot.create(capture_output='numpy', frame_buffer_size=180)

    def start(self):
        self.d.capture(target_fps=60)

    def get_latest_frame(self):
        r = self.d.get_latest_frame()
        r = cv2.cvtColor(r, cv2.COLOR_BGR2RGB)
        return True if r is not None else False, r

    def stop(self):
        self.d.stop()


class win32shot(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.hwnd = win32gui.FindWindow(None, 'hw1')
        left, top, right, bot = win32gui.GetWindowRect(self.hwnd)
        self.w = right - left
        self.h = bot - top
        self.hwndDC = win32gui.GetWindowDC(self.hwnd)
        self.mfcDC = win32ui.CreateDCFromHandle(self.hwndDC)
        self.saveDC = self.mfcDC.CreateCompatibleDC()
        self.saveBitMap = win32ui.CreateBitmap()

        self.buffer = []

    def run(self):
        while True:
            self.saveBitMap.CreateCompatibleBitmap(self.mfcDC, self.w, self.h)

            self.saveDC.SelectObject(self.saveBitMap)

            # Change the line below depending on whether you want the whole window
            # or just the client area.
            # result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 1)
            result = windll.user32.PrintWindow(self.hwnd, self.saveDC.GetSafeHdc(), 0)
            print(result)

            bmpinfo = self.saveBitMap.GetInfo()
            bmpstr = self.saveBitMap.GetBitmapBits(True)
            im = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1)

            win32gui.DeleteObject(self.saveBitMap.GetHandle())
            self.saveDC.DeleteDC()
            self.mfcDC.DeleteDC()
            # win32gui.ReleaseDC(hwnd, hwndDC)
            if result == 1:
                # PrintWindow Succeeded
                self.buffer.append(im)

    @property
    def get_latest_frame(self):
        return self.buffer.pop(0)
