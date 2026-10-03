import { post } from "../api";

const OPTIONS = [
  ["normal", "Normal driving"],
  ["closure", "Eyes closed"],
  ["yawn", "Yawning"],
  ["nod", "Head nodding"],
  ["none", "Stop labelling"],
];

export default function ScenarioButtons({ label }) {
  return (
    <section className="panel">
      <h3>Test scenario</h3>
      <p className="muted">
        Press a scenario, act it out, then press Stop labelling. Wait for the status to return to Alert before
        starting the next one. Results appear in the Report tab.
      </p>
      <div className="row">
        {OPTIONS.map(([key, text]) => (
          <button key={key} className={`btn ${label === key ? "on" : ""}`} onClick={() => post(`/label/${key}`)}>
            {text}
          </button>
        ))}
      </div>
    </section>
  );
}
