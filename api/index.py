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

# CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    """Handle contact form submissions."""
    print(f"Incoming Transmission from {contact.email}: {contact.message}")
    return {"message": "Handshake initiated. Message received in neural queue."}

# --- Page Routes ---

@app.get("/")
async def read_index():
    # Assumes index.html is in 'public' folder
    file_path = os.path.join("public", "index.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return JSONResponse(status_code=404, content={"error": "Index artifact not found."})

@app.get("/about")
async def read_about():
    # Serves the new About Me page
    file_path = os.path.join("public", "about.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return JSONResponse(status_code=404, content={"error": "About page not found."})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)