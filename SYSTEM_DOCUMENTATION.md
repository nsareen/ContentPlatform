# Content Platform System Documentation

## Overview

The Content Platform is an enterprise-grade content management system with Brand Voice Studio capabilities, designed to help organizations create, manage, and maintain consistent brand voice across all content. The system leverages modern AI technologies, including agentic workflows powered by LangGraph, to provide intelligent content generation and analysis.

## System Architecture

### Backend (FastAPI)

The backend is built with FastAPI, providing a robust API layer for the frontend to interact with. It includes:

1. **Authentication System**
   - JWT-based authentication with development mode support
   - Multi-layered fallback mechanisms for development and testing
   - Database-first authentication for production use

2. **Agentic AI System**
   - LangGraph-based workflows for intelligent content operations
   - Intent classification for understanding user requests
   - Specialized tools for brand voice creation, content generation, and analysis

3. **Rich Media Processing**
   - Integration with OpenAI's DALL-E for image generation
   - Image description extraction from generated content
   - Comprehensive logging for debugging and transparency

4. **Database Layer**
   - PostgreSQL database for data persistence
   - Alembic for database migrations
   - Multi-tenant architecture supporting organization-specific data

### Frontend (Next.js)

The frontend is built with Next.js and follows modern React patterns:

1. **UI Components**
   - Shadcn UI for consistent component styling
   - Tailwind CSS for responsive design
   - Custom components like collapsible sidebar and header

2. **State Management**
   - React Context for global state
   - TanStack Query (react-query) for data fetching
   - React Hook Form with Zod validation for form handling

3. **Authentication Flow**
   - Client-side authentication with JWT tokens
   - Auth check components for protected routes
   - Development mode support with mock authentication

4. **Content Generation Interface**
   - Brand Voice Studio for creating and managing brand voices
   - Rich Media Playground for generating content with images
   - Real-time content preview and editing

## Key Components

### Brand Voice Agent

The Brand Voice Agent (`backend/app/agents/brand_voice_agent_v2.py`) is a LangGraph-based agent that handles:

- Creating and managing brand voice profiles
- Analyzing content against brand voice guidelines
- Generating content that adheres to brand voice specifications

The agent uses a true agentic workflow with proper intent classification and tool routing, following modern LangGraph patterns:

- Tool classes with type annotations for Pydantic v2 compatibility
- State management passing state through the graph
- Conditional routing using LangGraph's conditional edges
- Function wrappers for tool nodes to avoid tuple issues

### Rich Content Agent

The Rich Content Agent (`backend/app/agents/rich_content_agent.py`) specializes in generating content with embedded image descriptions:

- Processes user requests for content generation
- Extracts image descriptions from generated content
- Integrates with DALL-E to generate images based on descriptions
- Combines text and images into rich media content

Recent enhancements include comprehensive logging throughout the workflow for better debugging and transparency.

### Authentication System

The authentication system supports multiple authentication modes:

- Standard JWT-based authentication for production
- Development mode authentication with special tokens
- Mock authentication for offline testing
- Special handling for test credentials

### API Routes

The system exposes several API endpoints:

- `/api/auth/*` - Authentication endpoints
- `/api/tenant/*` - Tenant management
- `/api/user/*` - User management
- `/api/brand-voice/*` - Brand voice operations
- `/api/agent/*` - Direct agent interactions
- `/api/rich-content/*` - Rich content generation
- `/api/proxy/*` - Proxy endpoints for external services

## Troubleshooting Guide

### Authentication Issues

1. **Token Validation Failures**
   - Ensure the token URL matches the backend's OAuth2PasswordBearer configuration
   - Check that the frontend is using the correct API base URL
   - Verify that CORS headers are properly configured

2. **Tenant Authorization Issues**
   - Verify that tenant IDs match between frontend requests and backend user context
   - Query the database directly to confirm actual tenant values
   - Ensure consistency between frontend requests and database records

3. **Development Mode Authentication**
   - Use the `/api/dev-token` endpoint for valid JWT tokens in development
   - Special test credentials: admin@example.com/password123
   - Check that the mock authentication system is properly detecting development mode

### Brand Voice Agent Issues

1. **Agent Initialization Failures**
   - Verify that all dependencies are imported at the top level
   - Check that tool validation schemas match exactly what tools expect
   - Ensure proper state management through the graph

2. **Tool Invocation Problems**
   - Use proper LangGraph tool invocation patterns
   - Avoid bypassing LangGraph with direct function calls
   - Implement proper conditional routing with add_conditional_edges

### Image Generation Issues

1. **API Key Limitations**
   - Project-based API keys (sk-proj-...) may not have access to image generation APIs
   - Use standard API keys (sk-...) for image generation
   - Check OpenAI API key permissions and rate limits

2. **Image Description Extraction**
   - Verify that the content format includes proper image descriptions
   - Check the extraction patterns in the _extract_image_descriptions method
   - Add more logging to debug extraction issues

## Best Practices Implemented

### Backend Development

1. **Proper Environment Configuration**
   - Environment variables loaded from .env files
   - Fallback mechanisms for development and testing
   - Clear separation between development and production settings

2. **Modern LangGraph Patterns**
   - TypedDict for state management
   - ToolNode for tool invocation
   - Proper message handling
   - Conditional routing with add_conditional_edges

3. **Error Handling and Logging**
   - Comprehensive logging throughout the system
   - Detailed error messages for debugging
   - Graceful fallbacks for service unavailability

4. **API Design**
   - RESTful API design with consistent patterns
   - Proper validation with Pydantic schemas
   - Clear separation of concerns between routes, services, and models

### Frontend Development

1. **Component Architecture**
   - Functional components with TypeScript interfaces
   - Proper separation of concerns
   - Reusable UI components

2. **State Management**
   - React Context for global state
   - TanStack Query for data fetching
   - React Hook Form for form handling

3. **Styling**
   - Tailwind CSS for consistent styling
   - Shadcn UI for component design
   - Responsive design principles

4. **Authentication Flow**
   - Secure token handling
   - Protected routes with auth checks
   - Development mode support

## Planned Improvements (Backlog)

1. **Enhanced Agentic Capabilities**
   - Improve intent classification for more accurate tool selection
   - Add more specialized tools for different content types
   - Implement memory for persistent agent context

2. **Rich Media Enhancements**
   - Support for more image generation models
   - Video content generation
   - Interactive content elements

3. **User Experience Improvements**
   - Real-time collaboration features
   - Content versioning and history
   - Advanced content editing capabilities

4. **Performance Optimization**
   - Caching strategies for frequently accessed data
   - Optimized image processing
   - Improved API response times

5. **Analytics and Insights**
   - Content performance metrics
   - Brand voice consistency scoring
   - Usage analytics and reporting

## Development Environment Setup

### Backend Setup

1. Create a PostgreSQL database:
   ```bash
   createdb contentplatform
   ```

2. Install Python dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Run database migrations:
   ```bash
   cd backend
   alembic upgrade head
   ```

4. Start the backend server:
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```

### Frontend Setup

1. Install Node.js dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start the frontend development server:
   ```bash
   cd frontend
   npm run dev
   ```

## Version History

- **v1.0.0-agentic-logging** - Content Platform with enhanced agentic system logging and image generation capabilities
- **v1.0.0-rich-media-playground** - Rich Media Playground with working image generation

## Conclusion

The Content Platform represents a modern approach to content management, leveraging AI technologies to enhance content creation and brand consistency. The system's architecture is designed to be modular, extensible, and maintainable, with clear separation of concerns and well-defined interfaces between components.

Future development should focus on enhancing the agentic capabilities, improving the rich media generation, and optimizing the user experience while maintaining the current best practices and architectural patterns.
