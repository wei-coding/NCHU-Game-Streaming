import time
import threading
class FpsMeter(threading.Thread):
    def __init__(self,interval = 10):
        threading.Thread.__init__(self)
        self.interval = interval
        self.count = 0
        self.fps = 0.0
        self.go = True
    def run(self):
        while(self.go):
            time.sleep(self.interval)
            self.fps = self.count / self.interval
            self.count = 0
            print(f'fps is {self.fps}')
    def inc_count(self):
        self.count += 1
    def get_fps(self) -> float:
        return self.fps