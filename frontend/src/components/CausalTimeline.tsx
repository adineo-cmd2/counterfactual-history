import { useEffect, useState } from 'react';
import { apiGet, apiPost } from '../lib/apiClient';
const BASE = (import.meta.env.BASE_URL ?? '/').replace(/\/$/, '');

interface Step {
  id: number;
  gen: number;
  domain: string;
  year_range: string;
  event: string;
  probability: 'high' | 'medium' | 'speculative' | string;
  analogy: string;
}

const DOMAIN_COLORS: Record<string, string> = {
  Politics: 'bg-red-100 text-red-900 border-red-300',
  Religion: 'bg-amber-100 text-amber-900 border-amber-300',
  Science: 'bg-sky-100 text-sky-900 border-sky-300',
  Culture: 'bg-violet-100 text-violet-900 border-violet-300',
  Economics: 'bg-emerald-100 text-emerald-900 border-emerald-300',
};

function probPill(prob: string): string {
  if (prob === 'high') return 'bg-green-700 text-white';
  if (prob === 'medium') return 'bg-amber-600 text-white';
  return 'bg-stone-500 text-white';
}

export default function CausalTimeline({ sessionId }: { sessionId: string }) {
  const [steps, setSteps] = useState<Step[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [domain, setDomain] = useState('All');
  const [narrative, setNarrative] = useState('');
  const [branching, setBranching] = useState<number | null>(null);

  useEffect(() => {
    if (!sessionId) {
      setLoading(false);
      return;
    }
    let cancelled = false;
    (async () => {
      try {
        const data = await apiGet(`/api/simulate/${sessionId}/timeline`);
        if (!cancelled) setSteps(data.steps ?? []);
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Load failed.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [sessionId]);

  async function loadDomain(d: string) {
    setDomain(d);
    if (d === 'All') {
      setNarrative('');
      return;
    }
    try {
      const data = await apiGet(`/api/simulate/${sessionId}/domain/${d}`);
      setNarrative(data.narrative ?? '');
    } catch (e) {
      setNarrative(e instanceof Error ? e.message : 'Domain load failed.');
    }
  }

  async function branchHere(stepId: number) {
    const premise = window.prompt('Branch premise — suppose what instead?');
    if (!premise || !premise.trim()) return;
    setBranching(stepId);
    try {
      const r = (await apiPost(`/api/simulate/${sessionId}/branch`, {
        step_id: stepId,
        premise: premise.trim(),
      })) as { child_session_id: number };
      window.location.href = `${BASE}/timeline?sid=${r.child_session_id}`;
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Branch failed.');
      setBranching(null);
    }
  }

  if (!sessionId) return <p className="text-sm">Missing ?sid=. Start a simulation first.</p>;
  if (loading) return <p className="text-sm">Loading timeline…</p>;

  const visible = domain === 'All' ? steps : steps.filter((s) => s.domain === domain);
  const gens = [...new Set(visible.map((s) => s.gen))].sort((a, b) => a - b);

  return (
    <div>
      {error && <p className="mb-3 border border-blood px-2 py-1 text-sm text-blood">{error}</p>}
      <div className="mb-4 flex flex-wrap items-center gap-2">
        {['All', 'Politics', 'Religion', 'Science', 'Culture', 'Economics'].map((d) => (
          <button
            key={d}
            onClick={() => void loadDomain(d)}
            className={`border px-2 py-1 text-xs ${domain === d ? 'border-blood text-blood' : 'border-parchment-line text-bark'}`}
          >
            {d}
          </button>
        ))}
      </div>
      {narrative && (
        <p className="display-serif mb-4 border border-parchment-line bg-parchment-dark p-3 text-sm italic">
          {narrative}
        </p>
      )}
      {gens.map((g) => (
        <section key={g} className="mb-6">
          <h3 className="display-serif mb-2 text-lg font-bold">Generation {g}</h3>
          <div className="grid gap-3 md:grid-cols-2">
            {visible
              .filter((s) => s.gen === g)
              .map((s) => (
                <article key={s.id} className="border border-parchment-line bg-white/60 p-3">
                  <div className="flex flex-wrap items-center gap-2">
                    <span
                      className={`border px-2 py-0.5 text-xs font-bold ${DOMAIN_COLORS[s.domain] ?? 'border-stone-300 bg-stone-100 text-stone-800'}`}
                    >
                      {s.domain}
                    </span>
                    <span className={`rounded-full px-2 py-0.5 text-xs ${probPill(s.probability)}`}>
                      {s.probability}
                    </span>
                    <span className="text-xs text-bark-soft">{s.year_range}</span>
                  </div>
                  <p className="mt-2 text-sm">{s.event}</p>
                  <p className="mt-1 text-xs italic text-bark-soft">Echoes {s.analogy}</p>
                  <button
                    onClick={() => void branchHere(s.id)}
                    disabled={branching === s.id}
                    className="mt-2 border border-blood px-2 py-1 text-xs text-blood hover:bg-blood hover:text-white disabled:opacity-50"
                  >
                    {branching === s.id ? 'Branching…' : 'Branch here'}
                  </button>
                </article>
              ))}
          </div>
        </section>
      ))}
      {visible.length === 0 && !loading && <p className="text-sm">No steps for this filter.</p>}
    </div>
  );
}
