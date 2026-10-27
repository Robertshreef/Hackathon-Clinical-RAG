import { ArrowUp, Mic, MicOff } from "lucide-react";
import { useCallback, useRef, useState } from "react";
import { useSpeechRecognition } from "../lib/useSpeechRecognition";

export default function ChatInput({ onSend, disabled }) {
  const [value, setValue] = useState("");
  const taRef = useRef(null);

  const resize = () => {
    if (!taRef.current) return;
    taRef.current.style.height = "auto";
    taRef.current.style.height = Math.min(taRef.current.scrollHeight, 160) + "px";
  };

  // Append recognized speech into whatever's already typed, with a space
  // between chunks so consecutive dictations don't run together.
  const handleSpeechResult = useCallback((chunk) => {
    setValue((prev) => (prev && !prev.endsWith(" ") ? prev + " " : prev) + chunk);
    requestAnimationFrame(resize);
  }, []);

  const { supported, listening, error, toggle } = useSpeechRecognition({
    onResult: handleSpeechResult,
  });

  const submit = () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
    if (taRef.current) taRef.current.style.height = "auto";
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  const autoGrow = (e) => {
    setValue(e.target.value);
    resize();
  };

  return (
    <div className="px-6 pb-5 pt-2">
      <div
        className={`max-w-3xl mx-auto flex items-end gap-2 bg-white border rounded-2xl px-3 py-2 shadow-card transition-all ${
          listening
            ? "border-rose shadow-glow"
            : "border-mist-line focus-within:border-brand-600 focus-within:shadow-glow"
        }`}
      >
        <textarea
          ref={taRef}
          rows={1}
          value={value}
          onChange={autoGrow}
          onKeyDown={handleKeyDown}
          placeholder={
            listening ? "Listening…" : "Ask Agentic Mind about your documents…"
          }
          className="flex-1 resize-none outline-none bg-transparent text-sm font-body text-navy-800 placeholder:text-navy-400/60 py-1.5 max-h-40"
        />

        {supported && (
          <button
            onClick={toggle}
            title={listening ? "Stop dictation" : "Dictate your question"}
            className={`shrink-0 w-8 h-8 rounded-full flex items-center justify-center transition-colors ${
              listening
                ? "bg-rose text-white animate-pulse"
                : "text-navy-400 hover:text-brand-600 hover:bg-brand-50"
            }`}
          >
            {listening ? (
              <MicOff className="w-4 h-4" />
            ) : (
              <Mic className="w-4 h-4" />
            )}
          </button>
        )}

        <button
          onClick={submit}
          disabled={disabled || !value.trim()}
          className="shrink-0 w-8 h-8 rounded-full bg-brand-600 hover:bg-brand-700 disabled:bg-navy-100 disabled:cursor-not-allowed flex items-center justify-center text-white transition-colors"
        >
          <ArrowUp className="w-4 h-4" />
        </button>
      </div>

      {error && (
        <p className="text-center text-[11px] text-rose font-body mt-2">{error}</p>
      )}
      <p className="text-center text-[11px] text-navy-400/70 font-body mt-2">
        Answers are grounded in your indexed documents — check the references rail.
      </p>
    </div>
  );
}
