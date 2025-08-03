import os
import pandas as pd
import streamlit as st
import plotly.express as px
import requests

st.set_page_config(page_title="📊 PhonePe Pulse Dashboard", layout="wide")

# 🚀 Fetch user metrics (optional, unused in this version)
@st.cache_data
def fetch_user_metrics():
    base_url = "https://data.phonepe.com/api/data/top/user/district"
    years = list(range(2018, 2024))
    quarters = [1, 2, 3, 4]
    states = [
        "andhra-pradesh", "karnataka", "tamil-nadu", "maharashtra", "delhi",
        "gujarat", "kerala", "west-bengal", "uttar-pradesh", "madhya-pradesh"
    ]
    user_rows = []
    for state in states:
        for year in years:
            for quarter in quarters:
                try:
                    url = f"{base_url}?state={state}&year={year}&quarter={quarter}"
                    r = requests.get(url)
                    if r.status_code == 200:
                        districts = r.json().get("data", {}).get("userDetails", {}).get("districts", [])
                        for d in districts:
                            user_rows.append({
                                "state": state,
                                "district": d.get("name"),
                                "year": year,
                                "quarter": quarter,
                                "registeredUsers": d.get("registeredUsers", 0),
                                "appOpens": d.get("appOpens", 0)
                            })
                except:
                    continue
    return pd.DataFrame(user_rows)

# 📂 Load local CSVs
output_dir = r"C:\Gokul Important things\Phone pay project\output"
transaction_df = pd.read_csv(os.path.join(output_dir, "transaction_categories.csv"))
map_df = pd.read_csv(os.path.join(output_dir, "map_hover_transactions.csv"))

# 🧼 Clean column names
transaction_df.columns = transaction_df.columns.str.strip().str.lower()
map_df.columns = map_df.columns.str.strip().str.lower()

# 🗺️ Rename for clarity
state_df = map_df.rename(columns={"district": "state"})

# 🧭 Tabbed dashboard
st.title("📱 PhonePe Pulse Insights Dashboard")
st.markdown("Explore user adoption, transaction behaviors, and regional activity across India.")
tab1, tab2, tab3 = st.tabs(["📊 Data Highlights", "💸 Transactions", "🏞️ State-Level Insights"])

# --- DATA HIGHLIGHTS TAB ---
with tab1:
    st.header("📊 Data Highlights & Summary")
    if transaction_df.empty:
        st.warning("⚠️ Transaction data not found.")
    else:
        total_txn = transaction_df['count'].sum()
        total_amt = transaction_df['amount'].sum()

        col1, col2 = st.columns(2)
        col1.metric("🧮 Total Transactions", f"{int(total_txn):,}")
        col2.metric("💰 Total Volume", f"₹{total_amt/1e9:.2f}B")

        # Top States
        if 'state' in transaction_df.columns:
            top_states = transaction_df.groupby('state')['count'].sum().sort_values(ascending=False).reset_index()
            st.subheader("🏆 Top Performing States")
            fig_state = px.bar(top_states.head(10), x='state', y='count', color='state',
                               title="Top 10 States by Transactions", text_auto=True)
            st.plotly_chart(fig_state, use_container_width=True)

        # Category Pie
        if 'category' in transaction_df.columns:
            category_summary = transaction_df.groupby('category')['amount'].sum().reset_index()
            st.subheader("🍕 Category Distribution")
            fig_pie = px.pie(category_summary, names='category', values='amount',
                            title="Transaction Volume by Category", hole=0.3)
            st.plotly_chart(fig_pie, use_container_width=True)

        # Yearly Trends
        if 'year' in transaction_df.columns:
            st.subheader("📈 Yearly Trends")
            year_summary = transaction_df.groupby('year')['amount'].sum().reset_index()
            fig_year = px.line(year_summary, x='year', y='amount', markers=True,
                               title="Year-wise Transaction Volume", labels={"amount": "₹ Volume"})
            st.plotly_chart(fig_year, use_container_width=True)

# --- TRANSACTIONS TAB ---
with tab2:
    st.header("💸 Transaction Insights")
    if transaction_df.empty:
        st.warning("⚠️ Transaction data not found.")
    else:
        years = sorted(transaction_df['year'].unique())
        categories = sorted(transaction_df['category'].unique())

        col1, col2 = st.columns(2)
        year_pick = col1.selectbox("📅 Select Year", years)
        category_pick = col2.selectbox("📦 Select Category", categories)

        selected_txns = transaction_df[
            (transaction_df['year'] == year_pick) & 
            (transaction_df['category'] == category_pick)
        ]

        if selected_txns.empty:
            st.warning("⚠️ No data found for this combination.")
        else:
            total_count = selected_txns['count'].sum()
            total_amount = selected_txns['amount'].sum()
            st.metric("🔢 Total Transactions", f"{int(total_count):,}")
            st.metric("💸 Total Volume", f"₹{total_amount/1e9:.2f}B")

            fig_txn = px.bar(
                selected_txns, x='quarter', y='amount', color='quarter',
                title=f"{year_pick} | {category_pick} Breakdown",
                labels={"amount": "₹ Volume"}, text_auto=True
            )
            st.plotly_chart(fig_txn, use_container_width=True)
            st.dataframe(selected_txns)

# --- STATE TRANSACTIONS TAB ---
with tab3:
    st.header("🏞️ State-Level Transaction Insights")
    if state_df.empty:
        st.warning("⚠️ State transaction data not found.")
    else:
        years = sorted(state_df['year'].unique())
        states = sorted(state_df['state'].unique())

        col1, col2 = st.columns(2)
        year_pick = col1.selectbox("📅 Select Year", years)
        state_pick = col2.selectbox("📍 Select State", states)

        filtered_df = state_df[
            (state_df['year'] == year_pick) & 
            (state_df['state'] == state_pick)
        ]

        if filtered_df.empty:
            st.warning("⚠️ No data found for this combination.")
        else:
            total_amount = filtered_df['amount'].sum()
            total_count = filtered_df['count'].sum()

            st.metric("🔢 Total Transactions", f"{int(total_count):,}")
            st.metric("💰 Total Volume", f"₹{total_amount/1e9:.2f}B")

            fig_amount = px.bar(
                filtered_df, x='quarter', y='amount', color='quarter',
                title=f"{state_pick} | ₹ Amount by Quarter ({year_pick})",
                labels={"amount": "₹ Volume"}, text_auto=True
            )

            fig_count = px.line(
                filtered_df, x='quarter', y='count', markers=True,
                title=f"{state_pick} | Transaction Count by Quarter ({year_pick})",
                labels={"count": "Transactions"}
            )

            st.plotly_chart(fig_amount, use_container_width=True)
            st.plotly_chart(fig_count, use_container_width=True)
            st.dataframe(filtered_df)
