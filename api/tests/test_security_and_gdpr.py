"""Security and GDPR checks.

These are lightweight, automatable checks that catch the most common regressions
(secrets leaking into responses, permissive CORS in a way that's undocumented,
personal-data fields creeping into the schema). They are not a substitute for a
full security review / pen test before production launch — see
docs/08_testing_strategy.md for the manual review checklist.
"""
import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from fastapi.testclient import TestClient

from app.api.main import app
from app.core.config import get_settings
from app.db.models import CO2Energy, CompanyESG, RegionalClimateRisk
from app.db.session import init_db

init_db()  # ensure tables exist on the in-memory/test DB before any request-based test runs
client = TestClient(app)

# GDPR: fields that would indicate individual-level personal data leaking into the schema
PERSONAL_DATA_INDICATORS = {
    "email", "phone", "ssn", "national_id", "date_of_birth", "full_name",
    "address", "ip_address", "passport", "tax_id",
}


def test_no_personal_data_fields_in_schema():
    """GDPR check: the platform is designed to hold only aggregate/company-level
    data, never individual personal data (see docs/02_architecture.md)."""
    for model in (CO2Energy, RegionalClimateRisk, CompanyESG):
        columns = {c.name.lower() for c in model.__table__.columns}
        overlap = columns & PERSONAL_DATA_INDICATORS
        assert not overlap, f"{model.__name__} unexpectedly has personal-data-like columns: {overlap}"


def test_health_endpoint_does_not_leak_secrets():
    resp = client.get("/health")
    body = resp.text.lower()
    for secret_marker in ("api_key", "password", "secret", "connection_string"):
        assert secret_marker not in body


def test_settings_never_hardcode_a_real_looking_secret():
    """Guards against accidentally committing a real-looking Azure key as a default."""
    settings = get_settings()
    assert settings.azure_openai_api_key in (None, "")
    assert settings.azure_sql_connection_string in (None, "")


def test_company_id_path_param_is_not_vulnerable_to_basic_sql_injection_string():
    """The ORM layer parameterizes queries; this just documents/asserts that a
    classic injection-style string doesn't 500 the app or return unexpected data."""
    resp = client.get("/api/v1/companies/'; DROP TABLE company_esg; --")
    assert resp.status_code in (404, 200)  # handled safely either way, never a 500


def test_cors_is_explicitly_configured_not_silently_absent():
    """Documents current dev-mode CORS policy (allow all) so it's a visible,
    intentional choice to tighten before production rather than a silent gap."""
    from app.api.main import app as fastapi_app
    middleware_classes = [m.cls.__name__ for m in fastapi_app.user_middleware]
    assert "CORSMiddleware" in middleware_classes
