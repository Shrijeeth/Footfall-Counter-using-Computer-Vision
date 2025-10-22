"""
Streamlit UI for Footfall Counter Application
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

# Configuration
API_BASE_URL = "http://localhost:8000"
WEBSOCKET_URL = "ws://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="Footfall Counter",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border: 1px solid #f5c6cb;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None


class APIClient:
    """API client for communicating with FastAPI backend"""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()

    def set_auth_token(self, token: str):
        """Set authentication token for requests"""
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def register(self, username: str, email: str, password: str):
        """Register a new user"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/register",
                json={"username": username, "email": email, "password": password},
            )
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            st.error(f"Registration error: {str(e)}")
            return None

    def login(self, username: str, password: str):
        """Login user and get access token"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                data={"username": username, "password": password},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            st.error(f"Login error: {str(e)}")
            return None

    def get_user_profile(self):
        """Get current user profile"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/users/me")
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            st.error(f"Profile error: {str(e)}")
            return None

    def get_configurations(self):
        """Get user configurations"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/configurations/")
            return response.json() if response.status_code == 200 else []
        except Exception as e:
            st.error(f"Configuration error: {str(e)}")
            return []

    def create_configuration(self, config_data):
        """Create new configuration"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/configurations/", json=config_data
            )
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            st.error(f"Configuration creation error: {str(e)}")
            return None

    def upload_video(self, video_file, config_id):
        """Upload video for processing"""
        try:
            files = {"file": video_file}
            data = {"config_id": config_id}
            response = self.session.post(
                f"{self.base_url}/api/v1/processing/upload-video",
                files=files,
                data=data,
            )
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Upload failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            st.error(f"Video upload error: {str(e)}")
            return None

    def get_processing_jobs(self):
        """Get processing jobs"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/processing/jobs")
            return response.json() if response.status_code == 200 else []
        except Exception as e:
            st.error(f"Jobs error: {str(e)}")
            return []

    def get_job_status(self, job_id):
        """Get job status"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/processing/jobs/{job_id}"
            )
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            st.error(f"Job status error: {str(e)}")
            return None

    def download_results(self, job_id):
        """Download job results"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/processing/jobs/{job_id}/download"
            )
            if response.status_code == 200:
                return response.content
            return None
        except Exception as e:
            st.error(f"Download error: {str(e)}")
            return None


# Initialize API client
api_client = APIClient(API_BASE_URL)


def show_login_page():
    """Display login/register page"""
    st.markdown(
        '<h1 class="main-header">👥 Footfall Counter</h1>', unsafe_allow_html=True
    )

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Login to Your Account")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit_login = st.form_submit_button("Login", use_container_width=True)

            if submit_login and username and password:
                with st.spinner("Logging in..."):
                    result = api_client.login(username, password)
                    if result and "access_token" in result:
                        st.session_state.authenticated = True
                        st.session_state.access_token = result["access_token"]
                        api_client.set_auth_token(result["access_token"])

                        # Get user profile
                        profile = api_client.get_user_profile()
                        if profile:
                            st.session_state.user_info = profile

                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Please try again.")

    with tab2:
        st.subheader("Create New Account")
        with st.form("register_form"):
            reg_username = st.text_input("Username", key="reg_username")
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input(
                "Password", type="password", key="reg_password"
            )
            reg_confirm_password = st.text_input(
                "Confirm Password", type="password", key="reg_confirm_password"
            )
            submit_register = st.form_submit_button(
                "Register", use_container_width=True
            )

            if submit_register:
                if not all(
                    [reg_username, reg_email, reg_password, reg_confirm_password]
                ):
                    st.error("Please fill in all fields.")
                elif reg_password != reg_confirm_password:
                    st.error("Passwords do not match.")
                elif len(reg_password) < 6:
                    st.error("Password must be at least 6 characters long.")
                else:
                    with st.spinner("Creating account..."):
                        result = api_client.register(
                            reg_username, reg_email, reg_password
                        )
                        if result:
                            st.success("Account created successfully! Please login.")
                        else:
                            st.error(
                                "Registration failed. Username or email may already exist."
                            )


def show_main_app():
    """Display main application interface"""
    # Set auth token
    if st.session_state.access_token:
        api_client.set_auth_token(st.session_state.access_token)

    # Sidebar
    with st.sidebar:
        st.markdown("### User Profile")
        if st.session_state.user_info:
            st.write(
                f"**Username:** {st.session_state.user_info.get('username', 'N/A')}"
            )
            st.write(f"**Email:** {st.session_state.user_info.get('email', 'N/A')}")

        st.markdown("---")

        # Navigation
        page = st.selectbox(
            "Navigate to:",
            [
                "Dashboard",
                "Configurations",
                "Video Processing",
                "Results",
                "Real-time Processing",
            ],
        )

        st.markdown("---")

        if st.button("Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.access_token = None
            st.session_state.user_info = None
            st.rerun()

    # Main content
    if page == "Dashboard":
        show_dashboard()
    elif page == "Configurations":
        show_configurations()
    elif page == "Video Processing":
        show_video_processing()
    elif page == "Results":
        show_results()
    elif page == "Real-time Processing":
        show_realtime_processing()


def show_dashboard():
    """Display dashboard with overview metrics"""
    st.markdown('<h1 class="main-header">📊 Dashboard</h1>', unsafe_allow_html=True)

    # Get data
    jobs = api_client.get_processing_jobs()
    configs = api_client.get_configurations()

    # Metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Jobs", len(jobs))

    with col2:
        completed_jobs = len([j for j in jobs if j.get("status") == "completed"])
        st.metric("Completed Jobs", completed_jobs)

    with col3:
        processing_jobs = len([j for j in jobs if j.get("status") == "processing"])
        st.metric("Processing Jobs", processing_jobs)

    with col4:
        st.metric("Configurations", len(configs))

    # Recent jobs
    if jobs:
        st.subheader("Recent Processing Jobs")
        df = pd.DataFrame(jobs)
        if not df.empty:
            # Format the dataframe for display - use available columns
            available_columns = ["id", "status", "created_at"]
            if "original_filename" in df.columns:
                available_columns.insert(1, "original_filename")
            elif "filename" in df.columns:
                available_columns.insert(1, "filename")

            display_df = df[available_columns].copy()
            display_df["created_at"] = pd.to_datetime(
                display_df["created_at"]
            ).dt.strftime("%Y-%m-%d %H:%M")

            # Rename columns for better display
            if "original_filename" in display_df.columns:
                display_df = display_df.rename(
                    columns={"original_filename": "filename"}
                )

            st.dataframe(display_df, use_container_width=True)

    # Job status distribution
    if jobs:
        st.subheader("Job Status Distribution")
        status_counts = pd.Series(
            [j.get("status", "unknown") for j in jobs]
        ).value_counts()
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Job Status Distribution",
        )
        st.plotly_chart(fig, use_container_width=True)


def show_configurations():
    """Display configuration management interface"""
    st.markdown('<h1 class="main-header">⚙️ Configurations</h1>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["View Configurations", "Create New"])

    with tab1:
        st.subheader("Your Configurations")
        configs = api_client.get_configurations()

        if configs:
            for config in configs:
                with st.expander(f"Configuration: {config.get('name', 'Unnamed')}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**ID:** {config.get('id')}")
                        st.write(f"**Name:** {config.get('name')}")
                        st.write(f"**Model:** {config.get('model_name')}")
                        st.write(
                            f"**Confidence:** {config.get('confidence_threshold')}"
                        )
                    with col2:
                        st.write(
                            f"**ROI Line:** ({config.get('roi_x1')}, {config.get('roi_y1')}) to ({config.get('roi_x2')}, {config.get('roi_y2')})"
                        )
                        st.write(
                            f"**Debounce:** {config.get('debounce_frames')} frames"
                        )
                        st.write(f"**Created:** {config.get('created_at', 'N/A')}")
        else:
            st.info("No configurations found. Create your first configuration below.")

    with tab2:
        st.subheader("Create New Configuration")
        with st.form("config_form"):
            name = st.text_input(
                "Configuration Name", placeholder="e.g., Main Entrance"
            )

            col1, col2 = st.columns(2)
            with col1:
                model_name = st.selectbox(
                    "Model", ["yolo11n.pt", "yolo11s.pt", "yolo11m.pt"]
                )
                confidence = st.slider("Confidence Threshold", 0.1, 1.0, 0.5, 0.1)
                debounce_frames = st.number_input("Debounce Frames", 1, 200, 50)

            with col2:
                st.write("**ROI Line Coordinates**")
                roi_x1 = st.number_input("Start X", 0, 1920, 100)
                roi_y1 = st.number_input("Start Y", 0, 1080, 300)
                roi_x2 = st.number_input("End X", 0, 1920, 500)
                roi_y2 = st.number_input("End Y", 0, 1080, 300)

            submit_config = st.form_submit_button(
                "Create Configuration", use_container_width=True
            )

            if submit_config and name:
                config_data = {
                    "name": name,
                    "model_name": model_name,
                    "confidence_threshold": confidence,
                    "roi_x1": roi_x1,
                    "roi_y1": roi_y1,
                    "roi_x2": roi_x2,
                    "roi_y2": roi_y2,
                    "debounce_frames": debounce_frames,
                }

                with st.spinner("Creating configuration..."):
                    result = api_client.create_configuration(config_data)
                    if result:
                        st.success("Configuration created successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to create configuration.")


def show_video_processing():
    """Display video processing interface"""
    st.markdown(
        '<h1 class="main-header">🎥 Video Processing</h1>', unsafe_allow_html=True
    )

    # Get configurations
    configs = api_client.get_configurations()

    if not configs:
        st.warning("Please create a configuration first before processing videos.")
        return

    st.subheader("Upload Video for Processing")

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "Choose a video file",
            type=["mp4", "avi", "mov", "mkv"],
            help="Upload a video file to process for footfall counting",
        )

    with col2:
        config_options = {f"{c['name']} (ID: {c['id']})": c["id"] for c in configs}
        selected_config = st.selectbox(
            "Select Configuration", options=list(config_options.keys())
        )

        if st.button(
            "Process Video", use_container_width=True, disabled=uploaded_file is None
        ):
            if uploaded_file and selected_config:
                config_id = config_options[selected_config]

                with st.spinner("Uploading and processing video..."):
                    result = api_client.upload_video(uploaded_file, config_id)
                    if result:
                        st.success(
                            f"Video uploaded successfully! Job ID: {result.get('job_id')}"
                        )
                        st.info(
                            "Processing started. Check the Results page for updates."
                        )
                    else:
                        st.error("Failed to upload video.")

    # Show video preview if uploaded
    if uploaded_file:
        st.subheader("Video Preview")
        st.video(uploaded_file)


def show_results():
    """Display processing results"""
    st.markdown('<h1 class="main-header">📈 Results</h1>', unsafe_allow_html=True)

    jobs = api_client.get_processing_jobs()

    if not jobs:
        st.info("No processing jobs found.")
        return

    # Job selection
    job_options = {
        f"Job {j['id']}: {j.get('original_filename', j.get('filename', 'Unknown'))} ({j.get('status', 'Unknown')})": j[
            "id"
        ]
        for j in jobs
    }
    selected_job = st.selectbox("Select Job", options=list(job_options.keys()))

    if selected_job:
        job_id = job_options[selected_job]
        job_details = api_client.get_job_status(job_id)

        if job_details:
            col1, col2 = st.columns([2, 1])

            with col1:
                st.subheader("Job Details")
                st.write(f"**Status:** {job_details.get('status', 'Unknown')}")
                st.write(
                    f"**Filename:** {job_details.get('original_filename', job_details.get('filename', 'Unknown'))}"
                )
                st.write(f"**Created:** {job_details.get('created_at', 'Unknown')}")

                if job_details.get("results"):
                    results = job_details["results"]
                    st.write(f"**Total Count:** {results.get('total_count', 0)}")
                    st.write(f"**Entry Count:** {results.get('entry_count', 0)}")
                    st.write(f"**Exit Count:** {results.get('exit_count', 0)}")

            with col2:
                st.subheader("Actions")

                # Refresh button
                if st.button("Refresh Status", use_container_width=True):
                    st.rerun()

                # Download results
                if job_details.get("status") == "completed":
                    if st.button("Download Results", use_container_width=True):
                        with st.spinner("Downloading..."):
                            content = api_client.download_results(job_id)
                            if content:
                                st.download_button(
                                    label="Download Video",
                                    data=content,
                                    file_name=f"processed_{job_details.get('filename', 'video')}.mp4",
                                    mime="video/mp4",
                                    use_container_width=True,
                                )

            # Results visualization
            if job_details.get("results") and job_details.get("status") == "completed":
                st.subheader("Results Visualization")

                results = job_details["results"]

                # Metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Count", results.get("total_count", 0))
                with col2:
                    st.metric("Entries", results.get("entry_count", 0))
                with col3:
                    st.metric("Exits", results.get("exit_count", 0))

                # Chart
                if (
                    results.get("entry_count", 0) > 0
                    or results.get("exit_count", 0) > 0
                ):
                    fig = go.Figure(
                        data=[
                            go.Bar(
                                name="Entries",
                                x=["Count"],
                                y=[results.get("entry_count", 0)],
                            ),
                            go.Bar(
                                name="Exits",
                                x=["Count"],
                                y=[results.get("exit_count", 0)],
                            ),
                        ]
                    )
                    fig.update_layout(title="Entry vs Exit Count", barmode="group")
                    st.plotly_chart(fig, use_container_width=True)


def show_realtime_processing():
    """Display real-time processing interface"""
    st.markdown(
        '<h1 class="main-header">🔴 Real-time Processing</h1>', unsafe_allow_html=True
    )

    st.info(
        "Real-time processing with WebSocket integration will be available in the next update."
    )

    # Placeholder for real-time features
    st.subheader("Coming Soon")
    st.write("- Live camera feed processing")
    st.write("- Real-time footfall counting")
    st.write("- Live dashboard updates")
    st.write("- WebSocket integration")


# Main application logic
def main():
    """Main application entry point"""
    if not st.session_state.authenticated:
        show_login_page()
    else:
        show_main_app()


if __name__ == "__main__":
    main()
