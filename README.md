# 🛡 Insurance Pricing & Order Management System

A Django-based web application for insurance comparison, dynamic pricing, and order management with installment support.

---

## 🚀 Features

- 🔎 Compare insurance companies based on dynamic pricing
- 💰 Pricing engine based on:
  - Vehicle base value
  - Vehicle production year
  - Company-specific coefficients
- 💳 Cash & installment payments
- 📅 Automatic installment schedule generation
- 👤 Custom user authentication (mobile-based)
- 📊 User dashboard with order tracking
- 🧪 Unit tests for pricing and order logic
- 🐳 Dockerized with PostgreSQL

---

## 🏗 Architecture

- Django MTV architecture
- Service Layer pattern:
  - `PricingService`
  - `OrderService`
- Environment-based configuration
- PostgreSQL inside Docker
- SQLite fallback for local development

---

## 🛠 Tech Stack

- Python 3.11+
- Django
- PostgreSQL
- Docker & Docker Compose
- psycopg
- Git

---

## ⚙️ Run Locally (SQLite)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## 🐳 Run with Docker (PostgreSQL)

### 1️⃣ Build & Start

```bash
docker compose up --build
```

### 2️⃣ Run migrations

```bash
docker compose exec web python manage.py migrate
```

### 3️⃣ Create superuser

```bash
docker compose exec web python manage.py createsuperuser
```

Then open:

```
http://localhost:8000
```

---

## 🧪 Run Tests

```bash
python manage.py test core
```

Or inside Docker:

```bash
docker compose exec web python manage.py test core
```

---

## 📂 Project Structure

```
core/
 ├── models.py
 ├── views.py
 ├── services/
 │    ├── pricing_service.py
 │    └── order_service.py
 ├── tests.py
imeno/
 ├── settings.py
docker-compose.yml
Dockerfile
```

---

## 🔐 Environment Variables

Create a `.env` file:

```
DEBUG=1
SECRET_KEY=your-secret-key
POSTGRES_DB=imeno
POSTGRES_USER=imeno
POSTGRES_PASSWORD=your-password
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

---

## 📈 What This Project Demonstrates

- Clean separation of concerns (views vs services)
- Business logic abstraction
- Dockerized deployment
- PostgreSQL configuration
- Testable architecture
- Environment-based settings
- REST-style API endpoints

---

## 📌 Resume Highlights

- Designed and implemented a dynamic insurance pricing engine.
- Refactored business logic into service layer to improve maintainability.
- Dockerized application with PostgreSQL using Docker Compose.
- Implemented unit tests for pricing and installment logic.
- Built custom authentication flow with mobile-based login.
