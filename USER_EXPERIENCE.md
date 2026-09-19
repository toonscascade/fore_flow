# 🎨 Forecast — User Experience (UX) & Interface Guide

The Forecast platform is designed with a **SOC (Security Operations Center) Analyst-first** philosophy. The user experience prioritizes rapid triage, clear data visualization, and actionable insights over overwhelming raw data presentation.

---

## 🎯 Target Audience
**Security Analysts, Incident Responders, and CISO/Security Managers** who need to quickly understand current threats, predict incoming attacks, and secure immutable evidence.

---

## 🚀 Key User Journeys

### 1. Secure Authentication & Onboarding
- **Experience**: Fast, secure login using Supabase Auth.
- **Design**: Minimalist login screen with clear error handling. JWT tokens are handled securely via HttpOnly cookies, ensuring the analyst doesn't have to worry about session hijacking.
- **Roles**: Distinct experiences based on role (Admin vs. Viewer), though the primary interface is tailored for the active analyst.

### 2. The "Single Pane of Glass" Overview
- **Experience**: Upon login, the analyst is presented with the **Dashboard Overview**.
- **Design Elements**:
  - **Stat Cards**: High-contrast, easy-to-read metric cards showing Total Threats, Critical Alerts, and System Health.
  - **Severity Badges**: Color-coded badges (Red for Critical, Orange for High) draw the eye immediately to what matters most.
- **Goal**: Answer "What is the current state of my network?" in less than 5 seconds.

### 3. Deep-Dive Threat Investigation
- **Experience**: Navigating to the **Threat Intel Center** allows for granular investigation.
- **Design Elements**:
  - **Data Tables**: Clean, paginated tables listing threats with sortable columns.
  - **Contextual Expansion**: Clicking a threat reveals associated IOCs (Indicators of Compromise) and MITRE ATT&CK mappings, eliminating the need to pivot between multiple tools.

### 4. Proactive AI Forecasting
- **Experience**: Moving beyond reactive defense using the **AI Forecast Panel**.
- **Design Elements**:
  - **Recharts Visualization**: Interactive line/area charts plotting historical threat volume against AI-predicted future volume.
  - **Tooltips**: Hovering over the graph provides specific predicted values and timestamps.
- **Goal**: Shift the analyst's mindset from "What happened?" to "What is about to happen?"

### 5. Forensic Evidence Verification
- **Experience**: The **Evidence Vault** provides a specialized view for immutable data.
- **Design Elements**:
  - **Verification Status Indicators**: Clear visual cues (e.g., green checkmarks, blockchain icons) showing whether a piece of evidence has been successfully anchored on-chain.
  - **One-Click Verification**: A simple button to re-verify the hash against the Ethereum smart contract, displaying the TxHash and Block Number seamlessly.

---

## 🧩 UI/UX Design Principles Applied

1. **Dark Mode by Default**: Tailored for SOC environments to reduce eye strain during long monitoring shifts. (If implemented; assuming modern security tool aesthetics).
2. **Information Hierarchy**: Critical alerts and high-level metrics are placed at the top/center. Raw logs and detailed JSON payloads are placed in expandable accordions or secondary tabs.
3. **Color as Context**: 
   - 🔴 **Red**: Critical threats, active breaches, blocked actions.
   - 🟠 **Orange/Yellow**: Warnings, anomalies requiring investigation.
   - 🟢 **Green**: System healthy, evidence verified on-chain.
   - 🔵 **Blue**: Informational, forecasts, standard metrics.
4. **Frictionless Navigation**: A persistent sidebar or top navigation bar allows instantaneous switching between the Overview, Threats, Forecasts, and Evidence views without losing context.
5. **Responsive Design**: Built with Vite and React, the dashboard scales gracefully, though it is optimized for wide-screen desktop displays typical in a SOC environment.

---

## 📈 Future UX Enhancements
- **Customizable Dashboards**: Allowing analysts to drag-and-drop widgets based on their specific daily focus (e.g., a malware analyst might prioritize the MITRE widget over the overall traffic graph).
- **Interactive Network Graphs**: Visualizing lateral movement and flow anomalies using node-link diagrams.
- **In-App Alerting**: Real-time toast notifications (e.g., via WebSockets) when a new critical anomaly is detected by the ML engine.
