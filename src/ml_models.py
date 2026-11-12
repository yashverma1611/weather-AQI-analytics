import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

def train_aqi_prediction_models(data_path=None):
    if data_path is None:
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'cleaned_aqi_data.csv')

    df = pd.read_csv(data_path).dropna(subset=['AQI'])

    # Define feature set: weather variables, temporal indices, and key pollutants
    feature_cols = ['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'Temperature',
                    'Wind_Speed', 'Humidity', 'Month', 'DayOfWeek']

    features = [f for f in feature_cols if f in df.columns]
    X = df[features]
    y = df['AQI']

    # 80-20 Train-Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Standardize numerical features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 1. Baseline Model: Multi-Linear Regression
    lr = LinearRegression()
    lr.fit(X_train_scaled, y_train)
    y_pred_lr = lr.predict(X_test_scaled)

    # 2. Advanced Ensemble Model: Random Forest Regressor
    rf = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
    rf.fit(X_train_scaled, y_train)
    y_pred_rf = rf.predict(X_test_scaled)

    def print_metrics(name, y_true, y_pred):
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        r2 = r2_score(y_true, y_pred)
        print(f"=== {name} Performance ===")
        print(f"Mean Absolute Error (MAE): {mae:.2f}")
        print(f"Root Mean Squared Error (RMSE): {rmse:.2f}")
        print(f"R-squared Score (R2): {r2:.4f}\n")
        return {"MAE": mae, "RMSE": rmse, "R2": r2}

    metrics_lr = print_metrics("Linear Regression", y_test, y_pred_lr)
    metrics_rf = print_metrics("Random Forest Regressor", y_test, y_pred_rf)

    # Save artifacts for Streamlit inference
    models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
    os.makedirs(models_dir, exist_ok=True)
    joblib.dump(rf, os.path.join(models_dir, "rf_aqi_model.pkl"))
    joblib.dump(scaler, os.path.join(models_dir, "scaler.pkl"))
    joblib.dump(features, os.path.join(models_dir, "features.pkl"))

    print(f"[SUCCESS] Model artifacts successfully serialized to {models_dir}")
    return rf, scaler

if __name__ == '__main__':
    train_aqi_prediction_models()
