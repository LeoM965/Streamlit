import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

# ── Config & Styles ──────────────────────────────────────────────
st.set_page_config(page_title="Steam Analytics Pro", page_icon="🎮", layout="wide")

def apply_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@800&family=DM+Sans:wght@400;500;700&display=swap');
    :root { --accent: #00f0ff; --accent2: #7000ff; --bg: #0f0f0f; --surf: #1a1a1a; }
    html, body, [class*="css"] { background-color: var(--bg) !important; color: #e8e8e8 !important; font-family: 'DM Sans', sans-serif !important; }
    h1, h2 { font-family: 'Syne', sans-serif !important; font-weight: 800; }
    .stMetric { background: var(--surf); border: 1px solid #2e2e2e; padding: 15px; border-radius: 10px; }
    .main-title { font-size: 44px; background: linear-gradient(90deg, var(--accent), var(--accent2)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

apply_custom_css()
st.markdown('<h1 class="main-title">Steam Market Intelligence</h1>', unsafe_allow_html=True)

# ── Data Processing ──────────────────────────────────────────────
@st.cache_data
def load_and_clean(file_path_or_buffer):
    df = pd.read_csv(file_path_or_buffer)
    df['Release_Date'] = pd.to_datetime(df['Release_Date'])
    # Calculate Rating % and Total Reviews accurately
    df['Total_Reviews'] = df['Positive_Reviews'] + df['Negative_Reviews']
    df['Rating_%'] = (df['Positive_Reviews'] / df['Total_Reviews'] * 100).fillna(0).round(1)
    return df

import os
csv_path = "steam_games.csv"
remote_url = "https://raw.githubusercontent.com/LeoM965/Streamlit/main/steam_games.csv"

# Check for local file, then remote URL
if os.path.exists(csv_path):
    st.sidebar.success(f"✅ Loaded local: `{csv_path}`")
    data_source = csv_path
else:
    # Try to use remote URL as a static source
    data_source = remote_url
    st.sidebar.info("🌐 Using remote static data source")

df_raw = load_and_clean(data_source)

# ── Filtering ─────────────────────────────────────────────────────
st.sidebar.header("🎯 Filters")
raw_genres = df_raw["Genre"].dropna().unique()
all_genres = sorted(list(set([g.strip() for sublist in raw_genres for g in str(sublist).split(';')])))

selected_genres = st.sidebar.multiselect("Genres", all_genres, default=["Action", "Indie", "Adventure", "Strategy"])
price_limit = st.sidebar.slider("Max Price ($)", 0.0, float(df_raw['Price'].max()), 60.0)

mask = (
    df_raw['Genre'].apply(lambda x: any(g in str(x).split(';') for g in selected_genres)) & 
    (df_raw['Price'] <= price_limit)
)
df = df_raw[mask]

# ── KPIs ──────────────────────────────────────────────────────────
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Games Analysis", len(df))
kpi2.metric("Avg Rating", f"{df['Rating_%'].mean():.1f}%")
kpi3.metric("Avg Price", f"${df['Price'].mean():.2f}")
kpi4.metric("Top Publisher", df['Developer'].mode()[0] if not df.empty else "N/A")

# ── Visuals ───────────────────────────────────────────────────────
st.markdown("---")
c1, c2 = st.columns([3, 2])

with c1:
    st.subheader("🚀 Price vs. User Satisfaction")
    fig_scatter = px.scatter(
        df, x="Price", y="Rating_%", 
        size="Total_Reviews" if not df.empty else None, 
        color="Genre",
        hover_name="Name", hover_data=["Developer", "Total_Reviews"],
        size_max=35, template="plotly_dark", height=500,
        labels={"Rating_%": "Satisfaction (%)", "Price": "Price ($)"},
        title="Gaming Value: Price vs Rating"
    )
    fig_scatter.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_scatter, use_container_width=True)

with c2:
    st.subheader("📊 Popularity & Quality")
    tab1, tab2 = st.tabs(["Review Volume", "Satisfaction Dist."])
    
    with tab1:
        # Log-scaled Volume
        fig_vol, ax1 = plt.subplots(figsize=(8, 6))
        plt.style.use('dark_background')
        # Filter for reviews > 0 to avoid log issues
        vol_data = df[df['Total_Reviews'] > 0]['Total_Reviews']
        if not vol_data.empty:
            import numpy as np
            bins = np.logspace(np.log10(vol_data.min()), np.log10(vol_data.max()), 20)
            ax1.hist(vol_data, bins=bins, color="#00f0ff", edgecolor="white", alpha=0.7)
            ax1.set_xscale('log')
        ax1.set_xlabel("Review Count (Log Scale)")
        ax1.set_ylabel("Number of Games")
        fig_vol.patch.set_facecolor('#1a1a1a')
        ax1.set_facecolor('#1a1a1a')
        st.pyplot(fig_vol)
        
    with tab2:
        # Satisfaction Distribution
        fig_sat, ax2 = plt.subplots(figsize=(8, 6))
        ax2.hist(df['Rating_%'], bins=15, color="#7000ff", edgecolor="white", alpha=0.7)
        ax2.set_xlabel("Satisfaction Rate (%)")
        ax2.set_ylabel("Number of Games")
        fig_sat.patch.set_facecolor('#1a1a1a')
        ax2.set_facecolor('#1a1a1a')
        st.pyplot(fig_sat)

st.markdown("---")
st.subheader("📋 Top Filtered Games")
st.dataframe(df.sort_values("Positive_Reviews", ascending=False).head(20), use_container_width=True)

st.markdown("<br><p style='text-align:center;color:#444;'>No Redundancy • Professional Analytics • Seminar 3</p>", unsafe_allow_html=True)
