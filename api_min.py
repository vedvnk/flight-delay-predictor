from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.get("/api/airlines")
def airlines():
    return jsonify({
        "airlines": [
            {"name": "Delta Air Lines", "iata_code": "DL"},
            {"name": "United Airlines", "iata_code": "UA"},
            {"name": "American Airlines", "iata_code": "AA"},
            {"name": "Southwest Airlines", "iata_code": "WN"},
            {"name": "JetBlue", "iata_code": "B6"},
            {"name": "Alaska Airlines", "iata_code": "AS"},
        ]
    })

@app.get("/api/airline-performance/available-months")
def months():
    periods = [{"year": y, "month": m} for y in range(2022, 2028) for m in range(1, 13)]
    return jsonify({"periods": periods})

@app.get("/api/airline-performance/predict")
def predict():
    year = int(request.args.get("year", 2025))
    month = int(request.args.get("month", 12))
    airline = request.args.get("airline", "DL")
    data = {
        "airline": {"name": "Delta Air Lines" if airline == "DL" else "Airline", "iata_code": airline},
        "year": year,
        "month": month,
        "prediction": {
            "delay_probability": 0.27,
            "delay_risk_category": "MEDIUM",
            "delay_risk_color": "yellow",
            "predicted_delay_duration_formatted": "12 min",
        },
        "metrics": {"on_time_percentage": 0.81, "estimated_completion_factor": 0.98},
        "delay_causes": [
            {"cause": "Weather", "percentage": 0.35, "color": "orange"},
            {"cause": "Late inbound", "percentage": 0.25, "color": "purple"},
        ],
    }
    return jsonify(data)

@app.get("/flights/status")
def flights_status():
    from_code = request.args.get("from", "LAX")
    to_code = request.args.get("to", "ORD")
    date = request.args.get("date", "2025-09-21")
    flights = [
        {
            "flightNumber": "DL123",
            "airline": "Delta",
            "from": from_code,
            "to": to_code,
            "departureTime": "09:30",
            "arrivalTime": "15:05",
            "delayRisk": "LOW",
            "delayProbability": 0.12,
            "predictedDelayMinutes": 5,
        },
        {
            "flightNumber": "UA456",
            "airline": "United",
            "from": from_code,
            "to": to_code,
            "departureTime": "11:20",
            "arrivalTime": "17:00",
            "delayRisk": "MEDIUM",
            "delayProbability": 0.34,
            "predictedDelayMinutes": 18,
        },
    ]
    return jsonify({"flights": flights, "lastUpdated": date})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

