import json
import os
import csv

base_path = r"C:\Gokul Important things\Phone pay project\pulse\data\aggregated\transaction\country\india"
output_file = "transaction_categories.csv"
data_list = []

for year in os.listdir(base_path):
    year_path = os.path.join(base_path, year)
    if os.path.isdir(year_path):
        for file in os.listdir(year_path):
            if file.endswith(".json"):
                file_path = os.path.join(year_path, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    json_data = json.load(f)
                    quarter = os.path.splitext(file)[0]
                    categories = json_data.get("data", {}).get("transactionData", [])
                    for entry in categories:
                        name = entry.get("name", "")
                        for instrument in entry.get("paymentInstruments", []):
                            if instrument.get("type") == "TOTAL":
                                count = instrument.get("count", 0)
                                amount = instrument.get("amount", 0.0)
                                data_list.append({
                                    "year": year,
                                    "quarter": quarter,
                                    "category": name,
                                    "count": count,
                                    "amount": amount
                                })

# Save to CSV
with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["year", "quarter", "category", "count", "amount"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data_list)

print(f"✅ Saved {len(data_list)} category-level records to {output_file}")
