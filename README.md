# 📊 PhonePe Pulse Dashboard (Streamlit)

An interactive dashboard built with **Streamlit** to visualize and explore the [PhonePe Pulse](https://www.phonepe.com/pulse/) dataset.  
It lets you filter by year, quarter, and state to uncover insights into **Transactions**, **Users**, and **Insurance** across India.

---

## 🚀 Features

- **Multi‑Tab Navigation** → Separate views for Transactions, Users, and Insurance.
- **Dynamic Filters** → Year, Quarter, and State selectors for quick pivoting.
- **Interactive Maps** → State/District choropleth with hover metrics.
- **Top Rankings** → Top 10 States/Districts/Pincodes by transactions, users, or insurance.
- **Device Insights** → Registered users by brand with share %.
- **Quarter‑over‑Quarter Trends** → Growth indicators in Transactions and Insurance.

---

## 🗂 Folder Structure

. ├── app.py # Main Streamlit entry point ├── data_loader.py # Reads aggregated JSON & preps DataFrames ├── map_loader.py # GeoJSON & map‑specific transforms ├── user_loader.py # Registered users, app opens, devices ├── Insurance_data.py # Insurance tab processing ├── pulse/ # 📂 PhonePe Pulse JSON dataset ├── requirements.txt ├── .gitignore └── README.md

Code

---

## 📥 Installation & Setup

**1. Clone the repository**


git clone https://github.com/Gokulraj721/phonepe-pulse-dashboard-v2/edit/main/README.md

2. Create a virtual environment & activate

bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
3. Install dependencies

bash
pip install -r requirements.txt
▶️ Running the Dashboard
From the project root:

bash
streamlit run app.py
Then open the provided local URL in your browser. You’ll see:

Filters in the sidebar → select Year, Quarter, State

Tabs at the top → Transactions | Users | Insurance

Live charts and maps update instantly based on your filters
