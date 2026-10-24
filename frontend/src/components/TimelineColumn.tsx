import { useEffect, useState } from 'react';
import { apiGet } from '../lib/apiClient';

interface Step {
  id: number;
  gen: number;
  domain: string;
  year_range: string;
  event: string;
  probability: string;
}

export default function TimelineColumn({ sessionId }: { sessionId: string }) {
  const [steps, setSteps] = useState<Step[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

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

  if (!sessionId) return <p className="text-sm">Enter an id.</p>;
  if (loading) return <p className="text-sm">Loading #{sessionId}…</p>;
  if (error) return <p className="border border-blood px-2 py-1 text-sm text-blood">{error}</p>;

  return (
    <div className="border border-parchment-line bg-white/60 p-3">
      <h3 className="display-serif mb-2 font-bold">Session #{sessionId}</h3>
      <ul className="grid gap-2">
        {steps.map((s) => (
          <li key={s.id} className="border border-parchment-line p-2 text-sm">
            <span className="text-xs font-bold text-bark-soft">
              G{s.gen} · {s.domain} · {s.year_range}
            </span>
            <p className="mt-1">{s.event}</p>
          </li>
        ))}
      </ul>
      {steps.length === 0 && <p className="text-sm">No steps.</p>}
    </div>
  );
}
