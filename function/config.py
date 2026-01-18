import os

COMPANIES = {
    # Microsoft Companies
    "contoso_corp": {
        "provider": "microsoft",
        "tenant_id": "contoso.onmicrosoft.com",     
        "client_id": "11111111-2222-3333-4444-555555555555",  
        "client_secret": os.environ["MS_CLIENT_SECRET"],      # 
        "dry_run": True  # Safety ON
    },
    
    "fabrikam_inc": {
        "provider": "microsoft", 
        "tenant_id": "fabrikam.onmicrosoft.com",     
        "client_id": "66666666-7777-8888-9999-000000000000",  
        "client_secret": os.environ["FABRIKAM_CLIENT_SECRET"], 
        "dry_run": False  # Live for this client
    },
    
    # Google Companies
    "google_company": {
        "provider": "google",
        "domain": "googlecompany.com",              
        "admin_email": "admin@googlecompany.com",   
        "service_account_json": os.environ["GOOGLE_SA_JSON"],
        "dry_run": True
    }
}
