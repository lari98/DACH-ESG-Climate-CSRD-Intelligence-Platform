"""Database tests: schema creation, load-then-query roundtrip, uniqueness constraints."""
import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import Base, CO2Energy, CompanyESG


@pytest.fixture()
def db_session(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path}/test.db")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_schema_creates_all_tables(db_session):
    tables = Base.metadata.tables.keys()
    assert {"co2_energy", "regional_climate_risk", "company_esg"}.issubset(tables)


def test_insert_and_query_co2_energy(db_session):
    row = CO2Energy(
        country_code="DE", year=2023, co2_emissions_mt=666.0, co2_per_capita_t=7.9,
        renewable_share_pct=51.6, fossil_share_pct=42.2, nuclear_share_pct=6.2,
        electricity_generation_twh=585.6, electricity_price_eur_mwh=78.8, data_quality="sample",
    )
    db_session.add(row)
    db_session.commit()
    result = db_session.query(CO2Energy).filter_by(country_code="DE", year=2023).first()
    assert result is not None
    assert result.co2_emissions_mt == 666.0


def test_company_id_unique_constraint(db_session):
    c1 = CompanyESG(
        company_id="X-1", company_name="A", country_code="DE", sector="Energy",
        scope1_tco2e=1, scope2_tco2e=1, scope3_tco2e=1,
        esg_readiness_score=50, csrd_readiness_score=50, reporting_gaps_count=0, data_quality="sample",
    )
    db_session.add(c1)
    db_session.commit()

    c2 = CompanyESG(
        company_id="X-1", company_name="B", country_code="AT", sector="Finance",
        scope1_tco2e=1, scope2_tco2e=1, scope3_tco2e=1,
        esg_readiness_score=60, csrd_readiness_score=60, reporting_gaps_count=1, data_quality="sample",
    )
    db_session.add(c2)
    with pytest.raises(Exception):
        db_session.commit()
