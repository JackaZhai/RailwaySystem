import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import { LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { MapContainer, TileLayer, CircleMarker, Tooltip as LeafletTooltip } from "react-leaflet";
import "leaflet/dist/leaflet.css";

interface PassengerFlowSummary {
  station: string;
  line: string;
  total_in: number;
  total_out: number;
}

interface TemporalTrendPoint {
  timestamp: string;
  passengers_in: number;
  passengers_out: number;
}

interface SpatialDistributionPoint {
  station: string;
  total_in: number;
  total_out: number;
}

interface Recommendation {
  line: string;
  recommendation: string;
  rationale: string;
}

interface StationMetric {
  station: string;
  total_passengers: number;
  average_headway: number;
  peak_hour: number | null;
}

const defaultPosition: [number, number] = [37.7749, -122.4194];
const stationCoordinates: Record<string, [number, number]> = {
  Central: [37.7749, -122.4194],
};

function App() {
  const [flow, setFlow] = useState<PassengerFlowSummary[]>([]);
  const [trend, setTrend] = useState<TemporalTrendPoint[]>([]);
  const [spatial, setSpatial] = useState<SpatialDistributionPoint[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [metrics, setMetrics] = useState<StationMetric[]>([]);
  const [filters, setFilters] = useState({ line: "", station: "" });

  useEffect(() => {
    axios.get<PassengerFlowSummary[]>("/api/analytics/flow/").then((response) => setFlow(response.data));
    axios.get<TemporalTrendPoint[]>("/api/analytics/temporal/?freq=H").then((response) => setTrend(response.data));
    axios.get<SpatialDistributionPoint[]>("/api/analytics/spatial/").then((response) => setSpatial(response.data));
    axios.get<Recommendation[]>("/api/lines/recommendations/").then((response) => setRecommendations(response.data));
    axios.get<StationMetric[]>("/api/stations/metrics/").then((response) => setMetrics(response.data));
  }, []);

  const filteredFlow = useMemo(() => {
    return flow.filter((item) => {
      const lineMatches = filters.line ? item.line === filters.line : true;
      const stationMatches = filters.station ? item.station === filters.station : true;
      return lineMatches && stationMatches;
    });
  }, [flow, filters]);

  return (
    <div className="app-container">
      <header className="header">
        <h1>Railway Operations Dashboard</h1>
      </header>

      <main className="dashboard">
        <section className="panel">
          <h2>Passenger Flow</h2>
          <div className="filters">
            <input
              placeholder="Filter by line"
              value={filters.line}
              onChange={(event) => setFilters((prev) => ({ ...prev, line: event.target.value }))}
            />
            <input
              placeholder="Filter by station"
              value={filters.station}
              onChange={(event) => setFilters((prev) => ({ ...prev, station: event.target.value }))}
            />
          </div>
          <table className="table">
            <thead>
              <tr>
                <th>Station</th>
                <th>Line</th>
                <th>Total In</th>
                <th>Total Out</th>
              </tr>
            </thead>
            <tbody>
              {filteredFlow.map((item) => (
                <tr key={`${item.station}-${item.line}`}>
                  <td>{item.station}</td>
                  <td>{item.line}</td>
                  <td>{item.total_in}</td>
                  <td>{item.total_out}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        <section className="panel">
          <h2>Line Recommendations</h2>
          <ul>
            {recommendations.map((item) => (
              <li key={item.line}>
                <strong>{item.line}:</strong> {item.recommendation}
                <p>{item.rationale}</p>
              </li>
            ))}
          </ul>
        </section>

        <section className="panel" style={{ gridColumn: "1 / span 2" }}>
          <h2>Temporal Trend</h2>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={trend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" hide />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="passengers_in" stroke="#2563eb" />
              <Line type="monotone" dataKey="passengers_out" stroke="#f97316" />
            </LineChart>
          </ResponsiveContainer>
        </section>

        <section className="panel">
          <h2>Station Metrics</h2>
          <table className="table">
            <thead>
              <tr>
                <th>Station</th>
                <th>Total</th>
                <th>Avg Headway (min)</th>
                <th>Peak Hour</th>
              </tr>
            </thead>
            <tbody>
              {metrics.map((metric) => (
                <tr key={metric.station}>
                  <td>{metric.station}</td>
                  <td>{metric.total_passengers}</td>
                  <td>{metric.average_headway.toFixed(2)}</td>
                  <td>{metric.peak_hour ?? "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        <section className="panel">
          <h2>Spatial Distribution</h2>
          <MapContainer center={defaultPosition} zoom={12} className="map-container">
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            {spatial.map((point) => {
              const position = stationCoordinates[point.station] ?? defaultPosition;
              return (
              <CircleMarker
                key={point.station}
                center={position}
                radius={Math.max(5, (point.total_in + point.total_out) / 100)}
                color="#2563eb"
              >
                <LeafletTooltip>
                  {point.station}: {point.total_in + point.total_out} passengers
                </LeafletTooltip>
              </CircleMarker>
            );
            })}
          </MapContainer>
        </section>
      </main>
    </div>
  );
}

export default App;
