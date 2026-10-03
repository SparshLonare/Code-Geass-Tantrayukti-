import { LineChart, Line, YAxis, ReferenceLine, ResponsiveContainer } from "recharts";

export default function LiveChart({ history }) {
  return (
    <section className="panel">
      <h3>Live signals</h3>
      <div className="chart">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={history} margin={{ top: 4, right: 4, bottom: 0, left: 0 }}>
            <YAxis domain={[0, 1]} width={28} tick={{ fill: "#8fa3b8", fontSize: 11 }} />
            <ReferenceLine y={0.9} stroke="#ef4444" strokeDasharray="4 4" />
            <ReferenceLine y={0.5} stroke="#f59e0b" strokeDasharray="4 4" />
            <Line dataKey="fatigue_score" name="Fatigue score" stroke="#e8f0f8" strokeWidth={2.5} dot={false} isAnimationActive={false} />
            <Line dataKey="blink" name="Eye closure" stroke="#38bdf8" dot={false} isAnimationActive={false} />
            <Line dataKey="perclos" name="PERCLOS" stroke="#a78bfa" dot={false} isAnimationActive={false} />
            <Line dataKey="jaw" name="Mouth open" stroke="#34d399" dot={false} isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <p className="legend">
        <i style={{ background: "#e8f0f8" }} />Fatigue score
        <i style={{ background: "#38bdf8" }} />Eye closure
        <i style={{ background: "#a78bfa" }} />PERCLOS
        <i style={{ background: "#34d399" }} />Mouth open
      </p>
    </section>
  );
}
