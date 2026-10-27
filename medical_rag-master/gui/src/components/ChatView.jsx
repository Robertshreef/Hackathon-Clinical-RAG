import { BrainCircuit } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { chatApi } from "../lib/api";
import ChatInput from "./ChatInput";
import CitationsRail from "./CitationsRail";
import EmergencyAlertBanner from "./EmergencyAlertBanner";
import MessageBubble from "./MessageBubble";

export default function ChatView({ conversation }) {
  const [messages, setMessages] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [sending, setSending] = useState(false);
  const [railOpen, setRailOpen] = useState(false);
  const [error, setError] = useState("");

  // Which message's sources the rail is currently showing. `sources` is
  // read off that message object, so old assistant turns work the same way
  // as the latest one, as long as they were received this session.
  const [railMessageId, setRailMessageId] = useState(null);
  const [activeCite, setActiveCite] = useState(null);

  const bottomRef = useRef(null);

  useEffect(() => {
    let cancelled = false;
    setMessages([]);
    setRailMessageId(null);
    setActiveCite(null);
    setRailOpen(false);
    setError("");
    setLoadingHistory(true);

    chatApi
      .getHistory(conversation.id)
      .then((history) => {
        if (cancelled) return;
        // History from the backend has no `sources` (see README — only the
        // live send_message response carries CitedSource[]), so these
        // messages start with sources: undefined until/unless the user
        // re-asks something in this session.
        setMessages(history.map((m, i) => ({ ...m, id: `h-${i}` })));
      })
      .catch((err) => !cancelled && setError(err.message))
      .finally(() => !cancelled && setLoadingHistory(false));

    return () => {
      cancelled = true;
    };
  }, [conversation.id]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending]);

  const handleSend = async (text) => {
    setError("");
    const userMsg = { id: `u-${Date.now()}`, role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setSending(true);
    try {
      const res = await chatApi.sendMessage(conversation.id, text);
      const assistantMsg = {
        id: `a-${Date.now()}`,
        role: "assistant",
        content: res.answer,
        sources: res.sources || [],
        alert: res.alert || null,
      };
      setMessages((prev) => [...prev, assistantMsg]);
      if (assistantMsg.sources.length) {
        setRailMessageId(assistantMsg.id);
        setActiveCite(null);
        setRailOpen(true);
      }
    } catch (err) {
      setError(err.message || "Failed to get a response");
      setMessages((prev) => [
        ...prev,
        {
          id: `a-err-${Date.now()}`,
          role: "assistant",
          content: "I ran into an error answering that. Please try again.",
        },
      ]);
    } finally {
      setSending(false);
    }
  };

  const handleCiteClick = (message, idx) => {
    setRailMessageId(message.id);
    setActiveCite(idx);
    setRailOpen(true);
  };

  const railMessage = messages.find((m) => m.id === railMessageId);
  // `undefined` (never had sources this session) vs `[]` (had a response,
  // just didn't cite anything) are shown differently in the rail.
  const railSources = railMessage?.sources;
  const railUnavailable = Boolean(railMessage) && railMessage.sources === undefined;

  return (
    <div className="flex-1 flex h-full min-w-0">
      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-14 shrink-0 border-b border-mist-line flex items-center px-6 bg-white/60 backdrop-blur">
          <h2 className="font-display font-semibold text-base text-navy-800 truncate">
            {conversation.name}
          </h2>
        </header>

        <div className="flex-1 overflow-y-auto scroll-quiet px-6 py-6">
          <div className="max-w-3xl mx-auto space-y-5">
            {loadingHistory && (
              <p className="text-sm text-navy-400 font-body text-center py-10">
                Loading conversation…
              </p>
            )}

            {!loadingHistory && messages.length === 0 && (
              <div className="text-center py-16">
                <div className="w-12 h-12 rounded-2xl bg-brand-100 flex items-center justify-center mx-auto mb-3">
                  <BrainCircuit className="w-6 h-6 text-brand-600" />
                </div>
                <p className="font-display font-semibold text-lg text-navy-800">
                  Start the conversation
                </p>
                <p className="text-sm text-navy-400 font-body mt-1">
                  Ask a question grounded in your indexed documents.
                </p>
              </div>
            )}

            {messages.map((m) => (
              <div key={m.id}>
                {m.role === "assistant" && <EmergencyAlertBanner alert={m.alert} />}
                <MessageBubble
                  message={m}
                  activeCite={railMessageId === m.id ? activeCite : null}
                  onCiteClick={(idx) => handleCiteClick(m, idx)}
                />
              </div>
            ))}

            {sending && (
              <div className="flex gap-3 animate-rise">
                <div className="shrink-0 w-7 h-7 rounded-full bg-brand-100 text-brand-700 flex items-center justify-center mt-0.5">
                  <BrainCircuit className="w-3.5 h-3.5" />
                </div>
                <div className="bg-white border border-mist-line rounded-2xl rounded-tl-sm px-4 py-3 dot-pulse flex gap-1.5 shadow-card">
                  <span className="w-1.5 h-1.5 rounded-full bg-brand-600 inline-block" />
                  <span className="w-1.5 h-1.5 rounded-full bg-brand-600 inline-block" />
                  <span className="w-1.5 h-1.5 rounded-full bg-brand-600 inline-block" />
                </div>
              </div>
            )}

            {error && (
              <p className="text-sm text-rose bg-rose/10 border border-rose/20 rounded-md px-3 py-2 max-w-3xl">
                {error}
              </p>
            )}
            <div ref={bottomRef} />
          </div>
        </div>

        <ChatInput onSend={handleSend} disabled={sending} />
      </div>

      <CitationsRail
        sources={railSources || []}
        unavailable={railUnavailable}
        activeIndex={activeCite}
        open={railOpen}
        onToggle={() => setRailOpen((o) => !o)}
      />
    </div>
  );
}