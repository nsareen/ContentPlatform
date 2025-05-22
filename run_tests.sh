#!/bin/bash

# Content Platform Test Runner
# This script runs both backend and integration tests

set -e  # Exit on error

echo "===== Content Platform Test Runner ====="
echo "Running tests to ensure no regression issues..."

# Function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Function to ensure dependencies are installed
ensure_dependencies() {
  echo ""
  echo "===== Checking Dependencies ====="
  cd backend
  
  # Check if pip is installed
  if ! command_exists pip; then
    echo "Error: pip is required to install Python dependencies."
    echo "Please install pip and try again."
    exit 1
  fi
  
  # Install backend dependencies
  echo "Installing backend dependencies..."
  pip install -r requirements.txt
  
  # Ensure alembic is in the PATH
  if ! command_exists alembic; then
    echo "Adding alembic to PATH..."
    export PATH="$PATH:$(python -m site --user-base)/bin"
    if ! command_exists alembic; then
      echo "Installing alembic globally..."
      pip install alembic
    fi
  fi
  
  # Check if pytest is installed
  if ! command_exists pytest; then
    echo "Installing pytest..."
    pip install pytest
  fi
  
  cd ..
  echo "Dependencies check completed."
}

# Function to run database migrations
run_migrations() {
  echo ""
  echo "===== Running Database Migrations ====="
  cd backend
  
  # Run alembic migrations
  echo "Running alembic migrations..."
  python -c "
import alembic.config
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath('.')))
alembic_args = ['--raiseerr', 'upgrade', 'head']
alembic.config.main(argv=alembic_args)
"
  
  # If direct alembic command fails, use the manual migration script
  if [ $? -ne 0 ]; then
    echo "Alembic command failed, using manual migration script..."
    python scripts/apply_migration.py
  fi
  
  cd ..
  echo "Database migrations completed."
}

# Function to run backend tests
run_backend_tests() {
  echo ""
  echo "===== Running Backend Tests ====="
  cd backend
  
  # Run backend tests
  pytest tests/test_api.py -v
  
  cd ..
  echo "Backend tests completed."
}

# Function to run integration tests
run_integration_tests() {
  echo ""
  echo "===== Running Integration Tests ====="
  cd tests/integration
  
  # Check if npm is installed
  if ! command_exists npm; then
    echo "Error: npm is required to run integration tests."
    echo "Please install Node.js and npm, then try again."
    exit 1
  fi
  
  # Install dependencies
  echo "Installing integration test dependencies..."
  npm install
  
  # Run integration tests
  echo "Running integration tests..."
  npm test
  
  cd ../..
  echo "Integration tests completed."
}

# Function to check if servers are running
check_servers() {
  echo ""
  echo "===== Checking Servers ====="
  
  # Check if backend server is running
  if curl -s http://localhost:8000 > /dev/null; then
    echo "✅ Backend server is running."
  else
    echo "❌ Backend server is not running. Please start it before running integration tests."
    echo "   Run: cd backend && python -m uvicorn app.main:app --reload"
    exit 1
  fi
  
  # Check if frontend server is running
  if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend server is running."
  else
    echo "❌ Frontend server is not running. Please start it before running integration tests."
    echo "   Run: cd frontend && npm run dev"
    exit 1
  fi
}

# Main execution
echo "Starting test suite..."

# Ensure dependencies are installed
ensure_dependencies

# Run database migrations
run_migrations

# Run backend tests
run_backend_tests

# Check if servers are running before integration tests
check_servers

# Run integration tests
run_integration_tests

echo ""
echo "===== All Tests Completed ====="
echo "✅ Test suite completed successfully!"
