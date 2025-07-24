"""
FairClaimRCM FastAPI Application

Main entry point for the healthcare revenue cycle management API.
Provides transparent coding and claims adjudication services.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from api.routes import claims, coding, terminology, audit
from api.models.database import engine, Base
from core.config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FairClaimRCM API",
    description="Transparent healthcare revenue cycle management and medical coding API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(claims.router, prefix="/api/v1/claims", tags=["claims"])
app.include_router(coding.router, prefix="/api/v1/coding", tags=["coding"])
app.include_router(terminology.router, prefix="/api/v1/terminology", tags=["terminology"])
app.include_router(audit.router, prefix="/api/v1/audit", tags=["audit"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to FairClaimRCM API",
        "version": "0.1.0",
        "docs": "/docs",
        "description": "Transparent healthcare revenue cycle management"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "fairclaimrcm-api"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
