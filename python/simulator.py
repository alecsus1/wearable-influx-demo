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
# A - Setup and configuration
# ============================

INFLUXDB_URL = os.getenv("INFLUXDB_URL") 
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")
ACTIVITY = os.getenv("ACTIVITY")


missing_vars = []

for var_name, var_value in [
    ("INFLUXDB_URL", INFLUXDB_URL),
    ("INFLUXDB_TOKEN", INFLUXDB_TOKEN),
    ("INFLUXDB_ORG", INFLUXDB_ORG),
    ("INFLUXDB_BUCKET", INFLUXDB_BUCKET)
]:
    
    if not var_value:
        missing_vars.append(var_name)

if missing_vars:
   
    print(f"Error: The following environment variables are missing: {', '.join(missing_vars)}") 
    sys.exit(1) 


client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG) 
write_api = client.write_api() 

print("Connection to InfluxDB ready!")
print(f"URL: {INFLUXDB_URL}, Org: {INFLUXDB_ORG}, Bucket: {INFLUXDB_BUCKET}")

# ============================
# B - Garmin-like data schema
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
# C - Simulated data generation
# ============================

# Initial values
hr = random.randint(activity_params[current_activity]["hr_min"] + 5,
                    activity_params[current_activity]["hr_max"] - 5)  # bpm
steps = 0
calories = 0.0
distance = 0.0  # meters
stress_prev = (hr - activity_params[current_activity]["hr_min"]) / (
    activity_params[current_activity]["hr_max"] - activity_params[current_activity]["hr_min"]
) * 100
STEP_LENGTH = 0.78  # meters for step

# ============================
# D - Simulation loop and writing to InfluxDB
# ============================

try:
    while True:
        # --- Update HR (small random variation)
        hr += random.choice([-1, 0, 1])
        hr = max(activity_params[current_activity]["hr_min"],
                 min(activity_params[current_activity]["hr_max"], hr))

        # --- Update steps and calories
        steps += random.randint(1, 3)
        calories += 0.05 * (steps / 2)
        distance += steps * STEP_LENGTH

        # --- calculate stress based on HR
        base_stress = (hr - activity_params[current_activity]["hr_min"]) / (
            activity_params[current_activity]["hr_max"] - activity_params[current_activity]["hr_min"]
        ) * 100
        stress_raw = base_stress + random.uniform(-5, 5)
        stress_raw = max(0, min(100, stress_raw))
        
        # time filter with stress_prev update
        stress = 0.8 * stress_prev + 0.2 * stress_raw
        stress_prev = stress  # update for the next cycle

        # --- current timestamp 
        timestamp = datetime.now(timezone.utc)
        #heart_rate
        point_hr = Point("heart_rate") \
            .tag("device", COMMON_TAGS["device"]) \
            .tag("user", COMMON_TAGS["user"]) \
            .tag("activity", current_activity) \
            .field("bpm", hr) \
            .time(timestamp)

        #steps
        point_steps = Point("steps") \
            .tag("device", COMMON_TAGS["device"]) \
            .tag("user", COMMON_TAGS["user"]) \
            .tag("activity", current_activity) \
            .field("steps_cumulative", steps) \
            .time(timestamp)

        #calories
        point_calories = Point("calories") \
            .tag("device", COMMON_TAGS["device"]) \
            .tag("user", COMMON_TAGS["user"]) \
            .tag("activity", current_activity) \
            .field("kcal", round(calories, 2)) \
            .time(timestamp)

        #distance
        point_distance = Point("distance") \
            .tag("device", COMMON_TAGS["device"]) \
            .tag("user", COMMON_TAGS["user"]) \
            .tag("activity", current_activity) \
            .field("meters", round(distance, 2)) \
            .time(timestamp)
        
        #stress
        point_stress = Point("stress")\
            .tag("device", COMMON_TAGS["device"]) \
            .tag("user", COMMON_TAGS["user"]) \
            .tag("activity", current_activity) \
            .field("level_float", stress)\
            .time(timestamp)

 
        
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=[point_hr, point_steps, point_calories, point_distance, point_stress])

        # --- logging for debug
        print(f"[{timestamp}] HR: {hr} bpm | Steps: {steps} | Calories: {calories:.2f} kcal | Distance: {distance:.2f} m | Stress: {stress:.2f}")
        print(f"hr={hr:.2f}, stress_raw={stress_raw:.2f}, stress_prev={stress_prev:.2f}, stress={stress:.2f}")

        # --- waits 1 second
        time.sleep(1)

except KeyboardInterrupt:
    print("Simulation interrupted by user")
