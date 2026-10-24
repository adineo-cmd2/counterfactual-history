"""Branching: a new session whose chain diverges from a parent step."""

from app.services import causal_chain_builder as ccb


def _end_year(year_range: str) -> int:
    try:
        return int((year_range or "").split("-")[1])
    except (IndexError, ValueError):
        return 0


def fork(parent_steps: list, step_key: str, new_premise: str,
         gens: int = 5) -> tuple:
    """Return (steps, edges, label) for the child timeline.

    The child chain starts at the parent step's end year; its first event
    states the branch supposition explicitly.
    """
    parent = next((s for s in parent_steps if s.get("key") == step_key), None)
    if parent is None:
        raise ValueError("step not found")
    year = _end_year(parent.get("year_range", ""))
    seed = (
        f"Given '{ccb._short(parent.get('event', ''), 60)}', "
        f"suppose {new_premise.strip()}"
    )
    steps, edges = ccb.build(new_premise, year, seed_override=seed, gens=gens)
    label = f"branch from {parent.get('domain')}@{parent.get('year_range')}"
    return steps, edges, label
