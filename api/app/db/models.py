"""SQLAlchemy ORM models for the serving layer (Gold-equivalent tables)."""
from __future__ import annotations

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class CO2Energy(Base):
    __tablename__ = "co2_energy"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    country_code: Mapped[str] = mapped_column(String(2), index=True)
    year: Mapped[int] = mapped_column(Integer, index=True)
    co2_emissions_mt: Mapped[float] = mapped_column(Float)
    co2_per_capita_t: Mapped[float] = mapped_column(Float)
    renewable_share_pct: Mapped[float] = mapped_column(Float)
    fossil_share_pct: Mapped[float] = mapped_column(Float)
    nuclear_share_pct: Mapped[float] = mapped_column(Float)
    electricity_generation_twh: Mapped[float] = mapped_column(Float)
    electricity_price_eur_mwh: Mapped[float] = mapped_column(Float)
    data_quality: Mapped[str] = mapped_column(String(20))


class RegionalClimateRisk(Base):
    __tablename__ = "regional_climate_risk"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    country_code: Mapped[str] = mapped_column(String(2), index=True)
    region: Mapped[str] = mapped_column(String(100), index=True)
    physical_risk_score: Mapped[float] = mapped_column(Float)
    transition_risk_score: Mapped[float] = mapped_column(Float)
    flood_risk_score: Mapped[float] = mapped_column(Float)
    heat_stress_score: Mapped[float] = mapped_column(Float)
    composite_climate_risk_score: Mapped[float] = mapped_column(Float)
    risk_level: Mapped[str] = mapped_column(String(10))
    data_quality: Mapped[str] = mapped_column(String(20))


class CompanyESG(Base):
    __tablename__ = "company_esg"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    company_name: Mapped[str] = mapped_column(String(200))
    country_code: Mapped[str] = mapped_column(String(2), index=True)
    sector: Mapped[str] = mapped_column(String(100))
    scope1_tco2e: Mapped[float] = mapped_column(Float)
    scope2_tco2e: Mapped[float] = mapped_column(Float)
    scope3_tco2e: Mapped[float] = mapped_column(Float)
    esg_readiness_score: Mapped[float] = mapped_column(Float)
    csrd_readiness_score: Mapped[float] = mapped_column(Float)
    reporting_gaps_count: Mapped[int] = mapped_column(Integer)
    data_quality: Mapped[str] = mapped_column(String(20))
