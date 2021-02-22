import threading
import time
class FrameSegment(threading.Thread):
    """
    Object to break down image frame segment
    if the size of image exceed maximum datagram size
    """
    MAX_DGRAM = 2**16
    MAX_IMAGE_DGRAM = MAX_DGRAM - 64  # extract 64 bytes in case UDP frame overflown

    def __init__(self, sock, port, addr="127.0.0.1"):
        threading.Thread.__init__(self)
        self.s = sock
        self.port = port
        self.addr = addr
        self.buffer = []

    def run(self):
        """
        Compress image and Break down
        into data segments
        """
        while(True):
            if(len(self.buffer) != 0):
                img = self.buffer.pop()
                compress_img = cv2.imencode('.jpg', img)[1]
                dat = compress_img.tostring()
                size = len(dat)
                count = math.ceil(size/(self.MAX_IMAGE_DGRAM))
                array_pos_start = 0
                while count:
                    array_pos_end = min(size, array_pos_start + self.MAX_IMAGE_DGRAM)
                    self.s.sendto(struct.pack("B", count) +
                        dat[array_pos_start:array_pos_end],
                        (self.addr, self.port)
                        )
                    array_pos_start = array_pos_end
                    count -= 1
            else:
                time.sleep(10)
    def add_buffer(self,img):
        self.buffer.insert(0,img)