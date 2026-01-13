import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/alerts'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    """Initialize SQLite database and create table if it doesn't exist"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_path TEXT NOT NULL,
            label TEXT NOT NULL,
            confidence REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Homepage - displays latest alert"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM alerts 
        ORDER BY timestamp DESC 
        LIMIT 1
    ''')
    latest_alert = cursor.fetchone()
    conn.close()
    
    alert = None
    if latest_alert:
        alert = {
            'id': latest_alert['id'],
            'image_path': latest_alert['image_path'],
            'label': latest_alert['label'],
            'confidence': latest_alert['confidence'],
            'timestamp': latest_alert['timestamp']
        }
    
    return render_template('index.html', alert=alert)

@app.route('/history')
def history():
    """History page - displays all alerts"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM alerts 
        ORDER BY timestamp DESC
    ''')
    alerts = cursor.fetchall()
    conn.close()
    
    alerts_list = []
    for alert in alerts:
        alerts_list.append({
            'id': alert['id'],
            'image_path': alert['image_path'],
            'label': alert['label'],
            'confidence': alert['confidence'],
            'timestamp': alert['timestamp']
        })
    
    return render_template('history.html', alerts=alerts_list)

@app.route('/alert', methods=['POST'])
def create_alert():
    """API endpoint to create a new alert"""
    try:
        # Validate required fields
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        if 'label' not in request.form:
            return jsonify({'error': 'No label provided'}), 400
        
        if 'confidence' not in request.form:
            return jsonify({'error': 'No confidence provided'}), 400
        
        if 'timestamp' not in request.form:
            return jsonify({'error': 'No timestamp provided'}), 400
        
        file = request.files['image']
        label = request.form['label']
        confidence = float(request.form['confidence'])
        timestamp = request.form['timestamp']
        
        # Validate file
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif, webp'}), 400
        
        # Validate confidence range
        if not (0.0 <= confidence <= 1.0):
            return jsonify({'error': 'Confidence must be between 0.0 and 1.0'}), 400
        
        # Generate unique filename to prevent conflicts
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
        filename = secure_filename(unique_filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save image
        file.save(filepath)
        
        # Store relative path for web access
        image_path = f"alerts/{filename}"
        
        # Insert into database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO alerts (image_path, label, confidence, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (image_path, label, confidence, timestamp))
        conn.commit()
        alert_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            'success': True,
            'id': alert_id,
            'message': 'Alert created successfully',
            'image_path': image_path
        }), 201
    
    except ValueError as e:
        return jsonify({'error': f'Invalid confidence value: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

if __name__ == '__main__':
    # Initialize database on startup
    init_db()
    
    # Get port from environment variable (Render.com) or default to 5000
    port = int(os.environ.get("PORT", 5000))
    
    # Run app
    app.run(host='0.0.0.0', port=port, debug=False)
