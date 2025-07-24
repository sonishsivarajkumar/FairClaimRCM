# FairClaimRCM

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com/)

**Make inpatient coding and claims adjudication transparent, accurate, and auditable—so providers get paid fairly and payers see exactly why each dollar posts.**

> **Development Status**: ✅ **v0.1 MVP Complete!** This implementation includes a fully functional API with 25+ endpoints, comprehensive terminology services, ML-assisted coding recommendations, claims management, audit logging, and a complete test suite. Ready for development, testing, and production deployment!

## Mission

FairClaimRCM is an open-source healthcare revenue cycle management system that brings transparency and accuracy to medical coding and claims processing. Our goal is to eliminate the black box nature of current RCM systems and provide clear, auditable explanations for every coding decision and reimbursement calculation.

## Key Features

- ✅ **Transparent Coding**: AI-assisted medical coding with complete audit trails
- ✅ **Explainable AI**: Every coding decision comes with human-readable explanations
- ✅ **Audit-Ready**: Full compliance tracking and documentation
- ✅ **Extensible**: Modular architecture for easy customization
- ✅ **Standards-Compliant**: Built on ICD-10, CPT, DRG standards
- ✅ **Fast API**: 25+ RESTful endpoints for seamless integration
- ✅ **Comprehensive Testing**: Unit, integration, performance, and security tests
- ✅ **CLI Interface**: Command-line tool for development and testing
- ✅ **Docker Ready**: Container deployment and development environment

## Architecture

### Core Modules

| Module | Responsibility | Status |
|--------|----------------|--------|
| **Terminology & Mapping** | ICD-10, CPT, DRG lookup service with version tracking | ✅ Complete |
| **Code Recommendation** | Rule-based + ML-assisted code suggestion with confidence scoring | ✅ Complete |
| **Audit & Explainability** | Per-claim "why this code" reports with decision traces | ✅ Complete |
| **Claims Validation API** | REST endpoints for chart submission and claim processing | ✅ Complete |
| **Reimbursement Engine** | Fee schedule processing and reimbursement simulation | 🟡 Basic |
| **Web UI Dashboard** | Interactive interface for claim analysis and metrics | ⏳ Planned |
| **Data Connectors** | HL7/FHIR ingestion and legacy system exports | ⏳ Planned |

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 14+ (for web UI - optional)
- PostgreSQL (or SQLite for development)
- Docker (optional)

### Option 1: Quick Start Script

```bash
# Make the script executable and run it
chmod +x start.sh
./start.sh
```

This script will:
- Create a virtual environment
- Install dependencies
- Run basic tests
- Start the API server

### Option 2: Manual Installation

1. **Set up Python environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env as needed
   ```

3. **Start the API server**
   ```bash
   cd api
   python -m uvicorn main:app --reload
   ```

4. **Access the API documentation**
   Open http://localhost:8000/docs in your browser

## Available API Endpoints

The FairClaimRCM API provides 25+ endpoints across 4 main modules:

### 🔍 Terminology Services (`/api/v1/terminology/`)
- **ICD-10**: Search, validate, and get detailed code information
- **CPT**: Procedure code search and validation with category filtering
- **DRG**: Diagnosis-related group lookup and validation

### 🧠 Coding Engine (`/api/v1/coding/`)
- **Analyze**: Generate coding recommendations from clinical text
- **Validate**: Validate sets of medical codes
- **Estimate**: Basic reimbursement estimation

### 📋 Claims Management (`/api/v1/claims/`)
- **CRUD Operations**: Create, read, update, delete claims
- **Search**: Find claims by various criteria
- **Coding**: Get recommendations for specific claims

### 📊 Audit & Compliance (`/api/v1/audit/`)
- **Logs**: Track all system activities
- **Reports**: Generate compliance reports
- **History**: View audit trails for claims and users

*Full API documentation available at http://localhost:8000/docs*

### Option 3: Docker Quick Start

```bash
docker-compose up -d
```

### Testing the Installation

```bash
# Test core functionality (36 unit tests)
python3 tests/test_core.py

# Run comprehensive test suite
chmod +x scripts/run_tests.sh
./scripts/run_tests.sh unit          # Unit tests
./scripts/run_tests.sh integration   # Integration tests
./scripts/run_tests.sh quality       # Code quality checks
./scripts/run_tests.sh all           # All tests

# Use the CLI tool
python3 cli.py health
python3 cli.py analyze "Patient presents with chest pain"
python3 cli.py validate --icd10 "I21.9" --cpt "99213"
python3 cli.py search icd10 "myocardial"

# Run API examples
cd examples && python3 basic_api_usage.py
```

## Documentation

- [Getting Started Guide](docs/getting-started.md)
- [Architecture Overview](docs/architecture.md)
- [API Reference](docs/api-reference.md)
- [Examples & Tutorials](examples/)
- [Development Guide](docs/development.md)

## Contributing

We welcome contributions from the healthcare and software development communities! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Ways to Contribute

- Report bugs and issues
- Suggest new features
- Improve documentation
- Add test cases
- Submit code improvements
- Help with translations

## Roadmap

### v0.1 (MVP) - Core Coding Engine ✅ **COMPLETED**
- ✅ **Basic ICD-10/CPT/DRG lookup service** - Full search and validation
- ✅ **Rule-based coding suggestions** - ML-assisted recommendations
- ✅ **REST API for code validation** - 25+ endpoints across 4 modules
- ✅ **Basic audit logging** - Comprehensive audit trails
- ✅ **Claims management** - Full CRUD operations
- ✅ **CLI interface** - Command-line tool for testing
- ✅ **Test infrastructure** - Unit, integration, performance tests
- ✅ **Docker support** - Container deployment ready

### v0.2 - Enhanced Intelligence 🚧 **IN PROGRESS**
- ✅ **ML-powered code recommendations** - Basic implementation
- ✅ **Confidence scoring** - Initial confidence calculation
- ✅ **Detailed audit reports** - Per-claim audit trails
- 🟡 **Batch processing capabilities** - Basic batch API endpoint
- ⏳ **Enhanced ML training** - Real clinical data integration
- ⏳ **Improved reimbursement engine** - Comprehensive fee schedules

### v0.3 - Web Interface & Analytics
- ⏳ **React web UI dashboard** - Interactive interface
- ⏳ **Advanced analytics** - Coding pattern analysis
- ⏳ **Real-time monitoring** - System performance metrics
- ⏳ **User management** - Multi-user support
- ⏳ **Enhanced batch processing** - Large-scale claim processing

### v1.0 - Full Platform
- ⏳ **HL7/FHIR integration** - Healthcare data standards
- ⏳ **EHR connectors** - Direct EHR integration
- ⏳ **Multi-tenant support** - Organization management
- ⏳ **Enterprise features** - SSO, advanced security
- ⏳ **Advanced AI models** - Deep learning for coding
- ⏳ **Real-time data feeds** - Live terminology updates

**Legend**: ✅ Complete | 🟡 Partial | 🚧 In Progress | ⏳ Planned

## Tech Stack

- **Backend**: Python + FastAPI
- **Frontend**: React + Tailwind CSS
- **Database**: PostgreSQL + Elasticsearch
- **ML/AI**: scikit-learn, transformers
- **Rules Engine**: JSON-based rule definitions
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Healthcare Compliance

FairClaimRCM is designed with healthcare compliance in mind:
- HIPAA-ready architecture (encryption, audit logs)
- SOC 2 Type II compliance features
- HL7/FHIR standard implementations
- Audit trail requirements for medical coding

## Community

- [Discussions](https://github.com/your-org/fairclaimrcm/discussions)
- [Mailing List](mailto:fairclaimrcm@yourorg.com)
- [Twitter](https://twitter.com/fairclaimrcm)
- [LinkedIn](https://linkedin.com/company/fairclaimrcm)

## Use Cases

- **Healthcare Providers**: Improve coding accuracy and reduce claim denials
- **RCM Companies**: Add transparency to client reporting
- **Payers**: Validate claims with clear audit trails
- **Consultants**: Analyze coding patterns and optimize workflows
- **Researchers**: Study healthcare coding patterns and outcomes

---

**Made with dedication for the healthcare community**

*FairClaimRCM - Because every claim deserves a fair and transparent review.*
