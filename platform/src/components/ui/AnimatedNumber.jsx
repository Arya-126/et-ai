import { useEffect, useRef, useState } from "react";

// Count-up animation for KPI numbers. Renders the raw value unchanged when it
// isn't a finite number (e.g. "LLM", "offline", "—", "…") so it's drop-in safe.
export default function AnimatedNumber({ value, duration = 900, format, className = "" }) {
  const target = typeof value === "number" ? value : Number(value);
  const animatable = Number.isFinite(target);
  const [display, setDisplay] = useState(animatable ? 0 : value);
  const fromRef = useRef(0);
  const rafRef = useRef(0);

  useEffect(() => {
    if (!animatable) { setDisplay(value); return; }
    const reduce = window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches;
    if (reduce) { setDisplay(target); return; }

    const from = fromRef.current;
    const start = performance.now();
    const ease = (t) => 1 - Math.pow(1 - t, 3); // easeOutCubic

    const tick = (now) => {
      const t = Math.min(1, (now - start) / duration);
      const v = from + (target - from) * ease(t);
      setDisplay(v);
      if (t < 1) rafRef.current = requestAnimationFrame(tick);
      else fromRef.current = target;
    };
    rafRef.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(rafRef.current);
  }, [target, animatable, duration, value]);

  if (!animatable) return <span className={className}>{display}</span>;

  const rounded = Number.isInteger(target) ? Math.round(display) : display;
  return <span className={className}>{format ? format(rounded) : rounded.toLocaleString("en-IN")}</span>;
}
