# 🚀 SmartMeet Development Guide

This guide will help you set up the SmartMeet development environment using **PostgreSQL** (same as production) and our professional development tools.

## 🏗️ Architecture Overview

**SmartMeet** is a comprehensive meeting scheduling solution with two main components:

- **Web Portal** (`apps/web-portal`): Next.js app on `localhost:3000`

  - OAuth authentication
  - User management
  - Calendar integration dashboard

- **Outlook Add-in** (`apps/outlook-addin`): React/TypeScript on `localhost:3001`
  - HTTPS required (Microsoft requirement)
  - Direct Outlook integration
  - Meeting scheduling from emails

## 🚀 Quick Start (Professional Setup)

### Option 1: Start Everything Together

```bash
# From project root - starts both portal and add-in
npm run dev
```

### Option 2: Start Components Individually

```bash
# Web Portal only
npm run dev:portal

# Outlook Add-in only
npm run dev:addin

# Outlook Add-in with automatic sideloading (recommended)
npm run dev:addin-auto
```

## 📋 Development Checklist

Before you start developing:

- [ ] ✅ Node.js installed (latest LTS)
- [ ] ✅ Office 365 subscription
- [ ] ✅ Development certificates installed
- [ ] ✅ Web portal accessible at https://localhost:3000
- [ ] ✅ Add-in dev server running at https://localhost:3001
- [ ] ✅ HTTPS certificates working (no browser warnings)
- [ ] ✅ Manifest validation passes: `npm run validate:addin`

## 🔧 Microsoft Office Add-in Best Practices

Your setup now follows Microsoft's official recommendations:

### ✅ What's Correctly Implemented:

- **HTTPS Development Server**: Required for Office add-ins
- **Proper Port Separation**: Avoids conflicts between services
- **Microsoft Development Certificates**: Official SSL certificates
- **Manifest Validation**: Automated checking against Microsoft schema
- **Professional File Structure**: Follows Office add-in conventions
- **Error Handling**: Comprehensive error boundaries for add-in environment
- **Cross-Origin Support**: Proper headers for Office integration

### 🛠️ Available Commands:

```bash
# Validate add-in manifest
npm run validate:addin

# Build for production
npm run build

# Build individual components
npm run build:portal
npm run build:addin
```

## 🧪 Testing Your Add-in

### Manual Testing:

1. Start the add-in: `npm run dev:addin`
2. Open Outlook (web, desktop, or Mac)
3. Navigate to a message
4. Look for "SmartMeet DEV" in the ribbon
5. Click "Schedule Meeting" button

### Automated Testing (Recommended):

```bash
# This automatically sideloads the add-in
npm run dev:addin-auto
```

## 🔍 Troubleshooting

### Common Issues:

**"Add-in won't load"**

- Check browser console for certificate errors
- Verify HTTPS is working: `curl -k https://localhost:3001`
- Ensure manifest is valid: `npm run validate:addin`

**"Office.js not available"**

- Check if add-in is properly sideloaded
- Verify you're testing in a supported Outlook version
- Check browser developer tools for script errors

**"HTTPS Certificate Issues"**

```bash
# Reinstall certificates
cd apps/outlook-addin
npx office-addin-dev-certs install --machine
```

## 🔗 Integration Between Components

The add-in can communicate with the web portal:

```javascript
// Example: Check authentication status
const response = await fetch("https://localhost:3000/api/auth/status");
const authStatus = await response.json();
```

## 📁 File Structure

```
smartMeet/
├── apps/
│   ├── web-portal/          # Next.js OAuth portal
│   │   ├── src/
│   │   └── package.json
│   └── outlook-addin/       # Office add-in
│       ├── src/
│       │   ├── taskpane/    # Main UI components
│       │   └── commands/    # Ribbon commands
│       ├── manifest-dev.xml # Development manifest
│       ├── manifest.xml     # Production manifest
│       └── package.json
└── package.json             # Root development scripts
```

## 🚀 Deployment

### Development:

- Web Portal: Vercel (automatic)
- Add-in: Served from localhost:3001

### Production:

- Web Portal: Vercel deployment
- Add-in: Vercel static hosting (configured in `manifest.xml`)

## 📚 Resources

- [Microsoft Office Add-ins Documentation](https://docs.microsoft.com/office/dev/add-ins/)
- [Outlook Add-in API Reference](https://docs.microsoft.com/javascript/api/outlook)
- [Office Add-in Manifest Reference](https://docs.microsoft.com/office/dev/add-ins/reference/manifest/)

---

**🎉 Your development environment is now professionally configured and follows Microsoft's best practices!**

## 🛠️ **Manual Setup (Step by Step)**

If you prefer to understand each step:

### 1. **Environment Setup**

```bash
# Create environment files
make env-setup

# Edit your OAuth credentials (required for full functionality)
nano .env.local
```

### 2. **Install Dependencies**

```bash
# Install all dependencies (Python + Node.js)
make install-deps
```

### 3. **Database Setup**

```bash
# Start PostgreSQL with Docker
make dev-db

# Check database status
make db-status

# Run migrations
make migrate

# Seed with test data
make db-seed
```

### 4. **Start Development**

```bash
# Start API backend
make start-api

# Or start all services
make dev
```

## 🗄️ **Database Information**

**Connection Details:**

- **URL**: `postgresql://smartmeet:password@localhost:5432/smartmeet_dev`
- **Host**: `localhost`
- **Port**: `5432`
- **Database**: `smartmeet_dev`
- **Username**: `smartmeet`
- **Password**: `password`

**Database Admin Interface:**

- **Adminer**: http://localhost:8080
- **Direct PostgreSQL Console**: `make db-console`

## 🔧 **Available Make Commands**

### Quick Commands

```bash
make first-setup    # Complete first-time setup
make dev           # Start all services
make start-api     # Start API backend only
make stop          # Stop all services
```

### Database Commands

```bash
make dev-db        # Start PostgreSQL database
make db-status     # Check database connection
make migrate       # Run database migrations
make db-seed       # Seed with test data
make db-reset      # Reset database (⚠️ DELETES ALL DATA)
make db-console    # PostgreSQL interactive console
```

### Development Commands

```bash
make start-web     # Start Next.js web portal
make start-addin   # Start Outlook add-in
make console       # Python interactive console
make logs          # Show database logs
```

### Utility Commands

```bash
make test          # Run all tests
make lint          # Run linting
make clean         # Clean up containers
```

## 🌐 **Access Points**

Once running, you can access:

| Service               | URL                        | Description                |
| --------------------- | -------------------------- | -------------------------- |
| **API Backend**       | http://localhost:8000      | FastAPI backend            |
| **API Documentation** | http://localhost:8000/docs | Interactive API docs       |
| **Web Portal**        | http://localhost:3000      | Next.js web application    |
| **Outlook Add-in**    | http://localhost:3001      | Outlook add-in interface   |
| **Database Admin**    | http://localhost:8080      | Adminer database interface |

## 🔐 **OAuth Setup**

To enable calendar integration, you'll need to set up OAuth applications:

### Microsoft Azure App Registration

1. Go to [Azure Portal](https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps)
2. Create new app registration
3. Required permissions:
   - `Calendars.Read`
   - `Calendars.Read.Shared`
   - `User.Read`
4. Add redirect URI: `http://localhost:3000/auth/microsoft/callback`
5. Copy Client ID and Client Secret to `.env.local`

### Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create OAuth 2.0 credentials
3. Required scope: `https://www.googleapis.com/auth/calendar.readonly`
4. Add redirect URI: `http://localhost:3000/auth/google/callback`
5. Copy Client ID and Client Secret to `.env.local`

## 🐳 **Docker Services**

The development environment uses Docker for:

- **PostgreSQL 15**: Main database
- **Redis 7**: Caching (optional)
- **Adminer**: Database administration interface

Start all with: `make dev-db`

## 📊 **Database Management**

### Common Operations

```bash
# Check what's in the database
make console
> with get_db_session() as db:
>     users = db.query(User).all()
>     print([u.email for u in users])

# Reset and reseed database
make db-reset
make db-seed

# View database logs
make logs
```

### Migration Status

```bash
make migration:status
```

## 🧪 **Testing**

```bash
# Run all tests
make test

# Run specific service tests
cd apps/api-backend && python -m pytest
cd apps/web-portal && npm test
```

## 🚨 **Troubleshooting**

### Database Connection Issues

```bash
# Check if PostgreSQL is running
make db-status

# Restart database
make stop
make dev-db

# Check logs
make logs
```

### Port Conflicts

If ports are in use, stop services:

```bash
make stop
```

### Clean Installation

```bash
# Complete cleanup and restart
make clean
make first-setup
```

## 🔄 **Daily Development Workflow**

```bash
# 1. Pull latest changes
git pull

# 2. Install any new dependencies
make install-deps

# 3. Start database
make dev-db

# 4. Run any new migrations
make migrate

# 5. Start API
make start-api

# 6. Start frontend (in another terminal)
make start-web
```

## 📁 **Project Structure**

```
smartMeet/
├── packages/database/     # Shared database models & connection
├── tools/database/        # Database management CLI
├── apps/api-backend/      # FastAPI backend
├── apps/web-portal/       # Next.js web app
├── apps/outlook-addin/    # Outlook add-in
├── docker/               # Docker Compose files
├── .env.local            # Environment variables
└── Makefile              # Development commands
```

This structure follows **monorepo best practices** with shared packages and clean separation of concerns.

## 🤝 **Need Help?**

1. Run `make help` to see all available commands
2. Check the logs with `make logs`
3. Verify database status with `make db-status`
4. Reset everything with `make clean && make first-setup`
