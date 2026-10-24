interface Row {
  gen: number;
  year_range: string;
  domain: string;
  a: string | null;
  b: string | null;
  status: string;
}

export default function TimelineColumn({ title, rows, side }: { title: string; rows: Row[]; side: 'a' | 'b' }) {
  return (
    <div className="border border-agedbrown/30 bg-white p-3">
      <h3 className="display-serif text-lg">{title}</h3>
      <div className="mt-2 space-y-2">
        {rows.map((r, i) => {
          const text = side === 'a' ? r.a : r.b;
          const bg = r.status === 'shared' ? 'bg-green-50' : r.status === 'diverged' ? 'bg-red-50' : 'bg-stone-100';
          return (
            <div key={i} className={`${bg} p-2 text-sm`}>
              <p className="mono-n text-xs opacity-70">{r.year_range} · {r.domain} · gen {r.gen}</p>
              <p>{text ?? '—'}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
