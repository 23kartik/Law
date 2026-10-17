from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import case, courts, draft, research

app = FastAPI(title="Legal Advocacy Platform API", version="0.1.0")

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(case.router)
app.include_router(research.router)
app.include_router(courts.router)
app.include_router(draft.router)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
