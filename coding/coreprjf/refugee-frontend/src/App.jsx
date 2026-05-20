import { useState } from "react";
import axios from "axios";

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const runOptimization = async () => {
    setLoading(true);
    try {
      const res = await axios.get("http://localhost:5000/optimize");
      setData(res.data);
    } catch (err) {
      console.error(err);
      alert("Backend not responding");
    }
    setLoading(false);
  };

  return (
    <div
  style={{
    minHeight: "100vh",
    overflowX: "hidden",
    backgroundColor: "#b4481d",
    fontFamily: "Segoe UI, sans-serif",
    padding: "40px"
  }}
>
      {/* Header */}
      <h1 style={{
        color: "#111827",
        marginBottom: 20,
        fontWeight: "bold"
      }}>
        Refugee Allocation Optimization Dashboard
      </h1>

      <button
        onClick={runOptimization}
        style={{
          padding: "10px 20px",
          backgroundColor: "#2563eb",
          color: "white",
          border: "none",
          borderRadius: 8,
          cursor: "pointer",
          fontWeight: "bold"
        }}
      >
        Run Optimization
      </button>

      {loading && <p style={{ marginTop: 20 }}>Running optimization...</p>}

      {data && (
        <div style={{ marginTop: 40 }}>

          {/* SUMMARY CARDS */}
          <div style={{
            display: "flex",
            gap: 20,
            flexWrap: "wrap"
          }}>
            <Card title="Total Refugees" value={data.original_refugees} />
            <Card title="Allocated" value={data.total_allocated_refugees} />
            <Card title="Unallocated" value={data.unallocated_refugees} />
            <Card title="Objective Score" value={data.objective_value} />
            <Card title="Solve Time (ms)" value={data.solve_time_ms} />
          </div>

          {/* PROGRESS */}
          <div style={{ marginTop: 40 }}>
            <h3 style={{ color: "#111827" }}>Allocation Coverage</h3>
            <ProgressBar
              percentage={
                (data.total_allocated_refugees /
                  data.original_refugees) *
                100
              }
            />
          </div>

          {/* TABLE */}
          <div style={{ marginTop: 40 }}>
            <h3 style={{ color: "#111827" }}>City Allocations</h3>

            <table style={{
              width: "100%",
              marginTop: 15,
              backgroundColor: "white",
              borderRadius: 12,
              overflow: "hidden",
              boxShadow: "0 6px 12px rgba(0,0,0,0.08)",
              borderCollapse: "collapse"
            }}>

              <thead style={{ backgroundColor: "#1f2937", color: "white" }}>
                <tr>
                  <th style={cellStyle}>City</th>
                  <th style={cellStyle}>Allocated</th>
                  <th style={cellStyle}>Capacity</th>
                  <th style={cellStyle}>Usage %</th>
                </tr>
              </thead>

              <tbody>
  {data.city_allocations.map((city, index) => {
    const usage = (city.allocated_refugees / city.capacity) * 100;

    return (
      <tr
        key={index}
        style={{
          backgroundColor: index % 2 === 0 ? "white" : "#f3f4f6"
        }}
      >
        <td style={cellStyle}>{city.city}</td>
        <td style={cellStyle}>{city.allocated_refugees}</td>
        <td style={cellStyle}>{city.capacity}</td>
        <td style={cellStyle}>{usage.toFixed(1)}%</td>
      </tr>
    );
  })}
</tbody>

            </table>
          </div>

        </div>
      )}
    </div>
  );
}

function Card({ title, value }) {
  return (
    <div style={{
      flex: "1 1 220px",
      backgroundColor: "white",
      padding: 25,
      borderRadius: 12,
      boxShadow: "0 6px 12px rgba(0,0,0,0.08)"
    }}>
      <h4 style={{ color: "#343434", marginBottom: 8 }}>{title}</h4>
      <h2 style={{ color: "#111827" }}>{value}</h2>
    </div>
  );
}

function ProgressBar({ percentage }) {
  return (
    <div style={{
      width: "100%",
      backgroundColor: "#e5e7eb",
      borderRadius: 8,
      overflow: "hidden",
      height: 28
    }}>
      <div style={{
        width: `${percentage}%`,
        backgroundColor: "#059669",
        height: "100%",
        textAlign: "center",
        color: "white",
        fontWeight: "bold",
        lineHeight: "28px"
      }}>
        {percentage.toFixed(1)}%
      </div>
    </div>
  );
}

const cellStyle = {
  padding: 12,
  textAlign: "center",
  borderBottom: "1px solid #205dd6",
  color: "#111827",          // ADD THIS
  backgroundColor: "white"  
};

export default App;