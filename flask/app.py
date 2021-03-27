from flask import Flask, render_template, Response, request
from flask_caching import Cache
import screenshot as scn
from turbojpeg import TurboJPEG, TJPF_BGR
from numba import jit
from functools import lru_cache

app = Flask(__name__)

screen = scn.FastScreenshots()
screen.start()

jpeg = TurboJPEG()

signal = True

@jit
def encode_jpeg(frame):
    return jpeg.encode(frame, pixel_format=TJPF_BGR)


@jit
def gen_frames():
    global signal
    while signal:
        success, frame = screen.get_latest_frame()  # read the camera frame
        if not success:
            break
        else:
            frame = encode_jpeg(frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')