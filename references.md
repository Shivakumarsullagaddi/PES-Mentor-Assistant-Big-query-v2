# PES Mentor System — Reference Catalog

All official documentation, codelabs, repositories, and videos used during
the development of the PES Mentor Vault and Scout system.

---

## 1. ADK Core — Foundation

| Resource | Link |
|---|---|
| ADK Official Documentation | https://adk.dev |
| Your First Agent with ADK (Codelab) | https://codelabs.developers.google.com/your-first-agent-with-adk#0 |
| Build Agents with ADK — Foundation (Codelab) | https://codelabs.developers.google.com/devsite/codelabs/build-agents-with-adk-foundation#0 |
| Build Agents with ADK — Data Analyst Agent (Codelab) | https://codelabs.developers.google.com/devsite/codelabs/build-agents-with-adk-data-analyst-agent#0 |
| ADK + MCP + BigQuery + Maps (Codelab) | https://codelabs.developers.google.com/adk-mcp-bigquery-maps#0 |

---

## 2. ADK Streaming & Live Audio — Future Roadmap

> **Status:** Not implemented in current version. Live Audio through Google ID
> page requires additional OAuth configuration. Tracked for Phase 3.

| Resource | Link |
|---|---|
| ADK Streaming Developer Guide Part 1 | https://adk.dev/streaming/dev-guide/part1/ |
| Gemini Live API Documentation | https://ai.google.dev/gemini-api/docs/live-api |
| ADK Bidirectional Demo (GitHub Samples) | https://github.com/google/adk-samples/tree/main/python/agents/bidi-demo |
| ADK Streaming Workshop (YouTube) | https://www.youtube.com/watch?v=f0-t_jIW9yY |
| ADK Live API Intro (Codelab) | https://codelabs.developers.google.com/intro-to-adk-live#0 |
| ADK Bidirectional Streaming Workshop (GitHub) | https://github.com/kazunori279/adk-streaming-guide/blob/main/workshops/workshop.md |

---

## 3. Google Cloud Speech-to-Text

| Resource | Link |
|---|---|
| Speech-to-Text Console (Project: developer-491706) | https://console.cloud.google.com/speech/overview?project=developer-491706 |
| Speech-to-Text Python3 Codelab | https://codelabs.developers.google.com/codelabs/cloud-speech-text-python3#0 |

---

## 4. Multimodal & Advanced Agent Patterns

| Resource | Link |
|---|---|
| Personal Expense Assistant — Multimodal ADK (Codelab) | https://codelabs.developers.google.com/personal-expense-assistant-multimodal-adk#0 |
| Graph RAG, Memory & Multimodal Agents — Hands-On AI Workshop (YouTube) | https://www.youtube.com/watch?v=FzvIuoIJCcU |

---

## 5. Vertex AI Model Versions

| Resource | Link |
|---|---|
| Official Gemini & Embedding Model Version Table | https://cloud.google.com/vertex-ai/generative-ai/docs/learn/model-versions |

**Confirmed stable models for this project:**

| Model Name | Type | Used For |
|---|---|---|
| `gemini-2.5-flash` | LLM | Agent reasoning (both Vault & Scout) |
| `text-embedding-004` | Embedding | BigQuery `VECTOR_SEARCH` pipeline |

---

## 6. BigQuery ML & Vector Search

| Resource | Link |
|---|---|
| BigQuery ML — Remote Models | https://cloud.google.com/bigquery/docs/bigquery-ml-remote-model-tutorial |
| BigQuery Vector Search | https://cloud.google.com/bigquery/docs/vector-search |
| ML.GENERATE_TEXT_EMBEDDING Reference | https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-generate-text-embedding |

---

## 7. Security Notes

- All API keys must be stored in `.env` files locally and as Cloud Run
  environment variable secrets.
- Never commit `.env` files or raw API keys to any version control system.
- Tavily API key rotation is recommended every 90 days.
- The BigQuery service account (`bqcx-482781773486-b9a5`) requires
  `roles/aiplatform.user` IAM permission to call Vertex AI embedding models.
