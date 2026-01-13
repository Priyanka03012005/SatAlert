# 🔥 Wildfire Detection Alert Web Application

A complete Flask-based web application for monitoring and alerting on wildfire detections. Designed for cloud deployment on Render.com with SQLite database and real-time alert display.

## 📋 Features

- **Latest Alert Display**: Homepage shows the most recent wildfire detection with image, label, confidence score, and timestamp
- **Alert History**: Complete history page with all previous detections in reverse chronological order
- **RESTful API**: POST endpoint to receive detection alerts from AI systems
- **Auto-refresh**: Homepage automatically refreshes every 3 seconds
- **Dark Theme UI**: Modern, responsive design optimized for mobile and desktop
- **Image Management**: Automatic image storage and serving with clickable thumbnails

## 🏗️ Project Structure

```
satellite/
├── app.py                 # Main Flask application
├── database.db            # SQLite database (auto-created)
├── requirements.txt       # Python dependencies
├── static/
│   └── alerts/           # Stored detection images
├── templates/
│   ├── index.html        # Homepage template
│   └── history.html      # History page template
└── README.md             # This file
```

## 🚀 Local Development Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation Steps

1. **Clone or download the project**

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Homepage: http://localhost:5000
   - History: http://localhost:5000/history
   - API Endpoint: http://localhost:5000/alert (POST)

## ☁️ Render.com Deployment

### Step 1: Prepare Your Repository

1. Push your code to GitHub, GitLab, or Bitbucket
2. Ensure all files are committed

### Step 2: Create Render Web Service

1. Go to [Render.com](https://render.com) and sign up/login
2. Click "New +" → "Web Service"
3. Connect your repository
4. Configure the service:
   - **Name**: wildfire-detection-alert (or your choice)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Plan**: Free tier is sufficient for testing

### Step 3: Environment Variables

No environment variables are required. The app automatically uses the `PORT` environment variable provided by Render.

### Step 4: Deploy

Click "Create Web Service" and wait for deployment to complete.

### Important Notes for Render

- The database (`database.db`) will persist in the filesystem
- Images in `static/alerts/` will persist between deployments
- For production, consider using a managed database service
- Free tier services may spin down after inactivity

## 🔌 API Usage

### POST /alert

Create a new alert by sending detection data.

**Endpoint**: `https://your-app.onrender.com/alert`

**Method**: POST

**Content-Type**: multipart/form-data

**Parameters**:
- `image` (file, required): Detection image file (png, jpg, jpeg, gif, webp)
- `label` (string, required): Detection label (e.g., "fire", "smoke")
- `confidence` (float, required): Confidence score between 0.0 and 1.0
- `timestamp` (string, required): Timestamp in format "YYYY-MM-DD HH:MM:SS"

**Example using Python requests**:

```python
import requests
from datetime import datetime

ALERT_URL = "https://your-app.onrender.com/alert"

# Prepare data
with open("detection_image.jpg", "rb") as img_file:
    response = requests.post(
        ALERT_URL,
        files={"image": img_file},
        data={
            "label": "fire",
            "confidence": 0.92,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    )

if response.status_code == 201:
    print("Alert created successfully!")
    print(response.json())
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

**Example using cURL**:

```bash
curl -X POST https://your-app.onrender.com/alert \
  -F "image=@detection_image.jpg" \
  -F "label=fire" \
  -F "confidence=0.92" \
  -F "timestamp=2026-01-13 18:22:10"
```

**Success Response** (201):
```json
{
    "success": true,
    "id": 1,
    "message": "Alert created successfully",
    "image_path": "alerts/abc123def456.jpg"
}
```

**Error Response** (400/500):
```json
{
    "error": "Error message description"
}
```

## 🤖 AI Integration Example

Here's a complete example of how to integrate with an AI detection system:

```python
import requests
import cv2
import numpy as np
from datetime import datetime
import os

# Configuration
ALERT_URL = "https://your-app.onrender.com/alert"
MODEL_PATH = "your_model.pth"  # Your AI model path

def detect_wildfire(image_path):
    """
    Your AI detection function
    Returns: (label, confidence)
    """
    # Load and preprocess image
    image = cv2.imread(image_path)
    # ... your detection logic ...
    
    # Example return (replace with actual detection)
    label = "fire"  # or "smoke"
    confidence = 0.92
    
    return label, confidence

def send_alert(image_path, label, confidence):
    """Send detection alert to web application"""
    try:
        with open(image_path, "rb") as img_file:
            response = requests.post(
                ALERT_URL,
                files={"image": img_file},
                data={
                    "label": label,
                    "confidence": str(confidence),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                timeout=10
            )
        
        if response.status_code == 201:
            print(f"✅ Alert sent successfully: {label} ({confidence:.2%})")
            return True
        else:
            print(f"❌ Error sending alert: {response.status_code}")
            print(response.json())
            return False
    
    except Exception as e:
        print(f"❌ Exception sending alert: {str(e)}")
        return False

# Main detection loop
if __name__ == "__main__":
    # Example: Process images from a directory
    image_dir = "detection_images"
    
    for filename in os.listdir(image_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(image_dir, filename)
            
            # Run detection
            label, confidence = detect_wildfire(image_path)
            
            # Only send alert if confidence is above threshold
            if confidence > 0.7:
                send_alert(image_path, label, confidence)
```

## 🗄️ Database Schema

The application uses SQLite with the following schema:

```sql
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_path TEXT NOT NULL,
    label TEXT NOT NULL,
    confidence REAL NOT NULL,
    timestamp TEXT NOT NULL
);
```

## 🛡️ Error Handling

The application includes comprehensive error handling:

- Missing required fields return 400 Bad Request
- Invalid file types are rejected
- Confidence values are validated (0.0 - 1.0)
- Database errors are caught and handled gracefully
- Missing images display appropriate messages

## 📱 Browser Compatibility

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## 🔒 Security Considerations

For production deployment, consider:

- Adding authentication/authorization
- Implementing rate limiting
- Using environment variables for sensitive data
- Adding HTTPS (automatic on Render.com)
- Implementing file size limits (currently 16MB)
- Adding input validation and sanitization
- Using a managed database service for better reliability

## 📝 License

This project is provided as-is for educational and development purposes.

## 🤝 Contributing

Feel free to fork, modify, and use this project for your needs.

## 📧 Support

For issues or questions, please check:
- Flask documentation: https://flask.palletsprojects.com/
- Render.com documentation: https://render.com/docs

---

**Built with ❤️ for wildfire detection and monitoring**
