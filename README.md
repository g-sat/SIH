# Face Recognition System

A comprehensive face recognition system with multiple implementations:
1. **Simple Face Recognition** (`simple_face_recognition.py`) - Working OpenCV-based solution ✅
2. **Advanced Face Recognition** (`face_recognition_system.py`) - Uses face_recognition library (has dlib issues)
3. **Quick Face Recognition** (`quick_face_recognition.py`) - Lightweight implementation (has dlib issues)

## Features

- 🎯 **Real-time face recognition** using webcam
- 📸 **Image-based face recognition** for testing with photos
- 💾 **Automatic face encoding** from your dataset
- 🏷️ **Name labeling** based on filename patterns
- ⚡ **Optimized performance** with frame skipping and resizing
- 🎨 **Visual feedback** with bounding boxes and confidence scores

## Dataset Structure

Your dataset should be organized as follows:
```
dataset/
├── person1_1.png
├── person1_2.png
├── person1_3.png
├── person2_1.png
├── person2_2.png
└── ...
```

The system extracts names from filenames using the pattern: `name_number.extension`

## Current Dataset

Your dataset contains faces for:
- Keertana (5 images)
- Mahesh (5 images)
- abhinav (5 images)
- asritha (5 images)
- harsha (5 images)
- koushal (5 images)
- praseen (5 images)
- sathwik (5 images)
- sathwik_k (5 images)
- sudheer (5 images)
- venkat (5 images)

## Installation

All required dependencies are already installed in your environment:
- `face_recognition`
- `opencv-python`
- `dlib`
- `numpy`

## Usage

### 🚀 Recommended: Simple Face Recognition (Working Solution)

Use the simple OpenCV-based solution that's confirmed to work:

```bash
python simple_face_recognition.py
```

Options:
1. **Real-time recognition (webcam)**: Live face detection and recognition
2. **Recognize faces in an image**: Test with a specific image file
3. **Test system**: Verify the system is working correctly
4. **Exit**: Close the application

### 🧪 Alternative: Test Other Implementations

If you want to try the face_recognition library versions (may have dlib issues):

```bash
python test_face_recognition.py  # Test all systems
python quick_face_recognition.py  # Quick implementation
python face_recognition_system.py  # Full-featured system
```

### 3. Advanced Usage

For more features and options, use the full system:

```bash
python face_recognition_system.py
```

Additional features:
- Save/load face encodings for faster startup
- Re-encode dataset when adding new faces
- Batch processing capabilities

## How It Works

1. **Face Encoding**: The system loads all images from the dataset and creates 128-dimensional face encodings using the `face_recognition` library
2. **Face Detection**: Uses HOG (Histogram of Oriented Gradients) or CNN models to detect faces in images/video
3. **Face Recognition**: Compares detected face encodings with known encodings using Euclidean distance
4. **Labeling**: Assigns names based on the closest match (if confidence > 60%)

## Performance Tips

- **Frame Processing**: The system processes every other frame for better performance
- **Image Resizing**: Frames are resized to 1/4 size for faster processing
- **Distance Threshold**: Faces with distance > 0.6 are marked as "Unknown"
- **Multiple Images**: Having 3-5 images per person improves recognition accuracy

## Controls

### Webcam Mode
- **'q'**: Quit the application
- **ESC**: Alternative quit method

### Image Mode
- **Any key**: Close the result window

## Troubleshooting

### Common Issues

1. **No camera found**
   - Check if your webcam is connected
   - Try different camera indices (0, 1, 2)
   - Ensure no other application is using the camera

2. **Poor recognition accuracy**
   - Add more images per person (3-5 recommended)
   - Ensure good lighting in dataset images
   - Use images with different angles and expressions

3. **Slow performance**
   - Reduce camera resolution
   - Increase frame skipping interval
   - Use smaller face detection model

### Error Messages

- **"No face found in image"**: The image doesn't contain a detectable face
- **"Could not open webcam"**: Camera access issue
- **"Failed to capture frame"**: Camera connection problem

## Adding New People

1. Add new images to the `dataset/` folder following the naming convention: `name_number.extension`
2. Run the system and choose "Re-encode dataset" option
3. The system will automatically include the new person in recognition

## Technical Details

- **Face Detection**: Uses dlib's face detection algorithms
- **Face Recognition**: 128-dimensional face embeddings
- **Distance Metric**: Euclidean distance for face comparison
- **Confidence Threshold**: 0.6 (adjustable)
- **Image Formats**: Supports PNG, JPG, JPEG, BMP

## File Structure

```
├── face_recognition_system.py    # Full-featured system
├── quick_face_recognition.py     # Simple, fast implementation
├── test_face_recognition.py      # System testing script
├── dataset/                      # Your face images
├── face_encodings.pkl           # Saved encodings (auto-generated)
└── README.md                    # This file
```

## Next Steps

1. **Test the system**: Run `python test_face_recognition.py`
2. **Try quick recognition**: Run `python quick_face_recognition.py`
3. **Add more people**: Add images to dataset and re-encode
4. **Customize settings**: Modify confidence thresholds and performance parameters

Enjoy your face recognition system! 🎉
