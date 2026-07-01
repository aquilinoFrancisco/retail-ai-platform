import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Setup logging before imports to ensure all modules use configured handlers
import logging_config
from app.startup_checks import validate_runtime
from app.api.routes import router as api_router
from app.api.stream import router as stream_router

logger = logging.getLogger("retail_platform.main")

# Initialize FastAPI app
app = FastAPI(
    title="Retail Agentic Platform API",
    description="Enterprise-Grade LangGraph + CrewAI Multi-Agent Operational Triage Engine",
    version="0.1.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """
    On application startup, executes comprehensive environment validation checks 
    and caches the active connectivity configuration (Gemini LLM and crew models).
    """
    logger.info("Initializing Retail Agentic Platform API service...")
    
    # Run the validation
    runtime = validate_runtime()
    
    # Cache in the application state object
    app.state.runtime = runtime
    
    logger.info(
        f"Platform runtime loaded successfully. "
        f"Gemini LLM Integration: {'ENABLED' if runtime.get('gemini_enabled') else 'DISABLED'}. "
        f"Simulation fallback: {'ACTIVE' if runtime.get('simulation_mode') else 'INACTIVE'}."
    )

# Include API Routers
app.include_router(api_router)
app.include_router(stream_router)

# Entry point for standalone local testing
if __name__ == "__main__":
    import uvicorn
    # Bind port 3000 to listen behind the workspace proxy as required
    uvicorn.run("app.main:app", host="0.0.0.0", port=3000, reload=True)
