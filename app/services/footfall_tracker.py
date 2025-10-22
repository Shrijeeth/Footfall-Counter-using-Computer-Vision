from typing import Dict, List, Tuple

import cv2


class FootfallTracker:
    """Footfall tracking using a line ROI."""

    def __init__(
        self, line_coords: Tuple[int, int, int, int], debounce_frames: int = 50
    ):
        """
        Initialize the footfall tracker.

        Args:
            line_coords: (x1, y1, x2, y2) for the ROI line
            debounce_frames: Number of frames to wait before counting another event for the same person
        """
        self.line = line_coords
        self.debounce_frames = debounce_frames
        self.entry_count = 0
        self.exit_count = 0
        self.tracked_objects = {}
        self.recent_events = {}
        self.frame_number = 0

    def is_crossing_line(
        self,
        prev_box: Tuple[int, int, int, int],
        curr_box: Tuple[int, int, int, int],
        prev_center: Tuple[int, int],
        curr_center: Tuple[int, int],
    ) -> int:
        """Check if any part of the bounding box crossed the line."""
        x1, y1, x2, y2 = self.line

        # Check if center crosses line
        def side(px, py):
            return (y2 - y1) * px - (x2 - x1) * py + (x2 * y1 - x1 * y2)

        prev_side = side(*prev_center)
        curr_side = side(*curr_center)
        center_cross = 0
        if prev_side != 0 and curr_side != 0 and prev_side * curr_side < 0:
            center_cross = 1 if prev_side < curr_side else -1  # 1: entry, -1: exit

        # Check if line intersects with the bbox edges
        def bbox_edges(box):
            x1, y1, x2, y2 = box
            return [
                ((x1, y1), (x2, y1)),  # top
                ((x2, y1), (x2, y2)),  # right
                ((x2, y2), (x1, y2)),  # bottom
                ((x1, y2), (x1, y1)),  # left
            ]

        def line_intersect(p1, p2, q1, q2):
            """Return True if lines (p1-p2) and (q1-q2) intersect"""

            def ccw(A, B, C):
                return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

            return ccw(p1, q1, q2) != ccw(p2, q1, q2) and ccw(p1, p2, q1) != ccw(
                p1, p2, q2
            )

        prev_cross = any(
            line_intersect((x1, y1), (x2, y2), e[0], e[1]) for e in bbox_edges(prev_box)
        )
        curr_cross = any(
            line_intersect((x1, y1), (x2, y2), e[0], e[1]) for e in bbox_edges(curr_box)
        )
        bbox_cross = (
            (not prev_cross and curr_cross)
            or (prev_cross and not curr_cross)
            or (prev_cross and curr_cross)
        )

        if center_cross != 0 and bbox_cross:
            return center_cross
        return 0

    def should_count_event(self, track_id: int, event_type: str) -> bool:
        """Check if enough time has passed since the last event for this track ID."""
        if track_id not in self.recent_events:
            return True
        frames_since_last = self.frame_number - self.recent_events[track_id]["frame"]
        return frames_since_last > self.debounce_frames

    def record_event(self, track_id: int, event_type: str):
        """Record an event for debouncing purposes."""
        self.recent_events[track_id] = {"type": event_type, "frame": self.frame_number}

    def draw_roi(self, frame):
        """Draw the ROI line on the frame."""
        x1, y1, x2, y2 = self.line
        return cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    def draw_event_text(
        self,
        frame,
        text: str,
        center_x: int,
        center_y: int,
        color: Tuple[int, int, int],
    ):
        """Draw event text (ENTRY/EXIT) near the person."""
        return cv2.putText(
            frame,
            text,
            (center_x - 30, center_y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2,
        )

    def draw_counts(self, frame):
        """Draw the current entry and exit counts on the frame."""
        frame = cv2.putText(
            frame,
            f"Entries: {self.entry_count}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )
        frame = cv2.putText(
            frame,
            f"Exits: {self.exit_count}",
            (10, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2,
        )
        return frame

    def process_detections(self, tracks) -> List[Dict]:
        """Extract person detections from YOLO tracking results."""
        if tracks.boxes is None or tracks.boxes.id is None:
            return []

        person_boxes = tracks.boxes.xyxy.cpu().numpy()
        track_ids = tracks.boxes.id.cpu().numpy()

        detections = []
        for i, track_id in enumerate(track_ids):
            x1, y1, x2, y2 = person_boxes[i]
            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)
            detections.append(
                {
                    "track_id": int(track_id),
                    "center": (center_x, center_y),
                    "bbox": (int(x1), int(y1), int(x2), int(y2)),
                }
            )
        return detections

    def check_crossings(self, detection: Dict, frame):
        """Check if a person crossed the ROI line and update counts."""
        track_id = detection["track_id"]
        center = detection["center"]
        bbox = detection["bbox"]

        if track_id in self.tracked_objects:
            prev_bbox, prev_center = self.tracked_objects[track_id]

            crossing = self.is_crossing_line(prev_bbox, bbox, prev_center, center)

            if crossing == 1 and self.should_count_event(track_id, "exit"):
                self.exit_count += 1
                self.record_event(track_id, "exit")
                frame = self.draw_event_text(frame, "EXIT", *center, (0, 0, 255))
            elif crossing == -1 and self.should_count_event(track_id, "entry"):
                self.entry_count += 1
                self.record_event(track_id, "entry")
                frame = self.draw_event_text(frame, "ENTRY", *center, (0, 255, 0))

        self.tracked_objects[track_id] = (bbox, center)
        return frame

    def process_frame(self, tracks):
        """Process a single frame and return the annotated frame."""
        self.frame_number += 1
        frame = tracks.plot()
        frame = self.draw_roi(frame)
        detections = self.process_detections(tracks)
        for detection in detections:
            frame = self.check_crossings(detection, frame)
        frame = self.draw_counts(frame)
        return frame

    def get_counts(self) -> Dict[str, int]:
        """Get the current entry and exit counts."""
        return {
            "entries": self.entry_count,
            "exits": self.exit_count,
            "total": self.entry_count + self.exit_count,
        }

    def reset_counts(self):
        """Reset all counts and tracking data."""
        self.entry_count = 0
        self.exit_count = 0
        self.tracked_objects = {}
        self.recent_events = {}
        self.frame_number = 0
