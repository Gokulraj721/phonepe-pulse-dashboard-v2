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

# ---------------------- Helpers: normalization & filters ----------------------
def normalize_years(df: pd.DataFrame) -> pd.Series:
    if "year" not in df.columns:
        return pd.Series([], dtype=int)
    return pd.to_numeric(df["year"], errors="coerce").dropna().astype(int)

def normalize_quarters(df: pd.DataFrame) -> pd.Series:
    if "quarter" not in df.columns:
        return pd.Series([], dtype=object)
    q = (
        df["quarter"]
        .astype(str)
        .str.extract(r"(\d+)", expand=False)  # get just the number part
        .astype(float)
        .dropna()
        .astype(int)
        .clip(lower=1, upper=4)              # keep Q1..Q4 only
        .apply(lambda x: f"Q{x}")
    )
    return q

def to_quarter_int(q_label: str) -> int | None:
    if q_label == "All":
        return None
    try:
        return int(str(q_label).replace("Q", "").strip())
    except Exception:
        return None

def apply_year_quarter_filters(df: pd.DataFrame, year_sel, q_sel):
    out = df.copy()
    # Year
    if "year" in out.columns and year_sel != "All":
        out = out[pd.to_numeric(out["year"], errors="coerce") == int(year_sel)]
    # Quarter
    if "quarter" in out.columns and q_sel != "All":
        q_num = to_quarter_int(q_sel)
        q_col_num = (
            out["quarter"]
            .astype(str)
            .str.extract(r"(\d+)", expand=False)
            .astype(float)
        )
        out = out[q_col_num == float(q_num)]
    return out

# ---------------------- Build filter options ----------------------
all_years = sorted(
    set(normalize_years(insurance_df)) |
    set(normalize_years(hover_df)) |
    set(normalize_years(category_df)) |
    set(normalize_years(device_df))
)

all_quarters_raw = list(
    set(normalize_quarters(insurance_df)) |
    set(normalize_quarters(hover_df)) |
    set(normalize_quarters(category_df)) |
    set(normalize_quarters(device_df))
)
# Sort quarters by numeric order Q1..Q4
all_quarters = [q for q in ["Q1", "Q2", "Q3", "Q4"] if q in set(all_quarters_raw)]

# ---------------------- Sidebar ----------------------
st.sidebar.header("📌 Filters")
year_options = ["All"] + all_years
quarter_options = ["All"] + all_quarters

selected_year = st.sidebar.selectbox("Select Year", year_options, index=0)
selected_quarter = st.sidebar.selectbox("Select Quarter", quarter_options, index=0)

# ---------------------- Tabs ----------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🛡️ Insurance Summary",
    "🗺️ Transaction Map",
    "📂 Transaction Categories",
    "📱 Device Usage",
    "📊 Summary Insights"
])

# ---------------------- 1. Insurance Summary ----------------------
with tab1:
    st.subheader("🛡️ Insurance Coverage Summary")

    df_ins_f = apply_year_quarter_filters(insurance_df, selected_year, selected_quarter)

    if df_ins_f.empty:
        st.warning("No insurance data available for the selected filters.")
    else:
        # Metrics
        total_value = pd.to_numeric(df_ins_f.get("amount"), errors="coerce").fillna(0).sum()
        total_policies = pd.to_numeric(df_ins_f.get("count"), errors="coerce").fillna(0).sum()

        c1, c2 = st.columns(2)
        c1.metric("💰 Total Insurance Value", f"₹{total_value:,.2f}")
        c2.metric("🧾 Total Policies Issued", f"{int(total_policies):,}")

        # Policies by type (if column exists)
        if "type" in df_ins_f.columns:
            policy_summary = (
                df_ins_f.groupby("type", dropna=False, as_index=False)
                        .agg(total_count=("count", "sum"))
                        .sort_values("total_count", ascending=False)
            )
            st.subheader("📊 Policies Issued by Type")
            st.dataframe(policy_summary, use_container_width=True)

            fig1 = px.pie(
                policy_summary,
                names="type",
                values="total_count",
                title=f"Policy Distribution – {selected_quarter}, {selected_year}" if selected_year != "All" or selected_quarter != "All" else "Policy Distribution – All Data",
                hole=0.35
            )
            st.plotly_chart(fig1, use_container_width=True)

        # State-wise view if present
        if "state" in df_ins_f.columns:
            state_summary = (
                df_ins_f.groupby("state", dropna=True, as_index=False)
                        .agg(total_value=("amount", "sum"),
                             total_policies=("count", "sum"))
                        .sort_values("total_value", ascending=False)
            )
            st.subheader("🗺️ State-wise Insurance Value")
            fig_state = px.bar(
                state_summary.head(20),
                x="state", y="total_value",
                hover_data=["total_policies"],
                title="Top 20 States by Insurance Value",
                labels={"total_value": "Total Value", "state": "State"},
                color="total_value",
                color_continuous_scale="Blues"
            )
            st.plotly_chart(fig_state, use_container_width=True)

# ---------------------- 2. Transaction Map ----------------------
with tab2:
    st.subheader("🗺️ District‑Level Transaction Map")

    df_map_f = apply_year_quarter_filters(hover_df, selected_year, selected_quarter)

    if df_map_f.empty:
        st.warning("No map hover data available for the selected filters.")
    else:
        df_map = df_map_f.copy()
        # Ensure numeric
        df_map["amount"] = pd.to_numeric(df_map.get("amount"), errors="coerce").fillna(0)
        df_map["count"]  = pd.to_numeric(df_map.get("count"), errors="coerce").fillna(0)

        # Fallback location text for scatter_geo
        if "district" in df_map.columns:
            df_map["location"] = df_map["district"].astype(str) + ", India"
        else:
            df_map["location"] = "India"

        fig_map = px.scatter_geo(
            df_map,
            locations="location",
            locationmode="country names",
            color="amount",
            size="amount",
            hover_name="district" if "district" in df_map.columns else None,
            hover_data={"count": True, "amount": ":,.0f", "location": False},
            title=(
                f"Transactions by District – {selected_quarter}, {selected_year}"
                if selected_year != "All" or selected_quarter != "All"
                else "Transactions by District – All Data"
            ),
            projection="natural earth",
            color_continuous_scale="Purples"
        )
        fig_map.update_layout(
            geo=dict(
                scope="asia",
                center={"lat": 22, "lon": 78},
                projection_scale=5,
                showland=True,
                landcolor="#EAEAEA"
            )
        )
        st.plotly_chart(fig_map, use_container_width=True)

# ---------------------- 3. Transaction Categories ----------------------
with tab3:
    st.subheader("📂 Transaction Categories")

    df_cat_f = apply_year_quarter_filters(category_df, selected_year, selected_quarter)

    if df_cat_f.empty:
        st.warning("No category data available for the selected filters.")
    else:
        st.dataframe(df_cat_f, use_container_width=True)

        # Summaries
        df_cat_f["amount"] = pd.to_numeric(df_cat_f.get("amount"), errors="coerce").fillna(0)
        cat_summary = (
            df_cat_f.groupby("category", dropna=False, as_index=False)
                    .agg(total_amount=("amount", "sum"))
                    .sort_values("total_amount", ascending=False)
        )

        fig3 = px.bar(
            cat_summary,
            x="category", y="total_amount",
            color="category",
            title=(
                f"Amount by Category – {selected_quarter}, {selected_year}"
                if selected_year != "All" or selected_quarter != "All"
                else "Amount by Category – All Data"
            ),
            labels={"total_amount": "Amount"}
        )
        st.plotly_chart(fig3, use_container_width=True)

# ---------------------- 4. Device Usage ----------------------
with tab4:
    st.subheader("📱 Device Usage")

    df_dev_f = apply_year_quarter_filters(device_df, selected_year, selected_quarter)

    if df_dev_f.empty:
        st.warning("No device data available for the selected filters.")
    else:
        st.dataframe(df_dev_f, use_container_width=True)

        df_dev_f["count"] = pd.to_numeric(df_dev_f.get("count"), errors="coerce").fillna(0)
        brand_summary = (
            df_dev_f.groupby("brand", dropna=False, as_index=False)
                    .agg(total_users=("count", "sum"))
                    .sort_values("total_users", ascending=False)
        )

        fig4 = px.pie(
            brand_summary, names="brand", values="total_users",
            title=(
                f"Device Brand Distribution – {selected_quarter}, {selected_year}"
                if selected_year != "All" or selected_quarter != "All"
                else "Device Brand Distribution – All Data"
            ),
            hole=0.35
        )
        st.plotly_chart(fig4, use_container_width=True)

# ---------------------- 5. Summary Insights ----------------------
with tab5:
    st.subheader("📊 Summary Insights")

    # Insurance over time (All data)
    ins = insurance_df.copy()
    if not ins.empty:
        ins["year"] = pd.to_numeric(ins.get("year"), errors="coerce")
        ins["quarter"] = (
            ins.get("quarter").astype(str).str.extract(r"(\d+)", expand=False).astype(float)
        )
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
                ins_summary, x="year", y="total_insured", color=ins_summary["quarter"].astype(str),
                title="Total Insured Over Time", markers=True, labels={"color":"Quarter"}
            )
            st.plotly_chart(fig5, use_container_width=True)
        with c2:
            fig5b = px.line(
                ins_summary, x="year", y="total_value", color=ins_summary["quarter"].astype(str),
                title="Total Insurance Value Over Time", markers=True, labels={"color":"Quarter"}
            )
            st.plotly_chart(fig5b, use_container_width=True)

    # Transaction amount over time (All data)
    hov = hover_df.copy()
    if not hov.empty:
        hov["year"] = pd.to_numeric(hov.get("year"), errors="coerce")
        hov["quarter"] = (
            hov.get("quarter").astype(str).str.extract(r"(\d+)", expand=False).astype(float)
        )
        hov["amount"] = pd.to_numeric(hov.get("amount"), errors="coerce").fillna(0)
        hov = hov.dropna(subset=["year", "quarter"])
        hov["year"] = hov["year"].astype(int)
        hov["quarter"] = hov["quarter"].astype(int)

        hov_summary = (
            hov.groupby(["year", "quarter"], as_index=False)
               .agg(total_txn_amount=("amount","sum"))
               .sort_values(["year","quarter"])
        )
        fig6 = px.line(
            hov_summary, x="year", y="total_txn_amount", color=hov_summary["quarter"].astype(str),
            title="Total Transaction Amount Over Time", markers=True, labels={"color":"Quarter"}
        )
        st.plotly_chart(fig6, use_container_width=True)

    # Category trends over time (All data)
    cat = category_df.copy()
    if not cat.empty:
        cat["year"] = pd.to_numeric(cat.get("year"), errors="coerce")
        cat["quarter"] = (
            cat.get("quarter").astype(str).str.extract(r"(\d+)", expand=False).astype(float)
        )
        cat["amount"] = pd.to_numeric(cat.get("amount"), errors="coerce").fillna(0)
        cat = cat.dropna(subset=["year", "quarter"])
        cat["year"] = cat["year"].astype(int)
        cat["quarter"] = cat["quarter"].astype(int)

        cat_summary = (
            cat.groupby(["year", "quarter"], as_index=False)
               .agg(total_amount=("amount","sum"))
               .sort_values(["year","quarter"])
        )
        fig7 = px.line(
            cat_summary, x="year", y="total_amount", color=cat_summary["quarter"].astype(str),
            title="Category Transaction Amount Over Time", markers=True, labels={"color":"Quarter"}
        )
        st.plotly_chart(fig7, use_container_width=True)

    # Top 10 Districts (All data)
    if "district" in hover_df.columns:
        top_dist = (
            hover_df.assign(amount=pd.to_numeric(hover_df.get("amount"), errors="coerce").fillna(0))
                    .groupby("district", as_index=False)
                    .agg(total_amount=("amount","sum"))
                    .sort_values("total_amount", ascending=False)
                    .head(10)
        )
        st.subheader("🏆 Top 10 Districts by Transaction Amount")
        st.dataframe(top_dist, use_container_width=True)

    # Top 10 Brands (All data)
    if "brand" in device_df.columns:
        top_brand = (
            device_df.assign(count=pd.to_numeric(device_df.get("count"), errors="coerce").fillna(0))
                     .groupby("brand", as_index=False)
                     .agg(total_users=("count","sum"))
                     .sort_values("total_users", ascending=False)
                     .head(10)
        )
        st.subheader("📱 Top 10 Device Brands by User Count")
        st.dataframe(top_brand, use_container_width=True)

# ---------------------- Footer ----------------------
st.markdown("---")
st.markdown("📌 Built by Gokul | Powered by Streamlit & MySQL")
