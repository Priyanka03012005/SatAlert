# -*- coding: utf-8 -*-

from ultralytics import YOLO
import cv2
import requests
import time
import os
from datetime import datetime
import torch

# ================= CONFIG =================
MODEL_PATH = "wildfire_model.pt"

# ESP32-CAM stream OR use 0 for USB/Pi camera
CAMERA_URL = "http://10.0.8.20:81/stream"
# CAMERA_URL = 0

ALERT_URL = "https://satalert.onrender.com/alert"

CONFIDENCE_THRESHOLD = 0.5
ALERT_COOLDOWN = 30  # seconds
SAVE_DIR = "detections"
# =========================================

os.makedirs(SAVE_DIR, exist_ok=True)

print("CUDA available:", torch.cuda.is_available())

# ---------- Load YOLO Model (CPU only) ----------
model = YOLO(MODEL_PATH)
model.to("cpu")
CLASS_NAMES = model.names

# ---------- Camera ----------
cap = cv2.VideoCapture(CAMERA_URL)
if not cap.isOpened():
    print("? Cannot open camera stream")
    exit(1)

print("? Camera connected")
print("?? CPU-only inference enabled")
print("?? SatAlert started\n")

last_alert_time = 0
alert_count = 0

# ---------- Main Loop ----------
while True:
    ret, frame = cap.read()
    if not ret:
        print("?? No frame received")
        time.sleep(1)
        continue

    frame = cv2.resize(frame, (416, 416))

    # YOLO inference (CPU)
    results = model(frame, device="cpu", verbose=False)

    detected = False
    label = ""
    confidence = 0.0

    for r in results:
        for box in r.boxes:
            confidence = float(box.conf[0])
            cls = int(box.cls[0])
            label = CLASS_NAMES.get(cls, "Unknown")

            if confidence < CONFIDENCE_THRESHOLD:
                continue

            # Only fire/smoke classes
            if label.lower() not in ["fire", "smoke", "flame"]:
                continue

            detected = True

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(
                frame,
                f"{label} {confidence:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 255),
                2
            )

    # ---------- Send Alert ----------
    now = time.time()
    if detected and (now - last_alert_time > ALERT_COOLDOWN):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = f"{SAVE_DIR}/{label}_{int(now)}.jpg"

        cv2.imwrite(filename, frame)

        try:
            with open(filename, "rb") as img:
                response = requests.post(
                    ALERT_URL,
                    files={"image": img},
                    data={
                        "label": label,
                        "confidence": str(confidence),
                        "timestamp": timestamp
                    },
                    timeout=10
                )

            if response.status_code in (200, 201):
                alert_count += 1
                print(f"?? Alert sent ({alert_count}) ? {label} ({confidence:.2f})")
            else:
                print(f"? Server error: {response.status_code}")

        except Exception as e:
            print("? Failed to send alert:", e)

        last_alert_time = now

    # ---------- Display ----------
    cv2.putText(
        frame,
        f"Alerts: {alert_count}",
        (10, 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.imshow("SatAlert Fire Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# ---------- Cleanup ----------
cap.release()
cv2.destroyAllWindows()
print("?? SatAlert stopped")
