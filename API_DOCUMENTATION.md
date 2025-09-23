# Face Recognition API Documentation

## 🚀 Overview

This API provides three main functionalities:
1. **Video Capturing** - Record video from webcam
2. **Video to Frames** - Extract frames from recorded video
3. **Face Recognition** - Process frames and recognize faces

## 📦 Installation

1. **Install dependencies:**
   ```bash
   pip install -r api_requirements.txt
   ```

2. **Start the API server:**
   ```bash
   python face_recognition_api.py
   ```

3. **Test the API:**
   ```bash
   python api_client.py
   ```

## 🌐 API Endpoints

### Base URL: `http://localhost:5000`

---

### 1. Health Check
**GET** `/api/health`

Check if the API is running and face recognition is loaded.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "face_recognition_loaded": true
}
```

---

### 2. Load Dataset
**POST** `/api/load-dataset`

Load the face recognition dataset from the dataset directory.

**Response:**
```json
{
  "success": true,
  "message": "Loaded 33 faces",
  "faces_loaded": 33,
  "unique_people": 11
}
```

---

### 3. Start Recording
**POST** `/api/start-recording`

Start video recording from webcam.

**Request Body:**
```json
{
  "camera_index": 1,
  "duration": 10
}
```

**Response:**
```json
{
  "success": true,
  "message": "Recording started for 10 seconds",
  "camera_index": 1
}
```

---

### 4. Stop Recording
**POST** `/api/stop-recording`

Stop the current video recording.

**Response:**
```json
{
  "success": true,
  "message": "Recording stopped",
  "frames_captured": 300
}
```

---

### 5. Recording Status
**GET** `/api/recording-status`

Get the current recording status.

**Response:**
```json
{
  "is_recording": true,
  "frames_captured": 150,
  "timestamp": "2024-01-01T12:00:00"
}
```

---

### 6. Extract Frames
**POST** `/api/extract-frames`

Extract frames from the recorded video.

**Request Body:**
```json
{
  "frame_interval": 5
}
```

**Response:**
```json
{
  "success": true,
  "message": "Extracted 60 frames",
  "frames": [
    {
      "frame_number": 0,
      "filename": "frame_0000.jpg",
      "filepath": "./extracted_frames/frame_0000.jpg"
    }
  ],
  "frames_directory": "./extracted_frames"
}
```

---

### 7. Process Single Frame
**POST** `/api/process-frame`

Process a single frame for face recognition.

**Three input methods:**

#### Method 1: File Upload
```bash
curl -X POST -F "frame_file=@image.jpg" http://localhost:5000/api/process-frame
```

#### Method 2: File Path
```json
{
  "frame_path": "./extracted_frames/frame_0000.jpg"
}
```

#### Method 3: Base64 Image
```json
{
  "frame_base64": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

**Response:**
```json
{
  "success": true,
  "detections": [
    {
      "name": "sathwik",
      "confidence": 85.5,
      "bbox": {
        "x": 100,
        "y": 50,
        "width": 120,
        "height": 120
      }
    }
  ],
  "faces_found": 1,
  "annotated_frame_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "timestamp": "2024-01-01T12:00:00"
}
```

---

### 8. Process All Frames
**POST** `/api/process-all-frames`

Process all extracted frames for face recognition.

**Response:**
```json
{
  "success": true,
  "message": "Processed 60 frames",
  "results": [
    {
      "frame_file": "frame_0000.jpg",
      "detections": [
        {
          "name": "sathwik",
          "confidence": 85.5,
          "bbox": {"x": 100, "y": 50, "width": 120, "height": 120}
        }
      ],
      "faces_found": 1,
      "annotated_frame": "./extracted_frames/annotated_frame_0000.jpg"
    }
  ],
  "total_faces_detected": 45
}
```

## 🔄 Complete Workflow

### 1. Using Python Client

```python
from api_client import FaceRecognitionAPIClient

client = FaceRecognitionAPIClient()

# 1. Load dataset
result = client.load_dataset()
print(result)

# 2. Start recording
result = client.start_recording(camera_index=1, duration=10)
print(result)

# 3. Wait for recording to complete
import time
time.sleep(11)

# 4. Extract frames
result = client.extract_frames(frame_interval=5)
print(result)

# 5. Process all frames
result = client.process_all_frames()
print(result)
```

### 2. Using cURL Commands

```bash
# 1. Health check
curl http://localhost:5000/api/health

# 2. Load dataset
curl -X POST http://localhost:5000/api/load-dataset

# 3. Start recording
curl -X POST -H "Content-Type: application/json" \
  -d '{"camera_index": 1, "duration": 10}' \
  http://localhost:5000/api/start-recording

# 4. Check status
curl http://localhost:5000/api/recording-status

# 5. Extract frames
curl -X POST -H "Content-Type: application/json" \
  -d '{"frame_interval": 5}' \
  http://localhost:5000/api/extract-frames

# 6. Process all frames
curl -X POST http://localhost:5000/api/process-all-frames
```

## 📁 Directory Structure

```
├── face_recognition_api.py      # Main API server
├── api_client.py               # Python client for testing
├── api_requirements.txt        # Dependencies
├── dataset/                    # Your face images
├── extracted_frames/           # Auto-created for frame extraction
│   ├── frame_0000.jpg         # Extracted frames
│   └── annotated_frame_0000.jpg # Processed frames with detections
└── API_DOCUMENTATION.md       # This file
```

## 🎯 Features

### Video Capturing API
- ✅ Start/stop recording from external webcam (camera 1)
- ✅ Configurable recording duration
- ✅ Real-time status monitoring
- ✅ Automatic fallback to camera 0

### Video to Frames API
- ✅ Extract frames at configurable intervals
- ✅ Save frames as individual JPG files
- ✅ Automatic directory management
- ✅ Frame numbering and metadata

### Face Recognition API
- ✅ Process single frames or batch process
- ✅ Multiple input methods (file, path, base64)
- ✅ Confidence scoring and bounding boxes
- ✅ Annotated output images
- ✅ Color-coded detection levels

## 🔧 Configuration

### Camera Settings
- Default external camera: index 1
- Fallback camera: index 0
- Recording FPS: ~30 frames per second

### Face Recognition Settings
- Confidence threshold: 60%
- Face detection: OpenCV Haar Cascade
- Recognition method: Template matching
- Supported formats: JPG, PNG, BMP

### API Settings
- Host: 0.0.0.0 (accessible from network)
- Port: 5000
- Debug mode: Enabled
- CORS: Enabled for cross-origin requests

## 🚨 Error Handling

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "Error description"
}
```

Common errors:
- Camera not available
- Dataset not loaded
- No frames to process
- Invalid image format
- Recording already in progress

## 🧪 Testing

Run the demo workflow:
```bash
python api_client.py
```

Choose option 1 for complete workflow test.

## 🔗 Integration Examples

### JavaScript/Web Integration
```javascript
// Start recording
fetch('http://localhost:5000/api/start-recording', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({camera_index: 1, duration: 10})
})
.then(response => response.json())
.then(data => console.log(data));
```

### Python Integration
```python
import requests

# Process a frame
with open('image.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/api/process-frame',
        files={'frame_file': f}
    )
    result = response.json()
    print(result)
```

## 📊 Performance

- **Recording**: ~30 FPS capture rate
- **Frame extraction**: ~100 frames/second
- **Face recognition**: ~5-10 frames/second
- **Memory usage**: ~200MB for typical dataset

## 🎉 Ready to Use!

Your face recognition system is now available as a REST API! 

Start the server and begin capturing, processing, and recognizing faces programmatically.
