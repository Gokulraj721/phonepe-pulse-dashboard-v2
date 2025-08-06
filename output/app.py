import os
import pandas as pd
import streamlit as st
import plotly.express as px
import requests

st.set_page_config(page_title="📊 PhonePe Pulse Dashboard", layout="wide")

# 📂 Load local CSVs
output_dir = r"C:\Gokul Important things\Phone pay project\output"
transaction_df = pd.read_csv(os.path.join(output_dir, "transaction_categories.csv"))
map_df = pd.read_csv(os.path.join(output_dir, "map_hover_transactions.csv"))

# 🧼 Clean column names
transaction_df.columns = transaction_df.columns.str.strip().str.lower()
map_df.columns = map_df.columns.str.strip().str.lower()
map_df.rename(columns={"district": "state"}, inplace=True)
state_df = map_df.copy()

# ✅ Full state name mapping for GeoJSON compatibility
state_name_map = {
    "andaman & nicobar islands": "Andaman & Nicobar Island",
    "andhra pradesh": "Andhra Pradesh",
    "arunachal pradesh": "Arunachal Pradesh",
    "assam": "Assam",
    "bihar": "Bihar",
    "chhattisgarh": "Chhattisgarh",
    "delhi": "Delhi",
    "goa": "Goa",
    "gujarat": "Gujarat",
    "haryana": "Haryana",
    "himachal pradesh": "Himachal Pradesh",
    "jammu & kashmir": "Jammu & Kashmir",
    "jharkhand": "Jharkhand",
    "karnataka": "Karnataka",
    "kerala": "Kerala",
    "ladakh": "Ladakh",
    "madhya pradesh": "Madhya Pradesh",
    "maharashtra": "Maharashtra",
    "manipur": "Manipur",
    "meghalaya": "Meghalaya",
    "mizoram": "Mizoram",
    "nagaland": "Nagaland",
    "odisha": "Odisha",
    "punjab": "Punjab",
    "rajasthan": "Rajasthan",
    "sikkim": "Sikkim",
    "tamil nadu": "Tamil Nadu",
    "telangana": "Telangana",
    "tripura": "Tripura",
    "uttar pradesh": "Uttar Pradesh",
    "uttarakhand": "Uttarakhand",
    "west bengal": "West Bengal",
    "lakshadweep": "Lakshadweep"
}

# 🔄 Shared filters
years = sorted(state_df['year'].unique())
states = sorted(state_df['state'].unique())
st.sidebar.header("🔄 Global Filters")
selected_year = st.sidebar.selectbox("📅 Select Year", years, key="global_year")
selected_state = st.sidebar.selectbox("📍 Select State", states, key="global_state")

# 🧭 Tabs
st.title("📱 PhonePe Pulse Insights Dashboard")
st.markdown("Explore user adoption, transaction behaviors, and regional activity across India.")
tab1, tab2, tab3 = st.tabs(["📊 Data Highlights", "💸 Transactions", "🏞️ State-Level Insights"])

# --- TAB 1 ---
with tab1:
    st.header("📊 Data Highlights & Summary")
    if transaction_df.empty:
        st.warning("⚠️ Transaction data not found.")
    else:
        total_txn = transaction_df['count'].sum()
        total_amt = transaction_df['amount'].sum()

        col1, col2 = st.columns(2)
        col1.metric("🧮 Total Transactions", f"{int(total_txn):,}")
        col2.metric("💰 Total Volume", f"₹{total_amt/1e12:.2f}T")

        category_summary = transaction_df.groupby('category')['amount'].sum().reset_index()
        st.subheader("🍕 Category Distribution")
        fig_pie = px.pie(category_summary, names='category', values='amount',
                         title="Transaction Volume by Category", hole=0.3)
        st.plotly_chart(fig_pie, use_container_width=True)

        year_summary = transaction_df.groupby('year')['amount'].sum().reset_index()
        st.subheader("📈 Yearly Trends")
        fig_year = px.line(year_summary, x='year', y='amount', markers=True,
                           title="Year-wise Transaction Volume", labels={"amount": "₹ Volume (T)"})
        st.plotly_chart(fig_year, use_container_width=True)

# --- TAB 2 ---
with tab2:
    st.header("💸 Transaction Insights")
    categories = sorted(transaction_df['category'].unique())
    category_pick = st.selectbox("📦 Select Category", categories, key="txn_category")

    selected_txns = transaction_df[
        (transaction_df['year'] == selected_year) & 
        (transaction_df['category'] == category_pick)
    ]

    if selected_txns.empty:
        st.warning("⚠️ No data found for this combination.")
    else:
        total_count = selected_txns['count'].sum()
        total_amount = selected_txns['amount'].sum()
        st.metric("🔢 Total Transactions", f"{int(total_count):,}")
        st.metric("💸 Total Volume", f"₹{total_amount/1e12:.2f}T")

        fig_txn = px.bar(
            selected_txns, x='quarter', y='amount', color='quarter',
            title=f"{selected_year} | {category_pick} Breakdown",
            labels={"amount": "₹ Volume (T)"}, text_auto=True
        )
        st.plotly_chart(fig_txn, use_container_width=True)
        st.dataframe(selected_txns)

# --- TAB 3 ---
with tab3:
    st.header("🏞️ State-Level Transaction Insights")
    filtered_df = state_df[
        (state_df['year'] == selected_year) & 
        (state_df['state'] == selected_state)
    ]

    if filtered_df.empty:
        st.warning("⚠️ No data found for this combination.")
    else:
        total_amount = filtered_df['amount'].sum()
        total_count = filtered_df['count'].sum()

        st.metric("🔢 Total Transactions", f"{int(total_count):,}")
        st.metric("💰 Total Volume", f"₹{total_amount/1e12:.2f}T")

        fig_amount = px.bar(
            filtered_df, x='quarter', y='amount', color='quarter',
            title=f"{selected_state} | ₹ Amount by Quarter ({selected_year})",
            labels={"amount": "₹ Volume (T)"}, text_auto=True
        )

        fig_count = px.line(
            filtered_df, x='quarter', y='count', markers=True,
            title=f"{selected_state} | Transaction Count by Quarter ({selected_year})",
            labels={"count": "Transactions"}
        )

        st.plotly_chart(fig_amount, use_container_width=True)
        st.plotly_chart(fig_count, use_container_width=True)
        st.dataframe(filtered_df)

        # 🌍 Choropleth Map of India with Highlight
        st.subheader("🗺️ India Map - Transaction Volume by State")
        map_data = state_df[state_df['year'] == selected_year].groupby('state')['amount'].sum().reset_index()

        # Normalize state names for GeoJSON compatibility
        map_data['state'] = map_data['state'].str.lower()
        map_data['geo_name'] = map_data['state'].map(state_name_map)

        # Add highlight flag
        selected_geo_name = state_name_map.get(selected_state.lower(), "")
        map_data['highlight'] = map_data['geo_name'].apply(lambda x: 1 if x == selected_geo_name else 0)

        geojson_url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
        geojson_data = requests.get(geojson_url).json()

        fig_map = px.choropleth(
            map_data,
            geojson=geojson_data,
            featureidkey="properties.ST_NM",
            locations="geo_name",
            color="amount",
            color_continuous_scale="YlOrBr",
            title=f"Total Transaction Volume by State ({selected_year})",
            labels={"amount": "₹ Volume (T)"},
            hover_name="geo_name"
        )

        fig_map.update_traces(
            marker_line_width=map_data["highlight"] * 5,
            marker_line_color="crimson"
        )

        fig_map.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig_map, use_container_width=True)
