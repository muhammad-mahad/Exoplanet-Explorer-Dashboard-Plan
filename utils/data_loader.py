import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

# Load data (using cache for performance)
@st.cache_data
def load_data():
    """Load and preprocess the exoplanet dataset"""
    # In a real app, you would load from a file instead
    # For demo purposes, I'll create a simulated dataset if needed
    
    # Check if the file exists in the current directory or in the parent directory
    paths_to_check = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), 
                                     '../data/exoplanets_full_features.csv'))
    ]
    
    data = None
    for path in paths_to_check:
        if os.path.exists(path):
            data = pd.read_csv(path)
            break

    # If no real data file found, create simulated data for demonstration
    if data is None:
        st.warning("No exoplanet data file found. Using simulated data for demonstration.")
        # Create simulated data with all required columns
        np.random.seed(42)
        n_samples = 500
        
        # Generate realistic looking data
        data = pd.DataFrame({
            # Planet Information
            'pl_name': [f'Planet-{i}' for i in range(n_samples)],
            'hostname': [f'Star-{i//3}' for i in range(n_samples)],  # ~3 planets per star on average
            'disc_year': np.random.choice(range(1995, 2025), n_samples),
            'discoverymethod': np.random.choice(['Transit', 'Radial Velocity', 'Imaging', 'Microlensing', 'Timing'], 
                                              n_samples, p=[0.5, 0.3, 0.1, 0.05, 0.05]),
            
            # System Information
            'sy_snum': np.random.choice([1, 2, 3], n_samples, p=[0.8, 0.15, 0.05]),
            'sy_pnum': np.random.choice(range(1, 10), n_samples),
            'sy_mnum': np.random.choice(range(0, 5), n_samples, p=[0.4, 0.3, 0.15, 0.1, 0.05]),
            
            # Habitability Factors
            'pl_rade': np.random.lognormal(0, 1, n_samples),  # Earth radii
            'pl_masse': np.random.lognormal(0, 1.5, n_samples),  # Earth masses
            'pl_orbper': np.random.lognormal(3, 2, n_samples),  # Orbital period in days
            'pl_orbsmax': np.random.lognormal(-0.5, 1, n_samples),  # Orbit semi-major axis in AU
            'pl_eqt': np.random.normal(300, 200, n_samples),  # Equilibrium temperature
            'pl_insol': np.random.lognormal(0, 2, n_samples),  # Insolation flux
            
            # Physical Characteristics
            'pl_dens': np.random.lognormal(1, 0.5, n_samples),  # Density
            'pl_orbeccen': np.random.beta(1, 5, n_samples),  # Orbital eccentricity
            'pl_bmasse': np.random.lognormal(0, 1.5, n_samples),  # Best mass measurement
            
            # Star Information
            'st_spectype': np.random.choice(['G', 'K', 'M', 'F', 'A', 'B', 'O'], n_samples, 
                                           p=[0.3, 0.3, 0.2, 0.1, 0.05, 0.03, 0.02]),
            'st_teff': np.random.normal(5000, 1500, n_samples),  # Star temperature
            'st_rad': np.random.lognormal(0, 0.5, n_samples),  # Star radius
            'st_mass': np.random.lognormal(0, 0.3, n_samples),  # Star mass
            'st_age': np.random.lognormal(0, 1, n_samples) * 5,  # Star age in billions of years
            
            # Location Information
            'ra': np.random.uniform(0, 360, n_samples),  # Right ascension
            'dec': np.random.uniform(-90, 90, n_samples),  # Declination
            'sy_dist': np.random.lognormal(3, 1, n_samples),  # Distance in parsecs
        })
    
    # Data cleaning and preprocessing
    # Handle missing values
    numeric_cols = data.select_dtypes(include=['float64', 'int64']).columns
    data[numeric_cols] = data[numeric_cols].fillna(data[numeric_cols].median())
    categorical_cols = data.select_dtypes(include=['object']).columns
    data[categorical_cols] = data[categorical_cols].fillna('Unknown')
    
    # Add some derived columns for analysis
    data['earth_similarity'] = 1 / (1 + 
                                   np.abs(np.log10(data['pl_rade'])) + 
                                   np.abs(np.log10(data['pl_masse'] + 0.001)) +
                                   np.abs(data['pl_eqt'] - 288) / 288)
    
    return data