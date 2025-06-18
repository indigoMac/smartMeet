# SmartMeet Development Roadmap

## Current Status ✅

- **OAuth Web Portal**: Working perfectly ✅
- **Railway Backend**: Deployed and functional ✅
- **Vercel Frontend**: Deployed and working ✅
- **Azure Integration**: Properly configured ✅

## Current Issues 🔴

### Outlook Add-in OAuth Problem

- **Issue**: OAuth button doesn't work in Outlook add-in
- **Root Cause**: Popup-based OAuth doesn't work well in Office add-ins
- **Impact**: Users can't authenticate within the actual Outlook application
- **Status**: Needs immediate fix

### Architecture Debt

- **Backend**: Single file (main.py) - not scalable
- **Database**: No persistent storage - using in-memory dictionary
- **Testing**: No test suite
- **CI/CD**: Basic deployment, no proper environments

## Development Priorities

### 🔥 PHASE 1: Critical Fixes (Week 1)

#### 1.1 Fix Outlook Add-in OAuth

**Goal**: Make authentication work within Outlook application
**Approach**:

- Replace popup with Office Dialog API
- Create dedicated auth callback for add-ins
- Implement proper token sharing between contexts

**Files to modify**:

- `apps/outlook-addin/src/taskpane/taskpane.tsx`
- `apps/api-backend/main.py` (add add-in auth endpoint)

#### 1.2 Database Setup

**Goal**: Replace in-memory storage with persistent database
**What to store**:

- Users (id, email, name, created_at, updated_at)
- OAuth tokens (user_id, provider, access_token, refresh_token, expires_at)
- Meeting requests (id, created_by, participants, proposed_times, status)
- Calendar events cache (for performance optimization)

**Technology**: PostgreSQL on Railway
**Steps**:

1. Add Railway PostgreSQL service
2. Install SQLAlchemy + Alembic
3. Create database models
4. Migrate existing in-memory logic

### 🛠️ PHASE 2: Backend Restructure (Week 2)

#### 2.1 Modular Backend Architecture

**Current**: Single file (main.py) with 700+ lines
**Target**: Proper FastAPI structure

```
apps/api-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app setup
│   ├── config.py            # Environment config
│   ├── database.py          # DB connection & session
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── oauth_token.py
│   │   └── meeting.py
│   ├── routers/             # API route modules
│   │   ├── __init__.py
│   │   ├── auth.py          # OAuth routes
│   │   ├── calendar.py      # Calendar integration
│   │   └── meetings.py      # Meeting management
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── oauth_service.py
│   │   ├── calendar_service.py
│   │   └── meeting_service.py
│   ├── schemas/             # Pydantic models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── meeting.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── migrations/              # Alembic migrations
├── tests/                   # Test files
│   ├── test_auth.py
│   ├── test_calendar.py
│   └── test_meetings.py
├── requirements.txt
└── alembic.ini
```

#### 2.2 Error Handling & Logging

- Structured logging with proper levels
- Error tracking and monitoring
- Graceful error responses for frontend

### 🎨 PHASE 3: New UI/Features (Week 3-4)

#### 3.1 New UI Requirements

**Status**: Waiting for user specifications
**Questions**:

- What new features are needed?
- UI/UX changes for web portal?
- Changes to Outlook add-in interface?
- Additional calendar providers (Google Calendar completion)?

#### 3.2 Enhanced Outlook Add-in

**Improvements**:

- Better user experience
- Meeting template management
- Calendar conflict detection
- Bulk scheduling capabilities

### 🧪 PHASE 4: Testing & Quality (Week 5)

#### 4.1 Test Suite Implementation

**Backend Tests**:

- Unit tests (pytest)
- Integration tests for OAuth flows
- API endpoint tests
- Database model tests

**Frontend Tests**:

- React component tests (Jest + React Testing Library)
- E2E tests for OAuth flows
- Outlook add-in testing

#### 4.2 Code Quality

- ESLint/Prettier for TypeScript
- Black/isort for Python
- Pre-commit hooks
- Code coverage reporting

### 🚀 PHASE 5: DevOps & Production (Week 6)

#### 5.1 Environment Setup

**Environments**:

- **Development**: Local development
- **Staging**: Testing environment
- **Production**: Live environment

**Infrastructure**:

- Railway for backend (all environments)
- Vercel for frontends (all environments)
- Separate databases per environment

#### 5.2 CI/CD Pipeline

**GitHub Actions**:

- Automated testing on PR
- Deployment to staging on merge to `develop`
- Deployment to production on merge to `main`
- Database migrations
- Environment variable management

#### 5.3 Monitoring & Alerts

- Application performance monitoring
- Error tracking (Sentry?)
- Uptime monitoring
- Log aggregation

## Technical Debt Items

### High Priority

- [ ] Database implementation
- [ ] Backend code organization
- [ ] OAuth token refresh handling
- [ ] Error handling standardization

### Medium Priority

- [ ] Caching layer for calendar data
- [ ] Rate limiting implementation
- [ ] API documentation (OpenAPI/Swagger)
- [ ] Security audit

### Low Priority

- [ ] Performance optimization
- [ ] Advanced scheduling algorithms
- [ ] Multi-timezone support enhancement
- [ ] Mobile responsiveness

## Dependencies & Tools

### Current Stack

- **Backend**: FastAPI, Python 3.11
- **Frontend**: Next.js, React, TypeScript
- **Add-in**: Office.js, React, TypeScript
- **Deployment**: Railway (backend), Vercel (frontends)
- **Authentication**: Azure AD, Google OAuth

### New Dependencies (Proposed)

```python
# Backend additions
sqlalchemy>=2.0.0
alembic>=1.12.0
psycopg2-binary>=2.9.0
pytest>=7.4.0
pytest-asyncio>=0.21.0
factory-boy>=3.3.0  # For test fixtures
```

```json
// Frontend additions
{
  "@testing-library/react": "^13.4.0",
  "@testing-library/jest-dom": "^5.16.5",
  "jest": "^29.6.0",
  "cypress": "^12.17.0"
}
```

## Success Metrics

### Phase 1 Success Criteria

- [ ] Users can authenticate within Outlook add-in
- [ ] Database stores user data persistently
- [ ] OAuth tokens don't expire immediately

### Phase 2 Success Criteria

- [ ] Backend code is modular and maintainable
- [ ] API response times < 500ms
- [ ] Error rates < 1%

### Phase 3 Success Criteria

- [ ] New UI features are implemented and functional
- [ ] User feedback is positive
- [ ] Feature adoption rate > 50%

### Phase 4 Success Criteria

- [ ] Test coverage > 80%
- [ ] No critical bugs in production
- [ ] Automated testing prevents regressions

### Phase 5 Success Criteria

- [ ] Zero-downtime deployments
- [ ] Environment parity achieved
- [ ] Monitoring and alerting functional

## Next Immediate Actions

1. **Get user's new UI requirements** 📋
2. **Set up PostgreSQL on Railway** 🗄️
3. **Fix Outlook add-in OAuth** 🔧
4. **Begin backend restructure** 🏗️

---

## Notes

- This roadmap is flexible and priorities can shift based on user feedback
- Each phase should include user testing and feedback loops
- Technical decisions should be documented as we progress
- Security and performance should be considered at each phase

**Last Updated**: December 17, 2024
**Status**: Draft - Awaiting user input on new UI requirements
