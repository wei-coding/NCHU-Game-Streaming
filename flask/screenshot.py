import d3dshot
class gpu_screenshots():
    def __init__(self):
        self.d = d3dshot.create(capture_output='numpy', frame_buffer_size=5)
    def shot(self):
        self.d.capture()
    def get_frames(self):
        r = self.d.get_latest_frame()
        return True if r is not None else False, r
    def stop(self):
        self.d.stop()