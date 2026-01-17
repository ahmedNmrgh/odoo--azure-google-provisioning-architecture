# Multi-Directory Model

Each customer has a fully isolated directory to avoid any management issues/mistakes and to be compliant to our customers.

## Microsoft
- One Entra tenant per company
- Platform operator is Global Admin
- App-only authentication(register the app and give it permissions)
- Certificate-based auth(stored in azure key vault rather than on site for less chnace to be attacked)
- Microsoft Graph API

## Google
- One Workspace per company
- Platform operator is Super Admin
- Service account (identity for the function app on azure since everything is centralized on azure)
- Domain-wide delegation
- Admin SDK API

## Isolation
No shared users
No shared groups
No shared domains
No shared identity stores
