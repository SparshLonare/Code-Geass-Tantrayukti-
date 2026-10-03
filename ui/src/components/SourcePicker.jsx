import { useEffect, useState } from "react";
import { get, post } from "../api";

export default function SourcePicker({ current }) {
  const [options, setOptions] = useState(["webcam"]);
  useEffect(() => {
    get("/sources").then((d) => setOptions(d.sources)).catch(() => {});
  }, []);
  return (
    <label className="source">
      Source
      <select value={current ?? "webcam"} onChange={(e) => post("/source", { source: e.target.value })}>
        {options.map((o) => <option key={o} value={o}>{o === "webcam" ? "Webcam" : o}</option>)}
      </select>
    </label>
  );
}
