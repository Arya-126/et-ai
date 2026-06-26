import { useEffect, useRef, useState } from "react";

// Subscribe to the backend SSE stream. `onEvent(evt)` fires for each event;
// returns whether the stream is currently connected (for a "● LIVE" indicator).
export function useEvents(onEvent) {
  const [live, setLive] = useState(false);
  const cb = useRef(onEvent);
  cb.current = onEvent;

  useEffect(() => {
    let es;
    try {
      es = new EventSource("/events");
    } catch {
      return;
    }
    es.onopen = () => setLive(true);
    es.onerror = () => setLive(false);
    es.onmessage = (e) => {
      try {
        const d = JSON.parse(e.data);
        if (d.type && d.type !== "hello") cb.current?.(d);
      } catch {
        /* ignore keep-alives */
      }
    };
    return () => es.close();
  }, []);

  return live;
}

// tiny debounce so a burst of events triggers one refetch
export function debounce(fn, ms = 400) {
  let t;
  return (...a) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...a), ms);
  };
}
