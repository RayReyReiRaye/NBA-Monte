import pandas as pd
from config import STAT_COLUMNS


def compute_player_averages(df: pd.DataFrame) -> pd.DataFrame:
    """
    Groups by player and team, returns season averages for stat columns.
    """
    gp = df.groupby(['PLAYER_NAME', 'TEAM']).mean(numeric_only=True).reset_index()
    gp.rename(columns=lambda c: f"AVG_{c}" if c not in ['PLAYER_NAME', 'TEAM', 'Player_ID'] else c, inplace=True)
    return gp


def compute_recent_averages(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes last 5 and last 10 game averages for each stat and player.
    """
    df = df.sort_values(by=['PLAYER_NAME', 'GAME_DATE'], ascending=[True, False]).reset_index(drop=True)
    recs = []
    for (pname, team), group in df.groupby(['PLAYER_NAME', 'TEAM']):
        last5 = group.head(5)
        last10 = group.head(10)
        row = {'PLAYER_NAME': pname, 'TEAM': team}
        for sc in STAT_COLUMNS:
            row[f"AVG_{sc}_LAST_5"] = last5[sc].mean()
            row[f"AVG_{sc}_LAST_10"] = last10[sc].mean()
        recs.append(row)
    return pd.DataFrame(recs)


def merge_all_stats(base_df: pd.DataFrame, season_avg: pd.DataFrame, recent_avg: pd.DataFrame, reg_min: pd.DataFrame, lineup_roles: pd.DataFrame) -> pd.DataFrame:
    """
    Combines all stat tables into one simulation-ready DataFrame.
    """
    df = pd.merge(season_avg, recent_avg, on=['PLAYER_NAME', 'TEAM'], how='left')
    df = pd.merge(df, reg_min, on='PLAYER_NAME', how='left')
    df["AVG_MIN"] = df["REG_MIN"].fillna(df.get("AVG_MIN", 20))
    df = pd.merge(df, lineup_roles[['PLAYER_NAME', 'TEAM', 'Role']], on=['PLAYER_NAME', 'TEAM'], how='left')
    return df[df["AVG_MIN"] >= 8]
