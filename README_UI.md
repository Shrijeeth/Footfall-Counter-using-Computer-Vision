# Footfall Counter - Streamlit UI

A comprehensive web interface for the Footfall Counter application built with Streamlit, providing an intuitive way to interact with all API functionalities.

## Features

### 🔐 Authentication

- **User Registration**: Create new accounts with username, email, and password
- **User Login**: Secure authentication with JWT tokens
- **Session Management**: Persistent login sessions with automatic token handling

### ⚙️ Configuration Management

- **View Configurations**: Browse all your saved configurations
- **Create Configurations**: Set up new ROI lines and processing parameters
- **Configuration Details**: View model settings, confidence thresholds, and ROI coordinates

### 🎥 Video Processing

- **File Upload**: Support for MP4, AVI, MOV, and MKV formats
- **Configuration Selection**: Choose from your saved configurations
- **Processing Status**: Real-time updates on processing progress
- **Video Preview**: Preview uploaded videos before processing

### 📊 Results & Analytics

- **Job Management**: View all processing jobs and their status
- **Results Visualization**: Interactive charts showing entry/exit counts
- **Download Results**: Download processed videos with annotations
- **Metrics Dashboard**: Overview of total jobs, completion rates, and statistics

### 📈 Dashboard

- **Overview Metrics**: Total jobs, completed jobs, processing jobs, configurations
- **Recent Activity**: Latest processing jobs with timestamps
- **Status Distribution**: Visual breakdown of job statuses
- **Quick Navigation**: Easy access to all features

## Installation

### Prerequisites

- Python 3.8+
- FastAPI backend running (see main README)
- All dependencies from `requirements.txt`

### Setup

1. **Install Dependencies**

   ```bash
   make install
   ```

2. **Start the Complete Application**

   ```bash
   make run-ui
   ```

   This starts both FastAPI (port 8000) and Streamlit (port 8501)

### Alternative Startup Methods

**Run Services Separately:**

```bash
# Terminal 1: Start FastAPI
make run-api

# Terminal 2: Start Streamlit
make run-streamlit
```

**Direct Commands:**

```bash
# FastAPI only
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Streamlit only
python -m streamlit run streamlit_app.py --server.port 8501
```

## Usage

### 1. Access the Application

- **Streamlit UI**: `http://localhost:8501`
- **FastAPI Docs**: `http://localhost:8000/docs`
- **API Health**: `http://localhost:8000/health`

### 2. Getting Started

1. **Register/Login**
   - Create a new account or login with existing credentials
   - The UI handles JWT token management automatically

2. **Create Configuration**
   - Navigate to "Configurations" tab
   - Set up your ROI line coordinates
   - Configure model parameters and thresholds

3. **Process Videos**
   - Go to "Video Processing" tab
   - Upload your video file
   - Select a configuration
   - Monitor processing status

4. **View Results**
   - Check "Results" tab for completed jobs
   - View analytics and download processed videos
   - Monitor job progress and statistics

### 3. Dashboard Overview

The dashboard provides:

- **Metrics**: Quick stats on jobs and configurations
- **Recent Jobs**: Latest processing activities
- **Status Charts**: Visual representation of job distribution
- **Navigation**: Quick access to all features

## API Integration

The Streamlit UI integrates with all FastAPI endpoints:

### Authentication Endpoints

- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User authentication

### User Management

- `GET /api/v1/users/me` - Get user profile

### Configuration Management

- `GET /api/v1/configurations/` - List configurations
- `POST /api/v1/configurations/` - Create configuration

### Video Processing

- `POST /api/v1/processing/upload-video` - Upload video
- `GET /api/v1/processing/jobs` - List jobs
- `GET /api/v1/processing/jobs/{id}` - Job details
- `GET /api/v1/processing/jobs/{id}/download` - Download results

## Configuration Options

### Environment Variables

```bash
# API Configuration
API_BASE_URL=http://localhost:8000
WEBSOCKET_URL=ws://localhost:8000

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### Streamlit Settings

The app uses these Streamlit configurations:

- **Layout**: Wide mode for better space utilization
- **Theme**: Default Streamlit theme with custom CSS
- **File Upload**: Max 200MB for video files
- **Session State**: Persistent authentication and user data

## Features in Detail

### 🎨 User Interface

- **Responsive Design**: Works on desktop and tablet devices
- **Modern Styling**: Clean, professional interface with custom CSS
- **Interactive Elements**: Real-time updates and feedback
- **Navigation**: Intuitive sidebar navigation

### 📊 Data Visualization

- **Plotly Charts**: Interactive charts for results visualization
- **Metrics Display**: Clear presentation of key statistics
- **Progress Indicators**: Visual feedback for long-running operations
- **Status Badges**: Color-coded status indicators

### 🔄 Real-time Updates

- **Job Status**: Automatic refresh of processing status
- **Live Metrics**: Updated dashboard statistics
- **Progress Tracking**: Visual progress indicators
- **Error Handling**: Graceful error messages and recovery

## Troubleshooting

### Common Issues

1. **Connection Errors**

   ```text
   Error: Connection refused
   ```

   - Ensure FastAPI backend is running on port 8000
   - Check if the API_BASE_URL is correct

2. **Authentication Issues**

   ```text
   Error: Invalid credentials
   ```

   - Verify username and password
   - Check if the user account exists

3. **Upload Failures**

   ```text
   Error: File upload failed
   ```

   - Check file format (MP4, AVI, MOV, MKV)
   - Ensure file size is under 200MB
   - Verify configuration exists

4. **Processing Errors**

   ```text
   Error: Processing failed
   ```

   - Check FastAPI logs for detailed errors
   - Verify configuration parameters
   - Ensure sufficient disk space

### Debug Mode

Enable debug mode for detailed error information:

```bash
streamlit run streamlit_app.py --logger.level=debug
```

### Logs

Check logs for troubleshooting:

- **Streamlit logs**: Console output where Streamlit is running
- **FastAPI logs**: Backend API logs
- **Browser console**: For client-side JavaScript errors

## Development

### Project Structure

```text
├── streamlit_app.py          # Main Streamlit application
├── run_ui.py                 # Startup script for both services
├── requirements.txt          # Dependencies including Streamlit
└── README_UI.md             # This documentation
```

### Adding New Features

1. **New Pages**: Add functions like `show_new_page()` and update navigation
2. **API Integration**: Extend `APIClient` class with new endpoints
3. **Visualizations**: Add new Plotly charts in result sections
4. **Styling**: Update CSS in the markdown section

### Testing

Test the UI components:

```bash
# Run with test data
streamlit run streamlit_app.py

# Test API connectivity
curl http://localhost:8000/health
```

## Security

### Authentication

- JWT tokens are stored in Streamlit session state
- Tokens are automatically included in API requests
- Session expires when browser is closed

### Data Protection

- No sensitive data is stored in browser localStorage
- All API communication uses the backend's security measures
- File uploads are handled securely through FastAPI

## Performance

### Optimization

- Efficient API calls with proper error handling
- Lazy loading of data where appropriate
- Caching of configuration data
- Minimal re-renders with proper state management

### Scalability

- Stateless design for horizontal scaling
- Efficient data structures for large datasets
- Optimized file upload handling
- Responsive UI for various screen sizes

## Support

For issues and questions:

1. Check the troubleshooting section above
2. Review FastAPI backend logs
3. Verify all dependencies are installed
4. Ensure proper network connectivity between services

## Future Enhancements

Planned features:

- **Real-time Processing**: WebSocket integration for live feeds
- **Advanced Analytics**: More detailed charts and statistics
- **Batch Processing**: Multiple video upload and processing
- **Export Options**: CSV/Excel export of results
- **User Management**: Admin panel for user administration
- **Themes**: Dark/light mode toggle
- **Mobile Support**: Responsive design for mobile devices
