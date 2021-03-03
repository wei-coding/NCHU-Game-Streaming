import threading
import time
class TestThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        while True:
            time.sleep(1)
            print("Sleeping...")
if __name__ == "__main__":
    t = TestThread()
    t.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        