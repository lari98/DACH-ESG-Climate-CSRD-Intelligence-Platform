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
    co2_per_capita_t: float = Field(ge=0)
    renewable_share_pct: float = Field(ge=0, le=100)
    fossil_share_pct: float = Field(ge=0, le=100)
    nuclear_share_pct: float = Field(ge=0, le=100)
    electricity_generation_twh: float = Field(ge=0)
    electricity_price_eur_mwh: float = Field(ge=0)
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
