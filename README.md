# Wearable InfluxDB Simulator
A Docker-based wearable data simulator (Garmin Forerunner 265-style)
that generates realistic physiological metrics (heart rate, steps, stress, calories, distance) and stores them in InfluxDB 2.7.

The project is designed for:
•	testing time series pipelines
•	creating demos without real devices
•	integration with dashboards (Grafana)
•	research and experimentation


---

##  Architecture

- **Python** → wearable data simulation
- **InfluxDB 2.7** → time series storage
- **Docker / Docker Compose** → isolation and reproducibility

Each component is containerized and configurable via environment variables.

---

## Simulate Metrics

The simulator generates data once per second for a single activity:

•	Heart Rate (bpm)
•	Steps (cumulative)
•	Stress (0–100, derived from HR with time filter)
•	Calories (kcal)
•	Distance (meters)


Metrics are consistent with the selected activity type:
- `walking`
- `running`
- `cycling`

---

## Requirements

- Docker ≥ 20.x
- Docker Compose v2

---

## Quick start

1. Clone the repository:
  
   git clone https://github.com/alecsus1/wearable-influx-demo.git
   cd wearable-influx-demo
   docker compose up -d

   http://localhost:8086 (to view the influxDB UI)

