import os
import json
import azure.functions as func
from azure.storage.queue import QueueClient

QUEUE_NAME = "user-sync"

def main(myblob: func.InputStream):
    # myblob.name example: "company_123/users.csv"
    path_parts = myblob.name.split("/")
    
    if len(path_parts) != 2:
        print(f"ERROR: Unexpected blob path: {myblob.name}")
        return
    
    company_folder = path_parts[0]
    filename = path_parts[1]

    csv_content = myblob.read().decode("utf-8")

    queue_client = QueueClient.from_connection_string(
        os.environ["AzureWebJobsStorage"],
        QUEUE_NAME
    )

    message = {
        "company": company_folder,
        "csv": csv_content
    }

    queue_client.send_message(json.dumps(message))
    print(f"✅ Queued CSV '{filename}' for company '{company_folder}'")
