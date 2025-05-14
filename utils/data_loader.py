import streamlit as st
import pandas as pd
import numpy as np
import os

def comprehensive_exoplanet_preprocessing(file_path):
    """
    Comprehensive preprocessing of exoplanet dataset with detailed cleaning and feature engineering
    
    Args:
        file_path (str): Path to the exoplanet CSV file
    
    Returns:
        pd.DataFrame: Cleaned and enhanced exoplanet dataset
    """
    # Read the dataset
    df = pd.read_csv(file_path)
    
    # Rename columns to full, descriptive names
    column_name_mapping = {
        # Basic Planet Information
        'pl_name': 'planet_name',
        'hostname': 'host_star_name',
        'disc_year': 'discovery_year',
        'discoverymethod': 'discovery_method',
        
        # Planetary System Information
        'sy_snum': 'number_of_stars_in_system',
        'sy_pnum': 'number_of_planets_in_system',
        'sy_mnum': 'number_of_moons_in_system',
        
        # Habitability & Earth Comparison Factors
        'pl_rade': 'planet_radius_earth_radii',
        'pl_masse': 'planet_mass_earth_masses',
        'pl_orbper': 'orbital_period_days',
        'pl_orbsmax': 'orbit_semi_major_axis_au',
        'pl_eqt': 'equilibrium_temperature',
        'pl_insol': 'insolation_flux_compared_to_earth',
        
        # Physical Characteristics
        'pl_dens': 'planet_density',
        'pl_orbeccen': 'orbital_eccentricity',
        'pl_bmasse': 'planet_mass_best_measurement',
        
        # Star Information
        'st_spectype': 'star_spectral_type',
        'st_teff': 'star_temperature_kelvin',
        'st_rad': 'star_radius_solar_radii',
        'st_mass': 'star_mass_solar_masses',
        'st_age': 'star_age_billion_years',
        
        # Location Information
        'ra': 'right_ascension',
        'dec': 'declination',
        'sy_dist': 'distance_from_earth_parsecs'
    }
    df = df.assign(**{ new_name: df[old_name] 
                   for old_name, new_name in column_name_mapping.items() })
    
    # Standardized missing value handling
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
    
    # Replace infinite values with NaN
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    
    # Intelligent imputation strategy
    for col in numeric_columns:
        # If less than 10% missing, use median
        # If more than 10% missing, use 0 or a domain-specific default
        missing_percentage = df[col].isna().mean() * 100
        
        if missing_percentage < 10:
            df[col].fillna(df[col].median(), inplace=True)
        else:
            # Domain-specific default values or 0
            default_values = {
                'star_age_billion_years': 0,
                'orbital_eccentricity': 0,
                'planet_density': 0,
                'star_temperature_kelvin': df['star_temperature_kelvin'].median()
            }
            df[col].fillna(default_values.get(col, 0), inplace=True)
    
    # Categorical column handling
    categorical_cols = df.select_dtypes(include=['object']).columns

    df[categorical_cols] = df[categorical_cols].fillna('Unknown')

    # get the float64 columns
    numeric_columns = df.select_dtypes(include=['float64']).columns

    # round them to 2 decimals in-place
    df[numeric_columns] = df[numeric_columns].round(2)
    
    # Advanced feature engineering
    def safe_log_transform(series, epsilon=1e-10):
        """
        Safe logarithmic transformation that handles zero and negative values
        """
        shifted_series = series + abs(series.min()) + epsilon
        return np.log(shifted_series)
    
    # Derived features for scientific analysis
    df['planet_habitability_score'] = (
        1 / (1 + 
             np.abs(np.log10(df['planet_radius_earth_radii'] + 1e-10)) + 
             np.abs(np.log10(df['planet_mass_earth_masses'] + 1e-10)) + 
             np.abs(df['equilibrium_temperature'] - 288) / 288)
    ).round(4)
    
    # Star classification based on temperature
    def classify_star_type(temp):
        if temp > 30000: return 'O-type (Blue)'
        elif temp > 10000: return 'B-type (Blue-White)'
        elif temp > 7500: return 'A-type (White)'
        elif temp > 6000: return 'F-type (Yellow-White)'
        elif temp > 5200: return 'G-type (Yellow)'
        elif temp > 3700: return 'K-type (Orange)'
        else: return 'M-type (Red)'
    
    df['star_type_classification'] = df['star_temperature_kelvin'].apply(classify_star_type)
    
    # Outlier detection and handling using IQR method
    def remove_outliers_iqr(df, columns, factor=1.5):
        df_clean = df.copy()
        for col in columns:
            Q1 = df_clean[col].quantile(0.25)
            Q3 = df_clean[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - factor * IQR
            upper_bound = Q3 + factor * IQR
            df_clean = df_clean[(df_clean[col] >= lower_bound) & (df_clean[col] <= upper_bound)]
        return df_clean
    
    # Remove extreme outliers from key numeric columns
    outlier_columns = [
        'planet_radius_earth_radii', 'planet_mass_earth_masses', 
        'orbital_period_days', 'star_temperature_kelvin',
        'star_mass_solar_masses', 'distance_from_earth_parsecs'
    ]
    df = remove_outliers_iqr(df, outlier_columns)
    
    # Additional derived features
    df['planet_to_star_mass_ratio'] = (df['planet_mass_best_measurement'] / (df['star_mass_solar_masses'] * 333000)).round(6)
    df['star_energy_output'] = (df['star_mass_solar_masses'] * (df['star_temperature_kelvin'] ** 4)).round(2)
    
    # Logarithmic transformations for distribution normalization
    log_columns = [
        'log_planet_radius', 'log_planet_mass', 
        'log_star_mass', 'log_star_temperature'
    ]
    df['log_planet_radius'] = safe_log_transform(df['planet_radius_earth_radii'])
    df['log_planet_mass'] = safe_log_transform(df['planet_mass_earth_masses'])
    df['log_star_mass'] = safe_log_transform(df['star_mass_solar_masses'])
    df['log_star_temperature'] = safe_log_transform(df['star_temperature_kelvin'])
    
    return df

# Example usage
# exoplanet_data = comprehensive_exoplanet_preprocessing('path/to/exoplanets_full_features.csv')
# print(exoplanet_data.info())

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
            data = comprehensive_exoplanet_preprocessing(path)
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

    # Add some derived columns for analysis
    data['earth_similarity'] = 1 / (1 + 
                                   np.abs(np.log10(data['pl_rade'])) + 
                                   np.abs(np.log10(data['pl_masse'] + 0.001)) +
                                   np.abs(data['pl_eqt'] - 288) / 288)
    
    return data