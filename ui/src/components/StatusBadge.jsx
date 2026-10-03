const LABEL = {
  OK: "Alert",
  WARNING: "Getting drowsy",
  ALARM: "Wake up",
  LOW_CONFIDENCE: "Can't monitor",
  CALIBRATING: "Calibrating",
};

export default function StatusBadge({ m }) {
  const state = m?.state ?? "LOW_CONFIDENCE";
  const score = m?.fatigue_score ?? 0;
  const c = m?.components;
  return (
    <section className={`status ${state}`}>
      <h2>{LABEL[state]}</h2>
      <p className="reason">{m?.reason || (state === "OK" ? "Driver looks awake." : "\u00a0")}</p>
      <div className="bar"><div style={{ width: `${Math.round(score * 100)}%` }} /></div>
      <p className="score">Fatigue score {score.toFixed(2)}</p>
      {c && (
        <dl className="signals">
          <div><dt>Eyes closed</dt><dd>{m.closure_s.toFixed(1)} s</dd></div>
          <div><dt>PERCLOS</dt><dd>{Math.round(m.perclos * 100)}%</dd></div>
          <div><dt>Yawns (60 s)</dt><dd>{m.yawns}</dd></div>
          <div><dt>Head down</dt><dd>{m.head_down_s.toFixed(1)} s</dd></div>
          <div><dt>Nods (30 s)</dt><dd>{m.nods}</dd></div>
          <div><dt>Pitch change</dt><dd>{m.pitch_delta}&deg;</dd></div>
        </dl>
      )}
    </section>
  );
}
