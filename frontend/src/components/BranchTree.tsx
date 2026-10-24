import { useEffect, useMemo, useState } from 'react';
import { apiGet } from '../lib/apiClient';

interface LibItem {
  id: number;
  premise: string;
  divergence_year: number;
  branches: number;
  parent_session_id: number | null;
}

interface Node {
  item: LibItem;
  children: Node[];
}

function buildForest(items: LibItem[]): Node[] {
  const byId = new Map<number, Node>();
  for (const it of items) byId.set(it.id, { item: it, children: [] });
  const roots: Node[] = [];
  for (const it of items) {
    const node = byId.get(it.id)!;
    if (it.parent_session_id != null && byId.has(it.parent_session_id)) {
      byId.get(it.parent_session_id)!.children.push(node);
    } else {
      roots.push(node);
    }
  }
  const sortRec = (ns: Node[]) => {
    ns.sort((a, b) => a.item.id - b.item.id);
    ns.forEach((n) => sortRec(n.children));
  };
  sortRec(roots);
  return roots;
}

function openSession(id: number) {
  window.location.href = `/timeline?sid=${id}`;
}

function TreeNodeView({
  node,
  depth,
  expanded,
  toggle,
}: {
  node: Node;
  depth: number;
  expanded: Set<number>;
  toggle: (id: number) => void;
}) {
  const isOpen = expanded.has(node.item.id);
  const hasKids = node.children.length > 0;
  return (
    <li className="mt-1">
      <div className="flex items-center gap-2" style={{ marginLeft: depth * 16 }}>
        {hasKids ? (
          <button
            onClick={() => toggle(node.item.id)}
            aria-label={isOpen ? 'collapse' : 'expand'}
            className="border border-parchment-line px-1 text-xs"
          >
            {isOpen ? '−' : '+'}
          </button>
        ) : (
          <span className="inline-block w-6 text-center text-xs text-bark-soft">·</span>
        )}
        <button onClick={() => openSession(node.item.id)} className="text-left text-sm hover:text-blood">
          <span className="font-bold">#{node.item.id}</span> {node.item.premise.slice(0, 80)}
          <span className="text-xs text-bark-soft"> ({node.item.divergence_year})</span>
        </button>
      </div>
      {hasKids && isOpen && (
        <ul>
          {node.children.map((c) => (
            <TreeNodeView key={c.item.id} node={c} depth={depth + 1} expanded={expanded} toggle={toggle} />
          ))}
        </ul>
      )}
    </li>
  );
}

function layoutPositions(roots: Node[]): { x: number; y: number; id: number }[] {
  const pts: { x: number; y: number; id: number }[] = [];
  let y = 0;
  const walk = (ns: Node[], depth: number) => {
    for (const n of ns) {
      pts.push({ x: 30 + depth * 90, y: 24 + y * 30, id: n.item.id });
      y += 1;
      walk(n.children, depth + 1);
    }
  };
  walk(roots, 0);
  return pts;
}

export default function BranchTree() {
  const [items, setItems] = useState<LibItem[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<Set<number>>(new Set());

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = (await apiGet('/api/simulate/library')) as LibItem[];
        if (!cancelled) {
          setItems(data);
          setExpanded(new Set(data.map((d) => d.id)));
        }
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Load failed.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const roots = useMemo(() => buildForest(items), [items]);
  const pts = useMemo(() => layoutPositions(roots), [roots]);
  const byId = useMemo(() => new Map(items.map((i) => [i.id, i])), [items]);
  const height = Math.max(80, pts.length * 30 + 40);

  function toggle(id: number) {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  if (loading) return <p className="text-sm">Loading branches…</p>;
  if (error) return <p className="border border-blood px-2 py-1 text-sm text-blood">{error}</p>;
  if (items.length === 0) return <p className="text-sm">No simulations yet. Start one first.</p>;

  const parentOf = new Map<number, number | null>(items.map((i) => [i.id, i.parent_session_id]));
  const posById = new Map(pts.map((p) => [p.id, p]));

  return (
    <div>
      <svg
        width="100%"
        height={height}
        viewBox={`0 0 600 ${height}`}
        className="mb-4 border border-parchment-line bg-white/50"
        role="img"
        aria-label="branch tree"
      >
        {pts.map((p) => {
          const pid = parentOf.get(p.id);
          const pp = pid != null ? posById.get(pid) : undefined;
          if (!pp) return null;
          return (
            <line key={`e-${pid}-${p.id}`} x1={pp.x} y1={pp.y} x2={p.x} y2={p.y} stroke="#b91c1c" strokeWidth={1.5} />
          );
        })}
        {pts.map((p) => (
          <g key={p.id} onClick={() => openSession(p.id)} style={{ cursor: 'pointer' }}>
            <circle cx={p.x} cy={p.y} r={9} fill="#faf3e3" stroke="#57534e" strokeWidth={1.5} />
            <text x={p.x} y={p.y + 4} textAnchor="middle" fontSize={9} fill="#57534e">
              {p.id}
            </text>
            <text x={p.x + 14} y={p.y + 4} fontSize={10} fill="#57534e">
              {(byId.get(p.id)?.premise ?? '').slice(0, 34)}
            </text>
          </g>
        ))}
      </svg>
      <ul>
        {roots.map((r) => (
          <TreeNodeView key={r.item.id} node={r} depth={0} expanded={expanded} toggle={toggle} />
        ))}
      </ul>
    </div>
  );
}
