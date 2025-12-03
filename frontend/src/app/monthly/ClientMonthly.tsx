"use client"
import { useEffect, useMemo, useState } from "react"

type Airline = { name: string; iata_code: string }
type Period = { year: number; month: number }
type PredictionResponse = {
  airline: Airline
  year: number
  month: number
  prediction: {
    delay_probability: number
    delay_risk_category: "LOW" | "MEDIUM" | "HIGH"
    delay_risk_color: "green" | "yellow" | "red"
    predicted_delay_duration_formatted: string
  }
  metrics: { on_time_percentage: number; estimated_completion_factor: number }
  delay_causes: { cause: string; percentage: number; color: string }[]
}

const API_BASE =
  (process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000").replace(/\/+$/, "")

export default function ClientMonthly() {
  const [mounted, setMounted] = useState(false)
  const [airlines, setAirlines] = useState<Airline[]>([])
  const [periods, setPeriods] = useState<Period[]>([])
  const [year, setYear] = useState<number>(2025)
  const [month, setMonth] = useState<number>(12)
  const [airline, setAirline] = useState<string>("DL")
  const [loading, setLoading] = useState(false)
  const [err, setErr] = useState<string | null>(null)
  const [data, setData] = useState<PredictionResponse | null>(null)

  useEffect(() => {
    setMounted(true)
    fetch(`${API_BASE}/api/airlines`)
      .then((r) => r.json())
      .then((json) => setAirlines(json.airlines ?? []))
      .catch(() => setAirlines([]))

    // NOTE: read "periods" not "months"
    fetch(`${API_BASE}/api/airline-performance/available-months`)
      .then((r) => r.json())
      .then((json) => setPeriods(json.periods ?? []))
      .catch(() => setPeriods([]))
  }, [])

  const years = useMemo(() => {
    const fixed = [2022, 2023, 2024, 2025, 2026, 2027]
    const apiYears = Array.from(new Set(periods.map((p) => p.year)))
    return Array.from(new Set([...fixed, ...apiYears])).sort((a, b) => a - b)
  }, [periods])

  useEffect(() => {
    if (!mounted) return
    setLoading(true)
    setErr(null)
    fetch(
      `${API_BASE}/api/airline-performance/predict?year=${year}&month=${month}&airline=${airline}`
    )
      .then(async (r) => {
        if (!r.ok) throw new Error(`API ${r.status}`)
        const json = await r.json()
        setData(json)
        setLoading(false)
      })
      .catch((e) => {
        setErr(e?.message || "Failed to fetch")
        setLoading(false)
      })
  }, [mounted, year, month, airline])

  return (
    <main
      style={{ padding: 24, color: "#fff", background: "#0b1220", minHeight: "100vh" }}
      suppressHydrationWarning
    >
      <h1 style={{ fontSize: 28, fontWeight: 800 }}>Monthly Delay Predictor</h1>

      <div
        style={{
          marginTop: 16,
          display: "grid",
          gap: 16,
          gridTemplateColumns: "repeat(3, minmax(220px, 1fr))",
          alignItems: "end",
        }}
      >
        <label style={{ display: "grid", gap: 6 }}>
          <span style={{ fontSize: 12, color: "#cbd5e1" }}>Airline</span>
          <select
            value={airline}
            onChange={(e) => setAirline(e.target.value)}
            style={{
              padding: "10px 12px",
              borderRadius: 10,
              border: "1px solid #334155",
              background: "#0f172a",
              color: "#fff",
              fontSize: 14,
              minHeight: 40,
            }}
          >
            {airlines.length === 0 && <option value="DL">Delta (DL)</option>}
            {airlines.map((a) => (
              <option key={a.iata_code} value={a.iata_code}>
                {a.name} ({a.iata_code})
              </option>
            ))}
          </select>
        </label>

        <label style={{ display: "grid", gap: 6 }}>
          <span style={{ fontSize: 12, color: "#cbd5e1" }}>Year</span>
          <select
            value={year}
            onChange={(e) => setYear(Number(e.target.value))}
            style={{
              padding: "10px 12px",
              borderRadius: 10,
              border: "1px solid #334155",
              background: "#0f172a",
              color: "#fff",
              fontSize: 14,
              minHeight: 40,
            }}
          >
            {years.map((y) => (
              <option key={y} value={y}>
                {y}
              </option>
            ))}
          </select>
        </label>

        <label style={{ display: "grid", gap: 6 }}>
          <span style={{ fontSize: 12, color: "#cbd5e1" }}>Month</span>
          <select
            value={month}
            onChange={(e) => setMonth(Number(e.target.value))}
            style={{
              padding: "10px 12px",
              borderRadius: 10,
              border: "1px solid #334155",
              background: "#0f172a",
              color: "#fff",
              fontSize: 14,
              minHeight: 40,
            }}
          >
            {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div style={{ marginTop: 16 }}>
        {loading && <p>Loading prediction…</p>}
        {err && <p style={{ color: "crimson" }}>Error: {err}</p>}
        {!loading && !err && data && (
          <div
            style={{
              marginTop: 12,
              border: "1px solid #334155",
              borderRadius: 12,
              padding: 16,
              background: "rgba(255,255,255,0.06)",
              maxWidth: 720,
            }}
          >
            <h2 style={{ fontSize: 18, fontWeight: 700 }}>
              {data.airline?.name ?? airline} • {data.year}-
              {String(data.month).padStart(2, "0")}
            </h2>
            <p style={{ marginTop: 8 }}>
              Risk: {data.prediction.delay_risk_category} • Probability:{" "}
              {(data.prediction.delay_probability * 100).toFixed(1)}%
            </p>
            <p>Predicted delay: {data.prediction.predicted_delay_duration_formatted}</p>
            <p style={{ marginTop: 8 }}>
              On-time: {(data.metrics.on_time_percentage * 100).toFixed(1)}% • Completion factor:{" "}
              {(data.metrics.estimated_completion_factor * 100).toFixed(1)}%
            </p>
          </div>
        )}
      </div>
    </main>
  )
}