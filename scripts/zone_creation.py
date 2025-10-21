import argparse
import os
import sys

import cv2

roi_line = []  # Will store two points defining the line


def draw_line(event, x, y, flags, param):
    global roi_line, img_copy
    if event == cv2.EVENT_LBUTTONDOWN:
        roi_line = [(x, y)]
    elif event == cv2.EVENT_LBUTTONUP:
        roi_line.append((x, y))
        cv2.line(img_copy, roi_line[0], roi_line[1], (0, 255, 255), 2)
        cv2.imshow("Frame", img_copy)
        print("Line ROI coordinates:", roi_line)


# Parse command line arguments
parser = argparse.ArgumentParser(
    description="Create line ROI for footfall counter by drawing on video frame"
)
parser.add_argument("video_path", help="Path to the input video file")
args = parser.parse_args()

# Validate video file exists
if not os.path.exists(args.video_path):
    print(f"Error: Video file '{args.video_path}' not found.")
    sys.exit(1)

# Load video
video_path = args.video_path
cap = cv2.VideoCapture(video_path)

# Get total frame count and select a middle frame
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
if total_frames == 0:
    raise ValueError("Video has no frames or frame count could not be determined")

# Use middle frame, or frame 100 if video is long enough
target_frame = min(100, total_frames // 2)
print(f"Video has {total_frames} frames, using frame {target_frame}")

cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
ret, frame = cap.read()
cap.release()

if not ret:
    raise ValueError("Could not read frame from video")

img_copy = frame.copy()
cv2.imshow("Frame", img_copy)
cv2.setMouseCallback("Frame", draw_line)

print("Click and drag to draw the door ROI line, release to confirm.")
cv2.waitKey(0)
cv2.destroyAllWindows()

# Extract coordinates
if len(roi_line) == 2:
    x1, y1 = roi_line[0]
    x2, y2 = roi_line[1]
    door_roi_line = (x1, y1, x2, y2)
    print("Final line ROI:", door_roi_line)

    frame_h, frame_w = frame.shape[:2]

    # Normalize coordinates
    x1_norm = x1 / frame_w
    y1_norm = y1 / frame_h
    x2_norm = x2 / frame_w
    y2_norm = y2 / frame_h

    door_roi_line_normalized = (x1_norm, y1_norm, x2_norm, y2_norm)
    print("Normalized line ROI:", door_roi_line_normalized)

    # Draw line on frame
    frame = cv2.line(frame, roi_line[0], roi_line[1], (0, 255, 0), 2)

# Save frame
image_path = os.path.expanduser("data/roi_line_frame.jpg")
os.makedirs(os.path.dirname(image_path), exist_ok=True)
cv2.imwrite(image_path, frame)
print(f"Frame saved to {image_path}")
