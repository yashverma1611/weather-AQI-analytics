import os
import pandas as pd
import numpy as np

def load_and_preprocess_aqi(file_path=None):
    """
    Loads raw CPCB daily air quality CSV, performs time-series parsing,
    imputes missing pollutant readings, and creates analytical features.
    """
    if file_path is None:
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'city_day.csv')

    print(f"[INFO] Ingesting dataset from: {file_path}")
    df = pd.read_csv(file_path, parse_dates=['Date'])

    # Select target major urban cities for comparative study
    target_cities = ['Delhi', 'Lucknow', 'Ahmedabad', 'Kolkata',
                     'Mumbai', 'Hyderabad', 'Bengaluru', 'Chennai']
    df = df[df['City'].isin(target_cities)].copy()

    # Sort chronologically by city and date
    df = df.sort_values(by=['City', 'Date']).reset_index(drop=True)

    # Core pollutant features
    pollutants = ['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3']

    # Step 1: Forward-fill localized gaps (<= 2 days) per city
    for city in target_cities:
        city_mask = df['City'] == city
        df.loc[city_mask, pollutants] = df.loc[city_mask, pollutants].ffill(limit=2).bfill(limit=1)

    # Step 2: Temporal feature extraction
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['DayOfWeek'] = df['Date'].dt.dayofweek

    # Step 3: Impute remaining NaN values using City-Month Grouped Median
    for pol in pollutants:
        if pol in df.columns:
            df[pol] = df.groupby(['City', 'Month'])[pol].transform(lambda x: x.fillna(x.median()))

    # Step 4: Map seasons according to Indian Meteorological Department (IMD)
    season_conditions = [
        df['Month'].isin([12, 1, 2]),
        df['Month'].isin([3, 4, 5]),
        df['Month'].isin([6, 7, 8, 9]),
        df['Month'].isin([10, 11])
    ]
    season_labels = ['Winter', 'Summer', 'Monsoon', 'Post-Monsoon']
    df['Season'] = np.select(season_conditions, season_labels, default='Other')

    # Step 5: Classify COVID-19 Lockdown Phases (Year 2020)
    lockdown_start = pd.to_datetime('2020-03-24')
    lockdown_end = pd.to_datetime('2020-05-31')

    df['Lockdown_Phase'] = 'Normal'
    df.loc[(df['Date'] >= lockdown_start) & (df['Date'] <= lockdown_end), 'Lockdown_Phase'] = 'Lockdown'
    df.loc[(df['Year'] == 2020) & (df['Date'] < lockdown_start), 'Lockdown_Phase'] = 'Pre-Lockdown'
    df.loc[(df['Year'] == 2020) & (df['Date'] > lockdown_end), 'Lockdown_Phase'] = 'Post-Lockdown'

    print(f"[SUCCESS] Preprocessed dataset: {df.shape[0]} rows, {df.shape[1]} columns.")
    return df

if __name__ == "__main__":
    from generate_dataset import generate_cpcb_dataset
    generate_cpcb_dataset()
    cleaned_df = load_and_preprocess_aqi()
    out_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'cleaned_aqi_data.csv')
    cleaned_df.to_csv(out_path, index=False)
    print(f"[SUCCESS] Exported cleaned dataset to: {out_path}")
