import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os
import numpy as np

PAGE_TITLE = "Star-Planet Relationships"
ICON = "⭐"

# --- Page Configuration ---
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=ICON,
    layout="wide"
)

# --- Load Data ---
# Assuming utils.data_loader.py is in a directory named 'utils'
# and this script is in a directory parallel to 'utils' or utils is in PYTHONPATH.
# For standalone execution, ensure load_data() returns a valid DataFrame.
# Dummy load_data for demonstration if the actual one isn't available.
try:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from utils.data_loader import load_data
    df = load_data()
except (ImportError, FileNotFoundError) as e:
    st.warning(f"Could not load data using utils.data_loader (Error: {e}). Using sample data instead.")
    sample_data = {
        'disc_year': [2000 + i for i in range(20)],
        'sy_pnum': [1, 2, 1, 3, 1, 2, 4, 1, 2, 1, 5, 1, 2, 3, 1, 2, 1, 1, 2, 3],
        'star_type_classification': ['G-type', 'M-type', 'K-type', 'F-type', 'G-type', 'M-type', 'K-type', 'F-type', 'G-type', 'M-type', 'K-type', 'F-type', 'G-type', 'M-type', 'K-type', 'F-type', 'G-type', 'M-type', 'K-type', 'F-type'],
        'discoverymethod': ['Radial Velocity', 'Transit', 'Radial Velocity', 'Transit', 'Imaging', 'Transit', 'Radial Velocity', 'Transit', 'Radial Velocity', 'Transit', 'Imaging', 'Transit', 'Radial Velocity', 'Transit', 'Radial Velocity', 'Transit', 'Imaging', 'Transit', 'Radial Velocity', 'Transit'],
        'planet_habitability_score': [0.1 + i * 0.045 for i in range(20)], # Max 0.1 + 19*0.045 = 0.1 + 0.855 = 0.955
        'host_star_name': [f'Star {chr(65+i)}' for i in range(20)],
        'st_mass': [0.8 + i*0.02 for i in range(20)],
        'star_temperature_kelvin': [5000 + i*50 for i in range(20)],
        'st_rad': [0.7 + i*0.01 for i in range(20)],
        'st_age': [1 + i*0.2 for i in range(20)],
        'pl_masse': [0.5 + i*0.3 for i in range(20)],
        'pl_rade': [0.5 + i*0.1 for i in range(20)],
        'pl_eqt': [150 + i * 15 for i in range(20)],
        'pl_orbper': [10 + i * 20 for i in range(20)],
        'pl_name': [f'Planet {i}' for i in range(20)]
    }
    df = pd.DataFrame(sample_data)
    # Ensure some scores are higher for better sorting demo
    df.loc[df.index % 4 == 0, 'planet_habitability_score'] = np.random.uniform(0.7, 0.95, len(df[df.index % 4 == 0]))


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
    "Discovery Year", min_year, max_year, (max_year-20 if max_year-20 >= min_year else min_year, max_year)
)

# Planets per System
min_sys, max_sys = int(df.sy_pnum.min()), int(df.sy_pnum.max())
system_range = st.sidebar.slider(
    "No of Planets in System", min_sys, max_sys, (min_sys, max_sys) # Changed to use min_sys
)

# Star Class
# Ensure star_type_classification is string and handle potential NaN
df['star_type_classification'] = df['star_type_classification'].astype(str)
types = sorted(df.star_type_classification.str[0].unique().tolist())
default_types = [t for t in ['G','K','M', 'F'] if t in types]
if not default_types and types: default_types = [types[0]] # Ensure at least one default if available

selected_types = st.sidebar.multiselect(
    "Star Spectral Class (First Letter)", types, default=default_types
)

# Discovery Method
# Handle potential NaN in discoverymethod
df['discoverymethod'] = df['discoverymethod'].astype(str)
all_methods = sorted(df.discoverymethod.unique().tolist())
top_methods = df.discoverymethod.value_counts().nlargest(4).index.tolist()

method_choice = st.sidebar.selectbox(
    "Discovery Method", ['All'] + top_methods # Use top_methods if you prefer, or all_methods for complete list
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
    mask &= (df.discoverymethod == method_choice)
filtered = df[mask].copy() # Use .copy() to avoid SettingWithCopyWarning on later modifications

# Display filter summary
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Showing {len(filtered)} planets**")
unique_stars_col = 'host_star_name' if 'host_star_name' in filtered.columns else 'Star Name Fallback' # Handle if column missing
if unique_stars_col not in filtered.columns and 'pl_name' in filtered.columns: # Basic fallback
    filtered[unique_stars_col] = filtered['pl_name'].apply(lambda x: x.rsplit(' ',1)[0] if isinstance(x,str) else "Unknown Star")

st.sidebar.markdown(f"**From {filtered[unique_stars_col].nunique() if unique_stars_col in filtered.columns and not filtered.empty else 0} unique star systems**")


# --- Section 1: How Stellar Properties Influence Planets ---
st.header("1️⃣ How Stellar Properties Influence Planets", divider="blue")

s1_col1, s1_col2 = st.columns([3, 1]) # Renamed columns for clarity

with s1_col1:
    star_property_options = {
        "st_mass": "Star Mass (solar masses)",
        "star_temperature_kelvin": "Star Temperature (K)",
        "st_rad": "Star Radius (solar radii)",
        "st_age": "Star Age (billion years)"
    }
    planet_property_options = {
        "pl_masse": "Planet Mass (Earth masses)",
        "pl_rade": "Planet Radius (Earth radii)"
    }
    
    valid_star_properties = [k for k in star_property_options.keys() if k in filtered.columns]
    valid_planet_properties = [k for k in planet_property_options.keys() if k in filtered.columns]

    if not valid_star_properties or not valid_planet_properties:
        st.warning("Required columns for Section 1 plots are missing from the filtered data.")
    else:
        star_property = st.selectbox(
            "Select Star Property:",
            valid_star_properties,
            format_func=lambda x: star_property_options.get(x, x)
        )
        
        planet_property = st.selectbox(
            "Select Planet Property:",
            valid_planet_properties,
            format_func=lambda x: planet_property_options.get(x, x)
        )
        
        if not filtered.empty and star_property and planet_property:
            fig1 = px.scatter(
                filtered,
                x=star_property,
                y=planet_property,
                color='star_type_classification' if 'star_type_classification' in filtered.columns else None,
                size='pl_rade' if 'pl_rade' in filtered.columns else None,
                hover_name='pl_name' if 'pl_name' in filtered.columns else None,
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
                    'planet_habitability_score':'Habitability Score',
                    'pl_name': 'Planet Name'
                },
                trendline='ols' if filtered[star_property].nunique() > 1 and filtered[planet_property].nunique() > 1 else None, # OLS needs >1 unique points
                trendline_scope='overall',
                trendline_color_override='darkred',
                opacity=0.7,
                log_x=True if star_property != "st_age" else False, # st_age might have zeros or negatives
                log_y=True
            )
            fig1.update_layout(
                height=550, 
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig1, use_container_width=True)
        elif filtered.empty:
            st.info("No data matches current filters for Section 1 plot.")
        else:
            st.warning("Please select valid star and planet properties.")


with s1_col2:
    st.markdown("The size of each point represents the planet's radius in Earth units.")
    if not filtered.empty and 'star_property' in locals() and 'planet_property' in locals() and star_property and planet_property:
        if star_property in filtered.columns and planet_property in filtered.columns and filtered[star_property].notna().any() and filtered[planet_property].notna().any():
            # Drop NaN before calculating correlation
            corr_df = filtered[[star_property, planet_property]].dropna()
            if len(corr_df) > 1 and corr_df[star_property].nunique() > 1 and corr_df[planet_property].nunique() > 1 :
                correlation = corr_df.corr().iloc[0, 1]
                st.metric("Correlation Coefficient", f"{correlation:.2f}")
            else:
                st.caption("Not enough data points for correlation.")
            
            avg_by_star_type = filtered.groupby('star_type_classification')[planet_property].mean().sort_values()
            if not avg_by_star_type.empty:
                largest_type = avg_by_star_type.index[-1]
                largest_value = avg_by_star_type.iloc[-1]
                metric_label = "Largest Planets" if planet_property == "pl_rade" else "Most Massive Planets"
                unit = "R⊕" if planet_property == "pl_rade" else "M⊕"
                st.metric(f"Star Type with {metric_label}", f"{largest_type} ({largest_value:.2f} {unit})")
        else:
            st.caption("Select properties to see metrics.")
    elif filtered.empty:
        st.caption("No data for metrics.")


st.subheader("2️⃣ Star Type to Planetary System Distribution", divider="blue")
s2_col1, s2_col2 = st.columns([3, 1])

with s2_col2:
    st.markdown("""
        - **Star Type:** The inner circle groups systems by the spectral type of their host stars.
        - **Number of Planets:** The outer circle shows how many planets are in each system.
        
        The size of each segment reflects the proportion of systems in that category.
    """)

with s2_col1:
    if not filtered.empty and 'star_type_classification' in filtered.columns and 'sy_pnum' in filtered.columns:
        fig4 = px.sunburst(
            filtered.dropna(subset=['star_type_classification', 'sy_pnum']), # Ensure no NaNs in path columns
            path=['star_type_classification', 'sy_pnum'],
            values=None, # Automatically counts occurrences
            color='star_type_classification',
            labels={'star_type_classification': 'Star Type', 'sy_pnum': 'Planets in System', 'count':'Count'}
        )
        fig4.update_traces(
            textinfo='label+percent entry',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percent: %{percentEntry:.2%}<extra></extra>'
        )
        fig4.update_layout(height=600)
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("No data matches current filters for Section 2 sunburst chart, or required columns are missing.")


st.header("3️⃣ Multi-Planet System Distribution", divider="blue")
s3_col1, s3_col2 = st.columns([3, 1])

with s3_col1:
    if not filtered.empty and 'sy_pnum' in filtered.columns and 'star_type_classification' in filtered.columns:
        system_sizes_by_star = filtered.groupby(['sy_pnum', 'star_type_classification']).size().reset_index(name='count')
        if not system_sizes_by_star.empty:
            fig3 = px.bar(
                system_sizes_by_star,
                x='sy_pnum',
                y='count',
                color='star_type_classification',
                labels={'sy_pnum': 'Number of Planets in System', 'count': 'Count of Systems', 'star_type_classification': 'Star Type'}
            )
            fig3.update_layout(
                height=450,
                xaxis=dict(tickmode='linear', title='Number of Planets in System'),
                yaxis=dict(title='Number of Star Systems'),
                barmode='group',
                legend_title="Star Type"
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No data to display for multi-planet system distribution.")
    else:
        st.info("No data matches current filters for Section 3 bar chart, or required columns are missing.")

with s3_col2:
    st.markdown("The bar chart shows the breakdown of system sizes by star type.")
    if not filtered.empty and 'sy_pnum' in filtered.columns:
        avg_planets = filtered['sy_pnum'].mean()
        max_planets = filtered['sy_pnum'].max()
        st.metric("Average Planets per System", f"{avg_planets:.2f}")
        st.metric("Most Complex System", f"{int(max_planets)} planets") # Ensure integer display

        multi_planet_data = filtered[filtered['sy_pnum'] > 1]
        if not multi_planet_data.empty and 'star_type_classification' in multi_planet_data.columns:
            star_type_counts = multi_planet_data['star_type_classification'].value_counts()
            top_star_type = star_type_counts.index[0] if not star_type_counts.empty else "N/A"
            st.metric("Top Star Type with Multi-Planet Systems", top_star_type)
        else:
            st.caption("No multi-planet systems found with current filters or star type data missing.")
    elif filtered.empty:
        st.caption("No data for metrics.")

# --- Section 4: The Goldilocks Zone (MODIFIED) ---
st.header("4️⃣ The Goldilocks Zone: Temperature & Orbital Balance", divider="blue")

s4_col1, s4_col2 = st.columns([3, 1]) # Renamed columns for clarity

with s4_col2:
    st.markdown("Adjust the **Potential Habitable Zone** temperature range (Kelvin):")
    # Ensure pl_eqt or fallback exists and has valid data for slider min/max
    temp_col_for_slider = "pl_eqt" if "pl_eqt" in filtered.columns and filtered["pl_eqt"].notna().any() else "equilibrium_temperature"
    
    min_temp_data = 0
    max_temp_data = 600 # Default max if no data
    default_min_slider = 180
    default_max_slider = 310

    if temp_col_for_slider in filtered.columns and filtered[temp_col_for_slider].notna().any():
        min_temp_data = max(0, float(filtered[temp_col_for_slider].min())) # Ensure non-negative
        max_temp_data = float(filtered[temp_col_for_slider].max())
        # Adjust defaults to be within data range if possible
        default_min_slider = max(min_temp_data, 180 if 180 < max_temp_data else min_temp_data)
        default_max_slider = min(max_temp_data, 310 if 310 > min_temp_data else max_temp_data)
        if default_min_slider > default_max_slider : # Ensure min <= max
            default_min_slider = min_temp_data
            default_max_slider = max_temp_data
            if default_min_slider > default_max_slider: # if data range is inverted or single point
                 default_max_slider = default_min_slider + 100 # arbitrary small range
    
    # Ensure slider max_value is greater than min_value
    if max_temp_data <= min_temp_data: max_temp_data = min_temp_data + 100


    temp_range_slider_value = st.slider(
        "Habitable Temperature Range (K)",
        min_value=float(min_temp_data), # Use float for consistency
        max_value=float(max_temp_data),
        value=(float(default_min_slider), float(default_max_slider)),
        key="habitable_temp_slider_goldilocks" # Unique key
    )
    habitable_temp_min_selected = temp_range_slider_value[0]
    habitable_temp_max_selected = temp_range_slider_value[1]

    st.markdown(f"""
    🌿 **Green band** = Selected temperature range ({habitable_temp_min_selected:.0f}K - {habitable_temp_max_selected:.0f}K) for potential liquid water.

    **Key:** - **Temp ~288K** (Earth's avg surface temp) is often cited.
    - **Orbital period** affects seasons.
    - **Star type** shifts the true habitable zone.
    """)

with s4_col1:
    x_col_goldilocks = "pl_eqt" if "pl_eqt" in filtered.columns else "equilibrium_temperature"
    y_col_goldilocks = "pl_orbper" if "pl_orbper" in filtered.columns else "orbital_period_days"
    name_col_goldilocks = "pl_name" if "pl_name" in filtered.columns else "planet_name"
    size_col_goldilocks = "pl_rade" if "pl_rade" in filtered.columns else None
    color_col_goldilocks = "star_type_classification" if "star_type_classification" in filtered.columns else None

    if x_col_goldilocks not in filtered.columns or y_col_goldilocks not in filtered.columns:
        st.error(f"Required columns for Goldilocks plot ('{x_col_goldilocks}', '{y_col_goldilocks}') are missing.")
    elif filtered.empty:
        st.info("No data matches current filters for the Goldilocks plot.")
    else:
        fig2 = px.scatter(
            filtered,
            x=x_col_goldilocks,
            y=y_col_goldilocks,
            color=color_col_goldilocks,
            size=size_col_goldilocks,
            hover_name=name_col_goldilocks,
            hover_data=["planet_habitability_score", "star_temperature_kelvin"],
            log_y=True,
            opacity=0.7,
            labels={
                x_col_goldilocks: "Equilibrium Temperature (K)",
                y_col_goldilocks: "Orbital Period (days)",
                color_col_goldilocks: "Star Type",
                size_col_goldilocks: "Planet Radius (Earth Radii)",
                "planet_habitability_score": 'Habitability Score',
                'star_temperature_kelvin': 'Star Temperature (K)',
                name_col_goldilocks: 'Planet Name'
            }
        )

        fig2.add_trace(
            go.Scatter(
                x=[288], y=[365.25], mode="markers",
                marker=dict(color="blue", size=15, symbol="star", line=dict(color="white", width=2)),
                name="Earth (Surface Temp)", hoverinfo="name"
            )
        )
        # Use selected values from the slider for the green zone
        fig2.add_shape(
            type="rect",
            x0=habitable_temp_min_selected,
            x1=habitable_temp_max_selected,
            y0=1, y1=1000, # As per original user code for y-range
            fillcolor="green", opacity=0.25, layer="below",
            line_width=1, line=dict(color="darkgreen"),
        )
        fig2.add_annotation(
            x=(habitable_temp_min_selected + habitable_temp_max_selected) / 2,
            y=5, # As per original user code
            text="Potential Habitable Zone", showarrow=False,
            font=dict(size=14, color="darkgreen", family="Arial Bold")
        )

        fig2.update_layout(height=550, yaxis_range=[-1, 3])
        st.plotly_chart(fig2, use_container_width=True)

# --- Section 5: Planets in Selected Habitable Zone (MODIFIED) ---
st.header(f"5️⃣ Planets in Selected Zone ({habitable_temp_min_selected:.0f}K - {habitable_temp_max_selected:.0f}K)", divider="blue")

s5_col1, s5_col2 = st.columns([3, 1]) # Renamed columns for clarity

with s5_col2:
    show_in_table_slider = st.slider(
        "Show top planets in selected zone:", 
        min_value=1, max_value=20, value=5, # Adjusted min_value
        key="show_in_table_slider_goldilocks" # Unique key
    )
    st.markdown(f"""
        These planets fall within the selected temperature range ({habitable_temp_min_selected:.0f}K - {habitable_temp_max_selected:.0f}K) 
        and are ranked by their habitability score.
    """)

with s5_col1:
    temp_col_for_table_filter = "pl_eqt" if "pl_eqt" in filtered.columns else "equilibrium_temperature"
    
    if temp_col_for_table_filter not in filtered.columns:
        st.warning(f"Temperature column ('{temp_col_for_table_filter}') not found. Cannot filter planets for the table.")
    elif "planet_habitability_score" not in filtered.columns:
        st.warning("Planet habitability score column not found. Cannot sort planets for the table.")
    elif filtered.empty:
        st.info("No planets in the base dataset to filter for the table.")
    else:
        # Filter planets within the selected temperature range from the Goldilocks slider
        planets_in_selected_zone = filtered[
            (filtered[temp_col_for_table_filter] >= habitable_temp_min_selected) &
            (filtered[temp_col_for_table_filter] <= habitable_temp_max_selected)
        ].copy()

        most_habitable_in_zone = planets_in_selected_zone.sort_values(
            "planet_habitability_score", ascending=False
        ).head(show_in_table_slider)

        if not most_habitable_in_zone.empty:
            cols_to_show_config = {
                ('pl_name', 'planet_name'): 'Planet Name',
                ('planet_habitability_score',): 'Habitability Score',
                ('host_star_name', 'star_type_classification'): 'Host Star', # Fallback for Host Star
                ('star_type_classification',): 'Star Type',
                ('pl_eqt', 'equilibrium_temperature'): 'Temp (K)',
                ('pl_rade',): 'Radius (Earth)'
            }
            
            display_columns_actual = {}
            for actual_cols_tuple, display_name in cols_to_show_config.items():
                for actual_col in actual_cols_tuple:
                    if actual_col in most_habitable_in_zone.columns:
                        display_columns_actual[actual_col] = display_name
                        break 
            
            table_df_selected_zone = most_habitable_in_zone[list(display_columns_actual.keys())].copy()
            table_df_selected_zone.columns = [display_columns_actual[col] for col in table_df_selected_zone.columns]

            if 'Habitability Score' in table_df_selected_zone.columns:
                table_df_selected_zone['Habitability Score'] = pd.to_numeric(table_df_selected_zone['Habitability Score'], errors='coerce').round(3)
            if 'Temp (K)' in table_df_selected_zone.columns:
                table_df_selected_zone['Temp (K)'] = pd.to_numeric(table_df_selected_zone['Temp (K)'], errors='coerce').round(1)
            if 'Radius (Earth)' in table_df_selected_zone.columns:
                table_df_selected_zone['Radius (Earth)'] = pd.to_numeric(table_df_selected_zone['Radius (Earth)'], errors='coerce').round(2)
            
            st.dataframe(table_df_selected_zone, use_container_width=True, hide_index=True)
        else:
            st.info(f"No planets found within the selected temperature range ({habitable_temp_min_selected:.0f}K - {habitable_temp_max_selected:.0f}K) and other active filters.")


# --- Footer ---
st.markdown("---")
st.caption("Data source: NASA Exoplanet Archive (via preprocessed dataset) • Built with Streamlit & Plotly")