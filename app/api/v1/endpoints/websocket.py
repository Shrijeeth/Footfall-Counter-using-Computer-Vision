import asyncio
import json
from typing import Dict

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.configuration import Configuration
from app.services.footfall_tracker import FootfallTracker
from app.services.video_processor import VideoProcessor

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for real-time processing."""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.processing_tasks: Dict[str, asyncio.Task] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.processing_tasks:
            self.processing_tasks[client_id].cancel()
            del self.processing_tasks[client_id]

    async def send_message(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            await websocket.send_text(json.dumps(message))


manager = ConnectionManager()


async def process_livestream_realtime(
    client_id: str,
    stream_url: str,
    roi_coords: tuple,
    confidence: float,
    debounce_frames: int,
):
    """Process livestream in real-time and send updates via WebSocket."""
    try:
        # Initialize video processor and tracker
        video_processor = VideoProcessor()
        tracker = FootfallTracker(roi_coords, debounce_frames)

        # Send initial status
        await manager.send_message(
            client_id,
            {
                "type": "status",
                "message": "Starting livestream processing...",
                "status": "starting",
            },
        )

        # Create tracking generator
        track_generator = video_processor.model.track(
            source=stream_url,
            classes=[0],  # Person class
            conf=confidence,
            tracker="botsort.yaml",
            batch=1,
            stream=True,
        )

        frame_count = 0

        # Process frames
        for tracks in track_generator:
            # Check if client is still connected
            if client_id not in manager.active_connections:
                break

            # Process frame
            tracker.process_frame(tracks)
            frame_count += 1

            # Send periodic updates (every 30 frames to avoid overwhelming)
            if frame_count % 30 == 0:
                counts = tracker.get_counts()
                await manager.send_message(
                    client_id,
                    {
                        "type": "update",
                        "frame_count": frame_count,
                        "entry_count": counts["entries"],
                        "exit_count": counts["exits"],
                        "total_count": counts["total"],
                    },
                )

            # Small delay to prevent overwhelming
            await asyncio.sleep(0.01)

    except Exception as e:
        await manager.send_message(
            client_id, {"type": "error", "message": f"Processing error: {str(e)}"}
        )

    finally:
        # Send final results
        if client_id in manager.active_connections:
            counts = tracker.get_counts()
            await manager.send_message(
                client_id,
                {
                    "type": "completed",
                    "final_counts": counts,
                    "total_frames": frame_count,
                },
            )


@router.websocket("/livestream/{client_id}")
async def websocket_livestream(
    websocket: WebSocket, client_id: str, db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time livestream processing."""
    await manager.connect(websocket, client_id)

    try:
        while True:
            # Receive processing request
            data = await websocket.receive_text()
            request_data = json.loads(data)

            # Validate request
            required_fields = ["stream_url", "configuration_id"]
            if not all(field in request_data for field in required_fields):
                await manager.send_message(
                    client_id,
                    {
                        "type": "error",
                        "message": "Missing required fields: stream_url, configuration_id",
                    },
                )
                continue

            # Get configuration
            config = (
                db.query(Configuration)
                .filter(Configuration.id == request_data["configuration_id"])
                .first()
            )

            if not config:
                await manager.send_message(
                    client_id, {"type": "error", "message": "Configuration not found"}
                )
                continue

            # Stop any existing processing task
            if client_id in manager.processing_tasks:
                manager.processing_tasks[client_id].cancel()

            # Start new processing task
            roi_coords = (config.roi_x1, config.roi_y1, config.roi_x2, config.roi_y2)
            confidence = request_data.get(
                "confidence_threshold", config.confidence_threshold
            )
            debounce_frames = request_data.get(
                "debounce_frames", config.debounce_frames
            )

            task = asyncio.create_task(
                process_livestream_realtime(
                    client_id,
                    request_data["stream_url"],
                    roi_coords,
                    confidence,
                    debounce_frames,
                )
            )

            manager.processing_tasks[client_id] = task

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        await manager.send_message(
            client_id, {"type": "error", "message": f"WebSocket error: {str(e)}"}
        )
        manager.disconnect(client_id)
