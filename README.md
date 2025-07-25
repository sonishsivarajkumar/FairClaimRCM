# FairClaimRCM

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com/)

**Make inpatient coding and claims adjudication transparent, accurate, and auditable—so providers get paid fairly and payers see exactly why each dollar posts.**

> **Development Status**: ✅ **v0.3 Complete!** This implementation includes a comprehensive web UI dashboard, advanced analytics, real-time monitoring, user management, enhanced batch processing, and an improved reimbursement engine. The system now provides over 40+ API endpoints across 9 modules with interactive web interface and enterprise-ready features.

## Mission

FairClaimRCM is an open-source healthcare revenue cycle management system that brings transparency and accuracy to medical coding and claims processing. Our goal is to eliminate the black box nature of current RCM systems and provide clear, auditable explanations for every coding decision and reimbursement calculation.

## Key Features

- ✅ **Transparent Coding**: Rule-based medical coding with complete audit trails
- ✅ **Explainable AI**: Every coding decision comes with human-readable explanations
- ✅ **Audit-Ready**: Full compliance tracking and documentation
- ✅ **Extensible**: Modular architecture for easy customization
- ✅ **Standards-Compliant**: Built on ICD-10, CPT, DRG standards
- ✅ **Fast API**: 40+ RESTful endpoints across 9 modules for seamless integration
- ✅ **Comprehensive Testing**: Unit, integration, performance, and security tests
- ✅ **CLI Interface**: Command-line tool for development and testing
- ✅ **Docker Ready**: Container deployment and development environment
- ✅ **Web UI Dashboard**: Interactive React-based interface with real-time updates
- ✅ **Advanced Analytics**: Coding pattern analysis and performance metrics
- ✅ **Real-time Monitoring**: System health monitoring and alerting
- ✅ **User Management**: Multi-user support with role-based access
- ✅ **Batch Processing**: Large-scale claim processing with parallel execution
- ✅ **Enhanced Reimbursement**: Comprehensive fee schedules and payment simulation

## Architecture

### Core Modules

| Module | Responsibility | Status |
|--------|----------------|--------|
| **Terminology & Mapping** | ICD-10, CPT, DRG lookup service with version tracking | ✅ Complete |
| **Code Recommendation** | Rule-based + pattern matching code suggestion with confidence scoring | ✅ Complete |
| **Audit & Explainability** | Per-claim "why this code" reports with decision traces | ✅ Complete |
| **Claims Validation API** | REST endpoints for chart submission and claim processing | ✅ Complete |
| **Reimbursement Engine** | Comprehensive fee schedule processing and payment simulation | ✅ Complete |
| **Web UI Dashboard** | Interactive React interface with real-time analytics | ✅ Complete |
| **Analytics & Reporting** | Advanced analytics with coding pattern analysis | ✅ Complete |
| **User Management** | Multi-user support with role-based access control | ✅ Complete |
| **Batch Processing** | Large-scale parallel claim processing | ✅ Complete |
| **Real-time Monitoring** | System health monitoring and performance metrics | ✅ Complete |
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

The FairClaimRCM API provides 40+ endpoints across 9 main modules:

### 🔍 Terminology Services (`/api/v1/terminology/`)
- **ICD-10**: Search, validate, and get detailed code information
- **CPT**: Procedure code search and validation with category filtering
- **DRG**: Diagnosis-related group lookup and validation

### 🧠 Coding Engine (`/api/v1/coding/`)
- **Analyze**: Generate coding recommendations from clinical text
- **Validate**: Validate sets of medical codes
- **Estimate**: Basic reimbursement estimation
- **Batch**: Process multiple claims in parallel

### 📋 Claims Management (`/api/v1/claims/`)
- **CRUD Operations**: Create, read, update, delete claims
- **Search**: Find claims by various criteria
- **Coding**: Get recommendations for specific claims
- **Status Tracking**: Monitor claim processing status

### 📊 Analytics & Reporting (`/api/v1/analytics/`)
- **Dashboard Metrics**: Key performance indicators and statistics
- **Coding Patterns**: Analysis of coding trends and accuracy
- **Performance**: System performance and response metrics
- **Reimbursement Trends**: Payment analysis and forecasting

### 👥 User Management (`/api/v1/users/`)
- **User CRUD**: Create, read, update, delete users
- **Authentication**: Login, logout, session management
- **Roles & Permissions**: Role-based access control
- **Activity Tracking**: User activity and audit logs

### 🔄 Batch Processing (`/api/v1/batch/`)
- **Job Management**: Create, monitor, and control batch jobs
- **File Upload**: Process CSV/JSON files with claims data
- **Progress Tracking**: Real-time job progress and status
- **Result Export**: Download results in multiple formats

### 💰 Reimbursement Engine (`/api/v1/reimbursement/`)
- **Calculate**: Comprehensive reimbursement calculations
- **Fee Schedules**: Medicare, Medicaid, and commercial rates
- **Simulation**: Multi-payer scenario comparison
- **Validation**: Coverage and eligibility checks

### 📈 Real-time Monitoring (`/api/v1/monitoring/`)
- **System Health**: CPU, memory, disk usage monitoring
- **Application Metrics**: API performance and user activity
- **Database Performance**: Connection and query metrics
- **Alerts**: Active system alerts and notifications

### 📋 Audit & Compliance (`/api/v1/audit/`)
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
- ✅ **Rule-based coding suggestions** - Pattern matching and terminology mapping
- ✅ **REST API for code validation** - 25+ endpoints across 4 modules
- ✅ **Basic audit logging** - Comprehensive audit trails
- ✅ **Claims management** - Full CRUD operations
- ✅ **CLI interface** - Command-line tool for testing
- ✅ **Test infrastructure** - Unit, integration, performance tests
- ✅ **Docker support** - Container deployment ready

### v0.2 - Enhanced Intelligence ✅ **COMPLETED**
- ✅ **Rule-based code recommendations** - Deterministic pattern matching
- ✅ **Confidence scoring** - Rule-based confidence calculation
- ✅ **Detailed audit reports** - Per-claim audit trails
- ✅ **Batch processing capabilities** - Basic batch API endpoint
- ⚠️ **Note**: ML capabilities limited by lack of training data

### v0.3 - Web Interface & Analytics ✅ **COMPLETED**
- ✅ **React web UI dashboard** - Complete interactive interface with real-time updates
- ✅ **Advanced analytics** - Comprehensive coding pattern analysis and metrics
- ✅ **Real-time monitoring** - System performance monitoring with alerts
- ✅ **User management** - Multi-user support with role-based access control
- ✅ **Enhanced batch processing** - Large-scale parallel claim processing
- ✅ **Improved reimbursement engine** - Comprehensive fee schedules and payment simulation

### v1.0+ - Advanced Features (Requires Clinical Data Partnership)
- ⏳ **True ML Models** - Requires access to annotated clinical datasets
- ⏳ **Deep Learning Coding** - Natural language processing for clinical text

### v1.0 - Full Platform
- ⏳ **HL7/FHIR integration** - Healthcare data standards
- ⏳ **EHR connectors** - Direct EHR integration
- ⏳ **Multi-tenant support** - Organization management
- ⏳ **Enterprise features** - SSO, advanced security
- ⏳ **Real-time data feeds** - Live terminology updates

**Legend**: ✅ Complete | 🟡 Partial | 🚧 In Progress | ⏳ Planned

## Tech Stack

- **Backend**: Python + FastAPI
- **Frontend**: React + Tailwind CSS (planned)
- **Database**: PostgreSQL + SQLite
- **Coding Engine**: Rule-based pattern matching
- **Rules Engine**: JSON-based rule definitions
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions

**Note**: ML/AI capabilities (scikit-learn, transformers) are present but limited by lack of training data. Current coding recommendations use deterministic rule-based approaches.

## Machine Learning Considerations

**Current Approach**: FairClaimRCM uses **rule-based intelligence** rather than machine learning due to the lack of available clinical training data. The system provides:

- ✅ **Pattern Matching**: Keywords and phrases mapped to medical codes
- ✅ **Terminology Matching**: Direct clinical term to code relationships  
- ✅ **Confidence Scoring**: Rule-based confidence calculation
- ✅ **Explainable Results**: Clear reasoning for each recommendation

**Why Not "True" ML?**: 
- 🔒 **Clinical Data Privacy**: Real patient data requires HIPAA compliance and partnerships
- 💰 **Commercial Datasets**: Proprietary medical coding datasets are expensive
- 📊 **Annotation Complexity**: Medical coding requires expert clinical knowledge

**Future ML Enhancement Path**:
- 🤝 **Healthcare Partnerships**: Collaborate with healthcare organizations
- 📚 **Synthetic Data**: Generate realistic but artificial clinical scenarios
- 🔄 **Federated Learning**: Train models without centralizing sensitive data
- 📖 **Public Datasets**: Utilize available medical literature and code mappings

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
