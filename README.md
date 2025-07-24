# FairClaimRCM 🏥💰

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com/)

**Make inpatient coding and claims adjudication transparent, accurate, and auditable—so providers get paid fairly and payers see exactly why each dollar posts.**

> **🚧 Development Status**: This is an MVP implementation showcasing the core architecture and functionality. The system includes working API endpoints, sample terminology data, and basic ML-assisted coding recommendations. Ready for development, testing, and contributions!

## 🎯 Mission

FairClaimRCM is an open-source healthcare revenue cycle management system that brings transparency and accuracy to medical coding and claims processing. Our goal is to eliminate the black box nature of current RCM systems and provide clear, auditable explanations for every coding decision and reimbursement calculation.

## ✨ Key Features

- **🔍 Transparent Coding**: AI-assisted medical coding with complete audit trails
- **📊 Explainable AI**: Every coding decision comes with human-readable explanations
- **💯 Audit-Ready**: Full compliance tracking and documentation
- **🔧 Extensible**: Modular architecture for easy customization
- **🌐 Standards-Compliant**: Built on HL7/FHIR, ICD-10, CPT standards
- **⚡ Fast API**: RESTful endpoints for seamless integration

## 🏗️ Architecture

### Core Modules

| Module | Responsibility |
|--------|----------------|
| **Terminology & Mapping** | ICD-10, CPT, DRG lookup service with version tracking |
| **Code Recommendation** | Rule-based + ML-assisted code suggestion with confidence scoring |
| **Audit & Explainability** | Per-claim "why this code" reports with decision traces |
| **Reimbursement Engine** | Fee schedule processing and reimbursement simulation |
| **Claims Validation API** | REST endpoints for chart submission and claim processing |
| **Web UI Dashboard** | Interactive interface for claim analysis and metrics |
| **Data Connectors** | HL7/FHIR ingestion and legacy system exports |

## 🚀 Quick Start

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

### Option 3: Docker Quick Start

```bash
docker-compose up -d
```

### Testing the Installation

```bash
# Test core functionality
python3 tests/test_core.py

# Use the CLI tool
python3 cli.py health
python3 cli.py analyze "Patient presents with chest pain"

# Run API examples
cd examples && python3 basic_api_usage.py
```

## 📖 Documentation

- [🏁 Getting Started Guide](docs/getting-started.md)
- [🏗️ Architecture Overview](docs/architecture.md)
- [🔌 API Reference](docs/api-reference.md)
- [🧪 Examples & Tutorials](examples/)
- [🛠️ Development Guide](docs/development.md)

## 🤝 Contributing

We welcome contributions from the healthcare and software development communities! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Ways to Contribute

- 🐛 Report bugs and issues
- 💡 Suggest new features
- 📝 Improve documentation
- 🧪 Add test cases
- 🔧 Submit code improvements
- 🌐 Help with translations

## 📋 Roadmap

### v0.1 (MVP) - Core Coding Engine
- [ ] Basic ICD-10/CPT lookup service
- [ ] Simple rule-based coding suggestions
- [ ] REST API for code validation
- [ ] Basic audit logging

### v0.2 - Enhanced Intelligence
- [ ] ML-powered code recommendations
- [ ] Confidence scoring
- [ ] Detailed audit reports
- [ ] Batch processing capabilities

### v1.0 - Full Platform
- [ ] Complete web UI dashboard
- [ ] HL7/FHIR integration
- [ ] Advanced analytics
- [ ] Multi-tenant support
- [ ] Enterprise deployment options

## 🛠️ Tech Stack

- **Backend**: Python + FastAPI
- **Frontend**: React + Tailwind CSS
- **Database**: PostgreSQL + Elasticsearch
- **ML/AI**: scikit-learn, transformers
- **Rules Engine**: JSON-based rule definitions
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🏥 Healthcare Compliance

FairClaimRCM is designed with healthcare compliance in mind:
- HIPAA-ready architecture (encryption, audit logs)
- SOC 2 Type II compliance features
- HL7/FHIR standard implementations
- Audit trail requirements for medical coding

## 🌟 Community

- 💬 [Discussions](https://github.com/your-org/fairclaimrcm/discussions)
- 📧 [Mailing List](mailto:fairclaimrcm@yourorg.com)
- 🐦 [Twitter](https://twitter.com/fairclaimrcm)
- 💼 [LinkedIn](https://linkedin.com/company/fairclaimrcm)

## 🎯 Use Cases

- **Healthcare Providers**: Improve coding accuracy and reduce claim denials
- **RCM Companies**: Add transparency to client reporting
- **Payers**: Validate claims with clear audit trails
- **Consultants**: Analyze coding patterns and optimize workflows
- **Researchers**: Study healthcare coding patterns and outcomes

---

**Made with ❤️ for the healthcare community**

*FairClaimRCM - Because every claim deserves a fair and transparent review.*
