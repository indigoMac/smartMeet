# SmartMeet Setup Guide

This guide will help you set up and deploy the SmartMeet project, which consists of three main applications:

1. **API Backend** (FastAPI) - `/apps/api-backend/`
2. **Web Portal** (Next.js) - `/apps/web-portal/`
3. **Outlook Add-in** (React + Office.js) - `/apps/outlook-addin/`

## Prerequisites

- Node.js 18+
- Python 3.9+
- npm or yarn
- Git

## Quick Start

### 1. Install Dependencies

**API Backend:**

```bash
cd apps/api-backend
pip install -r requirements.txt
```

**Web Portal:**

```bash
cd apps/web-portal
npm install
```

**Outlook Add-in:**

```bash
cd apps/outlook-addin
npm install
```

### 2. Environment Setup

Copy `env.example` to `.env` and fill in your OAuth credentials:

```bash
cp env.example .env
```

Required environment variables:

- `MICROSOFT_CLIENT_ID` - Azure App Registration Client ID
- `MICROSOFT_CLIENT_SECRET` - Azure App Registration Client Secret
- `GOOGLE_CLIENT_ID` - Google Cloud Console OAuth Client ID
- `GOOGLE_CLIENT_SECRET` - Google Cloud Console OAuth Client Secret
- `JWT_SECRET_KEY` - Random secret key for JWT tokens

### 3. OAuth Setup

#### Microsoft Azure

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to "App registrations" → "New registration"
3. Name: "SmartMeet"
4. Redirect URI: `https://smartmeet.vercel.app/connect/microsoft/callback`
5. API permissions: Add `Calendars.Read.Shared` scope
6. Copy Client ID and generate a Client Secret

#### Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project or select existing
3. Enable Google Calendar API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Application type: Web application
6. Authorized redirect URI: `https://smartmeet.vercel.app/connect/google/callback`
7. Copy Client ID and Client Secret

### 4. Development

Run each application in development mode:

**API Backend:**

```bash
cd apps/api-backend
uvicorn main:app --reload --port 8000
```

**Web Portal:**

```bash
cd apps/web-portal
npm run dev
```

**Outlook Add-in:**

```bash
cd apps/outlook-addin
npm start
```

The applications will be available at:

- API: http://localhost:8000
- Web Portal: http://localhost:3000
- Outlook Add-in: https://localhost:3000 (HTTPS required for Office.js)

### 5. Testing

#### API Backend

```bash
cd apps/api-backend
# Visit http://localhost:8000/docs for Swagger UI
curl http://localhost:8000/health
```

#### Web Portal

- Navigate to http://localhost:3000
- Test OAuth flows at http://localhost:3000/connect

#### Outlook Add-in

1. Sideload the manifest in Outlook
2. Use manifest.xml from `apps/outlook-addin/manifest.xml`
3. Follow [Microsoft's sideloading guide](https://docs.microsoft.com/en-us/office/dev/add-ins/testing/test-debug-office-add-ins)

## Deployment

### Vercel Deployment

1. **Connect to Vercel:**

   ```bash
   npm install -g vercel
   vercel login
   ```

2. **Configure Environment Variables:**
   Add the following environment variables in Vercel dashboard:

   - `MICROSOFT_CLIENT_ID`
   - `MICROSOFT_CLIENT_SECRET`
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
   - `JWT_SECRET_KEY`

3. **Deploy:**

   ```bash
   vercel --prod
   ```

4. **Update OAuth Redirect URIs:**
   Update your OAuth applications to use your Vercel domain:
   - Microsoft: `https://your-domain.vercel.app/connect/microsoft/callback`
   - Google: `https://your-domain.vercel.app/connect/google/callback`

### Manual Deployment

Each app can be deployed separately:

**API Backend:**

- Deploy to any Python hosting service (Heroku, Railway, etc.)
- Ensure environment variables are set

**Web Portal:**

- Build: `npm run build`
- Deploy static files to any hosting service

**Outlook Add-in:**

- Build: `npm run build`
- Host the `dist/` folder on HTTPS
- Update manifest.xml URLs to point to your hosting

## Office Add-in Installation

### For Development

1. Open Outlook (desktop or web)
2. Go to Add-ins → "Manage Add-ins" → "Upload My Add-in"
3. Select the manifest.xml file
4. The SmartMeet add-in should appear in the ribbon

### For Production

1. Submit to Microsoft AppSource OR
2. Deploy via Microsoft 365 admin center for organization-wide installation

## Project Structure

```
smartmeet/
├── apps/
│   ├── api-backend/          # FastAPI backend
│   │   ├── main.py          # Main application file
│   │   └── requirements.txt  # Python dependencies
│   ├── outlook-addin/        # Office.js React add-in
│   │   ├── manifest.xml     # Office add-in manifest
│   │   ├── src/             # Source code
│   │   └── webpack.config.js # Build configuration
│   └── web-portal/          # Next.js web application
│       ├── src/app/         # App router pages
│       └── package.json     # Node.js dependencies
├── infrastructure/
├── .github/workflows/       # CI/CD configuration
└── vercel.json             # Vercel deployment config
```

## API Endpoints

- `GET /health` - Health check
- `GET /connect/microsoft` - Start Microsoft OAuth
- `GET /connect/google` - Start Google OAuth
- `POST /availability` - Calculate meeting availability
- `GET /availability/{meeting_id}` - Get meeting data

## Web Portal Routes

- `/` - Landing page
- `/connect` - OAuth connection page
- `/success` - OAuth success confirmation
- `/availability/{meetingId}` - Meeting time selection

## Troubleshooting

### Common Issues

1. **OAuth Errors:**

   - Verify redirect URIs match exactly
   - Check client ID/secret configuration
   - Ensure proper scopes are requested

2. **Office Add-in Not Loading:**

   - Manifest must be served over HTTPS
   - Check browser console for errors
   - Verify Office.js is loaded correctly

3. **CORS Issues:**

   - API backend includes CORS middleware
   - Ensure frontend URL is whitelisted

4. **Build Errors:**
   - Clear node_modules and reinstall dependencies
   - Check TypeScript configuration
   - Verify all environment variables are set

### Debugging

- API Backend: Check FastAPI logs and `/docs` endpoint
- Web Portal: Use browser dev tools and Next.js error overlay
- Outlook Add-in: Use F12 dev tools in Office applications

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review the project README.md
3. Create an issue in the project repository

## Security Notes

- Never commit `.env` files or secrets to version control
- Use environment variables for all sensitive configuration
- Implement proper authentication and authorization in production
- Regularly update dependencies for security patches
- Follow OAuth best practices and security guidelines
