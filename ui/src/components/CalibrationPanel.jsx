import { post } from "../api";

export default function CalibrationPanel({ m }) {
  const c = m?.calibration;
  return (
    <section className="panel">
      <h3>Calibration</h3>
      <p className="muted">
        Sets thresholds from this person's own face. Look at the camera and blink normally for 12 seconds.
        Recalibrate when the driver changes.
      </p>
      <button className="btn primary" disabled={c?.active} onClick={() => post("/calibrate/start")}>
        {c?.active ? `Calibrating ${Math.round(c.progress * 100)}%` : c?.done ? "Recalibrate" : "Start calibration"}
      </button>
      {c?.active && <div className="bar slim"><div style={{ width: `${c.progress * 100}%` }} /></div>}
      {c?.message && !c.active && <p className={c.failed ? "bad" : "good"}>{c.message}</p>}
      {c?.done && (
        <p className="muted">
          Open-eye ratio {c.baseline_ear} &middot; blink baseline {c.baseline_blink}
        </p>
      )}
      <p className="muted">Lighting {m ? Math.round(m.brightness * 100) : 0}%{m?.dark_mode ? " (low-light boost on)" : ""}. Face found in {m ? Math.round(m.detect_rate * 100) : 0}% of recent frames. {m?.fps ?? 0} fps.</p>
    </section>
  );
}
