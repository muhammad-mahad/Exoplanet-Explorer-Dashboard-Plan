import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

def star_planet_relationships_page(data):
    """
    Streamlit page focused on exploring the relationships between stars and their planets.
    
    Args:
        data (pd.DataFrame): Preprocessed exoplanet dataset
    """
    st.title("⭐🪐 Star-Planet Relationships")
    
    st.markdown("""
    ### Explore how stellar properties influence planetary systems
    
    This page allows you to investigate the complex relationships between stars and their planets.
    Discover patterns in how stellar properties like mass, temperature, and age correlate with 
    planetary characteristics such as size, orbit, and potential habitability.
    """)
    
    # Sidebar filters for interactive exploration
    st.sidebar.header("Filter Data")
    
    # Filter by star type
    available_star_types = sorted(data['star_type_classification'].unique())
    selected_star_types = st.sidebar.multiselect(
        "Select Star Types", 
        available_star_types,
        default=available_star_types[:3]  # Default to first 3 types
    )
    
    # Filter by discovery method
    available_discovery_methods = sorted(data['discovery_method'].unique())
    selected_discovery_methods = st.sidebar.multiselect(
        "Discovery Methods",
        available_discovery_methods,
        default=available_discovery_methods  # Default to all methods
    )
    
    # Date range slider
    min_year = int(data['discovery_year'].min())
    max_year = int(data['discovery_year'].max())
    year_range = st.sidebar.slider(
        "Discovery Year Range",
        min_year, max_year,
        (min_year, max_year)
    )
    
    # Apply filters
    filtered_data = data[
        (data['star_type_classification'].isin(selected_star_types)) &
        (data['discovery_method'].isin(selected_discovery_methods)) &
        (data['discovery_year'] >= year_range[0]) &
        (data['discovery_year'] <= year_range[1])
    ]
    
    # Display filtered data count
    st.sidebar.markdown(f"**Showing:** {len(filtered_data)} planets")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Analysis Options")
        analysis_type = st.radio(
            "Choose Analysis",
            ["Planet Size vs Star Properties", 
             "Orbital Characteristics", 
             "System Architecture",
             "Habitability Factors"]
        )
    
    with col2:
        # Quick facts about the filtered dataset
        st.subheader("Quick Stats")
        
        # Calculate some interesting metrics
        avg_planets_per_star = filtered_data.groupby('host_star_name').size().mean()
        most_common_star_type = filtered_data['star_type_classification'].value_counts().idxmax()
        planets_in_habitable_zone = filtered_data[
            (filtered_data['planet_habitability_score'] > 0.5)
        ].shape[0]
        
        st.markdown(f"""
        - **Avg planets per star:** {avg_planets_per_star:.2f}
        - **Most common star type:** {most_common_star_type}
        - **Potentially habitable planets:** {planets_in_habitable_zone}
        """)
    
    # Main analysis section based on selection
    st.markdown("---")
    
    if analysis_type == "Planet Size vs Star Properties":
        planet_size_vs_star_analysis(filtered_data)
    
    elif analysis_type == "Orbital Characteristics":
        orbital_characteristics_analysis(filtered_data)
    
    elif analysis_type == "System Architecture":
        system_architecture_analysis(filtered_data)
    
    elif analysis_type == "Habitability Factors":
        habitability_analysis(filtered_data)


def planet_size_vs_star_analysis(data):
    """Analysis of planet size in relation to star properties"""
    st.subheader("Planet Size vs Star Properties")
    
    # Allow user to select which star property to analyze against planet size
    star_property = st.selectbox(
        "Select Star Property to Compare Against Planet Size:",
        ["star_mass_solar_masses", "star_temperature_kelvin", "star_radius_solar_radii", "star_age_billion_years"],
        format_func=lambda x: {
            "star_mass_solar_masses": "Star Mass (solar masses)",
            "star_temperature_kelvin": "Star Temperature (K)",
            "star_radius_solar_radii": "Star Radius (solar radii)",
            "star_age_billion_years": "Star Age (billion years)"
        }.get(x)
    )
    
    # Create a scatter plot of planet radius vs selected star property
    fig = px.scatter(
        data,
        x=star_property,
        y="planet_radius_earth_radii",
        color="star_type_classification",
        hover_name="planet_name",
        hover_data=["host_star_name", "discovery_year", "discovery_method"],
        opacity=0.7,
        size="planet_mass_earth_masses",
        size_max=20,
        title=f"Planet Size vs {star_property.replace('_', ' ').title()}",
        labels={
            "planet_radius_earth_radii": "Planet Radius (Earth radii)",
            "star_mass_solar_masses": "Star Mass (solar masses)",
            "star_temperature_kelvin": "Star Temperature (K)",
            "star_radius_solar_radii": "Star Radius (solar radii)",
            "star_age_billion_years": "Star Age (billion years)",
            "star_type_classification": "Star Type"
        }
    )
    
    # Add a trend line
    fig.update_layout(
        height=600,
        width=800
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Additional insights - correlation stats
    col1, col2 = st.columns(2)
    
    with col1:
        # Calculate correlation between planet radius and selected star property
        correlation = data['planet_radius_earth_radii'].corr(data[star_property])
        st.metric(
            "Correlation Coefficient", 
            f"{correlation:.3f}",
            help="Pearson correlation coefficient between planet radius and selected star property"
        )
    
    with col2:
        # Calculate average planet radius by star type
        avg_radius_by_star_type = data.groupby('star_type_classification')['planet_radius_earth_radii'].mean().sort_values()
        st.metric(
            "Star Type with Largest Planets", 
            f"{avg_radius_by_star_type.index[-1]} ({avg_radius_by_star_type.iloc[-1]:.2f} R⊕)",
            help="Star classification with the largest average planet radius"
        )
    
    # Show secondary plot - planet radius distribution by star type
    st.subheader("Planet Size Distribution by Star Type")
    
    fig = px.box(
        data,
        x="star_type_classification", 
        y="planet_radius_earth_radii",
        color="star_type_classification",
        notched=True,
        title="Distribution of Planet Sizes Across Different Star Types",
        labels={
            "star_type_classification": "Star Type",
            "planet_radius_earth_radii": "Planet Radius (Earth radii)"
        }
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("Analysis Insights"):
        st.markdown("""
        ### Key Findings:
        - **Size Correlation**: There is often a correlation between star mass and planet size, with massive stars 
          tending to host larger planets.
        - **Hot Jupiters**: Very large planets close to stars (Hot Jupiters) are more common around hotter star types.
        - **Small Planets**: Smaller, rocky planets are most frequently found around K and M-type stars.
        
        These patterns reflect the complex physics of planetary formation, where the available material in 
        the protoplanetary disk and the star's radiation affect what kinds of planets can form and survive.
        """)


def orbital_characteristics_analysis(data):
    """Analysis of orbital characteristics in relation to star properties"""
    st.subheader("Orbital Characteristics Analysis")
    
    # Select x-axis parameter (star property)
    x_param = st.selectbox(
        "Select Star Property:",
        ["star_mass_solar_masses", "star_temperature_kelvin", "star_radius_solar_radii", "star_age_billion_years"],
        format_func=lambda x: {
            "star_mass_solar_masses": "Star Mass (solar masses)",
            "star_temperature_kelvin": "Star Temperature (K)",
            "star_radius_solar_radii": "Star Radius (solar radii)",
            "star_age_billion_years": "Star Age (billion years)"
        }.get(x)
    )
    
    # Select y-axis parameter (orbital characteristic)
    y_param = st.selectbox(
        "Select Orbital Parameter:",
        ["orbital_period_days", "orbit_semi_major_axis_au", "orbital_eccentricity"],
        format_func=lambda x: {
            "orbital_period_days": "Orbital Period (days)",
            "orbit_semi_major_axis_au": "Semi-Major Axis (AU)",
            "orbital_eccentricity": "Orbital Eccentricity"
        }.get(x)
    )
    
    # Create the scatter plot
    fig = px.scatter(
        data,
        x=x_param,
        y=y_param,
        color="star_type_classification",
        size="planet_radius_earth_radii",
        hover_name="planet_name",
        hover_data=["host_star_name", "discovery_year", "discovery_method"],
        opacity=0.7,
        log_x='auto',  # Auto-detect if log scale is appropriate
        log_y='auto',  # Auto-detect if log scale is appropriate
        title=f"Relationship between {y_param.replace('_', ' ').title()} and {x_param.replace('_', ' ').title()}",
        labels={
            "orbital_period_days": "Orbital Period (days)",
            "orbit_semi_major_axis_au": "Semi-Major Axis (AU)",
            "orbital_eccentricity": "Orbital Eccentricity",
            "star_mass_solar_masses": "Star Mass (solar masses)",
            "star_temperature_kelvin": "Star Temperature (K)",
            "star_radius_solar_radii": "Star Radius (solar radii)",
            "star_age_billion_years": "Star Age (billion years)",
            "star_type_classification": "Star Type",
            "planet_radius_earth_radii": "Planet Radius (Earth radii)"
        }
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add some additional plots for deeper analysis
    st.subheader("Orbital Period Distribution by Star Type")
    
    # Create log-scaled orbital period histogram by star type
    fig = px.histogram(
        data,
        x="orbital_period_days",
        color="star_type_classification",
        log_x=True,
        barmode="overlay",
        opacity=0.7,
        nbins=50,
        title="Distribution of Orbital Periods Across Star Types",
        labels={
            "orbital_period_days": "Orbital Period (days)",
            "star_type_classification": "Star Type"
        }
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Interactive orbital relationship explorer
    st.subheader("Orbital Parameter Relations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Calculate correlation between selected parameters
        correlation = data[x_param].corr(data[y_param])
        st.metric(
            "Correlation", 
            f"{correlation:.3f}",
            help=f"Pearson correlation coefficient between {x_param} and {y_param}"
        )
    
    with col2:
        # Calculate a meaningful metric based on the selected orbital parameter
        if y_param == "orbital_period_days":
            metric_value = data.groupby('star_type_classification')[y_param].median().sort_values().iloc[-1]
            metric_name = data.groupby('star_type_classification')[y_param].median().sort_values().index[-1]
            st.metric(
                "Star Type with Longest Median Orbit",
                f"{metric_name} ({metric_value:.1f} days)",
                help="Star type with the longest median orbital period"
            )
        elif y_param == "orbit_semi_major_axis_au":
            metric_value = data.groupby('star_type_classification')[y_param].median().sort_values().iloc[-1]
            metric_name = data.groupby('star_type_classification')[y_param].median().sort_values().index[-1]
            st.metric(
                "Star Type with Widest Median Orbit",
                f"{metric_name} ({metric_value:.2f} AU)",
                help="Star type with the widest median orbital distance"
            )
        else:  # orbital_eccentricity
            metric_value = data.groupby('star_type_classification')[y_param].mean().sort_values().iloc[-1]
            metric_name = data.groupby('star_type_classification')[y_param].mean().sort_values().index[-1]
            st.metric(
                "Star Type with Most Eccentric Orbits",
                f"{metric_name} ({metric_value:.3f})",
                help="Star type with the highest average orbital eccentricity"
            )
    
    with st.expander("Orbital Dynamics Insights"):
        st.markdown("""
        ### Key Orbital Patterns:
        
        - **Kepler's Third Law**: The data generally follows Kepler's third law of planetary motion, where 
          orbital period squared is proportional to semi-major axis cubed.
        
        - **Hot Jupiters vs Cold Jupiters**: Large gas giants can be found in very close orbits (Hot Jupiters, 
          with periods of a few days) or distant orbits (Cold Jupiters, with periods of years or decades).
        
        - **Orbital Eccentricity**: Eccentric orbits are more common for planets in wide orbits, while planets
          in close orbits tend to have more circular paths due to tidal forces.
        
        - **Migration**: Many planets are found in orbits where they likely couldn't have formed, suggesting
          they migrated from their formation location due to interactions with the protoplanetary disk or
          other planets.
        """)


def system_architecture_analysis(data):
    """Analysis of planetary system architectures"""
    st.subheader("Planetary System Architecture")
    
    # Calculate systems with multiple planets
    system_sizes = data.groupby('host_star_name')['planet_name'].count().reset_index()
    system_sizes.columns = ['host_star_name', 'planet_count']
    
    # Merge with star data (keeping only one entry per star)
    star_data = data.drop_duplicates('host_star_name')[['host_star_name', 'star_type_classification', 
                                                       'star_mass_solar_masses', 
                                                       'star_temperature_kelvin']]
    systems_df = pd.merge(system_sizes, star_data, on='host_star_name')
    
    # Filter to systems with at least 2 planets for meaningful analysis
    multi_planet_systems = systems_df[systems_df['planet_count'] > 1]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Stars in Dataset", 
                  len(systems_df), 
                  help="Number of unique host stars in the filtered dataset")
    
    with col2:
        st.metric("Multi-Planet Systems", 
                  len(multi_planet_systems), 
                  help="Number of systems with 2+ planets")
    
    # Planetary system size distribution
    fig = px.histogram(
        systems_df,
        x="planet_count",
        color="star_type_classification",
        nbins=max(systems_df['planet_count']),
        title="Distribution of Planetary System Sizes",
        labels={
            "planet_count": "Number of Planets in System",
            "star_type_classification": "Star Type"
        }
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # System architecture characteristics
    st.subheader("System Architecture by Star Type")
    
    # Calculate average planets per system by star type
    avg_planets_by_star_type = systems_df.groupby('star_type_classification')['planet_count'].mean().reset_index()
    avg_planets_by_star_type.columns = ['Star Type', 'Average Planets per System']
    
    fig = px.bar(
        avg_planets_by_star_type,
        x='Star Type',
        y='Average Planets per System',
        color='Star Type',
        title="Average Number of Planets by Star Type",
        labels={
            "Star Type": "Star Classification",
            "Average Planets per System": "Average Planets per System"
        }
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Relationship between star mass and system multiplicity
    fig = px.scatter(
        systems_df,
        x="star_mass_solar_masses",
        y="planet_count",
        color="star_type_classification",
        size="star_temperature_kelvin",
        size_max=15,
        opacity=0.7,
        hover_name="host_star_name",
        title="Relationship Between Star Mass and Number of Planets",
        labels={
            "star_mass_solar_masses": "Star Mass (solar masses)",
            "planet_count": "Number of Planets",
            "star_type_classification": "Star Type",
            "star_temperature_kelvin": "Star Temperature (K)"
        }
    )
    
    # Add trendline
    fig.update_layout(height=500)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Analysis of planet spacing in multi-planet systems
    if len(multi_planet_systems) >= 5:  # Only show if we have enough multi-planet systems
        st.subheader("Planetary Spacing in Multi-Planet Systems")
        
        # Get top 5 systems with most planets for orbital spacing analysis
        top_systems = multi_planet_systems.sort_values('planet_count', ascending=False).head(5)['host_star_name'].tolist()
        
        # Create plot to visualize orbital spacing
        fig = make_subplots(rows=len(top_systems), cols=1, 
                          subplot_titles=[f"System: {sys}" for sys in top_systems],
                          vertical_spacing=0.1)
        
        for i, system_name in enumerate(top_systems):
            # Get planets for this system
            system_planets = data[data['host_star_name'] == system_name].sort_values('orbit_semi_major_axis_au')
            
            # Add planets as markers
            fig.add_trace(
                go.Scatter(
                    x=system_planets['orbit_semi_major_axis_au'],
                    y=[1] * len(system_planets),  # All at same y level
                    mode='markers',
                    marker=dict(
                        size=system_planets['planet_radius_earth_radii'] * 2,  # Size proportional to radius
                        color=system_planets['equilibrium_temperature'],
                        colorscale='Viridis',
                        showscale=False
                    ),
                    text=system_planets['planet_name'],
                    hovertemplate='<b>%{text}</b><br>Orbit: %{x:.2f} AU<br>',
                    name=system_name
                ),
                row=i+1, col=1
            )
            
            # Format the subplot
            fig.update_xaxes(type='log', title_text="Orbital Distance (AU)" if i == len(top_systems)-1 else "", row=i+1, col=1)
            fig.update_yaxes(showticklabels=False, row=i+1, col=1)
        
        fig.update_layout(
            height=150 * len(top_systems),
            title_text="Orbital Architecture of Top 5 Largest Planetary Systems",
            showlegend=False,
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("System Architecture Insights"):
        st.markdown("""
        ### Key Architecture Patterns:
        
        - **System Multiplicity**: Many stars host multiple planets, with some systems containing 5+ planets.
        
        - **Peas in a Pod**: In multi-planet systems, planets often have similar sizes and regular spacing,
          a phenomenon known as "peas in a pod."
        
        - **Star Type Influence**: Different star types tend to host different system architectures:
          - M-dwarfs often have tightly packed systems of small planets
          - G-type stars like our Sun can host diverse planetary architectures
          - Massive stars tend to have fewer detected planets
        
        - **Migration and Stability**: The current architecture of planetary systems reflects both their 
          formation conditions and subsequent dynamical evolution through migration and gravitational interactions.
        """)


def habitability_analysis(data):
    """Analysis focused on potential habitability factors"""
    st.subheader("Habitability Analysis")
    
    # Create a more visual representation of the data
    st.markdown("""
    Explore what makes a planet potentially habitable and how stellar properties influence the 
    habitability zone - the region around a star where conditions might be right for liquid water.
    """)
    
    # Filter to show planets with calculated habitability scores
    habitability_data = data.dropna(subset=['planet_habitability_score'])
    
    # Let user select habitability threshold
    hab_threshold = st.slider(
        "Habitability Score Threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.05,
        help="Filter planets by minimum habitability score"
    )
    
    # Create highlighted data for potentially habitable planets
    potentially_habitable = habitability_data[habitability_data['planet_habitability_score'] >= hab_threshold]
    
    # Display counts
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total Planets", 
            len(habitability_data),
            help="Number of planets with habitability data"
        )
    
    with col2:
        st.metric(
            "Potentially Habitable", 
            len(potentially_habitable),
            help=f"Planets with habitability score ≥ {hab_threshold}"
        )
    
    with col3:
        percentage = (len(potentially_habitable) / len(habitability_data) * 100) if len(habitability_data) > 0 else 0
        st.metric(
            "Percentage", 
            f"{percentage:.1f}%",
            help="Percentage of potentially habitable planets"
        )
    
    # Create habitability visualization
    st.subheader("Habitability Map")
    
    # The main habitability scatter plot
    fig = px.scatter(
        habitability_data,
        x="star_temperature_kelvin",
        y="orbit_semi_major_axis_au",
        color="planet_habitability_score",
        size="planet_radius_earth_radii",
        hover_name="planet_name",
        hover_data=["host_star_name", "equilibrium_temperature", "planet_habitability_score"],
        color_continuous_scale="RdYlGn",  # Red-Yellow-Green color scale
        range_color=[0, 1],
        opacity=0.85,
        log_y=True,
        title="Planet Habitability Map: Star Temperature vs Orbital Distance",
        labels={
            "star_temperature_kelvin": "Star Temperature (K)",
            "orbit_semi_major_axis_au": "Orbital Distance (AU)",
            "planet_habitability_score": "Habitability Score",
            "planet_radius_earth_radii": "Planet Size (Earth radii)"
        }
    )
    
    # Customize the figure
    fig.update_layout(
        height=600,
        coloraxis_colorbar=dict(
            title="Habitability<br>Score",
            thicknessmode="pixels", thickness=20,
            lenmode="pixels", len=300,
            tickvals=[0, 0.25, 0.5, 0.75, 1],
            ticktext=["0<br>(Not habitable)", "0.25", "0.5", "0.75", "1<br>(Most habitable)"]
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Table of most habitable planets
    if len(potentially_habitable) > 0:
        st.subheader(f"Top Potentially Habitable Planets (Score ≥ {hab_threshold})")
        
        # Show the most potentially habitable planets
        habitable_display = potentially_habitable.sort_values('planet_habitability_score', ascending=False)
        
        # Select and rename columns for display
        display_cols = {
            'planet_name': 'Planet Name',
            'host_star_name': 'Host Star',
            'star_type_classification': 'Star Type',
            'planet_radius_earth_radii': 'Radius (Earth)',
            'planet_mass_earth_masses': 'Mass (Earth)',
            'equilibrium_temperature': 'Temp (K)',
            'planet_habitability_score': 'Habitability Score',
            'orbit_semi_major_axis_au': 'Orbit (AU)'
        }
        
        st.dataframe(
            habitable_display[display_cols.keys()].rename(columns=display_cols),
            hide_index=True,
            column_config={
                'Habitability Score': st.column_config.ProgressColumn(
                    'Habitability Score',
                    help='Habitability score from 0 to 1',
                    format="%.2f",
                    min_value=0,
                    max_value=1
                ),
                'Radius (Earth)': st.column_config.NumberColumn(
                    'Radius (R⊕)',
                    format="%.2f"
                ),
                'Mass (Earth)': st.column_config.NumberColumn(
                    'Mass (M⊕)',
                    format="%.2f"
                ),
                'Temp (K)': st.column_config.NumberColumn(
                    'Temp (K)',
                    format="%d"
                ),
                'Orbit (AU)': st.column_config.NumberColumn(
                    'Orbit (AU)',
                    format="%.3f"
                )
            }
        )

    # Distribution of habitability by star type
    st.subheader("Habitability by Star Type")
    
    fig = px.box(
        habitability_data,
        x="star_type_classification",
        y="planet_habitability_score",
        color="star_type_classification",
        notched=True,
        title="Distribution of Habitability Scores Across Star Types",
        labels={
            "star_type_classification": "Star Type",
            "planet_habitability_score": "Habitability Score"
        }
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Relationship between planet size and habitability
    st.subheader("Planet Size vs Habitability")
    
    fig = px.scatter(
        habitability_data,
        x="planet_radius_earth_radii",
        y="planet_habitability_score",
        color="star_type_classification",
        opacity=0.7,
        hover_name="planet_name",
        hover_data=["host_star_name", "equilibrium_temperature"],
        title="Relationship Between Planet Size and Habitability",
        labels={
            "planet_radius_earth_radii": "Planet Radius (Earth radii)",
            "planet_habitability_score": "Habitability Score",
            "star_type_classification": "Star Type"
        }
    )
    
    fig.add_shape(
        type="rect",
        x0=0.5, y0=hab_threshold,
        x1=2.0, y1=1.0,
        line=dict(color="green", width=2, dash="dash"),
        fillcolor="rgba(0,255,0,0.1)",
        name="Earth-like + Habitable"
    )
    
    fig.add_annotation(
        x=1.25, y=0.9,
        text="Earth-like<br>Habitable Zone",
        showarrow=False,
        font=dict(color="green")
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("Habitability Insights"):
        st.markdown("""
        ### What Makes a Planet Potentially Habitable?
        
        - **The Goldilocks Zone**: Planets need to orbit at the right distance from their star—not too hot,
          not too cold—for liquid water to potentially exist on their surface.
        
        - **Planet Size Matters**: Planets between 0.5 and 2.0 Earth radii are most likely to be rocky rather
          than gaseous, a prerequisite for habitability as we understand it.
        
        - **Star Type Influence**: 
          - M-dwarf stars have close-in habitable zones but higher radiation and tidal locking challenges
          - G and K-type stars provide more stable environments with wider habitable zones
          - Massive, hot stars have short lifespans that may not allow enough time for life to evolve
        
        - **Beyond Temperature**: True habitability depends on many factors not fully captured in this analysis,
          including atmospheric composition, magnetic field strength, geological activity, and star stability.
        
        The planets highlighted here are those that are most similar to Earth in the factors we can measure,
        but we still have much to learn about what makes a planet truly habitable.
        """)

# Page header
st.title(f"⭐ {PAGE_TITLE}")
st.markdown("""
    Explore the intricate dance between stars and their planetary companions.
    Uncover the cosmic relationships that shape planetary systems.
""")

# Load and preprocess data
data = load_data()

star_planet_relationships_page(data)