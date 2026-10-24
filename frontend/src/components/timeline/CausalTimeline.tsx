import { useEffect, useState } from 'react';
import { apiGet, apiPost } from '../../lib/apiClient';

interface Step {
  id: number;
  gen: number;
  domain: string;
  year_range: string;
  event: string;
  probability: string;
  analogy: string;
}

const DOMAIN_COLORS: Record<string, string> = {
  Politics: 'bg-red-100 text-red-900',
  Religion: 'bg-amber-100 text-amber-900',
  Science: 'bg-sky-100 text-sky-900',
  Culture: 'bg-purple-100 text-purple-900',
  Economics: 'bg-green-100 text-green-900',
};

export default function CausalTimeline() {
  const [sid, setSid] = useState('');
  const [steps, setSteps] = useState<Step[]>([]);
  const [error, setError] = useState('');

  async function load(id: string) {
    if (!id) return;
    try {
      const data = await apiGet(`/api/simulate/${id}/timeline`);
      setSteps((data.steps ?? []) as Step[]);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load.');
    }
  }

  useEffect(() => {
    const q = new URLSearchParams(window.location.search).get('sid') ?? '';
    setSid(q);
    if (q) load(q);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function branchHere(stepId: number) {
    const premise = window.prompt('Branch supposition — what if, even here…?');
    if (!premise || !premise.trim()) return;
    try {
      const data = await apiPost(`/api/simulate/${sid}/branch`, {
        step_id: stepId,
        premise: premise.trim(),
      });
      window.location.href = `/timeline?sid=${data.child_session_id}`;
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Branch failed.');
    }
  }

  return (
    <div>
      <div className="flex gap-2">
        <input className="border border-agedbrown/40 bg-white px-2 py-1" value={sid} onChange={(e) => setSid(e.target.value)} placeholder="Session id" />
        <button className="border border-agedbrown/40 px-3 py-1" onClick={() => load(sid)}>Open</button>
      </div>
      {error && <p className="mt-2 text-sm text-deepred">{error}</p>}
      <div className="mt-4 space-y-3 border-l-2 border-agedbrown/40 pl-4">
        {steps.map((s) => (
          <div key={s.id} className="border border-agedbrown/30 bg-white p-3">
            <div className="flex flex-wrap items-center gap-2 text-xs">
              <span className="mono-n">{s.year_range}</span>
              <span className={`px-1 ${DOMAIN_COLORS[s.domain] ?? 'bg-stone-200'}`}>{s.domain}</span>
              <span className="border border-agedbrown/40 px-1" title="high: strong precedent · medium: plausible · speculative: thin evidence">{s.probability}</span>
            </div>
            <p className="display-serif mt-1">{s.event}</p>
            <p className="mt-1 text-xs opacity-70">Echoes {s.analogy}</p>
            <button className="mt-1 text-xs underline" onClick={() => branchHere(s.id)}>Branch here</button>
          </div>
        ))}
      </div>
    </div>
  );
}
