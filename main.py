from flask import Flask, render_template, request, jsonify
import os
import base64
from datetime import datetime
import numpy as np
from database import init_db, add_user, add_attendance
from face_utils import save_face_encoding, recognize_face

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/punch_in')
def punch_in():
    return render_template('punch_in.html')

@app.route('/sheet')
def sheet():
    from database import get_all_attendance
    attendance_records = get_all_attendance()
    return render_template('sheet.html', records=attendance_records)

@app.route('/api/register', methods=['POST'])
def api_register():
    try:
        data = request.get_json()
        name = data.get('name')
        image_data = data.get('image')
        
        if not name or not image_data:
            return jsonify({'success': False, 'message': 'Name and image required'})
        
        # Decode base64 image
        image_data = image_data.split(',')[1]  # Remove data:image/jpeg;base64,
        image_bytes = base64.b64decode(image_data)
        
        # Save image temporarily
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f'temp_{name}.jpg')
        with open(temp_path, 'wb') as f:
            f.write(image_bytes)
        
        # Process face encoding
        encoding = save_face_encoding(temp_path, name)
        
        if encoding is not None:
            # Save to database
            add_user(name, encoding.tolist())
            os.remove(temp_path)  # Clean up temp file
            return jsonify({'success': True, 'message': f'{name} registered successfully!'})
        else:
            os.remove(temp_path)
            return jsonify({'success': False, 'message': 'No face detected in image'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/punch_in', methods=['POST'])
def api_punch_in():
    try:
        data = request.get_json()
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({'success': False, 'message': 'Image required'})
        
        # Decode base64 image
        image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        
        # Save image temporarily
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_punch.jpg')
        with open(temp_path, 'wb') as f:
            f.write(image_bytes)
        
        # Recognize face
        recognized_name = recognize_face(temp_path)
        
        if recognized_name:
            # Add attendance record
            add_attendance(recognized_name, datetime.now())
            os.remove(temp_path)
            return jsonify({
                'success': True, 
                'message': f'Welcome {recognized_name}! Attendance marked.',
                'name': recognized_name,
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        else:
            os.remove(temp_path)
            return jsonify({'success': False, 'message': 'Face not recognized'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)