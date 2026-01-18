import json
import azure.functions as func
from azure.storage.queue import QueueClient
import os

app = func.FunctionApp()

@app.blob_trigger(
    arg_name="myblob",
    path="csv-uploads/{company}/{filename}.csv",
    connection="AzureWebJobsStorage"
)
def csv_trigger(myblob: func.InputStream):
    """
    Triggered when CSV is uploaded to: csv-uploads/{company}/{filename}.csv
    Sends CSV content to queue for processing.
    """
    try:
        # Path format: "company_name/filename.csv"
        path_parts = myblob.name.split("/")
        
        # Validate path format
        if len(path_parts) != 2:
            print(f"⚠️ Invalid path format: {myblob.name}")
            return
        
        company = path_parts[0]
        filename = path_parts[1]
        
        # Validate file type
        if not filename.lower().endswith('.csv'):
            print(f"⚠️ Not a CSV file: {filename}")
            return
        
        # Read CSV content
        csv_content = myblob.read().decode("utf-8-sig")  # utf-8-sig handles BOM
        
        # Send to queue
        queue_client = QueueClient.from_connection_string(
            os.environ["AzureWebJobsStorage"],
            "user-sync-queue"
        )
        
        message = {
            "company": company,
            "csv": csv_content,
            "filename": filename
        }
        
        queue_client.send_message(json.dumps(message))
        print(f"✅ Queued CSV '{filename}' for company '{company}'")
        
    except Exception as e:
        print(f"❌ Blob trigger error: {str(e)}")
        # Don't raise - Azure will retry automatically
