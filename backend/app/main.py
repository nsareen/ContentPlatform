from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Content Platform API",
    description="Enterprise Content Platform with Brand Voice Studio",
    version="0.1.0",
)

# Configure CORS - allow all origins in development mode
app.add_middleware(
    CORSMiddleware,
    # Use a wildcard to allow all origins in development mode
    allow_origins=["*"],  # This is safe for development but should be restricted in production
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
from app.api.routes import auth, tenant, user, brand_voice, agent, rich_content, proxy

app.include_router(auth.router, prefix="/api")
app.include_router(tenant.router, prefix="/api")
app.include_router(user.router, prefix="/api")
app.include_router(brand_voice.router, prefix="/api")
app.include_router(agent.router, prefix="/api")
app.include_router(rich_content.router, prefix="/api")
app.include_router(proxy.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
