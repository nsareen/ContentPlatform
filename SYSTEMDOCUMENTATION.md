# Content Platform System Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Backend Configuration](#backend-configuration)
4. [Frontend Configuration](#frontend-configuration)
5. [Authentication System](#authentication-system)
6. [API Integration](#api-integration)
7. [CORS Configuration](#cors-configuration)
8. [Common Issues and Solutions](#common-issues-and-solutions)
9. [Development Workflow](#development-workflow)
10. [Troubleshooting Guide](#troubleshooting-guide)

## System Overview

The Content Platform is a web application for creating, managing, and analyzing brand voices. It consists of a Next.js frontend and FastAPI backend with PostgreSQL database. The system allows users to:

- Create and manage brand voices
- Analyze content against brand voice guidelines
- Manage different versions of brand voices
- Filter brand voices by tenant

## Architecture

### High-Level Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Next.js        │────▶│  FastAPI        │────▶│  PostgreSQL     │
│  Frontend       │     │  Backend        │     │  Database       │
│                 │◀────│                 │◀────│                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Component Overview

- **Frontend**: Next.js application with App Router, Tailwind CSS, and custom API client
- **Backend**: FastAPI application with SQLAlchemy ORM, JWT authentication, and CORS middleware
- **Database**: PostgreSQL in production, SQLite for local development

## Backend Configuration

### Framework and Dependencies
- **Framework**: FastAPI
- **Database ORM**: SQLAlchemy
- **Authentication**: JWT Bearer tokens with OAuth2PasswordBearer
- **Port**: 8000
- **API Base URL**: http://localhost:8000
- **API Prefix**: /api

### Key Backend Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/token` | POST | Authentication token endpoint |
| `/api/dev-token` | GET | Development token endpoint (development only) |
| `/api/voices/` | GET | Brand voice endpoint with tenant filtering |
| `/api/voices/all/` | GET | Special endpoint to get all brand voices without tenant filtering |
| `/api/voices/{id}/` | GET/PUT/DELETE | Specific brand voice operations |
| `/api/voices/{id}/analyze/` | POST | Brand voice analysis endpoint |
| `/api/voices/{id}/versions/` | GET | Get all versions of a brand voice |
| `/api/voices/{id}/versions/{version_id}/restore/` | POST | Restore a previous version |

### Database Models

The system uses the following key models:

- **Tenant**: Represents a tenant in the system
- **User**: Represents a user with role and tenant association
- **BrandVoice**: Represents a brand voice with versions
- **ContentProject**: Represents a content project associated with a brand voice
- **Task**: Represents a task in a content project

### CORS Configuration

The backend has CORS middleware configured in `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3010", "http://127.0.0.1:60597"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Frontend Configuration

### Framework and Dependencies
- **Framework**: Next.js with App Router
- **Port**: 3000 (may use alternative ports like 3010 if 3000 is in use)
- **API Client**: Custom implementation using fetch/XMLHttpRequest
- **State Management**: React Context
- **Styling**: Tailwind CSS

### Key Frontend Files
- `src/config/api-config.ts` - API configuration including URLs and environment detection
- `src/lib/api/brand-voice-service.ts` - Brand voice API service
- `src/lib/auth/auth-service.ts` - Authentication service
- `src/app/brand-voices/page.tsx` - Brand voices listing page
- `src/app/brand-voices/[id]/edit/page.tsx` - Brand voice edit page
- `src/components/brand-voice/brand-voice-form.tsx` - Brand voice form component

### Environment Detection

The frontend uses several environment detection mechanisms:

```typescript
// Detect environment
export const isDevelopment = process.env.NODE_ENV !== 'production';

// Detect if we're running in the browser preview proxy
export const isProxyEnvironment = typeof window !== 'undefined' && 
  window.location.hostname.includes('127.0.0.1') && 
  !['3000', '3001', '3002', '3003', '3004', '3005'].includes(window.location.port);
```

### API Configuration

The frontend uses hardcoded backend URL and token for maximum reliability:

```typescript
// Backend URL - hardcoded for reliability
const BACKEND_URL = 'http://localhost:8000';

// Hardcoded token for development
const DEV_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTEyMyIsInRlbmFudF9pZCI6InRlbmFudC0xMjMiLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3NDY2MTA2NjZ9.056qf8G2X03J4obGB4fkB1YW6AtTdn1nU2A8G7a2uzI';
```

## Authentication System

### Token Structure

The system uses JWT tokens with the following claims:
- `sub`: User ID (e.g., "user-123")
- `tenant_id`: Tenant identifier (e.g., "tenant-123")
- `role`: User role (e.g., "admin")
- `exp`: Expiration timestamp

### Working Development Token

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTEyMyIsInRlbmFudF9pZCI6InRlbmFudC0xMjMiLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3NDY2MTA2NjZ9.056qf8G2X03J4obGB4fkB1YW6AtTdn1nU2A8G7a2uzI
```

### Backend Authentication Implementation

- Located in `backend/app/core/auth.py`
- Uses `OAuth2PasswordBearer` from FastAPI
- Development mode bypasses strict validation
- Token URL is configured as `/token` (becomes `/api/token` with prefix)

### Frontend Authentication Implementation

- Located in `frontend/src/lib/auth/auth-service.ts`
- Multiple token retrieval methods with fallbacks
- Hardcoded development token for reliability

## API Integration

### Authentication Implementation

- **Token Management**: Use the centralized auth service for all token operations
- **Token Format**: Always use `Bearer {token}` in Authorization header
- **Token Endpoints**: 
  - Production: `/api/token`
  - Development: `/api/dev-token`

### URL Construction

- **Base URL**: Always use `http://localhost:8000` for local development
- **API Prefix**: All endpoints must include `/api` prefix
- **Trailing Slashes**: FastAPI endpoints require trailing slashes (e.g., `/api/voices/`)
- **Full URL Example**: `http://localhost:8000/api/voices/`

### Error Handling

- Implement comprehensive error handling with detailed logging
- Include fallback mechanisms for critical operations
- Log both error messages and stack traces for debugging
- Use try/catch blocks around all API calls

### Direct API Access

For maximum reliability, use direct fetch with hardcoded token:

```typescript
const response = await fetch('http://localhost:8000/api/voices/all/', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTEyMyIsInRlbmFudF9pZCI6InRlbmFudC0xMjMiLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3NDY2MTA2NjZ9.056qf8G2X03J4obGB4fkB1YW6AtTdn1nU2A8G7a2uzI'
  },
  mode: 'cors'
});
```

### Tenant Filtering and Authorization Model

#### Tenant Filtering in API Endpoints

- Standard endpoints filter by tenant_id: `/api/voices/`
- To get all brand voices regardless of tenant: `/api/voices/all/`
- Admin role is required for cross-tenant operations

#### Cross-Tenant Access for Admin Users

The system implements a consistent authorization model across all endpoints that allows admin users to access resources from any tenant:

1. **API Endpoints Authorization**:
   - All API endpoints that access tenant-specific resources include a tenant check with an admin role exception
   - Example implementation pattern:
   ```python
   # Check if user belongs to the tenant or is an admin
   if resource.tenant_id != current_user.tenant_id and current_user.role != UserRole.ADMIN:
       raise HTTPException(
           status_code=status.HTTP_403_FORBIDDEN,
           detail="Not authorized to access this resource"
       )
   ```

2. **Agent Implementation Authorization**:
   - Agent implementations (brand_voice_agent_v1.py, rich_content_agent_v1.py) retrieve resources without tenant filtering
   - This allows admin users to access resources from any tenant once they pass the API authorization check
   - Example implementation pattern:
   ```python
   # Get the resource from the database without tenant filtering
   # This allows admin users to access resources from any tenant
   db_resource = db.query(ResourceModel).filter(
       ResourceModel.id == resource_id
   ).first()
   ```

#### Affected Modules and Components

The following components implement the tenant filtering and admin cross-tenant access model:

1. **API Routes**:
   - `app/api/routes/brand_voice.py`: Brand voice endpoints
   - `app/api/routes/agent.py`: Content generation endpoints
   - `app/api/routes/rich_content.py`: Rich content generation endpoints

2. **Agent Implementations**:
   - `app/agents/brand_voice_agent_v1.py`: Brand voice agent implementation
   - `app/agents/rich_content_agent_v1.py`: Rich content agent implementation

3. **Frontend Services**:
   - `src/lib/api/brand-voice-service.ts`: Brand voice API service
   - `src/components/brand-voice/rich-playground-panel-fixed.tsx`: Rich playground panel

#### Token Structure and Tenant Information

The JWT token contains the tenant_id and role information used for authorization:

```json
{
  "sub": "user-123",
  "tenant_id": "tenant-123",
  "role": "admin",
  "exp": 1746610666
}
```

- The `tenant_id` claim is used to filter resources by tenant
- The `role` claim is used to determine if a user can access resources from other tenants
- Admin users (`role="admin"`) can access resources from any tenant

## CORS Configuration

### Required CORS Headers

- `Access-Control-Allow-Origin`: Must match the frontend origin exactly
- `Access-Control-Allow-Credentials`: Must be set to `true` for authenticated requests
- `Access-Control-Allow-Methods`: Should include all HTTP methods used
- `Access-Control-Allow-Headers`: Must include `Authorization` and `Content-Type`

### Browser Preview Environment

- Browser preview runs on a different port (e.g., `127.0.0.1:60597`)
- This origin must be explicitly added to the CORS allowed origins
- Check the actual port in the browser URL and add it if needed

## Common Issues and Solutions

### CORS Issues

- Ensure all frontend origins are added to the backend CORS configuration
- Use consistent URL formats with proper protocol, domain, and port
- For browser preview environments, add the preview port to allowed origins

### Authentication Issues

- Use a consistent token format across all requests
- Include proper Authorization header: `Bearer <token>`
- For development, use the hardcoded token that's known to work
- Check token expiration and implement refresh logic
- Ensure the user associated with the token exists in the database
- Verify that the token contains the correct tenant_id and role claims

### Tenant and Authorization Issues

- **403 Forbidden errors**: Check if the user's tenant_id matches the resource's tenant_id or if the user has admin role
- **Missing resources**: Verify that the endpoint is not applying tenant filtering when it shouldn't
- **Cross-tenant access**: Ensure the user has the admin role when accessing resources from other tenants
- **Agent implementation issues**: Check if the agent is applying tenant filtering in database queries

### API Endpoint Issues

- Always use full URLs with backend address for all endpoints
- Include trailing slashes for FastAPI endpoints
- Use the special `/api/voices/all/` endpoint to get all brand voices without tenant filtering
- Ensure consistent error handling and logging for all API requests
- When implementing new endpoints, follow the established pattern for tenant filtering with admin exceptions

### Common Authentication Errors

#### 401 Unauthorized
- **Possible causes**:
  - Missing Authorization header
  - Invalid token format (missing "Bearer" prefix)
  - Expired token
  - Token signed with wrong key
  - User not found in database

#### 403 Forbidden
- **Possible causes**:
  - User lacks required permissions
  - Tenant mismatch (trying to access resources from another tenant)
  - Role insufficient for the requested operation

## Development Workflow

1. Start the backend server:
   ```bash
   cd backend && python -m uvicorn app.main:app --reload --port 8000
   ```

2. Start the frontend server:
   ```bash
   cd frontend && npm run dev
   ```

3. Access the application at http://localhost:3000 or the alternative port

## Troubleshooting Guide

### Step-by-Step Tenant and Authorization Debugging

1. **Verify user and tenant existence**:
   ```bash
   # Connect to the database and check if the user exists
   cd backend && python -c "from app.db.database import SessionLocal; from app.models.models import User; db = SessionLocal(); user = db.query(User).filter(User.id == 'user-123').first(); print(f'User ID: {user.id}, Tenant ID: {user.tenant_id}, Role: {user.role}') if user else print('User not found'); db.close()"
   ```

2. **Check brand voice tenant association**:
   ```bash
   # Connect to the database and check brand voice tenant ID
   cd backend && python -c "from app.db.database import SessionLocal; from app.models.models import BrandVoice; db = SessionLocal(); voices = db.query(BrandVoice).all(); print('Brand voice IDs and their tenant IDs:'); [print(f'- {voice.id}: {voice.name} (tenant: {voice.tenant_id})') for voice in voices[:5]]; db.close()"
   ```

3. **Verify tenant authorization in API endpoints**:
   - Check if the API endpoint has the admin role exception in the tenant check
   - Look for code like: `if resource.tenant_id != current_user.tenant_id and current_user.role != UserRole.ADMIN:`

4. **Verify tenant filtering in agent implementations**:
   - Check if the agent implementation is applying tenant filtering in database queries
   - Look for code like: `db_voice = db.query(BrandVoice).filter(BrandVoice.id == brand_voice_id, BrandVoice.tenant_id == tenant_id).first()`
   - This should be changed to: `db_voice = db.query(BrandVoice).filter(BrandVoice.id == brand_voice_id).first()`

5. **Test with direct API calls**:
   ```bash
   # Test accessing a brand voice from another tenant with admin token
   curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTEyMyIsInRlbmFudF9pZCI6InRlbmFudC0xMjMiLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3NDY2MTA2NjZ9.056qf8G2X03J4obGB4fkB1YW6AtTdn1nU2A8G7a2uzI" http://localhost:8000/api/voices/9a71c7d2-7c17-4cb8-9958-7a0588e988ec/
   ```

### Step-by-Step Authentication Debugging

1. **Verify token format**:
   ```
   Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTEyMyIsInRlbmFudF9pZCI6InRlbmFudC0xMjMiLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3NDY2MTA2NjZ9.056qf8G2X03J4obGB4fkB1YW6AtTdn1nU2A8G7a2uzI
   ```

2. **Check token expiration**:
   - Decode the token at jwt.io to verify expiration
   - Current working token expires in 2025

3. **Verify CORS headers**:
   - Use browser Network tab to inspect preflight requests
   - Check if the `Access-Control-Allow-Origin` header matches your frontend origin

4. **Test with direct API call**:
   ```bash
   curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTEyMyIsInRlbmFudF9pZCI6InRlbmFudC0xMjMiLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3NDY2MTA2NjZ9.056qf8G2X03J4obGB4fkB1YW6AtTdn1nU2A8G7a2uzI" http://localhost:8000/api/voices/all/
   ```

5. **Check backend logs**:
   - Look for JWT validation errors
   - Check for CORS-related messages
   - Verify the user lookup process

### API Request Checklist

Before making any API request, ensure:

1. ✅ Full URL with correct protocol, domain, and port
2. ✅ Proper API prefix (/api)
3. ✅ Trailing slash for FastAPI endpoints
4. ✅ Authorization header with Bearer token
5. ✅ Correct Content-Type header
6. ✅ CORS mode set to 'cors'
7. ✅ Proper error handling with detailed logging

### Adding New API Endpoints

When adding new API endpoints:

1. **Backend**:
   - Add route to appropriate router file
   - Include proper authentication dependencies
   - Add CORS configuration if needed
   - Implement proper error handling
   - Add tenant filtering where appropriate

2. **Frontend**:
   - Add endpoint to `src/config/api-config.ts`
   - Create service method using direct fetch approach
   - Include proper error handling and logging
   - Use full URLs with backend address
   - Include proper authorization headers

### Testing New Endpoints

1. Test directly with curl or Postman
2. Verify CORS headers in browser network tab
3. Check authentication token validity
4. Implement detailed logging for debugging

### Common Pitfalls

- Missing trailing slashes in FastAPI endpoints
- Inconsistent URL formats between frontend and backend
- Missing or incorrect Authorization headers
- Not handling CORS properly for browser preview environments
- Filtering by tenant_id when all records are needed
