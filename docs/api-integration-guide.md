# Content Platform API Integration Guide

This guide provides comprehensive documentation for integrating with the Content Platform API, with a focus on brand voice functionality.

## Table of Contents

1. [API Architecture](#api-architecture)
2. [Authentication](#authentication)
3. [Brand Voice API](#brand-voice-api)
4. [Content Generation API](#content-generation-api)
5. [Error Handling](#error-handling)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## API Architecture

The Content Platform uses a layered API architecture:

```
Frontend (Next.js) <--> API Proxy <--> Backend (FastAPI)
```

For reliable integration, especially during development and debugging, we recommend using direct backend access:

```typescript
// Direct backend access pattern
const directUrl = `${DIRECT_BACKEND_URL}/api/endpoint`;
const response = await fetch(directUrl, {
  method: 'METHOD',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify(data)
});
```

## Authentication

All API endpoints require authentication using JWT tokens:

```typescript
// Authentication headers
const headers = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${token}`
};
```

For development, you can use the DEV_TOKEN from the constants file:

```typescript
import { DEV_TOKEN } from '@/lib/api/constants';
```

## Brand Voice API

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/voices/` | GET | Get brand voices for current tenant |
| `/api/voices/all/` | GET | Get all brand voices (admin only) |
| `/api/voices/{id}/` | GET | Get a specific brand voice |
| `/api/voices/` | POST | Create a new brand voice |
| `/api/voices/{id}` | PUT | Update a brand voice |
| `/api/voices/{id}/versions/` | GET | Get versions of a brand voice |
| `/api/voices/{id}/versions/{version}/restore/` | POST | Restore a previous version |
| `/api/voices/{id}/analyze/` | POST | Analyze a brand voice |

### Example: Fetching Brand Voices

```typescript
// Using direct backend access for reliability
const getAllBrandVoices = async (): Promise<BrandVoice[]> => {
  try {
    const directUrl = `${DIRECT_BACKEND_URL}/api/voices/all/`;
    
    const response = await fetch(directUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${DEV_TOKEN}`
      }
    });
    
    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Failed to get brand voices:', error);
    throw error;
  }
};
```

### Example: Updating a Brand Voice

```typescript
const updateBrandVoice = async (id: string, data: BrandVoiceUpdateRequest): Promise<BrandVoice> => {
  try {
    const directUrl = `${DIRECT_BACKEND_URL}/api/voices/${id}`;
    
    const response = await fetch(directUrl, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${DEV_TOKEN}`
      },
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Server error response:`, errorText);
      throw new Error(`Request failed with status ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Failed to update brand voice with ID ${id}:`, error);
    throw error;
  }
};
```

## Content Generation API

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/agent/generate` | POST | Generate content using a brand voice |
| `/api/agent/analyze` | POST | Analyze content for brand voice characteristics |
| `/api/agent/chat` | POST | Chat with the brand voice agent |

### Example: Generating Content

```typescript
const generateContent = async (brandVoiceId: string, prompt: string): Promise<any> => {
  try {
    const directUrl = `${DIRECT_BACKEND_URL}/api/agent/generate`;
    
    const response = await fetch(directUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${DEV_TOKEN}`
      },
      body: JSON.stringify({
        brand_voice_id: brandVoiceId,
        prompt: prompt,
        content_type: 'general'
      })
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Server error response:`, errorText);
      throw new Error(errorText || 'Failed to generate content');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error generating content:', error);
    throw error;
  }
};
```

## Error Handling

Implement robust error handling for all API calls:

```typescript
try {
  // API call
} catch (error) {
  // Log detailed error information
  console.error(`[Component] Error details:`, error);
  
  // Extract error message for display
  let errorMessage = 'An unknown error occurred';
  if (error instanceof Error) {
    errorMessage = error.message;
  }
  
  // Display user-friendly error
  setErrorMessage(`Failed to complete operation: ${errorMessage}`);
}
```

## Best Practices

1. **Direct Backend Access**: For reliable API communication, use direct backend access with consistent authentication.

2. **Consistent Authentication**: Use a centralized token management approach.

3. **Error Handling**: Log detailed error information and provide user-friendly error messages.

4. **Versioning**: When making significant changes to brand voices, ensure proper versioning.

5. **Authorization**: Always check user roles and tenant access in backend routes.

## Troubleshooting

### Common Issues

1. **404 Not Found Errors**:
   - Check the exact endpoint URL format (trailing slashes matter)
   - Verify that you're using the correct HTTP method
   - Ensure the resource ID is valid

2. **401 Unauthorized Errors**:
   - Verify that the authentication token is valid and not expired
   - Check that the token is included in the Authorization header

3. **403 Forbidden Errors**:
   - Verify that the user has the correct role and tenant access
   - Check backend logs for detailed authorization failure information

4. **500 Internal Server Errors**:
   - Check backend logs for detailed error information
   - Verify that all required fields are included in the request
   - Check for database constraints that might be violated

### Debugging Tools

1. **Console Logging**: Add detailed logging with component prefixes.

2. **Network Monitoring**: Use browser developer tools to inspect network requests.

3. **Backend Logs**: Check server logs for detailed error information.

4. **Test Cases**: Run the test suite to verify API functionality.

## Adding New Components

When adding new components that interact with the API:

1. **API Configuration**:
   - Add new endpoints to the appropriate configuration file
   - Follow the established naming conventions

2. **Service Layer**:
   - Create a dedicated service file for the new component
   - Implement methods for all required API operations
   - Use the direct backend access pattern for reliability

3. **Error Handling**:
   - Implement consistent error handling
   - Log detailed error information
   - Provide user-friendly error messages

4. **Testing**:
   - Create unit tests for all API methods
   - Test both success and error scenarios
   - Verify authorization requirements

5. **Documentation**:
   - Update this guide with new endpoints and examples
   - Document any special considerations for the new component
