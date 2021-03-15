from turbojpeg import TJPF_BGR
import turbojpeg as JPEG
import cv2
import screenshot as sc
import numpy as np

jpeg = JPEG.TurboJPEG()
scn = sc.gpu_screenshots()

scn.start()
shot = scn.get_latest_frame()[1]
while shot is None:
    shot = scn.get_latest_frame()[1]
scn.stop()

shot = np.asarray(shot,dtype=np.uint8)
#print(shot)
jpg_file = jpeg.encode(shot)
with open('output1.jpg','wb') as f:
    f.write(jpg_file)
jpg_file = cv2.imencode('.jpg',shot)[1]
with open('output2.jpg','wb') as f:
    f.write(jpg_file)

with open('output1.jpg','rb') as f:
    jpg_file = jpeg.decode(f.read())
    jpg_file = jpeg.encode(jpg_file)
    with open('output3.jpg','wb') as fw:
        fw.write(jpg_file)
