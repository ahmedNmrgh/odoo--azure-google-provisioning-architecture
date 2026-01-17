## Processing Flow

1. CSV is uploaded to Azure Blob Storage from odoo through a small application that also detects any change in users and recreate CSV file with every change
2. Blob trigger Azure Function activates
3. CSV metadata is read
4. customerId is extracted from path
5. Customer configuration is loaded
6. Provider is selected (Microsoft or Google)
7. Message is pushed to Azure Queue Storage
8. Worker Function processes message
9. Authentication is performed
10. Dry-run preview is generated
11. If approved Users are created 
12. Results are logged
13. CSV is archived
14. Audit log is stored for further analysis and improvement
