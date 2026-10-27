import { BrainCircuit, Loader2 } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import ChatView from "./components/ChatView";
import LoginScreen from "./components/LoginScreen";
import Sidebar from "./components/Sidebar";
import { useAuth } from "./context/AuthContext";
import { chatApi } from "./lib/api";

export default function App() {
  const { status } = useAuth();

  if (status === "loading") {
    return (
      <div className="min-h-screen bg-navy-900 flex items-center justify-center">
        <Loader2 className="w-6 h-6 text-white/50 animate-spin" />
      </div>
    );
  }

  if (status === "guest") return <LoginScreen />;

  return <ChatWorkspace />;
}

function ChatWorkspace() {
  const [conversations, setConversations] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [createError, setCreateError] = useState("");

  const refresh = useCallback(async () => {
    const list = await chatApi.listConversations();
    setConversations(list);
    return list;
  }, []);

  useEffect(() => {
    refresh()
      .then((list) => {
        if (list.length) setActiveId(list[0].id);
      })
      .catch((err) => setCreateError(err.message || "Failed to load conversations"))
      .finally(() => setLoading(false));
  }, [refresh]);

  const handleCreate = async () => {
    setCreateError("");
    try {
      const conv = await chatApi.createConversation(
        `New conversation ${conversations.length + 1}`
      );
      setConversations((prev) => [conv, ...prev]);
      setActiveId(conv.id);
    } catch (err) {
      setCreateError(err.message || "Failed to create conversation — is the backend running?");
    }
  };

  const handleRename = async (id, name) => {
    const updated = await chatApi.renameConversation(id, name);
    setConversations((prev) => prev.map((c) => (c.id === id ? updated : c)));
  };

  const handleDelete = async (id) => {
    await chatApi.deleteConversation(id);
    setConversations((prev) => {
      const next = prev.filter((c) => c.id !== id);
      if (activeId === id) setActiveId(next[0]?.id ?? null);
      return next;
    });
  };

  const activeConversation = conversations.find((c) => c.id === activeId);

  return (
    <div className="h-screen w-full flex bg-mist overflow-hidden">
      <Sidebar
        conversations={conversations}
        activeId={activeId}
        onSelect={setActiveId}
        onCreate={handleCreate}
        onRename={handleRename}
        onDelete={handleDelete}
      />

      {loading ? (
        <div className="flex-1 flex items-center justify-center">
          <Loader2 className="w-5 h-5 text-navy-200 animate-spin" />
        </div>
      ) : activeConversation ? (
        <ChatView key={activeConversation.id} conversation={activeConversation} />
      ) : (
        <EmptyState onCreate={handleCreate} error={createError} />
      )}
    </div>
  );
}

function EmptyState({ onCreate, error }) {
  return (
    <div className="flex-1 flex flex-col items-center justify-center gap-3">
      <div className="w-14 h-14 rounded-2xl bg-brand-100 flex items-center justify-center">
        <BrainCircuit className="w-7 h-7 text-brand-600" strokeWidth={1.5} />
      </div>
      <p className="font-display font-semibold text-lg text-navy-800">
        No conversation open
      </p>
      <button
        onClick={onCreate}
        className="text-sm font-body font-medium bg-brand-600 hover:bg-brand-700 text-white px-4 py-2 rounded-lg transition-colors"
      >
        Start a conversation
      </button>
      {error && (
        <p className="text-sm text-red-500 bg-red-50 border border-red-200 rounded-lg px-4 py-2 max-w-sm text-center font-body">
          ⚠️ {error}
        </p>
      )}
    </div>
  );
}
