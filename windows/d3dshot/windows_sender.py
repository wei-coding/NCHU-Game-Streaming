import cv2
import socket
import time
import numpy as np
import screenshot
import d3dshot
from FpsMeter import *
from FrameSegment import *
from PIL import Image

def main():
    """ Top level main function """
    # Set up UDP socket
    conti = True
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    port = 12345
    fs = FrameSegment(s, port)
    fs.start()
    fm = FpsMeter(interval=5)
    fm.start()
    ss = screenshot.gpu_screenshots()
    ss.shot()
    try:
        while conti:
            img = ss.get_frames()
            while img is None:
                img = ss.get_frames()
            img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
            fs.add_buffer(img)
            fm.inc_count()
    except KeyboardInterrupt:
        conti = False
        ss.stop()
        fm.stop()
        fs.stop()
        
    s.close()
if __name__ == "__main__":
    main()
