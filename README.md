# 🧠 Chat-to-SQL POC (Local LLM + PostgreSQL)

This is a local **Proof of Concept (POC)** that lets you **chat with your database** using natural language.  
A locally running **Llama 3 model (via Ollama)** converts your question into SQL, executes it on your **local PostgreSQL** database, and returns tabular results inside a simple chat interface built with **FastAPI + React**.

---

## 🚀 Features
- 🔗 Connects to your **local PostgreSQL** database  
- 💬 Natural-language questions → SQL → query results  
- 🤖 Uses **Llama 3** via **Ollama** (runs fully offline)  
- 🧠 Dynamically inspects DB schema for context-aware SQL generation  
- 🧱 FastAPI backend with lightweight SQL validation  
- 🪶 React (Vite) frontend chat UI  
- 🔒 Basic masking for sensitive columns (`email`, `phone`, `ssn`)

---

## 🧩 Architecture Overview
```
Frontend (Vite + React)
        │
        ▼
 FastAPI Backend ──► Ollama (Llama 3)
        │
        ▼
 PostgreSQL Database
```

---

## ⚙️ Prerequisites
Install locally:
- **Docker & Docker Compose**
- **Python 3.10+**
- **Node 16+ / npm**
- **Ollama** → [https://ollama.com/download](https://ollama.com/download)

Verify:
```bash
docker --version
python --version
node -v
ollama --version
```

---

## 🗂️ Project Structure
```
poc-llm-sql/
├── docker-compose.yml
├── seed.sql
├── backend/
│   ├── app.py
│   ├── db.py
│   ├── llm.py
│   ├── sql_validator.py
│   ├── requirements.txt
│   └── .env
└── frontend/
    └── (Vite React app)
```

---

## 🐘 Step 1 – Database Setup

### 1.1 Create `docker-compose.yml`
```yaml
version: "3.9"
services:
  db:
    image: postgres:16
    container_name: poc_db
    environment:
      POSTGRES_USER: pocuser
      POSTGRES_PASSWORD: pocpass
      POSTGRES_DB: pocdb
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
  adminer:
    image: adminer
    ports:
      - "8080:8080"
volumes:
  pgdata:
```

### 1.2 Start containers
```bash
docker compose up -d
```

### 1.3 Seed sample data
Create `seed.sql`:
```sql
CREATE TABLE IF NOT EXISTS customers (
  id SERIAL PRIMARY KEY,
  name TEXT,
  country TEXT,
  email TEXT
);
CREATE TABLE IF NOT EXISTS orders (
  id SERIAL PRIMARY KEY,
  customer_id INT REFERENCES customers(id),
  order_date DATE,
  amount NUMERIC(10,2)
);
INSERT INTO customers (name,country,email) VALUES
('Alice','Nepal','alice@example.com'),
('Bob','India','bob@example.com'),
('Carol','Nepal','carol@example.com')
ON CONFLICT DO NOTHING;
INSERT INTO orders (customer_id,order_date,amount) VALUES
(1,'2025-10-01',120.50),
(1,'2025-10-02',99.99),
(2,'2025-10-01',200.00),
(3,'2025-10-03',50.00);
```

Run:
```bash
docker exec -i poc_db psql -U pocuser -d pocdb < seed.sql
```

Adminer UI → <http://localhost:8080>

---

## 🤖 Step 2 – LLM Setup (Ollama + Llama 3)
```bash
ollama pull llama3
ollama serve    # if not auto-started
ollama run llama3 "SELECT 1;"
```
Model listens on `http://localhost:11434`.

---

## 🧠 Step 3 – Backend (FastAPI)

### 3.1 Install deps
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt`
```
fastapi
uvicorn[standard]
psycopg2-binary
python-dotenv
sqlparse
requests
pydantic
```

### 3.2 Environment `.env`
```
DB_HOST=localhost
DB_PORT=5432
DB_USER=pocuser
DB_PASS=pocpass
DB_NAME=pocdb
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3
```

### 3.3 Run backend
```bash
uvicorn app:app --reload --port 8000
```

Test:
```bash
curl -X POST http://localhost:8000/chat   -H "Content-Type: application/json"   -d '{"message":"show total order amount per customer"}'
```

---

## 💬 Step 4 – Frontend (Vite + React)
```bash
cd ../frontend
npm install
npm run dev -- --host
```
Open <http://localhost:5173>

You can now chat with your DB.

---

## 🧾 Example Prompts
| User Prompt | Result |
|--------------|---------|
| “Show total order amount per customer.” | `SELECT ... SUM(o.amount) ... GROUP BY ...` |
| “List all customers from Nepal.” | Filtered rows |

---

## 🧱 Safety & Validation
- Only **SELECT** statements allowed  
- Auto-`LIMIT 200`  
- Masks sensitive fields (`email`, `phone`, `ssn`)  
- Simple guardrail via regex + `sqlparse`  

---

## 🧪 Troubleshooting
| Problem | Fix |
|----------|-----|
| Ollama connection refused | Run `ollama serve` |
| DB connection error | Check Postgres container → `docker ps` |
| CORS error | Backend enables CORS for `*` |
| Llama3 returns text not SQL | Confirm `.env` model = `llama3` and strict prompt in `llm.py` |

---

## 🏁 Quick Start
```bash
# 1. Start DB
docker compose up -d
# 2. Seed DB
docker exec -i poc_db psql -U pocuser -d pocdb < seed.sql
# 3. Run Ollama
ollama serve
ollama pull llama3
# 4. Backend
cd backend && source .venv/bin/activate && uvicorn app:app --reload --port 8000
# 5. Frontend
cd ../frontend && npm run dev -- --host
```

Visit  
- **Frontend:** <http://localhost:5173>  
- **Backend Docs:** <http://localhost:8000/docs>  
- **Adminer UI:** <http://localhost:8080>

---

## 🔮 Future Enhancements
- Caching (Re-use query results)  
- Chart generation (Vega-Lite)  
- Auth / RBAC  
- Dockerize everything for 1-click run  
- Better SQL safety (`sqlglot` AST validation)

---

## 📄 License
MIT © 2025 Subhan S. karki
