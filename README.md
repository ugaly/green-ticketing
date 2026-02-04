# Ticket Management System

A small, working **Ticket Management System** with:

- **Customer flow** to create and track tickets
- **Admin flow** to manage/assign/resolve tickets
- **External integration endpoint** to ingest tickets from another system (API key protected)

This is a small but complete prototype with a **clean foundation**, not a production-ready system.

---

## Tech Stack

- **Python 3** + **Django 5.1**
- **Django REST Framework** (JSON-only API responses)
- **SQLite** (default)
- Optional: **Celery + Redis** (pre-wired in settings, not required to run locally)

---

## Quickstart

Clone the repo and enter the project folder:

```bash
git clone https://github.com/ugaly/green-ticketing.git
cd green-ticketing

python3 -m venv .venv
source .venv/bin/activate

pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

cp .env.example .env
python manage.py migrate
python manage.py runserver
```

API will be available at `http://127.0.0.1:8000/`.

---

## Docker

This avoids local Python/pip SSL quirks and gives you a clean “pro” story.

### Build + run

```bash
git clone https://github.com/ugaly/green-ticketing.git
cd green-ticketing
cp .env.example .env

docker compose up --build
```

Open `http://127.0.0.1:8000/`.

### Migrations (Docker)

Migrations are run automatically on container start (dev convenience). If you want to run manually:

```bash
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
```

### Create superuser (Django admin UI)

```bash
docker compose exec web python manage.py createsuperuser
```

Then open `http://127.0.0.1:8000/django-admin/`.

### Celery worker (automatic)

Celery + Redis start automatically with `docker compose up`.

```bash
docker compose ps
```

---

## Day-to-day Django commands (local)

### Make migrations + migrate

```bash
python manage.py makemigrations
python manage.py migrate
```

### Create superuser

```bash
python manage.py createsuperuser
```

### Django Admin UI

The built-in Django admin UI is available at:

- `GET /django-admin/`

It was moved from `/admin/` so we can use the API path `/admin/tickets`.

---

## Role Simulation (No Auth)

Use **either headers** (preferred) or **query params**.

### Headers (preferred)

- `X-ROLE`: `customer` | `admin`
- `X-USER`: email (string identifier)

### Query params

- `?role=customer|admin&user=email`

If missing/invalid, the API returns a clear error.

---

## Environment Variables

See `.env.example`.

- **`EXTERNAL_TICKET_API_KEY`**: shared secret for `POST /external/tickets`
- **`API_PAGE_SIZE`**: default pagination size
- **Celery/Redis (optional)**:
  - `CELERY_TASK_ALWAYS_EAGER` (default `true` so Redis is not required)
  - `CELERY_BROKER_URL` / `CELERY_RESULT_BACKEND` (defaults to `redis://localhost:6379/0`)

### Generating strong keys (recommended)

Generate a good Django secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Generate an external API key (shared secret) for the integration endpoint:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Set them in your `.env`:

- `DJANGO_SECRET_KEY=<output>`
- `EXTERNAL_TICKET_API_KEY=<output>`

---

## Data Model (Minimum)

### Ticket

- `id`
- `source`: `customer|external`
- `external_ref` (required if `source=external`)
- `title` (required)
- `description` (optional)
- `priority`: `low|medium|high`
- `status`: `open|in_progress|resolved|closed`
- `category`: `billing|technical|general`
- `customer_id` (email, optional)
- `assigned_to` (email, optional)
- `created_at`, `updated_at`

### Comment

- `id`
- `ticket_id`
- `author`
- `role`: `customer|admin`
- `message`
- `created_at`

### Category

- `id`
- `name` (unique)

### TicketAttachment

- `id`
- `ticket_id`
- `file` (stored under `media/attachments/...`)
- `created_at`

On startup, a few default categories are **seeded automatically**:
- `"billing"`, `"technical"`, `"general"`

Admins can add/edit/delete categories via Django admin at `/django-admin/tickets/category/`.

---

## API Endpoints

All endpoints speak **JSON**.

### Customer Endpoints

#### Create ticket (JSON)

```bash
curl -s -X POST "http://127.0.0.1:8000/customer/tickets" \
  -H "Content-Type: application/json" \
  -H "X-ROLE: customer" \
  -H "X-USER: alice@example.com" \
  -d '{"title":"Refund not received","description":"Please check","priority":"high","category":"billing"}'
```

#### Create ticket (with file attachments, optional)

```bash
curl -s -X POST "http://127.0.0.1:8000/customer/tickets" \
  -H "X-ROLE: customer" \
  -H "X-USER: alice@example.com" \
  -F "title=Refund not received" \
  -F "description=Please check" \
  -F "priority=high" \
  -F "category=billing" \
  -F "attachments=@/path/to/screenshot1.png" \
  -F "attachments=@/path/to/screenshot2.log"
```

#### List own tickets (paginated)

```bash
curl -s "http://127.0.0.1:8000/customer/tickets" \
  -H "X-ROLE: customer" \
  -H "X-USER: alice@example.com"
```

#### Ticket details (+ comments)

```bash
curl -s "http://127.0.0.1:8000/customer/tickets/1" \
  -H "X-ROLE: customer" \
  -H "X-USER: alice@example.com"
```

#### Add comment

```bash
curl -s -X POST "http://127.0.0.1:8000/customer/tickets/1/comments" \
  -H "Content-Type: application/json" \
  -H "X-ROLE: customer" \
  -H "X-USER: alice@example.com" \
  -d '{"message":"Any update?"}'
```

#### Close ticket (Rule: only if status=resolved)

```bash
curl -s -X POST "http://127.0.0.1:8000/customer/tickets/1/close" \
  -H "X-ROLE: customer" \
  -H "X-USER: alice@example.com"
```

If not resolved, returns **409** with a clear message.

---

### Admin Endpoints

#### List tickets (filters + search + pagination)

Filters:
- `status`, `priority`, `category`, `assigned_to`, `source`
- `q` (search in title/description/external_ref/customer_id/assigned_to)

```bash
curl -s "http://127.0.0.1:8000/admin/tickets?status=open&priority=high&q=refund" \
  -H "X-ROLE: admin" \
  -H "X-USER: admin@example.com"
```

#### Ticket details (+ comments)

```bash
curl -s "http://127.0.0.1:8000/admin/tickets/1" \
  -H "X-ROLE: admin" \
  -H "X-USER: admin@example.com"
```

#### Update ticket (assign / status change / etc.)

```bash
curl -s -X PUT "http://127.0.0.1:8000/admin/tickets/1" \
  -H "Content-Type: application/json" \
  -H "X-ROLE: admin" \
  -H "X-USER: admin@example.com" \
  -d '{"status":"in_progress","assigned_to":"agent1@example.com","priority":"high"}'
```

#### Add admin comment

```bash
curl -s -X POST "http://127.0.0.1:8000/admin/tickets/1/comments" \
  -H "Content-Type: application/json" \
  -H "X-ROLE: admin" \
  -H "X-USER: admin@example.com" \
  -d '{"message":"Investigating internally."}'
```

#### Stats (bonus)

```bash
curl -s "http://127.0.0.1:8000/admin/tickets/stats" \
  -H "X-ROLE: admin" \
  -H "X-USER: admin@example.com"
```

---

### External Ticket Ingestion

Protected by:
- `X-API-KEY: <EXTERNAL_TICKET_API_KEY>`
#### JSON only

```bash
curl -s -X POST "http://127.0.0.1:8000/external/tickets" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: dev-external-api-key" \
  -d '{"external_ref":"EXT-123","title":"Partner system alert","description":"Something broke","priority":"medium"}'
```

#### With file attachments (optional)

```bash
curl -s -X POST "http://127.0.0.1:8000/external/tickets" \
  -H "X-API-KEY: dev-external-api-key" \
  -F "external_ref=EXT-123" \
  -F "title=Partner system alert" \
  -F "description=Something broke" \
  -F "priority=medium" \
  -F "attachments=@/path/to/log.txt" \
  -F "attachments=@/path/to/screenshot.png"
```

Response:
- `ticket_id`, `external_ref`, `status`, `attachments: [absolute_url, ...]`

### Category Endpoint

Public endpoint for frontend dropdowns:

```bash
curl -s "http://127.0.0.1:8000/categories"
```

Response example:

```json
[
  { "id": 1, "name": "billing" },
  { "id": 2, "name": "technical" },
  { "id": 3, "name": "general" }
]
```

---

## Project Structure (clean foundation)

High-level layout of the project:

```text
.
├── Dockerfile
├── docker-compose.yml
├── README.md
├── requirements.txt
├── .env.example
├── ticketing.postman_collection.json
├── manage.py
├── ticketing/                # Django project settings & wiring
│   ├── settings.py           # Django + DRF + env + Celery config
│   ├── urls.py               # Root URL routes -> tickets.urls + django-admin
│   ├── celery.py             # Celery app bootstrap
│   └── __init__.py
└── tickets/                  # Tickets domain app
    ├── models.py             # Ticket + Comment models and validation
    ├── admin.py              # Django admin configuration
    ├── api/                  # DRF serializers + views (customer/admin/external)
    │   ├── serializers.py
    │   ├── customer_views.py
    │   ├── admin_views.py
    │   └── external_views.py
    └── domain/               # Domain layer (business logic + queries)
        ├── actor.py          # Role/user extraction from headers/query
        ├── permissions.py    # Simple role checks
        ├── selectors.py      # Read/query helpers
        └── services.py       # Write/business operations (create/update/close/comment)
```

---

## Tests (bonus)

```bash
python manage.py test
```

Included:
- Customer can only see own tickets
- External ingest requires correct API key

---

## Postman Collection

- A ready-to-use Postman collection is included:
  - `ticketing.postman_collection.json`
- To use it:
  1. Open Postman → **Import**
  2. Select `ticketing.postman_collection.json` from the project root
  3. Adjust variables if needed:
     - `baseUrl` (default `http://127.0.0.1:8000`)
     - `customerEmail` / `adminEmail`
     - `externalApiKey` (matches `EXTERNAL_TICKET_API_KEY` in `.env`)

This gives you preconfigured requests for **Customer**, **Admin**, and **External** flows.

---

## Assumptions / Shortcuts

- No real authentication/authorization (role simulation only)
- SQLite for simplicity
- Basic validation and clean separation of concerns
- JSON-only responses to keep API consistent

---

## What I’d Improve With More Time

- Proper auth (JWT/session), real Users/Agents model
- Separate “internal note” vs “public comment”
- Audit log/timeline events table (status change events, assignment events)
- Webhooks + retries for external integrations
- Rate limiting + idempotency keys for external ingest
- Observability: structured logging, metrics, tracing
- Dockerfile + docker-compose (Django + Redis) for instant setup

