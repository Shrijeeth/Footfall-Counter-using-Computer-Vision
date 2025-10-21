# Footfall Counter using Computer Vision

A sophisticated computer vision system for counting people entering and exiting through doorways, gates, or other defined boundaries using YOLO11 object detection and BoT-SORT tracking algorithms.

## 🎯 Overview

This project implements a real-time footfall counting system that:

- **Detects people** using YOLO11 object detection model
- **Tracks individuals** across video frames using BoT-SORT algorithm
- **Counts entries/exits** when people cross a defined line ROI (Region of Interest)
- **Prevents duplicate counts** with intelligent debouncing logic
- **Generates annotated videos** with visual feedback and count displays

## 🚀 Features

- **Line-based ROI Detection**: Uses a simple line boundary instead of rectangular regions for more accurate entry/exit detection
- **Real-time Processing**: Optimized for live video streams and recorded footage
- **Robust Tracking**: BoT-SORT algorithm maintains consistent person identities even through occlusions
- **Visual Feedback**: Real-time display of entry/exit events and running counts
- **Interactive ROI Setup**: GUI tool for easily defining counting boundaries on video frames
- **Configurable Parameters**: Adjustable confidence thresholds, debounce periods, and tracking settings

## 📁 Project Structure

```text
Footfall-Counter-using-Computer-Vision/
├── data/                           # Video files and sample data
│   ├── 853874-hd_1920_1080_25fps.mp4  # Sample input video
│   └── roi_line_frame.jpg          # ROI visualization frame
├── notebooks/                      # Jupyter notebooks
│   ├── footfall_counter_v1.ipynb  # Main implementation notebook
│   └── tracking_output_*.mp4       # Generated output videos
├── scripts/                        # Utility scripts
│   └── zone_creation.py           # Interactive ROI line creation tool
├── botsort.yaml                   # BoT-SORT tracker configuration
├── requirements.txt               # Python dependencies
├── Makefile                       # Build and utility commands
└── README.md                      # This file
```

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- OpenCV
- PyTorch (automatically installed with ultralytics)

### Setup

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/Footfall-Counter-using-Computer-Vision.git
   cd Footfall-Counter-using-Computer-Vision
   ```

2. **Install dependencies**:

   ```bash
   make install
   # or manually:
   pip install -r requirements.txt
   ```

3. **For development** (includes linting tools):

   ```bash
   make dev-install
   ```

## 🎮 Usage

### Quick Start

1. **Define ROI Line** (Interactive):

   ```bash
   make mark-video-zone VIDEO=data/853874-hd_1920_1080_25fps.mp4
   ```

   - Click and drag to draw a line across the entry/exit boundary
   - The tool will save the coordinates and generate a visualization

2. **Run Footfall Counter**:
   - Open `notebooks/footfall_counter_v1.ipynb` in Jupyter
   - Update the `video_roi` coordinates with your line coordinates
   - Run all cells to process the video and generate counts

### Advanced Usage

#### Custom Video Processing

```python
from ultralytics import YOLO

# Load model
model = YOLO("yolo11n.pt")

# Configure tracking
track_generator = model.track(
    source="your_video.mp4",
    classes=[0],  # Person class only
    conf=0.5,     # Confidence threshold
    tracker="botsort.yaml",
    stream=True
)

# Process with FootfallTracker
tracker = FootfallTracker(roi_line_coords, debounce_frames=50)
for tracks in track_generator:
    processed_frame = tracker.process_frame(tracks)
```

#### ROI Line Coordinates

The ROI is defined as a line with coordinates `(x1, y1, x2, y2)`:

- `(x1, y1)`: Start point of the line
- `(x2, y2)`: End point of the line
- People crossing this line trigger entry/exit events

## ⚙️ Configuration

### BoT-SORT Tracker Settings (`botsort.yaml`)

```yaml
tracker_type: botsort
track_high_thresh: 0.15    # First-stage match threshold
track_low_thresh: 0.1      # Second-stage threshold
new_track_thresh: 0.25     # New track creation threshold
track_buffer: 30           # Frames to keep lost tracks
match_thresh: 0.8          # Association similarity threshold
```

### Footfall Counter Parameters

- **Debounce Frames**: `50` (prevents duplicate counts for ~2 seconds at 25fps)
- **Confidence Threshold**: `0.5` (minimum detection confidence)
- **Person Class**: `0` (COCO dataset person class)

## 🔧 Development

### Code Quality

```bash
make format    # Format code with ruff
make lint      # Fix import sorting and basic issues
make check     # Run full linting check
```

### Project Commands

```bash
# Install dependencies
make install

# Install development dependencies
make dev-install

# Create ROI for a video
make mark-video-zone VIDEO=path/to/video.mp4
```

## 📊 Algorithm Details

### Detection Pipeline

1. **YOLO11 Detection**: Identifies people in each frame with bounding boxes
2. **BoT-SORT Tracking**: Assigns consistent IDs to people across frames
3. **Line Crossing Detection**: Checks if person's center and bounding box cross the ROI line
4. **Event Classification**: Determines if crossing is entry or exit based on direction
5. **Debouncing**: Prevents duplicate counts from the same person within debounce period

### Counting Logic

- **Entry**: Person moves from one side of the line to the other (direction depends on line orientation)
- **Exit**: Person moves in the opposite direction
- **Debouncing**: Same person cannot trigger another count for 50 frames (configurable)

## 🎥 Output

The system generates:

- **Annotated Video**: Original video with ROI line, bounding boxes, and count displays
- **Console Output**: Real-time entry/exit counts and final totals
- **Visual Feedback**: Green "ENTRY" and red "EXIT" labels on detected events

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Ultralytics YOLO**: State-of-the-art object detection
- **BoT-SORT**: Advanced multi-object tracking algorithm
- **OpenCV**: Computer vision library for video processing

## 📞 Support

For questions, issues, or contributions, please:

- Open an issue on GitHub
- Check existing documentation in the notebooks
- Review the configuration files for parameter tuning

---

**Note**: This system is designed for controlled environments with clear entry/exit points. Performance may vary based on video quality, lighting conditions, and crowd density.
