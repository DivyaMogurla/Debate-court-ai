
"""Streamlit UI for Debate Court."""

import json

import streamlit as st

from workflow import run_debate


st.set_page_config(
    page_title="Debate Court",
    page_icon="⚖️",
    layout="wide",
)


st.title("⚖️ Debate Court")

st.caption(
    "Multi-Agent AI Decision Support System: "
    "a Proponent, an Opponent and a Judge debate your decision."
)


with st.sidebar:
    st.header("Settings")

    provider = st.selectbox(
        "LLM Provider",
        ["gemini", "ollama"],
    )

    if provider == "gemini":
        st.info("LLM Provider: Gemini")

        # Fixed Gemini model
        model = st.text_input(
            "Gemini Model",
            value="gemini-3.5-flash-lite",
        )

    else:
        st.info("LLM Provider: Ollama")

        model = st.text_input(
            "Ollama Model",
            value="llama3.2",
        )

        st.markdown(
            "Ollama is running locally on your computer."
        )

    rounds = st.slider(
        "Debate rounds",
        1,
        4,
        2,
    )

    temperature = st.slider(
        "Creativity",
        0.0,
        1.0,
        0.7,
        0.1,
    )


EXAMPLES = {
    "Custom": "",
    "Career": (
        "Should I leave my stable job to join "
        "an early-stage AI startup?"
    ),
    "Business": (
        "Should our company switch its whole backend "
        "from a monolith to microservices?"
    ),
    "Education": (
        "Should I pursue a master's degree abroad "
        "or start working right after graduation?"
    ),
}


choice = st.selectbox(
    "Example cases",
    list(EXAMPLES),
)


case = st.text_area(
    "Describe the decision or proposal",
    value=EXAMPLES[choice],
    height=120,
    placeholder=(
        "Include context: goals, constraints, "
        "budget, timeline..."
    ),
)


if st.button(
    "Start Trial",
    type="primary",
    disabled=not case.strip(),
):

    transcript = []
    verdict = {}

    try:

        with st.status(
            "Court is in session...",
            expanded=True,
        ) as status:

            for step in run_debate(
                case.strip(),
                rounds,
                provider,
                model,
                temperature,
            ):

                node = step["node"]
                data = step["data"]

                if node in (
                    "proponent",
                    "opponent",
                ):

                    turn = data["transcript"][0]

                    transcript.append(turn)

                    if node == "proponent":
                        icon = "🟢"
                    else:
                        icon = "🔴"

                    with st.chat_message(
                        "user"
                        if node == "proponent"
                        else "assistant",
                        avatar=icon,
                    ):

                        st.markdown(
                            f"**{turn['speaker']} "
                            f"(Round {turn['round']})**"
                        )

                        st.write(turn["text"])

                elif node == "judge":

                    verdict = data["verdict"]

            status.update(
                label="Verdict delivered",
                state="complete",
            )

    except Exception as e:

        st.error(
            f"Something went wrong: {e}"
        )

        st.stop()


    st.divider()

    st.subheader("🧑‍⚖️ Verdict")


    c1, c2 = st.columns(2)


    with c1:
        st.metric(
            "Decision",
            verdict.get(
                "verdict",
                "Undecided",
            ),
        )


    with c2:
        st.metric(
            "Score",
            f"{verdict.get('score', 50)}/100",
        )


    st.markdown("### Reasoning")

    st.write(
        verdict.get(
            "reasoning",
            "No reasoning available.",
        )
    )


    st.markdown("### 🏆 Winning Argument")

    st.write(
        verdict.get(
            "winning_argument",
            "No winning argument provided.",
        )
    )


    st.markdown("### 📜 Debate Transcript")


    for turn in transcript:

        speaker = turn.get(
            "speaker",
            "Unknown",
        )

        round_number = turn.get(
            "round",
            "?",
        )

        text = turn.get(
            "text",
            "",
        )

        if speaker == "Proponent":
            icon = "🟢"
        else:
            icon = "🔴"

        st.markdown(
            f"**{icon} {speaker} "
            f"(Round {round_number})**"
        )

        st.write(text)


    st.download_button(
        "Download Case File (JSON)",

        json.dumps(
            {
                "case": case,
                "transcript": transcript,
                "verdict": verdict,
            },
            indent=2,
        ),

        file_name="debate_court_case.json",

        mime="application/json",
    )

