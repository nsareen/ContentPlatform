# Brand Voice Generator Tests

This document provides instructions for running the test scripts for the Brand Voice Generator feature.

## Test Structure

The tests are organized in three layers:

1. **Backend Tests**: Test the LangGraph agent and API endpoints
2. **Frontend Tests**: Test the frontend service and UI components
3. **End-to-End Tests**: Test the entire application workflow

## Prerequisites

- Backend server running on port 8001
- Frontend development server running on port 3000
- Python 3.8+ for backend tests
- Node.js 14+ for frontend tests
- Playwright installed for E2E tests (`npm install -D playwright`)

## Running Backend Tests

### 1. Test the Brand Voice Generator Agent

This test validates that the LangGraph agent correctly generates brand voice components.

```bash
cd /Users/nitinsareen/Documents/GitHub/nitin-sareen/ContentPlatform/backend
python -m tests.brand_voice_generator.test_generator_agent
```

### 2. Test the API Endpoints

This test validates that the FastAPI endpoints for the brand voice generator work correctly.

```bash
cd /Users/nitinsareen/Documents/GitHub/nitin-sareen/ContentPlatform/backend
python -m tests.brand_voice_generator.test_api_endpoints
```

## Running Frontend Tests

### 1. Test the Brand Voice Service

This test validates that the frontend service correctly communicates with the backend API.

```bash
cd /Users/nitinsareen/Documents/GitHub/nitin-sareen/ContentPlatform/frontend
npx jest tests/brand-voice-generator/test-brand-voice-service.js
```

### 2. Test the UI Components

This test validates that the React components for the brand voice generator work correctly.

```bash
cd /Users/nitinsareen/Documents/GitHub/nitin-sareen/ContentPlatform/frontend
npx jest tests/brand-voice-generator/test-generator-components.js
```

## Running End-to-End Tests

This test validates the entire brand voice generator workflow from the main application.

```bash
cd /Users/nitinsareen/Documents/GitHub/nitin-sareen/ContentPlatform
npx playwright test tests/e2e/brand_voice_generator_e2e.js
```

## Test Data

All tests use the same sample content for consistency:

```
At Eco-Friendly Solutions, we believe that small changes can make a big impact. 
Our sustainable products are designed with the planet in mind, using only 
recyclable materials and ethical manufacturing processes. 
We're committed to reducing waste and helping our customers live more 
environmentally conscious lives. Join us in our mission to create a greener future!
```

## Troubleshooting

### Backend Tests

- Make sure the backend server is running on port 8001
- Check that the LangGraph dependencies are installed
- Verify that the database migrations have been applied

### Frontend Tests

- Make sure the frontend development server is running
- Check that the API URL in the tests matches your backend server
- Verify that all UI components are correctly imported

### End-to-End Tests

- Make sure both backend and frontend servers are running
- Check that the APP_URL in the test matches your frontend server
- Increase the timeout values if tests fail due to slow responses

## Expected Results

All tests should pass with output similar to:

```
✅ All tests passed!
```

If a test fails, it will provide detailed error information to help diagnose the issue.
