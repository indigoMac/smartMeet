# SmartMeet

A professional-grade productivity tool that simplifies external meeting scheduling via an Outlook add-in and secure backend infrastructure.

## What SmartMeet Does

SmartMeet allows users to select multiple external email recipients in Outlook, then finds mutual availability across everyone's calendars (Microsoft Outlook or Google Calendar) without revealing full calendar content, using OAuth2 and free/busy access only.

Participants who don't already use SmartMeet are invited via a secure link to a web portal where they can authorize calendar access.

## System Architecture

### 3 Main Components:

1. **Outlook Add-in** (`apps/outlook-addin/`)

   - Built with React + Office.js
   - Appears as a task pane inside Outlook
   - Allows users to select invitees and trigger availability search

2. **API Backend** (`apps/api-backend/`)

   - Built using FastAPI
   - Handles OAuth2 calendar integrations (Microsoft + Google)
   - Free/busy data fetching and availability computation logic
   - Optionally stores minimal user data (tokens, status)

3. **Web Fallback Portal** (`apps/web-portal/`)
   - Built with Next.js (TypeScript)
   - For external invitees to authorize calendar access and view proposed meeting times
   - Hosted on Vercel

## Tech Stack

| Area          | Stack/Service                    |
| ------------- | -------------------------------- |
| UI            | React, Office.js                 |
| Web Portal    | Next.js (TypeScript)             |
| API Backend   | FastAPI (Python)                 |
| Calendar APIs | Microsoft Graph, Google Calendar |
| Auth          | OAuth2 (PKCE)                    |
| Deployment    | Vercel                           |
| CI/CD         | GitHub → Vercel (auto deploy)    |
| Database      | Optional (PostgreSQL or MongoDB) |

## Project Structure

```
smartmeet/
├── apps/
│   ├── outlook-addin/       # React + Office.js
│   ├── api-backend/         # FastAPI (OAuth + calendar logic)
│   └── web-portal/          # Next.js app
├── infrastructure/
│   └── vercel.json          # Multi-project config
├── .github/
│   └── workflows/ci.yml     # GitHub Actions CI
├── .env.example             # Environment variable template
├── README.md
└── vercel.json
```

## Setup Instructions

### 1. Install Dependencies

Each app has its own dependencies. Navigate to each directory and install:

```bash
# Outlook Add-in
cd apps/outlook-addin && npm install

# API Backend
cd apps/api-backend && pip install -r requirements.txt

# Web Portal
cd apps/web-portal && npm install
```

### 2. Environment Configuration

Copy `.env.example` to `.env` and fill in your OAuth credentials:

```bash
cp .env.example .env
```

### 3. OAuth Setup

#### Microsoft (Azure App Registration)

- Required scope: `Calendars.Read.Shared`
- Redirect URI: `https://smartmeet.vercel.app/connect/microsoft/callback`

#### Google (Google Cloud Console)

- Scope: `https://www.googleapis.com/auth/calendar.readonly`
- Redirect URI: `https://smartmeet.vercel.app/connect/google/callback`

### 4. Development

Run each app in development mode:

```bash
# API Backend
cd apps/api-backend && uvicorn main:app --reload

# Web Portal
cd apps/web-portal && npm run dev

# Outlook Add-in
cd apps/outlook-addin && npm start
```

### 5. Deployment

Deploy to Vercel:

```bash
vercel --prod
```

## Web Portal Routes

- `/connect` → Start OAuth flow
- `/success` → Confirmation page
- `/availability/:meetingId` → Show time proposals

## Outlook Add-in

The add-in manifest references the Vercel deployment:

- SourceLocation: `https://smartmeet.vercel.app/outlook-addin/taskpane.html`
- Parses To/CC fields for recipient emails
- Triggers backend API call to fetch availability
- Inserts best time options into Outlook email body or meeting invite

## API Endpoints

- `GET /health` → Health check
- `POST /connect/microsoft` → Microsoft OAuth flow
- `POST /connect/google` → Google OAuth flow
- `POST /availability` → Calculate mutual availability
- `GET /availability/:meetingId` → Get meeting availability data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License
# Force deployment Fri Jun 13 16:13:02 BST 2025
