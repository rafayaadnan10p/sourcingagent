from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.limiter import limiter
from app.routers import jd, search, export

settings = get_settings()

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="AI Sourcing Agent", version="0.1.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,   # never wildcard
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(jd.router)
app.include_router(search.router)
app.include_router(export.router)


@app.get("/health")
def health():
    return {"status": "ok"}
