import face_recognition
import cv2
import os
import numpy as np
import pickle
from pathlib import Path

class FaceRecognitionSystem:
    def __init__(self, dataset_path="./dataset", encodings_file="face_encodings.pkl"):
        self.dataset_path = dataset_path
        self.encodings_file = encodings_file
        self.known_face_encodings = []
        self.known_face_names = []
        
    def load_dataset_and_encode(self):
        """Load images from dataset and create face encodings"""
        print("Loading dataset and creating face encodings...")
        
        # Get all image files from dataset
        dataset_dir = Path(self.dataset_path)
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        
        for image_path in dataset_dir.iterdir():
            if image_path.suffix.lower() in image_extensions:
                # Extract name from filename (assuming format: name_number.extension)
                name = image_path.stem.rsplit('_', 1)[0]
                
                print(f"Processing {image_path.name} for {name}")

                # Load image using OpenCV first
                cv_image = cv2.imread(str(image_path))
                if cv_image is None:
                    print(f"✗ Could not load {image_path.name}")
                    continue

                # Convert BGR to RGB for face_recognition
                image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
                
                # Get face encodings
                face_encodings = face_recognition.face_encodings(image)
                
                if face_encodings:
                    # Use the first face found in the image
                    face_encoding = face_encodings[0]
                    self.known_face_encodings.append(face_encoding)
                    self.known_face_names.append(name)
                    print(f"✓ Encoded face for {name}")
                else:
                    print(f"✗ No face found in {image_path.name}")
        
        print(f"Total faces encoded: {len(self.known_face_encodings)}")
        
    def save_encodings(self):
        """Save face encodings to file"""
        data = {
            'encodings': self.known_face_encodings,
            'names': self.known_face_names
        }
        with open(self.encodings_file, 'wb') as f:
            pickle.dump(data, f)
        print(f"Face encodings saved to {self.encodings_file}")
    
    def load_encodings(self):
        """Load face encodings from file"""
        if os.path.exists(self.encodings_file):
            with open(self.encodings_file, 'rb') as f:
                data = pickle.load(f)
                self.known_face_encodings = data['encodings']
                self.known_face_names = data['names']
            print(f"Loaded {len(self.known_face_encodings)} face encodings from {self.encodings_file}")
            return True
        return False
    
    def recognize_faces_in_image(self, image_path):
        """Recognize faces in a single image"""
        # Load the image using OpenCV
        image = cv2.imread(image_path)
        if image is None:
            print(f"Could not load image: {image_path}")
            return None

        # Convert BGR to RGB for face_recognition
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Find face locations and encodings
        face_locations = face_recognition.face_locations(rgb_image)
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
        
        # image is already in BGR format from cv2.imread
        
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Compare with known faces
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"
            
            # Use the known face with the smallest distance
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            
            if matches[best_match_index] and face_distances[best_match_index] < 0.6:
                name = self.known_face_names[best_match_index]
                confidence = 1 - face_distances[best_match_index]
            else:
                confidence = 0
            
            # Draw rectangle and label
            cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.rectangle(image, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
            
            label = f"{name} ({confidence:.2f})"
            cv2.putText(image, label, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
        
        return image
    
    def real_time_recognition(self, camera_index=0):
        """Real-time face recognition using webcam"""
        print("Starting real-time face recognition...")
        print("Press 'q' to quit")
        
        # Initialize webcam
        video_capture = cv2.VideoCapture(camera_index)
        
        if not video_capture.isOpened():
            print("Error: Could not open webcam")
            return
        
        # Process every other frame to speed up
        process_this_frame = True
        
        while True:
            ret, frame = video_capture.read()
            if not ret:
                print("Failed to capture frame")
                break
            
            # Resize frame for faster processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            if process_this_frame:
                # Find face locations and encodings
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                
                face_names = []
                face_confidences = []
                
                for face_encoding in face_encodings:
                    # Compare with known faces
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                    name = "Unknown"
                    confidence = 0
                    
                    # Use the known face with the smallest distance
                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    
                    if matches[best_match_index] and face_distances[best_match_index] < 0.6:
                        name = self.known_face_names[best_match_index]
                        confidence = 1 - face_distances[best_match_index]
                    
                    face_names.append(name)
                    face_confidences.append(confidence)
            
            process_this_frame = not process_this_frame
            
            # Display results
            for (top, right, bottom, left), name, confidence in zip(face_locations, face_names, face_confidences):
                # Scale back up face locations
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4
                
                # Choose color based on recognition
                color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                
                # Draw rectangle around face
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                
                # Draw label background
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                
                # Draw label text
                label = f"{name}"
                if confidence > 0:
                    label += f" ({confidence:.2f})"
                
                cv2.putText(frame, label, (left + 6, bottom - 6), 
                           cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
            
            # Display frame
            cv2.imshow('Face Recognition', frame)
            
            # Break on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Cleanup
        video_capture.release()
        cv2.destroyAllWindows()
        print("Face recognition stopped.")

def main():
    # Initialize the face recognition system
    fr_system = FaceRecognitionSystem()
    
    # Try to load existing encodings, if not found, create new ones
    if not fr_system.load_encodings():
        print("No existing encodings found. Creating new encodings from dataset...")
        fr_system.load_dataset_and_encode()
        fr_system.save_encodings()
    
    print("\nFace Recognition System Ready!")
    print("Choose an option:")
    print("1. Real-time recognition (webcam)")
    print("2. Recognize faces in an image")
    print("3. Re-encode dataset")
    print("4. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            fr_system.real_time_recognition()
        elif choice == '2':
            image_path = input("Enter path to image: ").strip()
            if os.path.exists(image_path):
                result_image = fr_system.recognize_faces_in_image(image_path)
                cv2.imshow('Face Recognition Result', result_image)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            else:
                print("Image not found!")
        elif choice == '3':
            fr_system.load_dataset_and_encode()
            fr_system.save_encodings()
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
