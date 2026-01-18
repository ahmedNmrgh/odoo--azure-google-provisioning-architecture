import os

# Simple hardcoded company configurations
# Add new companies here with their settings
COMPANIES = {
    "contoso": {
        "provider": "microsoft",
        "tenant_id": "contoso.onmicrosoft.com",  # Public info - safe to hardcode
        "client_id": os.environ.get("CONTOSO_CLIENT_ID"),  # From environment
        "client_secret": os.environ.get("CONTOSO_CLIENT_SECRET"),  # From environment
        "dry_run": os.environ.get("CONTOSO_DRY_RUN", "true").lower() == "true"
    },
    "google_company": {
        "provider": "google",
        "domain": "googlecompany.com",  # Public domain
        "admin_email": "admin@googlecompany.com",  # Public email
        "customer_id": os.environ.get("GOOGLE_CUSTOMER_ID", "my_customer"),  # Default to single domain
        "dry_run": os.environ.get("GOOGLE_DRY_RUN", "true").lower() == "true"
    }
}

def get_company_config(company_name):
    """Get configuration for a company"""
    config = COMPANIES.get(company_name)
    if config:
        config["company"] = company_name  # Add for logging
    return config
