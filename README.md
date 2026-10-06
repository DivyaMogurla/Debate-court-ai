# Debate Court – Multi-Agent AI Decision Support System

Three AI agents help you make better decisions:

- **Proponent** argues for your proposal
- **Opponent** argues against it
- **Judge** weighs both sides and returns a structured verdict (decision, confidence, risks, next steps)

The flow is orchestrated with **LangGraph**; the UI is **Streamlit**; the LLM is **Gemini** (API key) or a local **Ollama** model.

## Project structure

```
AI_Project/
├── app.py            # Streamlit UI
├── agents.py         # LLM client (Gemini/Ollama), Proponent/Opponent/Judge
├── workflow.py       # LangGraph debate loop
├── prompts.py        # Prompt templates
├── requirements.txt
├── .env              # API keys / settings (not committed)
└── README.md
```

## Setup (Python 3.11.9)

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

Edit `.env`:

- Gemini: set `LLM_PROVIDER=gemini` and `GEMINI_API_KEY=...`
- Ollama: set `LLM_PROVIDER=ollama`, then run `ollama pull llama3.1` and keep `ollama serve` running

## Run

```bash
streamlit run app.py
```

## How it works

```
Proponent -> Opponent -> (more rounds?) -> Proponent ... -> Judge -> Verdict
```

## Notes

- Verdicts are decision *support*, not professional legal, medical or financial advice.
- To pin exact versions after installing: `pip freeze > requirements.txt`.
