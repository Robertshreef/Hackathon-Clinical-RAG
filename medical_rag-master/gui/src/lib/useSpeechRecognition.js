import { useCallback, useEffect, useRef, useState } from "react";

/**
 * Wraps the browser SpeechRecognition API (Chrome/Edge/Safari; not
 * supported in Firefox as of writing). Returns interim + final transcripts
 * so the caller can append them into a text field live.
 */
export function useSpeechRecognition({ onResult } = {}) {
  const [supported] = useState(
    () =>
      typeof window !== "undefined" &&
      !!(window.SpeechRecognition || window.webkitSpeechRecognition)
  );
  const [listening, setListening] = useState(false);
  const [error, setError] = useState("");
  const recognitionRef = useRef(null);

  useEffect(() => {
    if (!supported) return;
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onresult = (event) => {
      let finalChunk = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        if (event.results[i].isFinal) {
          finalChunk += event.results[i][0].transcript;
        }
      }
      if (finalChunk) onResult?.(finalChunk);
    };

    recognition.onerror = (event) => {
      if (event.error === "not-allowed" || event.error === "service-not-allowed") {
        setError("Microphone access was denied.");
      } else if (event.error !== "no-speech" && event.error !== "aborted") {
        setError("Voice input hit an error. Try again.");
      }
      setListening(false);
    };

    recognition.onend = () => setListening(false);

    recognitionRef.current = recognition;
    return () => recognition.stop();
  }, [supported, onResult]);

  const start = useCallback(() => {
    if (!recognitionRef.current || listening) return;
    setError("");
    try {
      recognitionRef.current.start();
      setListening(true);
    } catch {
      // start() throws if already started; safe to ignore
    }
  }, [listening]);

  const stop = useCallback(() => {
    recognitionRef.current?.stop();
    setListening(false);
  }, []);

  const toggle = useCallback(() => {
    if (listening) stop();
    else start();
  }, [listening, start, stop]);

  return { supported, listening, error, start, stop, toggle };
}
