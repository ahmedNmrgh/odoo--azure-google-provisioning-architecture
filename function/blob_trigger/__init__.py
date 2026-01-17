import json
import logging
import os
import tempfile
from datetime import datetime
import azure.functions as func
from azure.storage.blob import BlobServiceClient
from azure.storage.queue import QueueClient

def main(myblob: func.InputStream):
    """
    Triggered when a CSV file is uploaded to blob storage
    """
    logging.info(f"CSV blob trigger processed: {myblob.name}")
    
    try:
        # Extract customer ID and file name from blob path
        # Path format: uploads/{customerId}/{fileName}.csv
        blob_path = myblob.name
        parts = blob_path.split('/')
        
        if len(parts) != 3:
            logging.error(f"Invalid blob path: {blob_path}")
            return
        
        customer_id = parts[1]
        file_name = parts[2]
        
        logging.info(f"Processing CSV for customer: {customer_id}, file: {file_name}")
        
        # 1. Read the CSV content
        csv_content = myblob.read().decode('utf-8')
        logging.info(f"CSV size: {len(csv_content)} bytes")
        
        # 2. Archive the CSV (save to archive folder)
        archive_blob(customer_id, file_name, csv_content)
        
        # 3. Send message to queue for processing
        queue_message = {
            "customer_id": customer_id,
            "file_name": file_name,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        send_to_queue(queue_message)
        
        logging.info(f"Successfully queued CSV for processing: {blob_path}")
        
    except Exception as e:
        logging.error(f"Error processing blob: {str(e)}")

def archive_blob(customer_id: str, file_name: str, content: str):
    """Save original CSV to archive folder"""
    try:
        # Get connection string from environment
        connection_string = os.environ["AzureWebJobsStorage"]
        
        # Create blob service client
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Generate archive path with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        archive_path = f"archive/raw/{timestamp}/{customer_id}/{file_name}"
        
        # Upload to archive
        blob_client = blob_service_client.get_blob_client(
            container="csv-uploads",  # Your container name
            blob=archive_path
        )
        
        blob_client.upload_blob(content, overwrite=True)
        logging.info(f"Archived CSV to: {archive_path}")
        
    except Exception as e:
        logging.error(f"Failed to archive blob: {str(e)}")
        raise

def send_to_queue(message: dict):
    """Send processing message to queue"""
    try:
        connection_string = os.environ["AzureWebJobsStorage"]
        
        queue_client = QueueClient.from_connection_string(
            connection_string,
            queue_name="csv-processing-queue"
        )
        
        queue_client.send_message(json.dumps(message))
        logging.info(f"Message sent to queue: {message}")
        
    except Exception as e:
        logging.error(f"Failed to send to queue: {str(e)}")
        raise
