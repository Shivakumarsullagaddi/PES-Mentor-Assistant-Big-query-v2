# 🏛️ PES Mentor System: Architectural Process & Design Philosophy

This document provides a deep-dive into how the **PES Mentor Scout** and **Vault** agents function, the technical logic behind their tools, and the strategic reasoning for our multi-agent architecture.

---

## 🛠️ Tool Interaction Matrix

The "Scout" agent utilizes a **Hybrid Search Strategy** to ensure every student query—whether a specific name or a vague idea—is handled with 100% precision.

| Tool Name | Search Type | Input Parameters | Background Logic | Best Used For... |
|:---|:---|:---|:---|:---|
| **`mentor_exact_filter`** | Deterministic SQL | `campus`, `department` | SQL `LIKE` Wildcards | Browsing lists of professors by category. |
| **`mentor_detailed_info`** | Fuzzy Logic Search | `professor_name` | `difflib` Pattern Matching | Deep-dives into a specific person (handles typos). |
| **`mentor_semantic_recommendation`**| AI Vector Search | `project_description`| Cosine Similarity | Matching project ideas to research expertise. |
| **`tavily_deep_research`** | Live Web Search | `query` | External API (Tavily) | Finding context outside the BigQuery database. |

---

## 🧠 Technical Workflow: How it Works

### 1. The Semantic "Idea" Match (Vector Search)
When a student describes a project, we don't look for keywords. We look for **meaning**.
- **The Vector:** We convert the text into a 768-dimensional mathematical vector using `text-embedding-004`.
- **The Comparison:** BigQuery uses **Cosine Similarity** to measure the "angle" between the student's idea and the professor's research history.
- **The Result:** We find professors who work on similar *concepts*, even if they don't use the exact same words.

### 2. The Human Error Guardrail (Fuzzy Matching)
If a user misspells a name, the `mentor_detailed_info` tool uses the **Gestalt Pattern Matching** algorithm. It calculates a similarity score between the input and all 570+ names in the database. If the score is >0.4, it finds the "Closest Intent" and retrieves the full profile.

### 3. The Precision Filter (SQL Wildcards)
For categorical searches (e.g., "EC Department"), we use `LOWER()` and `LIKE %value%`. This ensures that "EC", "Electronics", and "EC Dept" all point to the same database results without failing.

---

## 🚀 Why Multi-Agent? (Response to Resource Constraints)

In a professional environment, we face **Token Limits**, **Latency**, and **Cost constraints**. We solved this by splitting the logic into two specialized agents:

### 🛡️ The Mentor Vault (Internal Security)
- **Focus:** 100% internal database lookups.
- **Why:** By restricting it from the web, we save tokens and ensure it never hallucinates facts that aren't in the BigQuery sheet. It is a "Low-Cost, High-Accuracy" agent.

### 🛰️ The Mentor Scout (The Root Explorer)
- **Focus:** Higher-level reasoning and external search.
- **Why:** Web research is "Expensive" in terms of tokens and time. By making Scout the "Brain," it only uses the expensive Tavily tool when the internal "Vault" tools can't find an answer.

---

## 🔄 The End-to-End Flow

1.  **User Input:** Student asks a question in the UI.
2.  **Intent Analysis:** The Agent decides: "Is this a specific person? A category? Or a new idea?"
3.  **Tool Selection:**
    - If **Category** → `mentor_exact_filter`
    - If **Specific Person** → `mentor_detailed_info`
    - If **Vague Idea** → `mentor_semantic_recommendation`
4.  **Database Retrieval:** BigQuery processes the SQL/Vector query in < 500ms.
5.  **Contextual Response:** The Agent formats the data into a friendly, emoji-rich answer with the professor's image prominently displayed.

---

## 💎 Design Philosophy: "Aesthetic Precision"
We chose **GCP Cloud Run** and **BigQuery** because they allow us to scale to thousands of students without a permanent server cost. We use **Hybrid Search** because AI is great at ideas, but SQL is better at facts. Combining them gives us the best of both worlds.
