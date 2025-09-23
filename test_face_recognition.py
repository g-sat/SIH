import face_recognition
import cv2
import os
from pathlib import Path

def test_dataset():
    """Test if we can load and process images from the dataset"""
    print("=== Testing Dataset ===")
    
    dataset_path = "./dataset"
    if not os.path.exists(dataset_path):
        print("❌ Dataset folder not found!")
        return False
    
    dataset_dir = Path(dataset_path)
    image_files = list(dataset_dir.glob("*.png")) + list(dataset_dir.glob("*.jpg"))
    
    print(f"Found {len(image_files)} images in dataset")
    
    if len(image_files) == 0:
        print("❌ No images found in dataset!")
        return False
    
    # Test loading a few images
    successful_loads = 0
    face_detections = 0
    
    for i, image_path in enumerate(image_files[:5]):  # Test first 5 images
        try:
            print(f"Testing {image_path.name}...")

            # Load image using OpenCV first
            cv_image = cv2.imread(str(image_path))
            if cv_image is None:
                print(f"  ❌ Could not load {image_path.name}")
                continue

            # Convert BGR to RGB for face_recognition
            image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
            successful_loads += 1
            
            # Try to find faces
            face_locations = face_recognition.face_locations(image)
            if face_locations:
                face_detections += 1
                print(f"  ✅ Found {len(face_locations)} face(s)")
            else:
                print(f"  ⚠️  No faces detected")
                
        except Exception as e:
            print(f"  ❌ Error loading {image_path.name}: {e}")
    
    print(f"\nResults:")
    print(f"  Successfully loaded: {successful_loads}/{min(5, len(image_files))} images")
    print(f"  Face detections: {face_detections}/{min(5, len(image_files))} images")
    
    return successful_loads > 0 and face_detections > 0

def test_libraries():
    """Test if required libraries are working"""
    print("=== Testing Libraries ===")
    
    try:
        import face_recognition
        print("✅ face_recognition imported successfully")
    except ImportError as e:
        print(f"❌ face_recognition import failed: {e}")
        return False
    
    try:
        import cv2
        print("✅ cv2 (OpenCV) imported successfully")
        print(f"   OpenCV version: {cv2.__version__}")
    except ImportError as e:
        print(f"❌ cv2 import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ numpy imported successfully")
    except ImportError as e:
        print(f"❌ numpy import failed: {e}")
        return False
    
    return True

def test_camera():
    """Test if camera is accessible"""
    print("=== Testing Camera ===")
    
    # Try different camera indices
    for camera_index in [0, 1, 2]:
        cap = cv2.VideoCapture(camera_index)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"✅ Camera {camera_index} is working")
                print(f"   Frame size: {frame.shape[1]}x{frame.shape[0]}")
                cap.release()
                return True
            else:
                print(f"⚠️  Camera {camera_index} opened but can't read frames")
        cap.release()
    
    print("❌ No working camera found")
    return False

def quick_face_test():
    """Quick test of face recognition on one image"""
    print("=== Quick Face Recognition Test ===")
    
    dataset_path = "./dataset"
    dataset_dir = Path(dataset_path)
    image_files = list(dataset_dir.glob("*.png")) + list(dataset_dir.glob("*.jpg"))
    
    if not image_files:
        print("❌ No images found for testing")
        return False
    
    # Use the first image as both training and test (just for verification)
    test_image_path = image_files[0]
    print(f"Testing with: {test_image_path.name}")
    
    try:
        # Load image using OpenCV first
        cv_image = cv2.imread(str(test_image_path))
        if cv_image is None:
            print("❌ Could not load test image")
            return False

        # Convert BGR to RGB for face_recognition
        image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        face_encodings = face_recognition.face_encodings(image)
        
        if not face_encodings:
            print("❌ No face found in test image")
            return False
        
        print(f"✅ Found face encoding (shape: {face_encodings[0].shape})")
        
        # Test face comparison (should match itself)
        face_locations = face_recognition.face_locations(image)
        print(f"✅ Face location detected: {face_locations[0] if face_locations else 'None'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in face recognition test: {e}")
        return False

def main():
    print("🔍 Face Recognition System Test\n")
    
    # Run all tests
    tests = [
        ("Libraries", test_libraries),
        ("Dataset", test_dataset),
        ("Camera", test_camera),
        ("Face Recognition", quick_face_test)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        results[test_name] = test_func()
        print(f"{'='*50}")
    
    # Summary
    print(f"\n{'='*50}")
    print("🏁 TEST SUMMARY")
    print(f"{'='*50}")
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if not passed:
            all_passed = False
    
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🎉 Your face recognition system is ready to use!")
        print("Run 'python quick_face_recognition.py' to start recognizing faces!")
    else:
        print("\n⚠️  Please fix the failing tests before using the system.")

if __name__ == "__main__":
    main()
