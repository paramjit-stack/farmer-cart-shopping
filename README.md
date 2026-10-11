# FarmFresh — Farmer Products Shopping Cart

Full-stack assessment built with React (Vite), FastAPI, SQLAlchemy and MySQL. Two portals: admin product management and customer shopping.

## Requirements
- Python 3.11+ and Node.js 18+
- MySQL 8+

## Database setup
1. Open MySQL Workbench and run `CREATE DATABASE IF NOT EXISTS farmer_shopping_cart;`.
2. Execute `backend/database.sql` **once on a new empty database**. The script creates six related tables. If you already created these tables, do not rerun it.

## Backend setup (PowerShell)
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```
Edit `backend/.env` with your own local MySQL password. Generate a JWT secret with `python -c "import secrets; print(secrets.token_hex(32))"` and put it in `JWT_SECRET_KEY`. Never commit `.env`.

Create the first admin (one-time setup):
```powershell
python seed_admin.py
```
Provide a valid admin email and password (at least 8 characters).

Start the API:
```powershell
python -m uvicorn app.main:app --reload
```
Swagger: http://127.0.0.1:8000/docs ; database check: http://127.0.0.1:8000/health

## Frontend setup (second terminal)
```powershell
cd frontend
npm install
npm run dev
```
Open http://127.0.0.1:5173 . Optionally copy `frontend/.env.example` to `frontend/.env` to change the API URL.

## Demo walkthrough
1. Log in with the seeded admin credentials. Add a product with name, category, farmer, description, price, stock, image URL and status. Edit it, change stock and deactivate/reactivate it.
2. Log out and register a customer. Browse active products, search by name, filter by category and open a product detail.
3. Add an in-stock quantity to the cart; change or remove items; verify the total.
4. Checkout and open Orders. Confirm that stock was reduced in the admin portal.
5. Try an excessive quantity, negative stock or an inactive product to demonstrate validation.

## API overview
- `POST /api/auth/login`, `POST /api/auth/register`, `GET /api/auth/me`
- `GET /api/products`, `GET /api/products/{id}` (active products only)
- `GET /api/admin/products`, `POST /api/admin/products`, `PUT /api/admin/products/{id}`, `DELETE /api/admin/products/{id}`, `PATCH /api/admin/products/{id}/status`, `PATCH /api/admin/products/{id}/stock`
- `GET /api/cart`, `POST /api/cart/items`, `PUT /api/cart/items/{id}`, `DELETE /api/cart/items/{id}`
- `POST /api/orders/checkout`, `GET /api/orders`

## Design decisions and assumptions
- Product images use URLs, as permitted by the assessment. No payment gateway is required: checkout means placing an order.
- A customer creates a simple account to persist their cart and order history; the initial admin is seeded locally rather than exposed via public admin registration.
- JWT bearer tokens expire after 60 minutes. Admin endpoints check the user role on the server.
- MySQL `DECIMAL` and Python `Decimal` are used for money. Pydantic and database constraints prevent negative prices/stock and invalid quantities.
- Checkout uses one database transaction and `SELECT ... FOR UPDATE` locks on product rows. Stock is checked again at checkout; if any line fails, the entire transaction rolls back.
- Order items store product name and purchase price snapshots. Deleting a product removes pending cart references; historical order items retain their snapshots.
- Frontend stores its access token in localStorage for this time-boxed assessment. A production application would evaluate HttpOnly cookies, CSRF protections, rate limiting and further test coverage.

## Repository hygiene
`.gitignore` excludes `venv/`, `node_modules/`, `.env`, caches and build outputs. Commit `.env.example`, `database.sql`, and this README, but never local passwords or JWT secrets.
