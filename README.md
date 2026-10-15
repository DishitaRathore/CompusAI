# CampusFlow AI

CampusFlow AI is an AI-powered student support and cybersecurity assistant built for educational institutions.

It helps students access attendance and fee information, ask policy questions, create support tickets, report cybersecurity incidents, and view chat history.

The application combines a FastAPI backend, MySQL database, Streamlit interface, RAG pipeline, FAISS vector search, a local FLAN-T5 model, and a fine-tuned DistilBERT intent classifier.

## Features

- Attendance queries
- Fee-status queries
- Support-ticket creation
- Phishing and cybersecurity reporting
- Cybersecurity guidance
- College-policy questions
- Chat-history retrieval
- Student and administrator authentication
- MySQL database integration
- Retrieval-Augmented Generation using FAISS
- Local FLAN-T5 response generation
- Fine-tuned DistilBERT intent classification
- Audit logging
- Security-event logging
- PII and secret masking
- Prompt-injection protection
- API rate limiting
- Safe fallback responses
- Streamlit user interface

## System Architecture

```mermaid
flowchart TD
    UI["Streamlit User Interface"] --> API["FastAPI Backend"]

    API --> AUTH["Authentication and Authorization"]
    API --> ROUTER["Chatbot Router"]

    ROUTER --> DBTOOLS["MySQL Database Tools"]
    ROUTER --> TICKET["Support Ticket Workflow"]
    ROUTER --> SECURITY["Security Event Workflow"]
    ROUTER --> HISTORY["Chat History Workflow"]
    ROUTER --> RAG["RAG Pipeline"]
    ROUTER --> FALLBACK["Safe Fallback"]

    DBTOOLS --> MYSQL["MySQL Database"]
    RAG --> FAISS["FAISS Vector Index"]
    RAG --> LLM["Local FLAN-T5 Model"]
```

## Technology Stack

| Component | Technology |
|---|---|
| User interface | Streamlit |
| Backend API | FastAPI |
| Database | MySQL |
| ORM | SQLAlchemy |
| Intent classifier | Fine-tuned DistilBERT |
| Embedding model | Sentence Transformers |
| Vector search | FAISS |
| Language model | Local FLAN-T5 |
| Authentication | API-key authentication |
| Testing | Python smoke tests and evaluation scripts |

## RAG Pipeline

The RAG system uses educational policies, cybersecurity guidelines, and privacy documents stored in the `knowledge_base/` directory.

```mermaid
flowchart LR
    DOCS["Knowledge-base documents"] --> EMB["Sentence Transformer embeddings"]
    EMB --> INDEX["FAISS vector index"]

    QUESTION["User question"] --> QEMB["Question embedding"]
    QEMB --> INDEX

    INDEX --> CONTEXT["Retrieved context"]
    CONTEXT --> LLM["Local FLAN-T5 model"]
    LLM --> ANSWER["Context-aware answer"]
```

The RAG process works as follows:

1. Policy and cybersecurity documents are stored in `knowledge_base/`.
2. Sentence Transformers convert the documents into embeddings.
3. FAISS stores the embeddings.
4. The user's question is converted into an embedding.
5. FAISS retrieves the most relevant context.
6. The local FLAN-T5 model generates an answer using the retrieved context.

## Machine Learning Intent Classifier

CampusFlow AI uses a fine-tuned DistilBERT classifier to identify the intent of each user message.

```mermaid
flowchart TD
    QUESTION["User question"] --> CLASSIFIER["DistilBERT intent classifier"]

    CLASSIFIER --> ATTENDANCE["Attendance workflow"]
    CLASSIFIER --> FEES["Fee workflow"]
    CLASSIFIER --> TICKET["Support-ticket workflow"]
    CLASSIFIER --> SECURITY["Security workflow"]
    CLASSIFIER --> POLICY["RAG policy workflow"]
    CLASSIFIER --> HISTORY["Chat-history workflow"]
    CLASSIFIER --> UNKNOWN["Safe fallback"]
```

### Supported intents

| Intent | Description |
|---|---|
| `attendance_query` | Attendance-related questions |
| `fee_query` | Fee and payment questions |
| `create_ticket` | Support-ticket requests |
| `security_report` | Phishing or security reports |
| `security_guidance` | Cybersecurity advice |
| `policy_question` | College-policy questions |
| `chat_history` | Previous-message requests |
| `unknown` | Unknown or low-confidence requests |

The classifier was evaluated on a project-specific test set with an accuracy of approximately 94%.

## Database Design

CampusFlow AI uses MySQL and SQLAlchemy for persistent data storage.

The database stores:

- Student records
- Attendance records
- Fee records
- Support tickets
- Chat messages
- Audit logs
- Security events

```mermaid
erDiagram
    STUDENT ||--o{ ATTENDANCE : has
    STUDENT ||--o{ FEE : has
    STUDENT ||--o{ TICKET : creates
    STUDENT ||--o{ CHAT_MESSAGE : sends
    STUDENT ||--o{ AUDIT_LOG : generates
    STUDENT ||--o{ SECURITY_EVENT : reports

    STUDENT {
        int id
        string name
        string email
        string department
    }

    ATTENDANCE {
        int id
        int student_id
        float percentage
    }

    FEE {
        int id
        int student_id
        float total_amount
        float paid_amount
        float remaining_amount
    }

    TICKET {
        int id
        int student_id
        string title
        string description
        string status
    }

    CHAT_MESSAGE {
        int id
        int student_id
        string role
        string content
    }

    AUDIT_LOG {
        int id
        int student_id
        string action
        string message
    }

    SECURITY_EVENT {
        int id
        int student_id
        string event_type
        string severity
        string status
    }
```

## Project Structure

```text
CompusAI/
├── main.py
├── chatbot.py
├── intent_classifier.py
├── train_intent_classifier.py
├── evaluate_intent_classifier.py
├── database.py
├── models.py
├── schemas.py
├── auth.py
├── tools.py
├── rag.py
├── llm.py
├── streamlit_app.py
├── requirements.txt
├── .env.example
├── .gitignore
│
├── data/
│   ├── intent_data.csv
│   └── raw/
│       ├── attendance.csv
│       ├── fees.csv
│       └── students.csv
│
├── knowledge_base/
│   ├── attendance_policy.txt
│   ├── fee_policy.txt
│   ├── cybersecurity_basics.txt
│   ├── cybersecurity_guidelines.txt
│   └── student_data_protection.txt
│
├── classifier_smoke_test.py
├── security_smoke_test.py
├── prompt_injection_smoke_test.py
├── pii_masking_smoke_test.py
├── rate_limit_smoke_test.py
├── smoke_test.py
├── test_intent_classifier.py
├── test_rag.py
└── test_sensitive_data_masking.py
```

Generated local artifacts such as `.env`, `.venv/`, `models/`, and `knowledge.index` are excluded from Git.

## Installation

Clone the repository:

```bash
git clone https://github.com/DishitaRathore/CompusAI.git
cd CompusAI
```

Create and activate the virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Create the environment file:

```bash
cp .env.example .env
```

Update `.env` with the local MySQL connection string and API keys.

Never commit the real `.env` file.

## Environment Variables

Example `.env` configuration:

```env
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/campusflow

APP_API_KEY=student-1001-demo-key
ADMIN_API_KEY=admin-demo-key

STUDENT_API_KEYS_JSON={"1002":"student-1002-demo-key"}
```

Use placeholder values in `.env.example`.

Use real values only in `.env`.

## Database Setup

Initialize the database tables:

```bash
python init_db.py
```

Load demo data:

```bash
python seed_data.py
```

## Train the Intent Classifier

Train the classifier:

```bash
python train_intent_classifier.py
```

Evaluate the classifier:

```bash
python evaluate_intent_classifier.py
```

The trained model is saved locally in:

```text
models/intent_classifier/
```

The trained model directory is excluded from Git because it contains large generated files.

## Run the Application

Start the FastAPI backend in Terminal 1:

```bash
python -m uvicorn main:app --reload
```

Start the Streamlit frontend in Terminal 2:

```bash
streamlit run streamlit_app.py
```

Open the Streamlit application:

```text
http://localhost:8501
```

FastAPI Swagger documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/chat` | Send a student message |
| `GET` | `/chat-history/{student_id}` | Retrieve chat history |
| `GET` | `/security-events` | View security events |
| `GET` | `/audit-logs` | View audit logs |
| `GET` | `/docs` | Open FastAPI Swagger documentation |

Student endpoints require a valid student API key.

Administrator endpoints require the administrator API key.

## Security Controls

CampusFlow AI includes the following security controls:

- API-key authentication
- Student-level authorization
- Administrator-only endpoints
- PII masking
- Secret-value masking
- Audit logging
- Security-event logging
- Prompt-injection protection
- Rate limiting
- Safe fallback responses
- Environment-based secret management

## Testing

Compile the main files:

```bash
python -m py_compile \
main.py \
chatbot.py \
auth.py \
tools.py \
intent_classifier.py \
streamlit_app.py
```

Run the classifier routing test:

```bash
python classifier_smoke_test.py
```

Run authorization tests:

```bash
python security_smoke_test.py
```

Run prompt-injection tests:

```bash
python prompt_injection_smoke_test.py
```

Run PII-masking tests:

```bash
python test_sensitive_data_masking.py
python pii_masking_smoke_test.py
```

Run the rate-limit test last:

```bash
python rate_limit_smoke_test.py
```

The rate-limit test intentionally sends multiple requests.

## Security and Privacy Notes

- Never commit `.env`.
- Never upload real API keys.
- Never upload real database passwords.
- Do not commit generated model files.
- Do not commit private student data.
- The included data is fictional demo data.
- Production deployments should use a shared rate-limiting system such as Redis.
- Production deployments should use HTTPS.

## Current Limitations

- The rate limiter is currently in-memory and resets when the application restarts.
- The intent classifier was trained on a small project-specific dataset.
- The trained model must be generated locally or stored separately.
- The FAISS index must be generated from the knowledge-base documents.
