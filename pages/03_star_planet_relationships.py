import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import load_data

PAGE_TITLE = "Star-Planet Relationships"

# Configure page
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon="✨",
    layout="wide"
)

# Load the data
data = load_data()

# Page header
st.title(f"⭐ {PAGE_TITLE}")
st.markdown("""
    This page explores the fascinating relationships between exoplanets and their host stars.
    Discover how star properties influence planetary characteristics and explore how planets
    are distributed across our galaxy.
""")

# Create layout with two columns for the first row
col1, col2 = st.columns([1, 1])

# 1. Star Properties Map (Scatter Plot)
with col1:
    st.header("Star Properties Map")
    st.markdown("Explore how star temperature, radius, mass, and age relate to each other.")
    
    # Add search functionality for star types or hostnames
    search_text = st.text_input("Search for specific star types or host stars", "")
    
    # Filter data based on search
    filtered_data = data
    if search_text:
        filtered_data = data[
            data['st_spectype'].str.contains(search_text, case=False) |
            data['hostname'].str.contains(search_text, case=False)
        ]
    
    # Create scatter plot
    fig_star_props = px.scatter(
        filtered_data,
        x='st_teff',
        y='st_rad',
        color='st_mass',
        size='st_age',
        hover_name='hostname',
        labels={
            'st_teff': 'Star Temperature (K)',
            'st_rad': 'Star Radius (Solar Radii)',
            'st_mass': 'Star Mass (Solar Masses)',
            'st_age': 'Star Age (Gyr)'
        },
        title='Star Properties Visualization',
        color_continuous_scale=px.colors.sequential.Viridis,
        size_max=20,
        log_y=True,
    )
    
    # Add labels for notable stars (top 5 by mass)
    notable_stars = filtered_data.sort_values('st_mass', ascending=False).head(5)
    fig_star_props.add_trace(
        go.Scatter(
            x=notable_stars['st_teff'],
            y=notable_stars['st_rad'],
            text=notable_stars['hostname'],
            mode='text',
            showlegend=False,
            textposition='top center'
        )
    )
    
    # Display the plot
    st.plotly_chart(fig_star_props, use_container_width=True)

# 2. Planet Mass vs. Star Mass (Log-scale Scatter Plot)
with col2:
    st.header("Planet Mass vs. Star Mass")
    st.markdown("Examine the relationship between planet mass and host star mass.")
    
    # Star age slider for filtering
    min_age = float(data['st_age'].min())
    max_age = float(data['st_age'].max())
    selected_age_range = st.slider(
        "Filter by star age (Gyr)",
        min_value=min_age,
        max_value=max_age,
        value=(min_age, max_age)
    )
    
    # Filter data based on selected age range
    filtered_by_age = data[
        (data['st_age'] >= selected_age_range[0]) &
        (data['st_age'] <= selected_age_range[1])
    ]
    
    # Create log-scale scatter plot
    fig_mass_relation = px.scatter(
        filtered_by_age,
        x='st_mass',
        y='pl_bmasse',
        color='discoverymethod',
        hover_name='pl_name',
        hover_data=['hostname', 'st_age', 'pl_bmasse', 'st_mass'],
        labels={
            'st_mass': 'Star Mass (Solar Masses)',
            'pl_bmasse': 'Planet Mass (Earth Masses)',
            'discoverymethod': 'Discovery Method'
        },
        title='Planet Mass vs. Star Mass Relationship',
        log_x=True,
        log_y=True,
    )
    
    # Add reference lines for different mass ratios
    x_range = np.logspace(np.log10(filtered_by_age['st_mass'].min()), 
                         np.log10(filtered_by_age['st_mass'].max()), 100)
    
    # Jupiter mass line (317.8 Earth masses)
    jupiter_y = x_range * 317.8 / 1047.57  # Jupiter/Sun mass ratio
    fig_mass_relation.add_trace(
        go.Scatter(x=x_range, y=jupiter_y, mode='lines', name='Jupiter/Sun ratio',
                 line=dict(color='orange', width=1, dash='dash'))
    )
    
    # Earth mass line
    earth_y = x_range * 1.0 / 333000  # Earth/Sun mass ratio
    fig_mass_relation.add_trace(
        go.Scatter(x=x_range, y=earth_y, mode='lines', name='Earth/Sun ratio',
                 line=dict(color='blue', width=1, dash='dash'))
    )
    
    # Display the plot
    st.plotly_chart(fig_mass_relation, use_container_width=True)

# Create layout with two columns for the second row
col3, col4 = st.columns([1, 1])

# 3. Celestial Map
with col3:
    st.header("Celestial Map")
    st.markdown("Explore the distribution of exoplanets across the celestial sphere.")
    
    # Add spectral type filter
    spectral_types = ['All'] + sorted(data['st_spectype'].unique().tolist())
    selected_spectral_type = st.selectbox("Filter by star spectral type", spectral_types)
    
    # Filter data based on selected spectral type
    filtered_by_type = data
    if selected_spectral_type != 'All':
        filtered_by_type = data[data['st_spectype'] == selected_spectral_type]
    
    # Create celestial map
    fig_celestial = px.scatter_geo(
        filtered_by_type,
        lon='ra',
        lat='dec',
        color='disc_year',
        size='pl_rade',
        hover_name='pl_name',
        hover_data=['hostname', 'st_spectype', 'sy_dist'],
        labels={
            'ra': 'Right Ascension',
            'dec': 'Declination',
            'disc_year': 'Discovery Year',
            'pl_rade': 'Planet Radius (Earth Radii)'
        },
        title='Celestial Distribution of Exoplanets',
        color_continuous_scale=px.colors.sequential.Plasma,
        projection='natural earth',
        size_max=15,
    )
    
    # Adjust layout for celestial map
    fig_celestial.update_geos(
        showcoastlines=False,
        showland=False,
        showcountries=False,
        showocean=True,
        oceancolor='rgb(5, 5, 20)',
        bgcolor='rgba(0,0,0,0)',
    )
    
    # Display the plot
    st.plotly_chart(fig_celestial, use_container_width=True)

# 4. Multi-planet System Composition (Box Plot)
with col4:
    st.header("Multi-planet System Composition")
    st.markdown("Explore how orbital parameters vary in systems with different numbers of planets.")
    
    # Add metric selection for y-axis
    metrics = {
        'pl_orbper': 'Orbital Period (days)',
        'pl_orbsmax': 'Semi-major Axis (AU)',
        'pl_orbeccen': 'Orbital Eccentricity',
        'pl_rade': 'Planet Radius (Earth Radii)',
        'pl_masse': 'Planet Mass (Earth Masses)',
        'pl_eqt': 'Equilibrium Temperature (K)'
    }
    selected_metric = st.radio("Select metric to visualize", list(metrics.keys()), 
                             format_func=lambda x: metrics[x])
    
    # Group data by number of planets in system
    # Only consider systems with 1-8 planets for clarity
    system_sizes = sorted(data['sy_pnum'].unique())
    system_sizes = [size for size in system_sizes if 1 <= size <= 8]
    
    # Prepare data for box plot
    box_data = []
    for size in system_sizes:
        system_data = data[data['sy_pnum'] == size]
        if not system_data.empty:
            for _, row in system_data.iterrows():
                box_data.append({
                    'Number of Planets': f"{size}",
                    'Value': row[selected_metric],
                    'hostname': row['hostname'],
                    'pl_name': row['pl_name']
                })
    
    box_df = pd.DataFrame(box_data)
    
    # Create box plot
    if not box_df.empty:
        fig_box = px.box(
            box_df,
            x='Number of Planets',
            y='Value',
            hover_data=['hostname', 'pl_name'],
            labels={
                'Value': metrics[selected_metric],
                'Number of Planets': 'Number of Planets in System'
            },
            title=f'{metrics[selected_metric]} vs. Number of Planets in System',
            color='Number of Planets',
            color_discrete_sequence=px.colors.qualitative.Safe,
        )
        
        # Add individual points for better visualization
        fig_box.update_traces(boxpoints='all', jitter=0.3, pointpos=-1.8)
        
        # Adjust y-axis scale if needed
        if selected_metric in ['pl_orbper', 'pl_orbsmax', 'pl_masse', 'pl_rade']:
            fig_box.update_layout(yaxis_type='log')
        
        # Display the plot
        st.plotly_chart(fig_box, use_container_width=True)
    else:
        st.error("Not enough data to create box plot for the selected parameters.")

# Add a conclusion section
st.markdown("""
## Key Insights

- **Star-Planet Mass Relationship**: There appears to be a correlation between star mass and the mass of their planets, 
  following certain proportionality ratios like the Jupiter-Sun and Earth-Sun mass ratios.
  
- **Celestial Distribution**: Exoplanets have been discovered across the celestial sphere, with some regions showing 
  higher concentrations due to observational biases in our detection methods.
  
- **Multi-planet Systems**: Systems with more planets tend to show different distributions of orbital parameters 
  compared to systems with fewer planets, suggesting different formation mechanisms or evolutionary paths.
  
- **Star Properties**: The properties of host stars (temperature, radius, mass, and age) are interconnected and 
  influence the types of planets that form around them.

Explore these relationships further by using the interactive filters and visualizations above!
""")

# Add information about the data source
st.sidebar.header("About the Data")
st.sidebar.markdown("""
This dashboard uses exoplanet data containing information about:

- Planet properties (mass, radius, temperature, etc.)
- Host star characteristics (spectral type, temperature, mass, etc.)
- Orbital parameters
- Discovery information

The visualizations help explore relationships between star properties and their planets.
""")

# Add a note about interactivity
st.sidebar.header("Interactivity Tips")
st.sidebar.markdown("""
- Use the search box to find specific stars or star types
- Filter by star age using the slider
- Select different spectral types to filter the celestial map
- Choose different metrics to explore in the multi-planet system box plot
- Hover over data points for detailed information
""")