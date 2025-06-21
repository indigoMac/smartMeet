# SmartMeet Outlook Add-in - Development Setup

## Architecture Overview

- **Web Portal**: Next.js app on `localhost:3000` (OAuth & user management)
- **Outlook Add-in**: React/TypeScript on `localhost:3001` (HTTPS required)

## Prerequisites

✅ Node.js (latest LTS)
✅ Office 365 subscription
✅ Development certificates installed

## Development Workflow

### Option 1: Manual Development (Current)

```bash
# Start the add-in dev server
npm run start

# In another terminal, validate manifest
npm run validate

# Sideload the add-in (if needed)
npm run sideload
```

### Option 2: Automated Development (Recommended)

```bash
# Starts dev server AND automatically sideloads add-in
npm run start:desktop  # For Outlook desktop
npm run start:web      # For Outlook web

# Stop everything
npm run stop
```

## Testing Checklist

- [ ] Web portal accessible at https://localhost:3000
- [ ] Add-in dev server running at https://localhost:3001
- [ ] HTTPS certificates working (no browser warnings)
- [ ] Add-in loads in Outlook without errors
- [ ] React components render correctly
- [ ] Office.js API calls work

## Manifest Files

- `manifest-dev.xml` - Development (localhost:3001)
- `manifest.xml` - Production (Vercel deployment)

## Troubleshooting

- If HTTPS fails: `npx office-addin-dev-certs install --machine`
- If add-in doesn't load: Check browser console for CORS/certificate errors
- If Office.js fails: Ensure add-in is properly sideloaded

## Integration with Web Portal

The add-in can communicate with the web portal at localhost:3000 for:

- User authentication status
- Calendar integration
- Meeting scheduling workflows
