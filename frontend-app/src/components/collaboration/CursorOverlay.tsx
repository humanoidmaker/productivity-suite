interface RemoteCursor {
  user_id: string;
  name: string;
  color: string;
  x: number;
  y: number;
}

interface Props {
  cursors: RemoteCursor[];
}

export function CursorOverlay({ cursors }: Props) {
  return (
    <div className="pointer-events-none absolute inset-0 z-50">
      {cursors.map(cursor => (
        <div
          key={cursor.user_id}
          className="absolute transition-all duration-100"
          style={{ left: cursor.x, top: cursor.y }}
        >
          {/* Cursor arrow */}
          <svg width="16" height="20" viewBox="0 0 16 20" fill="none" className="drop-shadow">
            <path d="M0 0L16 12H6L0 20V0Z" fill={cursor.color} />
          </svg>
          {/* Name label */}
          <div
            className="absolute left-4 top-3 px-1.5 py-0.5 rounded text-[10px] font-medium text-white whitespace-nowrap"
            style={{ backgroundColor: cursor.color }}
          >
            {cursor.name}
          </div>
        </div>
      ))}
    </div>
  );
}
