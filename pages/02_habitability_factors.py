import streamlit as st
import pandas as pd
import plotly.express as px
import os, sys

# Add utility path and import dataset loader
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import load_data

# Set page configuration
ICON = "🌍"
PAGE_TITLE = "Habitability Factors"

# --- Page Configuration ---
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=ICON,
    layout="wide"
)

# Load dataset
df = load_data()

st.title(f"{ICON} {PAGE_TITLE}")
st.markdown("""
Explore potential habitability of exoplanets using key metrics:
- **Mass vs. Radius** for Earth-likeness
- **Orbital Properties** for stable climate conditions
- **Density distribution** to detect rocky vs. gas planets
- **Distance vs. Temperature** heatmap for finding planets in the habitable zone
""")

# Remove rows with missing critical values for visuals
clean_df = df[df[["pl_masse", "pl_rade", "pl_eqt", "pl_insol"]].notnull().all(axis=1)]

# === ROW 1 ===
col1, col2 = st.columns(2)

# --- Plot 1: Mass vs Radius ---
with col1:
    st.subheader("🌍 Mass vs. Radius Scatter Plot")
    st.markdown("Analyze the relation between planet mass and radius. Color and size reveal climate potential.")
    temp_range = st.slider("Filter by Equilibrium Temperature (K)", int(clean_df["pl_eqt"].min()), int(clean_df["pl_eqt"].max()), (200, 911))
    temp_filtered = clean_df[(clean_df["pl_eqt"] >= temp_range[0]) & (clean_df["pl_eqt"] <= temp_range[1])]

    fig1 = px.scatter(
        temp_filtered, x="pl_masse", y="pl_rade",
        color="pl_eqt", size="pl_insol", hover_name="pl_name",
        hover_data=["hostname", "pl_masse", "pl_rade", "pl_eqt", "pl_insol"],
        labels={"pl_masse": "Planet Mass (Earth Masses)", "pl_rade": "Planet Radius (Earth Radii)", "pl_eqt": "Equilibrium Temperature (K)", "pl_insol": "Insolation (Earth Flux)"},
        color_continuous_scale="Turbo"
    )
    fig1.add_shape(type="line", x0=1, x1=1, y0=0, y1=temp_filtered["pl_rade"].max(), line=dict(color="black", dash="dash"))
    fig1.add_shape(type="line", x0=0, x1=temp_filtered["pl_masse"].max(), y0=1, y1=1, line=dict(color="black", dash="dash"))
    fig1.add_annotation(x=1, y=1, text="Earth", showarrow=True)
    st.plotly_chart(fig1, use_container_width=True)

# --- Plot 2: Orbital Properties ---
with col2:
    st.subheader("🌀 Orbital Properties Visualization")
    st.markdown("Inspect how orbital characteristics affect planetary stability and seasonal variation.")
    method_options = df["discoverymethod"].dropna().unique().tolist()
    selected_methods = st.multiselect("Filter by Discovery Methods:", method_options, default=[method_options[0]])
    search_text = st.text_input("Search by Planet or Host Name")

    filtered_orb = df[df[["pl_orbper", "pl_orbsmax", "pl_orbeccen"]].notnull().all(axis=1)]
    if selected_methods:
        filtered_orb = filtered_orb[filtered_orb["discoverymethod"].isin(selected_methods)]
    if search_text:
        filtered_orb = filtered_orb[filtered_orb["pl_name"].str.contains(search_text, na=False, case=False) |
                                   filtered_orb["hostname"].str.contains(search_text, na=False, case=False)]

    fig2 = px.scatter(
        filtered_orb, x="pl_orbper", y="pl_orbsmax", color="pl_orbeccen",
        hover_data=["pl_name", "hostname", "disc_year"],
        labels={"pl_orbper": "Orbital Period (Days)", "pl_orbsmax": "Orbit Semi-Major Axis (AU)", "pl_orbeccen": "Orbital Eccentricity"},
        color_continuous_scale="Viridis"
    )
    st.plotly_chart(fig2, use_container_width=True)

# === ROW 2 ===
col3, col4 = st.columns(2)

# --- Plot 3: Planetary Density Histogram ---
with col3:
    st.subheader("🧱 Planetary Density Distribution")
    st.markdown("Identify rocky planets by comparing their densities to Earth's (~5.51 g/cm³).")
    mass_range = st.slider("Planet Mass Range (Earth Masses)", float(df["pl_masse"].min()), float(df["pl_masse"].max()), (0.5, 10.0))
    density_df = df[(df["pl_dens"].notnull()) & (df["pl_masse"] >= mass_range[0]) & (df["pl_masse"] <= mass_range[1])]
    fig3 = px.histogram(
        density_df, x="pl_dens", nbins=30,
        labels={"pl_dens": "Planet Density (g/cm³)"},
        color_discrete_sequence=["#636EFA"]
    )
    fig3.update_layout(yaxis_title="# of Planets")
    fig3.update_traces(hovertemplate='Planet Density (g/cm³): %{x}<br># of Planets: %{y}<extra></extra>')
    fig3.add_vline(x=5.51, line_dash="dash", line_color="green", annotation_text="Earth", annotation_position="top")
    st.plotly_chart(fig3, use_container_width=True)

# --- Plot 4: Distance vs. Habitability Heat Map ---
with col4:
    st.subheader("🔥 Distance vs. Habitability Heat Map")
    st.markdown("Shows how far planets are from Earth and how many fall into potentially habitable temperature ranges.")
    heat_df = df[df[["sy_dist", "pl_eqt"]].notnull()]
    heat_df["temp_bin"] = pd.cut(heat_df["pl_eqt"], bins=[0,100,200,300,400,500,1000], labels=["0–100","100–200","200–300","300–400","400–500","500+"])
    heat_df["dist_bin"] = pd.cut(heat_df["sy_dist"], bins=[0,25,50,75,100,1000], labels=["0–25","25–50","50–75","75–100","100+"])
    grouped = heat_df.groupby(["temp_bin", "dist_bin"], observed=False).size().reset_index(name="count")

    fig4 = px.density_heatmap(
        grouped, x="dist_bin", y="temp_bin", z="count",
        color_continuous_scale="Magma",
        labels={"dist_bin": "Distance from Earth (parsecs)", "temp_bin": "Temperature Range (K)", "count": "# of Planets"}
    )
    fig4.add_shape(type="rect", x0=1, x1=2, y0=2, y1=3, xref='x', yref='y', line=dict(color="green", width=2, dash="dot"))
    fig4.add_annotation(x=1.5, y=2.5, text="Habitable Zone", showarrow=False, font=dict(color="lime"))
    st.plotly_chart(fig4, use_container_width=True)

# Footer Note
st.markdown("---")
st.caption("Visualizations generated using NASA Exoplanet Archive data. Interactive dashboard built with Streamlit and Plotly.")