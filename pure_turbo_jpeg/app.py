from flask import Flask, render_template, Response, request
import cv2
import screenshot as scn
from turbojpeg import TurboJPEG

app = Flask(__name__)

screen = scn.gpu_screenshots()
screen.start()

JPEG_ARGUM = [int(cv2.IMWRITE_JPEG_QUALITY), 95, int(cv2.IMWRITE_JPEG_OPTIMIZE), 0]

signal = True


def gen_frames():
    global signal
    while signal:
        success, frame = screen.get_latest_frame()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame, JPEG_ARGUM)
            #frame = jpeg.encode(frame, pixel_format=TJPF_BGR)
            frame = buffer.tobytes()
            #frame = stream.encode(frame)
            
            yield (b'--frame\r\n'
                b'Content-Type: video/h264\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
