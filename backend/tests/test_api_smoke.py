from fastapi.testclient import TestClient

from app.main import app


def test_full_chain():
    c = TestClient(app)
    assert c.get("/healthz").json() == {"ok": True}
    r = c.post("/api/simulate/start",
               json={"premise": "the printing press was never invented",
                     "divergence_year": 1440})
    assert r.status_code == 200
    sid = r.json()["session_id"]
    assert r.json()["steps"] >= 5
    r = c.get(f"/api/simulate/{sid}/timeline")
    assert r.status_code == 200
    steps = r.json()["steps"]
    assert sorted({s["gen"] for s in steps}) == [0, 1, 2, 3, 4]
    assert {s["domain"] for s in steps if s["gen"] == 0} == {
        "Politics", "Religion", "Science", "Culture", "Economics"}
    assert {s["probability"] for s in steps} <= {"high", "medium", "speculative"}
    target = next(s for s in steps if s["gen"] == 2)
    r = c.post(f"/api/simulate/{sid}/branch",
               json={"step_id": target["id"], "premise": "paper stays cheap"})
    assert r.status_code == 200
    kid = r.json()["child_session_id"]
    assert kid != sid
    r = c.get(f"/api/simulate/{sid}/domain/Science")
    assert r.status_code == 200 and "speculative fiction" in r.json()["narrative"]
    r = c.get(f"/api/simulate/compare?a={sid}&b={kid}")
    assert r.status_code == 200 and len(r.json()["rows"]) > 0
    r = c.get("/api/simulate/library")
    assert any(s["id"] == sid and s["branches"] >= 1 for s in r.json())
    r = c.delete(f"/api/simulate/{sid}")
    assert r.status_code == 409
    r = c.delete(f"/api/simulate/{sid}?force=true")
    assert r.status_code == 200
