# app.py
import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px

# ---------------------- Page setup ----------------------
st.set_page_config(page_title="PhonePe Pulse Dashboard", layout="wide")

# ---------------------- MySQL Connection ----------------------
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345",
        database="phonepe_dashboard"
    )

# ---------------------- Load Data ----------------------
@st.cache_data(show_spinner=False)
def load_data():
    conn = get_connection()
    insurance_df = pd.read_sql("SELECT * FROM insurance_data", conn)
    hover_df     = pd.read_sql("SELECT * FROM map_hover_transactions", conn)
    category_df  = pd.read_sql("SELECT * FROM transaction_categories", conn)
    device_df    = pd.read_sql("SELECT * FROM user_device_data", conn)
    conn.close()
    return insurance_df, hover_df, category_df, device_df

insurance_df, hover_df, category_df, device_df = load_data()

# ---------------------- Name helpers ----------------------
_STATE_FIX = {
    "andaman & nicobar islands": "Andaman and Nicobar Islands",
    "andaman and nicobar isl": "Andaman and Nicobar Islands",
    "delhi": "NCT of Delhi",
    "nct of delhi": "NCT of Delhi",
    "jammu & kashmir": "Jammu and Kashmir",
    "dadra & nagar haveli and daman & diu": "Dadra and Nagar Haveli and Daman and Diu",
    "dadra and nagar haveli": "Dadra and Nagar Haveli and Daman and Diu",
    "daman and diu": "Dadra and Nagar Haveli and Daman and Diu",
    "arunanchal pradesh": "Arunachal Pradesh",
    "telengana": "Telangana",
    "odisha": "Odisha",
}

def norm_state(s: str) -> str:
    if not isinstance(s, str):
        return ""
    key = s.strip().lower().replace("&", "and")
    key = " ".join(key.split())
    return _STATE_FIX.get(key, key.title())

# ---------------------- Filters helpers ----------------------
def normalize_years(df: pd.DataFrame) -> pd.Series:
    if "year" not in df.columns:
        return pd.Series([], dtype=int)
    return pd.to_numeric(df["year"], errors="coerce").dropna().astype(int)

def normalize_quarters(df: pd.DataFrame) -> pd.Series:
    if "quarter" not in df.columns:
        return pd.Series([], dtype=object)
    q = (df["quarter"].astype(str)
         .str.extract(r"(\d+)", expand=False)
         .astype(float).dropna().astype(int)
         .clip(1, 4)
         .apply(lambda x: f"Q{x}"))
    return q

def to_quarter_int(q_label: str):
    if q_label == "All":
        return None
    try:
        return int(str(q_label).replace("Q", "").strip())
    except Exception:
        return None

def apply_year_quarter_filters(df: pd.DataFrame, year_sel, q_sel):
    out = df.copy()
    if "year" in out.columns and year_sel != "All":
        out = out[pd.to_numeric(out["year"], errors="coerce") == int(year_sel)]
    if "quarter" in out.columns and q_sel != "All":
        q_num = to_quarter_int(q_sel)
        q_col_num = out["quarter"].astype(str).str.extract(r"(\d+)", expand=False).astype(float)
        out = out[q_col_num == float(q_num)]
    return out

# ---------------------- India state centroids ----------------------
STATE_CENTROIDS = {
    "Andhra Pradesh": (15.9129, 79.7400),
    "Arunachal Pradesh": (28.2180, 94.7278),
    "Assam": (26.2006, 92.9376),
    "Bihar": (25.0961, 85.3131),
    "Chhattisgarh": (21.2787, 81.8661),
    "Goa": (15.2993, 74.1240),
    "Gujarat": (22.2587, 71.1924),
    "Haryana": (29.0588, 76.0856),
    "Himachal Pradesh": (31.1048, 77.1734),
    "Jharkhand": (23.6102, 85.2799),
    "Karnataka": (15.3173, 75.7139),
    "Kerala": (10.8505, 76.2711),
    "Madhya Pradesh": (22.9734, 78.6569),
    "Maharashtra": (19.7515, 75.7139),
    "Manipur": (24.6637, 93.9063),
    "Meghalaya": (25.4670, 91.3662),
    "Mizoram": (23.1645, 92.9376),
    "Nagaland": (26.1584, 94.5624),
    "Odisha": (20.9517, 85.0985),
    "Punjab": (31.1471, 75.3412),
    "Rajasthan": (27.0238, 74.2179),
    "Sikkim": (27.5330, 88.5122),
    "Tamil Nadu": (11.1271, 78.6569),
    "Telangana": (18.1124, 79.0193),
    "Tripura": (23.9408, 91.9882),
    "Uttar Pradesh": (27.5706, 80.0982),
    "Uttarakhand": (30.0668, 79.0193),
    "West Bengal": (22.9868, 87.8550),
    "Andaman and Nicobar Islands": (11.7401, 92.6586),
    "Chandigarh": (30.7333, 76.7794),
    "Dadra and Nagar Haveli and Daman and Diu": (20.3000, 73.0000),
    "NCT of Delhi": (28.7041, 77.1025),
    "Jammu and Kashmir": (33.7782, 76.5762),
    "Ladakh": (34.1526, 77.5770),
    "Lakshadweep": (10.5667, 72.6417),
    "Puducherry": (11.9416, 79.8083),
}

# ---------------------- Build filter options ----------------------
all_years = sorted(
    set(normalize_years(insurance_df)) |
    set(normalize_years(hover_df)) |
    set(normalize_years(category_df)) |
    set(normalize_years(device_df))
)
all_quarters = sorted(
    set(normalize_quarters(insurance_df)) |
    set(normalize_quarters(hover_df)) |
    set(normalize_quarters(category_df)) |
    set(normalize_quarters(device_df)),
    key=lambda x: int(x.replace("Q", ""))
)

# ---------------------- Sidebar ----------------------
st.sidebar.header("📌 Filters")
year_options = ["All"] + all_years
quarter_options = ["All"] + all_quarters
selected_year = st.sidebar.selectbox("Select Year", year_options, index=0)
selected_quarter = st.sidebar.selectbox("Select Quarter", quarter_options, index=0)

# ---------------------- Tabs ----------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🛡️ Insurance Summary",
    "🗺️ State-Level Transaction Map",
    "📂 Transaction Categories",
    "📱 Device Usage",
    "📊 Summary Insights"
])

# ---------------------- 1) Insurance Summary ----------------------
with tab1:
    st.subheader("🛡️ Insurance Coverage Summary")

    df_ins_f = apply_year_quarter_filters(insurance_df, selected_year, selected_quarter)

    if df_ins_f.empty:
        st.warning("No insurance data available for the selected filters.")
    else:
        total_value = pd.to_numeric(df_ins_f.get("amount"), errors="coerce").fillna(0).sum()
        total_policies = pd.to_numeric(df_ins_f.get("count"), errors="coerce").fillna(0).sum()

        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Total Insurance Value", f"₹{total_value:,.2f}")
        c2.metric("🧾 Total Policies Issued", f"{int(total_policies):,}")
        c3.metric("📆 Filter", f"{selected_quarter}, {selected_year}" if selected_year!="All" or selected_quarter!="All" else "All Data")

        label_col = "state" if "state" in df_ins_f.columns else "district"
        df_ins_f["state_norm"] = df_ins_f[label_col].astype(str).apply(norm_state)

        state_summary = (
            df_ins_f.assign(amount=pd.to_numeric(df_ins_f.get("amount"), errors="coerce").fillna(0),
                            count=pd.to_numeric(df_ins_f.get("count"), errors="coerce").fillna(0))
                     .groupby("state_norm", as_index=False)
                     .agg(total_value=("amount", "sum"),
                          total_policies=("count", "sum"))
                     .sort_values("total_value", ascending=False)
        )

        st.subheader("🗺️ Top 20 States by Insurance Value")
        fig_state = px.bar(
            state_summary.head(20),
            x="state_norm", y="total_value",
            hover_data=["total_policies"],
            title="Top 20 States by Insurance Value",
            labels={"total_value": "Total Value", "state_norm": "State"},
            color="total_value",
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig_state, use_container_width=True)

# ---------------------- 2) State-Level Transaction Map ----------------------
with tab2:
    st.subheader("🗺️ State-Level Transaction Map")

    df_map_f = apply_year_quarter_filters(hover_df, selected_year, selected_quarter)

    if df_map_f.empty:
        st.warning("No transaction data available for the selected filters.")
    else:
        label_col = "state" if "state" in df_map_f.columns else "district"
        df_map_f["state_norm"] = df_map_f[label_col].astype(str).apply(norm_state)
        df_map_f["amount"] = pd.to_numeric(df_map_f.get("amount"), errors="coerce").fillna(0)
        df_map_f["count"]  = pd.to_numeric(df_map_f.get("count"), errors="coerce").fillna(0)

        state_agg = (
            df_map_f.groupby("state_norm", as_index=False)
                    .agg(total_amount=("amount", "sum"),
                         total_count=("count", "sum"))
        )
        state_agg["lat"] = state_agg["state_norm"].map(lambda s: STATE_CENTROIDS.get(s, (None, None))[0])
        state_agg["lon"] = state_agg["state_norm"].map(lambda s: STATE_CENTROIDS.get(s, (None, None))[1])
        state_agg = state_agg.dropna(subset=["lat", "lon"])

        if state_agg.empty:
            st.warning("Could not place states on the map (name mismatch).")
        else:
            fig_map = px.scatter_mapbox(
                state_agg,
                lat="lat", lon="lon",
                size="total_amount",
                color="total_amount",
                hover_name="state_norm",
                hover_data={"total_amount": ":,", "total_count": ":,d", "lat": False, "lon": False},
                size_max=40,
                zoom=3.9,
                center={"lat": 22.9734, "lon": 78.6569},
                mapbox_style="open-street-map",
                title=("Transactions by State – "
                       f"{selected_quarter}, {selected_year}" if selected_year!="All" or selected_quarter!="All"
                       else "Transactions by State – All Data"),
                color_continuous_scale="Viridis"
            )
            fig_map.update_layout(margin=dict(l=0, r=0, t=60, b=0))
            st.plotly_chart(fig_map, use_container_width=True)

            # -------- New Breakdown Section --------
            st.markdown("### 📊 State Transaction Breakdown")
            chart_type = st.radio("Select view:", ["Bar Chart", "Pie Chart", "Table"], horizontal=True)

            if chart_type == "Bar Chart":
                fig_bar = px.bar(
                    state_agg.sort_values("total_amount", ascending=False),
                    x="state_norm", y="total_amount",
                    hover_data=["total_count"],
                    color="total_amount", color_continuous_scale="Blues",
                    title="Transaction Amount by State"
                )
                st.plotly_chart(fig_bar, use_container_width=True)

            elif chart_type == "Pie Chart":
                fig_pie = px.pie(
                    state_agg, names="state_norm", values="total_amount",
                    title="Transaction Share by State"
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            else:
                st.dataframe(state_agg.sort_values("total_amount", ascending=False), use_container_width=True)

# ---------------------- 3) Transaction Categories ----------------------
with tab3:
    st.subheader("📂 Transaction Categories")

    df_cat_f = apply_year_quarter_filters(category_df, selected_year, selected_quarter)

    if df_cat_f.empty:
        st.warning("No category data available for the selected filters.")
    else:
        df_cat_f["amount"] = pd.to_numeric(df_cat_f.get("amount"), errors="coerce").fillna(0)
        cat_summary = (
            df_cat_f.groupby("category", dropna=False, as_index=False)
                    .agg(total_amount=("amount", "sum"))
                    .sort_values("total_amount", ascending=False)
        )
        st.dataframe(cat_summary, use_container_width=True)

        fig3 = px.bar(
            cat_summary,
            x="category", y="total_amount",
            color="category",
            title=("Amount by Category – "
                   f"{selected_quarter}, {selected_year}" if selected_year!="All" or selected_quarter!="All"
                   else "Amount by Category – All Data"),
            labels={"total_amount": "Amount"}
        )
        st.plotly_chart(fig3, use_container_width=True)

# ---------------------- 4) Device Usage ----------------------
with tab4:
    st.subheader("📱 Device Usage")

    df_dev_f = apply_year_quarter_filters(device_df, selected_year, selected_quarter)

    if df_dev_f.empty:
        st.warning("No device data.")
    else:
        df_dev_f["count"] = pd.to_numeric(df_dev_f.get("count"), errors="coerce").fillna(0)
        brand_summary = (
            df_dev_f.groupby("brand", dropna=False, as_index=False)
                    .agg(total_users=("count", "sum"))
                    .sort_values("total_users", ascending=False)
        )

        st.dataframe(brand_summary, use_container_width=True)

        fig4 = px.pie(
            brand_summary, names="brand", values="total_users",
            title=("Device Brand Distribution – "
                   f"{selected_quarter}, {selected_year}" if selected_year!="All" or selected_quarter!="All"
                   else "Device Brand Distribution – All Data"),
            hole=0.35
        )
        st.plotly_chart(fig4, use_container_width=True)

# ---------------------- 5) Summary Insights ----------------------
with tab5:
    st.subheader("📊 Summary Insights")

    ins_all_val = pd.to_numeric(insurance_df.get("amount"), errors="coerce").fillna(0).sum() if not insurance_df.empty else 0
    ins_all_cnt = pd.to_numeric(insurance_df.get("count"), errors="coerce").fillna(0).sum() if not insurance_df.empty else 0
    hov_all_amt = pd.to_numeric(hover_df.get("amount"), errors="coerce").fillna(0).sum() if not hover_df.empty else 0
    hov_all_cnt = pd.to_numeric(hover_df.get("count"), errors="coerce").fillna(0).sum() if not hover_df.empty else 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("💳 Total Transaction Amount", f"₹{hov_all_amt:,.0f}")
    k2.metric("🧮 Total Transactions", f"{int(hov_all_cnt):,}")
    k3.metric("🛡️ Total Insurance Value", f"₹{ins_all_val:,.0f}")
    k4.metric("📑 Total Policies", f"{int(ins_all_cnt):,}")

    st.markdown("---")

    ins = insurance_df.copy()
    if not ins.empty:
        ins["year"] = pd.to_numeric(ins.get("year"), errors="coerce")
        ins["quarter"] = ins.get("quarter").astype(str).str.extract(r"(\d+)", expand=False).astype(float)
        ins = ins.dropna(subset=["year", "quarter"])
        ins["year"] = ins["year"].astype(int)
        ins["quarter"] = ins["quarter"].astype(int)

        ins_summary = (
            ins.groupby(["year", "quarter"], as_index=False)
               .agg(total_insured=("count","sum"), total_value=("amount","sum"))
               .sort_values(["year","quarter"])
        )
        c1, c2 = st.columns(2)
        with c1:
            fig5 = px.line(
                ins_summary, x="year", y="total_insured",
                color=ins_summary["quarter"].astype(str),
                title="Total Policies Over Time", markers=True, labels={"color":"Quarter"}
            )
            st.plotly_chart(fig5, use_container_width=True)
        with c2:
            fig5b = px.line(
                ins_summary, x="year", y="total_value",
                color=ins_summary["quarter"].astype(str),
                title="Total Insurance Value Over Time", markers=True, labels={"color":"Quarter"}
            )
            st.plotly_chart(fig5b, use_container_width=True)

    hov = hover_df.copy()
    if not hov.empty:
        hov["year"] = pd.to_numeric(hov.get("year"), errors="coerce")
        hov["quarter"] = hov.get("quarter").astype(str).str.extract(r"(\d+)", expand=False).astype(float)
        hov = hov.dropna(subset=["year", "quarter"])
        hov["year"] = hov["year"].astype(int)
        hov["quarter"] = hov["quarter"].astype(int)

        hov_summary = (
            hov.groupby(["year", "quarter"], as_index=False)
               .agg(total_txn=("count","sum"), total_amount=("amount","sum"))
               .sort_values(["year","quarter"])
        )
        c3, c4 = st.columns(2)
        with c3:
            fig6 = px.line(
                hov_summary, x="year", y="total_txn",
                color=hov_summary["quarter"].astype(str),
                title="Total Transactions Over Time", markers=True, labels={"color":"Quarter"}
            )
            st.plotly_chart(fig6, use_container_width=True)
        with c4:
            fig6b = px.line(
                hov_summary, x="year", y="total_amount",
                color=hov_summary["quarter"].astype(str),
                title="Total Transaction Amount Over Time", markers=True, labels={"color":"Quarter"}
            )
            st.plotly_chart(fig6b, use_container_width=True)

# ---------------------- Footer ----------------------
st.markdown("---")
st.markdown("📌 Built by Gokul | Powered by Streamlit & MySQL")

