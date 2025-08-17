import os
import json
import csv

# ✅ Your actual base directory
base_dir = "pulse/data/aggregated/user/country/india"

# 📁 Output CSV file
output_csv = "user_device_data.csv"

# 🧱 CSV headers
headers = ["year", "quarter", "brand", "count", "percentage"]

# 📦 Store extracted rows
device_data = []

# 🔍 Traverse year folders
for year_folder in os.listdir(base_dir):
    year_path = os.path.join(base_dir, year_folder)
    if not os.path.isdir(year_path):
        continue

    for file_name in os.listdir(year_path):
        if not file_name.endswith(".json"):
            continue

        file_path = os.path.join(year_path, file_name)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # ✅ Defensive check for usersByDevice
            users_by_device = data.get("data", {}).get("usersByDevice")
            if users_by_device:
                for device in users_by_device:
                    device_data.append({
                        "year": year_folder,
                        "quarter": file_name.replace(".json", ""),
                        "brand": device.get("brand", "Unknown"),
                        "count": device.get("count", 0),
                        "percentage": device.get("percentage", 0.0)
                    })
            else:
                print(f"⚠️ Skipping file with missing usersByDevice: {file_path}")

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")

# 📝 Write to CSV
with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=headers)
    writer.writeheader()
    writer.writerows(device_data)

print(f"✅ Extraction complete. Data saved to {output_csv}")
