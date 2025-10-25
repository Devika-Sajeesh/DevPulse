import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

export default function ComplexityChart({ radon }) {
  if (!radon || !Array.isArray(radon)) return null;

  // Safely parse Radon output
  const data = radon
    .filter((item) => item.line.includes(" - ") && /\(\d+\)/.test(item.line))
    .map((item) => {
      const parts = item.line.split(" - ");
      const funcNamePart = parts[0].trim().split(" ");
      const func = funcNamePart.length > 1 ? funcNamePart[1] : funcNamePart[0];
      const match = parts[1].match(/\((\d+)\)/);
      const grade = match ? parseInt(match[1]) : 0;
      return { name: func, complexity: grade };
    });

  const getColor = (score) => {
    if (score <= 5) return "#10b981"; // Green - good
    if (score <= 10) return "#f59e0b"; // Orange - medium
    return "#ef4444"; // Red - bad
  };

  if (data.length === 0) return <p>No complexity data available.</p>;

  return (
    <div className="complexity-chart">
      <div className="chart-header">
        <h3>Function Complexity Analysis</h3>
        <div className="legend">
          <div className="legend-item">
            <span className="legend-color low"></span> Low
          </div>
          <div className="legend-item">
            <span className="legend-color medium"></span> Medium
          </div>
          <div className="legend-item">
            <span className="legend-color high"></span> High
          </div>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={data}>
          <XAxis dataKey="name" tick={{ fontSize: 12 }} />
          <YAxis />
          <Tooltip
            formatter={(value) => [`Complexity: ${value}`, ""]}
            labelFormatter={(value) => `Function: ${value}`}
          />
          <Bar dataKey="complexity" name="Complexity">
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getColor(entry.complexity)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
