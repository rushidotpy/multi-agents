link: https://multi-agents-workflow-automator.streamlit.app/

# Multi-Agent Marketing Brief Automator

A **4-agent LLM workflow** to turn short product descriptions into structured, high-quality marketing briefs in **one click**. Built with **Python + Streamlit** and leveraging **Groq's openai/gpt-oss-120B** model.

---

## 🚀 Features

- Automated multi-agent workflow:
  - **Researcher**: extracts insights from product description
  - **Strategist**: creates marketing strategy
  - **Writer**: drafts the brief
  - **Reviewer**: validates draft and triggers iterative refinement if needed
- Pre-agent LLM infers **target audience and metadata** automatically
- Token-efficient prompts: each agent sees **only minimal context**
- Rate-limit handling and retries using **Groq Python SDK**
- Browser-friendly **Streamlit UI** for one-click execution
- Secure API key management via **environment variables** or Streamlit secrets

---

## ⚙️ How It Works

1. **Input:** A short product description.
2. **Pre-agent LLM:** Infers target audience and metadata.
3. **Agent workflow:**  
   - Researcher → Strategist → Writer → Reviewer  
   - Optional reviewer loop for iterative refinement
4. **Output:** Structured, multi-section marketing brief.

**Prompt context per agent:**
| Agent      | Context Provided              |
|------------|-------------------------------|
| Researcher | Product + Summary             |
| Strategist | Product + Research            |
| Writer     | Product + Strategy            |
| Reviewer   | Product + Draft               |

---

## 💻 Tech Stack

- **Language:** Python 3.11+  
- **UI:** Streamlit  
- **LLM:** `openai/gpt-oss-120B` via **Groq SDK**  
- **Data:** JSON product specs, shared state directory  
- **Secrets:** `.env` file or Streamlit secrets (ignored in Git)  

---

## 📁 Project Structure

project-root/
│
├── app.py # Entry point, loads products and runs workflow
├── agents/ # Agent definitions and prompts
│ ├── researcher.py
│ ├── strategist.py
│ ├── writer.py
│ └── reviewer.py
├── llmclient.py # Groq LLM client with rate-limit handling
├── products.json # Sample product input
├── state/ # Shared workflow state (research, strategy, draft, review)
├── requirements.txt
└── README.md


Watch the multi-agent system generate a structured marketing brief: https://drive.google.com/file/d/12QV3Ddbs16qiGAD-_3o0qyyFX9X08jIq/view?usp=sharing

🔧 Next Steps / Future Work
Integrate real-world data retrieval for richer research

Support additional content formats (emails, ads, social posts)

Add analytics dashboards for output insights

Experiment with custom agent tools and plugins

📌 Key Learnings
Designing token-efficient multi-agent workflows

Handling rate limits and retries for large-scale LLM calls

Structuring AI automation for real-world usability

Iterative feedback loops to maintain high-quality outputs
