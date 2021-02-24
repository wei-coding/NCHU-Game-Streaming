import pyaudio
import wave
import threading
import time
import struct

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 5

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("* recording")

frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    print(data)
    frames.append(data)

print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()

wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

class AudioSender(threading.Thread):
    MAX_DGRAM = 2**16
    MAX_IMAGE_DGRAM = MAX_DGRAM - 64  # extract 64 bytes in case UDP frame overflown
    def __init__(self, sock, port, addr="127.0.0.1"):
        threading.Thread.__init__(self)
        self.buffer = []
        self.sock = sock
        self.port = port
        self.addr = addr
    def run(self):
        while True:
            if(len(self.buffer) != 0):
                frame = self.buffer.pop(0)
                size = len(frame)
                count = math.ceil(size/(self.MAX_IMAGE_DGRAM))
                array_pos_start = 0
                while count:
                    array_pos_end = min(size, array_pos_start + self.MAX_IMAGE_DGRAM)
                    self.s.sendto(struct.pack("B", count) +
                        frame[array_pos_start:array_pos_end],
                        (self.addr, self.port)
                        )
                    array_pos_start = array_pos_end
                    count -= 1
            else:
                time.sleep(0.1)
    def add(self, data):
        self.buffer.append(data)
class AudioRecoder(threading.Thread):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    def __init__(self):
        threading.Thread.__init__(self)
        self.p = pyaudio.PyAudio()
        self.buffer = []
    def run(self):
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
        while True:
            data = stream.read(CHUNK)
            self.buffer.append(data)
    def get_frame(self):
        frame = self.buffer.pop(0)
        return frame
class AudioReceiver(threading.Thread):
    MAX_DGRAM = 2**16
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    def __init__(self, sock, port):
        self.sock = sock
        self.port = port
        self.p = pyaudio.PyAudio()
        self.sock.bind(('127.0.0.1',12346))
        dat = b''
        self.dump_buffer(s)
    def run(self):
        stream = p.open(format = FORMAT,
                        channels = CHANNELS,
                        rate = RATE,
                        output = True)
        while True:
            seg, addr = s.recvfrom(MAX_DGRAM)
            if struct.unpack("B", seg[0:1])[0] > 1:
                dat += seg[1:]
            else:
                dat += seg[1:]
                stream.write(dat)
                dat = b''
    def dump_buffer(self, s):
    """ Emptying buffer frame """
        while True:
            seg, addr = s.recvfrom(MAX_DGRAM)
            print(seg[0])
            if struct.unpack("B", seg[0:1])[0] == 1:
                print("finish emptying buffer")
                break
