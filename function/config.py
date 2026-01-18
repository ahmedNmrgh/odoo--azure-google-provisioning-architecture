import os

COMPANIES = {
    "company_123": {
        "provider": "microsoft",  # or "google"
        "tenant_id": os.environ.get("COMPANY123_TENANT_ID", ""),
        "client_id": os.environ.get("COMPANY123_CLIENT_ID", ""),
        "client_secret": os.environ.get("COMPANY123_CLIENT_SECRET", ""),
        "dry_run": os.environ.get("COMPANY123_DRY_RUN", "true").lower() == "true"
    },

    "company_456": {
    "provider": "google",
    "domain": os.environ.get("COMPANY456_DOMAIN", ""),  # ← Add this
    "admin_email": os.environ.get("COMPANY456_ADMIN_EMAIL", ""),  # ← Add this
    "service_account_json": os.environ.get("COMPANY456_SA_JSON", ""),
    "dry_run": True
    }
}
