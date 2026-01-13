# odoo--azure-google-provisioning-architecture
This project aims to make Odoo the single source of truth for user management and automatically synchronize user changes (creation, updates, deactivation) to Microsoft Entra ID and Google Workspace.  Instead of manually creating and managing users across multiple platforms, all user lifecycle actions are performed once in Odoo and then propagated automatically to identity providers.


this project is an issue I have talked about with my interviewer in one of my job interviews , I have took a simple look on it to figgure why this is an issue but i couldn't stop thinking abt it now I'm simply enjoying it , and since I'm preping for az-305 solution architect , this seemed to be a good opurtunity to design this and implement it if I get the job ofc >_<.


the architecture goes like this :
The solution uses a centralized, event-driven architecture. Each time Odoo exports a user list as a CSV file, it uploads the file to secure cloud storage in a folder dedicated to that customer. The file upload automatically triggers a lightweight cloud function that does nothing except register the event and place a message onto a queue. A separate worker function then processes the queue message, ensuring that only one provisioning job runs per customer at a time while allowing many customers to be processed in parallel. The worker reads the CSV, validates the data, compares it against the target directory, and creates missing users in either Microsoft Entra ID or Google Workspace. All actions are logged, the original file is archived for auditing, and failures are retried safely using the queue. This design avoids race conditions, scales automatically, and keeps customer environments isolated while remaining simple to operate.
