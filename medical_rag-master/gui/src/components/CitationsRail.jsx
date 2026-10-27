import {
  AlertCircle,
  PanelRightClose,
  PanelRightOpen,
  Waypoints,
} from "lucide-react";
import { useEffect, useRef } from "react";
import CitationCard from "./CitationCard";

export default function CitationsRail({
  sources,
  unavailable,
  activeIndex,
  open,
  onToggle,
}) {
  const cardRefs = useRef({});

  useEffect(() => {
    if (activeIndex && cardRefs.current[activeIndex]) {
      cardRefs.current[activeIndex].scrollIntoView({
        behavior: "smooth",
        block: "nearest",
      });
    }
  }, [activeIndex, sources]);

  if (!open) {
    return (
      <button
        onClick={onToggle}
        className="shrink-0 w-10 h-full bg-mist-dim border-l border-mist-line flex flex-col items-center pt-4 gap-3 hover:bg-mist-line/60 transition-colors"
        title="Show references"
      >
        <PanelRightOpen className="w-4 h-4 text-navy-400" />
        {sources.length > 0 && (
          <span className="text-[10px] font-mono text-teal-dim bg-teal-soft rounded-full w-5 h-5 flex items-center justify-center">
            {sources.length}
          </span>
        )}
      </button>
    );
  }

  return (
    <aside className="shrink-0 w-80 h-full bg-mist-dim border-l border-mist-line flex flex-col shadow-rail">
      <div className="flex items-center justify-between h-14 px-4 border-b border-mist-line">
        <div className="flex items-center gap-2 text-navy-800">
          <Waypoints className="w-4 h-4 text-teal-dim" />
          <span className="font-display font-semibold text-sm">References</span>
        </div>
        <button
          onClick={onToggle}
          className="p-1 rounded hover:bg-mist-line/70 text-navy-400"
          title="Hide references"
        >
          <PanelRightClose className="w-4 h-4" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto scroll-quiet p-3 space-y-2">
        {unavailable ? (
          <div className="text-center py-10 px-4">
            <AlertCircle className="w-6 h-6 text-navy-200 mx-auto mb-2" />
            <p className="text-sm text-navy-400 font-body">
              Reference data for this message isn't available. It was loaded
              from conversation history, which doesn't include sources —
              only answers generated in this session do.
            </p>
          </div>
        ) : sources.length === 0 ? (
          <div className="text-center py-10 px-4">
            <Waypoints className="w-6 h-6 text-navy-200 mx-auto mb-2" />
            <p className="text-sm text-navy-400 font-body">
              Sources cited in the assistant's latest answer will appear here.
            </p>
          </div>
        ) : (
          sources.map((s) => (
            <CitationCard
              key={s.index}
              source={s}
              isActive={String(activeIndex) === String(s.index)}
              cardRef={(el) => (cardRefs.current[s.index] = el)}
            />
          ))
        )}
      </div>
    </aside>
  );
}