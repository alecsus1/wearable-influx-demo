# -------------------------------
# simulator.py
# Punti A, B, C, D
# -------------------------------

import os
import sys
import time
import random
from datetime import datetime, timezone
from influxdb_client import InfluxDBClient, Point

# ============================
# Punto A - Setup e configurazione
# ============================

# Leggi variabili d'ambiente
INFLUXDB_URL = os.getenv("INFLUXDB_URL") #getenv: funzione del modulo os utilizzata per leggere le variabili d'ambiente del so in modo sicuro 
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")
ACTIVITY = os.getenv("ACTIVITY")

# Verifica variabili d'ambiente
missing_vars = []
#for con unpacking su lista di tuple: la prima variabile prende il primo elemento della tupla e la 
#seconda il secondo elemento
for var_name, var_value in [
    ("INFLUXDB_URL", INFLUXDB_URL),
    ("INFLUXDB_TOKEN", INFLUXDB_TOKEN),
    ("INFLUXDB_ORG", INFLUXDB_ORG),
    ("INFLUXDB_BUCKET", INFLUXDB_BUCKET)
]:
    #se la variabile non ha valori memorizza il nome della variabile vuota nell'array
    if not var_value:
        missing_vars.append(var_name)

if missing_vars:
    #.join: è un metodo delle stringhe che serve a concatenare una sequenza di stringhe con un separatore(in questo caso , + spazio)
    print(f"Errore: le seguenti variabili d'ambiente mancano: {', '.join(missing_vars)}") 
    sys.exit(1) #interrompe lo script - 1 indica errore in unix

# Inizializza client InfluxDB
client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG) #oggetto che parla con ifluxdb(connessione al DB)
write_api = client.write_api() #client.write_api(): metodo del client; write_api: oggetto specializzato per la scrittura

print("✅ Connessione a InfluxDB pronta!")
print(f"URL: {INFLUXDB_URL}, Org: {INFLUXDB_ORG}, Bucket: {INFLUXDB_BUCKET}")

# ============================
# Punto B - Schema dati Garmin-like
# ============================

COMMON_TAGS = {
    "device": "GarminForerunner265",
    "user": "Alex"
}

current_activity = ACTIVITY
activity_params = {
    "running": {"hr_min": 120, "hr_max": 180, "step_range": (1, 3), "calorie_factor": 0.05},
    "walking": {"hr_min": 80, "hr_max": 120, "step_range": (1, 2), "calorie_factor": 0.03},
    "cycling": {"hr_min": 100, "hr_max": 160, "step_range": (0, 0), "calorie_factor": 0.07}
}

# ============================
# Punto C - Generazione dati simulati
# ============================

# Valori iniziali
hr = random.randint(activity_params[current_activity]["hr_min"] + 5,
                    activity_params[current_activity]["hr_max"] - 5)  # bpm
steps = 0
calories = 0.0
distance = 0.0  # metri
stress_prev = (hr - activity_params[current_activity]["hr_min"]) / (
    activity_params[current_activity]["hr_max"] - activity_params[current_activity]["hr_min"]
) * 100
STEP_LENGTH = 0.78  # metri per passo

# ============================
# Punto D - Loop di simulazione e scrittura su InfluxDB
# ============================

try:
    while True:
        # --- aggiorna HR (piccola variazione casuale)
        hr += random.choice([-1, 0, 1]) #sceglie un elemento a caso nella lista con probabilità uniforme
        hr = max(activity_params[current_activity]["hr_min"],
                 min(activity_params[current_activity]["hr_max"], hr))

        # --- aggiorna passi e calorie
        steps += random.randint(1, 3)
        calories += 0.05 * (steps / 2)
        distance += steps * STEP_LENGTH

        # --- calcola stress in base ad HR
        base_stress = (hr - activity_params[current_activity]["hr_min"]) / (
            activity_params[current_activity]["hr_max"] - activity_params[current_activity]["hr_min"]
        ) * 100
        stress_raw = base_stress + random.uniform(-5, 5)
        stress_raw = max(0, min(100, stress_raw))
        
        # filtro temporale con aggiornamento stress_prev
        stress = 0.8 * stress_prev + 0.2 * stress_raw
        stress_prev = stress  # aggiorno per il ciclo successivo

        # --- timestamp corrente
        timestamp = datetime.now(timezone.utc)
        # --- crea point heart_rate
        #Point: classe di influxdb-client, serve a costruire un singolo record
        # / in python consente di spezzare una riga lunga e rende il codice leggibile
        point_hr = Point("heart_rate") \
            .tag("device", COMMON_TAGS["device"]) \
            .tag("user", COMMON_TAGS["user"]) \
            .tag("activity", current_activity) \
            .field("bpm", hr) \
            .time(timestamp)

        # --- crea point steps
        point_steps = Point("steps") \
            .tag("device", COMMON_TAGS["device"]) \
            .tag("user", COMMON_TAGS["user"]) \
            .tag("activity", current_activity) \
            .field("steps_cumulative", steps) \
            .time(timestamp)

        # --- crea point calories
        point_calories = Point("calories") \
            .tag("device", COMMON_TAGS["device"]) \
            .tag("user", COMMON_TAGS["user"]) \
            .tag("activity", current_activity) \
            .field("kcal", round(calories, 2)) \
            .time(timestamp)

        # --- crea point distance
        point_distance = Point("distance") \
            .tag("device", COMMON_TAGS["device"]) \
            .tag("user", COMMON_TAGS["user"]) \
            .tag("activity", current_activity) \
            .field("meters", round(distance, 2)) \
            .time(timestamp)
        
        #crea point stress

        point_stress = Point("stress")\
            .tag("device", COMMON_TAGS["device"]) \
            .tag("user", COMMON_TAGS["user"]) \
            .tag("activity", current_activity) \
            .field("level_float", stress)\
            .time(timestamp)

        # --- invia tutti i point a InfluxDB
        # .write: è il metodo che prende i point; liconverte nel formato influxdb (line protocol); li manda via HTTP al server
        # org=.... influxdb verifica che il token sia valido e che il token sia autorizzato per questa org e bucket
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=[point_hr, point_steps, point_calories, point_distance, point_stress])

        # --- logging per debug
        print(f"[{timestamp}] HR: {hr} bpm | Steps: {steps} | Calories: {calories:.2f} kcal | Distance: {distance:.2f} m | Stress: {stress:.2f}")
        print(f"hr={hr:.2f}, stress_raw={stress_raw:.2f}, stress_prev={stress_prev:.2f}, stress={stress:.2f}")

        # --- attende 1 secondo
        time.sleep(1)

except KeyboardInterrupt:
    print("Simulazione interrotta dall'utente")
