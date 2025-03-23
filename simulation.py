import pandas as pd
import numpy as np
from config import PROP_THRESHOLDS


def monte_carlo_player_projection(player_df: pd.DataFrame, num_simulations=1000) -> pd.DataFrame:
    """
    Runs Monte Carlo simulations for key stats using weighted historical averages.
    Returns a DataFrame with predicted means and hit probabilities.
    """
    results = []

    for _, row in player_df.iterrows():
        pname = row['PLAYER_NAME']
        team = row['TEAM']
        reg_min = row.get("REG_MIN", row.get("AVG_MIN", 30))
        role = row.get("Role", "Starter")

        base_min = reg_min if role == "Starter" else max(1.0, reg_min * 0.9)
        sim_mins = np.random.normal(base_min, 0.05 * base_min, num_simulations)
        sim_mins = np.clip(sim_mins, 0, 48)

        stat_results = {}
        for stat, thresholds in PROP_THRESHOLDS.items():
            season_avg = row.get(f"AVG_{stat}", 0)
            recent_avg = row.get(f"AVG_{stat}_LAST_5", season_avg)
            weighted_avg = 0.67 * recent_avg + 0.33 * season_avg

            usage_multiplier = 1 + row.get("USG_PCT", 20) / 100
            mean_val = weighted_avg * usage_multiplier
            sim_vals = np.random.poisson(mean_val, num_simulations)
            
            stat_results[f"AVG_SIM_{stat}"] = np.mean(sim_vals)
            for t in thresholds:
                stat_results[f"PROB_{stat}_GE_{t}"] = np.mean(sim_vals >= t)

        row_out = {
            "PLAYER_NAME": pname,
            "TEAM": team,
            "SIM_MIN": np.mean(sim_mins),
        }
        row_out.update(stat_results)
        results.append(row_out)

    return pd.DataFrame(results)
