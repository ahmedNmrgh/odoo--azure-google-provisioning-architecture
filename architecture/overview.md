## Platform overview
A centralized identity automation platform that provisions users into either Microsoft Entra ID or Google Workspace using CSV driven workflows and serverless architecture.
Each customer is isolated in their own directory (tenant or workspace).
The platform never creates users in both providers for the same customer unless explictly asked to by the client to enjoy both azure and google licensing.

## Core features
- Multi-directory identity management
- Azure Entra ID provisioning
- Google Workspace provisioning
- CSV as source of truth
- Event-driven processing
- Dry-run preview mode (test) 
- Centralized storage
- Serverless execution
- Strong isolation per customer

## Technology Stack
- Azure Blob Storage
- Azure Functions (Python)
- Azure Key Vault
- Azure Queue Storage
- Microsoft Graph API
- Google Admin SDK
- Google Service Accounts
- Domain-wide delegation
