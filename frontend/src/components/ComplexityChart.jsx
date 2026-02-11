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
  // radon is an object with { blocks: [...], average_complexity, total_functions, total_complexity }
  if (!radon || !radon.blocks || !Array.isArray(radon.blocks) || radon.blocks.length === 0) {
    return <p>No complexity data available.</p>;
  }

  const data = radon.blocks
    .slice(0, 20) // Limit to top 20 for readability
    .map((block) => ({
      name: block.name || "unknown",
      complexity: block.complexity || 0,
      grade: block.grade || "?",
    }));

  const getColor = (score) => {
    if (score <= 5) return "var(--secondary, #22c55e)";
    if (score <= 10) return "var(--warning, #f59e0b)";
    return "var(--danger, #ef4444)";
  };

  if (data.length === 0) return <p>No complexity data available.</p>;

  return (
    <div className="complexity-chart">
      <div className="chart-header">
        <h3>Function Complexity Analysis</h3>
        <div className="legend">
          <div className="legend-item">
            <span className="legend-color low"></span>
            Low (≤5)
          </div>
          <div className="legend-item">
            <span className="legend-color medium"></span>
            Medium (6-10)
          </div>
          <div className="legend-item">
            <span className="legend-color high"></span>
            High (&gt;10)
          </div>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={data}>
          <XAxis
            dataKey="name"
            tick={{ fontSize: 12 }}
            angle={-45}
            textAnchor="end"
            height={80}
          />
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
