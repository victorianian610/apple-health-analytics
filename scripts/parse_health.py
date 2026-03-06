import xml.etree.ElementTree as ET
import pandas as pd
from tqdm import tqdm
import os

XML_PATH = "data/export.xml"
OUT_DIR  = "data"

# Metric type → output filename
METRICS = {
    "HKQuantityTypeIdentifierStepCount":            "steps.csv",
    "HKQuantityTypeIdentifierHeartRate":            "heart_rate.csv",
    "HKCategoryTypeIdentifierSleepAnalysis":        "sleep.csv",
    "HKQuantityTypeIdentifierActiveEnergyBurned":   "active_calories.csv",
    "HKQuantityTypeIdentifierDistanceWalkingRunning": "distance.csv",
}

def parse_records(xml_path):
    print("Parsing XML — this may take a minute for large files...")
    tree = ET.parse(xml_path)
    root = tree.getroot()

    buckets = {k: [] for k in METRICS}

    for record in tqdm(root.iter("Record")):
        rtype = record.attrib.get("type", "")
        if rtype in METRICS:
            buckets[rtype].append({
                "start":  record.attrib.get("startDate"),
                "end":    record.attrib.get("endDate"),
                "value":  record.attrib.get("value"),
                "unit":   record.attrib.get("unit"),
                "source": record.attrib.get("sourceName"),
            })

    return buckets

def parse_workouts(root):
    workouts = []
    for w in root.iter("Workout"):
        workouts.append({
            "activity":  w.attrib.get("workoutActivityType", "").replace("HKWorkoutActivityType", ""),
            "start":     w.attrib.get("startDate"),
            "end":       w.attrib.get("endDate"),
            "duration_min": float(w.attrib.get("duration", 0)),
            "calories":  w.attrib.get("totalEnergyBurned"),
            "distance":  w.attrib.get("totalDistance"),
        })
    return workouts

def save_csvs(buckets, root):
    for metric_type, rows in buckets.items():
        if rows:
            fname = METRICS[metric_type]
            df = pd.DataFrame(rows)
            df["start"] = pd.to_datetime(df["start"])
            df["end"]   = pd.to_datetime(df["end"])
            df["value"] = pd.to_numeric(df["value"], errors="coerce")
            df.to_csv(os.path.join(OUT_DIR, fname), index=False)
            print(f"✅ Saved {len(df):,} rows → {fname}")

    # Workouts
    tree = ET.parse(XML_PATH)
    workouts = parse_workouts(tree.getroot())
    if workouts:
        df_w = pd.DataFrame(workouts)
        df_w["start"] = pd.to_datetime(df_w["start"])
        df_w["end"]   = pd.to_datetime(df_w["end"])
        df_w.to_csv(os.path.join(OUT_DIR, "workouts.csv"), index=False)
        print(f"✅ Saved {len(df_w):,} rows → workouts.csv")

if __name__ == "__main__":
    tree = ET.parse(XML_PATH)
    root = tree.getroot()
    buckets = {k: [] for k in METRICS}
    print("Parsing XML — this may take a minute...")
    for record in tqdm(root.iter("Record")):
        rtype = record.attrib.get("type", "")
        if rtype in METRICS:
            buckets[rtype].append({
                "start":  record.attrib.get("startDate"),
                "end":    record.attrib.get("endDate"),
                "value":  record.attrib.get("value"),
                "unit":   record.attrib.get("unit"),
                "source": record.attrib.get("sourceName"),
            })
    save_csvs(buckets, root)
    print("\n🎉 All done! Check your data/ folder.")