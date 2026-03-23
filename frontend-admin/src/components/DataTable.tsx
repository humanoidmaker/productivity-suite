interface Column<T> {
  key: string;
  label: string;
  render?: (item: T) => React.ReactNode;
  width?: string;
}

interface Props<T> {
  columns: Column<T>[];
  data: T[];
  keyField: string;
  onRowClick?: (item: T) => void;
}

export function DataTable<T extends Record<string, unknown>>({ columns, data, keyField, onRowClick }: Props<T>) {
  return (
    <div className="border border-gray-800 rounded-xl overflow-hidden">
      <table className="w-full">
        <thead>
          <tr className="bg-gray-900/50">
            {columns.map(col => (
              <th key={col.key} className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider" style={{ width: col.width }}>
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-800/50">
          {data.map(item => (
            <tr key={String(item[keyField])} onClick={() => onRowClick?.(item)}
              className={`transition-colors ${onRowClick ? "cursor-pointer hover:bg-gray-800/50" : ""}`}>
              {columns.map(col => (
                <td key={col.key} className="px-4 py-3 text-sm text-gray-300">
                  {col.render ? col.render(item) : String(item[col.key] ?? "")}
                </td>
              ))}
            </tr>
          ))}
          {data.length === 0 && (
            <tr><td colSpan={columns.length} className="px-4 py-8 text-center text-sm text-gray-600">No data</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
