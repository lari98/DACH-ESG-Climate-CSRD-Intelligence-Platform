"""FastAPI serving layer — consumed by the R Shiny dashboard and any other client.

Run locally:
    uvicorn app.api.main:app --reload --port 8000

Docs:
    http://localhost:8000/docs
"""
from __future__ import annotations

import time
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.routes_ai import router as ai_router
from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.models import CO2Energy, CompanyESG, RegionalClimateRisk

logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def _lifespan(_app: FastAPI):
    # Startup: runs on every API start AND every uvicorn --reload auto-restart (i.e.
    # every time a code edit is picked up), so schema fixes AND data refreshes apply
    # themselves with no manual migration/refresh step ever required - see
    # app.db.session.ensure_schema_up_to_date and app.core.scheduler.
    from app.core.scheduler import start_background_refresh
    from app.db.session import init_db

    init_db()
    start_background_refresh()
    yield
    # (no shutdown work needed - the auto-refresh thread is a daemon thread)


app = FastAPI(title=settings.api_title, version=settings.api_version, lifespan=_lifespan)
app.include_router(ai_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production to the dashboard's origin
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000
    logger.info("%s %s -> %s (%.1fms)", request.method, request.url.path, response.status_code, duration_ms)
    return response


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "version": settings.api_version,
        "environment": settings.environment,
        "data_mode": settings.data_mode,
    }


@app.get("/api/v1/co2-energy")
def get_co2_energy(
    country: str | None = Query(None, description="Filter by ISO country code: DE, AT, CH"),
    year_from: int | None = None,
    year_to: int | None = None,
    db: Session = Depends(get_db),
) -> list[dict]:
    q = db.query(CO2Energy)
    if country:
        q = q.filter(CO2Energy.country_code == country.upper())
    if year_from:
        q = q.filter(CO2Energy.year >= year_from)
    if year_to:
        q = q.filter(CO2Energy.year <= year_to)
    rows = q.order_by(CO2Energy.country_code, CO2Energy.year).all()
    return [
        {c.name: getattr(r, c.name) for c in CO2Energy.__table__.columns}
        for r in rows
    ]


@app.get("/api/v1/climate-risk")
def get_climate_risk(
    country: str | None = Query(None, description="Filter by ISO country code: DE, AT, CH"),
    db: Session = Depends(get_db),
) -> list[dict]:
    q = db.query(RegionalClimateRisk)
    if country:
        q = q.filter(RegionalClimateRisk.country_code == country.upper())
    rows = q.order_by(RegionalClimateRisk.country_code, RegionalClimateRisk.region).all()
    return [
        {c.name: getattr(r, c.name) for c in RegionalClimateRisk.__table__.columns}
        for r in rows
    ]


@app.get("/api/v1/companies")
def get_companies(
    country: str | None = None,
    sector: str | None = None,
    db: Session = Depends(get_db),
) -> list[dict]:
    q = db.query(CompanyESG)
    if country:
        q = q.filter(CompanyESG.country_code == country.upper())
    if sector:
        q = q.filter(CompanyESG.sector == sector)
    rows = q.all()
    return [
        {c.name: getattr(r, c.name) for c in CompanyESG.__table__.columns}
        for r in rows
    ]


@app.get("/api/v1/companies/{company_id}")
def get_company(company_id: str, db: Session = Depends(get_db)) -> dict:
    row = db.query(CompanyESG).filter(CompanyESG.company_id == company_id).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return {c.name: getattr(row, c.name) for c in CompanyESG.__table__.columns}
