## Education Bot Showcase

Sanitized showcase copy of a client MVP built with FastAPI, PostgreSQL, and a Telegram bot interface.

This repository keeps the application code, migrations, and tests, while removing private repository history and real deployment credentials.

### Features

- Telegram bot flows for registration and authentication
- User profile management
- Content library and offerings catalog
- Perks and external links
- JWT-based API authorization
- FastAPI + SQLAlchemy + Alembic backend

### Stack

- Python
- FastAPI
- Aiogram
- SQLAlchemy async
- PostgreSQL
- Alembic
- Docker Compose

### Quick Start

```bash
cp .env.example .env
docker compose up -d
```

Then open a second terminal and run:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Notes

- This is a showcase version of a private client MVP.
- Secrets and environment-specific values were replaced with safe local placeholders.
- This copy intentionally uses neutral wording instead of client branding.
