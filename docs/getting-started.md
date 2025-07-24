# Getting Started with FairClaimRCM

This guide will help you get FairClaimRCM up and running on your local machine.

## Prerequisites

- Python 3.8 or higher
- PostgreSQL (optional - can use Docker)
- Node.js 14+ (for future web UI development)
- Git

## Quick Start with Docker

The fastest way to get started is using Docker Compose:

```bash
# Clone the repository
git clone <your-repo-url>
cd fairclaimrcm

# Start all services
docker-compose up -d

# Check if everything is running
curl http://localhost:8000/health
```

Access the API documentation at: http://localhost:8000/docs

## Manual Installation

### 1. Set up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Set up Database

#### Option A: PostgreSQL (Recommended)
```bash
# Install PostgreSQL
# macOS: brew install postgresql
# Ubuntu: sudo apt-get install postgresql

# Create database
createdb fairclaimrcm
```

#### Option B: SQLite (Development Only)
```bash
# Update DATABASE_URL in .env file:
DATABASE_URL=sqlite:///./fairclaimrcm.db
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
nano .env
```

### 4. Start the API Server

```bash
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000

## Testing the Installation

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Run Core Tests
```bash
python tests/test_core.py
```

### 3. Use the CLI Tool
```bash
# Analyze clinical text
python cli.py analyze "Patient presents with chest pain and shortness of breath"

# Validate codes
python cli.py validate --icd10 "I21.9" --cpt "99213"

# Search terminology
python cli.py search icd10 "myocardial"
```

### 4. Run API Examples
```bash
cd examples
python basic_api_usage.py
```

## API Usage Examples

### Create a Claim
```python
import requests

claim_data = {
    "claim_id": "CLAIM-001",
    "patient_id": "PATIENT-123",
    "encounter_id": "ENC-456",
    "chief_complaint": "Chest pain",
    "history_present_illness": "65-year-old male with acute chest pain...",
    "discharge_summary": "Patient treated for myocardial infarction..."
}

response = requests.post("http://localhost:8000/api/v1/claims/", json=claim_data)
```

### Get Coding Recommendations
```python
coding_request = {
    "clinical_text": "Patient presents with acute myocardial infarction",
    "include_explanations": True
}

response = requests.post("http://localhost:8000/api/v1/coding/analyze", json=coding_request)
recommendations = response.json()
```

### Search Terminology
```python
response = requests.get("http://localhost:8000/api/v1/terminology/icd10/search?q=myocardial&limit=5")
results = response.json()
```

## Directory Structure

```
fairclaimrcm/
├── api/                    # FastAPI application
│   ├── main.py            # Application entry point
│   ├── models/            # Database and Pydantic models
│   ├── routes/            # API route handlers
│   └── services/          # Business logic services
├── core/                  # Core functionality
│   ├── terminology/       # Medical code services (ICD-10, CPT, DRG)
│   ├── ml/               # Machine learning components
│   └── config.py         # Configuration management
├── data/                 # Sample data and terminology files
├── docs/                 # Documentation
├── examples/             # Usage examples and demos
├── tests/                # Test suite
├── web-ui/              # Future React web application
├── docker-compose.yml   # Docker services configuration
├── Dockerfile          # API container definition
├── requirements.txt    # Python dependencies
└── cli.py             # Command-line interface
```

## Configuration Options

Key configuration options in `.env`:

| Setting | Description | Default |
|---------|-------------|---------|
| `DATABASE_URL` | Database connection string | PostgreSQL localhost |
| `DEBUG` | Enable debug mode | `false` |
| `HOST` | API server host | `0.0.0.0` |
| `PORT` | API server port | `8000` |
| `SECRET_KEY` | JWT secret key | Change in production |
| `ELASTICSEARCH_URL` | Search engine URL | `http://localhost:9200` |

## Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs for interactive API documentation
2. **Run Examples**: Check out the `examples/` directory for usage patterns
3. **Add Your Data**: Update terminology files in `data/terminology/`
4. **Customize Rules**: Modify coding logic in `core/` modules
5. **Extend the API**: Add new endpoints in `api/routes/`

## Getting Help

- **API Documentation**: http://localhost:8000/docs
- **Examples**: `examples/` directory
- **Tests**: Run `python tests/test_core.py`
- **CLI Help**: `python cli.py --help`

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you've activated the virtual environment and installed dependencies
2. **Database Connection**: Check your DATABASE_URL in `.env`
3. **Port Conflicts**: Change the PORT setting if 8000 is already in use
4. **Permission Errors**: Ensure the CLI script is executable: `chmod +x cli.py`

### Development Tips

- Use `uvicorn main:app --reload` for automatic reloading during development
- Check logs for detailed error messages
- Use the interactive API docs at `/docs` for testing endpoints
- Run tests frequently to catch issues early

## Production Deployment

For production deployment, consider:

1. **Security**: Change SECRET_KEY and use proper authentication
2. **Database**: Use a managed PostgreSQL service
3. **Monitoring**: Add logging and monitoring solutions
4. **Scaling**: Use proper WSGI server like Gunicorn
5. **SSL**: Enable HTTPS with proper certificates
