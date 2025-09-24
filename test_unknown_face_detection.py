#!/usr/bin/env python3
"""
Test script to demonstrate unknown face detection
"""

import cv2
import numpy as np
from stable_face_recognition_with_attendance import StableFaceRecognitionWithAttendance

def test_unknown_face_detection():
    """Test the unknown face detection system"""
    print('🔍 Testing Unknown Face Detection System')
    print('=' * 50)
    
    # Initialize the face recognition system
    fr_system = StableFaceRecognitionWithAttendance()
    
    if len(fr_system.known_faces) == 0:
        print("❌ No faces loaded! Please check your dataset.")
        return
    
    print(f"✅ Loaded {len(fr_system.known_faces)} faces from dataset")
    print(f"📊 Known people: {', '.join(set(fr_system.known_names))}")
    print(f"🎯 Recognition threshold: {fr_system.recognition_threshold:.1%}")
    print(f"📝 Attendance threshold: {fr_system.confidence_threshold:.1%}")
    
    # Test with a known face (first face in dataset)
    print("\n🧪 Testing with KNOWN face...")
    known_face = fr_system.known_faces[0]
    known_name_expected = fr_system.known_names[0]
    
    name, confidence = fr_system.recognize_face(known_face)
    print(f"   Expected: {known_name_expected}")
    print(f"   Result: {name} ({confidence:.1%})")
    
    if name == known_name_expected:
        print("   ✅ Known face correctly identified")
    else:
        print("   ⚠️  Known face not recognized correctly")
    
    # Test with a random noise image (should be unknown)
    print("\n🧪 Testing with UNKNOWN face (random noise)...")
    unknown_face = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
    
    name, confidence = fr_system.recognize_face(unknown_face)
    print(f"   Result: {name} ({confidence:.1%})")
    
    if name == "Unknown":
        print("   ✅ Unknown face correctly identified as Unknown")
    else:
        print("   ⚠️  Unknown face incorrectly identified as known person")
    
    # Test with a very low confidence match
    print("\n🧪 Testing with LOW CONFIDENCE face...")
    # Create a heavily distorted version of a known face
    distorted_face = cv2.GaussianBlur(known_face, (15, 15), 0)
    distorted_face = cv2.addWeighted(distorted_face, 0.3, np.random.randint(0, 255, known_face.shape, dtype=np.uint8), 0.7, 0)
    
    name, confidence = fr_system.recognize_face(distorted_face)
    print(f"   Result: {name} ({confidence:.1%})")
    
    if confidence < fr_system.recognition_threshold:
        print("   ✅ Low confidence correctly marked as Unknown")
    else:
        print(f"   ⚠️  Low confidence still recognized as {name}")
    
    print("\n📊 System Behavior Summary:")
    print(f"   🎯 Faces with confidence ≥ {fr_system.recognition_threshold:.1%}: Recognized as known person")
    print(f"   🎯 Faces with confidence < {fr_system.recognition_threshold:.1%}: Marked as 'Unknown'")
    print(f"   📝 Only faces with confidence ≥ {fr_system.confidence_threshold:.1%}: Get attendance recorded")
    print(f"   ❌ Unknown faces: NO attendance recorded (security feature)")
    
    print("\n🎉 Unknown Face Detection Test Complete!")
    print("\n💡 In the live system:")
    print("   - Known faces appear with GREEN boxes and names")
    print("   - Unknown faces appear with RED boxes and 'UNKNOWN PERSON'")
    print("   - Only known faces with sufficient confidence get attendance recorded")
    print("   - Unknown faces are logged but NO attendance is recorded")

if __name__ == "__main__":
    test_unknown_face_detection()
