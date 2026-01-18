import json
import csv
import io
import time
import os
import random
import string
import azure.functions as func
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
import shared_config

app = func.FunctionApp()

# -------------------------
# Utilities
# -------------------------
def generate_temp_password():
    """Generate a temporary password that meets complexity requirements"""
    chars = string.ascii_letters + string.digits + "!@#$%"
    password = []
    
    # Ensure at least one of each type
    password.append(random.choice(string.ascii_lowercase))
    password.append(random.choice(string.ascii_uppercase))
    password.append(random.choice(string.digits))
    password.append(random.choice("!@#$%"))
    
    # Fill remaining
    for _ in range(8):  # 12 total characters
        password.append(random.choice(chars))
    
    random.shuffle(password)
    return ''.join(password)

def parse_csv_safe(csv_text):
    """Parse CSV with basic validation"""
    users = {}
    
    try:
        reader = csv.DictReader(io.StringIO(csv_text))
        
        for row in reader:
            email = row.get("email", "").strip().lower()
            
            # Basic validation
            if not email or "@" not in email:
                continue
            
            # Extract basic fields
            users[email] = {
                "email": email,
                "first_name": row.get("first_name", "").strip(),
                "last_name": row.get("last_name", "").strip(),
                "password": row.get("password", "").strip() or generate_temp_password()
            }
            
    except Exception as e:
        print(f"⚠️ CSV parsing error: {e}")
    
    return users

# -------------------------
# Microsoft Graph API
# -------------------------
def get_microsoft_token(config):
    """Get access token using client secret"""
    try:
        url = f"https://login.microsoftonline.com/{config['tenant_id']}/oauth2/v2.0/token"
        
        data = {
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials"
        }
        
        response = requests.post(url, data=data, timeout=30)
        response.raise_for_status()
        
        return response.json()["access_token"]
        
    except Exception as e:
        print(f"❌ Microsoft authentication failed: {e}")
        raise

def process_microsoft_users(config, users, dry_run=True):
    """Create/update Microsoft users"""
    results = []
    
    if dry_run:
        print(f"🔍 DRY-RUN: Would process {len(users)} Microsoft users")
        for email in users:
            results.append({
                "email": email,
                "action": "would_process",
                "status": "dry_run"
            })
        return results
    
    try:
        token = get_microsoft_token(config)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Process users one by one with delay
        for email, user_data in users.items():
            try:
                # Prepare user data
                create_data = {
                    "accountEnabled": True,
                    "displayName": f"{user_data['first_name']} {user_data['last_name']}",
                    "mailNickname": email.split("@")[0],
                    "userPrincipalName": email,
                    "passwordProfile": {
                        "forceChangePasswordNextSignIn": True,
                        "password": user_data["password"]
                    }
                }
                
                # Create user
                response = requests.post(
                    "https://graph.microsoft.com/v1.0/users",
                    headers=headers,
                    json=create_data,
                    timeout=30
                )
                
                if response.status_code == 201:
                    user_id = response.json().get("id")
                    results.append({
                        "email": email,
                        "action": "created",
                        "status": "success",
                        "user_id": user_id,
                        "password": user_data["password"]  # Return password for logging
                    })
                    print(f"✅ Created Microsoft user: {email}")
                    
                elif response.status_code == 400 and "already exists" in response.text.lower():
                    results.append({
                        "email": email,
                        "action": "skipped",
                        "status": "already_exists"
                    })
                    print(f"⚠️ User already exists: {email}")
                    
                else:
                    results.append({
                        "email": email,
                        "action": "failed",
                        "status": "error",
                        "error": response.text[:200]
                    })
                    print(f"❌ Failed to create {email}: {response.status_code}")
                
                # Delay to avoid rate limits (2 requests per second)
                time.sleep(0.5)
                
            except Exception as e:
                results.append({
                    "email": email,
                    "action": "error",
                    "status": "error",
                    "error": str(e)
                })
                print(f"❌ Error processing {email}: {e}")
                # Continue with next user
        
    except Exception as e:
        print(f"❌ Microsoft processing failed: {e}")
        # Return partial results
    
    return results

# -------------------------
# Google Workspace API
# -------------------------
def get_google_service(config):
    """Create Google Admin SDK service"""
    try:
        # Service account JSON from environment
        sa_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        if not sa_json:
            raise ValueError("Google service account JSON not found in environment")
        
        credentials = service_account.Credentials.from_service_account_info(
            json.loads(sa_json),
            scopes=["https://www.googleapis.com/auth/admin.directory.user"],
            subject=config["admin_email"]
        )
        
        return build('admin', 'directory_v1', credentials=credentials)
        
    except Exception as e:
        print(f"❌ Google service creation failed: {e}")
        raise

def process_google_users(config, users, dry_run=True):
    """Create/update Google users"""
    results = []
    
    if dry_run:
        print(f"🔍 DRY-RUN: Would process {len(users)} Google users")
        for email in users:
            results.append({
                "email": email,
                "action": "would_process",
                "status": "dry_run"
            })
        return results
    
    try:
        service = get_google_service(config)
        
        # Process users one by one
        for email, user_data in users.items():
            try:
                # Prepare user data
                user_body = {
                    "primaryEmail": email,
                    "name": {
                        "givenName": user_data["first_name"],
                        "familyName": user_data["last_name"]
                    },
                    "password": user_data["password"],
                    "changePasswordAtNextLogin": True
                }
                
                # Create user
                created_user = service.users().insert(body=user_body).execute()
                
                results.append({
                    "email": email,
                    "action": "created",
                    "status": "success",
                    "user_id": created_user.get("id"),
                    "password": user_data["password"]
                })
                print(f"✅ Created Google user: {email}")
                
                # Google is slower, wait longer between requests
                time.sleep(1)
                
            except Exception as e:
                error_msg = str(e)
                if "already exists" in error_msg.lower():
                    results.append({
                        "email": email,
                        "action": "skipped",
                        "status": "already_exists"
                    })
                    print(f"⚠️ User already exists: {email}")
                else:
                    results.append({
                        "email": email,
                        "action": "error",
                        "status": "error",
                        "error": error_msg[:200]
                    })
                    print(f"❌ Error creating {email}: {error_msg}")
        
    except Exception as e:
        print(f"❌ Google processing failed: {e}")
        # Return partial results
    
    return results

# -------------------------
# Main Queue Function
# -------------------------
@app.queue_trigger(
    arg_name="msg",
    queue_name="user-sync-queue",
    connection="AzureWebJobsStorage"
)
def user_sync_worker(msg: func.QueueMessage):
    """
    Queue-triggered function that processes CSV and creates users.
    """
    try:
        # Parse queue message
        data = json.loads(msg.get_body().decode("utf-8"))
        company = data.get("company")
        csv_text = data.get("csv", "")
        
        if not company:
            print("❌ No company in queue message")
            return
        
        print(f"👷 Processing queue message for: {company}")
        
        # Get company configuration
        config = shared_config.get_company_config(company)
        if not config:
            print(f"❌ No configuration found for company: {company}")
            return
        
        # Parse CSV
        users = parse_csv_safe(csv_text)
        if not users:
            print(f"⚠️ No valid users found in CSV for {company}")
            return
        
        print(f"📄 Found {len(users)} valid users in CSV")
        
        # Process based on provider
        dry_run = config.get("dry_run", True)
        
        if config["provider"] == "microsoft":
            results = process_microsoft_users(config, users, dry_run)
        elif config["provider"] == "google":
            results = process_google_users(config, users, dry_run)
        else:
            print(f"❌ Unknown provider: {config['provider']}")
            return
        
        # Calculate summary
        successful = len([r for r in results if r.get("status") == "success"])
        skipped = len([r for r in results if r.get("status") == "already_exists"])
        failed = len([r for r in results if r.get("status") == "error"])
        
        # Print summary
        print(f"\n📊 SUMMARY for {company}:")
        print(f"   ✅ Created: {successful}")
        print(f"   ⚠️ Skipped (already exists): {skipped}")
        print(f"   ❌ Failed: {failed}")
        
        # Show passwords for new users (dry-run safe)
        if not dry_run and successful > 0:
            print(f"\n🔑 Passwords for new users:")
            for result in results:
                if result.get("status") == "success" and result.get("password"):
                    print(f"   {result['email']}: {result['password']}")
        
    except Exception as e:
        print(f"❌ Queue processing error: {str(e)}")
        # Don't raise - Azure will retry 5 times, then send to dead letter queue
