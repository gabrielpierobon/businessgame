"""
Main entry point for the Business Game FastAPI application.
"""
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from app.api.routes import router as api_router
from app.db.mongodb import connect_to_mongo, close_mongo_connection

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Business Game",
    description="A turn-based business simulation game modeling a global manufacturing company as a Markov Decision Process",
    version="0.1.0",
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routes
app.include_router(api_router, prefix="/api")

# Setup startup and shutdown events
@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

# Include frontend routes
from app.api.frontend import router as frontend_router
app.include_router(frontend_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 