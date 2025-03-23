import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, r2_score
from config import MAX_GAMES_LOOKBACK


def train_minutes_regression(df_logs: pd.DataFrame) -> (pd.DataFrame, pd.DataFrame):
    """
    Trains an XGBoost regression model for each player to predict minutes.
    Adds REG_PRED_MIN column to df_logs with predicted values.
    """
    df_logs = df_logs.copy()
    if "GAME_DATE" not in df_logs.columns or df_logs["GAME_DATE"].isna().all():
        print("GAME_DATE missing or invalid; skipping regression.")
        df_logs["REG_PRED_MIN"] = df_logs["MIN"].mean()
        return df_logs, pd.DataFrame()

    df_logs['GAME_DATE'] = pd.to_datetime(df_logs['GAME_DATE'], errors='coerce')
    df_logs.sort_values(by="GAME_DATE", inplace=True)
    df_logs["GAME_INDEX"] = df_logs.groupby("PLAYER_NAME").cumcount()

    df_logs['LAST_5_MIN'] = df_logs.groupby("PLAYER_NAME")["MIN"].rolling(5, min_periods=1).mean().reset_index(0, drop=True)
    df_logs['LAST_10_MIN'] = df_logs.groupby("PLAYER_NAME")["MIN"].rolling(10, min_periods=1).mean().reset_index(0, drop=True)
    df_logs['EWMA_MIN'] = df_logs.groupby("PLAYER_NAME")["MIN"].transform(lambda x: x.ewm(span=5).mean())
    df_logs['REST_DAYS'] = df_logs.groupby("PLAYER_NAME")["GAME_DATE"].diff().dt.days.fillna(2)

    feature_cols = ["GAME_INDEX", "LAST_5_MIN", "LAST_10_MIN", "EWMA_MIN", "REST_DAYS"]

    results = []
    pred_map = {}

    for pname, group in df_logs.groupby("PLAYER_NAME"):
        group = group.tail(MAX_GAMES_LOOKBACK)
        if len(group) < 3:
            fallback = group["MIN"].mean()
            pred_map[pname] = fallback
            results.append({"PLAYER_NAME": pname, "TrainSize": 0, "TestSize": 0, "MSE": None, "R2": None, "Predicted_MIN": fallback})
            continue

        X = group[feature_cols].values
        y = group["MIN"].values
        cutoff = int(0.8 * len(group))
        X_train, y_train = X[:cutoff], y[:cutoff]
        X_test, y_test = X[cutoff:], y[cutoff:]

        try:
            model = XGBRegressor(n_estimators=50, max_depth=3, random_state=42)
            model.fit(X_train, y_train)

            pred_min = model.predict([group[feature_cols].iloc[-1]])[0]
            mse = mean_squared_error(y_test, model.predict(X_test)) if len(X_test) > 0 else None
            r2 = r2_score(y_test, model.predict(X_test)) if len(X_test) > 0 else None
            pred_min = float(np.clip(pred_min, 0, 48))
            pred_map[pname] = pred_min

            results.append({
                "PLAYER_NAME": pname,
                "TrainSize": len(X_train),
                "TestSize": len(X_test),
                "MSE": mse,
                "R2": r2,
                "Predicted_MIN": pred_min
            })

        except Exception as e:
            print(f"Regression failed for {pname}: {e}")
            fallback = group["MIN"].mean()
            pred_map[pname] = fallback
            results.append({"PLAYER_NAME": pname, "TrainSize": 0, "TestSize": 0, "MSE": None, "R2": None, "Predicted_MIN": fallback})

    df_logs["REG_PRED_MIN"] = df_logs["PLAYER_NAME"].map(pred_map)
    results_df = pd.DataFrame(results)
    return df_logs, results_df
