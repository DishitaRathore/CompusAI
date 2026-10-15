# CampusFlow AI

CampusFlow AI is a secure education ERP assistant inspired by common university ERP workflows.

It combines structured student data, cybersecurity incident reporting, document retrieval, and a local language model.

The project uses fictional data and does not contain real university records.

## Features

- Attendance lookup
- Fee-status lookup
- Student support-ticket creation
- Cybersecurity incident reporting
- Security-event tracking
- Audit logging
- Conversation history
- Role-based API access
- FAISS-based semantic search
- RAG-based policy answers
- Local FLAN-T5 answer generation
- Student chatbot UI
- Admin security dashboard
- Automated API smoke tests

## Technology Stack

- Python
- FastAPI
- MySQL
- SQLAlchemy
- PyMySQL
- Sentence Transformers
- FAISS
- Hugging Face Transformers
- FLAN-T5
- HTML, CSS, and JavaScript

## Architecture

```text
Student UI
    |
    v
FastAPI API
    |
    +--> MySQL
    |      +--> Students
    |      +--> Attendance
    |      +--> Fees
    |      +--> Tickets
    |      +--> Chat messages
    |      +--> Audit logs
    |      +--> Security events
    |
    +--> FAISS
           |
           +--> Education policies
           +--> Cybersecurity guidelines
           +--> Privacy documents
                    |
                    v
              Local FLAN-T5 model


How RAG Works
1. Policy documents are stored in the knowledge_base folder.
2. Sentence Transformers convert documents into embeddings.
3. FAISS stores the embeddings.
4. A user question is also converted into an embedding.
5. FAISS retrieves the most relevant document.
6. FLAN-T5 generates an answer using the retrieved context.


resume_chatbot/
|
|-- main.py
|-- chatbot.py
|-- database.py
|-- models.py
|-- schemas.py
|-- auth.py
|-- tools.py
|-- rag.py
|-- llm.py
|-- seed_data.py
|-- init_db.py
|-- smoke_test.py
|-- requirements.txt
|-- .env
|-- knowledge_base/
|-- frontend/
|   |-- index.html
|   |-- admin.html
|-- knowledge.index
|-- knowledge_metadata.json

## Machine Learning Intent Classifier

CampusFlow AI includes a fine-tuned DistilBERT classifier that routes user questions to the correct system workflow.

Supported intents:

- `attendance_query`
- `fee_query`
- `create_ticket`
- `security_report`
- `security_guidance`
- `policy_question`
- `chat_history`
- `unknown`

The classifier routes requests to:

```text
User question
    |
    v
DistilBERT intent classifier
    |
    +--> MySQL database tools
    +--> Support-ticket workflow
    +--> Security-event workflow
    +--> RAG and local language model
    +--> Safe fallback