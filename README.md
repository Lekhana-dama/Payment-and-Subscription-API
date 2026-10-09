# PaymentAPI — Payment & Subscription Management API

A RESTful backend API built with **FastAPI, PostgreSQL, SQLAlchemy, and Alembic** to manage users, subscription plans, subscriptions, payments, and invoices.

## Features

* **Authentication & Authorization** — JWT-based authentication and protected endpoints.
* **Plan Management** — Create and retrieve subscription plans.
* **Subscription Management** — Manage user subscriptions and their lifecycle.
* **Payment Processing** — Payment service with pending payment records and idempotency support.
* **Payment Provider Abstraction** — Separate payment-provider logic from business logic.
* **Webhook Architecture** — Support for payment-provider event handling.
* **Database Management** — PostgreSQL with asynchronous SQLAlchemy.
* **Database Migrations** — Schema versioning with Alembic.
* **API Security** — CORS configuration, rate limiting, and protected routes.
* **Health Checks** — Endpoints for checking application health.
* **Automated Testing** — Pytest-based test suite.

## Tech Stack

| Technology | Purpose                                 |
| ---------- | --------------------------------------- |
| Python     | Programming language                    |
| FastAPI    | REST API framework                      |
| PostgreSQL | Relational database                     |
| SQLAlchemy | ORM and asynchronous database access    |
| Alembic    | Database migrations                     |
| Pydantic   | Request validation and response schemas |
| JWT        | Authentication                          |
| Pytest     | Automated testing                       |

## Project Structure

```text
PaymentAPI/
├── alembic/
├── app/
│   ├── models/
│   ├── repositories/
│   ├── routers/
│   ├── schemes/
│   ├── services/
│   ├── payment_providers/
│   └── main.py
├── tests/
├── uploads/
├── alembic.ini
├── requirements.txt
└── README.md
```

## Prerequisites

* Python 3.11 or later
* PostgreSQL
* Git

Use the Python version supported by your installed dependencies.

## Local Installation

### 1. Clone the repository

```bash
git clone https://github.com/Lekhana-dama/Payment-and-Subscription-API.git
cd Payment-and-Subscription-API
```

### 2. Create a virtual environment

**Windows PowerShell:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root. Use the variable names expected by your application's configuration.

Example:

```env
DATABASE_URL=postgresql+asyncpg://YOUR_USER:YOUR_PASSWORD@localhost:5433/Payment_API
SECRET_KEY=replace-with-a-long-random-secret
```

Update the database username, password, port, and database name to match your local PostgreSQL configuration.

**Security:** Never commit `.env` files, database credentials, production secrets, or real payment-provider keys to GitHub.

### 5. Apply database migrations

Make sure PostgreSQL is running and the database exists, then execute:

```bash
alembic upgrade head
```

### 6. Start the API

```bash
python -m uvicorn app.main:app --reload
```

The local API should be available at:

* API base URL: http://127.0.0.1:8000
* Interactive Swagger documentation: http://127.0.0.1:8000/docs
* ReDoc documentation: http://127.0.0.1:8000/redoc
* OpenAPI schema: http://127.0.0.1:8000/openapi.json

These URLs apply when running locally with Uvicorn's default host and port.

## API Modules

The application is organized around the following resources. Exact paths and HTTP methods are defined by the registered routers and OpenAPI documentation.

| Module            | Responsibility                                     |
| ----------------- | -------------------------------------------------- |
| Authentication    | Registration, login, and authenticated-user access |
| Plans             | Subscription plan management                       |
| Subscriptions     | User subscription lifecycle                        |
| Payments          | Payment creation and payment status                |
| Invoices          | Invoice management                                 |
| Payment Providers | Provider-specific payment operations               |

Open `/docs` to inspect the available endpoints, request schemas, authentication requirements, and response formats.

## Running Tests

Activate the virtual environment and run:

```bash
pytest -q
```

**Latest recorded test result:** `5 passed, 23 warnings`.

The warnings included deprecations from Pydantic configuration, datetime handling, and the Starlette test client. This result reflects the last recorded test run, not a guarantee about future changes.

## Database Migrations

Apply pending migrations:

```bash
alembic upgrade head
```

View migration history:

```bash
alembic history
```

Check whether model changes require a new migration:

```bash
alembic check
```

If you change database models, review the generated migration before applying it.

## Security Considerations

* Use a strong, randomly generated secret key.
* Keep credentials in environment variables.
* Validate authentication and authorization on protected routes.
* Verify webhook signatures before trusting payment events.
* Make payment processing idempotent to reduce duplicate processing.
* Validate payment ownership and allowed status transitions.
* Never treat a client-provided payment status as proof of successful payment.
* Use HTTPS and production-grade secrets when deploying.
* Configure CORS origins and rate limits appropriately for the environment.

## Current Scope

This project is a backend learning and portfolio project demonstrating API development, database management, authentication, and payment-system architecture.

The demo payment provider is intended for development and testing. It is not a real payment processor. Production payment processing requires integration with a supported provider, verification of signed webhooks, and appropriate reconciliation and error-handling mechanisms.

## Future Improvements

* Complete and test payment-provider integration.
* Expand webhook security and duplicate-event tests.
* Add more integration and edge-case tests.
* Improve logging and monitoring.
* Configure production hosting and managed PostgreSQL.
* Add API usage examples and architecture documentation.

## Author

**Lekhana Dama**

GitHub: https://github.com/Lekhana-dama

## License

Add a license file if you intend to distribute this project under an open-source license.
