# PES Mentor Recommendation System 🎓

## Aim of the Project
The goal of this project is to build a highly interactive, intelligent, and visually appealing AI Mentor Recommendation Web Platform for PES University students. It guides students to their perfect faculty mentors for capstones, research projects, and academic guidance by combining internal university databases with real-time web intelligence.

<img width="1464" height="622" alt="image" src="https://github.com/user-attachments/assets/34111909-71a4-42b8-a8ef-22f2d0cb002e" />

## 🔗 Live Deployment

Access the application here:  
👉 https://mentor-scout-482781773486.us-central1.run.app/

## What We Have Done
We successfully designed and deployed a multi-agent system using the **Google Agent Development Kit (ADK)**, hosted serverlessly on Google Cloud Run. The platform features two specialized intelligent agents:
1. **Mentor Vault**: A highly accurate internal database agent that instantly retrieves specific professor details, filters by campus, and performs advanced semantic profile matching using Vector Embeddings.
2. **Mentor Scout**: A "Double Powered" super-agent. It checks our internal BigQuery databases first, but can also launch highly advanced Deep Web Searches (via the Tavily AI engine) to fetch real-time LinkedIn profiles, external references, and recent publications.

## What We Faced (Challenges & Resolutions)
This architecture was forged through rigorous debugging and architectural pivots:
- **MCP Network Stalling**: Initially attempted to build Model Context Protocol (MCP) servers to host data bridges, but hit strict `HTTP 405 Method Not Allowed` constraints inside containerized environments. **Fix:** Pivoted to direct, stateless SDK integrations built natively into the ADK tools.
- **Strict Pydantic Crashing**: Google ADK's compiler aggressively rejected our default parameters. **Fix:** Mastered Python's `typing.Optional` to ensure stable tool compilation.
- **UI Markdown Distortions**: Generated images were originally expanding to massive sizes and rendering blindly at the bottom of the chat window. **Fix:** Stripped standard Markdown entirely and enforced rigid, beautifully aligned inline HTML `<img ...>` tags pushed to the top of the LLM's thought stream. 
- **Cloud Run Variable Bloat**: Early deployments failed due to conflicting Global Location tags. **Fix:** Systematically stripped `.env` variables to ensure perfectly localized `us-central1` orchestration.
