# PES Mentor System — Deployment Guide

Complete deployment process for `mentor_vault` and `mentor_scout` agents
using Google ADK `v1.28.1` on Cloud Run.

---

## Key Configuration Variables

| Variable                    | Value                | Purpose                                        |
|-----------------------------|----------------------|------------------------------------------------|
| `MODEL`                     | `gemini-2.5-flash`   | Primary reasoning model for both agents        |
| `EMBEDDING_MODEL`           | `text-embedding-004` | Required for BigQuery `VECTOR_SEARCH`          |
| `GOOGLE_GENAI_USE_VERTEXAI` | `TRUE`               | Routes all API calls through Vertex AI         |
| `PROJECT_ID`                | `developer-491706`   | GCP Project ID                                 |
| `DATASET_ID`                | `pes_staff_dataset`  | BigQuery dataset name                          |
| `TABLE_ID`                  | `pes_staff_info`     | BigQuery table name                            |

> **Important:** `text-embedding-004` is the confirmed stable embedding model.
> Do NOT use placeholder names like `embedding_model` in deployment commands.

---

## 1. Deploying Mentor Vault

The `mentor_vault` agent queries the internal PES BigQuery database only.

**Directory to run from:** `~/pes_mentor_v2/adk_agent/`

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

The `mentor_scout` agent queries internal BigQuery tools AND performs live web
research using the Tavily API. This is the ROOT agent.

**Directory to run from:** `~/pes_mentor_v2/adk_agent/`

> **Security Warning:** Replace `[YOUR_TAVILY_API_KEY]` with your actual key.
> NEVER commit your real API key to GitHub or any public version control system.

```bash
uvx --from google-adk==1.28.1 adk deploy cloud_run \
  --project=developer-491706 \
  --region=us-central1 \
  --service_name=mentor-scout \
  --with_ui mentor_scout \
  -- --set-env-vars="PROJECT_ID=developer-491706,GOOGLE_CLOUD_PROJECT=developer-491706,DATASET_ID=pes_staff_dataset,TABLE_ID=pes_staff_info,EMBEDDING_MODEL=text-embedding-004,MODEL=gemini-2.5-flash,GOOGLE_GENAI_USE_VERTEXAI=TRUE,TAVILY_API_KEY=[YOUR_TAVILY_API_KEY]"
```

---

## 3. BigQuery Vector Search — Test Query

Use this query in BigQuery Studio to validate the embedding pipeline before deployment.

```sql
SELECT base.name, base.department, base.research, base.image
FROM VECTOR_SEARCH(
    TABLE `developer-491706.pes_staff_dataset.pes_staff_info`,
    'embedding',
    (
        SELECT text_embedding AS embedding
        FROM ML.GENERATE_TEXT_EMBEDDING(
            MODEL `developer-491706.pes_staff_dataset.embedding_model`,
            (SELECT 'cyber security in machine learning and blockchain' AS content)
        )
    ),
    top_k => 5,
    distance_type => 'COSINE'
)
```

**Expected Result:** Top 5 faculty members ranked by cosine similarity to the query topic.

---

## 4. Post-Deployment Verification

Once deployed, Cloud Run outputs a public HTTPS Service URL.
Open the URL in your browser to access the ADK Web UI and test:

- **Text input** → Handled by `gemini-2.5-flash` over standard REST API
- **Microphone (Future)** → Live WebSocket endpoint (see references.md for roadmap)

### Local Testing Before Deployment

**Directory:** `~/pes_mentor_v2/adk_agent/`

```bash
# Terminal mode (interactive CLI)
adk run mentor_scout

# Web UI mode (browser at port 8000)
adk web --allow_origins 'regex:https://.*\.cloudshell\.dev'
```

---

## 5. Environment Variables — Local `.env` File

**Directory:** `~/pes_mentor_v2/`
**File:** `.env`

```text
PROJECT_ID=developer-491706
GOOGLE_CLOUD_PROJECT=developer-491706
DATASET_ID=pes_staff_dataset
TABLE_ID=pes_staff_info
EMBEDDING_MODEL=embedding_model
MODEL=gemini-2.5-flash
GOOGLE_GENAI_USE_VERTEXAI=TRUE
TAVILY_API_KEY=[YOUR_TAVILY_API_KEY]
```

> **Note on EMBEDDING_MODEL:** In local `.env`, we reference the BigQuery remote model
> alias `embedding_model`. In Cloud Run deployment commands, we use `text-embedding-004`
> as the explicit Vertex AI model name.
