import { useEffect, useState } from 'react';
import { apiGet } from '../../lib/apiClient';
const BASE = (import.meta.env.BASE_URL ?? '/').replace(/\/$/, '');

interface Sim {
  id: number;
  premise: string;
  divergence_year: number;
  branches: number;
  parent_session_id: number | null;
}

// Dependency-free collapsible tree (offline-safe).
export default function BranchTree() {
  const [sims, setSims] = useState<Sim[]>([]);
  const [collapsed, setCollapsed] = useState<Record<number, boolean>>({});

  useEffect(() => {
    apiGet('/api/simulate/library').then((d) => setSims(Array.isArray(d) ? d : []));
  }, []);

  const kids = new Map<number | null, Sim[]>();
  for (const s of sims) {
    const k = s.parent_session_id ?? null;
    if (!kids.has(k)) kids.set(k, []);
    kids.get(k)!.push(s);
  }

  function render(id: number | null, depth: number): React.ReactNode {
    return (kids.get(id) ?? []).map((s) => (
      <div key={s.id}>
        <div className="flex items-center gap-2" style={{ marginLeft: depth * 24 }}>
          {kids.has(s.id) && (
            <button className="mono-n w-5 border border-agedbrown/40" onClick={() => setCollapsed((c) => ({ ...c, [s.id]: !c[s.id] }))}>
              {collapsed[s.id] ? '+' : '−'}
            </button>
          )}
          <button className="underline" onClick={() => { window.location.href = `${BASE}/timeline?sid=${s.id}`; }}>
            #{s.id} {s.premise.slice(0, 60)}
          </button>
          <span className="text-xs opacity-60">({s.divergence_year})</span>
        </div>
        {!collapsed[s.id] && render(s.id, depth + 1)}
      </div>
    ));
  }

  if (!sims.length) return <p className="text-sm opacity-70">No simulations yet — start one first.</p>;
  return <div className="space-y-1">{render(null, 0)}</div>;
}
