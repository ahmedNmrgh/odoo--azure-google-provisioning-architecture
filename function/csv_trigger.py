import azure.functions as func
import json
from azure.storage.queue import QueueClient
import os

QUEUE_NAME = "user-provisioning-queue"

def main(myblob: func.InputStream):
    blob_path = myblob.name  # csv-uploads/company_123/users.csv
    parts = blob_path.split("/")

    if len(parts) != 3:
        return  # invalid structure

    company = parts[1]
    csv_content = myblob.read().decode("utf-8")

    message = {
        "company": company,
        "csv": csv_content
    }

    queue = QueueClient.from_connection_string(
        os.environ["AzureWebJobsStorage"],
        QUEUE_NAME
    )

    queue.send_message(json.dumps(message))
