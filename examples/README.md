# FairClaimRCM Examples

This directory contains example scripts, data, and API usage demonstrations for FairClaimRCM.

## Available Examples

### 1. Basic API Usage (`basic_api_usage.py`)
Demonstrates fundamental API operations:
- Creating claims
- Getting coding recommendations  
- Validating codes
- Retrieving audit trails

### 2. Sample Clinical Data (`sample_clinical_data.json`)
Contains realistic clinical documentation examples for testing.

### 3. Postman Collection (`fairclaimrcm_api.postman_collection.json`)
Complete API collection for testing all endpoints.

### 4. Batch Processing (`batch_processing.py`)
Shows how to process multiple claims efficiently.

## Quick Start

1. **Start the API server**:
   ```bash
   cd ../api
   uvicorn main:app --reload
   ```

2. **Run basic examples**:
   ```bash
   python basic_api_usage.py
   ```

3. **Test with sample data**:
   ```bash
   python process_sample_data.py
   ```

## API Endpoints Overview

- **Claims**: `/api/v1/claims/`
- **Coding**: `/api/v1/coding/`
- **Terminology**: `/api/v1/terminology/`
- **Audit**: `/api/v1/audit/`

See the API documentation at http://localhost:8000/docs for complete details.
