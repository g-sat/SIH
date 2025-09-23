import face_recognition
import cv2
import os
import numpy as np
from pathlib import Path

def load_known_faces(dataset_path="./dataset"):
    """Load and encode all faces from the dataset"""
    known_face_encodings = []
    known_face_names = []
    
    print("Loading faces from dataset...")
    
    # Get all image files
    dataset_dir = Path(dataset_path)
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    
    for image_path in dataset_dir.iterdir():
        if image_path.suffix.lower() in image_extensions:
            # Extract name from filename (format: name_number.extension)
            name = image_path.stem.rsplit('_', 1)[0]
            
            print(f"Loading {image_path.name} for {name}")

            # Load image using OpenCV first, then convert for face_recognition
            cv_image = cv2.imread(str(image_path))
            if cv_image is None:
                print(f"✗ Could not load {image_path.name}")
                continue

            # Convert BGR to RGB for face_recognition
            rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
            face_encodings = face_recognition.face_encodings(rgb_image)
            
            if face_encodings:
                known_face_encodings.append(face_encodings[0])
                known_face_names.append(name)
                print(f"✓ Loaded {name}")
            else:
                print(f"✗ No face found in {image_path.name}")
    
    print(f"Total faces loaded: {len(known_face_encodings)}")
    return known_face_encodings, known_face_names

def recognize_faces_webcam(known_face_encodings, known_face_names):
    """Real-time face recognition using webcam"""
    print("\nStarting webcam face recognition...")
    print("Press 'q' to quit")
    
    # Try different camera indices
    video_capture = None
    for camera_index in [1]:
        video_capture = cv2.VideoCapture(camera_index)
        if video_capture.isOpened():
            print(f"Using camera {camera_index}")
            break
        video_capture.release()
    
    if not video_capture or not video_capture.isOpened():
        print("Error: Could not open any camera")
        return
    
    # Variables for processing optimization
    process_this_frame = True
    face_locations = []
    face_encodings = []
    face_names = []
    
    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("Failed to capture frame")
            break
        
        # Resize frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Only process every other frame to save time
        if process_this_frame:
            # Find all face locations and encodings in the current frame
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            
            face_names = []
            for face_encoding in face_encodings:
                # See if the face matches any known faces
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"
                confidence = 0
                
                # Use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                
                if matches[best_match_index] and face_distances[best_match_index] < 0.6:
                    name = known_face_names[best_match_index]
                    confidence = (1 - face_distances[best_match_index]) * 100
                
                face_names.append((name, confidence))
        
        process_this_frame = not process_this_frame
        
        # Display the results
        for (top, right, bottom, left), (name, confidence) in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            
            # Choose color based on recognition
            if name == "Unknown":
                color = (0, 0, 255)  # Red for unknown
            else:
                color = (0, 255, 0)  # Green for known
            
            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            
            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            
            # Create label text
            if confidence > 0:
                label = f"{name} ({confidence:.1f}%)"
            else:
                label = name
            
            cv2.putText(frame, label, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
        
        # Display the resulting image
        cv2.imshow('Face Recognition', frame)
        
        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()

def test_with_image(known_face_encodings, known_face_names, image_path):
    """Test face recognition with a single image"""
    if not os.path.exists(image_path):
        print(f"Image {image_path} not found!")
        return
    
    print(f"Testing with image: {image_path}")

    # Load the test image using OpenCV
    test_image = cv2.imread(image_path)
    if test_image is None:
        print(f"Could not load image: {image_path}")
        return

    # Convert BGR to RGB for face_recognition
    test_image_rgb = cv2.cvtColor(test_image, cv2.COLOR_BGR2RGB)
    
    # Find faces in the test image
    face_locations = face_recognition.face_locations(test_image_rgb)
    face_encodings = face_recognition.face_encodings(test_image_rgb, face_locations)
    
    print(f"Found {len(face_locations)} face(s) in the image")
    
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Compare with known faces
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"
        confidence = 0
        
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        
        if matches[best_match_index] and face_distances[best_match_index] < 0.6:
            name = known_face_names[best_match_index]
            confidence = (1 - face_distances[best_match_index]) * 100
        
        print(f"Detected: {name} (confidence: {confidence:.1f}%)")
        
        # Draw rectangle and label
        color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
        cv2.rectangle(test_image_rgb, (left, top), (right, bottom), color, 2)
        cv2.rectangle(test_image_rgb, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
        
        label = f"{name} ({confidence:.1f}%)" if confidence > 0 else name
        cv2.putText(test_image, label, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
    
    # Convert back to BGR for display
    test_image = cv2.cvtColor(test_image_rgb, cv2.COLOR_RGB2BGR)

    # Show the result
    cv2.imshow('Face Recognition Test', test_image)
    cv2.waitKey(1)
    cv2.destroyAllWindows()

def main():
    print("=== Face Recognition System ===")
    
    # Load known faces from dataset
    known_face_encodings, known_face_names = load_known_faces()
    
    if not known_face_encodings:
        print("No faces found in dataset! Please check your dataset folder.")
        return
    
    print(f"\nLoaded faces for: {', '.join(set(known_face_names))}")
    
    while True:
        print("\nChoose an option:")
        print("1. Start webcam recognition")
        print("2. Test with an image")
        print("3. Exit")
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == '1':
            recognize_faces_webcam(known_face_encodings, known_face_names)
        elif choice == '2':
            image_path = input("Enter image path: ").strip()
            test_with_image(known_face_encodings, known_face_names, image_path)
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()
