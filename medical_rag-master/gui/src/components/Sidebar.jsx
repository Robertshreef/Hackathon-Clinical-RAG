import { BrainCircuit, LogOut, Pencil, Plus, Trash2 } from "lucide-react";
import { useState } from "react";
import { useAuth } from "../context/AuthContext";

export default function Sidebar({
  conversations,
  activeId,
  onSelect,
  onCreate,
  onRename,
  onDelete,
}) {
  const { user, logout } = useAuth();
  const [editingId, setEditingId] = useState(null);
  const [draft, setDraft] = useState("");

  const startEdit = (conv) => {
    setEditingId(conv.id);
    setDraft(conv.name);
  };

  const commitEdit = () => {
    if (draft.trim()) onRename(editingId, draft.trim());
    setEditingId(null);
  };

  return (
    <aside className="w-64 shrink-0 h-full bg-navy-900 text-white flex flex-col">
      <div className="flex items-center gap-2.5 px-4 h-14 border-b border-white/10">
        <div className="w-7 h-7 rounded-lg bg-brand-600 flex items-center justify-center shrink-0">
          <BrainCircuit className="w-4 h-4 text-white" strokeWidth={1.75} />
        </div>
        <span className="font-display font-semibold text-[15px] tracking-tight truncate">
          Agentic Mind
        </span>
      </div>

      <div className="px-3 pt-3">
        <button
          onClick={onCreate}
          className="w-full flex items-center gap-2 rounded-lg bg-brand-600 hover:bg-brand-700 px-3 py-2 text-sm font-body font-medium text-white transition-colors"
        >
          <Plus className="w-4 h-4" />
          New conversation
        </button>
      </div>

      <nav className="flex-1 overflow-y-auto scroll-quiet px-2 py-3 space-y-0.5">
        {conversations.length === 0 && (
          <p className="text-xs text-white/40 px-3 py-4 font-body">
            No conversations yet. Start one above.
          </p>
        )}
        {conversations.map((conv) => (
          <div
            key={conv.id}
            className={`group flex items-center gap-1 rounded-lg px-2.5 py-2 cursor-pointer transition-colors ${
              conv.id === activeId
                ? "bg-white/10 text-white"
                : "text-white/65 hover:bg-white/5 hover:text-white"
            }`}
            onClick={() => onSelect(conv.id)}
          >
            {editingId === conv.id ? (
              <input
                autoFocus
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                onBlur={commitEdit}
                onKeyDown={(e) => {
                  if (e.key === "Enter") commitEdit();
                  if (e.key === "Escape") setEditingId(null);
                }}
                onClick={(e) => e.stopPropagation()}
                className="flex-1 bg-transparent border-b border-brand-400 outline-none text-sm font-body py-0.5"
              />
            ) : (
              <span className="flex-1 text-sm font-body truncate">{conv.name}</span>
            )}

            <button
              onClick={(e) => {
                e.stopPropagation();
                startEdit(conv);
              }}
              className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-white/10 transition-opacity"
              title="Rename"
            >
              <Pencil className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDelete(conv.id);
              }}
              className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-rose/20 hover:text-rose transition-opacity"
              title="Delete"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          </div>
        ))}
      </nav>

      <div className="border-t border-white/10 px-3 py-3 flex items-center gap-2.5">
        <div className="w-8 h-8 rounded-full bg-brand-600/30 border border-brand-400/40 flex items-center justify-center text-xs font-display font-semibold text-brand-400 shrink-0">
          {(user?.full_name || user?.email || "?")[0].toUpperCase()}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-body truncate">{user?.full_name || "—"}</p>
          <p className="text-xs text-white/40 truncate">{user?.email}</p>
        </div>
        <button
          onClick={logout}
          title="Sign out"
          className="p-1.5 rounded hover:bg-white/10 text-white/60 hover:text-white transition-colors"
        >
          <LogOut className="w-4 h-4" />
        </button>
      </div>
    </aside>
  );
}
