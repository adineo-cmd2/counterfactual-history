"""Persist a generated chain as session + steps + edges."""

from app.models.simulation_session import SimulationSession
from app.models.sim_step import SimStep
from app.models.sim_edge import SimEdge
from app.models.branch_node import BranchNode
from app.services import causal_chain_builder as ccb


def run_simulation(db, user_id: int, premise: str, year: int,
                   domains: list | None = None,
                   parent_session_id: int | None = None,
                   branch_from_step_id: int | None = None,
                   branch_note: str = "") -> dict:
    steps, edges = ccb.build(premise, int(year), domains)
    session = SimulationSession(
        user_id=user_id, premise=premise, divergence_year=int(year),
        parent_session_id=parent_session_id,
        branch_from_step_id=branch_from_step_id, branch_note=branch_note or "",
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    id_by_key: dict = {}
    for s in steps:
        row = SimStep(session_id=session.id, gen=s["gen"], idx=s["idx"],
                      domain=s["domain"], year_range=s["year_range"],
                      event=s["event"], probability=s["probability"],
                      analogy=s["historical_analogy"])
        db.add(row)
        db.commit()
        db.refresh(row)
        id_by_key[s["key"]] = row.id
    for e in edges:
        db.add(SimEdge(session_id=session.id,
                       from_step_id=id_by_key[e["from_key"]],
                       to_step_id=id_by_key[e["to_key"]]))
    db.commit()
    return {"session_id": session.id, "steps": len(steps)}
