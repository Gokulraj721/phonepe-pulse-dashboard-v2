import os
import json
import pandas as pd

# 📁 Define base paths
country_path = r"C:\Gokul Important things\Phone pay project\pulse\data\aggregated\insurance\country\india"
state_path = os.path.join(country_path, "state")

insurance_records = []

# 🔁 Extract country-level insurance data
for year in os.listdir(country_path):
    year_folder = os.path.join(country_path, year)
    if not os.path.isdir(year_folder) or year == "state":
        continue

    for file in os.listdir(year_folder):
        if file.endswith(".json"):
            quarter = f"Q{file.split('.')[0]}"
            file_path = os.path.join(year_folder, file)

            with open(file_path, "r") as f:
                try:
                    data = json.load(f)
                    txn_data = data.get("data", {}).get("transactionData", [])
                    for txn in txn_data:
                        if txn.get("name") == "Insurance":
                            for instrument in txn.get("paymentInstruments", []):
                                insurance_records.append({
                                    "level": "Country",
                                    "state": "India",
                                    "year": int(year),
                                    "quarter": quarter,
                                    "type": instrument.get("type"),
                                    "count": instrument.get("count"),
                                    "amount": instrument.get("amount")
                                })
                except Exception as e:
                    print(f"❌ Error reading {file_path}: {e}")

# 🔁 Extract state-level insurance data
for state in os.listdir(state_path):
    state_folder = os.path.join(state_path, state)
    if not os.path.isdir(state_folder):
        continue

    for year in os.listdir(state_folder):
        year_folder = os.path.join(state_folder, year)
        if not os.path.isdir(year_folder):
            continue

        for file in os.listdir(year_folder):
            if file.endswith(".json"):
                quarter = f"Q{file.split('.')[0]}"
                file_path = os.path.join(year_folder, file)

                with open(file_path, "r") as f:
                    try:
                        data = json.load(f)
                        txn_data = data.get("data", {}).get("transactionData", [])
                        for txn in txn_data:
                            if txn.get("name") == "Insurance":
                                for instrument in txn.get("paymentInstruments", []):
                                    insurance_records.append({
                                        "level": "State",
                                        "state": state,
                                        "year": int(year),
                                        "quarter": quarter,
                                        "type": instrument.get("type"),
                                        "count": instrument.get("count"),
                                        "amount": instrument.get("amount")
                                    })
                    except Exception as e:
                        print(f"❌ Error reading {file_path}: {e}")


output_dir = r"C:\Gokul Important things\Phone pay project\output"
df_insurance = pd.DataFrame(insurance_records)
df_insurance.to_csv(os.path.join(output_dir, "insurance_data.csv"), index=False)

print("✅ insurance_data.csv created with country and state-level insights.")
