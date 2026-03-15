# 🛰️ SatAlert

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

**Built with ❤️ for wildfire detection and monitoring**
