"""Template causal-chain builder. Deterministic, offline, mock-first.

An LLM hook (``_llm_rewrite``) replaces template text when API keys are
present; otherwise templates are used verbatim.
"""

import os
import re

DOMAINS = ["Politics", "Religion", "Science", "Culture", "Economics"]
YEAR_STEPS = [8, 12, 15, 20, 25]
GEN_PROB = ["high", "high", "medium", "medium", "speculative"]

_STOP = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with",
    "was", "were", "is", "are", "be", "been", "never", "ever", "what", "if",
    "had", "has", "have", "not", "no", "it", "its",
}

GEN0_TEMPLATES = {
    "Politics": (
        "Rulers scramble as '{subject}' upends the old order; {faction} "
        "seizes the new levers of power.",
        "Analogy: the fall of bronze-age palace economies.",
    ),
    "Religion": (
        "Priests declare '{subject}' a sign; {faction} splits over its meaning.",
        "Analogy: the Reformation pamphlet wars.",
    ),
    "Science": (
        "Scholars race to explain '{subject}'; {faction} founds a new school of inquiry.",
        "Analogy: the longitude prize contests.",
    ),
    "Culture": (
        "Songs and stories obsess over '{subject}'; {faction} makes it fashion.",
        "Analogy: the 19th-century railway novel boom.",
    ),
    "Economics": (
        "Markets reprice everything around '{subject}'; {faction} corners the new trade.",
        "Analogy: the Dutch tulip mania repricing.",
    ),
}

CHILD_TEMPLATES = [
    (
        "Because '{cause}', {faction} pushes further and triggers backlash.",
        "Analogy: prohibition-era blowback.",
    ),
    (
        "The aftershock of '{cause}' redraws alliances; {faction} benefits most.",
        "Analogy: post-plague labour bargains.",
    ),
    (
        "'{cause}' becomes doctrine; {faction} enforces the new orthodoxy.",
        "Analogy: the inquisition printing licences.",
    ),
]

FACTIONS = ["river cities", "hill clans", "guild leagues", "temple orders", "port princes"]


def keywords(premise: str) -> list:
    words = re.findall(r"[A-Za-z]{5,}", (premise or "").lower())
    seen, out = set(), []
    for w in words:
        if w not in _STOP and w not in seen:
            seen.add(w)
            out.append(w)
    return out


def _subject(premise: str) -> str:
    kws = keywords(premise)
    if kws:
        return " ".join(kws[:3])
    return (premise or "the change").strip()[:60]


def _short(text: str, n: int = 48) -> str:
    t = " ".join((text or "").split())
    return t if len(t) <= n else t[:n].rstrip() + "…"


def _llm_rewrite(premise: str, steps: list) -> list:
    if not (os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")):
        return steps
    # Real LLM rewrite lives here; v1 keeps templates even with keys
    # so output stays deterministic and testable.
    return steps


def build(premise: str, year: int, domains: list | None = None,
          seed_override: str | None = None, gens: int = 5) -> tuple:
    """Return (steps, edges). Steps are dicts with a temp `_key`.

    Step dict: {key, gen, idx, domain, year_range, event, probability,
    historical_analogy, caused_by[]}. Edge dict: {from_key, to_key}.
    """
    domains = [d for d in (domains or DOMAINS) if d in DOMAINS] or list(DOMAINS)
    subject = _subject(premise)
    steps, edges = [], []
    cursor = int(year)
    prev_keys: list = []
    idx = 0
    for g in range(max(int(gens), 1)):
        span = YEAR_STEPS[g] if g < len(YEAR_STEPS) else 25
        year_range = f"{cursor}-{cursor + span}"
        prob = GEN_PROB[g] if g < len(GEN_PROB) else "speculative"
        if g == 0:
            for di, domain in enumerate(domains):
                tmpl, analogy = GEN0_TEMPLATES[domain]
                if seed_override and di == 0:
                    event = seed_override
                else:
                    event = tmpl.format(
                        subject=subject,
                        faction=FACTIONS[(di + g) % len(FACTIONS)],
                    )
                key = f"g{g}n{di}"
                steps.append({"key": key, "gen": g, "idx": idx, "domain": domain,
                              "year_range": year_range, "event": event,
                              "probability": prob, "historical_analogy": analogy,
                              "caused_by": []})
                prev_keys.append(key)
                idx += 1
        else:
            new_keys = []
            for pi, pkey in enumerate(prev_keys):
                parent = next(s for s in steps if s["key"] == pkey)
                domain = DOMAINS[(DOMAINS.index(parent["domain"]) + 1) % len(DOMAINS)]
                tmpl, analogy = CHILD_TEMPLATES[(pi + g) % len(CHILD_TEMPLATES)]
                event = tmpl.format(
                    cause=_short(parent["event"]),
                    faction=FACTIONS[(pi + g) % len(FACTIONS)],
                )
                key = f"g{g}n{pi}"
                steps.append({"key": key, "gen": g, "idx": idx, "domain": domain,
                              "year_range": year_range, "event": event,
                              "probability": prob, "historical_analogy": analogy,
                              "caused_by": [pkey]})
                edges.append({"from_key": pkey, "to_key": key})
                new_keys.append(key)
                idx += 1
            prev_keys = new_keys
        cursor += span
    return _llm_rewrite(premise, steps), edges
