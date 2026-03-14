# Senior Mortgage Underwriting System

An **Agentic AI Multi-Agent Workflow** that automates mortgage underwriting using specialized AI agents, coordinated via LangGraph, with RAG-based policy compliance and human-in-the-loop review.

## Architecture

```
                        ┌─────────────┐
                        │  Initialize  │
                        └──────┬──────┘
                               ▼
                        ┌─────────────┐
                   ┌───>│  Supervisor  │<───┐
                   │    └──────┬──────┘    │
                   │           │           │
          ┌────────┴───┐  ┌───┴────┐  ┌───┴────────┐
          │   Credit    │  │ Income │  │   Asset     │
          │  Analyst    │  │Analyst │  │  Analyst    │
          └────────────┘  └────────┘  └────────────┘
                   │           │           │
                   │    ┌──────┴──────┐    │
                   │    │ Collateral  │    │
                   │    │   Analyst   │    │
                   │    └─────────────┘    │
                   │           │           │
                   └───────────┼───────────┘
                               ▼
                        ┌─────────────┐
                        │   Critic    │
                        └──────┬──────┘
                               ▼
                        ┌─────────────┐
                        │  Decision   │
                        └──────┬──────┘
                               ▼
                        ┌─────────────┐
                        │ Human Review│
                        │   (HITL)    │
                        └─────────────┘
```

### Agent Roles

| Agent | Responsibility |
|-------|---------------|
| **Credit Analyst** | Credit score, payment history, derogatory items |
| **Income Analyst** | Employment stability, DTI ratio, payment capacity |
| **Asset Analyst** | Down payment verification, reserves, large deposits |
| **Collateral Analyst** | Property value, LTV ratio, condition assessment |
| **Critic** | Cross-validates all analyses for consistency |
| **Decision** | Synthesizes findings into APPROVED / CONDITIONAL / DENIED |
| **Supervisor** | Routes workflow between agents |

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Orchestration | LangGraph (StateGraph) |
| LLM | OpenAI GPT-4o-mini via LangChain |
| Vector Store | ChromaDB (RAG policy retrieval) |
| SQL Database | PostgreSQL (SQLAlchemy ORM) |
| UI | Streamlit |
| Containerization | Docker + Docker Compose |
| Cloud Deployment | AWS ECS Fargate |

## Project Structure

```
├── app.py                        # Streamlit entry point
├── pyproject.toml                # Dependencies & project metadata
├── Dockerfile                    # Container image
├── docker-compose.yml            # Full stack (app + PostgreSQL + ChromaDB)
├── .env.example                  # Environment variable template
│
├── src/
│   ├── core/
│   │   ├── config.py             # Settings from .env (pydantic-settings)
│   │   ├── state.py              # UnderwritingState TypedDict
│   │   ├── compliance.py         # PII sanitization + bias detection
│   │   └── llm.py                # ChatOpenAI & Embeddings factories
│   ├── tools/
│   │   └── calculators.py        # DTI, LTV, reserves, housing ratio, etc.
│   ├── rag/
│   │   └── policy_store.py       # ChromaDB vector store + policy retrieval
│   ├── agents/
│   │   ├── credit_analyst.py     # Credit analysis agent
│   │   ├── income_analyst.py     # Income analysis agent
│   │   ├── asset_analyst.py      # Asset analysis agent
│   │   ├── collateral_analyst.py # Collateral analysis agent
│   │   ├── critic.py             # QA review agent
│   │   ├── decision.py           # Final decision agent
│   │   └── supervisor.py         # Routing & initialization
│   ├── workflow/
│   │   └── graph.py              # LangGraph StateGraph builder
│   ├── db/
│   │   ├── models.py             # SQLAlchemy models
│   │   └── repository.py         # CRUD operations
│   └── ui/
│       └── pages.py              # Streamlit pages
│
├── data/
│   ├── mortgage_test_cases.json  # 3 test cases (Approve / Conditional / Deny)
│   └── underwriting_policies.txt # Policy document for RAG indexing
│
├── scripts/
│   ├── start_local.sh            # Run locally without Docker
│   ├── deploy_docker.sh          # One-click Docker deployment
│   └── init_db.py                # Initialize database schema
│
└── deploy/aws/
    ├── task-definition.json      # ECS Fargate task definition
    └── deploy.sh                 # Build, push to ECR, deploy to ECS
```

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# 1. Clone the repo
git clone https://github.com/AMindCoder/senior-mortgage-underwriting-system.git
cd senior-mortgage-underwriting-system

# 2. Configure environment
cp .env.example .env
# Edit .env and set your OPENAI_API_KEY

# 3. Deploy (one command)
./scripts/deploy_docker.sh
```

This starts **three services**:
- **Streamlit app** at [http://localhost:8501](http://localhost:8501)
- **PostgreSQL** at `localhost:5432`
- **ChromaDB** at `http://localhost:8000`

### Option 2: Local Development

```bash
# 1. Install dependencies
pip install -e .

# 2. Start PostgreSQL and ChromaDB separately (or use Docker for just those)
docker compose up -d postgres chromadb

# 3. Configure and run
cp .env.example .env
# Edit .env — set OPENAI_API_KEY, POSTGRES_HOST=localhost, CHROMA_HOST=localhost

./scripts/start_local.sh
```

### Option 3: AWS ECS Fargate

```bash
# Prerequisites: AWS CLI configured, ECR repo created, RDS instance running

# Edit deploy/aws/deploy.sh with your AWS account details
./deploy/aws/deploy.sh
```

See `deploy/aws/task-definition.json` for the full ECS task configuration. Secrets (API keys, DB credentials) are pulled from AWS Secrets Manager.

## Environment Variables

| Variable | Description | Default |
|----------|------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | *required* |
| `OPENAI_API_BASE` | OpenAI API base URL | `https://api.openai.com/v1` |
| `OPENAI_MODEL` | LLM model | `gpt-4o-mini` |
| `OPENAI_TEMPERATURE` | LLM temperature | `0` |
| `OPENAI_EMBEDDING_MODEL` | Embedding model | `text-embedding-3-small` |
| `POSTGRES_USER` | PostgreSQL user | `underwriting` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `underwriting_secret` |
| `POSTGRES_DB` | PostgreSQL database | `mortgage_underwriting` |
| `POSTGRES_HOST` | PostgreSQL host | `postgres` (Docker) / `localhost` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `CHROMA_HOST` | ChromaDB host | `chromadb` (Docker) / `localhost` |
| `CHROMA_PORT` | ChromaDB port | `8000` |
| `POLICY_PDF_PATH` | Path to policy document | `data/underwriting_policies.pdf` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Features

- **Multi-Agent Orchestration** — 7 specialized agents coordinated via LangGraph StateGraph with supervisor routing
- **RAG Policy Compliance** — Underwriting policies indexed in ChromaDB; agents retrieve relevant sections per analysis
- **PII Sanitization** — SSN, name, address, phone, email redacted before LLM processing
- **Bias Detection** — Fair Lending Act compliance checks on every agent output
- **Calculator Tools** — Deterministic DTI, LTV, reserves, housing ratio calculations (no LLM hallucination)
- **Human-in-the-Loop** — High-risk decisions flagged for senior underwriter review via Streamlit UI
- **Audit Trail** — Full reasoning chain persisted for regulatory compliance
- **PostgreSQL Persistence** — Applications, decisions, and audit logs stored in relational DB
- **One-Click Deployment** — Docker Compose locally, ECS Fargate on AWS

## Streamlit UI Pages

| Page | Description |
|------|-------------|
| **Submit Application** | JSON input or form-based application submission |
| **Processing Dashboard** | View analysis results and decision summary |
| **Human Review** | HITL interface for overriding AI decisions |
| **Audit Trail** | Full reasoning chain, bias flags, compliance status |

## Test Cases

Three test cases are included in `data/mortgage_test_cases.json`:

| Case | Applicant | Credit Score | DTI | Expected Decision |
|------|-----------|-------------|-----|-------------------|
| CASE-2024-001 | Sarah Johnson | 780 | 28% | APPROVED |
| CASE-2024-002 | Michael Chen | 665 | 42% | CONDITIONAL_APPROVAL |
| CASE-2024-003 | Robert Martinez | 580 | 55% | DENIED |

## License

This project is for educational purposes as part of the Great Learning program.
