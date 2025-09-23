import cv2
import os
import numpy as np
import pickle
from pathlib import Path

class OpenCVFaceRecognition:
    def __init__(self, dataset_path="./dataset", model_file="face_model.yml"):
        self.dataset_path = dataset_path
        self.model_file = model_file
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.label_to_name = {}
        self.name_to_label = {}
        self.is_trained = False
        
    def load_dataset_and_train(self):
        """Load images from dataset and train the face recognizer"""
        print("Loading dataset and training face recognizer...")
        
        faces = []
        labels = []
        current_label = 0
        
        # Get all image files from dataset
        dataset_dir = Path(self.dataset_path)
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        
        # Group images by person name
        name_images = {}
        for image_path in dataset_dir.iterdir():
            if image_path.suffix.lower() in image_extensions:
                # Extract name from filename (assuming format: name_number.extension)
                name = image_path.stem.rsplit('_', 1)[0]
                if name not in name_images:
                    name_images[name] = []
                name_images[name].append(image_path)
        
        print(f"Found {len(name_images)} people in dataset")
        
        for name, image_paths in name_images.items():
            if name not in self.name_to_label:
                self.name_to_label[name] = current_label
                self.label_to_name[current_label] = name
                current_label += 1
            
            label = self.name_to_label[name]
            print(f"Processing {len(image_paths)} images for {name} (label: {label})")
            
            for image_path in image_paths:
                # Load image
                image = cv2.imread(str(image_path))
                if image is None:
                    print(f"✗ Could not load {image_path.name}")
                    continue
                
                # Convert to grayscale
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                
                # Detect faces
                face_rects = self.face_cascade.detectMultiScale(gray, 1.1, 5)
                
                for (x, y, w, h) in face_rects:
                    # Extract face region
                    face = gray[y:y+h, x:x+w]
                    # Resize to standard size
                    face = cv2.resize(face, (100, 100))
                    
                    faces.append(face)
                    labels.append(label)
                    print(f"✓ Added face from {image_path.name}")
                    break  # Use only the first face found
        
        if len(faces) == 0:
            print("❌ No faces found in dataset!")
            return False
        
        print(f"Training with {len(faces)} face samples...")
        
        # Train the recognizer
        self.face_recognizer.train(faces, np.array(labels))
        self.is_trained = True
        
        print(f"✅ Training completed!")
        return True
    
    def save_model(self):
        """Save the trained model and labels"""
        if not self.is_trained:
            print("❌ Model not trained yet!")
            return False
        
        # Save the face recognizer model
        self.face_recognizer.save(self.model_file)
        
        # Save the label mappings
        label_file = self.model_file.replace('.yml', '_labels.pkl')
        with open(label_file, 'wb') as f:
            pickle.dump({
                'label_to_name': self.label_to_name,
                'name_to_label': self.name_to_label
            }, f)
        
        print(f"✅ Model saved to {self.model_file}")
        return True
    
    def load_model(self):
        """Load the trained model and labels"""
        if not os.path.exists(self.model_file):
            return False
        
        # Load the face recognizer model
        self.face_recognizer.read(self.model_file)
        
        # Load the label mappings
        label_file = self.model_file.replace('.yml', '_labels.pkl')
        if os.path.exists(label_file):
            with open(label_file, 'rb') as f:
                data = pickle.load(f)
                self.label_to_name = data['label_to_name']
                self.name_to_label = data['name_to_label']
        
        self.is_trained = True
        print(f"✅ Model loaded from {self.model_file}")
        return True
    
    def recognize_faces_in_image(self, image_path):
        """Recognize faces in a single image"""
        if not self.is_trained:
            print("❌ Model not trained yet!")
            return None
        
        # Load the image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Could not load image: {image_path}")
            return None
        
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        face_rects = self.face_cascade.detectMultiScale(gray, 1.1, 5)
        
        print(f"Found {len(face_rects)} face(s) in the image")
        
        for (x, y, w, h) in face_rects:
            # Extract and resize face
            face = gray[y:y+h, x:x+w]
            face = cv2.resize(face, (100, 100))
            
            # Recognize face
            label, confidence = self.face_recognizer.predict(face)
            
            # Get name (lower confidence = better match)
            if confidence < 100:  # Threshold for recognition
                name = self.label_to_name.get(label, "Unknown")
                confidence_percent = max(0, 100 - confidence)
            else:
                name = "Unknown"
                confidence_percent = 0
            
            print(f"Detected: {name} (confidence: {confidence_percent:.1f}%)")
            
            # Draw rectangle and label
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(image, (x, y), (x+w, y+h), color, 2)
            cv2.rectangle(image, (x, y+h-35), (x+w, y+h), color, cv2.FILLED)
            
            label_text = f"{name} ({confidence_percent:.1f}%)" if confidence_percent > 0 else name
            cv2.putText(image, label_text, (x+6, y+h-6), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
        
        return image
    
    def real_time_recognition(self, camera_index=0):
        """Real-time face recognition using webcam"""
        if not self.is_trained:
            print("❌ Model not trained yet!")
            return
        
        print("Starting real-time face recognition...")
        print("Press 'q' to quit")
        
        # Initialize webcam
        video_capture = cv2.VideoCapture(camera_index)
        
        if not video_capture.isOpened():
            print("Error: Could not open webcam")
            return
        
        while True:
            ret, frame = video_capture.read()
            if not ret:
                print("Failed to capture frame")
                break
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            face_rects = self.face_cascade.detectMultiScale(gray, 1.1, 5)
            
            for (x, y, w, h) in face_rects:
                # Extract and resize face
                face = gray[y:y+h, x:x+w]
                face = cv2.resize(face, (100, 100))
                
                # Recognize face
                label, confidence = self.face_recognizer.predict(face)
                
                # Get name (lower confidence = better match)
                if confidence < 100:  # Threshold for recognition
                    name = self.label_to_name.get(label, "Unknown")
                    confidence_percent = max(0, 100 - confidence)
                else:
                    name = "Unknown"
                    confidence_percent = 0
                
                # Choose color based on recognition
                color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                
                # Draw rectangle around face
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                
                # Draw label background
                cv2.rectangle(frame, (x, y+h-35), (x+w, y+h), color, cv2.FILLED)
                
                # Draw label text
                label_text = f"{name}"
                if confidence_percent > 0:
                    label_text += f" ({confidence_percent:.1f}%)"
                
                cv2.putText(frame, label_text, (x+6, y+h-6), 
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
    fr_system = OpenCVFaceRecognition()
    
    # Try to load existing model, if not found, train new one
    if not fr_system.load_model():
        print("No existing model found. Training new model from dataset...")
        if fr_system.load_dataset_and_train():
            fr_system.save_model()
        else:
            print("❌ Failed to train model!")
            return
    
    print("\nOpenCV Face Recognition System Ready!")
    print("Choose an option:")
    print("1. Real-time recognition (webcam)")
    print("2. Recognize faces in an image")
    print("3. Re-train model")
    print("4. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            fr_system.real_time_recognition()
        elif choice == '2':
            image_path = input("Enter path to image: ").strip()
            if os.path.exists(image_path):
                result_image = fr_system.recognize_faces_in_image(image_path)
                if result_image is not None:
                    cv2.imshow('Face Recognition Result', result_image)
                    cv2.waitKey(0)
                    cv2.destroyAllWindows()
            else:
                print("Image not found!")
        elif choice == '3':
            if fr_system.load_dataset_and_train():
                fr_system.save_model()
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
