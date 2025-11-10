import threading
import time
import math
from collections import deque
from flask import Flask, render_template, Response, jsonify
import cv2
import mediapipe as mp
import numpy as np
import pyautogui

# Try importing Pycaw for reading system volume
use_pycaw = False
try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    import pythoncom

    pythoncom.CoInitialize()
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    audio_interface = cast(interface, POINTER(IAudioEndpointVolume))
    vol_range = audio_interface.GetVolumeRange()
    MIN_VOL, MAX_VOL = vol_range[0], vol_range[1]
    use_pycaw = True
except Exception:
    use_pycaw = False

# ----------------------------------------
# Flask app setup
# ----------------------------------------
app = Flask(__name__, static_folder="static", template_folder="templates")

# Shared state for UI
state = {"gesture": "No Hand", "volume_percent": 50, "detected": False}
V_HISTORY_LEN = 80
volume_history = deque([50] * V_HISTORY_LEN, maxlen=V_HISTORY_LEN)

# Mediapipe setup
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils


def get_system_volume():
    """Read current system master volume (Windows only)."""
    if not use_pycaw:
        return state["volume_percent"]
    try:
        current_level = audio_interface.GetMasterVolumeLevel()
        percent = int(np.interp(current_level, [MIN_VOL, MAX_VOL], [0, 100]))
        return max(0, min(100, percent))
    except Exception:
        return state["volume_percent"]


class CameraThread:
    def __init__(self, src=0):
        self.cap = cv2.VideoCapture(src)
        self.lock = threading.Lock()
        self.frame = None
        self.running = False
        self.thread = None
        self.hands = mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )
        self.last_adjust = 0
        self.current_volume = get_system_volume()

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

        # Background volume sync thread
        threading.Thread(target=self._sync_system_volume, daemon=True).start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        self.cap.release()
        self.hands.close()

    def _sync_system_volume(self):
        """Continuously reads system volume every 0.3s to update display."""
        global state, volume_history
        while self.running:
            vol = get_system_volume()
            state["volume_percent"] = vol
            volume_history.append(vol)
            time.sleep(0.3)

    def _run(self):
        global state, volume_history
        smoothness = 0.85
        smooth_bar = 0.0

        while self.running:
            success, img = self.cap.read()
            if not success:
                time.sleep(0.01)
                continue

            img = cv2.flip(img, 1)
            h, w, _ = img.shape
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.hands.process(img_rgb)

            gesture = "No Hand"
            detected = False
            target_volume = self.current_volume

            if results.multi_hand_landmarks:
                detected = True
                for handLms in results.multi_hand_landmarks:
                    lm = handLms.landmark
                    mp_drawing.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

                    # Thumb tip (4) and Index tip (8)
                    x1, y1 = int(lm[4].x * w), int(lm[4].y * h)
                    x2, y2 = int(lm[8].x * w), int(lm[8].y * h)
                    cv2.circle(img, (x1, y1), 8, (255, 0, 255), -1)
                    cv2.circle(img, (x2, y2), 8, (255, 0, 255), -1)
                    cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

                    # Calculate distance between thumb and index
                    length = math.hypot(x2 - x1, y2 - y1)

                    # Finger status
                    tips = [4, 8, 12, 16, 20]
                    fingers = []
                    fingers.append(1 if lm[tips[0]].x > lm[tips[0]-1].x else 0)
                    for t in range(1, 5):
                        fingers.append(1 if lm[tips[t]].y < lm[tips[t]-2].y else 0)
                    total_fingers = fingers.count(1)

                    # Gesture mapping
                    if total_fingers == 0:
                        gesture = "Closed (Mute)"
                        target_volume = 0
                    elif total_fingers == 5:
                        gesture = "Open (100%)"
                        target_volume = 100
                    else:
                        target_volume = int(np.clip(np.interp(length, [10, 250], [0, 100]), 0, 100))
                        gesture = f"Pinching ({target_volume}%)"

                    smooth_bar = smooth_bar * smoothness + target_volume * (1 - smoothness)
                    new_volume = int(smooth_bar)
                    diff = new_volume - self.current_volume
                    now = time.time()

                    if abs(diff) >= 5 and (now - self.last_adjust) > 0.3:
                        key = "volumeup" if diff > 0 else "volumedown"
                        steps = min(abs(diff) // 3, 5)
                        for _ in range(steps):
                            pyautogui.press(key)
                            time.sleep(0.03)
                        self.current_volume = new_volume
                        self.last_adjust = now

                    state["gesture"] = gesture
                    state["detected"] = detected

            else:
                state["gesture"] = "No Hand Detected"
                state["detected"] = False

            with self.lock:
                self.frame = img

            time.sleep(0.01)

    def get_frame(self):
        with self.lock:
            if self.frame is None:
                return None
            ret, jpeg = cv2.imencode(".jpg", self.frame)
            if not ret:
                return None
            return jpeg.tobytes()


camera = CameraThread(0)
camera.start()


def generate_frames():
    while True:
        frame = camera.get_frame()
        if frame is None:
            time.sleep(0.01)
            continue
        yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        time.sleep(0.02)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/state")
def get_state():
    return jsonify({
        "gesture": state.get("gesture", "No Hand"),
        "detected": state.get("detected", False),
        "volume_percent": state.get("volume_percent", 0),
        "history": list(volume_history),
    })


if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        camera.stop()
