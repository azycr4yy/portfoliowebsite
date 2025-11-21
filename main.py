import os
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# --- Configuration ---
app = FastAPI(
    title="Udayan J // Neural Architect Portfolio",
    description="Backend API for portfolio hosting and ML model inference demos.",
    version="2.4.0"
)

# CORS (Cross-Origin Resource Sharing) - Vital for frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models ---
class ContactRequest(BaseModel):
    email: str
    message: str
    source: Optional[str] = "portfolio_v2"

# --- API Endpoints ---

@app.get("/api/health")
async def health_check():
    """System Status Check for Footer Display"""
    return {
        "status": "ONLINE",
        "timestamp": datetime.now().isoformat(),
        "location": "LATENT_SPACE",
        "latency": "12ms"
    }

@app.post("/api/contact")
async def handle_contact(contact: ContactRequest):
    """
    Handle contact form submissions. 
    TODO: Integrate SendGrid or SMTP here.
    """
    print(f"Incoming Transmission from {contact.email}: {contact.message}")
    # Simulate processing time
    return {"message": "Handshake initiated. Message received in neural queue."}

# --- Static File Serving ---
# Mounts the 'public' directory to serve CSS/JS/Images if you separate them later
# app.mount("/static", StaticFiles(directory="public/static"), name="static")

# Serve the main Single Page Application (SPA)
@app.get("/")
async def read_index():
    # Assumes your index.html is in a folder named 'public'
    file_path = os.path.join("public", "index.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return JSONResponse(status_code=404, content={"error": "Index artifact not found."})

# --- Entry Point ---
if __name__ == "__main__":
    # Use PORT environment variable for deployment platforms (Railway/Render/Heroku)
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)