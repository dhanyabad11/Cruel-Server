from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import deadline_routes, notification_settings_routes
from app.config import settings
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI instance
app = FastAPI(
    title="AI Cruel - Deadline Manager",
    description="A production-level deadline management system with portal scraping and smart notifications",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - Production-level configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include routers (NO AUTH - simplified)
app.include_router(deadline_routes.router, prefix="/api/deadlines", tags=["deadlines"])
app.include_router(notification_settings_routes.router, tags=["notification-settings"])

@app.get("/")
async def root():
    return {"message": "AI Cruel - Deadline Manager API", "version": "2.0.0", "database": "Neon PostgreSQL", "auto_deploy": "enabled"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-cruel-backend", "database": "neon"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )