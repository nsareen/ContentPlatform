# Import compatibility layers first to ensure they're applied before any other imports
from app.utils.pydantic_compat import *
from app.utils.langchain_patch import *
from app.utils.example_selector_patch import *  # Targeted patch for LengthBasedExampleSelector

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Content Platform API",
    description="Enterprise Content Platform with Brand Voice Studio",
    version="0.1.0",
)

# Import environment variables
import os

# Determine if we're in development mode
IS_DEV = os.environ.get('ENV', 'development') == 'development'

# Configure CORS - allow specific origins with credentials
app.add_middleware(
    CORSMiddleware,
    # In development, allow all localhost origins for easier testing
    # In production, explicitly list allowed origins for security
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:3004",
        "http://localhost:3005",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://127.0.0.1:3003",
        "http://127.0.0.1:3004",
        "http://127.0.0.1:3005",
        # Add any other frontend origins as needed
    ] if not IS_DEV else ["*"],  # Allow all origins in development mode for easier testing,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    # Explicitly list all headers that might be used
    allow_headers=[
        "Content-Type", 
        "Authorization", 
        "Accept", 
        "Origin", 
        "X-Requested-With",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
        "X-CSRF-Token"
    ],
    expose_headers=["*"],
    # Important: Set max age to reduce preflight requests
    max_age=86400  # 24 hours
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Content Platform API"}

# Import and include routers
from app.api.routes import auth, tenant, user, brand_voice, agent, rich_content, proxy, brand_voice_analysis, brand_voice_analyzer, brand_voice_generator

app.include_router(auth.router, prefix="/api")
app.include_router(tenant.router, prefix="/api")
app.include_router(user.router, prefix="/api")
app.include_router(brand_voice.router, prefix="/api")
app.include_router(agent.router, prefix="/api")
app.include_router(rich_content.router, prefix="/api")
app.include_router(proxy.router, prefix="/api")
app.include_router(brand_voice_analysis.router, prefix="/api")
app.include_router(brand_voice_analyzer.router, prefix="/api")
app.include_router(brand_voice_generator.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
