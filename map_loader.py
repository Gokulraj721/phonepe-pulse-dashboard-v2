import json
import os
import pandas as pd

# ✅ Years to include
years = ["2018", "2019", "2020", "2021", "2022", "2023", "2024"]

# ✅ Root directory
base_root = r"C:\Gokul Important things\Phone pay project\pulse\data\map\transaction\hover\country\india"

hover_records = []

for year in years:
    year_path = os.path.join(base_root, year)
    if not os.path.isdir(year_path):
        print(f"⛔ Skipping missing year folder: {year_path}")
        continue

    for quarter_file in os.listdir(year_path):
        if not quarter_file.endswith(".json"):
            continue

        file_path = os.path.join(year_path, quarter_file)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                hover_data = data.get("data", {}).get("hoverDataList")

                if not hover_data:
                    print(f"⚠️ No hover data found in: {file_path}")
                    continue

                for district_obj in hover_data:
                    district_name = district_obj.get("name")
                    metrics_list = district_obj.get("metric", [])

                    for metric in metrics_list:
                        if metric.get("type") == "TOTAL":
                            hover_records.append({
                                "year": year,
                                "quarter": int(quarter_file.strip(".json")),
                                "district": district_name,
                                "count": metric.get("count", 0),
                                "amount": metric.get("amount", 0)
                            })
                            break
        except Exception as e:
            print(f"⚠️ Skipped {file_path} due to error: {e}")

# ✅ Create output directory if missing
output_dir = r"C:\Gokul Important things\Phone pay project\output"
os.makedirs(output_dir, exist_ok=True)

# ✅ Save to CSV
df = pd.DataFrame(hover_records)
output_path = os.path.join(output_dir, "map_hover_transactions.csv")
df.to_csv(output_path, index=False)

# ✅ Summary
print(f"\n📊 Total records loaded: {len(df)}")
print("✅ CSV created at:", output_path)
