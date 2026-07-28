# 🌱 Eco Monitor System

A scalable **carbon footprint monitoring and carbon credit management platform** designed using modern backend architecture, microservices concepts, and observability tools.

---

## 📌 Project Overview

Eco Monitor is a system that allows:

* Tracking carbon emissions
* Managing carbon credits
* Maintaining financial/credit ledger
* Monitoring sustainability metrics
* Visualizing data through dashboards

This project follows a **modular backend architecture** with clear separation of concerns:

* API Layer
* Business Logic Layer
* Data Layer
* Monitoring Layer

---

## 🎯 Objectives

* Build a **scalable backend system**
* Track **carbon usage & emissions**
* Manage **carbon credits & transactions**
* Provide **real-time monitoring**
* Enable **future microservices transition**

---

## 🏗️ System Architecture

### 🔹 High-Level Flow

```
User → API → Services → Database
                ↓
          Monitoring Tools
                ↓
            Dashboard
```

---

### 🔹 Detailed Architecture

#### 1. API Layer (`backend/api/`)

Handles incoming HTTP requests

* `auth.py` → Authentication APIs
* `user.py` → User management
* `carbon.py` → Carbon tracking
* `credits.py` → Credit management
* `ledger.py` → Transactions
* `portfolio.py` → User portfolio
* `health.py` → System health check

---

#### 2. Core Layer (`backend/core/`)

System-wide utilities

* `config.py` → Environment config
* `security.py` → JWT/Auth logic
* `dependencies.py` → Dependency injection

---

#### 3. Service Layer (`backend/services/`)

Business logic (MOST IMPORTANT)

* `auth_service.py`
* `carbon_service.py`
* `credit_service.py`
* `ledger_service.py`
* `portfolio_service.py`

👉 This is where actual logic happens.

---

#### 4. Models (`backend/models/`)

Database structure

* `user.py`
* `transaction.py`
* `carbon_record.py`
* `carbon_credit.py`
* `ledger_entry.py`

---

#### 5. Schemas (`backend/schemas/`)

Request/response validation

* `auth_schema.py`
* `carbon_schema.py`
* `credit_schema.py`
* `ledger_schema.py`

---

#### 6. Database Layer (`backend/db/`)

* `connection.py` → DB connection
* `session.py` → ORM session
* `base.py` → Base model
* `seed.py` → Initial data

---

#### 7. Middleware (`backend/middleware/`)

* Authentication guard
* Logging
* Error handling

---

#### 8. Frontend (`frontend/`)

Basic UI layer:

* `index.html`
* `app.js`
* `styles.css`

---

#### 9. Monitoring & Observability

(Planned / Extendable)

* Prometheus → Metrics
* Grafana → Dashboards
* Kepler → Energy monitoring

---

#### 10. Docker (`docker/`)

* `Dockerfile`
* `docker-compose.yml`

👉 Used for containerization & deployment

---

## 🔄 Workflow

### 1. User Authentication Flow

```
User → /auth/login → auth_service → DB → Token → User
```

---

### 2. Carbon Tracking Flow

```
User → /carbon/add
      → carbon_service
      → DB (carbon_record)
      → Response
```

---

### 3. Credit System Flow

```
Carbon Data → credit_service
            → Calculate credits
            → Store in DB
```

---

### 4. Ledger Transaction Flow

```
User Action → ledger_service
            → transaction + ledger_entry
            → DB
```

---

### 5. Portfolio Flow

```
User → /portfolio
     → portfolio_service
     → Aggregate data
     → Return summary
```

---

## 📂 Project Structure
🌳 Complete Folder Structure
eco-monitor/
│   .env
│   .gitignore
│   README.md
│   requirements.txt
│
├── backend/
│   │   config.py
│   │   constants.py
│   │   main.py
│   │
│   ├── api/
│   │       auth.py
│   │       carbon.py
│   │       credits.py
│   │       health.py
│   │       ledger.py
│   │       portfolio.py
│   │       user.py
│   │
│   ├── core/
│   │       config.py
│   │       dependencies.py
│   │       security.py
│   │
│   ├── db/
│   │       base.py
│   │       connection.py
│   │       database.py
│   │       seed.py
│   │       session.py
│   │
│   ├── middleware/
│   │       auth_guard.py
│   │       auth_middleware.py
│   │       error_handler.py
│   │       logger.py
│   │       logging_middleware.py
│   │
│   ├── models/
│   │       account.py
│   │       carbon_credit.py
│   │       carbon_record.py
│   │       credit.py
│   │       ledger_entry.py
│   │       transaction.py
│   │       user.py
│   │
│   ├── schemas/
│   │       auth_schema.py
│   │       carbon_schema.py
│   │       credit_schema.py
│   │       ledger_schema.py
│   │       user_schema.py
│   │
│   └── services/
│           auth_service.py
│           carbon_service.py
│           credit_service.py
│           ledger_service.py
│           portfolio_service.py
│
├── docker/
│       docker-compose.yml
│       Dockerfile
│
├── docs/
│       api-endpoints.md
│       architecture.md
│
├── frontend/
│       app.js
│       index.html
│       styles.css
│
└── tests/
        test_api.py
        test_auth.py
        test_carbon.py
📌 Root Files
.env

Stores environment variables like:

Database URL
Secret keys (JWT, API keys)
Config settings

👉 Keeps sensitive data secure and separate from code.

.gitignore

Specifies files/folders Git should ignore:

.env
__pycache__/
node_modules/
Logs
README.md

Main documentation file:

Project overview
Setup steps
Architecture
API usage
requirements.txt

Lists all Python dependencies:

fastapi
uvicorn
sqlalchemy
pydantic
⚙️ Backend (Core System)
backend/main.py

🚀 Entry point of backend:

Starts FastAPI server
Registers routes
Loads middleware
backend/config.py

Global configuration settings:

App config
Environment configs
backend/constants.py

Stores fixed values:

Status codes
Default limits
Static configs
🌐 API Layer (backend/api/)

Handles HTTP routes (endpoints)

auth.py
Login / Signup APIs
Token generation
carbon.py
Carbon tracking endpoints
Emission data APIs
credits.py
Carbon credit management
Buying/selling credits
health.py
Health check endpoint (/health)
Server status
ledger.py
Transaction history APIs
portfolio.py
User portfolio data
Carbon + financial summary
user.py
User profile APIs
Update / fetch user
🧠 Core Logic (backend/core/)
config.py
Internal config loader
Reads .env
dependencies.py
Dependency injection (FastAPI)
DB session provider
security.py
JWT authentication
Password hashing
🗄️ Database Layer (backend/db/)
base.py
Base ORM model (SQLAlchemy)
connection.py
Database connection setup
database.py
DB initialization
seed.py
Inserts initial data (test users, etc.)
session.py
DB session management
🛡️ Middleware (backend/middleware/)
auth_guard.py
Protects routes (auth required)
auth_middleware.py
Validates tokens in requests
error_handler.py
Global error handling
logger.py
Logging setup
logging_middleware.py
Logs every request/response
🧩 Models (backend/models/)

Defines database tables

account.py
User accounts
carbon_credit.py
Carbon credit assets
carbon_record.py
Emission records
credit.py
Credit transactions
ledger_entry.py
Financial logs
transaction.py
Transaction history
user.py
User table schema
🔄 Schemas (backend/schemas/)

Defines request/response formats (Pydantic)

auth_schema.py
Login/signup structure
carbon_schema.py
Carbon data format
credit_schema.py
Credit request/response
ledger_schema.py
Ledger response format
user_schema.py
User data validation
⚡ Services (backend/services/)

Business logic layer

auth_service.py
Handles login logic
carbon_service.py
Carbon calculations
credit_service.py
Credit operations
ledger_service.py
Ledger updates
portfolio_service.py
Portfolio analytics
🐳 Docker (docker/)
Dockerfile
Defines backend container
docker-compose.yml
Runs multiple services:
Backend
Database
📚 Documentation (docs/)
api-endpoints.md
List of all APIs
Request/response examples
architecture.md
System design
Flow diagrams
🎨 Frontend (frontend/)
index.html
Main UI layout
styles.css
Styling
app.js
Frontend logic
API calls
🧪 Tests (tests/)
test_api.py
API endpoint tests
test_auth.py
Authentication tests
test_carbon.py
Carbon logic tests
🔁 Workflow Architecture (High-Level)
User → Frontend → API → Services → Database
                         ↓
                  Business Logic
                         ↓
                    Response → Frontend
---

## ⚙️ Tech Stack

### Backend

* Python (FastAPI recommended)
* SQLAlchemy (ORM)
* JWT Authentication

### Database

* PostgreSQL / SQLite (dev)

### Frontend

* HTML, CSS, JS

### DevOps

* Docker
* Docker Compose

### Monitoring (Future)

* Prometheus
* Grafana

---

## 🔐 Functional Requirements

* User authentication & authorization
* Carbon emission tracking
* Carbon credit calculation
* Ledger transaction system
* Portfolio management
* API-based architecture

---

## ⚡ Non-Functional Requirements

* Scalable architecture
* Secure authentication (JWT)
* High availability
* Modular design
* Maintainability
* Logging & monitoring support

---

## 🧪 Testing

Located in `/tests`

* API tests
* Auth tests
* Carbon logic tests

---

## 🚀 How to Run

### 1. Install dependencies

```
pip install -r requirements.txt
```

---

### 2. Run backend

```
uvicorn backend.main:app --reload
```

---

### 3. Run with Docker

```
docker-compose up --build
```

---

## 📈 Future Enhancements

* Microservices split
* Blockchain for carbon credits
* AI-based emission prediction
* Real-time dashboards
* External API integrations

---

## 🧠 Key Concepts Used

* Layered Architecture
* Separation of Concerns
* REST API Design
* ORM (Object Relational Mapping)
* Authentication & Authorization
* Observability Design

---

## 👨‍💻 Contribution

This project is structured for:

* Learning system design
* Backend engineering practice
* Real-world scalable architecture

---

## 📜 License

MIT License

---

If you want next step, we can now:
👉 Start **coding backend (FastAPI setup)**
👉 OR build **auth system first (best starting point)**
