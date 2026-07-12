"""Pydantic validation models — the contract every record must satisfy before
promotion into the serving database (equivalent to a Gold-layer schema gate)."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

DataQuality = Literal["official", "estimated", "sample"]
CountryCode = Literal["DE", "AT", "CH"]


class CO2EnergyRecord(BaseModel):
    country_code: CountryCode
    year: int = Field(ge=1990, le=2100)
    co2_emissions_mt: float = Field(ge=0)
    renewable_share_pct: float = Field(ge=0, le=100)
    # Genuinely required fields end here (matches clean.REQUIRED_CO2_ENERGY_COLUMNS).
    # Everything below is optional: free live sources (OWID) don't publish all of these
    # for every country/year, e.g. electricity price isn't published by OWID at all -
    # treating them as required previously caused every live-sourced row to silently
    # fail the 95% quality gate and never reach the database.
    co2_per_capita_t: float | None = Field(default=None, ge=0)
    fossil_share_pct: float | None = Field(default=None, ge=0, le=100)
    nuclear_share_pct: float | None = Field(default=None, ge=0, le=100)
    electricity_generation_twh: float | None = Field(default=None, ge=0)
    electricity_price_eur_mwh: float | None = Field(default=None, ge=0)
    data_quality: DataQuality = "sample"


class RegionalClimateRiskRecord(BaseModel):
    country_code: CountryCode
    region: str
    physical_risk_score: float = Field(ge=0, le=10)
    transition_risk_score: float = Field(ge=0, le=10)
    flood_risk_score: float = Field(ge=0, le=10)
    heat_stress_score: float = Field(ge=0, le=10)
    composite_climate_risk_score: float = Field(ge=0, le=10)
    risk_level: Literal["Low", "Medium", "High"]
    data_quality: DataQuality = "sample"


class CompanyESGRecord(BaseModel):
    company_id: str
    company_name: str
    country_code: CountryCode
    sector: str
    scope1_tco2e: float = Field(ge=0)
    scope2_tco2e: float = Field(ge=0)
    scope3_tco2e: float = Field(ge=0)
    esg_readiness_score: float = Field(ge=0, le=100)
    csrd_readiness_score: float = Field(ge=0, le=100)
    reporting_gaps_count: int = Field(ge=0)
    data_quality: DataQuality = "sample"

    @field_validator("company_id")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("company_id must not be blank")
        return v
