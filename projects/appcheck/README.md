# AppScan Pro

Enterprise mobile application security static scanning platform.

## Features

- Support for Android (APK), iOS (IPA), and HarmonyOS (HAP)
- Static security analysis
- CVSS 3.1 scoring
- Multi-language support (English/Chinese)
- Report generation (HTML/DOCX/PDF)

## Tech Stack

- Backend: Python FastAPI + SQLAlchemy + PostgreSQL
- Frontend: React + TypeScript + Ant Design
- Task Queue: Celery + Redis
- Container: Docker Compose

## Quick Start

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down
```

Services:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/v1/docs

### Manual Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=postgresql://appcheck:appcheck@localhost:5432/appcheck
export SECRET_KEY=your-secret-key

# Run database migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Development

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## License

Proprietary - Internal Use Only
