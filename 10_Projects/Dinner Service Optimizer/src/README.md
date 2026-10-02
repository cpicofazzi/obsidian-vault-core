# 🍽️ Dinner Service Optimizer: Backend & Simulation Engine

An intelligent restaurant operations backend powered by FastAPI. Optimizes table allocation, computes wait-time forecasts for walk-ins, and synchronizes multi-course kitchen dispatching across cook stations.

---

## 🏗️ Architecture & Component Overview

```
10_Projects/Dinner Service Optimizer/
├── Dinner Service Optimizer.md    # Master project roadmap & milestones
├── requirements.txt               # Backend dependencies
└── src/
    ├── __init__.py                # Package root
    ├── models.py                  # Pydantic v2 data contracts & schemas
    ├── optimizer.py               # Table seating, wait-time prediction & kitchen coursing logic
    ├── app.py                     # FastAPI REST API & live service simulator
    └── README.md                  # This documentation
```

### Key Modules

1. **`models.py`**:
   - Strongly-typed Pydantic schemas for `Table`, `Party`, `Order`, `OrderItem`, and `KitchenStation`.
   - Enumerations for table statuses (`AVAILABLE`, `OCCUPIED`, `DIRTY`), courses (`BEVERAGE`, `APPETIZER`, `ENTREE`, `DESSERT`), and kitchen stations (`GRILL`, `SAUTE`, `COLD_LARDER`, `PASTRY`, `BAR`).

2. **`optimizer.py`**:
   - **`TableOptimizer`**: Multi-objective heuristic that penalizes excess seat capacity, balances server workload across restaurant sections (Main Dining, Patio, Bar), and gives priority placement to VIPs.
   - **`WaitTimePredictor`**: Computes estimated wait times for walk-in parties based on active table meal progression, turnover cleaning buffers, and queue positioning.
   - **`KitchenDispatchScheduler`**: Staggers course firing so that all entrees for a single table finish synchronously (e.g. staggering an 18-minute steak with a 12-minute risotto), while respecting station load limits.

3. **`app.py`**:
   - FastAPI server with interactive Swagger UI (`/docs`).
   - Endpoints for live party intake, table assignment, coursing dispatch, and simulated time-stepping.

---

## 🚀 Quickstart Guide

### 1. Environment Setup

Clone or open the repository in terminal, then create a virtual environment and install dependencies:

```bash
# Navigate to the project root
cd "10_Projects/Dinner Service Optimizer"

# Create and activate Python virtual environment
python -m venv .venv
source .venv/bin/activate       # On Linux / macOS
# or
.venv\Scripts\Activate.ps1      # On Windows PowerShell

# Install dependencies
pip install -r requirements.txt
```

### 2. Launch the Development Server

From within the `src/` directory:

```bash
cd src
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

Once running, access the interactive API docs at:  
👉 **`http://127.0.0.1:8000/docs`**

---

## 🎮 Interactive Simulation Walkthrough

You can test the entire workflow using `curl` or the Swagger UI:

### Step 1: Seed a Dinner Rush Scenario
Populate the restaurant with 3 seated tables and 3 waiting parties:
```bash
curl -X POST "http://127.0.0.1:8000/simulation/seed-rush"
```

### Step 2: Query Real-Time Service State
Check occupied tables, stations, and current service minute:
```bash
curl -X GET "http://127.0.0.1:8000/state"
```

### Step 3: Estimate Wait Time for a New Walk-In
Calculate expected wait time for an incoming party of 4:
```bash
curl -X POST "http://127.0.0.1:8000/parties/estimate-wait" \
     -H "Content-Type: application/json" \
     -d '{"id": "walkin_99", "name": "Miller Party", "size": 4}'
```

### Step 4: Advance the Clock (Step Simulation)
Advance service time by 10 minutes to cook dishes and process table turnover:
```bash
curl -X POST "http://127.0.0.1:8000/simulation/step" \
     -H "Content-Type: application/json" \
     -d '{"step_minutes": 10}'
```

---

## 🔌 Next Steps & Production Roadmap
- **MIP / OR-Tools Integration**: Extend `optimizer.py` with Google OR-Tools for exact global multi-party table matching.
- **Relational Persistence**: Replace in-memory `STATE` with SQLAlchemy models and an SQLite / PostgreSQL backend.
- **WebSocket Streaming**: Broadcast live station queue updates to kitchen display tablets (KDS).
