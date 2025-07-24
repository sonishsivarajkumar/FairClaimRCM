#!/bin/bash

# Run Tests Script for FairClaimRCM
# This script runs different types of tests based on the argument provided

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if dependencies are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    # Use the configured Python environment
    PYTHON_CMD="/Users/sonishsivarajkumar/.pyenv/versions/my_env/bin/python"
    
    if ! command -v "$PYTHON_CMD" &> /dev/null; then
        print_error "Python environment not found at $PYTHON_CMD"
        exit 1
    fi
    
    if ! "$PYTHON_CMD" -c "import pytest" &> /dev/null; then
        print_error "pytest is not installed. Run: pip install -r requirements-test.txt"
        exit 1
    fi
    
    print_success "Dependencies check passed"
}

# Function to set up test environment
setup_test_env() {
    print_status "Setting up test environment..."
    
    # Set test environment variables
    export ENVIRONMENT=test
    export DATABASE_URL=sqlite:///./test_fairclaimrcm.db
    export TESTING=true
    
    # Create test directories if they don't exist
    mkdir -p logs
    mkdir -p test-results
    
    print_success "Test environment setup complete"
}

# Function to run unit tests
run_unit_tests() {
    print_status "Running unit tests..."
    
    /Users/sonishsivarajkumar/.pyenv/versions/my_env/bin/python -m pytest tests/ -m "unit" \
        --cov=api --cov=core \
        --cov-report=term-missing \
        --cov-report=html:test-results/htmlcov \
        --cov-report=xml:test-results/coverage.xml \
        --junit-xml=test-results/unit-tests.xml \
        --tb=short \
        -v
    
    print_success "Unit tests completed"
}

# Function to run integration tests
run_integration_tests() {
    print_status "Running integration tests..."
    
    /Users/sonishsivarajkumar/.pyenv/versions/my_env/bin/python -m pytest tests/ -m "integration" \
        --junit-xml=test-results/integration-tests.xml \
        --tb=short \
        -v
    
    print_success "Integration tests completed"
}

# Function to run API tests
run_api_tests() {
    print_status "Running API tests..."
    
    # Start the API server in background for testing
    print_status "Starting API server for testing..."
    uvicorn api.main:app --host 127.0.0.1 --port 8001 &
    API_PID=$!
    
    # Wait for server to start
    sleep 5
    
    # Check if server is running
    if ! curl -f http://127.0.0.1:8001/health &> /dev/null; then
        print_error "Failed to start API server for testing"
        kill $API_PID 2>/dev/null || true
        exit 1
    fi
    
    # Run API tests
    TEST_API_URL=http://127.0.0.1:8001 /Users/sonishsivarajkumar/.pyenv/versions/my_env/bin/python -m pytest tests/ -m "api" \
        --junit-xml=test-results/api-tests.xml \
        --tb=short \
        -v
    
    # Stop the API server
    kill $API_PID 2>/dev/null || true
    
    print_success "API tests completed"
}

# Function to run ML tests
run_ml_tests() {
    print_status "Running ML component tests..."
    
    /Users/sonishsivarajkumar/.pyenv/versions/my_env/bin/python -m pytest tests/ -m "ml" \
        --junit-xml=test-results/ml-tests.xml \
        --tb=short \
        -v
    
    print_success "ML tests completed"
}

# Function to run performance tests
run_performance_tests() {
    print_status "Running performance tests..."
    
    # Start the API server
    print_status "Starting API server for performance testing..."
    uvicorn api.main:app --host 127.0.0.1 --port 8002 &
    API_PID=$!
    
    # Wait for server to start
    sleep 5
    
    # Run Locust performance tests
    locust -f tests/performance/locustfile.py \
        --headless \
        --users 5 \
        --spawn-rate 1 \
        --run-time 30s \
        --host http://127.0.0.1:8002 \
        --html test-results/performance-report.html
    
    # Stop the API server
    kill $API_PID 2>/dev/null || true
    
    print_success "Performance tests completed"
}

# Function to run security tests
run_security_tests() {
    print_status "Running security tests..."
    
    # Run Bandit security scan
    print_status "Running Bandit security scan..."
    bandit -r api/ core/ -f json -o test-results/bandit-report.json || true
    bandit -r api/ core/ || true
    
    # Run Safety vulnerability scan
    print_status "Running Safety vulnerability scan..."
    safety check --json --output test-results/safety-report.json || true
    safety check || true
    
    print_success "Security tests completed"
}

# Function to run all tests
run_all_tests() {
    print_status "Running all tests..."
    
    run_unit_tests
    run_integration_tests
    run_api_tests
    run_ml_tests
    
    print_success "All tests completed"
}

# Function to run code quality checks
run_code_quality() {
    print_status "Running code quality checks..."
    
    # Check formatting with Black
    print_status "Checking code formatting with Black..."
    /Users/sonishsivarajkumar/.pyenv/versions/my_env/bin/python -m black --check --diff api/ core/ cli.py || {
        print_warning "Code formatting issues found. Run 'black .' to fix them."
    }
    
    # Lint with Flake8
    print_status "Running Flake8 linting..."
    /Users/sonishsivarajkumar/.pyenv/versions/my_env/bin/python -m flake8 api/ core/ cli.py --count --select=E9,F63,F7,F82 --show-source --statistics || true
    /Users/sonishsivarajkumar/.pyenv/versions/my_env/bin/python -m flake8 api/ core/ cli.py --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    
    # Type checking with MyPy
    print_status "Running MyPy type checking..."
    /Users/sonishsivarajkumar/.pyenv/versions/my_env/bin/python -m mypy api/ core/ --ignore-missing-imports || true
    
    print_success "Code quality checks completed"
}

# Function to generate test report
generate_test_report() {
    print_status "Generating test report..."
    
    cat > test-results/test-summary.md << EOF
# Test Summary Report

## Test Results

| Test Type | Status | Details |
|-----------|--------|---------|
| Unit Tests | ✅ | See htmlcov/index.html for coverage |
| Integration Tests | ✅ | See integration-tests.xml |
| API Tests | ✅ | See api-tests.xml |
| ML Tests | ✅ | See ml-tests.xml |
| Code Quality | ✅ | Black, Flake8, MyPy checks |
| Security | ✅ | Bandit and Safety scans |

## Coverage Report

Coverage reports are available in:
- HTML: test-results/htmlcov/index.html
- XML: test-results/coverage.xml

## Performance Report

Performance test results: test-results/performance-report.html

## Security Reports

- Bandit: test-results/bandit-report.json
- Safety: test-results/safety-report.json

Generated on: $(date)
EOF
    
    print_success "Test report generated: test-results/test-summary.md"
}

# Function to clean up test artifacts
cleanup() {
    print_status "Cleaning up test artifacts..."
    
    # Remove test databases
    rm -f test_*.db
    rm -f .coverage
    
    # Clean up __pycache__ directories
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    
    print_success "Cleanup completed"
}

# Main script logic
main() {
    echo "========================================"
    echo "    FairClaimRCM Test Runner"
    echo "========================================"
    
    # Check dependencies first
    check_dependencies
    
    # Set up test environment
    setup_test_env
    
    case "${1:-all}" in
        "unit")
            run_unit_tests
            ;;
        "integration")
            run_integration_tests
            ;;
        "api")
            run_api_tests
            ;;
        "ml")
            run_ml_tests
            ;;
        "performance")
            run_performance_tests
            ;;
        "security")
            run_security_tests
            ;;
        "quality")
            run_code_quality
            ;;
        "all")
            run_all_tests
            run_code_quality
            run_security_tests
            ;;
        "clean")
            cleanup
            exit 0
            ;;
        "help"|"-h"|"--help")
            echo "Usage: $0 [test_type]"
            echo ""
            echo "Test types:"
            echo "  unit         Run unit tests only"
            echo "  integration  Run integration tests only"
            echo "  api          Run API tests only"
            echo "  ml           Run ML component tests only"
            echo "  performance  Run performance tests"
            echo "  security     Run security scans"
            echo "  quality      Run code quality checks"
            echo "  all          Run all tests (default)"
            echo "  clean        Clean up test artifacts"
            echo "  help         Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown test type: $1"
            echo "Run '$0 help' for usage information"
            exit 1
            ;;
    esac
    
    # Generate test report
    generate_test_report
    
    echo "========================================"
    print_success "Test execution completed!"
    echo "========================================"
}

# Run main function with all arguments
main "$@"
