import pandas as pd
import mysql.connector

# Load the CSV file
df = pd.read_csv('phonepe_transactions.csv')

# Connect to MySQL
conn = mysql.connector.connect(
    host='localhost',
    user='root',      # Replace with your MySQL username
    password='12345',  # Replace with your MySQL password
    database='phonepe'               # Make sure this database exists
)

cursor = conn.cursor()

# Insert data row by row
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO transactions (year, quarter, category, type, count, amount)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, tuple(row))

conn.commit()
cursor.close()
conn.close()

print("✅ Data loaded into MySQL database")
