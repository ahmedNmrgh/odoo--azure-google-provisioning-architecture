import json
import logging
import os
import csv
import io
from datetime import datetime
import azure.functions as func
from azure.storage.blob import BlobServiceClient

def main(msg: func.QueueMessage):
    """
    Triggered by a message in the queue
    """
    logging.info(f"Queue trigger processed: {msg.get_body().decode()}")
    
    try:
        # Parse queue message
        message_data = json.loads(msg.get_body().decode())
        customer_id = message_data["customer_id"]
        file_name = message_data["file_name"]
        
        logging.info(f"Processing queue message for: {customer_id}, file: {file_name}")
        
        # 1. Load customer configuration
        config = load_customer_config(customer_id)
        
        # 2. Download and parse CSV
        users = download_and_parse_csv(customer_id, file_name)
        
        # 3. Process based on dry-run mode
        if config.get("dry_run", True):
            # Dry-run mode: just validate
            results = process_dry_run(users, customer_id)
        else:
            # Live mode: actually create users
            results = process_live(users, customer_id, config)
        
        # 4. Save results
        save_results(customer_id, results)
        
        logging.info(f"Completed processing for {customer_id}: {len(users)} users")
        
    except Exception as e:
        logging.error(f"Error processing queue message: {str(e)}")
        raise

def load_customer_config(customer_id: str) -> dict:
    """Load customer-specific configuration"""
    # In production, load from Azure Key Vault or database
    # For now, return a simple config
    
    # Default configuration (dry-run mode)
    config = {
        "dry_run": True,  # Always start with dry-run for safety
        "provider": "microsoft",  # or "google"
        "tenant_id": f"{customer_id}.onmicrosoft.com"
    }
    
    # You can add more configuration loading logic here
    logging.info(f"Loaded config for {customer_id}: dry_run={config['dry_run']}")
    return config

def download_and_parse_csv(customer_id: str, file_name: str) -> list:
    """Download CSV from archive and parse it"""
    try:
        connection_string = os.environ["AzureWebJobsStorage"]
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Find the latest archive file for this customer
        # (In production, you'd store the archive path in queue message)
        container_client = blob_service_client.get_container_client("csv-uploads")
        
        # Simple: look for archive files (in real app, track the exact path)
        blob_list = container_client.list_blobs(name_starts_with=f"archive/raw/")
        
        # For demo: just parse the latest file for this customer
        # This is simplified - in production, store exact path in queue message
        
        # For now, return dummy data
        users = [
            {"email": "user1@example.com", "first_name": "John", "last_name": "Doe"},
            {"email": "user2@example.com", "first_name": "Jane", "last_name": "Smith"}
        ]
        
        logging.info(f"Parsed {len(users)} users from CSV")
        return users
        
    except Exception as e:
        logging.error(f"Failed to download/parse CSV: {str(e)}")
        raise

def process_dry_run(users: list, customer_id: str) -> dict:
    """Process in dry-run mode (validation only)"""
    logging.info(f"DRY-RUN MODE for {customer_id}")
    
    results = {
        "customer_id": customer_id,
        "mode": "dry_run",
        "timestamp": datetime.utcnow().isoformat(),
        "total_users": len(users),
        "actions": []
    }
    
    for user in users:
        # Simulate validation
        user_email = user.get("email", "")
        results["actions"].append({
            "user": user_email,
            "action": "would_create",
            "status": "valid",
            "message": "User would be created (dry-run mode)"
        })
    
    return results

def process_live(users: list, customer_id: str, config: dict) -> dict:
    """Process in live mode (actually create users)"""
    logging.info(f"LIVE MODE for {customer_id}")
    
    results = {
        "customer_id": customer_id,
        "mode": "live",
        "timestamp": datetime.utcnow().isoformat(),
        "total_users": len(users),
        "actions": []
    }
    
    provider = config.get("provider", "microsoft")
    
    for user in users:
        user_email = user.get("email", "")
        try:
            # Here you would call Microsoft Graph API or Google Admin SDK
            # For now, simulate success
            user_id = f"user-{datetime.utcnow().timestamp()}"
            
            results["actions"].append({
                "user": user_email,
                "action": "created",
                "status": "success",
                "user_id": user_id,
                "message": f"User created in {provider}"
            })
            
            logging.info(f"Created user: {user_email}")
            
        except Exception as e:
            results["actions"].append({
                "user": user_email,
                "action": "create",
                "status": "error",
                "message": str(e)
            })
            logging.error(f"Failed to create user {user_email}: {str(e)}")
    
    return results

def save_results(customer_id: str, results: dict):
    """Save processing results to blob storage"""
    try:
        connection_string = os.environ["AzureWebJobsStorage"]
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        results_path = f"archive/results/{timestamp}/{customer_id}_results.json"
        
        blob_client = blob_service_client.get_blob_client(
            container="csv-uploads",
            blob=results_path
        )
        
        results_json = json.dumps(results, indent=2)
        blob_client.upload_blob(results_json, overwrite=True)
        
        logging.info(f"Results saved to: {results_path}")
        
    except Exception as e:
        logging.error(f"Failed to save results: {str(e)}")
        raise
