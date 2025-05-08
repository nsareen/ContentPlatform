# Enterprise Content Platform

An enterprise-grade content platform with Brand Voice Studio capabilities, built using FastAPI for the backend and Next.js for the frontend.

## Project Structure

```
ContentPlatform/
├── backend/               # FastAPI backend
│   ├── alembic/           # Database migrations
│   ├── app/               # Application code
│   │   ├── api/           # API routes
│   │   ├── core/          # Core functionality
│   │   ├── db/            # Database configuration
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   └── utils/         # Utility functions
│   └── requirements.txt   # Python dependencies
└── frontend/              # Next.js frontend (to be implemented)
```

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL
- Node.js and npm (for frontend)

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
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000. You can access the Swagger UI documentation at http://localhost:8000/docs.

### Frontend Setup (Coming Soon)

The frontend will be implemented using Next.js with TypeScript, Tailwind CSS, and Shadcn UI components.

## Features

- Multi-tenant architecture
- Brand Voice Studio
- Content generation workflows
- Task management
- API for integrations
- Feedback and explainability

## API Endpoints

- `/api/token` - Authentication
- `/api/tenants` - Tenant management
- `/api/users` - User management
- `/api/voices` - Brand Voice management
- More endpoints coming soon...
