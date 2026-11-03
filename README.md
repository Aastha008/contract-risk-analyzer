<div align="center">

# ⚖️ Contract Risk Analyzer

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-005571?logo=fastapi)](https://fastapi.tiangolo.com/)
[![CI Status](https://github.com/daily-project-factory/contract-risk-analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/daily-project-factory/contract-risk-analyzer/actions)
[![Code Style: Black](https://img.shields.io/badge/code%25style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

*An automated legal document review service that parses contract files, extracts key legal clauses, and evaluates them against custom compliance rules using Retrieval-Augmented Generation (RAG).*

</div>

---

## 🛑 Problem Statement & Target Audience

### The Problem
Manual vendor contract reviews are notoriously slow, expensive, and error-prone. Legal and procurement teams are consistently bottlenecked by high volumes of incoming agreements (such as Master Services Agreements and Non-Disclosure Agreements), increasing the operational risk of missing non-standard liability caps, overly broad indemnification clauses, or ambiguous termination conditions.

### Target Audience
* **Legal Counsel & Corporate Lawyers:** Accelerate first-pass contract reviews and surface dangerous deviations from corporate playbooks instantly.
* **Procurement & Sourcing Teams:** Rapidly evaluate vendor proposals and risk profiles before escalating to formal legal review.
* **Compliance Officers:** Enforce consistent corporate compliance rules across all third-party contracts.

---

## ⚡ Key Features

* **Multi-Format Ingestion:** Seamlessly ingest PDF and DOCX contracts with advanced clause-level document chunking and structural extraction.
* **RAG-Powered Compliance Checking:** Compare extracted clauses against a configurable corporate rulebook stored in **ChromaDB** using high-dimensional vector embeddings.
* **Strict Structured Outputs:** Generate rigorous, validated JSON risk reports (covering governing law, liability limits, termination notices, and more) enforced via **Pydantic**.
* **High-Performance API:** Serve fast asynchronous analysis endpoints via **FastAPI** providing real-time risk scores and exact flagged clause citations.

---

## 🏗️ Architecture & System Design

The application follows a clean modular monolith architecture separating data ingestion, vector indexing, business logic, and API transport layers.

```
┌────────────────────────────────────────────────────────┐
│                      Client / CLI                      │
└                           ┬                            │
                            │ HTTP Request (PDF/DOCX)    │
                            ▼                            │
┌────────────────────────────────────────────────────────┐
│                 src/main.py & src/api.py               │
│               (FastAPI Routing & Ingestion)            │
└                           ┬                            │
                            │ Structured Contract Payload│
                            ▼                            │
┌────────────────────────────────────────────────────────┐
│                      src/core.py                       │
│        (PyPDF/DOCX Parsing, Chunking & LLM Engine)     │
└               ┬                                  ▲     │
                │ Query Vector Match               │     │ Context & Rules
                ▼                                  │     │
┌──────────────────────────────────┐               │     │
│           ChromaDB               ├───────────────┘     │
│   (Corporate Rulebook Embeddings)│                     │
└──────────────────────────────────┘                     │
                            │ Validated Pydantic Schema  │
                            ▼                            │
┌────────────────────────────────────────────────────────┐
│                     src/models.py                      │
│                (Pydantic Domain Models)                │
└────────────────────────────────────────────────────────┘
```

### Core Modules

| Module Path | Purpose |
| :--- | :--- |
| `src/models.py` | Pydantic domain schemas and request/response models for contract analysis and rulebooks. |
| `src/core.py` | Core processing engine for parsing PDF/DOCX, chunking clauses, querying ChromaDB, and LLM risk evaluation. |
| `src/api.py` | FastAPI HTTP routes, file upload handling, and analysis endpoints. |
| `src/main.py` | Uvicorn server entrypoint and application setup. |

---

## 💻 Technology Stack

* **Language:** Python 3.10+
* **Web Framework:** FastAPI & Uvicorn
* **Data Validation:** Pydantic v2
* **Vector Database:** ChromaDB
* **Orchestration & LLM:** LangChain & OpenAI API
* **Document Parsers:** PyPDF, python-docx
* **Testing:** Pytest

---

## 🚀 Installation & Virtual Environment Setup

Clone the repository and set up your isolated Python virtual environment:

```bash
# Clone the repository
git clone https://github.com/daily-project-factory/contract-risk-analyzer.git
cd contract-risk-analyzer

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🔑 Environment Variables Configuration

Copy the example environment file and configure your API keys and parameters:

```bash
cp .env.example .env
```

Edit `.env` and supply your specific keys:

```env
OPENAI_API_KEY=sk-proj-your-openai-api-key-here
CHROMA_PERSIST_DIRECTORY=./chroma_db
LOG_LEVEL=INFO
```

---

## 🔌 Usage

### Running the API Server

Start the development server using Uvicorn via `src/main.py`:

```bash
python src/main.py
```

The interactive API documentation will be available at:
* **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

### API Endpoints

#### `POST /api/v1/analyze`
Upload a contract (`.pdf` or `.docx`) for automated risk assessment.

* **Request:** `multipart/form-data` with file field `file`.
* **Response Example:**
```json
{
  "contract_name": "Vendor_Agreement_v2.pdf",
  "overall_risk_score": 78.5,
  "flagged_clauses": [
    {
      "clause_type": "Liability Limitation",
      "severity": "HIGH",
      "extracted_text": "Vendor liability shall be unlimited under all circumstances.",
      "rulebook_reference": "Standard liability must be capped at 12x annual fees.",
      "recommendation": "Negotiate a liability cap aligned with total contract value."
    }
  ],
  "summary": "Contract presents substantial exposure regarding liability and indemnification terms."
}
```

---

## 🧪 Automated Testing

Run the test suite using `pytest` to ensure all core parsers, API routes, and analysis loops are functioning correctly:

```bash
# Run all tests with verbose output
pytest -v

# Run specific test modules
pytest tests/test_core.py
pytest tests/test_api.py
```

---

## 🗂️ Project Structure Tree

```text
contract-risk-analyzer/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── api.py
│   ├── core.py
│   ├── main.py
│   └── models.py
└── tests/
    ├── __init__.py
    ├── test_api.py
    └── test_core.py
```

---

## 🗺️ Roadmap & Future Enhancements

- [ ] **Multi-Model Support:** Integrate local open-source LLMs via Ollama / HuggingFace pipelines for on-premise deployments.
- [ ] **Advanced Rulebook UI:** Build a frontend dashboard to manage custom corporate policies and risk tolerance thresholds without modifying JSON files.
- [ ] **Redlining Suggestions:** Automatically generate clause rewrites and negotiation talking points for flagged terms.
- [ ] **Audit Trail & Webhooks:** Add event hooks for Slack and Microsoft Teams alerting when high-risk agreements are processed.

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---
<div align="center">
Built with precision by the Engineering Team at Daily Project Factory.
</div>