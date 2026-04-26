# VeloxShip — Logistics Delivery Bill Management

A logistics bill management system for Vietnamese shipping companies. Built with FastAPI (Python) and React (Vite).

## Prerequisites (Linux)

- **Python**: 3.11+
- **Node.js**: 20 LTS
- **PostgreSQL**: 16+

---

## Local Environment Setup Guide (Linux)

### 1. Database Setup (PostgreSQL)

You need to create a PostgreSQL database and configure the connection credentials. You must also enable specific extensions for Vietnamese unaccented search.

Install PostgreSQL (if you haven't already on Ubuntu/Debian):
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

Create a new database and user (or use the default `postgres` user). Here is how to set the password for the `postgres` user, create the database `veloxship`, and enable the required extensions:

```bash
# Create a new user called 'velox_user' with password 'admin'
sudo -u postgres psql -c "CREATE USER velox_user WITH PASSWORD 'admin';"

# Create the database and assign ownership to the new user
sudo -u postgres createdb -O velox_user veloxship

# Connect to the database as superuser to create extensions
sudo -u postgres psql -d veloxship -c "CREATE EXTENSION IF NOT EXISTS unaccent;"
sudo -u postgres psql -d veloxship -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
```

### 2. Backend Setup

The backend is built with FastAPI and uses SQLAlchemy with asyncpg.

```bash
# Navigate to the backend directory
cd backend

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Configure environment variables
cp .env.example .env
```

**Configure `.env`:**
Edit the `.env` file you just created and update the `DATABASE_URL` with the password you set in step 1. Also, set a secure random string for `JWT_SECRET`.

```env
DATABASE_URL=postgresql+asyncpg://velox_user:admin@localhost:5432/veloxship
JWT_SECRET=your_random_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_TTL_MINUTES=15
REFRESH_TOKEN_TTL_DAYS=7
TRACKING_NUMBER_PREFIX=NL
CARRIER_NAME=Vận Chuyển HN
CARRIER_HOTLINE=0972 160 610
CARRIER_WEBSITE=newlinks.vn
CARRIER_EMAIL=info@newlinks.vn
```

**How to generate secure keys:**
- For `JWT_SECRET`, run:
  ```bash
  openssl rand -hex 32
  ```

**Run Database Migrations and Seed Data:**
Initialize your database schema and seed the initial service catalog and admin user:
```bash
alembic upgrade head
python -m app.scripts.seed
```

**Start the Backend Server:**
```bash
uvicorn app.main:app --reload --port 8000
```
The API will be available at `http://localhost:8000`, and the interactive API documentation at `http://localhost:8000/docs`.

### 3. Frontend Setup

The frontend is a React application powered by Vite.

Open a new terminal window:
```bash
# Navigate to the frontend directory
cd backend/../frontend # or just cd ../frontend from the backend dir

# Configure environment variables
cp .env.example .env

# Install dependencies
npm install

# Start the development server
npm run dev
```
The frontend will be available at `http://localhost:5173`.

---

## Key Workflows

### Create a Delivery Bill
1. Open http://localhost:5173. The interface is in Vietnamese.
2. Log in using the default seeded admin credentials:
   - **Username**: `admin`
   - **Password**: `admin123`
3. Click **Tạo phiếu gửi** (Create Bill).
4. Fill in the Sender, Receiver, and Content details.
5. Select the Service Tier and enter the calculated fees.
6. Click **Lưu & In phiếu** (Save & Print). The system generates a tracking number and opens the print preview.

### Manage Bills
1. Go back to the main list. You can search for the recipient name without diacritics.
2. Open a bill detail view to update its status (e.g., to "Đã lấy hàng", "Đang vận chuyển", "Đã giao").
3. View the audit log and reprint the bill at any time.

---

## Testing

To run the test suites for both backend and frontend:

**Backend:**
```bash
cd backend
source .venv/bin/activate
pytest                 # runs unit + integration (testcontainers spins up Postgres)
pytest tests/contract  # OpenAPI contract drift check
```

**Frontend:**
```bash
cd frontend
npm test               # vitest + Testing Library
npm run test:e2e       # Playwright smoke (login → create → preview)
```
