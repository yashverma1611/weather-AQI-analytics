import os
import csv
import math
import random
from datetime import datetime, timedelta

def generate_cpcb_dataset():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)
    csv_path = os.path.join(data_dir, 'city_day.csv')

    cities = {
        'Delhi': {'base_pm25': 120, 'base_pm10': 210, 'base_no2': 45, 'base_so2': 18, 'base_co': 1.6, 'base_o3': 40, 'base_temp': 25, 'base_wind': 8, 'humidity': 55},
        'Lucknow': {'base_pm25': 105, 'base_pm10': 180, 'base_no2': 38, 'base_so2': 14, 'base_co': 1.4, 'base_o3': 35, 'base_temp': 26, 'base_wind': 7, 'humidity': 60},
        'Ahmedabad': {'base_pm25': 85, 'base_pm10': 150, 'base_no2': 48, 'base_so2': 28, 'base_co': 1.3, 'base_o3': 38, 'base_temp': 29, 'base_wind': 11, 'humidity': 48},
        'Kolkata': {'base_pm25': 68, 'base_pm10': 125, 'base_no2': 32, 'base_so2': 12, 'base_co': 1.1, 'base_o3': 28, 'base_temp': 27, 'base_wind': 9, 'humidity': 75},
        'Mumbai': {'base_pm25': 52, 'base_pm10': 98, 'base_no2': 28, 'base_so2': 15, 'base_co': 0.9, 'base_o3': 26, 'base_temp': 28, 'base_wind': 14, 'humidity': 78},
        'Hyderabad': {'base_pm25': 48, 'base_pm10': 92, 'base_no2': 24, 'base_so2': 9, 'base_co': 0.8, 'base_o3': 25, 'base_temp': 27, 'base_wind': 12, 'humidity': 62},
        'Bengaluru': {'base_pm25': 36, 'base_pm10': 70, 'base_no2': 20, 'base_so2': 7, 'base_co': 0.7, 'base_o3': 24, 'base_temp': 23, 'base_wind': 13, 'humidity': 65},
        'Chennai': {'base_pm25': 44, 'base_pm10': 82, 'base_no2': 22, 'base_so2': 10, 'base_co': 0.8, 'base_o3': 27, 'base_temp': 29, 'base_wind': 15, 'humidity': 76}
    }

    start_date = datetime(2015, 1, 1)
    end_date = datetime(2020, 12, 31)
    total_days = (end_date - start_date).days + 1

    headers = ['City', 'Date', 'PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3', 'Temperature', 'Wind_Speed', 'Humidity', 'Precipitation', 'AQI', 'AQI_Bucket']

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for city, profile in cities.items():
            curr_date = start_date
            while curr_date <= end_date:
                month = curr_date.month
                day_of_year = curr_date.timetuple().tm_yday

                # Seasonal modulation (Winter peak in Nov-Jan, Monsoon trough in Jul-Sep)
                if month in [11, 12, 1]:  # Winter
                    season_factor = 2.1
                    temp_mod = -7
                    wind_mod = -3
                    humidity_mod = 10
                    rain = 0.0
                elif month in [2, 3]:  # Spring
                    season_factor = 1.3
                    temp_mod = 0
                    wind_mod = 0
                    humidity_mod = -5
                    rain = 1.0 if random.random() < 0.1 else 0.0
                elif month in [4, 5, 6]:  # Summer
                    season_factor = 0.95
                    temp_mod = 8
                    wind_mod = 4
                    humidity_mod = -15
                    rain = 3.0 if random.random() < 0.2 else 0.0
                elif month in [7, 8, 9]:  # Monsoon
                    season_factor = 0.45
                    temp_mod = 2
                    wind_mod = 5
                    humidity_mod = 20
                    rain = random.uniform(8.0, 35.0) if random.random() < 0.6 else 0.0
                else:  # Post-monsoon (October)
                    season_factor = 1.5
                    temp_mod = 0
                    wind_mod = -1
                    humidity_mod = 0
                    rain = 0.0

                # COVID Lockdown shock (24 March 2020 to 31 May 2020)
                is_lockdown = (curr_date >= datetime(2020, 3, 24) and curr_date <= datetime(2020, 5, 31))
                lockdown_factor = 0.42 if is_lockdown else 1.0

                # Noise & variation
                noise = random.uniform(0.85, 1.18)

                pm25 = max(5.0, profile['base_pm25'] * season_factor * lockdown_factor * noise)
                pm10 = max(10.0, profile['base_pm10'] * season_factor * lockdown_factor * noise)
                no2 = max(2.0, profile['base_no2'] * (0.4 if is_lockdown else season_factor * 0.9) * noise)
                so2 = max(1.0, profile['base_so2'] * noise)
                co = max(0.1, profile['base_co'] * (0.5 if is_lockdown else 1.0) * noise)
                o3 = max(5.0, profile['base_o3'] * noise)

                temp = profile['base_temp'] + temp_mod + random.uniform(-2, 2)
                wind = max(1.0, profile['base_wind'] + wind_mod + random.uniform(-1.5, 1.5))
                humidity = min(100.0, max(20.0, profile['humidity'] + humidity_mod + random.uniform(-5, 5)))

                # Calculate composite CPCB AQI approx
                # Based on PM2.5 breakpoint dominance
                if pm25 <= 30:
                    aqi = pm25 * (50 / 30)
                elif pm25 <= 60:
                    aqi = 50 + (pm25 - 30) * (50 / 30)
                elif pm25 <= 90:
                    aqi = 100 + (pm25 - 60) * (100 / 30)
                elif pm25 <= 120:
                    aqi = 200 + (pm25 - 90) * (100 / 30)
                elif pm25 <= 250:
                    aqi = 300 + (pm25 - 120) * (100 / 130)
                else:
                    aqi = 400 + (pm25 - 250) * (100 / 150)

                aqi = min(500.0, round(aqi, 1))

                # Categorize
                if aqi <= 50: bucket = 'Good'
                elif aqi <= 100: bucket = 'Satisfactory'
                elif aqi <= 200: bucket = 'Moderate'
                elif aqi <= 300: bucket = 'Poor'
                elif aqi <= 400: bucket = 'Very Poor'
                else: bucket = 'Severe'

                writer.writerow([
                    city,
                    curr_date.strftime('%Y-%m-%d'),
                    round(pm25, 2),
                    round(pm10, 2),
                    round(no2, 2),
                    round(so2, 2),
                    round(co, 2),
                    round(o3, 2),
                    round(temp, 1),
                    round(wind, 1),
                    round(humidity, 1),
                    round(rain, 1),
                    aqi,
                    bucket
                ])

                curr_date += timedelta(days=1)

    print(f"[SUCCESS] Generated complete 2015-2020 CPCB Air Quality & Weather Dataset: {csv_path}")

if __name__ == '__main__':
    generate_cpcb_dataset()
