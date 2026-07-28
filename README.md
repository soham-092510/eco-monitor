# 🌱 Eco Monitor System

A scalable and modular **Carbon Footprint Monitoring & Carbon Credit Management Platform**, designed using modern backend architecture, clean code principles, and observability-first design.

---

## 📌 Project Overview

Eco Monitor is an end-to-end system that enables:

* 🌍 Tracking carbon emissions
* 💳 Managing carbon credits
* 📊 Maintaining financial & carbon ledgers
* 📈 Monitoring sustainability metrics
* 🖥️ Visualizing insights via dashboards

The system is built using a **layered architecture**, ensuring scalability, maintainability, and easy transition to microservices.

---

## 🎯 Objectives

* Build a **production-ready scalable backend system**
* Track **carbon emissions and environmental impact**
* Manage **carbon credits and transactions efficiently**
* Enable **real-time monitoring & observability**
* Design for **future microservices architecture**

---

## 🏗️ System Architecture

### 🔹 High-Level Flow

```text
User → Frontend → API → Services → Database
                         ↓
                  Monitoring Layer
                         ↓
                      Dashboard
```

---

### 🔹 Architectural Design

The system is divided into well-defined layers:

---

### 1️⃣ API Layer (`backend/api/`)

Handles all incoming HTTP requests and routes them to services.

* `auth.py` → Authentication (Login / Signup / JWT)
* `user.py` → User management
* `carbon.py` → Carbon tracking APIs
* `credits.py` → Carbon credit operations
* `ledger.py` → Transaction & ledger APIs
* `portfolio.py` → Aggregated user data
* `health.py` → System health monitoring

---

### 2️⃣ Core Layer (`backend/core/`)

Provides shared utilities across the application.

* `config.py` → Environment configuration loader
* `security.py` → JWT authentication & password hashing
* `dependencies.py` → Dependency injection (FastAPI)

---

### 3️⃣ Service Layer (`backend/services/`) ⭐

> ⚠️ **Core Business Logic Layer (Most Important)**

* `auth_service.py` → Authentication logic
* `carbon_service.py` → Emission calculations
* `credit_service.py` → Credit computation & management
* `ledger_service.py` → Transaction processing
* `portfolio_service.py` → Portfolio aggregation

---

### 4️⃣ Models (`backend/models/`)

Defines database schema using ORM.

* `user.py`
* `transaction.py`
* `carbon_record.py`
* `carbon_credit.py`
* `ledger_entry.py`

---

### 5️⃣ Schemas (`backend/schemas/`)

Defines request/response validation using Pydantic.

* `auth_schema.py`
* `carbon_schema.py`
* `credit_schema.py`
* `ledger_schema.py`
* `user_schema.py`

---

### 6️⃣ Database Layer (`backend/db/`)

* `connection.py` → Database connection setup
* `session.py` → ORM session handling
* `base.py` → Base model definition
* `database.py` → DB initialization
* `seed.py` → Initial/test data population

---

### 7️⃣ Middleware (`backend/middleware/`)

Handles cross-cutting concerns:

* Authentication guards
* Logging & monitoring
* Global error handling

---

### 8️⃣ Frontend (`frontend/`)

A lightweight UI layer:

* `index.html` → Structure
* `styles.css` → Styling
* `app.js` → API integration

---

### 9️⃣ Observability & Monitoring (Planned)

* Prometheus → Metrics collection
* Grafana → Data visualization
* Kepler → Energy usage monitoring

---

### 🔟 Docker (`docker/`)

* `Dockerfile` → Container configuration
* `docker-compose.yml` → Multi-service orchestration

---

## 🔄 Workflow

### 🔐 Authentication Flow

```text
User → /auth/login → auth_service → DB → JWT Token → User
```

---

### 🌍 Carbon Tracking Flow

```text
User → /carbon/add → carbon_service → DB → Response
```

---

### 💳 Credit System Flow

```text
Carbon Data → credit_service → Compute Credits → Store → DB
```

---

### 📒 Ledger Flow

```text
User Action → ledger_service → Transaction + Ledger Entry → DB
```

---

### 📊 Portfolio Flow

```text
User → /portfolio → portfolio_service → Aggregate Data → Response
```

---

## 📂 Project Structure

> Clean, modular, and production-ready layout

```bash
eco-monitor/
│   .env                         # Environment variables (DB URL, JWT secret, API keys)
│   .gitignore                   # Files ignored by Git (env, cache, logs)
│   README.md                    # Project documentation
│   requirements.txt             # Python dependencies
│
├── backend/                     # Core backend application (FastAPI)
│   │   config.py                # Global configuration settings
│   │   constants.py             # Static values (status codes, defaults)
│   │   main.py                  # Entry point (FastAPI app initialization)
│   │
│   ├── api/                     # API layer (routes/controllers)
│   │       auth.py              # Authentication APIs (login/signup/JWT)
│   │       carbon.py            # Carbon tracking endpoints
│   │       credits.py           # Carbon credit operations APIs
│   │       health.py            # Health check endpoint (/health)
│   │       ledger.py            # Transaction & ledger APIs
│   │       portfolio.py         # Portfolio summary endpoints
│   │       user.py              # User profile management APIs
│   │
│   ├── core/                    # Core utilities (shared across app)
│   │       config.py            # Environment config loader (.env reader)
│   │       dependencies.py      # Dependency injection (DB/session providers)
│   │       security.py          # JWT auth, password hashing, security utils
│   │
│   ├── db/                      # Database layer (SQLAlchemy setup)
│   │       base.py              # Base ORM model class
│   │       connection.py        # Database connection configuration
│   │       database.py          # Database initialization
│   │       seed.py              # Seed script for initial/test data
│   │       session.py           # Database session management
│   │
│   ├── middleware/              # Middleware (request/response processing)
│   │       auth_guard.py        # Protects private routes (auth required)
│   │       auth_middleware.py   # Token validation middleware
│   │       error_handler.py     # Global exception handling
│   │       logger.py            # Logging configuration
│   │       logging_middleware.py# Logs all API requests/responses
│   │
│   ├── models/                  # ORM models (database tables)
│   │       account.py           # Account model (user financial accounts)
│   │       carbon_credit.py     # Carbon credit asset model
│   │       carbon_record.py     # Carbon emission records
│   │       credit.py            # Credit transaction model
│   │       ledger_entry.py      # Ledger entries (financial logs)
│   │       transaction.py       # Transaction history model
│   │       user.py              # User model (main user table)
│   │
│   ├── schemas/                 # Pydantic schemas (validation)
│   │       auth_schema.py       # Auth request/response schemas
│   │       carbon_schema.py     # Carbon data validation schemas
│   │       credit_schema.py     # Credit API schemas
│   │       ledger_schema.py     # Ledger response schemas
│   │       user_schema.py       # User data validation schemas
│   │
│   └── services/                # Business logic layer (core functionality)
│           auth_service.py      # Authentication logic (login, token handling)
│           carbon_service.py    # Carbon calculation & tracking logic
│           credit_service.py    # Credit calculation & management logic
│           ledger_service.py    # Ledger processing & transaction handling
│           portfolio_service.py # Portfolio aggregation & analytics
│
├── docker/                      # Containerization setup
│       docker-compose.yml       # Multi-service orchestration (backend + DB)
│       Dockerfile              # Backend container definition
│
├── docs/                        # Project documentation
│       api-endpoints.md         # API documentation (routes, requests, responses)
│       architecture.md          # System design & architecture explanation
│
├── frontend/                    # Frontend (basic UI)
│       app.js                   # Frontend logic & API calls
│       index.html               # Main HTML structure
│       styles.css               # Styling (UI/UX)
│
└── tests/                       # Testing suite
        test_api.py              # API endpoint tests
        test_auth.py             # Authentication tests
        test_carbon.py           # Carbon logic tests
```

*(Detailed structure explained above in architecture section)*

---

## ⚙️ Tech Stack

### Backend

* Python (FastAPI)
* SQLAlchemy (ORM)
* JWT Authentication

### Database

* PostgreSQL (Production)
* SQLite (Development)

### Frontend

* HTML, CSS, JavaScript

### DevOps

* Docker
* Docker Compose

### Monitoring (Planned)

* Prometheus
* Grafana

---

## 🔐 Functional Requirements

* User authentication & authorization
* Carbon emission tracking
* Carbon credit calculation
* Ledger transaction management
* Portfolio analytics
* RESTful API architecture

---

## ⚡ Non-Functional Requirements

* Scalable architecture
* Secure authentication (JWT)
* High availability
* Modular design
* Maintainability
* Logging & observability support

---

## 🧪 Testing

Located in `/tests`

* API testing
* Authentication testing
* Carbon logic validation

---

## 🚀 Getting Started

### 1️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 2️⃣ Run Backend

```bash
uvicorn backend.main:app --reload
```

---

### 3️⃣ Run with Docker

```bash
docker-compose up --build
```

---

## 📈 Future Enhancements

* Microservices architecture transition
* Blockchain-based carbon credit system
* AI-based emission prediction
* Real-time analytics dashboard
* Third-party API integrations

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

This project is ideal for:

* Backend engineering practice
* System design learning
* Building production-grade architectures

---
