"""15. Personal-data classification test — this platform is designed to hold only
business-level / aggregate ESG data (see docs/04_data_freshness_and_accuracy.md and
the GDPR-safe design notes in docs/05_ai_llm_design.md), never personal data about
identifiable individuals. This test scans column names and cell values for common PII
signatures so an accidental personal-data column/value gets caught before it ever
reaches the database or an AI prompt."""
from __future__ import annotations

import re

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?:\+?\d[\d\-\s()]{7,}\d)")
IBAN_RE = re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{10,30}\b")

# Column-name signatures that would indicate personal (not company/business) data if
# ever added to the schema. company_name/company_id are business identifiers, not
# personal data, and are intentionally excluded here.
PII_COLUMN_NAME_SIGNATURES = [
    "email", "e_mail", "phone", "telefon", "ssn", "social_security",
    "date_of_birth", "dob", "birth_date", "geburtsdatum", "personal_id",
    "passport", "national_id", "home_address", "street_address", "iban",
    "credit_card", "salary", "first_name", "last_name", "given_name", "surname",
]


def _check_no_pii_columns(df, dataset_name):
    lowered_cols = [c.lower() for c in df.columns]
    for sig in PII_COLUMN_NAME_SIGNATURES:
        hits = [c for c in lowered_cols if sig in c]
        assert not hits, f"{dataset_name} has a column matching PII signature '{sig}': {hits}"


def _check_no_pii_values(df, dataset_name, text_columns):
    for col in text_columns:
        if col not in df.columns:
            continue
        for value in df[col].dropna().astype(str):
            assert not EMAIL_RE.search(value), (
                f"{dataset_name}.{col} contains what looks like an email address: {value!r}"
            )
            assert not IBAN_RE.search(value), (
                f"{dataset_name}.{col} contains what looks like an IBAN: {value!r}"
            )


def test_co2_energy_has_no_pii_columns(co2_energy_df):
    _check_no_pii_columns(co2_energy_df, "co2_energy")


def test_regional_climate_risk_has_no_pii_columns(regional_climate_risk_df):
    _check_no_pii_columns(regional_climate_risk_df, "regional_climate_risk")


def test_company_esg_has_no_pii_columns(company_esg_df):
    _check_no_pii_columns(company_esg_df, "company_esg")


def test_company_esg_text_values_contain_no_pii(company_esg_df):
    _check_no_pii_values(company_esg_df, "company_esg", ["company_name", "sector", "company_id"])


def test_company_esg_is_business_level_not_individual_level(company_esg_df):
    """Every row must represent a company (aggregate), not a natural person - a cheap
    proxy check is that company_id/company_name values shouldn't look like a personal
    'First Last' two-word name with no business-entity suffix, though this is
    intentionally lenient (informational bound, not a hard legal classifier)."""
    suspicious = 0
    for name in company_esg_df["company_name"].dropna().astype(str):
        words = name.split()
        looks_like_person = (
            len(words) == 2 and all(w[:1].isupper() and w[1:].islower() for w in words if w)
        )
        if looks_like_person:
            suspicious += 1
    rate = suspicious / max(1, len(company_esg_df))
    assert rate < 0.05, (
        f"{suspicious} company_name value(s) ({rate:.0%}) look like personal names "
        f"rather than business entities - review for accidental personal data"
    )
