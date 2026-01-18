# Multi-Tenant User Provisioning System



## 🏗️ High-Level Architecture

### Core Decisions

1. **One Company = One Directory**
   - Security isolation
   - License isolation
   - Clean billing
   - Clean offboarding

2. **Either Microsoft OR Google**
   - Never both for same company
   - Avoid identity duplication
   - Simplify compliance

## 🔧 Implementation Phases

### PHASE 1: Tenant Creation (Manual, One-Time)

#### Microsoft Entra ID Tenant

- Create new Entra ID tenant per customer
- Initial domain: `companyxyz.onmicrosoft.com`
- You become Global Administrator & Billing Owner

#### Google Workspace Tenant

- Create Workspace account
- Choose admin email
- Add company domain
- Manual process, once per customer


### PHASE 2: Domain Verification (Mandatory Pre-Step)

#### Requirement

- **No user creation before domain verification**
- Prevents wrong emails and cleanup issues

#### Process

- Add custom domain in Entra/Workspace
- Customer adds TXT record to DNS
- Set domain as primary
- Users now get `user@company.com`



### PHASE 3: Licensing Setup (Pre-Automation)

#### Microsoft Licensing

- Create m365 group: "All Users"
- Assign license to group
- User exists → group → license (no code logic)

#### Google Licensing

- Assign license via OU or group
- Users land in default OU
- License auto-applies



### PHASE 4: Automation Scope Definition

#### Automated

- User creation
- Password generation
- Dry-run validation
- Logging
- Archiving




### PHASE 5: Central Infrastructure Setup

#### Single Azure Subscription 

- **Azure Blob Storage (Centralized)**
  
  ```
  Containers:
  └── uploads/
  └── archive/
  ```
  
  ```
  Structure:
  uploads/customerA/users.csv
  uploads/customerB/users.csv
  ```

- **Azure Function App (Single Instance)**
  - Language: Python
  - Trigger: Blob trigger
  - Scaling: Automatic
  - Deployment: One ZIP



### PHASE 6: Configuration Model

#### Customer Metadata

- Provider (Microsoft/Google)
- Tenant ID or domain
- Credentials
- Mode (dry-run/prod)

#### Storage

- Azure App Settings
- JSON configuration
- Azure Key Vault (preferred)

---

### PHASE 7: App Registration

#### Purpose

- Automation identity (not users)
- Function App needs API permissions

#### Microsoft App Registration

- Type: Confidential client
- Auth: Certificate
- Permissions: `User.ReadWrite.All`, `Group.ReadWrite.All`, `Directory.ReadWrite.All`
- Admin consent once

#### Google Service Account

- Create service account
- Enable domain-wide delegation
- Grant scope: `admin.directory.user`
- Delegate to admin email

---

### PHASE 8: CSV Contract Definition

#### Format

```
firstName,lastName,displayName,primaryEmail
```

#### Rules

- One user = one row
- Email domain must match tenant
- Not in the CSV → no user

---

### PHASE 9: Execution Flow


#### Step 1: File Upload

-CSV uploaded to designated storage path
-File structure: {company}/{filename}.csv

#### Step 2: Automatic Detection

-System detects new file via blob trigger
-Extracts company identifier from file path
-Validates file format and structure

#### Step 3: Configuration Retrieval

-Looks up company settings (provider, credentials, mode)
-Determines target platform (Microsoft/Google)
-Checks dry-run vs production mode

#### Step 4: CSV Processing

-Parses CSV content row by row
-Validates email formats and required fields
-Generates secure passwords for each user
-Creates internal user objects

#### Step 5: Safety Validation

-If dry-run mode:
-Logs all intended actions
-Provides preview without modifications
-Returns summary and stops
-If production mode:
-Proceeds with actual user creation

#### Step 6: Platform Authentication

-Establishes connection to target platform
-Uses service credentials for API access
-Obtains necessary authentication tokens

#### Step 7: User Creation

-Creates users via platform APIs
-Applies consistent naming conventions
-Sets initial passwords with forced reset
-Handles rate limits between API calls

#### Step 8: Error Management

-Processes each user independently
-Continues despite individual failures
-Logs detailed error information
-Maintains batch integrity

#### Step 9: Result Reporting

-Generates completion summary
-Logs success/failure counts
-Provides generated passwords for distribution
-Maintains audit trail

#### Step 10: Cleanup

-Leaves source files intact for traceability
-Comprehensive logging for all operations
-No automatic archiving (manual process)



### PHASE 10: Database Justification

#### Why No Database

**Existing Storage:**

- Blob storage (logs)
- Entra/Google (users)

**Database Adds:**

- Schema complexity
- Sync problems
- Additional cost
- New failure modes

**Only Add If You Need:**

- UI interface
- Complex reporting
- Cross-run analytics

---

### PHASE 11: Security Posture

#### Implementation

- Certificates > secrets
- Azure Key Vault for credentials
- App-only authentication
- Least privilege principle
- No interactive login
- Full audit logging

---

### PHASE 12: Scaling Model

- Azure Functions scale automatically
- CSV size limits manageable
- API throttling handled via retries
- Customers isolated by configuration
- Linear scaling (not exponential)

---

### PHASE 13: Your Role

#### Initial

- Global Administrator
- Tenant owner
- Automation owner

#### Transition

- Delegate admin to customer IT
- Remove yourself when contract ends
- Clean lifecycle management

---

## 🎙️ Interview Explanation

> "This system minimizes human error, avoids identity duplication, and keeps licensing simple. Everything complex is done once. Everything repetitive is automated."

---

## 📦 Deliverables Summary

1. **Central Azure Infrastructure**
   - Blob Storage with uploads/archive containers
   - Azure Function App (Python)

2. **Configuration Management**
   - Customer metadata store
   - App registration/Service accounts
   - Key Vault integration

3. **Processing Engine**
   - CSV validation and parsing
   - Dry-run safety mode
   - Multi-provider support (MS/Google)
   - Password generation

4. **Audit Trail**
   - Execution logging
   - CSV archiving
   - Immutable records

5. **Documentation**
   - Setup guides
   - CSV format specification
   - Troubleshooting procedures




