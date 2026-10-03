import { useEffect, useRef, useState } from "react";

export default function AlarmSound({ active }) {
  const [enabled, setEnabled] = useState(false);
  const ctxRef = useRef(null);

  const toggle = () => {
    if (!ctxRef.current) ctxRef.current = new (window.AudioContext || window.webkitAudioContext)();
    ctxRef.current.resume();   // browsers need a click before audio can play
    setEnabled((e) => !e);
  };

  useEffect(() => {
    if (!enabled || !active) return;
    const beep = () => {
      const ctx = ctxRef.current;
      const o = ctx.createOscillator();
      const g = ctx.createGain();
      o.type = "square";
      o.frequency.value = 880;
      g.gain.value = 0.15;
      o.connect(g);
      g.connect(ctx.destination);
      o.start();
      o.stop(ctx.currentTime + 0.25);
    };
    beep();
    const id = setInterval(beep, 600);
    return () => clearInterval(id);
  }, [active, enabled]);

  return (
    <button className={`btn ${enabled ? "on" : ""}`} onClick={toggle}>
      {enabled ? "Alarm sound on" : "Turn on alarm sound"}
    </button>
  );
}
