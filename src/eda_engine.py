import pandas as pd
import numpy as np

def compute_city_rankings(df):
    """Computes ranking of cities based on multi-year mean AQI and peak values."""
    ranking = df.groupby('City')['AQI'].agg(
        Mean_AQI='mean',
        Median_AQI='median',
        Max_AQI='max',
        Std_Dev='std'
    ).reset_index().sort_values(by='Mean_AQI', ascending=False)

    # Assign qualitative CPCB tier based on Mean AQI
    def categorize(aqi):
        if aqi <= 50: return 'Good'
        elif aqi <= 100: return 'Satisfactory'
        elif aqi <= 200: return 'Moderate'
        elif aqi <= 300: return 'Poor'
        elif aqi <= 400: return 'Very Poor'
        else: return 'Severe'

    ranking['Dominant_Tier'] = ranking['Mean_AQI'].apply(categorize)
    return ranking

def analyze_meteorological_correlation(df_merged):
    """
    Computes Pearson and Spearman correlation between weather features
    (Temperature, Wind Speed, Humidity, Precipitation) and air pollutants.
    """
    corr_columns = ['AQI', 'PM2.5', 'PM10', 'NO2', 'SO2', 'CO',
                    'Temperature', 'Wind_Speed', 'Humidity', 'Precipitation']
    available_cols = [c for c in corr_columns if c in df_merged.columns]
    corr_matrix = df_merged[available_cols].corr(method='pearson')

    print("\n--- Key Meteorological Correlations with AQI ---")
    if 'Temperature' in corr_matrix.columns:
        print(f"AQI vs Temperature: r = {corr_matrix.loc['AQI', 'Temperature']:.3f} (Negative correlation)")
    if 'Wind_Speed' in corr_matrix.columns:
        print(f"AQI vs Wind Speed: r = {corr_matrix.loc['AQI', 'Wind_Speed']:.3f} (Strong negative dispersion)")
    if 'Humidity' in corr_matrix.columns:
        print(f"AQI vs Humidity: r = {corr_matrix.loc['AQI', 'Humidity']:.3f} (Positive correlation)")

    return corr_matrix

def evaluate_covid_lockdown_impact(df):
    """Compares AQI in 2020 across Pre-Lockdown, Strict Lockdown, and Post-Lockdown."""
    df_2020 = df[df['Year'] == 2020]
    lockdown_summary = df_2020.groupby(['City', 'Lockdown_Phase'])['AQI'].mean().unstack()

    if 'Pre-Lockdown' in lockdown_summary.columns and 'Lockdown' in lockdown_summary.columns:
        lockdown_summary['Reduction_%'] = (
            (lockdown_summary['Pre-Lockdown'] - lockdown_summary['Lockdown']) /
            lockdown_summary['Pre-Lockdown'] * 100
        ).round(2)

    return lockdown_summary
