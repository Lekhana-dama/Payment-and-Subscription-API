# PayPilot — React frontend for PaymentAPI

A React + Vite dashboard that connects to the existing FastAPI Payment & Subscription API.

## Requirements
- Node.js 18+ (Node 20 LTS recommended)
- Your FastAPI backend running locally

## Run it

1. Extract this folder.
2. In a terminal, open the extracted `paymentapi-frontend` directory.
3. Install packages:

   ```bash
   npm install
   ```

4. Create a `.env` file in this directory with:

   ```env
   VITE_API_BASE_URL=http://127.0.0.1:8000
   ```

   `.env.example` already contains this default. Copy it to `.env` if desired.

5. Start the frontend:

   ```bash
   npm run dev
   ```

6. Open the URL Vite prints (usually `http://localhost:5173`).

## FastAPI CORS setup

In `app/main.py`, add:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Place the middleware after `app = FastAPI(...)` and before/around router registration. Restart Uvicorn after editing.

## API routes used

- `GET /` — backend connectivity check
- `GET /plans` — list plans
- `POST /auth/register` — create user
- `POST /auth/login` — OAuth2 form login (frontend sends `application/x-www-form-urlencoded`; email is sent as the `username` field)
- `POST /subscriptions` — create subscription
- `GET /subscriptions/{subscription_id}` — retrieve a subscription
- `POST /payments` — create payment with subscription ID and idempotency key
- `PATCH /payments/{payment_id}/success` — mark demo payment successful
- `PATCH /payments/{payment_id}/failed` — mark demo payment failed
- `GET /payments/` — payment history
- `POST /invoices/` — create invoice using payment ID
- `GET /invoices/{invoice_id}` — retrieve invoice

## Important schema note

The frontend was built against the router files provided for the capstone. It assumes:
- Registration accepts `username`, `email`, and `password`.
- `SubscriptionCreate` accepts `{ "plan_id": number }`.
- Plan responses expose `id`, `name`, `description`, `price`, `billing_interval`, and optionally `is_active`.
- Payment responses expose common fields such as `id`, `subscription_id`, `amount`, `status`, and `provider`.

The login request shape is confirmed from the router: it uses `OAuth2PasswordRequestForm`, which requires form-encoded credentials. If your Pydantic schemas use different fields, adjust the indicated request bodies in `src/App.jsx`.

## Security note

This starter stores the JWT in `sessionStorage` for this local demo frontend and clears it when the browser tab/session ends. For a production deployment, consider an HttpOnly Secure cookie/BFF approach, CSRF protections where applicable, HTTPS, and exact production CORS origins. The payment buttons call your demo success/failure endpoints; they do not process real money.
