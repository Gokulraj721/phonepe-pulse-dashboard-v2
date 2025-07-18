import streamlit as st
import pandas as pd
import mysql.connector

# Connect to MySQL
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='12345',
    database='phonepe'
)

# Load data
df = pd.read_sql("SELECT * FROM transactions", conn)

# Title
st.title("📊 PhonePe Pulse Dashboard")

# Filters
year = st.selectbox("Select Year", sorted(df['year'].unique()))
filtered_df = df[df['year'] == year]

# Chart
st.subheader(f"Transaction Amount by Category - {year}")
chart_data = filtered_df.groupby('category')['amount'].sum().sort_values(ascending=False)
st.bar_chart(chart_data)

conn.close()
