import face_recognition
import numpy as np
from database import get_all_users

def save_face_encoding(image_path, name):
    """Extract and return face encoding from image"""
    try:
        # Load image
        image = face_recognition.load_image_file(image_path)
        
        # Get face encodings
        face_encodings = face_recognition.face_encodings(image)
        
        if len(face_encodings) > 0:
            return face_encodings[0]
        else:
            return None
            
    except Exception as e:
        print(f"Error processing face: {e}")
        return None

def check_face_exists(image_path, tolerance=0.6):
    """Check if the face in the image already exists in the database"""
    try:
        # Load the image to check
        unknown_image = face_recognition.load_image_file(image_path)
        unknown_encodings = face_recognition.face_encodings(unknown_image)
        
        if len(unknown_encodings) == 0:
            return None, "No face detected in image"
        
        unknown_encoding = unknown_encodings[0]
        
        # Get all registered users
        users = get_all_users()
        
        if not users:
            return None, None  # No users registered yet
        
        # Check against all existing faces
        for user in users:
            known_encoding = np.array(user['face_encoding'])
            
            # Compare faces with tolerance
            matches = face_recognition.compare_faces([known_encoding], unknown_encoding, tolerance=tolerance)
            
            if matches[0]:  # Face matches
                return user['name'], f"Face is already registered!!"
        
        return None, None  # Face not found in database
    except Exception as e:
        print(f"Error checking face: {e}")
        return None, f"Error checking face: {str(e)}"

def recognize_face(image_path):
    """Recognize face from image and return name if found"""
    try:
        # Load the image to recognize
        unknown_image = face_recognition.load_image_file(image_path)
        unknown_encodings = face_recognition.face_encodings(unknown_image)
        
        if len(unknown_encodings) == 0:
            return None
        
        unknown_encoding = unknown_encodings[0]
        
        # Get all registered users
        users = get_all_users()
        
        if not users:
            return None
        
        # Create arrays of known encodings and names
        known_encodings = []
        known_names = []
        
        for user in users:
            known_encodings.append(np.array(user['face_encoding']))
            known_names.append(user['name'])
        
        # Compare faces
        matches = face_recognition.compare_faces(known_encodings, unknown_encoding)
        face_distances = face_recognition.face_distance(known_encodings, unknown_encoding)
        
        # Find the best match
        if True in matches:
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                return known_names[best_match_index]
        
        return None
        
    except Exception as e:
        print(f"Error recognizing face: {e}")
        return None