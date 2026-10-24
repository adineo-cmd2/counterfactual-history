from app.db.session import Base, engine, SessionLocal
from app.models.user import User
from app.models.simulation_session import SimulationSession
from app.models.sim_step import SimStep
from app.models.sim_edge import SimEdge
from app.models.branch_node import BranchNode
from app.core.security import hash_password


def test_session_steps_edges_branch_link():
    # Explicit drop order: sessions<->steps form an FK cycle
    # (sessions.branch_from_step_id -> steps.id).
    for table in (BranchNode.__table__, SimEdge.__table__, SimStep.__table__,
                  SimulationSession.__table__, User.__table__):
        table.drop(bind=engine, checkfirst=True)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    u = User(email="t6@example.com", password_hash=hash_password("secret123"))
    db.add(u)
    db.commit()
    db.refresh(u)
    s = SimulationSession(user_id=u.id, premise="No printing press", divergence_year=1440)
    db.add(s)
    db.commit()
    db.refresh(s)
    a = SimStep(session_id=s.id, gen=0, idx=0, domain="Politics",
                year_range="1440-1448", event="Scribes keep power.",
                probability="high", analogy="Manuscript culture persisted.")
    b = SimStep(session_id=s.id, gen=1, idx=1, domain="Science",
                year_range="1448-1460", event="Slow copying stalls ideas.",
                probability="medium", analogy="Late manuscript era.")
    db.add_all([a, b])
    db.commit()
    db.refresh(a)
    db.refresh(b)
    db.add(SimEdge(session_id=s.id, from_step_id=a.id, to_step_id=b.id))
    child = SimulationSession(user_id=u.id, premise="child", divergence_year=1460,
                              parent_session_id=s.id, branch_from_step_id=b.id,
                              branch_note="what if paper cheap?")
    db.add(child)
    db.commit()
    db.refresh(child)
    db.add(BranchNode(session_id=s.id, step_id=b.id, child_session_id=child.id,
                      label="cheap paper"))
    db.commit()
    assert db.query(SimStep).filter_by(session_id=s.id).count() == 2
    assert db.query(SimEdge).filter_by(session_id=s.id).count() == 1
    assert db.query(BranchNode).filter_by(session_id=s.id).count() == 1
    assert child.parent_session_id == s.id
    db.close()
