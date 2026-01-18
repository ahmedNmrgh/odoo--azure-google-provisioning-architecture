import azure.functions as func
import json
import csv
import io
import random
import string
import requests
from config import COMPANIES

def generate_password(length=12):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(random.choice(chars) for _ in range(length))

def parse_csv(csv_text):
    reader = csv.DictReader(io.StringIO(csv_text))
    users = []

    for row in reader:
        users.append({
            "email": row["email"].strip(),
            "first_name": row["first_name"].strip(),
            "last_name": row["last_name"].strip(),
            "password": generate_password()
        })

    return users

def create_microsoft_user(user, company_config):
    payload = {
        "accountEnabled": True,
        "displayName": f"{user['first_name']} {user['last_name']}",
        "mailNickname": user["email"].split("@")[0],
        "userPrincipalName": user["email"],
        "passwordProfile": {
            "password": user["password"],
            "forceChangePasswordNextSignIn": True
        }
    }

    if company_config["dry_run"]:
        print(f"[DRY-RUN] Would create Microsoft user {user['email']}")
        return

    # Token + API call intentionally simplified
    print(f"Creating Microsoft user {user['email']}")

def create_google_user(user, company_config):
    if company_config["dry_run"]:
        print(f"[DRY-RUN] Would create Google user {user['email']}")
        return

    print(f"Creating Google user {user['email']}")

def main(msg: func.QueueMessage):
    data = json.loads(msg.get_body().decode("utf-8"))

    company = data["company"]
    csv_text = data["csv"]

    if company not in COMPANIES:
        print(f"Unknown company: {company}")
        return

    company_config = COMPANIES[company]
    users = parse_csv(csv_text)

    for user in users:
        try:
            if company_config["provider"] == "microsoft":
                create_microsoft_user(user, company_config)

            elif company_config["provider"] == "google":
                create_google_user(user, company_config)

            else:
                print(f"Unsupported provider for {company}")

        except Exception as e:
            print(f"Failed for {user['email']}: {str(e)}")
