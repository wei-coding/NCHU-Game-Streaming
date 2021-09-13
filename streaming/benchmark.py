import turbojpeg
import cv2
import d3dshot
import time


def main():
    shot = d3dshot.create(capture_output='numpy')
    img = shot.screenshot()
    jpeg = turbojpeg.TurboJPEG()
    t = time.time()
    encoded_jpeg = jpeg.encode(img)
    print(time.time() - t)
    t = time.time()
    encoded_cv = cv2.imencode(".jpg", img)[1]
    print(time.time() - t)
    t = time.time()
    img = jpeg.decode(encoded_jpeg)
    print(time.time() - t)
    t = time.time()
    img = cv2.imdecode(encoded_cv, cv2.IMREAD_COLOR)
    print(time.time() - t)


if __name__ == "__main__":
    main()
