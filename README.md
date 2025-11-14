# NTAL Telehealth MVP

[![CI](https://github.com/tiwa-codes/NTAL/actions/workflows/ci.yml/badge.svg)](https://github.com/tiwa-codes/NTAL/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> Inclusive, safe telehealth via USSD/SMS/WhatsApp and an offline-first CHW app, with FHIR-based clinical data and consent/audit by design.

## 🌟 Features

- 🏥 **Store-and-Forward Triage** - Patients submit symptoms asynchronously
- 👨‍⚕️ **Provider Dashboard** - Healthcare professionals review and manage cases
- 🔐 **Secure Authentication** - JWT-based provider authentication
- 📱 **Multi-Channel Access** - Web, USSD, SMS, WhatsApp, IVR (stubs ready)
- 💻 **PWA Support** - Offline-capable Progressive Web App
- 🐳 **Docker Ready** - Containerized deployment
- ✅ **Tested** - Comprehensive test coverage with pytest
- 📖 **OpenAPI Docs** - Auto-generated API documentation

## 🏗️ Architecture

### Backend
- **FastAPI** - Modern, fast Python web framework
- **Pydantic** - Data validation using Python type annotations
- **SQLAlchemy** - SQL toolkit and ORM
- **SQLite** - Development database (PostgreSQL-ready for production)
- **Redis** - Session state and rate limiting for USSD
- **JWT Authentication** - Secure provider authentication
- **OpenAPI** - Auto-generated API documentation
- **pytest** - Testing framework

### Frontend
- **React 18** - UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool
- **Tailwind CSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **PWA** - Progressive Web App support

### Multi-Channel Access (Adapters)
- **USSD** - Feature phone support
- **SMS** - Text message integration
- **WhatsApp** - WhatsApp Business API
- **IVR** - Voice response system
- **Web** - Browser-based access

### Architecture Diagrams

Visual architecture diagrams are available in Mermaid format:

- **System Flow** - USSD-first end-to-end flow from citizens to providers
- **USSD Session Sequence** - Detailed sequence diagram of a typical USSD session
- **Components Overview** - High-level component architecture

**Mermaid sources:** `docs/architecture/diagrams/*.mmd`

**Render locally:**
```bash
npm install -D @mermaid-js/mermaid-cli
bash scripts/render-diagrams.sh
```

**Outputs:** `docs/architecture/diagrams/out/*.png` and `*.pdf`

The GitHub Action workflow automatically renders and uploads diagram artifacts on every change. Download them from the Actions tab.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)

### Option 1: Local Development

#### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Run database migrations (tables are auto-created)
# Seed initial data
python seed_data.py

# Note: If you encounter bcrypt compatibility issues, you may need to:
# pip install bcrypt==4.0.1

# Start development server
uvicorn app.main:app --reload
# Or use the convenience script:
# ./start-dev.sh
```

The backend will be available at http://localhost:8000
- API Documentation: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

#### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Start development server
npm run dev
```

The frontend will be available at http://localhost:5173

### Option 2: Docker

```bash
# Build and start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest -v
```

### Test Credentials

After seeding the database, use these credentials to login:

- **Doctor**: `dr.smith` / `pass123`
- **Nurse**: `nurse.jane` / `pass123`
- **CHW**: `chw.mary` / `pass123`

## 📡 API Endpoints

### Public Endpoints
- `GET /api/v1/health` - Health check
- `POST /api/v1/triage` - Submit patient triage (store-and-forward)
- `POST /api/v1/auth/login` - Provider login

### Protected Endpoints (Requires JWT)
- `GET /api/v1/me` - Get current provider info
- `GET /api/v1/encounters` - List all encounters
- `GET /api/v1/encounters/:id` - Get specific encounter
- `PUT /api/v1/encounters/:id` - Update encounter

## 🎯 Features

### For Patients
- ✅ Submit triage information via web form
- ✅ Store-and-forward model (async consultation)
- 📱 Multi-channel support (Web, USSD, SMS, WhatsApp, IVR)

### For Healthcare Providers
- ✅ Secure authentication with JWT
- ✅ Dashboard to view all cases
- ✅ Filter cases by status
- ✅ View detailed case information
- ✅ Update case status and urgency
- ✅ Add provider notes

### Technical Features
- ✅ RESTful API with OpenAPI documentation
- ✅ Type-safe code (Python type hints + TypeScript)
- ✅ Responsive UI with Tailwind CSS
- ✅ PWA support (offline capability)
- ✅ CORS enabled for cross-origin requests
- ✅ Comprehensive test coverage
- ✅ CI/CD with GitHub Actions
- ✅ Docker containerization

## 🔌 Adapter Stubs

Located in `backend/app/adapters/`:

- `ussd_adapter.py` - USSD integration for feature phones
- `sms_adapter.py` - SMS gateway integration
- `whatsapp_adapter.py` - WhatsApp Business API integration
- `ivr_adapter.py` - Interactive Voice Response integration

These are currently stubs ready for implementation with actual service providers.

## 📊 Database Schema

### Providers Table
- `id` - Primary key
- `username` - Unique username
- `email` - Email address
- `hashed_password` - Bcrypt hashed password
- `full_name` - Full name
- `role` - Provider role (doctor, nurse, chw, admin)
- `created_at` - Timestamp

### Encounters Table
- `id` - Primary key
- `patient_name` - Patient name
- `patient_phone` - Contact number
- `patient_age` - Age (optional)
- `patient_gender` - Gender (optional)
- `chief_complaint` - Main health concern
- `symptoms` - Detailed symptoms
- `duration` - Duration of symptoms
- `medical_history` - Past medical history
- `status` - pending, in_progress, completed, closed
- `urgency` - low, medium, high, critical
- `source` - web, ussd, sms, whatsapp, ivr
- `assigned_provider_id` - FK to providers
- `notes` - Provider notes
- `created_at` - Timestamp
- `updated_at` - Last update timestamp

## 🔒 Security

- JWT-based authentication
- Password hashing with bcrypt
- CORS protection
- Environment variable configuration
- SQL injection prevention (SQLAlchemy ORM)
- **USSD Privacy**: MSISDN hashed with SHA-256 + pepper; no PII in logs
- **Rate Limiting**: 10 USSD triages per phone number per 24 hours
- **Consent Tracking**: Version-tracked consent with each USSD session

## 📱 USSD Integration

### Overview

NTAL supports USSD as the primary entry point for patients with feature phones. The USSD flow guides users through a consent process, symptom collection, automated triage, and optional callback request.

### USSD Flow

1. **Consent** → User agrees to data processing (NDPA-compliant)
2. **Language Selection** → English or Yoruba
3. **Demographics** → Age group (anonymized) and gender
4. **Symptom Assessment** → Fever, headache, danger signs, cough
5. **Triage Result** → Risk level with advice
6. **Callback Option** → Request provider callback if needed

### Risk Levels

- **EMERGENCY**: Danger signs present (difficulty breathing, chest pain, confusion, severe bleeding) → Urgent callback
- **MALARIA_SUSPECT**: Fever + severe headache → High priority callback
- **FEVER_GENERAL**: Fever only → Medium priority callback
- **LOW_RISK**: No significant symptoms → Low priority callback

### API Endpoint

**POST /api/v1/ussd**

Request format (from USSD aggregator):
```json
{
  "sessionId": "ATUid_abc123",
  "phoneNumber": "+254712345678",
  "serviceCode": "*123#",
  "text": "1*2*3"
}
```

Response format:
```json
{
  "response": "CON Select age group:\n1. Under 5\n2. 5-17 years\n3. 18-49 years\n4. 50+ years"
}
```

- `CON` = Continue session (show menu)
- `END` = End session (final message)

### Testing USSD Locally

#### 1. Start the backend with Redis:

```bash
# Using Docker Compose (recommended)
docker-compose up

# Or locally with Redis installed
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

#### 2. Use the USSD Simulator:

```bash
cd backend

# Interactive mode
python ussd_simulator.py interactive +254712345678

# Run automated scenarios
python ussd_simulator.py scenario low_risk
python ussd_simulator.py scenario emergency
python ussd_simulator.py scenario malaria
python ussd_simulator.py scenario callback
```

### Callback Queue

Providers can manage callback requests through authenticated endpoints:

**GET /api/v1/callbacks** - List callbacks (filter by status/priority)
**POST /api/v1/callbacks/:id/assign** - Assign to provider
**POST /api/v1/callbacks/:id/complete** - Mark complete with outcome

### Analytics

**GET /api/v1/metrics/ussd** (Admin only)

Returns:
- Total USSD sessions and completion rate
- Risk distribution
- Daily encounter counts (last 7 days)
- Callback SLA metrics (avg time to assign/complete)

### Privacy & Data Minimization

USSD encounters store:
- ✅ Hashed MSISDN (SHA-256 + pepper) - NOT plain phone number
- ✅ Age group (e.g., "18-49") - NOT exact age
- ✅ Gender
- ✅ Symptom responses (structured JSON)
- ✅ Risk code and consent version

USSD encounters do NOT store:
- ❌ Patient name
- ❌ Exact phone number
- ❌ Location data
- ❌ Medical history details

### Rate Limiting

To prevent abuse, USSD enforces a rate limit of **10 triages per phone number per 24 hours**. After exceeding the limit, users receive:

```
END Limit reached. Try again tomorrow.
```

### Language Support

Current languages:
- **English (en)** - Default
- **Yoruba (yo)** - Nigerian language

Messages are kept concise (≤160 characters) for USSD compatibility. New languages can be added in `app/core/language_strings.py`.

### Aggregator Integration

To integrate with a real USSD aggregator:

1. Configure your USSD code (e.g., `*123#`) with the aggregator
2. Set the callback URL to: `https://your-domain.com/api/v1/ussd`
3. Ensure the aggregator sends POST requests with the standard fields
4. Configure environment variables in `.env`:

```env
REDIS_URL=redis://localhost:6379
HASH_PEPPER=your-secret-pepper-value-change-in-production
CONSENT_VERSION=v0.1-EN-USSD
RATE_LIMIT_MAX=10
```

## 🚢 Deployment

### Environment Variables

#### Backend (.env)
```env
DATABASE_URL=sqlite:///./ntal.db
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis for USSD session state and rate limiting
REDIS_URL=redis://localhost:6379

# USSD configuration
HASH_PEPPER=your-hash-pepper-change-in-production
CONSENT_VERSION=v0.1-EN-USSD
RATE_LIMIT_MAX=10
```

For PostgreSQL:
```env
DATABASE_URL=postgresql://user:password@localhost/ntal
```

#### Frontend (.env)
```
VITE_API_URL=http://localhost:8000/api/v1
```

## 📁 Project Structure

```
NTAL/
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   └── endpoints.py       # API routes
│   │   ├── adapters/              # Channel adapters (USSD, SMS, etc.)
│   │   ├── core/
│   │   │   ├── config.py          # Configuration
│   │   │   ├── database.py        # Database setup
│   │   │   └── security.py        # Auth & security
│   │   ├── models/
│   │   │   └── models.py          # SQLAlchemy models
│   │   ├── schemas/
│   │   │   └── schemas.py         # Pydantic schemas
│   │   └── main.py                # FastAPI app
│   ├── tests/                     # Pytest tests
│   ├── requirements.txt
│   ├── seed_data.py               # Database seeding
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/            # React components
│   │   ├── contexts/              # React contexts
│   │   ├── pages/                 # Page components
│   │   ├── services/              # API services
│   │   ├── types/                 # TypeScript types
│   │   └── App.tsx                # Main app component
│   ├── public/
│   │   ├── manifest.json          # PWA manifest
│   │   └── service-worker.js     # Service worker
│   ├── package.json
│   └── Dockerfile
├── .github/workflows/
│   └── ci.yml                     # GitHub Actions CI
├── docker-compose.yml
└── README.md
```

## 🛠️ Development

### Adding New Endpoints

1. Add route to `backend/app/api/v1/endpoints.py`
2. Create Pydantic schemas in `backend/app/schemas/schemas.py`
3. Add database models in `backend/app/models/models.py` if needed
4. Write tests in `backend/tests/`

### Adding New Frontend Pages

1. Create component in `frontend/src/pages/`
2. Add route to `frontend/src/App.tsx`
3. Create API service in `frontend/src/services/api.ts`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

## 📄 License

This project is part of the NTAL initiative for inclusive healthcare access.

## 🆘 Support

For issues and questions:
- Open an issue on GitHub
- Contact the development team

## 🔧 Troubleshooting

### Backend

**bcrypt compatibility issues**
```bash
# If you encounter bcrypt errors during installation or seeding:
pip uninstall bcrypt
pip install bcrypt==4.0.1
```

**Database locked errors**
```bash
# If SQLite database is locked, close any existing connections:
rm ntal.db
python seed_data.py
```

**Import errors**
```bash
# Ensure all dependencies are installed:
pip install -r requirements.txt
```

### Frontend

**Build errors with Tailwind**
```bash
# Clear node_modules and reinstall:
rm -rf node_modules package-lock.json
npm install
```

**CORS errors**
```bash
# Ensure backend is running and CORS is properly configured
# Check that VITE_API_URL in .env points to the correct backend URL
```

### Docker

**Port already in use**
```bash
# Change ports in docker-compose.yml or stop conflicting services
docker-compose down
docker-compose up
```

**Redis connection issues**
```bash
# Ensure Redis is running
redis-cli ping  # Should return PONG

# Or start with Docker
docker run -d -p 6379:6379 redis:7-alpine
```

## 🗺️ Roadmap

- [x] USSD flow with triage engine
- [x] Callback queue system
- [x] Multi-language support (EN, Yoruba)
- [x] Rate limiting and analytics
- [ ] Provider dashboard UI for callbacks
- [ ] Real USSD aggregator integration
- [ ] SMS/WhatsApp/IVR production integrations
- [ ] FHIR/DHIS2 export
- [ ] Real-time chat support
- [ ] Video consultation
- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard
- [ ] Audit logging
- [ ] Integration with existing EMR systems

