import d3dshot
import cv2
import time
import numpy as np
from PIL import Image
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 45]
d3dobj = d3dshot.create("numpy")
d3dobj.capture()
for _ in range(100):
    try:
        time.sleep(0.1)
        frame = d3dobj.get_latest_frame()
        while frame is None:
            frame = d3dobj.get_latest_frame()
        #img = Image.fromarray(frame)
        convert = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result, compress_img = cv2.imencode('.jpg', convert,encode_param)
        img = cv2.imdecode(compress_img, 1)
        cv2.imshow('frame',img)
        cv2.waitKey(1)
    except KeyboardInterrupt:
        d3dobj.stop()
        break
d3dobj.stop()