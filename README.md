# CosmaCare
### Astronaut Health Monitoring System

**NASA Space Apps Challenge 2026**  
**Team:** comsian  
**Challenge:** Create Health Monitoring Software for Astronauts on Space Missions

## 1. Project Overview

CosmaCare is a health-monitoring software prototype designed to support astronaut health monitoring during space missions.

It provides a dashboard for managing crew information, recording vital health measurements, monitoring alerts, and reviewing telemetry history.

The system demonstrates how health data can be collected and monitored to help mission teams identify potentially concerning health measurements.

## 2. Problem Statement

Astronauts operating in space missions may experience health challenges associated with microgravity, isolation, confinement, radiation exposure, and demanding mission conditions.

Continuous monitoring of crew health information can help mission teams identify abnormal readings and respond to potential health concerns.

CosmaCare demonstrates a software-based approach to organizing and monitoring astronaut health telemetry.

## 3. Implemented Features

- Crew member management.
- Health telemetry submission.
- Heart rate monitoring.
- Blood oxygen (SpO2) monitoring.
- Body temperature monitoring.
- Systolic and diastolic blood pressure recording.
- Automatic alert generation based on configured health thresholds.
- Critical alert identification.
- Alert acknowledgement.
- Telemetry history.
- Dashboard summaries and visual monitoring.
- REST API backend.
- SQLite database storage.

## 4. Technology Stack

| Component | Technology |
|---|---|
| Frontend | React |
| Backend | Python, FastAPI |
| Database | SQLite |
| ORM | SQLAlchemy |
| Data validation | Pydantic |
| API server | Uvicorn |
| Testing | Pytest |
| Charts | Recharts |
| Icons | Lucide React |

## 5. System Architecture

CosmaCare follows a frontend-backend architecture.

1. The React frontend provides the dashboard and user interface.
2. The frontend sends HTTP requests to the FastAPI backend.
3. FastAPI processes requests and validates incoming data.
4. SQLAlchemy manages database operations.
5. SQLite stores crew information, telemetry records, and alerts.
6. The backend returns responses to update the dashboard.

## 6. Project Structure

```text
cosmacare/
│
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   │   ├── alerts.py
│   │   │   ├── crew.py
│   │   │   └── telemetry.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── engine.py
│   │   ├── main.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── data/
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── pytest.ini
│
├── frontend/
│   └── Frontend/
│       ├── public/
│       ├── src/
│       │   ├── App.js
│       │   └── index.js
│       └── package.json
│
└── README.md
```

## 7. Installation and Setup

### Requirements

- Python 3.12
- Node.js and npm
- Windows, Linux, or macOS

### Backend Setup

Open a terminal in the project root:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
cd backend
pip install -r requirements.txt
```

Start the backend server:

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8081
```

Backend address:

`http://127.0.0.1:8081`

API documentation:

`http://127.0.0.1:8081/docs`

### Frontend Setup

Open a second terminal in the project root:

```powershell
cd frontend\Frontend
npm install
npm start
```

Open the frontend in your browser using the address displayed by React, normally:

`http://localhost:3000`

If port 3000 is already occupied, React may use port 3001.

## 8. API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Backend health check |
| GET | `/crew/` | Retrieve crew members |
| POST | `/crew/` | Add a crew member |
| GET | `/crew/{crew_id}` | Retrieve a crew member |
| POST | `/telemetry/` | Submit health telemetry |
| GET | `/telemetry/{crew_id}` | Retrieve telemetry history |
| GET | `/alerts/` | Retrieve alerts |
| POST | `/alerts/{alert_id}/acknowledge` | Acknowledge an alert |

## 9. Database

CosmaCare uses SQLite with SQLAlchemy.

The default database is automatically created in:

`backend/data/cosmacare.db`

SQLite Write-Ahead Logging (WAL) mode is enabled for database operations.

## 10. Testing

The backend includes automated tests for:

- Database operations
- Crew management
- Telemetry submission
- Alert management
- Health monitoring engine
- Data validation
- Performance testing

Run the tests from the backend directory:

```powershell
pytest -q
```

## 11. Future Improvements

Potential future development includes:

- Offline-first operation for communication-limited environments.
- AI-assisted health risk prediction.
- Radiation exposure monitoring.
- Isolation and confinement risk indicators.
- Integration with wearable health sensors.
- Advanced crew health analytics.
- Improved mission control reporting.

These are proposed improvements and are not claimed as completed functionality.

## 12. Project Goal

CosmaCare aims to demonstrate a practical software prototype for astronaut health data monitoring and alert management, supporting safer and more informed space mission operations.

**Developed for NASA Space Apps Challenge 2026.**