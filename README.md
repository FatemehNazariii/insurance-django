# Insurance Management System

A Django-based web application for insurance comparison, pricing, and order management.

## Features
- Dynamic insurance pricing engine
- Installment-based payment system
- Mobile-based authentication
- Admin panel for managing companies and rates
- Service-layer refactoring for business logic
- Unit tests implemented

## Tech Stack
- Django
- SQLite / PostgreSQL
- Docker
- HTML / Tailwind

## Run Locally

```bash
python -m venv .venv
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
