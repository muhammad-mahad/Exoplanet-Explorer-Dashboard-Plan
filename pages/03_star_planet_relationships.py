import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os

PAGE_TITLE = "Star-Planet Relationships"
ICON = "⭐"

# --- Page Configuration ---
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=ICON,
    layout="wide"
)

# --- Load Data ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.data_loader import load_data

df = load_data()

# --- Page Header ---
st.title(f"{ICON} {PAGE_TITLE}")
st.markdown("""
    Explore the fascinating interplay between stars and their planets.  
    Dive into how stellar properties like mass, temperature, and age influence planetary size, orbit, and habitability.  
    """)

# --- Sidebar Filters ---
st.sidebar.header("🔎 Filter Data")

# Discovery Year
min_year, max_year = int(df.disc_year.min()), int(df.disc_year.max())
discovery_range = st.sidebar.slider(
    "Discovery Year", min_year, max_year, (max_year-20, max_year)
)

# Planets per System
min_sys, max_sys = int(df.sy_pnum.min()), int(df.sy_pnum.max())
system_range = st.sidebar.slider(
    "No of Systems", min_sys, max_sys, (1, max_sys)
)

# Star Class
types = sorted(df.star_type_classification.str[0].unique().tolist())
selected_types = st.sidebar.multiselect(
    "Star Spectral Class", types, default=['G','K','M']
)

# Discovery Method
top_methods = df.discoverymethod.value_counts().nlargest(4).index.tolist()
method_choice = st.sidebar.selectbox(
    "Discovery Method", ['All'] + top_methods
)

# Habitability Score
min_h, max_h = float(df.planet_habitability_score.min()), float(df.planet_habitability_score.max())
habit_range = st.sidebar.slider(
    "Habitability Score Range", min_h, max_h, (min_h, max_h)
)

# Apply Filters
mask = (
    df.disc_year.between(*discovery_range) &
    df.sy_pnum.between(*system_range) &
    df.planet_habitability_score.between(*habit_range) &
    df.star_type_classification.str[0].isin(selected_types)
)
if method_choice != 'All':
    mask &= df.discoverymethod == method_choice
filtered = df[mask]

# Display filter summary
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Showing {len(filtered)} planets**")
st.sidebar.markdown(f"**From {filtered['host_star_name'].nunique() if 'host_star_name' in filtered.columns else 'N/A'} unique star systems**")

# --- Section 1: How Stellar Properties Influence Planets ---
st.header("1️⃣ How Stellar Properties Influence Planets", divider="blue")

col1, col2 = st.columns([3, 1])

with col1:
    # Allow user to select star and planet properties to compare
    star_property = st.selectbox(
        "Select Star Property:",
        ["st_mass", "star_temperature_kelvin", "st_rad", "st_age"],
        format_func=lambda x: {
            "st_mass": "Star Mass (solar masses)",
            "star_temperature_kelvin": "Star Temperature (K)",
            "st_rad": "Star Radius (solar radii)",
            "st_age": "Star Age (billion years)"
        }.get(x)
    )
    
    planet_property = st.selectbox(
        "Select Planet Property:",
        ["pl_masse", "pl_rade"],
        format_func=lambda x: {
            "pl_masse": "Planet Mass (Earth masses)",
            "pl_rade": "Planet Radius (Earth radii)"
        }.get(x)
    )
    
    # Create scatter plot with trend line
    fig1 = px.scatter(
        filtered,
        x=star_property,
        y=planet_property,
        color='star_type_classification',
        size='pl_rade',
        hover_data=['disc_year','sy_pnum','discoverymethod', 'planet_habitability_score'],
        labels={
            'st_mass':'Star Mass (solar masses)',
            'star_temperature_kelvin':'Star Temperature (K)',
            'st_rad':'Star Radius (solar radii)',
            'st_age':'Star Age (billion years)',
            'pl_masse':'Planet Mass (Earth masses)',
            'pl_rade':'Planet Radius (Earth radii)',
            'star_type_classification':'Star Class',
            'disc_year':'Discovery Year',
            'sy_pnum':'No of Planets in System',
            'discoverymethod':'Discovery Method',
            'planet_habitability_score':'Habitability Score'
        },
        trendline='ols',
        trendline_scope='overall',
        trendline_color_override='darkred',
        opacity=0.7,
        log_x=True if star_property != "st_age" else False,
        log_y=True
    )
    fig1.update_layout(
        height=550, 
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("""
        The size of each point represents the planet's radius in Earth units.
    """)
    
    # Calculate correlation for insight
    if star_property in filtered.columns and planet_property in filtered.columns:
        correlation = filtered[[star_property, planet_property]].corr().iloc[0, 1]
        st.metric("Correlation Coefficient", f"{correlation:.2f}")
        
        # Add star type with the largest planets
        avg_by_star_type = filtered.groupby('star_type_classification')[planet_property].mean().sort_values()
        if not avg_by_star_type.empty:
            largest_type = avg_by_star_type.index[-1]
            largest_value = avg_by_star_type.iloc[-1]
            
            # Format the metric label and value based on the selected planet property
            metric_label = "Largest Planets" if planet_property == "pl_rade" else "Most Massive Planets"
            unit = "R⊕" if planet_property == "pl_rade" else "M⊕"
            
            st.metric(
                f"Star Type with {metric_label}", 
                f"{largest_type} ({largest_value:.2f} {unit})"
            )

st.subheader("2️⃣ Star Type to Planetary System Distribution", divider="blue")

# Create two columns
col1, col2 = st.columns([3, 1])

with col2:
    st.markdown("""
        - **Star Type:** The inner circle groups systems by the spectral type of their host stars.
        - **Number of Planets:** The outer circle shows how many planets are in each system.
        
        The size of each segment reflects the proportion of systems in that category.
    """)

with col1:
    # Sunburst chart in its own section
    fig4 = px.sunburst(
        filtered,
        path=['star_type_classification', 'sy_pnum'],
        values=None,
        color='star_type_classification',
        labels={
            'star_type_classification': 'Star Type',
            'sy_pnum': 'Planets in System',
            'labels': 'Labels',
            'count': 'Count'
        }
    )
    fig4.update_traces(
        textinfo='label+percent entry',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percent: %{percentEntry:.2%}<extra></extra>'
    )
    fig4.update_layout(height=600)
    st.plotly_chart(fig4, use_container_width=True)

# --- Section 2: Multi-Planet Systems ---
st.header("3️⃣ Multi-Planet System Distribution", divider="blue")

# Create two columns
col1, col2 = st.columns([3, 1])

with col1:
    # Get data on systems by planet count
    system_sizes_by_star = filtered.groupby(['sy_pnum', 'star_type_classification']).size().reset_index(name='count')
    
    # Create grouped bar chart by star type
    fig3 = px.bar(
        system_sizes_by_star,
        x='sy_pnum',
        y='count',
        color='star_type_classification',
        labels={
            'sy_pnum': 'Number of Planets in System',
            'count': 'Count of Systems',
            'star_type_classification': 'Star Type'
        },
    )
    
    fig3.update_layout(
        height=450,
        xaxis=dict(tickmode='linear', title='Number of Planets in System'),
        yaxis=dict(title='Number of Star Systems'),
        barmode='group',
        legend_title="Star Type"
    )
    
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.markdown("""
        The bar chart shows the breakdown of system sizes (number of planets) by star type, revealing which stellar classes are more likely to host multi-planet systems.
    """)
    
    # Add metrics about system complexity
    avg_planets = filtered['sy_pnum'].mean()
    max_planets = filtered['sy_pnum'].max()
    
    st.metric("Average Planets per System", f"{avg_planets:.2f}")
    st.metric("Most Complex System", f"{max_planets} planets")
    
    # Show star types most likely to have multi-planet systems
    multi_planet_data = filtered[filtered['sy_pnum'] > 1]
    if not multi_planet_data.empty:
        star_type_counts = multi_planet_data['star_type_classification'].value_counts()
        top_star_type = star_type_counts.index[0] if not star_type_counts.empty else "N/A"
        st.metric("Top Star Type with Multi-Planet Systems", top_star_type)

# --- Section 3: The Goldilocks Zone (moved to the end) ---
st.header("4️⃣ The Goldilocks Zone: Temperature & Orbital Balance", divider="blue")

col1, col2 = st.columns([3, 1])

with col1:
    # Create scatter plot of temperature vs orbital period
    fig2 = px.scatter(
        filtered,
        x="pl_eqt" if "pl_eqt" in filtered.columns else "equilibrium_temperature",
        y="pl_orbper" if "pl_orbper" in filtered.columns else "orbital_period_days",
        color="star_type_classification",
        size="pl_rade",
        hover_name="pl_name" if "pl_name" in filtered.columns else "planet_name",
        hover_data=[
            "planet_habitability_score", 
            "star_temperature_kelvin"
        ],
        log_y=True,
        opacity=0.7,
        labels={
            "pl_eqt": "Equilibrium Temperature (K)",
            "equilibrium_temperature": "Equilibrium Temperature (K)",
            "pl_orbper": "Orbital Period (days)",
            "orbital_period_days": "Orbital Period (days)",
            "star_type_classification": "Star Type",
            "pl_rade": "Planet Radius (Earth Radii)",
            "planet_habitability_score": 'Habitability Score',
            'star_temperature_kelvin': 'Star Temperature (K)'
        }
    )

    # Add Earth reference point
    fig2.add_trace(
        go.Scatter(
            x=[288],
            y=[365.25],
            mode="markers",
            marker=dict(color="blue", size=15, symbol="star", line=dict(color="white", width=2)),
            name="Earth",
            hoverinfo="name"
        )
    )

    # Add habitable zone reference - increased opacity for visibility
    habitable_temp_min = 180
    habitable_temp_max = 310

    fig2.add_shape(
        type="rect",
        x0=habitable_temp_min,
        x1=habitable_temp_max,
        y0=1,
        y1=1000,
        fillcolor="green",
        opacity=0.3,  # Increased opacity for better visibility
        layer="below",
        line_width=1,
        line=dict(color="green"),
    )

    fig2.add_annotation(
        x=(habitable_temp_min + habitable_temp_max) / 2,
        y=5,
        text="Potential Habitable Zone",
        showarrow=False,
        font=dict(size=14, color="darkgreen", family="Arial Bold")
    )

    fig2.update_layout(
        height=550,
    )
    
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.markdown("""
    🌿 **Green band** = temperature range for liquid water — key for life.  

    **Key:**  
    - **Temp ~290K** = Earth-like  
    - **Orbital period** affects seasons  
    - **Star type** shifts habitable zone
    """)

# Most Earth-like planets section (moved to end)
st.header("5️⃣ Top Earth-like Planets", divider="blue")

col1, col2 = st.columns([3, 1])

with col2:
    # Allow user to select how many Earth-like planets to show
    show_earthlike = st.slider("Show top Earth-like planets:", 3, 15, 5)
    
    st.markdown("""
        These planets have the highest habitability scores, reflecting Earth-like temperature, size, and orbit.
    """)

with col1:
        
    # Display the most Earth-like planets based on habitability score in a table
    most_habitable = filtered.sort_values("planet_habitability_score", ascending=False).head(show_earthlike)

    # Create a compact dataframe for display
    if len(most_habitable) > 0:
        display_df = most_habitable.copy()
        
        # Select and rename columns for readability
        cols_to_show = {
            'pl_name' if 'pl_name' in most_habitable.columns else 'planet_name': 'Planet Name',
            'planet_habitability_score': 'Habitability Score',
            'host_star_name' if 'host_star_name' in most_habitable.columns else 'star_type_classification': 'Host Star',
            'star_type_classification': 'Star Type',
            'pl_eqt' if 'pl_eqt' in most_habitable.columns else 'equilibrium_temperature': 'Temp (K)',
            'pl_rade': 'Radius (Earth)'
        }
        
        # Keep only columns that exist in the dataframe
        cols_that_exist = {k: v for k, v in cols_to_show.items() if k in most_habitable.columns}
        
        table_df = most_habitable[list(cols_that_exist.keys())].copy()
        table_df.columns = list(cols_that_exist.values())
        
        # Format the numeric columns
        if 'Habitability Score' in table_df.columns:
            table_df['Habitability Score'] = table_df['Habitability Score'].round(3)
        if 'Temp (K)' in table_df.columns:
            table_df['Temp (K)'] = table_df['Temp (K)'].round(1)
        if 'Radius (Earth)' in table_df.columns:
            table_df['Radius (Earth)'] = table_df['Radius (Earth)'].round(2)
        
        st.dataframe(table_df, use_container_width=True)
    else:
        st.info("No planets match your current filter criteria.")

# --- Footer ---
st.markdown("---")
st.caption("Data source: NASA Exoplanet Archive • Built with Streamlit & Plotly")