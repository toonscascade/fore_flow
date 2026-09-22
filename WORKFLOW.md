# 🔄 Foreflow — System & Operational Workflows

The Foreflow platform is designed around a seamless pipeline that ingests raw network and threat data, processes it through advanced AI models, anchors findings immutably on the blockchain, and presents actionable intelligence to security analysts.

Below are the core operational workflows of the platform.

---

## 1. 🌐 Data Ingestion & Processing Workflow

**Goal**: Collect and standardize raw telemetry and intelligence.

1. **Network Telemetry Capture**: The `network_engine` intercepts raw network flow data (PCAP/Flow logs).
2. **Feature Extraction**: Scapy parses packets to extract key features (byte volume, packet counts, port entropy, inter-arrival times).
3. **Threat Intel Aggregation**: The `threat-intelligence` module pulls IOCs (Indicators of Compromise) from external feeds.
4. **Data Standardization**: All ingested data is normalized and staged in the Supabase PostgreSQL database for downstream processing.

---

## 2. 🧠 AI Detection & Forecasting Workflow

**Goal**: Identify current anomalies and predict future threat trajectories.

1. **Anomaly Detection (Real-Time)**:
   - Standardized network flows are passed to the **Isolation Forest** model (`anomaly_model.pkl`).
   - The model assigns an anomaly score (0.0 to 1.0) and a boolean `is_anomalous` flag.
   - Detected anomalies are logged to the `anomalies` table.
2. **Threat Correlation**:
   - Anomalies are cross-referenced with the MITRE ATT&CK engine and known threat intel.
   - Highly correlated events are promoted to active **Threats** and logged in the `threats` table.
3. **Temporal Forecasting (Batch/Triggered)**:
   - Historical threat data (last 48 sequence steps) is fed into the **PyTorch LSTM Forecaster** (`temporal_model.pt`).
   - The model predicts threat severity and volume for the next 24 steps (the Forecast Horizon).
   - Forecasts are stored in the `forecasts` table and visualized in the UI.

---

## 3. ⛓️ Blockchain Evidence Anchoring Workflow

**Goal**: Ensure cryptographic, tamper-proof integrity for critical forensic evidence.

1. **Evidence Selection**: A high-severity threat or critical anomaly is flagged for anchoring (either automatically or manually by an analyst).
2. **Hash Generation**: The backend generates a SHA-256 hash of the evidence payload (JSON string containing telemetry, IOCs, timestamps).
3. **Smart Contract Execution**: 
   - The backend uses Web3.py to call the `anchorEvidence(bytes32)` function on the `ThreatEvidence` Solidity smart contract.
   - The transaction is signed with the configured `BLOCKCHAIN_PRIVATE_KEY` and submitted to the local Hardhat EVM network.
4. **On-Chain Verification**: 
   - The transaction hash and block number are recorded in the `evidence` Supabase table.
   - Analysts can later trigger the `isAnchored()` function to verify that the stored hash matches the blockchain record, proving the data has not been altered since detection.

---

## 4. 👨‍💻 Analyst Response Workflow (UI Journey)

**Goal**: Enable SOC analysts to rapidly triage, investigate, and respond to threats.

1. **Triage (Overview)**: 
   - Analyst logs in and views the main dashboard.
   - They assess the overall system risk score and review the top active threats.
2. **Investigation (Threat Center)**:
   - Analyst selects a specific threat (e.g., "Credential Spraying Campaign").
   - They review the mapped MITRE ATT&CK tactics, involved IPs, and linked network anomalies.
3. **Forecasting (AI Forecast Panel)**:
   - To understand the potential evolution of the threat, the analyst reviews the AI-generated forecast graph to see if the attack volume is predicted to escalate.
4. **Verification (Evidence Vault)**:
   - If the threat requires legal or formal reporting, the analyst navigates to the Evidence Vault.
   - They initiate an on-chain verification check to cryptographically prove the integrity of the telemetry associated with the threat.
