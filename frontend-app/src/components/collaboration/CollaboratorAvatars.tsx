interface Collaborator {
  user_id: string;
  name: string;
  avatar_url: string | null;
  color: string;
}

interface Props {
  collaborators: Collaborator[];
}

export function CollaboratorAvatars({ collaborators }: Props) {
  if (collaborators.length === 0) return null;

  return (
    <div className="flex items-center -space-x-1.5">
      {collaborators.slice(0, 5).map(c => (
        <div
          key={c.user_id}
          className="h-6 w-6 rounded-full flex items-center justify-center text-[10px] font-medium text-white ring-2 ring-white"
          style={{ backgroundColor: c.color }}
          title={c.name}
        >
          {c.avatar_url ? (
            <img src={c.avatar_url} alt={c.name} className="w-full h-full rounded-full object-cover" />
          ) : (
            c.name[0]?.toUpperCase()
          )}
        </div>
      ))}
      {collaborators.length > 5 && (
        <div className="h-6 w-6 rounded-full bg-gray-200 flex items-center justify-center text-[9px] font-medium text-gray-600 ring-2 ring-white">
          +{collaborators.length - 5}
        </div>
      )}
    </div>
  );
}
