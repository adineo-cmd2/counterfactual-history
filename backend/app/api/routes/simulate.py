from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.simulation_session import SimulationSession
from app.models.sim_step import SimStep
from app.models.sim_edge import SimEdge
from app.models.branch_node import BranchNode
from app.schemas.simulate import SimulateStartIn, BranchIn
from app.services import causal_chain_builder as ccb
from app.services import branch_manager
from app.services import timeline_comparator
from app.services import simulation_pipeline as pipeline

router = APIRouter()


def _own(db: Session, user: User, sid: int) -> SimulationSession:
    s = db.query(SimulationSession).filter(
        SimulationSession.id == sid, SimulationSession.user_id == user.id
    ).first()
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    return s


def _step_dicts(db: Session, sid: int) -> list:
    rows = db.query(SimStep).filter(SimStep.session_id == sid).order_by(SimStep.gen, SimStep.idx).all()
    return [{"key": f"s{r.id}", "id": r.id, "gen": r.gen, "domain": r.domain,
             "year_range": r.year_range, "event": r.event,
             "probability": r.probability, "analogy": r.analogy} for r in rows]


@router.post("/start")
def start(body: SimulateStartIn, db: Session = Depends(get_db),
          user: User = Depends(get_current_user)):
    if not body.premise.strip():
        raise HTTPException(status_code=400, detail="Premise required")
    domains = [d for d in body.domains if d in ccb.DOMAINS] or None
    premise = body.premise.strip()
    if body.initial_conditions.strip():
        premise = f"{premise} [{body.initial_conditions.strip()}]"
    out = pipeline.run_simulation(db, user.id, premise, int(body.divergence_year), domains)
    return {"session_id": out["session_id"], "steps": out["steps"]}


@router.get("/{sid}/timeline")
def timeline(sid: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _own(db, user, sid)
    steps = db.query(SimStep).filter(SimStep.session_id == sid).order_by(SimStep.gen, SimStep.idx).all()
    edges = db.query(SimEdge).filter(SimEdge.session_id == sid).all()
    return {"session_id": sid,
            "steps": [{"id": r.id, "gen": r.gen, "domain": r.domain,
                       "year_range": r.year_range, "event": r.event,
                       "probability": r.probability, "analogy": r.analogy} for r in steps],
            "edges": [{"from": e.from_step_id, "to": e.to_step_id} for e in edges]}


@router.post("/{sid}/branch")
def branch(sid: int, body: BranchIn, db: Session = Depends(get_db),
           user: User = Depends(get_current_user)):
    parent = _own(db, user, sid)
    if not body.premise.strip():
        raise HTTPException(status_code=400, detail="Branch premise required")
    step = db.query(SimStep).filter(SimStep.id == body.step_id,
                                    SimStep.session_id == sid).first()
    if not step:
        raise HTTPException(status_code=404, detail="Step not found in session")
    steps = _step_dicts(db, sid)
    child_steps, child_edges, label = branch_manager.fork(
        steps, f"s{step.id}", body.premise.strip())
    out = pipeline.run_simulation(
        db, user.id, f"Branch of #{sid}: {body.premise.strip()}",
        int(child_steps[0]["year_range"].split("-")[0]),
        parent_session_id=parent.id, branch_from_step_id=step.id,
        branch_note=body.premise.strip(),
    )
    # Persist the forked chain shape (regenerate deterministically from branch year)
    # run_simulation already built from the same premise/year; swap in forked events:
    rows = db.query(SimStep).filter(SimStep.session_id == out["session_id"]).order_by(
        SimStep.gen, SimStep.idx).all()
    if len(rows) == len(child_steps):
        for row, cs in zip(rows, sorted(child_steps, key=lambda s: (s["gen"], s["idx"]))):
            row.event = cs["event"]
            row.probability = cs["probability"]
            row.analogy = cs["historical_analogy"]
            row.year_range = cs["year_range"]
            row.domain = cs["domain"]
            row.gen = cs["gen"]
        db.commit()
    db.add(BranchNode(session_id=sid, step_id=step.id,
                      child_session_id=out["session_id"], label=label))
    db.commit()
    return {"child_session_id": out["session_id"]}


@router.get("/{sid}/domain/{domain}")
def domain_view(sid: int, domain: str, db: Session = Depends(get_db),
                user: User = Depends(get_current_user)):
    _own(db, user, sid)
    if domain not in ccb.DOMAINS:
        raise HTTPException(status_code=400, detail="Unknown domain")
    rows = db.query(SimStep).filter(SimStep.session_id == sid,
                                    SimStep.domain == domain).order_by(SimStep.gen).all()
    parts = [f"In {r.year_range}, {r.event} Likelihood: {r.probability}. "
             f"Echoes {r.analogy}" for r in rows]
    narrative = (f"How {domain.lower()} unfolds after the divergence. "
                 "All below is speculative fiction. " + " ".join(parts))
    return {"domain": domain, "narrative": narrative,
            "steps": [{"year_range": r.year_range, "event": r.event,
                       "probability": r.probability} for r in rows]}


@router.get("/compare")
def compare(a: int, b: int, db: Session = Depends(get_db),
            user: User = Depends(get_current_user)):
    _own(db, user, a)
    _own(db, user, b)
    rows = timeline_comparator.compare(_step_dicts(db, a), _step_dicts(db, b))
    return {"a": a, "b": b, "rows": rows}


@router.get("/library")
def library(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    out = []
    for s in db.query(SimulationSession).filter(
            SimulationSession.user_id == user.id).order_by(SimulationSession.id).all():
        branches = db.query(SimulationSession).filter(
            SimulationSession.parent_session_id == s.id).count()
        out.append({"id": s.id, "premise": s.premise,
                    "divergence_year": s.divergence_year,
                    "branches": branches,
                    "parent_session_id": s.parent_session_id})
    return out


def _delete_session(db: Session, sid: int):
    db.query(BranchNode).filter(
        (BranchNode.session_id == sid) | (BranchNode.child_session_id == sid)
    ).delete(synchronize_session=False)
    db.query(SimEdge).filter(SimEdge.session_id == sid).delete()
    db.query(SimStep).filter(SimStep.session_id == sid).delete()
    db.query(SimulationSession).filter(SimulationSession.id == sid).delete()


@router.delete("/{sid}")
def delete(sid: int, force: bool = False, db: Session = Depends(get_db),
           user: User = Depends(get_current_user)):
    _own(db, user, sid)
    kids = db.query(SimulationSession).filter(
        SimulationSession.parent_session_id == sid,
        SimulationSession.user_id == user.id).all()
    if kids and not force:
        raise HTTPException(status_code=409, detail="Session has branches; use force=true")
    for k in kids:
        _delete_session(db, k.id)
    _delete_session(db, sid)
    db.commit()
    return {"deleted": sid}
