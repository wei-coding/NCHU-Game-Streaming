#!/usr/bin/env python

from __future__ import division
import cv2
import numpy as np
import socket
import struct
import math
import time
import threading
import background
from PIL import Image
import win32gui
import win32ui
import win32con
import ctypes
import ctypes.wintypes
from  ctypes import *
import time
import FrameSegment

def main(hwnd):
    """ Top level main function """
    # Set up UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    port = 12345
    fs = FrameSegment(s, port)
    fs.start()
    while True:
        try:
            img = background.background_screenshot(hwnd)
        except:
            break
        img = cv2.cvtColor(np.asarray(img),cv2.COLOR_RGB2BGR)
        fs.add_buffer(img)
    s.close()


if __name__ == "__main__":
    main(win32gui.FindWindow(None, '控制台'))
