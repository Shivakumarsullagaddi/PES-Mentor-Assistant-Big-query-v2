# Complete Project Documentation 📚

## 1. Getting Started: Google Cloud & BigQuery Setup
To start this project from scratch, follow these baseline infrastructure steps:
1. **Google Cloud Account**: Create a Google Cloud Project and note the `PROJECT_ID`. Enable billing.
2. **Enable Essential APIs**: Enable the Cloud Run API, Vertex AI API, and BigQuery API.
3. **Authentication**: In your terminal, authenticate the environment:
```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```
4. **BigQuery Database Setup**:
   - Create a Dataset (`pes_staff_dataset`) and a Table (`pes_staff_info`).
   - Run Vertex AI ML generation tasks to populate the table with a `text_embedding` column based on the professor's research topics.

## 2. API Keys & Environment Variables
Create a `.env` file in the root of your `adk_agent` directory. 
⚠️ **SECURITY WARNING:** NEVER expose your real `TAVILY_API_KEY` to public GitHub repositories. Use exactly this format:
```env
PROJECT_ID=your-project-id
GOOGLE_CLOUD_PROJECT=your-project-id
DATASET_ID=pes_staff_dataset
TABLE_ID=pes_staff_info
EMBEDDING_MODEL=embedding_model
MODEL="gemini-2.5-flash"
GOOGLE_GENAI_USE_VERTEXAI=TRUE
TAVILY_API_KEY=your_secure_tavily_key_here
```

## 3. The Architecture Pivot (Alternative Methods)
Our initial design relied on **Model Context Protocol (MCP)** endpoints decoupled from our agents via separate Cloud Run instances. 
- **The Failure**: MCP routing suffered from intense Docker isolation bugs, returning `405 Method Not Allowed` during internal handshake events. 
- **The Alternative Method**: We entirely decommissioned the MCP layer and embedded the exact backend logic (BigQuery clients and Tavily Python SDKs) directly into the `tools.py` of our ADK agents. This created a vastly faster, deeply integrated, and 100% serverless workflow!

## 4. Directory Structure
```text
pes_mentor_v2/
├── adk_agent/
│   ├── .env
│   ├── mentor_vault/
│   │   ├── agent.py         # Vault Logic & Prompting
│   │   ├── tools.py         # Native BigQuery SQL Tools
│   │   └── requirements.txt
│   ├── mentor_scout/
│   │   ├── agent.py         # Scout Logic & Consent Prompts
│   │   ├── tools.py         # BigQuery + Tavily Deep Search
│   │   └── requirements.txt
```

## 5. Agent Mechanics & Superior Features
### Mentor Vault (The Internal Intelligence)
Mentor Vault operates purely on the confirmed internal PES university database. It is equipped with highly advanced string manipulation:
1. **Tolerant Retrieval (Fuzzy Matching)**: We integrated Python's `difflib.get_close_matches(n=3)` with dynamic SQL `IN (...)` parameters. If a student severely misspells a professor's name, the agent automatically heals the spelling and fetches the closest 3 profiles!
2. **Multi-Parameter Wildcards**: Utilizes `LOWER(column) LIKE %val%` parameters rather than strict equality constraints, allowing infinite combinations of Department/Campus filtering.
3. **Vector Semantic Aliasing**: Solved complex SQL metadata errors by specifically mapping `distance_type => 'COSINE'` and explicitly aliasing `SELECT text_embedding AS embedding`.

### Mentor Scout (The Double-Powered Researcher)
Mentor Scout features all the internal database superiority of the Vault, but is armed with external live-web crawling capabilities.
- **Tavily Web Engine**: Integrates natively the `tavily-python` SDK to crawl LinkedIn, Google Scholar, and University press releases.
- **The "Consent" Prompt Feature**: Scout is coded to be uniquely curious. Instead of blindly running expensive Deep Web searches, she checks the internal database first, replies with emojis, and actively asks the user: *"Would you like me to do a deeper web research to find their latest external publications?"*

## 6. Elegant Rendering
Both agents are strictly prompted against generating ugly Markdown Tables (`|---|`) which overflow UI containers. Instead, they output HTML-embedded images at the absolute top of the chat logs (`<img src="URL" width="220" style="...">`) accompanied by rich emojis and beautifully bulleted Professional Dossier headers.

## 7. Deployment Commands
Deployment is strictly handled folder-by-folder in `us-central1` using the `uvx google-adk` framework to prevent requirements.txt bleed.

**Deploying Mentor Vault:**
```bash
cd ~/pes_mentor_v2/adk_agent
uvx --from google-adk==1.14.0 adk deploy cloud_run \
  --project=$PROJECT_ID \
  --region=us-central1 \
  --service_name=pes-mentor-vault \
  --with_ui mentor_vault \
  -- --set-env-vars="PROJECT_ID=$PROJECT_ID,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DATASET_ID=pes_staff_dataset,TABLE_ID=pes_staff_info,EMBEDDING_MODEL=embedding_model,MODEL=gemini-2.5-flash,GOOGLE_GENAI_USE_VERTEXAI=TRUE"
```

**Deploying Mentor Scout:**
```bash
cd ~/pes_mentor_v2/adk_agent
uvx --from google-adk==1.14.0 adk deploy cloud_run \
  --project=$PROJECT_ID \
  --region=us-central1 \
  --service_name=mentor-scout \
  --with_ui mentor_scout \
  -- --set-env-vars="PROJECT_ID=$PROJECT_ID,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DATASET_ID=pes_staff_dataset,TABLE_ID=pes_staff_info,EMBEDDING_MODEL=embedding_model,MODEL=gemini-2.5-flash,GOOGLE_GENAI_USE_VERTEXAI=TRUE,TAVILY_API_KEY=YOUR_TAVILY_KEY"
```
