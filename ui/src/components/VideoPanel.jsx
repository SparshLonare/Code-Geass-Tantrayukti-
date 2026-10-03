import { useState } from "react";
import { API } from "../api";

export default function VideoPanel({ state, error }) {
  const [k, setK] = useState(0);
  return (
    <div className={`video ${state}`}>
      <img
        key={k}
        src={`${API}/video?c=${k}`}
        alt="Driver camera"
        onError={() => setTimeout(() => setK((x) => x + 1), 1000)}
      />
      {error && <div className="video-error">{error}</div>}
    </div>
  );
}
