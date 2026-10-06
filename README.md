# ⚖️ Debate Court – Multi-Agent AI Decision Support System

**Debate Court** is an AI-powered decision-support system where three AI agents analyze a user's proposal from different perspectives.

* 🟢 **Proponent** – argues for the proposal
* 🔴 **Opponent** – argues against the proposal
* ⚖️ **Judge** – evaluates both sides and gives the final verdict

## 🚀 Features

* Multi-agent AI debate
* Structured AI verdict
* Risk and confidence analysis
* Recommended next steps
* Multiple debate rounds
* Gemini and Ollama support
* Streamlit UI
* LangGraph workflow

## 🛠️ Technologies

**Python • LangGraph • Streamlit • Google Gemini • Ollama • Requests • python-dotenv**

## 📁 Project Structure

```text
AI_Project/
├── app.py
├── agents.py
├── workflow.py
├── prompts.py
├── requirements.txt
└── README.md
```

## ⚙️ Installation

```bash
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## ▶️ Run

```bash
streamlit run app.py
```

If needed:

```bash
python -m streamlit run app.py
```

Open:

```text
http://localhost:8501
```

## 🧠 Workflow

```text
User Proposal
     ↓
Proponent
     ↓
Opponent
     ↓
Judge
     ↓
Final Verdict
```

## 🎯 Use Cases

* Technology decisions
* Project planning
* Business decisions
* Risk assessment
* General decision support

## 👩‍💻 Author

**Mogurla Divya**
B.Tech – Artificial Intelligence & Machine Learning

## ⚠️ Disclaimer

This project provides AI-based decision support and should not be considered professional legal, medical, or financial advice.
