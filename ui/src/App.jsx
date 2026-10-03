import { useState } from "react";
import { useMetrics } from "./useMetrics";
import VideoPanel from "./components/VideoPanel";
import StatusBadge from "./components/StatusBadge";
import LiveChart from "./components/LiveChart";
import CalibrationPanel from "./components/CalibrationPanel";
import ScenarioButtons from "./components/ScenarioButtons";
import SourcePicker from "./components/SourcePicker";
import AlarmSound from "./components/AlarmSound";
import ReportPage from "./components/ReportPage";

export default function App() {
  const { m, history, connected } = useMetrics();
  const [tab, setTab] = useState("live");
  const state = m?.state ?? "LOW_CONFIDENCE";

  return (
    <div className="app">
      <header className="top">
        <div className="brand">
          <span className={`dot ${connected ? "on" : ""}`} title={connected ? "Connected" : "Backend offline"} />
          Wakeup SID!!
        </div>
        <nav>
          <button className={`tab ${tab === "live" ? "active" : ""}`} onClick={() => setTab("live")}>Live</button>
          <button className={`tab ${tab === "report" ? "active" : ""}`} onClick={() => setTab("report")}>Reliability report</button>
        </nav>
        <div className="tools">
          <SourcePicker current={m?.source} />
          <AlarmSound active={state === "ALARM"} />
        </div>
      </header>

      {!connected && <p className="banner">Backend not reachable. Start it with: uvicorn server:app --port 8000</p>}

      {tab === "live" ? (
        <main className="live">
          <div className="left">
            <VideoPanel state={state} error={m?.error} />
            <LiveChart history={history} />
          </div>
          <div className="right">
            <StatusBadge m={m} />
            <CalibrationPanel m={m} />
            <ScenarioButtons label={m?.label} />
          </div>
        </main>
      ) : (
        <ReportPage />
      )}
    </div>
  );
}
