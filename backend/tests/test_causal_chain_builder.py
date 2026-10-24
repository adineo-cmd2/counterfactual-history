from app.services import causal_chain_builder as ccb
from app.services import branch_manager
from app.services import timeline_comparator


def _starts(year_range: str) -> int:
    return int((year_range or "0-0").split("-")[0])


def test_chain_shape_and_dag():
    steps, edges = ccb.build("the printing press was never invented", 1440)
    gens = sorted({s["gen"] for s in steps})
    assert gens == [0, 1, 2, 3, 4]
    assert {s["domain"] for s in steps if s["gen"] == 0} == set(ccb.DOMAINS)
    assert {s["probability"] for s in steps} <= {"high", "medium", "speculative"}
    # edges go forward in idx (DAG, no cycles possible by construction)
    by_key = {s["key"]: s for s in steps}
    for e in edges:
        assert by_key[e["from_key"]]["idx"] < by_key[e["to_key"]]["idx"]
        assert by_key[e["from_key"]]["gen"] + 1 == by_key[e["to_key"]]["gen"]
    # year ranges ascend along a chain path
    first = [s for s in steps if s["gen"] == 0][0]
    chain, cur = [first], first
    while True:
        nxt = [e for e in edges if e["from_key"] == cur["key"]]
        if not nxt:
            break
        cur = by_key[nxt[0]["to_key"]]
        chain.append(cur)
    starts = [_starts(s["year_range"]) for s in chain]
    assert starts == sorted(starts) and len(chain) == 5


def test_branch_fork_starts_at_step_year():
    steps, _ = ccb.build("the printing press was never invented", 1440)
    target = next(s for s in steps if s["gen"] == 2)
    child_steps, _, label = branch_manager.fork(steps, target["key"], "paper stays cheap")
    end_year = int(target["year_range"].split("-")[1])
    assert _starts(child_steps[0]["year_range"]) == end_year
    assert len({s["gen"] for s in child_steps}) == 5
    assert "paper stays cheap" in child_steps[0]["event"]
    assert "branch from" in label


def test_compare_shared_and_diverged():
    a, _ = ccb.build("the printing press was never invented", 1440)
    b, _ = ccb.build("the printing press was never invented", 1440)
    rows = timeline_comparator.compare(a, b)
    assert rows and all(r["status"] == "shared" for r in rows)
    c, _ = ccb.build("Rome never fell and steam engines rise early", 1400)
    rows2 = timeline_comparator.compare(a, c)
    assert any(r["status"] == "diverged" for r in rows2)
