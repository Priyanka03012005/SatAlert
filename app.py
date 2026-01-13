import os
import base64
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import uuid

# Database imports - supports both PostgreSQL and SQLite
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    import sqlite3
    POSTGRES_AVAILABLE = False

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL')  # Render PostgreSQL connection string
USE_POSTGRES = POSTGRES_AVAILABLE and DATABASE_URL is not None

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    """Get database connection (PostgreSQL or SQLite)"""
    if USE_POSTGRES:
        # Parse DATABASE_URL for PostgreSQL
        import urllib.parse as urlparse
        result = urlparse.urlparse(DATABASE_URL)
        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        return conn
    else:
        # Fallback to SQLite
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    """Initialize database and create table if it doesn't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if USE_POSTGRES:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id SERIAL PRIMARY KEY,
                image_data TEXT NOT NULL,
                image_filename TEXT NOT NULL,
                label TEXT NOT NULL,
                confidence REAL NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_data TEXT NOT NULL,
                image_filename TEXT NOT NULL,
                label TEXT NOT NULL,
                confidence REAL NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
    
    conn.commit()
    conn.close()

def get_alerts_from_db(query, params=None):
    """Execute query and return results as list of dicts"""
    conn = get_db_connection()
    
    if USE_POSTGRES:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]
    else:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        alerts = []
        for row in results:
            alerts.append({
                'id': row[0],
                'image_data': row[1],
                'image_filename': row[2],
                'label': row[3],
                'confidence': row[4],
                'timestamp': row[5]
            })
        return alerts

@app.route('/')
def index():
    """Homepage - displays latest alert"""
    query = '''
        SELECT * FROM alerts 
        ORDER BY timestamp DESC 
        LIMIT 1
    '''
    alerts = get_alerts_from_db(query)
    
    alert = None
    if alerts:
        alert_data = alerts[0]
        alert = {
            'id': alert_data['id'],
            'image_data': alert_data['image_data'],
            'image_filename': alert_data['image_filename'],
            'label': alert_data['label'],
            'confidence': alert_data['confidence'],
            'timestamp': alert_data['timestamp']
        }
    
    return render_template('index.html', alert=alert)

@app.route('/history')
def history():
    """History page - displays all alerts"""
    query = '''
        SELECT * FROM alerts 
        ORDER BY timestamp DESC
    '''
    alerts = get_alerts_from_db(query)
    
    alerts_list = []
    for alert_data in alerts:
        alerts_list.append({
            'id': alert_data['id'],
            'image_data': alert_data['image_data'],
            'image_filename': alert_data['image_filename'],
            'label': alert_data['label'],
            'confidence': alert_data['confidence'],
            'timestamp': alert_data['timestamp']
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
        
        # Read image file and convert to base64
        file_content = file.read()
        image_base64 = base64.b64encode(file_content).decode('utf-8')
        
        # Generate unique filename
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
        filename = secure_filename(unique_filename)
        
        # Insert into database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if USE_POSTGRES:
            cursor.execute('''
                INSERT INTO alerts (image_data, image_filename, label, confidence, timestamp)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            ''', (image_base64, filename, label, confidence, timestamp))
            alert_id = cursor.fetchone()[0]
        else:
            cursor.execute('''
                INSERT INTO alerts (image_data, image_filename, label, confidence, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (image_base64, filename, label, confidence, timestamp))
            alert_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'id': alert_id,
            'message': 'Alert created successfully',
            'image_filename': filename
        }), 201
    
    except ValueError as e:
        return jsonify({'error': f'Invalid confidence value: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/image/<int:alert_id>')
def get_image(alert_id):
    """Serve image for a specific alert"""
    if USE_POSTGRES:
        query = '''
            SELECT image_data, image_filename FROM alerts 
            WHERE id = %s
        '''
    else:
        query = '''
            SELECT image_data, image_filename FROM alerts 
            WHERE id = ?
        '''
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(query, (alert_id,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return jsonify({'error': 'Image not found'}), 404
    
    if USE_POSTGRES:
        image_data, filename = result
    else:
        image_data, filename = result[0], result[1]
    
    # Decode base64 and return image
    image_bytes = base64.b64decode(image_data)
    
    # Determine content type from filename
    ext = filename.rsplit('.', 1)[1].lower()
    content_types = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'webp': 'image/webp'
    }
    content_type = content_types.get(ext, 'image/jpeg')
    
    from flask import Response
    return Response(image_bytes, mimetype=content_type)

if __name__ == '__main__':
    # Initialize database on startup
    init_db()
    
    # Get port from environment variable (Render.com) or default to 5000
    port = int(os.environ.get("PORT", 5000))
    
    # Run app
    app.run(host='0.0.0.0', port=port, debug=False)
