import cv2
import os
import numpy as np
import time
from pathlib import Path

class StableFaceRecognition:
    def __init__(self, dataset_path="./dataset/images"):
        self.dataset_path = dataset_path
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.known_faces = []
        self.known_names = []
        
        # Stability parameters
        self.detection_history = {}
        self.detection_cooldown = 2.0  # 2 seconds between announcements
        self.stability_threshold = 5  # Need 5 consistent detections
        self.max_history_age = 3.0  # Clear history after 3 seconds
        
    def load_dataset(self):
        """Load and process faces from the dataset"""
        print("Loading faces from dataset...")
        
        dataset_dir = Path(self.dataset_path)
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        
        for image_path in dataset_dir.iterdir():
            if image_path.suffix.lower() in image_extensions:
                name = image_path.stem.rsplit('_', 1)[0]
                
                print(f"Loading {image_path.name} for {name}")
                
                image = cv2.imread(str(image_path))
                if image is None:
                    print(f"✗ Could not load {image_path.name}")
                    continue
                
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)
                
                if len(faces) > 0:
                    (x, y, w, h) = faces[0]
                    face = gray[y:y+h, x:x+w]
                    face = cv2.resize(face, (100, 100))
                    
                    self.known_faces.append(face)
                    self.known_names.append(name)
                    print(f"✓ Added face for {name}")
                else:
                    print(f"✗ No face found in {image_path.name}")
        
        print(f"Total faces loaded: {len(self.known_faces)}")
        return len(self.known_faces) > 0
    
    def compare_faces(self, face1, face2):
        """Compare two face images using template matching"""
        face1 = cv2.resize(face1, (100, 100))
        face2 = cv2.resize(face2, (100, 100))
        result = cv2.matchTemplate(face1, face2, cv2.TM_CCOEFF_NORMED)
        return result[0][0]
    
    def recognize_face(self, face_image):
        """Recognize a face by comparing with known faces"""
        if len(self.known_faces) == 0:
            return "Unknown", 0
        
        best_match_score = -1
        best_match_name = "Unknown"
        
        face_resized = cv2.resize(face_image, (100, 100))
        
        for i, known_face in enumerate(self.known_faces):
            score = self.compare_faces(face_resized, known_face)
            if score > best_match_score:
                best_match_score = score
                best_match_name = self.known_names[i]
        
        confidence = best_match_score * 100
        if best_match_score < 0.6:
            best_match_name = "Unknown"
            confidence = 0
        
        return best_match_name, confidence
    
    def update_detection_history(self, face_id, name, confidence, current_time):
        """Update detection history for stability"""
        if face_id not in self.detection_history:
            self.detection_history[face_id] = {
                'detections': [],
                'last_announcement': 0,
                'stable_name': None,
                'stable_confidence': 0
            }
        
        history = self.detection_history[face_id]
        
        # Add current detection
        history['detections'].append({
            'name': name,
            'confidence': confidence,
            'time': current_time
        })
        
        # Remove old detections
        history['detections'] = [d for d in history['detections'] 
                               if current_time - d['time'] < self.max_history_age]
        
        # Check for stability
        if len(history['detections']) >= self.stability_threshold:
            # Get most common name in recent detections
            recent_names = [d['name'] for d in history['detections'][-self.stability_threshold:]]
            most_common = max(set(recent_names), key=recent_names.count)
            
            # If we have enough consistent detections
            if recent_names.count(most_common) >= self.stability_threshold:
                history['stable_name'] = most_common
                # Average confidence for stable detections
                stable_confidences = [d['confidence'] for d in history['detections'][-self.stability_threshold:] 
                                    if d['name'] == most_common]
                history['stable_confidence'] = sum(stable_confidences) / len(stable_confidences)
                
                # Check if we should announce
                if (current_time - history['last_announcement'] > self.detection_cooldown and 
                    most_common != "Unknown"):
                    print(f"🎯 Stable Detection: {most_common} ({history['stable_confidence']:.1f}%)")
                    history['last_announcement'] = current_time
                
                return True, most_common, history['stable_confidence']
        
        return False, name, confidence
    
    def cleanup_old_detections(self, current_time):
        """Remove old detection histories"""
        to_remove = []
        for face_id, history in self.detection_history.items():
            if not history['detections'] or current_time - history['detections'][-1]['time'] > self.max_history_age:
                to_remove.append(face_id)
        
        for face_id in to_remove:
            del self.detection_history[face_id]
    
    def real_time_recognition(self, camera_index=1):
        """Real-time face recognition with stability"""
        if len(self.known_faces) == 0:
            print("❌ No faces loaded in dataset!")
            return
        
        print("🚀 Starting stable real-time face recognition...")
        print("📹 Using external webcam (camera 1)")
        print("⏱️  Detections are stabilized over 2-3 seconds")
        print("🔄 Press 'q' to quit")
        
        # Try external webcam first
        video_capture = cv2.VideoCapture(camera_index)
        if not video_capture.isOpened():
            print(f"⚠️  Camera {camera_index} not available, trying camera 0...")
            video_capture = cv2.VideoCapture(0)
            if not video_capture.isOpened():
                print("❌ Error: Could not open any webcam")
                return
        
        print(f"✅ Using camera {camera_index}")
        
        frame_count = 0
        process_every = 3  # Process every 3rd frame
        
        while True:
            ret, frame = video_capture.read()
            if not ret:
                print("Failed to capture frame")
                break
            
            frame_count += 1
            current_time = time.time()
            
            # Process every nth frame
            if frame_count % process_every == 0:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)
                
                # Track current frame's face IDs
                current_face_ids = set()
                
                for i, (x, y, w, h) in enumerate(faces):
                    face_id = f"face_{x//50}_{y//50}"  # Rough position-based ID
                    current_face_ids.add(face_id)
                    
                    face = gray[y:y+h, x:x+w]
                    name, confidence = self.recognize_face(face)
                    
                    # Update detection history
                    is_stable, stable_name, stable_confidence = self.update_detection_history(
                        face_id, name, confidence, current_time)
                    
                    # Draw based on stability
                    if is_stable and stable_name != "Unknown":
                        color = (0, 255, 0)  # Green for stable detection
                        display_name = stable_name
                        display_confidence = stable_confidence
                        thickness = 3
                    elif name != "Unknown":
                        color = (0, 255, 255)  # Yellow for unstable but recognized
                        display_name = name
                        display_confidence = confidence
                        thickness = 2
                    else:
                        color = (0, 0, 255)  # Red for unknown
                        display_name = "Unknown"
                        display_confidence = 0
                        thickness = 2
                    
                    # Draw rectangle and label
                    cv2.rectangle(frame, (x, y), (x+w, y+h), color, thickness)
                    cv2.rectangle(frame, (x, y+h-35), (x+w, y+h), color, cv2.FILLED)
                    
                    label = display_name
                    if display_confidence > 0:
                        label += f" ({display_confidence:.1f}%)"
                    
                    cv2.putText(frame, label, (x+6, y+h-6), 
                               cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
                
                # Cleanup old detections
                self.cleanup_old_detections(current_time)
            
            # Add status text
            status_text = f"Faces: {len(self.detection_history)} | Stable: {sum(1 for h in self.detection_history.values() if h.get('stable_name'))}"
            cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow('Stable Face Recognition', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        video_capture.release()
        cv2.destroyAllWindows()
        print("🛑 Face recognition stopped.")

def main():
    print("🎯 Stable Face Recognition System")
    print("=" * 40)
    
    fr_system = StableFaceRecognition()
    
    if not fr_system.load_dataset():
        print("❌ Failed to load dataset!")
        return
    
    unique_names = list(set(fr_system.known_names))
    print(f"\n✅ Loaded faces for: {', '.join(unique_names)}")
    print(f"📊 Total face samples: {len(fr_system.known_faces)}")
    
    print("\n🚀 Starting real-time recognition...")
    print("💡 Features:")
    print("   - Uses external webcam (camera 1)")
    print("   - Stable detection (2-3 second confirmation)")
    print("   - Reduced flickering")
    print("   - Color-coded confidence levels")
    
    input("\nPress Enter to start...")
    fr_system.real_time_recognition()

if __name__ == "__main__":
    main()
