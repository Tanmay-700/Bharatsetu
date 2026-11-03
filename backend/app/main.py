import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.core.logger import logger
from app.api.v1.router import api_v1_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing BharatSetu backend service...")
    await init_db()
    # Pre-warm embedding model in background so document uploads and queries have 0s cold-start
    import asyncio
    from app.services.retrieval.embeddings import embedding_service
    asyncio.get_event_loop().run_in_executor(None, embedding_service._load_model)
    logger.info("BharatSetu backend startup complete.")
    yield
    logger.info("Shutting down BharatSetu backend...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Multilingual AI Study & Knowledge Companion with Dynamic Jev Domain Routing and Chat Memory",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1
app.include_router(api_v1_router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "embedding_model": settings.EMBEDDING_MODEL_NAME,
        "reranker_model": settings.RERANKER_MODEL_NAME,
        "supported_languages": list(settings.SUPPORTED_LANGUAGES.keys())
    }

@app.get("/")
async def root():
    return {
        "message": "Welcome to BharatSetu Multilingual AI Knowledge System",
        "docs_url": "/docs",
        "health_url": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
