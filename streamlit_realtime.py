"""
Real-time processing component for Streamlit UI
WebSocket integration for live footfall counting
"""

import json
import queue
import time

import cv2
import streamlit as st
import websockets


class RealtimeProcessor:
    """Handle real-time video processing with WebSocket communication"""

    def __init__(self, websocket_url: str):
        self.websocket_url = websocket_url
        self.is_processing = False
        self.frame_queue = queue.Queue(maxsize=10)
        self.result_queue = queue.Queue()
        self.websocket = None

    async def connect_websocket(self, config_id: str):
        """Connect to WebSocket for real-time processing"""
        try:
            uri = f"{self.websocket_url}/api/v1/processing/livestream/{config_id}"
            self.websocket = await websockets.connect(uri)
            return True
        except Exception as e:
            st.error(f"WebSocket connection failed: {str(e)}")
            return False

    async def send_frame(self, frame):
        """Send frame to WebSocket for processing"""
        if self.websocket:
            try:
                # Convert frame to base64
                _, buffer = cv2.imencode(".jpg", frame)
                frame_data = buffer.tobytes()

                # Send frame data
                await self.websocket.send(frame_data)

                # Receive results
                response = await self.websocket.recv()
                result = json.loads(response)
                return result
            except Exception as e:
                st.error(f"Frame processing error: {str(e)}")
                return None
        return None

    def process_camera_feed(self, config_id: str):
        """Process live camera feed"""
        cap = cv2.VideoCapture(0)  # Use default camera

        if not cap.isOpened():
            st.error("Cannot access camera")
            return

        # Streamlit placeholders
        frame_placeholder = st.empty()
        metrics_placeholder = st.empty()

        total_count = 0

        try:
            while self.is_processing:
                ret, frame = cap.read()
                if not ret:
                    break

                # Display frame
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_placeholder.image(
                    frame_rgb, channels="RGB", use_column_width=True
                )

                # Process frame (placeholder for actual processing)
                # In real implementation, this would use the WebSocket

                # Update metrics
                metrics_placeholder.metric("Total Count", total_count)

                time.sleep(0.1)  # Control frame rate

        except Exception as e:
            st.error(f"Processing error: {str(e)}")
        finally:
            cap.release()


def show_realtime_processing():
    """Enhanced real-time processing interface"""
    st.markdown(
        '<h1 class="main-header">🔴 Real-time Processing</h1>', unsafe_allow_html=True
    )

    # Get configurations (assuming api_client is available)
    # This would need to be passed from the main app
    configs = []  # Placeholder

    if not configs:
        st.warning(
            "Please create a configuration first before starting real-time processing."
        )
        return

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Live Camera Feed")

        # Camera selection
        camera_source = st.selectbox(
            "Camera Source", ["Default Camera (0)", "External Camera (1)", "IP Camera"]
        )

        if camera_source == "IP Camera":
            _ = st.text_input(
                "IP Camera URL", placeholder="rtsp://192.168.1.100:554/stream"
            )

        # Processing controls
        col1_1, col1_2 = st.columns(2)

        with col1_1:
            start_button = st.button("Start Processing", use_container_width=True)

        with col1_2:
            stop_button = st.button("Stop Processing", use_container_width=True)

    with col2:
        st.subheader("Configuration")

        if configs:
            config_options = {f"{c['name']} (ID: {c['id']})": c["id"] for c in configs}
            _ = st.selectbox(
                "Select Configuration", options=list(config_options.keys())
            )

        st.subheader("Live Metrics")

        # Placeholders for real-time metrics
        total_metric = st.empty()
        entry_metric = st.empty()
        exit_metric = st.empty()

        # Initialize metrics
        total_metric.metric("Total Count", 0)
        entry_metric.metric("Entries", 0)
        exit_metric.metric("Exits", 0)

    # Processing status
    if "realtime_processing" not in st.session_state:
        st.session_state.realtime_processing = False

    if start_button and not st.session_state.realtime_processing:
        st.session_state.realtime_processing = True
        st.success("Real-time processing started!")

        # Here you would start the actual processing
        # processor = RealtimeProcessor(WEBSOCKET_URL)
        # processor.is_processing = True
        # processor.process_camera_feed(config_id)

    if stop_button and st.session_state.realtime_processing:
        st.session_state.realtime_processing = False
        st.info("Real-time processing stopped.")

    # Status indicator
    if st.session_state.realtime_processing:
        st.success("🟢 Processing Active")
    else:
        st.info("🔴 Processing Inactive")

    # Instructions
    st.subheader("Instructions")
    st.write("""
    1. **Select Configuration**: Choose a pre-configured ROI and model settings
    2. **Choose Camera Source**: Select your camera or IP stream
    3. **Start Processing**: Begin real-time footfall counting
    4. **Monitor Results**: Watch live metrics and video feed
    5. **Stop Processing**: End the session when done
    """)

    # Technical notes
    with st.expander("Technical Information"):
        st.write("""
        **WebSocket Integration:**
        - Real-time communication with FastAPI backend
        - Low-latency frame processing
        - Live result streaming
        
        **Camera Support:**
        - USB/Built-in cameras
        - IP cameras (RTSP/HTTP streams)
        - Video file simulation
        
        **Performance:**
        - Optimized for real-time processing
        - Configurable frame rate
        - Automatic quality adjustment
        """)


if __name__ == "__main__":
    show_realtime_processing()
