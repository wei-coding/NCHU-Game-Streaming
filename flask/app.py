from flask import Flask, render_template, Response, request
import screenshot as scn
from turbojpeg import TurboJPEG, TJPF_BGR

app = Flask(__name__)

screen = scn.FastScreenshots()
screen.start()

# screen = scn.win32shot()
# screen.start()

jpeg = TurboJPEG()

signal = True


def gen_frames():
    global signal
    while signal:
        success, frame = screen.get_latest_frame()  # read the camera frame
        if not success:
            break
        frame = jpeg.encode(frame, pixel_format=TJPF_BGR)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/continue')
@app.route('/stop')
def stop():
    global signal
    signal = not signal
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
