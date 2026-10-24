import { useEffect, useState } from 'react';
import { apiGet } from '../../lib/apiClient';
import TimelineColumn from './TimelineColumn';

interface Row {
  gen: number;
  year_range: string;
  domain: string;
  a: string | null;
  b: string | null;
  status: string;
}

export default function CompareView() {
  const [a, setA] = useState('');
  const [b, setB] = useState('');
  const [rows, setRows] = useState<Row[]>([]);

  useEffect(() => {
    const q = new URLSearchParams(window.location.search);
    const pa = q.get('a') ?? '';
    const pb = q.get('b') ?? '';
    setA(pa);
    setB(pb);
    if (pa && pb) {
      apiGet(`/api/simulate/compare?a=${pa}&b=${pb}`).then((d) => setRows((d.rows ?? []) as Row[]));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function go() {
    if (!a || !b) return;
    const d = await apiGet(`/api/simulate/compare?a=${a}&b=${b}`);
    setRows((d.rows ?? []) as Row[]);
  }

  return (
    <div>
      <div className="flex gap-2">
        <input className="border border-agedbrown/40 bg-white px-2 py-1" value={a} onChange={(e) => setA(e.target.value)} placeholder="Session A id" />
        <input className="border border-agedbrown/40 bg-white px-2 py-1" value={b} onChange={(e) => setB(e.target.value)} placeholder="Session B id" />
        <button className="border border-agedbrown/40 px-3 py-1" onClick={go}>Compare</button>
      </div>
      {rows.length > 0 && (
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          <TimelineColumn title={`Timeline A (#${a})`} rows={rows} side="a" />
          <TimelineColumn title={`Timeline B (#${b})`} rows={rows} side="b" />
        </div>
      )}
    </div>
  );
}
