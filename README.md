# NTAL Telehealth MVP

Inclusive, safe telehealth via USSD/SMS/WhatsApp and an offline-first CHW app, with FHIR-based clinical data and consent/audit by design.

## 🏗️ Architecture

### Backend
- **FastAPI** - Modern, fast Python web framework
- **Pydantic** - Data validation using Python type annotations
- **SQLAlchemy** - SQL toolkit and ORM
- **SQLite** - Development database (PostgreSQL-ready for production)
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

# Start development server
uvicorn app.main:app --reload
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

- **Doctor**: `dr.smith` / `password123`
- **Nurse**: `nurse.jane` / `password123`
- **CHW**: `chw.mary` / `password123`

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

## 🚢 Deployment

### Environment Variables

#### Backend (.env)
```
DATABASE_URL=sqlite:///./ntal.db
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

For PostgreSQL:
```
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

## 🗺️ Roadmap

- [ ] FHIR integration
- [ ] Real-time chat support
- [ ] Video consultation
- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Consent management
- [ ] Audit logging
- [ ] Integration with existing EMR systems

