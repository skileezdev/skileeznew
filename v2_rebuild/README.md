# Skileez V2.0 - Rebuild

This is the modernized version of Skileez, rebuilt for performance, scalability, and better developer experience.

## Tech Stack
- **Backend:** FastAPI (Python 3.12)
- **Frontend:** Next.js 14+ (TypeScript, TailwindCSS)
- **Database:** SQLAlchemy 2.0 (Async)
- **Auth:** JWT (JSON Web Tokens)

## Getting Started

### Backend
1. `cd backend`
2. `pip install -r requirements.txt`
3. `python run.py`
4. Visit `http://localhost:8000/docs` for API documentation.

### Frontend
1. `cd frontend`
2. `npm install`
3. `npm run dev`
4. Visit `http://localhost:3000`

## Structure
- `/backend/app/models`: Refactored database models.
- `/backend/app/api`: Clean, modular API routes.
- `/backend/app/services`: Reusable business logic (no logic in routes!).
