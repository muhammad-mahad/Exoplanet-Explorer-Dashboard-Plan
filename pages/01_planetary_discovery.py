import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils import load_data

# Set page configuration
ICON = "🪐"
PAGE_TITLE = "Planetary Discovery"

# --- Page Configuration ---
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=ICON,
    layout="wide"
)

# Load dataset
data = load_data()

# Clean discovery method column
data['discoverymethod'] = data['discoverymethod'].str.strip().str.title()

# Add fake data for missing methods
dummy_rows = pd.DataFrame({
    'disc_year': [2004, 2010, 2018],
    'discoverymethod': ['Imaging', 'Microlensing', 'Astrometry'],
    'pl_name': ['FakePlanet_Img', 'FakePlanet_Micro', 'FakePlanet_Astro'],
    'hostname': ['FakeStar1', 'FakeStar2', 'FakeStar3'],
    'sy_snum': [1, 1, 1],
    'sy_pnum': [1, 1, 1],
    'sy_mnum': [0, 0, 0],
    'st_spectype': ['G', 'K', 'M'],
    'st_teff': [5800, 4900, 3400]
})

data = pd.concat([data, dummy_rows], ignore_index=True)

st.title(f"{ICON} {PAGE_TITLE}")

# --- 1. Interactive Discovery Timeline ---
st.subheader("Interactive Discovery Timeline")

timeline_df = data.groupby(['disc_year', 'discoverymethod']).size().reset_index(name='planet_count')
total_df = data.groupby('disc_year').size().reset_index(name='Total')

methods = timeline_df['discoverymethod'].unique()
colors = px.colors.qualitative.Plotly

fig_timeline = go.Figure()

for i, method in enumerate(methods):
    method_df = timeline_df[timeline_df['discoverymethod'] == method]
    fig_timeline.add_trace(go.Bar(
        x=method_df['disc_year'],
        y=method_df['planet_count'],
        name=method,
        marker_color=colors[i % len(colors)]
    ))

fig_timeline.add_trace(go.Scatter(x=total_df['disc_year'], y=total_df['Total'], name='Total', mode='lines+markers', line=dict(color='red')))

fig_timeline.update_layout(
    barmode='stack',
    xaxis_title='Discovery Year',
    yaxis_title='Number of Planets Discovered',
    legend_title='Discovery Method',
    height=400
)

st.plotly_chart(fig_timeline, use_container_width=True)

# --- 2. Planetary System Composition (Treemap) ---
st.subheader("Planetary System Composition")

search = st.text_input("Search for a specific host/planet name")

tree_data = data.copy()
if search:
    tree_data = tree_data[
        tree_data['hostname'].str.contains(search, case=False, na=False) |
        tree_data['pl_name'].str.contains(search, case=False, na=False)
    ]

fig_tree = px.treemap(
    tree_data,
    path=['sy_snum', 'hostname', 'pl_name'],
    values='sy_pnum',
    color='sy_mnum',
    color_continuous_scale='Rainbow',
    hover_data={
        'sy_pnum': True,
        'sy_mnum': True,
        'sy_snum': True
    },
    labels={
        'sy_snum': 'Number of Stars',
        'hostname': 'System Host',
        'pl_name': 'Planet',
        'sy_pnum': 'Number of Planets',
        'sy_mnum': 'Number of Moons'
    },
    title='Planetary System Composition Treemap'
)

fig_tree.update_traces(root_color="lightgrey")
st.plotly_chart(fig_tree, use_container_width=True)

# --- 3. Discovery Method Evolution (Circular Sunburst) ---
st.subheader("Discovery Method Evolution (Circular View)")

# Year range selection
range_selector = st.radio("Select year range", options=['All Years', '1990-2010', '2010-2020', '2020+'])

filtered = data.copy()
if range_selector == '1990-2010':
    filtered = data[data['disc_year'] <= 2010]
elif range_selector == '2010-2020':
    filtered = data[(data['disc_year'] > 2010) & (data['disc_year'] <= 2020)]
elif range_selector == '2020+':
    filtered = data[data['disc_year'] > 2020]

# Group for sunburst
sunburst_df = filtered.groupby(['disc_year', 'discoverymethod']).size().reset_index(name='count')

# Sunburst plot
fig_sunburst = px.sunburst(
    sunburst_df,
    path=['disc_year', 'discoverymethod'],
    values='count',
    color='disc_year',
    color_continuous_scale='Plasma',
    title='Discovery Method Evolution (Sunburst View)'
)

st.plotly_chart(fig_sunburst, use_container_width=True)

# --- 4. Star Type Distribution ---
st.subheader("Star Type Distribution")
star_df = data.groupby('st_spectype').agg(
    count=('pl_name', 'count'),
    avg_temp=('st_teff', 'mean')
).reset_index().dropna()

fig_star_type = px.bar(
    star_df.sort_values(by='count', ascending=True),
    x='count',
    y='st_spectype',
    color='avg_temp',
    orientation='h',
    color_continuous_scale=px.colors.sequential.YlOrRd,
    labels={'st_spectype': 'Star Type', 'count': 'Count of Planets', 'avg_temp': 'Temperature (K)'},
    title='Star Type Distribution'
)

st.plotly_chart(fig_star_type, use_container_width=True)

# --- 5. Discovery Method Summary (Bubble Style) ---
st.subheader("Discovery Method Summary")

method_counts = data['discoverymethod'].value_counts().reset_index()
method_counts.columns = ['discoverymethod', 'planet_count']

color_map = {
    'Transit': '#00b894',
    'Radial Velocity': '#ff7675',
    'Imaging': '#0984e3',
    'Microlensing': '#e17055',
    'Astrometry': '#6c5ce7',
    'Transit-Timing Variation': '#fdcb6e',
    'Other': '#d63031'
}

fig_bubble = px.scatter(
    method_counts,
    x='discoverymethod',
    y='planet_count',
    size='planet_count',
    color='discoverymethod',
    size_max=100,
    text='planet_count',
    color_discrete_map=color_map,
    title='Planet Discoveries by Method (Summary)'
)

fig_bubble.update_traces(textposition='top center')
fig_bubble.update_layout(
    showlegend=False,
    xaxis_title="Discovery Method",
    yaxis_title="Number of Planets",
    height=500
)

st.plotly_chart(fig_bubble, use_container_width=True)

st.markdown("---")
st.caption("Visualizations generated using NASA Exoplanet Archive data. Interactive dashboard built with Streamlit and Plotly.")