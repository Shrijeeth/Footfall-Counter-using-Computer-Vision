# Footfall Counter FastAPI Application

A computer vision-based footfall counter system with user authentication, configuration management, and video/livestream processing capabilities.

## Features

- **User Authentication**: JWT-based authentication system with user registration and login
- **Configuration Management**: Store and manage ROI configurations for different locations
- **Video Processing**: Upload and process video files with footfall counting
- **Livestream Processing**: Real-time processing of livestreams
- **Background Processing**: Asynchronous video processing with job status tracking
- **RESTful API**: Complete REST API with OpenAPI documentation

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file with your settings
# Important: Change the SECRET_KEY for production use
```

### 3. Run the Application

```bash
# Using the startup script
python run.py

# Or directly with uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Access the API

- **API Documentation**: `http://localhost:8000/docs`
- **Alternative Docs**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login and get access token

### Users

- `GET /api/v1/users/me` - Get current user profile
- `GET /api/v1/users/{user_id}` - Get user by ID

### Configurations

- `POST /api/v1/configurations/` - Create a new configuration
- `GET /api/v1/configurations/` - Get all user configurations
- `GET /api/v1/configurations/{config_id}` - Get specific configuration
- `PUT /api/v1/configurations/{config_id}` - Update configuration
- `DELETE /api/v1/configurations/{config_id}` - Delete configuration

### Processing

- `POST /api/v1/processing/upload-video` - Upload and process video file
- `POST /api/v1/processing/livestream` - Process livestream
- `GET /api/v1/processing/jobs` - Get all processing jobs
- `GET /api/v1/processing/jobs/{job_id}` - Get specific job
- `GET /api/v1/processing/jobs/{job_id}/download` - Download processed video

## Usage Examples

### 1. Register and Login

```bash
# Register a new user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword",
    "full_name": "Test User"
  }'

# Login to get access token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpassword"
```

### 2. Create Configuration

```bash
# Create a new ROI configuration
curl -X POST "http://localhost:8000/api/v1/configurations/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Main Entrance",
    "description": "ROI for main entrance door",
    "roi_x1": 400,
    "roi_y1": 713,
    "roi_x2": 826,
    "roi_y2": 718,
    "confidence_threshold": 0.5,
    "debounce_frames": 50,
    "is_default": true
  }'
```

### 3. Upload and Process Video

```bash
# Upload a video file for processing
curl -X POST "http://localhost:8000/api/v1/processing/upload-video" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@path/to/your/video.mp4" \
  -F "configuration_id=1"
```

### 4. Process Livestream

```bash
# Process a livestream
curl -X POST "http://localhost:8000/api/v1/processing/livestream" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "stream_url": "rtsp://camera-ip:554/stream",
    "configuration_id": 1,
    "max_duration": 300
  }'
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./footfall_counter.db` |
| `SECRET_KEY` | JWT secret key | `your-secret-key-change-this-in-production` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | `30` |
| `MAX_FILE_SIZE` | Maximum upload file size | `104857600` (100MB) |
| `UPLOAD_DIR` | Directory for uploaded files | `uploads` |
| `STATIC_DIR` | Directory for processed files | `static` |

### ROI Configuration

The Region of Interest (ROI) is defined as a line with coordinates:

- `roi_x1, roi_y1`: Start point of the line
- `roi_x2, roi_y2`: End point of the line

People crossing this line trigger entry/exit events.

## Database Schema

### Users Table

- User authentication and profile information
- Relationships to configurations and processing jobs

### Configurations Table

- ROI settings and processing parameters
- User-specific configurations with default options

### Processing Jobs Table

- Job tracking for video processing
- Status, results, and metadata storage

## Development

### Project Structure

```text
app/
├── __init__.py
├── main.py                 # FastAPI application
├── api/
│   └── v1/
│       ├── api.py         # API router
│       └── endpoints/     # API endpoints
├── core/
│   ├── auth.py           # Authentication logic
│   ├── config.py         # Configuration settings
│   └── database.py       # Database setup
├── models/               # SQLAlchemy models
├── schemas/              # Pydantic schemas
└── services/             # Business logic
    ├── footfall_tracker.py
    └── video_processor.py
```

### Adding New Features

1. **Models**: Add new SQLAlchemy models in `app/models/`
2. **Schemas**: Add Pydantic schemas in `app/schemas/`
3. **Endpoints**: Add new API endpoints in `app/api/v1/endpoints/`
4. **Services**: Add business logic in `app/services/`

## Deployment

### Production Setup

1. **Environment**: Set production environment variables
2. **Database**: Use PostgreSQL or MySQL for production
3. **Security**: Generate secure SECRET_KEY
4. **CORS**: Configure appropriate ALLOWED_HOSTS
5. **File Storage**: Consider cloud storage for large files

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Troubleshooting

### Common Issues

1. **YOLO Model Download**: First run will download the YOLO model
2. **File Permissions**: Ensure write permissions for upload/static directories
3. **Database**: SQLite file will be created automatically
4. **CORS**: Configure ALLOWED_HOSTS for frontend integration

### Logs

Check application logs for detailed error information:

```bash
python run.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
