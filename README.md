# 🛡️ Foreflow — Cybersecurity Threat Intelligence & Forecasting Platform

> **AI-powered threat detection, blockchain-anchored evidence, and predictive security analytics — all in one platform.**

Foreflow is a full-stack cybersecurity forecasting and threat intelligence platform built for **Smart India Hackathon (SIH)**. It combines real-time anomaly detection, deep learning forecasting, tamper-proof blockchain evidence anchoring, and a modern analyst dashboard to transform raw security data into actionable, court-admissible intelligence.

---

## 🏗️ Architecture Overview

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Foreflow Platform                              │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│   ┌──────────────┐     ┌──────────────────┐     ┌──────────────────┐  │
│   │  React/Vite  │────▶│  FastAPI Backend  │────▶│    Supabase      │  │
│   │  Dashboard   │     │  (Python 3.13)    │     │  PostgreSQL DB   │  │
│   │  :5173       │     │  :8000            │     │  (ap-northeast-1)│  │
│   └──────────────┘     └────────┬─────────┘     └──────────────────┘  │
│                                 │                                      │
│                    ┌────────────┼────────────┐                        │
│                    ▼            ▼            ▼                        │
│            ┌──────────┐  ┌──────────┐  ┌──────────────┐              │
│            │ ML Engine│  │Blockchain│  │MITRE ATT&CK  │              │
│            │(PyTorch +│  │(Hardhat  │  │Engine        │              │
│            │ sklearn) │  │EVM :8545)│  │              │              │
│            └──────────┘  └──────────┘  └──────────────┘              │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
Forecast/
├── frontend/                 # React + Vite SPA dashboard
│   ├── src/
│   │   ├── pages/            # Dashboard, Evidence, Forecast, ThreatIntel
│   │   ├── components/       # StatCard, SeverityBadge, charts/
│   │   ├── services/         # api.js, auth.js, supabaseClient.js
│   │   └── SecureApp.jsx     # Auth-gated app wrapper
│   ├── package.json
│   └── vite.config.js        # Proxy /api → FastAPI :8000
│
├── backend/                  # FastAPI application
│   ├── app/
│   │   ├── api/routes/       # auth, detection, evidence, forecast, threats, health
│   │   ├── core/             # config, auth (JWT + Argon2), constants
│   │   ├── database/         # connection.py, supabase_client.py
│   │   ├── models/           # SQLAlchemy ORM: User, Threat, Anomaly, Evidence, Forecast
│   │   └── services/         # blockchain_service, detection_service, forecast_service,
│   │                         # live_forecast_service, forecasting_service
│   ├── migrations/           # SQL schema migrations (Supabase-ready)
│   ├── tests/                # pytest test suite
│   └── requirements.txt
│
├── blockchain/               # Ethereum smart contracts
│   ├── contracts/
│   │   └── ThreatEvidence.sol  # Solidity evidence anchoring contract
│   ├── abi/                    # Compiled ABI + bytecode
│   └── scripts/                # deploy.py, deploy_local.py
│
├── hardhat-node/             # Local EVM blockchain node config
│   ├── hardhat.config.cjs
│   └── package.json
│
├── ml_engine/                # Machine Learning pipeline
│   ├── anomaly_detection/    # Isolation Forest training
│   ├── pipelines/            # training_pipeline.py
│   ├── data/                 # Training datasets
│   └── saved_models/         # anomaly_model.pkl, temporal_model.pt
│
├── models/                   # Neural network model artifacts
│   └── network_world_model.pth  # LSTM world model
│
├── mitre-engine/             # MITRE ATT&CK technique mapping
├── network_engine/           # Network flow parsing & feature extraction
├── threat-intelligence/      # Threat intel feed integration
├── scripts/                  # seed_dashboard.py, train_models.py
├── tests/                    # Integration tests (blockchain, detection, forecast)
├── api/                      # Vercel serverless entrypoint
├── docs/                     # Project documentation
└── .env                      # Environment configuration
```

---

## 🚀 Core Features

### 🔐 Authentication & Authorization
- **Supabase-backed** user management with PostgreSQL
- **JWT session cookies** (HttpOnly, secure) via `argon2` password hashing
- **Role-based access control** (ADMIN, ANALYST, VIEWER)
- Registration, login, session validation, and audit logging

### 🤖 AI / Machine Learning Models
- **Isolation Forest Anomaly Detector** — Unsupervised anomaly detection on network flow features (packet count, byte volume, flow duration, port entropy)
- **PyTorch LSTM Temporal Forecaster** — Deep learning sequence model for predicting future threat levels over configurable horizons (default: 24 steps)
- **Network State World Model** — Neural network for modeling network state transitions and generating probabilistic threat forecasts
- **SHAP Explainability** — Model-agnostic feature importance for every prediction

### ⛓️ Blockchain Evidence Anchoring
- **Solidity Smart Contract** (`ThreatEvidence.sol`) deployed on local Hardhat EVM (Chain ID: 31337)
- **On-chain evidence hashing** — SHA-256 content hash anchored immutably with submitter address and timestamp
- **Tamper verification** — `isAnchored()` and `getRecord()` views for cryptographic proof
- **Web3.py integration** — Python-native blockchain interaction via `web3==7.2.0`

### 📊 Analyst Dashboard
- **Overview Console** — Real-time risk scoring, active threat count, anomaly metrics
- **Threat Intelligence Center** — MITRE ATT&CK mapped threats with severity badges and IOC tracking
- **AI Forecast Panel** — Interactive temporal forecast charts powered by Recharts
- **Evidence Vault** — Blockchain-anchored evidence records with on-chain verification status
- **Live Monitor** — Real-time network flow anomaly detection feed

### 🗄️ Database (Supabase PostgreSQL)
8 core tables with full audit trail:
| Table | Purpose |
|-------|---------|
| `users` | Analyst accounts, roles, credentials |
| `threats` | Detected threats with MITRE mappings |
| `anomalies` | Network flow anomaly records |
| `forecasts` | AI-generated threat forecasts |
| `evidence` | Forensic evidence with blockchain anchors |
| `audit_logs` | Full platform activity audit trail |
| `user_sessions` | Active session tracking |
| `threat_anomaly_links` | Threat ↔ Anomaly correlation mapping |

---

## 🛠️ Technology Stack

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.3.1 | UI framework |
| Vite | 7.3.6 | Build tool & dev server |
| React Router | 7.18.3 | Client-side routing |
| Recharts | 3.10.1 | Data visualization & charts |
| Lucide React | 0.446.0 | Icon library |
| Axios | 1.20.0 | HTTP client |
| @supabase/supabase-js | 2.49.1 | Supabase client SDK |

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.13 | Runtime |
| FastAPI | 0.115.0 | Web framework |
| Uvicorn | 0.30.6 | ASGI server |
| SQLAlchemy | 2.0.35 | Async ORM |
| asyncpg | 0.31.0 | PostgreSQL async driver |
| Pydantic | 2.9.2 | Data validation |
| PyJWT | 2.9.0 | JWT token handling |
| argon2-cffi | 23.1.0 | Password hashing |
| Supabase SDK | 2.11.0 | Supabase Python client |

### AI / ML
| Technology | Version | Purpose |
|------------|---------|---------|
| PyTorch | 2.4.1 | Deep learning (LSTM forecaster) |
| scikit-learn | 1.5.2 | Isolation Forest anomaly detection |
| NumPy | 1.26.4 | Numerical computing |
| Pandas | 2.2.3 | Data manipulation |
| SHAP | 0.46.0 | Model explainability |
| Scapy | 2.6.0 | Network packet parsing |

### Blockchain
| Technology | Version | Purpose |
|------------|---------|---------|
| Solidity | ^0.8.20 | Smart contract language |
| Hardhat | Latest | Local EVM node & deployment |
| Web3.py | 7.2.0 | Python ↔ Ethereum interaction |
| eth-account | 0.13.1 | Ethereum account management |

### Infrastructure
| Technology | Purpose |
|------------|---------|
| Supabase | Managed PostgreSQL + Auth (ap-northeast-1) |
| Hardhat Node | Local EVM blockchain (port 8545) |
| Vercel | Production deployment |
| Docker | Containerization (docker_compose.yml) |

---

## 🔑 Supabase Configuration

### Project Details
| Property | Value |
|----------|-------|
| **Project Ref** | `yeypcjqozmdergeeigwu` |
| **Region** | `ap-northeast-1` (Tokyo) |
| **Dashboard** | https://supabase.com/dashboard/project/yeypcjqozmdergeeigwu |
| **API URL** | `https://yeypcjqozmdergeeigwu.supabase.co` |
| **DB Pooler** | `aws-0-ap-northeast-1.pooler.supabase.com:5432` |

### Database Connection
```
postgresql+asyncpg://postgres.yeypcjqozmdergeeigwu:<PASSWORD>@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres
```

### Credentials
| Credential | Value |
|------------|-------|
| **DB User** | `postgres.yeypcjqozmdergeeigwu` |
| **DB Password** | `<YOUR_DB_PASSWORD>` |
| **Admin Email** | `admin@foreflow.security` |
| **Admin Password** | `<YOUR_ADMIN_PASSWORD>` |

> ⚠️ **Security Note**: Rotate these credentials before any production deployment. Never commit production secrets to source control.

### Environment Keys
```env
SUPABASE_URL=https://yeypcjqozmdergeeigwu.supabase.co
SUPABASE_ANON_KEY=<YOUR_SUPABASE_ANON_KEY>
SUPABASE_SERVICE_ROLE_KEY=<YOUR_SUPABASE_SERVICE_ROLE_KEY>
```

---

## ⚡ Quick Start — Run the Entire Project

### Prerequisites
- **Python 3.13+** installed
- **Node.js 18+** and npm installed
- **Git** installed

### Step 1: Clone & Enter Project
```bash
git clone https://github.com/dhairyabansal-dev/Forecast.git
cd Forecast
```

### Step 2: Create Python Virtual Environment
```bash
python -m venv .venv
```

**Activate (Windows PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Activate (Linux/macOS):**
```bash
source .venv/bin/activate
```

### Step 3: Install Backend Dependencies
```bash
pip install -r backend/requirements.txt
```

### Step 4: Configure Environment Variables
Copy the example environment file and fill in your Supabase credentials:
```bash
copy .env.example .env
copy .env.example backend\.env
```

Required variables in `.env` and `backend/.env`:
```env
# Supabase
SUPABASE_URL=https://yeypcjqozmdergeeigwu.supabase.co
SUPABASE_ANON_KEY=<your_anon_key>
SUPABASE_SERVICE_ROLE_KEY=<your_service_role_key>
DATABASE_URL=postgresql+asyncpg://postgres.yeypcjqozmdergeeigwu:<password>@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres

# Blockchain (local Hardhat)
BLOCKCHAIN_PROVIDER_URL=http://127.0.0.1:8545
BLOCKCHAIN_CHAIN_ID=31337
BLOCKCHAIN_PRIVATE_KEY=<YOUR_HARDHAT_PRIVATE_KEY>
```

Frontend env (`frontend/.env`):
```env
VITE_SUPABASE_URL=https://yeypcjqozmdergeeigwu.supabase.co
VITE_SUPABASE_ANON_KEY=<your_anon_key>
```

### Step 5: Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

### Step 6: Install & Start Local Blockchain Node
```bash
cd hardhat-node
npm install
npx hardhat node
```
> This starts a local EVM on `http://127.0.0.1:8545` (Chain ID 31337)

In a **new terminal**, deploy the smart contract:
```bash
cd Forecast
.\.venv\Scripts\python.exe blockchain/scripts/deploy_local.py
```
> Copy the deployed contract address to `THREAT_EVIDENCE_CONTRACT_ADDRESS` in both `.env` files.

### Step 7: Train AI Models
```bash
.\.venv\Scripts\python.exe scripts/train_models.py
```
This generates:
- `ml_engine/saved_models/anomaly_model.pkl` — Isolation Forest
- `ml_engine/saved_models/temporal_model.pt` — LSTM Forecaster
- `models/network_world_model.pth` — Network World Model

### Step 8: Seed Dashboard Data
```bash
.\.venv\Scripts\python.exe scripts/seed_dashboard.py
```
Creates sample threats, anomalies, admin user, and blockchain-anchored evidence.

### Step 9: Start Backend Server
```bash
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --app-dir backend
```

### Step 10: Start Frontend Dev Server
In a **new terminal**:
```bash
cd frontend
npm run dev
```

### Step 11: Open the Dashboard
Navigate to **http://localhost:5173** in your browser.

**Login credentials:**
- Email: `admin@foreflow.security`
- Password: `SecureAdmin!2026`

---

## 📡 API Reference

Base URL: `http://127.0.0.1:8000`

### Health & System
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Application health check |
| GET | `/api/v1/health/db` | Database connectivity status |
| GET | `/api/v1/health/blockchain` | Blockchain node connectivity |

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new analyst account |
| POST | `/api/auth/login` | Login and receive JWT session cookie |
| GET | `/api/auth/me` | Get current authenticated user |
| POST | `/api/auth/logout` | Invalidate session |

### Threat Intelligence
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/threats` | List all detected threats |
| GET | `/api/v1/threats/{id}` | Get threat details |
| POST | `/api/v1/threats` | Create new threat record |
| PUT | `/api/v1/threats/{id}` | Update threat |
| DELETE | `/api/v1/threats/{id}` | Delete threat |

### AI Detection & Forecasting
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/detection/analyze` | Run anomaly detection on network flow |
| POST | `/api/v1/forecast/generate` | Generate temporal threat forecast |
| GET | `/api/v1/forecast/history` | Retrieve past forecasts |

### Evidence & Blockchain
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/evidence` | List evidence records |
| POST | `/api/v1/evidence` | Create new evidence |
| POST | `/api/v1/evidence/{id}/anchor` | Anchor evidence hash on blockchain |
| GET | `/api/v1/evidence/{id}/verify` | Verify on-chain integrity |

---

## 🧪 Testing

### Run Full Test Suite
```bash
.\.venv\Scripts\python.exe -m pytest backend/tests tests/ -v
```

### Test Categories
| Test File | Coverage |
|-----------|----------|
| `backend/tests/test_backend_smoke.py` | API health, DB connection, blockchain status |
| `backend/tests/test_auth_security.py` | Registration, login, JWT validation, role checks |
| `tests/test_blockchain.py` | Evidence hashing, anchoring, verification |
| `tests/test_detection.py` | Anomaly detection API integration |
| `tests/test_forecasting.py` | Forecast generation API integration |

### Expected Output
```
========================= 11 passed, 1 warning in ~78s =========================
```

---

## 🔗 Blockchain Details

### Smart Contract: `ThreatEvidence.sol`
- **Network**: Local Hardhat EVM (Chain ID `31337`)
- **Contract Address**: `0x5FbDB2315678afecb367f032d93F642f64180aa3`
- **Deployer**: Hardhat Account #0 (`0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266`)

### Contract Functions
| Function | Type | Description |
|----------|------|-------------|
| `anchorEvidence(bytes32)` | Write | Anchor evidence hash on-chain |
| `isAnchored(bytes32)` | View | Check if hash exists |
| `getRecord(bytes32)` | View | Get submitter, timestamp, existence |
| `transferOwnership(address)` | Write | Transfer contract ownership |

---

## 🐳 Docker Deployment

```bash
docker compose -f docker_compose.yml up --build
```

---

## 🌐 Production Deployment (Vercel)

The project is configured for Vercel Services:
- `web` → Vite frontend from `frontend/`
- `api` → FastAPI through `api/index.py`
- All `/api/*` requests route to the FastAPI service

Set environment variables in the Vercel project dashboard — **never commit production secrets**.

---

## 📋 Environment Variable Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `APP_NAME` | ✅ | Application name |
| `APP_ENV` | ✅ | `development` / `production` |
| `SECRET_KEY` | ✅ | JWT signing secret |
| `DATABASE_URL` | ✅ | Supabase PostgreSQL connection string |
| `SUPABASE_URL` | ✅ | Supabase project API URL |
| `SUPABASE_ANON_KEY` | ✅ | Supabase anonymous/public key |
| `SUPABASE_SERVICE_ROLE_KEY` | ✅ | Supabase service role key |
| `BLOCKCHAIN_PROVIDER_URL` | ✅ | EVM JSON-RPC endpoint |
| `BLOCKCHAIN_CHAIN_ID` | ✅ | EVM chain ID |
| `BLOCKCHAIN_PRIVATE_KEY` | ✅ | Deployer wallet private key |
| `THREAT_EVIDENCE_CONTRACT_ADDRESS` | ✅ | Deployed contract address |
| `ANOMALY_MODEL_PATH` | ✅ | Path to Isolation Forest model |
| `TEMPORAL_MODEL_PATH` | ✅ | Path to LSTM model |
| `WORLD_MODEL_PATH` | ✅ | Path to world model |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ❌ | JWT expiry (default: 720) |
| `FORECAST_HORIZON` | ❌ | Forecast steps (default: 24) |
| `SEQUENCE_LENGTH` | ❌ | LSTM input sequence length (default: 48) |
| `LOG_LEVEL` | ❌ | Logging level (default: INFO) |

---

## 🔒 Security Considerations

- All passwords hashed with **Argon2id** (OWASP recommended)
- JWT tokens stored in **HttpOnly secure cookies** (no localStorage)
- **CORS** restricted to configured origins only
- **Role-based access** with ADMIN/ANALYST/VIEWER permissions
- Blockchain evidence provides **cryptographic tamper detection**
- Audit logs track all security-relevant platform activity

---

## 👥 Team

Built for **Smart India Hackathon (SIH)** by Team Nirmantra.

## 📄 License

See [LICENSE](./LICENSE) for details.
