import { ChevronDown, Download, FileText, Loader2 } from "lucide-react";
import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { chatApi } from "../lib/api";

export default function CitationCard({ source, isActive, cardRef }) {
  const [open, setOpen] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState(false);

  const pageLabel =
    source.starting_page === source.end_page
      ? `p. ${source.starting_page}`
      : `pp. ${source.starting_page}–${source.end_page}`;

  const handleDownload = async (e) => {
    e.stopPropagation();
    setDownloading(true);
    setDownloadError(false);
    try {
      await chatApi.downloadFile(source.file_name);
    } catch {
      setDownloadError(true);
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div
      ref={cardRef}
      className={`relative bg-white border rounded-xl transition-all duration-200 ${isActive
        ? "border-brand-600 shadow-glow"
        : "border-mist-line hover:border-teal/40"
        }`}
    >
      <div className="w-full flex items-start gap-2.5 px-3 py-2.5">
        <button
          onClick={() => setOpen((o) => !o)}
          className="flex items-start gap-2.5 flex-1 min-w-0 text-left"
        >
          <span className="shrink-0 mt-0.5 w-5 h-5 rounded-full bg-teal text-white font-mono text-[11px] flex items-center justify-center">
            {source.index}
          </span>
          <span className="flex-1 min-w-0">
            <span className="flex items-center gap-1.5 text-sm font-body font-medium text-navy-800 truncate">
              <FileText className="w-3.5 h-3.5 text-navy-400 shrink-0" />
              <span className="truncate">{source.file_name}</span>
            </span>
            <span className="block text-xs font-mono text-brand-600 mt-0.5">
              {pageLabel}
            </span>
          </span>
        </button>

        <button
          onClick={handleDownload}
          disabled={downloading}
          title={`Download ${source.file_name}`}
          className="shrink-0 p-1.5 rounded-md text-navy-400 hover:text-brand-600 hover:bg-brand-50 transition-colors disabled:opacity-60"
        >
          {downloading ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <Download className="w-3.5 h-3.5" />
          )}
        </button>

        <button
          onClick={() => setOpen((o) => !o)}
          className="shrink-0 p-1 text-navy-400"
        >
          <ChevronDown
            className={`w-4 h-4 transition-transform ${open ? "rotate-180" : ""}`}
          />
        </button>
      </div>

      {downloadError && (
        <p className="px-3 pb-2 pl-10 -mt-1 text-xs text-rose font-body">
          Couldn't download this file. Try again.
        </p>
      )}

      {open && (
        <div className="px-3 pb-3 pl-10 -mt-1 space-y-2.5 animate-rise">
          {source.content && (
            <div className="border-l-2 border-brand-400/50 pl-2.5">
              <p className="text-[10px] font-mono uppercase tracking-wide text-navy-400/70 mb-1">
                Excerpt
              </p>
              <div className="md-content text-xs leading-relaxed text-navy-800 max-h-48 overflow-y-auto scroll-quiet pr-1">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {source.content}
                </ReactMarkdown>
              </div>
            </div>
          )}

          <div className="border-l-2 border-teal/50 pl-2.5">
            <p className="text-[10px] font-mono uppercase tracking-wide text-navy-400/70 mb-1">
              Why it's cited
            </p>
            <p className="text-xs leading-relaxed text-navy-400 font-body">
              {source.reason}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}