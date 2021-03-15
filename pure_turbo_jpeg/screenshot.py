import d3dshot
import cv2
class gpu_screenshots():
    def __init__(self):
        self.d = d3dshot.create(capture_output='numpy', frame_buffer_size=5)
    def start(self):
        self.d.capture()
    def get_latest_frame(self):
        r = self.d.get_latest_frame()
        r = cv2.cvtColor(r, cv2.COLOR_BGR2RGB)
        return True if r is not None else False, r
    def stop(self):
        self.d.stop()