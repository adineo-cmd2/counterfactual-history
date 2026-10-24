"""Timeline comparison by generation index."""

import re

_WORD = re.compile(r"[a-z]{4,}")


def _tokens(text: str) -> set:
    return set(_WORD.findall((text or "").lower()))


def _similar(a: str, b: str) -> float:
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def compare(a_steps: list, b_steps: list, threshold: float = 0.6) -> list:
    """Align by generation; rows: {gen, year_range, domain, a, b, status}.

    Status: shared | diverged | only_a | only_b.
    """
    from collections import defaultdict

    def by_gen(steps):
        d: dict = defaultdict(list)
        for s in steps:
            d[s.get("gen", 0)].append(s)
        for g in d:
            d[g].sort(key=lambda s: s.get("domain", ""))
        return d

    ag, bg = by_gen(a_steps), by_gen(b_steps)
    rows = []
    for g in sorted(set(ag) | set(bg)):
        la, lb = ag.get(g, []), bg.get(g, [])
        # pair same-domain first, then leftovers
        used_b = set()
        for sa in la:
            match = None
            for j, sb in enumerate(lb):
                if j in used_b or sb.get("domain") != sa.get("domain"):
                    continue
                match = sb
                used_b = used_b | {j}
                break
            if match is None:
                rows.append({"gen": g, "year_range": sa.get("year_range"),
                             "domain": sa.get("domain"), "a": sa.get("event"),
                             "b": None, "status": "only_a"})
            else:
                sim = _similar(sa.get("event", ""), match.get("event", ""))
                rows.append({"gen": g, "year_range": sa.get("year_range"),
                             "domain": sa.get("domain"), "a": sa.get("event"),
                             "b": match.get("event"),
                             "status": "shared" if sim >= threshold else "diverged"})
        for j, sb in enumerate(lb):
            if j not in used_b:
                rows.append({"gen": g, "year_range": sb.get("year_range"),
                             "domain": sb.get("domain"), "a": None,
                             "b": sb.get("event"), "status": "only_b"})
    return rows
