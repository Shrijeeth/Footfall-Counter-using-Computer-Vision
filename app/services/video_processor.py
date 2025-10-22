import os
import time
from typing import Any, Callable, Dict, Optional

import cv2
from ultralytics import YOLO

from app.services.footfall_tracker import FootfallTracker


class VideoProcessor:
    """Service for processing videos and livestreams with footfall counting."""

    def __init__(self):
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load the YOLO model."""
        try:
            self.model = YOLO("yolo11n.pt")
        except Exception as e:
            print(f"Error loading YOLO model: {e}")
            raise

    def process_video_file(
        self,
        video_path: str,
        roi_coords: tuple,
        confidence: float = 0.5,
        debounce_frames: int = 50,
        output_path: Optional[str] = None,
        progress_callback: Optional[Callable[[float], None]] = None,
    ) -> Dict[str, Any]:
        """
        Process a video file and return footfall counts.

        Args:
            video_path: Path to the input video file
            roi_coords: ROI line coordinates (x1, y1, x2, y2)
            confidence: Detection confidence threshold
            debounce_frames: Debounce period for counting
            output_path: Path for output video (optional)
            progress_callback: Callback function for progress updates

        Returns:
            Dictionary with processing results
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        # Initialize tracker
        tracker = FootfallTracker(roi_coords, debounce_frames)

        # Setup video capture
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        if total_frames == 0:
            raise ValueError(
                "Video has no frames or frame count could not be determined"
            )

        # Setup video writer if output path is provided
        video_writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            video_writer = cv2.VideoWriter(
                output_path, fourcc, fps, (frame_width, frame_height)
            )

        # Process video with YOLO tracking
        start_time = time.time()
        processed_frames = 0

        try:
            # Create tracking generator
            track_generator = self.model.track(
                source=video_path,
                classes=[0],  # Person class
                conf=confidence,
                tracker="botsort.yaml",
                batch=1,
                stream=True,
            )

            # Process each frame
            for tracks in track_generator:
                processed_frame = tracker.process_frame(tracks)

                if video_writer:
                    video_writer.write(processed_frame)

                processed_frames += 1

                # Update progress
                if progress_callback:
                    progress = (processed_frames / total_frames) * 100
                    progress_callback(progress)

        finally:
            cap.release()
            if video_writer:
                video_writer.release()

        processing_time = time.time() - start_time

        return {
            "entry_count": tracker.entry_count,
            "exit_count": tracker.exit_count,
            "total_frames": processed_frames,
            "processing_duration": processing_time,
            "fps": fps,
            "output_path": output_path,
        }

    def process_livestream(
        self,
        stream_url: str,
        roi_coords: tuple,
        confidence: float = 0.5,
        debounce_frames: int = 50,
        max_duration: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Process a livestream and return footfall counts.

        Args:
            stream_url: URL or device index for the livestream
            roi_coords: ROI line coordinates (x1, y1, x2, y2)
            confidence: Detection confidence threshold
            debounce_frames: Debounce period for counting
            max_duration: Maximum processing duration in seconds

        Returns:
            Dictionary with processing results
        """
        # Initialize tracker
        tracker = FootfallTracker(roi_coords, debounce_frames)

        # Setup video capture
        cap = cv2.VideoCapture(stream_url)
        if not cap.isOpened():
            raise ValueError(f"Could not open stream: {stream_url}")

        start_time = time.time()
        processed_frames = 0

        try:
            # Create tracking generator
            track_generator = self.model.track(
                source=stream_url,
                classes=[0],  # Person class
                conf=confidence,
                tracker="botsort.yaml",
                batch=1,
                stream=True,
            )

            # Process frames
            for tracks in track_generator:
                tracker.process_frame(tracks)
                processed_frames += 1

                # Check if max duration reached
                if max_duration and (time.time() - start_time) > max_duration:
                    break

        finally:
            cap.release()

        processing_time = time.time() - start_time

        return {
            "entry_count": tracker.entry_count,
            "exit_count": tracker.exit_count,
            "total_frames": processed_frames,
            "processing_duration": processing_time,
        }

    def create_thumbnail(
        self, video_path: str, output_path: str, roi_coords: tuple
    ) -> str:
        """
        Create a thumbnail image from video with ROI overlay.

        Args:
            video_path: Path to the video file
            output_path: Path for the thumbnail image
            roi_coords: ROI line coordinates to overlay

        Returns:
            Path to the created thumbnail
        """
        cap = cv2.VideoCapture(video_path)

        # Get a frame from the middle of the video
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        middle_frame = total_frames // 2

        cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame)
        ret, frame = cap.read()
        cap.release()

        if not ret:
            raise ValueError("Could not extract frame from video")

        # Draw ROI on the frame
        x1, y1, x2, y2 = roi_coords
        frame = cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)

        # Save thumbnail
        cv2.imwrite(output_path, frame)
        return output_path
