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

## 8. Updates & Bug Fixes (April 2026)

### 8.1 Performance Fix — `tools.py` (Mentor Scout)
**Problem:** Every call to `mentor_detailed_info` was executing `SELECT name FROM table` to pull all 572+ professor names into memory just to run `difflib` fuzzy matching locally. This caused unnecessary BigQuery scan costs and increased latency on every name lookup.

**Fix:** Introduced a **module-level in-memory name cache** (`_name_cache`) and a helper function `_get_all_names()`. The name list is now fetched from BigQuery exactly **once per server session** and reused for all subsequent calls.

```python
_name_cache: list[str] = []

def _get_all_names() -> list[str]:
    global _name_cache
    if _name_cache:
        print("[DEBUG] Name cache HIT — skipping BigQuery fetch.")
        return _name_cache
    print("[DEBUG] Name cache MISS — fetching all names from BigQuery...")
    sql = f"SELECT name FROM `{PROJECT_ID}.{DATASET}.{TABLE}`"
    df = client.query(sql).to_dataframe()
    _name_cache = df['name'].dropna().tolist()
    print(f"[DEBUG] Cached {len(_name_cache)} professor names.")
    return _name_cache
```

**Impact:** BigQuery scan cost for name lookup dropped from N calls (one per query) to exactly 1 call per deployment lifetime. Cache resets only on server restart/redeploy.

---

### 8.2 Name Wildcard Filter — `tools.py` (Mentor Scout)
**Problem:** `mentor_exact_filter` only supported `campus` and `department` parameters. There was no way to do a SQL wildcard search on professor names (e.g., "find all professors named Swetha").

**Fix:** Added an optional `name` parameter to `mentor_exact_filter`:
```python
def mentor_exact_filter(campus=None, department=None, name=None) -> str:
```
This runs `LOWER(name) LIKE '%<value>%'` inside BigQuery, enabling partial name searches directly in SQL without pulling all records into memory.

---

### 8.3 Prompt Engineering Fixes — `agent.py` (Mentor Scout)

#### Fix 1 — List Query Rule
**Problem:** When a user said "list all professors named Swetha", the agent incorrectly called `mentor_detailed_info` (individual fuzzy lookup) instead of a filter tool.

**Fix:** Added a **LIST QUERY RULE** section to the prompt. If the user's message contains keywords like "list", "show all", "find all", "professors named", or "professors starting with", the agent now calls `mentor_exact_filter(name="<partial name>")` directly.

#### Fix 2 — Last Initial Rule
**Problem:** Professor names ending in a single letter initial (e.g., "Swetha P", "Ramesh K") completely failed fuzzy matching because `difflib` cannot meaningfully compare a single character suffix. The correct professor was never returned.

**Fix:** Added a **LAST INITIAL RULE** to the prompt. When the last part of a given name is a single capital letter, the agent calls `mentor_exact_filter(name="Swetha P")` first (SQL `LIKE '%swetha p%'` finds exact matches), and only falls back to fuzzy matching if no results are returned.

#### Fix 3 — Deep Search Confirmation Protocol
**Problem:** The agent was auto-firing `tavily_deep_research` whenever a user used the word "deep search" in their message, without giving the user a chance to verify the correct professor was matched. This was especially risky when the fuzzy matcher returned an ambiguous result.

**Fix:** Introduced a **DEEP SEARCH CONFIRMATION PROTOCOL** with **no exceptions**. The agent now always:
1. Calls internal tools first and shows the professor profile.
2. Ends every Branch A response with a confirmation message asking the user to verify and authorize the deep search.
3. Only calls `tavily_deep_research` after the user explicitly replies "yes", "go ahead", "deep search", or "sure".

This applies even when the user explicitly says "deep search" in their original message — identity verification comes first.

**Branch C (Vault Miss) is also updated:** Even when the professor is not found internally, the agent now asks "Shall I launch a Deep Web Search?" instead of auto-firing Tavily.

---

### 8.4 Resume-Based Mentor Recommendation — `agent.py` (Mentor Scout)
**Feature:** Added a **RESUME UPLOAD HANDLING PROTOCOL** to the Mentor Scout prompt. When a student uploads their resume, the agent:

1. **Verifies** it is a valid resume (checks for sections like Education, Projects, Skills, Objective). If it is not a resume, it rejects the file with a friendly message.
2. **Validates University**: Checks if the student is from PES University. If from a different university, it still proceeds but adds a note.
3. **Extracts and Summarizes**: Pulls out student name, university, branch, skills, projects, and objective/about section. Presents a clean summary to the user.
4. **Asks for Confirmation**: After the summary, asks "Shall I find the best PES faculty mentors who match your project interests?"
5. **Recommends Mentors**: On confirmation, builds a rich natural-language description from the extracted resume data and calls `mentor_semantic_recommendation(project_description=...)` to find the best-matched faculty using vector cosine similarity.

**No new tools or UI changes were required.** The existing `mentor_semantic_recommendation` tool handles the vector search. The ADK natively supports file uploads.

**Status:** ✅ Implemented and tested. Resume upload, extraction, and mentor recommendation are fully working.
