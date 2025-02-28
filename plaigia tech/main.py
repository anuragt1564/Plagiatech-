
from fastapi import FastAPI, Request, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from routes import plagiarism, rephrase, user
from config import settings
import redis.asyncio as redis
import uvicorn
import logging
import time
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PlagiaTech API",
    description="API for plagiarism checking and text rephrasing",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if settings.ENVIRONMENT == "production" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Error handling middleware
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Initialize rate limiter
@app.on_event("startup")
async def startup():
    try:
        # Connect to Redis for rate limiting
        redis_instance = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
        await FastAPILimiter.init(redis_instance)
        logger.info("Connected to Redis for rate limiting")
    except Exception as e:
        logger.warning(f"Failed to connect to Redis: {e}. Rate limiting disabled.")

# Shutdown event
@app.on_event("shutdown")
async def shutdown():
    logger.info("Shutting down API")

# Include routers with rate limiting
app.include_router(
    plagiarism.router, 
    prefix="/api",
    dependencies=[Depends(RateLimiter(times=100, seconds=3600))] if settings.ENVIRONMENT == "production" else []
)
app.include_router(
    rephrase.router, 
    prefix="/api",
    dependencies=[Depends(RateLimiter(times=100, seconds=3600))] if settings.ENVIRONMENT == "production" else []
)
app.include_router(user.router, prefix="/api")

# Serve static files (if needed)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return {
        "message": "Welcome to PlagiaTech API",
        "docs": "/api/docs",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# For running the app directly
if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=settings.PORT, 
        reload=settings.DEBUG
    )
