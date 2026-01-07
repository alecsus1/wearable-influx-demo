# Wearable InfluxDB Simulator
Simulatore di dati wearable (stile Garmin Forerunner 265) basato su Docker,  
che genera metriche fisiologiche realistiche (heart rate, steps, stress, calorie, distanza)
e le salva in InfluxDB 2.7.

Il progetto è pensato per:
- testare pipeline di time-series
- fare demo senza dispositivi reali
- integrazione con dashboard (Grafana)
- ricerca e sperimentazione

---

## 🧠 Architettura

- **Python** → simulazione dati wearable
- **InfluxDB 2.7** → storage time-series
- **Docker / Docker Compose** → isolamento e riproducibilità

Ogni componente è containerizzata e configurabile tramite variabili d’ambiente.

---

## 📊 Metriche simulate

Il simulatore genera dati una volta al secondo per una singola attività:

- Heart Rate (bpm)
- Steps (cumulativi)
- Stress (0–100, derivato da HR con filtro temporale)
- Calories (kcal)
- Distance (metri)

Le metriche sono coerenti con il tipo di attività selezionata:
- `walking`
- `running`
- `cycling`

---

## ⚙️ Requisiti

- Docker ≥ 20.x
- Docker Compose v2

---

## 🚀 Avvio rapido

1. Clona il repository:
   ```bash
   git clone <url-repo>
   cd wearable-influx
