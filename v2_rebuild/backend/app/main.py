from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.auth import router as auth_router
from .api.marketplace import router as marketplace_router
from .api.contracts import router as contracts_router
from .models.user import User, StudentProfile, CoachProfile
from .models.marketplace import LearningRequest, Proposal, Contract, Session

from contextlib import asynccontextmanager
from .models.database import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title="Skileez V2 API",
    description="Refactored and modernized Skileez backend",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS for Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(marketplace_router)
app.include_router(contracts_router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Skileez V2 API",
        "status": "online",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
