"""
Raspberry Pi Fire Detection System
Detects fires using YOLO model and sends alerts to SatAlert website
"""

from ultralytics import YOLO
import cv2
import requests
from datetime import datetime
import os
import time
import numpy as np

# ==================== CONFIGURATION ====================
# Website URL (update with your Render.com URL)
WEBSITE_URL = "https://satalert.onrender.com/alert"  # Change to your deployed URL
# For local testing: "http://localhost:5000/alert"

# Camera stream URL (ESP32-CAM or other IP camera)
CAMERA_URL = "http://192.168.0.100:81/stream"

# YOLO model path
MODEL_PATH = "wildfire_model.pt"

# Detection settings
CONFIDENCE_THRESHOLD = 0.5  # Minimum confidence to trigger alert
FIRE_CLASS_NAMES = ["fire", "smoke", "flame"]  # Class names that indicate fire
ALERT_COOLDOWN = 30  # Seconds between alerts (prevent spam)

# Image save settings
SAVE_DETECTIONS = True
DETECTION_FOLDER = "detections"
# ========================================================

class FireDetector:
    def __init__(self):
        """Initialize the fire detection system"""
        print("🔥 Initializing Fire Detection System...")
        
        # Load YOLO model
        try:
            self.model = YOLO(MODEL_PATH)
            print(f"✅ Model loaded: {MODEL_PATH}")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            exit(1)
        
        # Get class names from model
        self.class_names = self.model.names
        print(f"📋 Model classes: {list(self.class_names.values())}")
        
        # Initialize camera
        self.cap = cv2.VideoCapture(CAMERA_URL)
        if not self.cap.isOpened():
            print(f"❌ Cannot open video stream: {CAMERA_URL}")
            print("   Check camera URL and network connection")
            exit(1)
        print(f"✅ Camera connected: {CAMERA_URL}")
        
        # Create detection folder
        if SAVE_DETECTIONS:
            os.makedirs(DETECTION_FOLDER, exist_ok=True)
            print(f"✅ Detection folder: {DETECTION_FOLDER}")
        
        # Alert tracking
        self.last_alert_time = {}
        self.alert_count = 0
        
        print("🚀 System ready!\n")
    
    def is_fire_detected(self, label):
        """Check if detected label indicates fire/smoke"""
        label_lower = label.lower()
        for fire_name in FIRE_CLASS_NAMES:
            if fire_name in label_lower:
                return True
        return False
    
    def save_detection_image(self, frame, boxes, label, confidence):
        """Save detection image with timestamp"""
        if not SAVE_DETECTIONS:
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{DETECTION_FOLDER}/detection_{timestamp}_{self.alert_count}.jpg"
        
        # Draw detection on image
        annotated_frame = frame.copy()
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
            text = f"{label} {confidence:.2f}"
            cv2.putText(annotated_frame, text, (x1, y1 - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        cv2.imwrite(filename, annotated_frame)
        return filename
    
    def send_alert(self, image_path, label, confidence):
        """Send alert to SatAlert website"""
        try:
            print(f"\n📤 Sending alert: {label} ({confidence:.1%})")
            
            # Prepare timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Read image file
            with open(image_path, "rb") as img_file:
                files = {"image": (os.path.basename(image_path), img_file, "image/jpeg")}
                data = {
                    "label": label,
                    "confidence": str(confidence),
                    "timestamp": timestamp
                }
                
                # Send POST request
                response = requests.post(
                    WEBSITE_URL,
                    files=files,
                    data=data,
                    timeout=10
                )
            
            # Check response
            if response.status_code == 201:
                result = response.json()
                print(f"✅ Alert sent successfully!")
                print(f"   Alert ID: {result.get('id')}")
                print(f"   Timestamp: {timestamp}")
                return True
            else:
                print(f"❌ Error sending alert: HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Message: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"   Response: {response.text}")
                return False
        
        except requests.exceptions.Timeout:
            print(f"❌ Error: Request timed out. Check website URL: {WEBSITE_URL}")
            return False
        except requests.exceptions.ConnectionError:
            print(f"❌ Error: Could not connect to website. Check URL and internet: {WEBSITE_URL}")
            return False
        except Exception as e:
            print(f"❌ Error sending alert: {str(e)}")
            return False
    
    def should_send_alert(self, label):
        """Check if alert should be sent (cooldown check)"""
        current_time = time.time()
        last_time = self.last_alert_time.get(label, 0)
        
        if current_time - last_time >= ALERT_COOLDOWN:
            self.last_alert_time[label] = current_time
            return True
        return False
    
    def process_frame(self, frame):
        """Process a single frame for fire detection"""
        # Resize frame for faster processing
        frame_resized = cv2.resize(frame, (640, 480))
        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        
        # Run YOLO detection
        results = self.model(frame_rgb, verbose=False)
        
        # Process detections
        fire_detected = False
        for r in results:
            boxes = r.boxes
            for box in boxes:
                confidence = float(box.conf[0])
                cls = int(box.cls[0])
                label = self.class_names.get(cls, "Unknown")
                
                # Check if confidence meets threshold
                if confidence < CONFIDENCE_THRESHOLD:
                    continue
                
                # Check if it's a fire-related detection
                if self.is_fire_detected(label):
                    fire_detected = True
                    
                    # Check cooldown
                    if not self.should_send_alert(label):
                        print(f"⏳ Alert cooldown active for {label}, skipping...")
                        continue
                    
                    # Save detection image
                    image_path = self.save_detection_image(frame_resized, [box], label, confidence)
                    
                    if image_path:
                        # Send alert to website
                        self.alert_count += 1
                        self.send_alert(image_path, label, confidence)
        
        return fire_detected, results
    
    def draw_detections(self, frame, results):
        """Draw detection boxes on frame"""
        annotated_frame = frame.copy()
        
        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                label = self.class_names.get(cls, "Unknown")
                
                # Color: red for fire, green for others
                color = (0, 0, 255) if self.is_fire_detected(label) else (0, 255, 0)
                thickness = 3 if self.is_fire_detected(label) else 2
                
                # Draw box
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, thickness)
                
                # Draw label
                text = f"{label} {conf:.2f}"
                y_text = max(y1 - 10, 20)
                cv2.putText(annotated_frame, text, (x1, y_text), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        return annotated_frame
    
    def run(self):
        """Main detection loop"""
        print("🎥 Starting detection loop...")
        print("   Press 'q' to quit\n")
        
        frame_count = 0
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("⚠️ No frame received, retrying...")
                    time.sleep(1)
                    continue
                
                frame_count += 1
                
                # Process frame
                fire_detected, results = self.process_frame(frame)
                
                # Draw detections on frame
                annotated_frame = self.draw_detections(frame, results)
                
                # Add status text
                status_text = f"Frames: {frame_count} | Alerts: {self.alert_count}"
                if fire_detected:
                    status_text += " | 🔥 FIRE DETECTED!"
                
                cv2.putText(annotated_frame, status_text, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Display frame
                cv2.imshow("Fire Detection - SatAlert", annotated_frame)
                
                # Check for quit
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    print("\n🛑 Stopping detection...")
                    break
                
                # Small delay to prevent overwhelming the system
                time.sleep(0.1)
        
        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("\n🧹 Cleaning up...")
        self.cap.release()
        cv2.destroyAllWindows()
        print("✅ Cleanup complete")


def main():
    """Main function"""
    print("=" * 60)
    print("🛰️ SatAlert - Raspberry Pi Fire Detection System")
    print("=" * 60)
    print()
    
    # Check if model exists
    if not os.path.exists(MODEL_PATH):
        print(f"❌ Model file not found: {MODEL_PATH}")
        print("   Please ensure wildfire_model.pt is in the current directory")
        exit(1)
    
    # Create detector and run
    detector = FireDetector()
    detector.run()


if __name__ == "__main__":
    main()
