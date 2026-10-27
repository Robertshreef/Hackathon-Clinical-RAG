import { BrainCircuit, User } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  citationIndexFromHref,
  isCitationHref,
  prepareCitationMarkdown,
} from "../lib/citations";

export default function MessageBubble({ message, activeCite, onCiteClick }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex gap-3 animate-rise ${isUser ? "flex-row-reverse" : ""}`}>
      <div
        className={`shrink-0 w-7 h-7 rounded-full flex items-center justify-center mt-0.5 ${
          isUser ? "bg-navy-800 text-white" : "bg-brand-100 text-brand-700"
        }`}
      >
        {isUser ? (
          <User className="w-3.5 h-3.5" />
        ) : (
          <BrainCircuit className="w-3.5 h-3.5" />
        )}
      </div>

      <div
        className={`max-w-[70ch] rounded-2xl px-4 py-2.5 text-[0.925rem] ${
          isUser
            ? "bg-navy-800 text-white rounded-tr-sm"
            : "bg-white border border-mist-line text-navy-800 rounded-tl-sm shadow-card"
        }`}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap leading-relaxed font-body">
            {message.content}
          </p>
        ) : (
          <div className="md-content">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                a: ({ href, children }) => {
                  if (isCitationHref(href)) {
                    const idx = citationIndexFromHref(href);
                    return (
                      <button
                        onClick={() => onCiteClick?.(idx)}
                        className={`cite-marker ${
                          String(activeCite) === String(idx) ? "active" : ""
                        }`}
                        title={`Jump to source ${idx}`}
                      >
                        {idx}
                      </button>
                    );
                  }
                  return (
                    <a href={href} target="_blank" rel="noreferrer">
                      {children}
                    </a>
                  );
                },
              }}
            >
              {prepareCitationMarkdown(message.content)}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}
