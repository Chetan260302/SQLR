# SQL RAG Chatbot (Multi-Agent Architecture)

A **SQL Retrieval-Augmented Generation (RAG)** chatbot that answers natural language questions over relational databases using **LLMs + structured query execution**.

This project focuses on **schema-aware SQL generation**, **multi-agent orchestration**, and **secure execution** without exposing raw database data to LLMs.

---

## Features

- Natural language → SQL → Answer pipeline  
- Multi-agent workflow:
  - **Schema Agent** – extracts only relevant tables & columns
  - **SQL Agent** – generates dialect-aware SQL
  - **Execution Agent** – runs SQL safely (no LLM)
  - **Response Agent** – formats results into human-readable insights
- Supports multiple databases & SQL dialects
- Token-efficient (no full schema / full rows sent to LLM)
- Streaming chat UI
- Authentication (Login / Signup)
- Secure password hashing

---

## 🏗 Tech Stack

**Backend**
- FastAPI
- LangChain
- Ollama (local LLMs) / Gemini API
- SQLAlchemy
- PostgreSQL / MySQL / SQLite/SQL SERVER (dialect-agnostic)

**Frontend**
- React
- Tailwind CSS
- Streaming responses

---

##  Setup Instructions

### 1️ Clone the repo
```bash
git clone https://github.com/your-username/sql-rag-chatbot.git
cd sql-rag-chatbot
```

### 2 Backend SEtup
```bash
cd backend
python -m venv venv
# MAC source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### .env (create this inside backend folder)
```bash
GOOGLE_API_KEY="your api google api key" #optional if you will use local LLM
JWT_SECRET="your secret" # Generates quick random hex string (openssl rand -hex 32)
DB_SECRET_KEY="your secret" # run this in cmd to get your key [python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"]
```

### Run Backend
``bash
uvicorn main:app --reload

### Frontend Setup
``bash
cd frontend
npm install
npm run dev
```

### Future Improvements
- Vector DB fallback (when SQL fails)
- Query explanation & optimization hints
- Role-based DB access
- Visualization support (charts)
