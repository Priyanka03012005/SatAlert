"""
AI Integration Example for Wildfire Detection Alert System

This script demonstrates how to integrate an AI detection system
with the Wildfire Detection Alert Web Application.

Usage:
    python ai_integration_example.py
"""

import requests
from datetime import datetime
import os
import time

# Configuration
ALERT_URL = "http://localhost:5000/alert"  # Change to your Render.com URL in production
# ALERT_URL = "https://your-app.onrender.com/alert"  # For production

def send_alert(image_path, label, confidence):
    """
    Send detection alert to the web application.
    
    Args:
        image_path (str): Path to the detection image file
        label (str): Detection label ("fire" or "smoke")
        confidence (float): Confidence score between 0.0 and 1.0
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Validate image file exists
        if not os.path.exists(image_path):
            print(f"❌ Error: Image file not found: {image_path}")
            return False
        
        # Validate confidence range
        if not (0.0 <= confidence <= 1.0):
            print(f"❌ Error: Confidence must be between 0.0 and 1.0, got {confidence}")
            return False
        
        # Prepare timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Send POST request
        print(f"📤 Sending alert: {label} ({confidence:.2%}) from {image_path}")
        
        with open(image_path, "rb") as img_file:
            response = requests.post(
                ALERT_URL,
                files={"image": img_file},
                data={
                    "label": label,
                    "confidence": str(confidence),
                    "timestamp": timestamp
                },
                timeout=10
            )
        
        # Check response
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Alert sent successfully!")
            print(f"   Alert ID: {result.get('id')}")
            print(f"   Image Path: {result.get('image_path')}")
            print(f"   Timestamp: {timestamp}")
            return True
        else:
            print(f"❌ Error sending alert: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error message: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Response: {response.text}")
            return False
    
    except requests.exceptions.Timeout:
        print(f"❌ Error: Request timed out. Is the server running?")
        return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Could not connect to server. Check URL: {ALERT_URL}")
        return False
    except Exception as e:
        print(f"❌ Exception sending alert: {str(e)}")
        return False


def simulate_detection(image_path, label="fire", confidence=0.92):
    """
    Simulate a detection result (replace with your actual AI model).
    
    In a real implementation, you would:
    1. Load your AI model
    2. Preprocess the image
    3. Run inference
    4. Parse results
    
    Args:
        image_path (str): Path to image
        label (str): Simulated label
        confidence (float): Simulated confidence
    
    Returns:
        tuple: (label, confidence)
    """
    # TODO: Replace with actual AI detection
    # Example:
    # model = load_model("wildfire_model.pth")
    # image = preprocess_image(image_path)
    # prediction = model.predict(image)
    # label, confidence = parse_prediction(prediction)
    
    return label, confidence


def main():
    """Main function demonstrating the integration workflow."""
    print("=" * 60)
    print("🔥 Wildfire Detection Alert System - AI Integration")
    print("=" * 60)
    print()
    
    # Example 1: Send a single alert
    print("Example 1: Sending a single alert")
    print("-" * 60)
    
    # Replace with actual image path
    example_image = "example_detection.jpg"
    
    if os.path.exists(example_image):
        label, confidence = simulate_detection(example_image)
        send_alert(example_image, label, confidence)
    else:
        print(f"⚠️  Example image not found: {example_image}")
        print("   Create a test image or update the path in the script")
    
    print()
    
    # Example 2: Batch processing
    print("Example 2: Batch processing multiple detections")
    print("-" * 60)
    
    # Simulate multiple detections
    detections = [
        ("fire", 0.95),
        ("smoke", 0.87),
        ("fire", 0.91),
    ]
    
    for i, (label, confidence) in enumerate(detections, 1):
        print(f"\nDetection {i}:")
        # In real scenario, you would have actual image paths
        # For demo, we'll just show the structure
        print(f"  Would process image and send: {label} ({confidence:.2%})")
        # send_alert(f"detection_{i}.jpg", label, confidence)
        time.sleep(0.5)  # Small delay for demo
    
    print()
    print("=" * 60)
    print("Integration example complete!")
    print()
    print("Next steps:")
    print("1. Replace simulate_detection() with your actual AI model")
    print("2. Update ALERT_URL to your Render.com deployment URL")
    print("3. Implement your detection loop (camera feed, batch processing, etc.)")
    print("=" * 60)


if __name__ == "__main__":
    main()
