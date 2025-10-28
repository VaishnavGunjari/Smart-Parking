from flask import Flask, render_template, Response, jsonify
from flask_cors import CORS  # Import CORS
import cv2
import pickle
import numpy as np

app = Flask(__name__)
CORS(app)
# Load parking positions
with open('CarParkPos', 'rb') as f:
    posList = pickle.load(f)

width, height = 107, 48

# Video feed
cap = cv2.VideoCapture('/Users/karthikraghavk/Desktop/k/carPark.mp4')


def check_parking_space(imgPro):
    space_counter = 0
    for pos in posList:
        x, y = pos
        imgCrop = imgPro[y:y + height, x:x + width]
        count = cv2.countNonZero(imgCrop)
        if count < 900:
            space_counter += 1
    return space_counter, len(posList)


@app.route('/video_feed')
def video_feed():
    def generate_frames():
        while True:
            success, img = cap.read()
            if not success:
                print("Failed to retrieve frame.")
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
            imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                 cv2.THRESH_BINARY_INV, 25, 16)
            imgMedian = cv2.medianBlur(imgThreshold, 5)
            kernel = np.ones((3, 3), np.uint8)
            imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

            free_spaces, total_spaces = check_parking_space(imgDilate)
            _, jpeg = cv2.imencode('.jpg', img)
            frame = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/parking_status')
def parking_status():
    cap.set(cv2.CAP_PROP_POS_FRAMES, cap.get(cv2.CAP_PROP_POS_FRAMES))  # Get current frame for processing
    success, img = cap.read()
    if not success:
        return jsonify({'freeSpaces': 0, 'totalSpaces': 0})
    
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
    imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY_INV, 25, 16)
    imgMedian = cv2.medianBlur(imgThreshold, 5)
    kernel = np.ones((3, 3), np.uint8)
    imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

    free_spaces, total_spaces = check_parking_space(imgDilate)
    return jsonify({'freeSpaces': free_spaces, 'totalSpaces': total_spaces})


@app.route('/start_detection')
def start_detection():
    return jsonify({'status': 'Detection started'})


@app.route('/stop_detection')
def stop_detection():
    return jsonify({'status': 'Detection stopped'})


@app.route('/')
def home():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)