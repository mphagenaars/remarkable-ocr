"""
Remarkable 2 naar Tekst Converter - Main Application
FastAPI web interface voor email configuratie en connectiviteit testing
"""

import os
import logging
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

# Import route modules
from routes.connection_routes import router as connection_router
from routes.polling_routes import router as polling_router
from routes.notification_routes import router as notification_router
from routes.admin_routes import router as admin_router

# Load environment variables
load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Remarkable 2 naar Tekst Converter",
    description="Automatische conversie van handgeschreven notities naar tekst",
    version="0.1.0"
)

# Setup templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include route modules
app.include_router(connection_router)
app.include_router(polling_router)
app.include_router(notification_router)
app.include_router(admin_router)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Hoofdpagina met email configuratie formulier"""
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
