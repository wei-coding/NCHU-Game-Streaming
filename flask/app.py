from flask import Flask, render_template, Response, request
import cv2
import screenshot as scnshot

app = Flask(__name__)

screen = scnshot.gpu_screenshots()
screen.shot()

ENCODE_PARAM_JPEG = [int(cv2.IMWRITE_JPEG_QUALITY),80,int(cv2.IMWRITE_JPEG_OPTIMIZE),1]
ENCODE_PARAM_WEBP = [int(cv2.IMWRITE_WEBP_QUALITY), 80]
ENCODE_PARAM_PNG = [int(cv2.IMWRITE_PNG_COMPRESSION), 7]
signal = True

def gen_frames():
    global signal
    while signal:
        success, frame = screen.get_frames()  # read the camera frame
        if not success:
            break
        else:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            ret, buffer = cv2.imencode('.jpg', frame, ENCODE_PARAM_JPEG)
            frame = buffer.tobytes()
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