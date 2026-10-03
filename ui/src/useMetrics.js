import { useEffect, useState } from "react";
import { WS_URL } from "./api";

export function useMetrics() {
  const [m, setM] = useState(null);
  const [history, setHistory] = useState([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    let ws, retry, closed = false;
    const connect = () => {
      ws = new WebSocket(WS_URL);
      ws.onopen = () => setConnected(true);
      ws.onmessage = (e) => {
        const d = JSON.parse(e.data);
        setM(d);
        if (d.fatigue_score !== undefined) setHistory((h) => [...h.slice(-149), d]);
      };
      ws.onclose = () => {
        setConnected(false);
        if (!closed) retry = setTimeout(connect, 1000);
      };
    };
    connect();
    return () => {
      closed = true;
      clearTimeout(retry);
      ws && ws.close();
    };
  }, []);

  return { m, history, connected };
}
