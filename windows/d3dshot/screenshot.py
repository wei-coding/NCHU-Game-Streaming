import win32gui
import win32ui
import win32con
import ctypes
import ctypes.wintypes
from  ctypes import *
from PIL import Image
import time
import d3dshot

count = 0

def get_window_rect(hwnd):
    try:
        f = ctypes.windll.dwmapi.DwmGetWindowAttribute
    except WindowsError:
        f = None
    if f:
        rect = ctypes.wintypes.RECT()
        DWMWA_EXTENDED_FRAME_BOUNDS = 9
        f(ctypes.wintypes.HWND(hwnd),
          ctypes.wintypes.DWORD(DWMWA_EXTENDED_FRAME_BOUNDS),
          ctypes.byref(rect),
          ctypes.sizeof(rect)
          )
        return rect.left, rect.top, rect.right, rect.bottom

def background_screenshot(hwnd):
    global count

    left, top, right, bot = get_window_rect(hwnd)
    w = right - left
    h = bot - top

    wDC = win32gui.GetWindowDC(hwnd)
    dcObj=win32ui.CreateDCFromHandle(wDC)
    cDC=dcObj.CreateCompatibleDC()

    dataBitMap = win32ui.CreateBitmap()
    dataBitMap.CreateCompatibleBitmap(dcObj, w, h)

    cDC.SelectObject(dataBitMap)

    r = windll.user32.PrintWindow(hwnd, cDC.GetSafeHdc(), 0)

    bmpinfo = dataBitMap.GetInfo()
    bmpstr = dataBitMap.GetBitmapBits(True)

    im = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1)

    win32gui.DeleteObject(dataBitMap.GetHandle())
    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    '''
    if r == 1:
        im.save('sc%d.png'%(count))
        count += 1
    '''
    return im
class gpu_screenshots():
    def __init__(self):
        self.d = d3dshot.create(capture_output='numpy', frame_buffer_size=5)
    def shot(self):
        self.d.capture()
    def get_frames(self):
        return self.d.get_latest_frame()
    def stop(self):
        self.d.stop()

if __name__ == '__main__':
    hwnd = win32gui.FindWindow(None, '控制台')
    for _ in range(20):
        background_screenshot(hwnd)
        time.sleep(0.5)