import os
import json
import pandas as pd

# Base directory where JSON files are stored
base_dir = 'pulse/data/aggregated/transaction/country/india'

# List to collect all records
all_data = []

# Loop through each year folder
for year in os.listdir(base_dir):
    year_path = os.path.join(base_dir, year)
    if os.path.isdir(year_path):
        # Loop through each quarter file
        for file in os.listdir(year_path):
            if file.endswith('.json'):
                file_path = os.path.join(year_path, file)
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    transactions = data['data']['transactionData']
                    for txn in transactions:
                        name = txn['name']
                        for instrument in txn['paymentInstruments']:
                            all_data.append({
                                'year': year,
                                'quarter': file.replace('.json', ''),
                                'category': name,
                                'type': instrument['type'],
                                'count': instrument['count'],
                                'amount': instrument['amount']
                            })

# Convert to DataFrame
df = pd.DataFrame(all_data)

# Save to CSV
df.to_csv('phonepe_transactions.csv', index=False)
print("✅ Data saved to phonepe_transactions.csv")
