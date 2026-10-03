import { useEffect, useState } from "react";
import { get, post } from "../api";

const pct = (v) => (v == null ? "n/a" : `${Math.round(v * 100)}%`);
const fix = (v, d = 1) => (v == null ? "n/a" : v.toFixed(d));
const NAMES = { normal: "Normal driving", closure: "Eyes closed", yawn: "Yawning", nod: "Head nodding" };

export default function ReportPage() {
  const [r, setR] = useState(null);

  useEffect(() => {
    let on = true;
    const load = () => get("/report").then((d) => on && setR(d)).catch(() => {});
    load();
    const id = setInterval(load, 2000);
    return () => { on = false; clearInterval(id); };
  }, []);

  if (!r) return <p className="muted">Loading report...</p>;
  const s = r.summary;

  return (
    <div className="report">
      <div className="headline">
        <div><b>{pct(s.recall)}</b><span>Detection rate ({s.detected_segments} of {s.positive_segments} drowsy scenarios caught)</span></div>
        <div><b>{pct(s.precision)}</b><span>Alert precision (alerts that were real)</span></div>
        <div><b>{fix(s.false_alarms_per_min, 2)}</b><span>False alarms per minute of normal driving</span></div>
        <div><b>{pct(s.face_detect_rate)}</b><span>Frames with a face found</span></div>
        <div><b>{pct(s.low_confidence_share)}</b><span>Time spent unable to monitor</span></div>
      </div>

      <table>
        <thead>
          <tr><th>Scenario</th><th>Runs</th><th>Caught</th><th>Avg time to alert</th><th>Alerts</th><th>Seconds</th></tr>
        </thead>
        <tbody>
          {r.scenarios.map((x) => (
            <tr key={x.label}>
              <td>{NAMES[x.label]}</td>
              <td>{x.segments}</td>
              <td>{x.detected == null ? "n/a" : `${x.detected}/${x.segments}`}</td>
              <td>{x.mean_latency_s == null ? "n/a" : `${fix(x.mean_latency_s)} s`}</td>
              <td>{x.alerts}</td>
              <td>{fix(x.seconds, 0)}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <p className="muted">
        Measured from {s.frames} frames of labelled test runs acted out by the team. A drowsy scenario counts as caught
        if a new warning or alarm starts while it runs. An alert during normal driving counts as a false alarm.
      </p>
      <button className="btn" onClick={() => post("/report/reset").then(() => setR(null))}>Clear results</button>
    </div>
  );
}
