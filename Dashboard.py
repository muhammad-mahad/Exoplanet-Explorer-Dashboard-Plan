# import streamlit as st

# PAGE_TITLE = "Exoplanet Explorer"

# # Configure page
# st.set_page_config(
#     page_title=PAGE_TITLE,
#     page_icon="🔭",
#     layout="wide"
# )

import streamlit as st
import pandas as pd # Placeholder, in case you want to load a small summary data snippet later

# --- Page Configuration ---
# It's good practice to set page config as the first Streamlit command
# This can also be done in individual pages if you want different icons/titles per page,
# but a general one in Dashboard.py is good for the main landing page.
st.set_page_config(
    page_title="Exoplanet Explorer Dashboard",
    page_icon="🔭",  # A telescope or a general space icon
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Main Page Content ---
st.title("🔭 Welcome to the Exoplanet Explorer Dashboard!")
st.markdown("""
This interactive dashboard allows you to journey through the fascinating world of exoplanets. 
Discover distant worlds, analyze their characteristics, and explore the relationships they share with their host stars.

Navigate through the different sections using the sidebar on the left to begin your exploration.
""")

st.divider()

# --- Overview of Pages ---
st.header("What You Can Explore:")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🪐 Planetary Discovery")
    st.markdown("""
    Dive into the history of exoplanet discoveries. Visualize trends over time, 
    understand the methods used, and see the composition of known planetary systems.
    
    *Key Features:*
    - Interactive discovery timeline
    - Planetary system treemaps
    - Discovery method evolution
    """)
    if st.button("Go to Planetary Discovery", key="nav_discovery"):
        st.switch_page("pages/01_Planetary_Discovery.py")


with col2:
    st.subheader("🌍 Habitability Factors")
    st.markdown("""
    Investigate the factors that could make an exoplanet habitable. Analyze mass, radius, 
    orbital properties, and planetary density to identify potentially Earth-like worlds.
    
    *Key Features:*
    - Mass vs. Radius scatter plots
    - Orbital property visualizations
    - Planetary density distributions
    """)
    if st.button("Go to Habitability Factors", key="nav_habitability"):
        st.switch_page("pages/02_Habitability_Factors.py")

with col3:
    st.subheader("⭐ Star-Planet Relationships")
    st.markdown("""
    Explore the intricate connections between exoplanets and their host stars. 
    See how stellar properties like mass, temperature, and age influence the planets orbiting them.
    
    *Key Features:*
    - Stellar property influence on planets
    - Star type vs. system size distributions
    - Goldilocks zone analysis
    """)
    if st.button("Go to Star-Planet Relationships", key="nav_star_planet"):
        st.switch_page("pages/03_Star_Planet_Relationships.py")

st.divider()

st.markdown("""
### Get Started!
Use the navigation panel on the left to select a page and begin your cosmic journey. 
We hope you find this tool insightful and engaging!
""")

st.markdown("---")
st.caption("Visualizations generated using NASA Exoplanet Archive data. Interactive dashboard built with Streamlit and Plotly.")