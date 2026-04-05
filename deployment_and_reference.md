# PES Mentor System — Deployment Guide & Reference Catalog

This document covers the complete deployment process for both the `mentor_vault` and
`mentor_scout` agents using Google Agent Development Kit (ADK) `v1.28.1` on Cloud Run,
along with all official references used during development.

---

## Key Configuration Variables

| Variable                  | Value              | Purpose                                       |
|---------------------------|--------------------|-----------------------------------------------|
| `MODEL`                   | `gemini-2.5-flash` | Primary reasoning model for both agents       |
| `EMBEDDING_MODEL`         | `text-embedding-004` | Required for BigQuery `VECTOR_SEARCH`       |
| `GOOGLE_GENAI_USE_VERTEXAI` | `TRUE`           | Routes all API calls through Vertex AI        |
| `PROJECT_ID`              | `developer-491706` | Your GCP Project ID                           |
| `DATASET_ID`              | `pes_staff_dataset`| BigQuery dataset name                         |
| `TABLE_ID`                | `pes_staff_info`   | BigQuery table name                           |

> **Important:** `text-embedding-004` is the correct stable embedding model confirmed
> by the Vertex AI Model Versions documentation. Do NOT use placeholder names like
> `embedding_model`.

---

## 1. Deploying Mentor Vault

The `mentor_vault` agent queries the internal PES BigQuery database only.

```bash
uvx --from google-adk==1.28.1 adk deploy cloud_run \
  --project=developer-491706 \
  --region=us-central1 \
  --service_name=pes-mentor-vault \
  --with_ui mentor_vault \
  -- --set-env-vars="PROJECT_ID=developer-491706,GOOGLE_CLOUD_PROJECT=developer-491706,DATASET_ID=pes_staff_dataset,TABLE_ID=pes_staff_info,EMBEDDING_MODEL=text-embedding-004,MODEL=gemini-2.5-flash,GOOGLE_GENAI_USE_VERTEXAI=TRUE"
```

---

## 2. Deploying Mentor Scout

The `mentor_scout` agent is the root agent. It queries internal BigQuery tools AND
performs live web research using the Tavily API.

> **Security Warning:** Replace `[YOUR_TAVILY_API_KEY]` with your actual key before
> running. NEVER commit your real API key to GitHub or any version control system.

```bash
uvx --from google-adk==1.28.1 adk deploy cloud_run \
  --project=developer-491706 \
  --region=us-central1 \
  --service_name=mentor-scout \
  --with_ui mentor_scout \
  -- --set-env-vars="PROJECT_ID=developer-491706,GOOGLE_CLOUD_PROJECT=developer-491706,DATASET_ID=pes_staff_dataset,TABLE_ID=pes_staff_info,EMBEDDING_MODEL=text-embedding-004,MODEL=gemini-2.5-flash,GOOGLE_GENAI_USE_VERTEXAI=TRUE,TAVILY_API_KEY=[YOUR_TAVILY_API_KEY]"
```

---

## 3. Post-Deployment Verification

Once deployed, Cloud Run outputs a public HTTPS Service URL.
Open the URL in your browser to access the ADK Web UI and test:

- **Text input** → Handled by `gemini-2.5-flash` over standard REST API
- **Microphone** → Handled by the Live WebSocket endpoint (experimental)

---

## 4. Reference Catalog

### ADK Fundamentals (Codelabs)

- **Your First Agent with ADK**
  https://codelabs.developers.google.com/your-first-agent-with-adk#0

- **Build Agents with ADK — Data Analyst Agent**
  https://codelabs.developers.google.com/devsite/codelabs/build-agents-with-adk-data-analyst-agent#0

### Multimodal Integration

- **Personal Expense Assistant (Multimodal ADK)**
  https://codelabs.developers.google.com/personal-expense-assistant-multimodal-adk#0

### Vertex AI Model Versions

- **Official Gemini & Embedding Model Version Table**
  Confirms `gemini-2.5-flash` and `text-embedding-004` as currently stable versions.
  https://docs.cloud.google.com/vertex-ai/generative-ai/docs/learn/model-versions#embeddings-models

### Advanced Streaming & Audio (Future Roadmap)

- **Introduction to the ADK Live API (Audio-to-Audio)**
  https://codelabs.developers.google.com/intro-to-adk-live#0

- **ADK Bidirectional Streaming Developer Workshop (GitHub)**
  https://github.com/kazunori279/adk-streaming-guide/blob/main/workshops/workshop.md
