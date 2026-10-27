import { AlertTriangle, PhoneCall } from "lucide-react";

// Renders above an assistant message when the backend flags the query as
// medically urgent. Backend contract: ChatResponse.alert is either null or
// { severity: "urgent" | "emergency", message: string }.
export default function EmergencyAlertBanner({ alert }) {
  if (!alert) return null;

  const isEmergency = alert.severity === "emergency";

  return (
    <div
      role="alert"
      className={`flex items-start gap-3 rounded-xl border px-4 py-3 mb-2 animate-rise ${
        isEmergency
          ? "bg-rose/10 border-rose/40"
          : "bg-amber-50 border-amber-300"
      }`}
    >
      <div
        className={`shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isEmergency ? "bg-rose text-white" : "bg-amber-400 text-white"
        }`}
      >
        {isEmergency ? (
          <PhoneCall className="w-4 h-4" />
        ) : (
          <AlertTriangle className="w-4 h-4" />
        )}
      </div>
      <div className="flex-1 min-w-0">
        <p
          className={`text-sm font-display font-semibold ${
            isEmergency ? "text-rose" : "text-amber-800"
          }`}
        >
          {isEmergency
            ? "This sounds like a medical emergency"
            : "Please see a doctor about this"}
        </p>
        <p className="text-sm font-body text-navy-800 mt-0.5 leading-relaxed">
          {alert.message}
        </p>
        {isEmergency && (
          <p className="text-xs font-body text-rose/90 mt-1.5 font-medium">
            If you're in immediate danger, call your local emergency number now.
          </p>
        )}
        <p className="text-[11px] font-body text-navy-400 mt-1.5">
          This assistant answers questions from indexed documents and isn't a
          substitute for medical evaluation.
        </p>
      </div>
    </div>
  );
}
