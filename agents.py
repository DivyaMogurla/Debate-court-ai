"""LLM client wrapper and agent definitions for Debate Court."""

from __future__ import annotations

import os

import requests
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    """LLM wrapper supporting Gemini and local Ollama."""

    def __init__(
        self,
        provider: str | None = None,
        model: str | None = None,
        temperature: float = 0.7,
    ):
        self.provider = (
            provider
            or os.getenv("LLM_PROVIDER", "ollama")
        ).lower()

        if self.provider == "gemini":
            self.model = (
                model
                or os.getenv(
                    "GEMINI_MODEL",
                    "gemini-3.8-flash",
                )
            )

        elif self.provider == "ollama":
            self.model = (
                model
                or os.getenv(
                    "OLLAMA_MODEL",
                    "llama3.2",
                )
            )

        else:
            raise ValueError(
                f"Unsupported provider: {self.provider}"
            )

        self.temperature = temperature

    def generate(
        self,
        system: str,
        prompt: str,
    ) -> str:
        """Generate a response from the configured LLM."""

        if self.provider == "ollama":
            return self._ollama_generate(
                system,
                prompt,
            )

        if self.provider == "gemini":
            return self._gemini_generate(
                system,
                prompt,
            )

        raise ValueError(
            f"Unsupported provider: {self.provider}"
        )

    def _ollama_generate(
        self,
        system: str,
        prompt: str,
    ) -> str:
        """Send the prompt to the local Ollama server."""

        host = os.getenv(
            "OLLAMA_HOST",
            "http://localhost:11434",
        ).rstrip("/")

        response = requests.post(
            f"{host}/api/chat",
            json={
                "model": self.model,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                },
                "messages": [
                    {
                        "role": "system",
                        "content": system,
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
            },
            timeout=300,
        )

        response.raise_for_status()

        data = response.json()

        return data["message"]["content"].strip()

    def _gemini_generate(
        self,
        system: str,
        prompt: str,
    ) -> str:
        """Generate a response using Google Gemini."""

        from google import genai
        from google.genai import types

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        client = genai.Client(
            api_key=api_key,
        )

        response = client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system,
                temperature=self.temperature,
            ),
        )

        if not response.text:
            raise ValueError(
                "Gemini returned an empty response."
            )

        return response.text.strip()


class Proponent:
    """Agent that argues in favor of the case."""

    def __init__(self, client: LLMClient):
        self.client = client

    def respond(
        self,
        case: str,
        transcript: list,
        current_round: int,
        max_rounds: int,
    ) -> str:

        previous = format_transcript(transcript)

        system = """
You are the Proponent in a formal AI Debate Court.

Your job is to argue IN FAVOR of the case.

Rules:
- Give clear and logical arguments.
- Use reasoning and evidence where appropriate.
- Respond to important points from the opponent.
- Do not invent specific facts or statistics.
- Be professional and concise.
"""

        prompt = f"""
Case:
{case}

Current round:
{current_round} of {max_rounds}

Previous debate:
{previous}

Give the Proponent's argument for this round.
"""

        return self.client.generate(
            system,
            prompt,
        )


class Opponent:
    """Agent that argues against the case."""

    def __init__(self, client: LLMClient):
        self.client = client

    def respond(
        self,
        case: str,
        transcript: list,
        current_round: int,
        max_rounds: int,
    ) -> str:

        previous = format_transcript(transcript)

        system = """
You are the Opponent in a formal AI Debate Court.

Your job is to argue AGAINST the case.

Rules:
- Challenge the Proponent's reasoning.
- Identify weaknesses, risks and disadvantages.
- Give logical counterarguments.
- Do not invent specific facts or statistics.
- Be professional and concise.
"""

        prompt = f"""
Case:
{case}

Current round:
{current_round} of {max_rounds}

Previous debate:
{previous}

Give the Opponent's counterargument for this round.
"""

        return self.client.generate(
            system,
            prompt,
        )


class Judge:
    """Agent that evaluates both sides and gives a verdict."""

    def __init__(self, client: LLMClient):
        self.client = client

    def rule(
        self,
        case: str,
        transcript: list,
    ) -> dict:

        debate = format_transcript(transcript)

        system = """
You are the Judge of a formal AI Debate Court.

Evaluate both sides fairly.

Return your answer in exactly this format:

VERDICT: <Proponent or Opponent>
SCORE: <number from 0 to 100>
REASONING: <short explanation>
WINNING_ARGUMENT: <short explanation>

Rules:
- Judge based on logic.
- Judge based on evidence.
- Judge based on clarity.
- Judge based on rebuttals.
- Do not favor either side without reasoning.
"""

        prompt = f"""
Case:
{case}

Full debate transcript:
{debate}

Give the final verdict.
"""

        result = self.client.generate(
            system,
            prompt,
        )

        return parse_verdict(result)


def format_transcript(transcript: list) -> str:
    """Convert the debate transcript into readable text."""

    if not transcript:
        return "No previous arguments."

    lines = []

    for item in transcript:
        speaker = item.get(
            "speaker",
            "Unknown",
        )

        round_number = item.get(
            "round",
            "?",
        )

        text = item.get(
            "text",
            "",
        )

        lines.append(
            f"Round {round_number} - {speaker}:\n{text}"
        )

    return "\n\n".join(lines)


def parse_verdict(text: str) -> dict:
    """Convert the Judge response into a dictionary."""

    verdict = "Undecided"
    score = 50
    reasoning = text
    winning_argument = ""

    for line in text.splitlines():

        clean = line.strip()
        upper = clean.upper()

        if upper.startswith("VERDICT:"):

            value = clean.split(
                ":",
                1,
            )[1].strip()

            if "PROPONENT" in value.upper():
                verdict = "Proponent"

            elif "OPPONENT" in value.upper():
                verdict = "Opponent"

        elif upper.startswith("SCORE:"):

            value = clean.split(
                ":",
                1,
            )[1].strip()

            try:
                score = int(
                    float(value)
                )

                score = max(
                    0,
                    min(
                        100,
                        score,
                    ),
                )

            except ValueError:
                score = 50

        elif upper.startswith("REASONING:"):

            reasoning = clean.split(
                ":",
                1,
            )[1].strip()

        elif upper.startswith(
            "WINNING_ARGUMENT:"
        ):

            winning_argument = clean.split(
                ":",
                1,
            )[1].strip()

    return {
        "verdict": verdict,
        "score": score,
        "reasoning": reasoning,
        "winning_argument": winning_argument,
        "raw": text,
    }


def build_agents(
    provider: str | None = None,
    model: str | None = None,
    temperature: float = 0.7,
):
    """Create the three Debate Court agents."""

    client = LLMClient(
        provider=provider,
        model=model,
        temperature=temperature,
    )

    proponent = Proponent(client)
    opponent = Opponent(client)
    judge = Judge(client)

    return (
        proponent,
        opponent,
        judge,
    )
