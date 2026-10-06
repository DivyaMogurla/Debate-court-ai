"""LangGraph workflow: Proponent -> Opponent -> repeat -> Judge."""

from __future__ import annotations

import operator
from typing import Annotated, Any, Iterator, TypedDict

from langgraph.graph import END, StateGraph

from agents import build_agents


class CourtState(TypedDict):
    case: str
    max_rounds: int
    round: int
    transcript: Annotated[list, operator.add]
    verdict: dict


def build_graph(
    provider: str | None = None,
    model: str | None = None,
    temperature: float = 0.7,
):
    """Build and compile the Debate Court graph."""

    proponent, opponent, judge = build_agents(
        provider,
        model,
        temperature,
    )

    def proponent_node(state: CourtState) -> dict:
        text = proponent.respond(
            state["case"],
            state["transcript"],
            state["round"],
            state["max_rounds"],
        )

        return {
            "transcript": [
                {
                    "round": state["round"],
                    "speaker": "Proponent",
                    "text": text,
                }
            ]
        }

    def opponent_node(state: CourtState) -> dict:
        text = opponent.respond(
            state["case"],
            state["transcript"],
            state["round"],
            state["max_rounds"],
        )

        return {
            "transcript": [
                {
                    "round": state["round"],
                    "speaker": "Opponent",
                    "text": text,
                }
            ],
            "round": state["round"] + 1,
        }

    def judge_node(state: CourtState) -> dict:
        verdict = judge.rule(
            state["case"],
            state["transcript"],
        )

        return {
            "verdict": verdict
        }

    def should_continue(state: CourtState) -> str:
        if state["round"] <= state["max_rounds"]:
            return "proponent"

        return "judge"

    graph = StateGraph(CourtState)

    graph.add_node("proponent", proponent_node)
    graph.add_node("opponent", opponent_node)
    graph.add_node("judge", judge_node)

    graph.set_entry_point("proponent")

    graph.add_edge(
        "proponent",
        "opponent",
    )

    graph.add_conditional_edges(
        "opponent",
        should_continue,
        {
            "proponent": "proponent",
            "judge": "judge",
        },
    )

    graph.add_edge(
        "judge",
        END,
    )

    return graph.compile()


def run_debate(
    case: str,
    rounds: int = 2,
    provider: str | None = None,
    model: str | None = None,
    temperature: float = 0.7,
) -> Iterator[dict[str, Any]]:
    """Run the debate and yield updates from each node."""

    graph = build_graph(
        provider,
        model,
        temperature,
    )

    initial: CourtState = {
        "case": case,
        "max_rounds": rounds,
        "round": 1,
        "transcript": [],
        "verdict": {},
    }

    for update in graph.stream(
        initial,
        stream_mode="updates",
        config={
            "recursion_limit": 4 * rounds + 10
        },
    ):
        for node, data in update.items():
            yield {
                "node": node,
                "data": data,
            }