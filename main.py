import pandas as pd
from data_fetch import (
    get_team_id, fetch_team_roster, fetch_player_stats,
    fetch_injury_report, scrape_fantasydatanba_lineups
)
from utils import parse_matchup
from regression import train_minutes_regression
from simulation import monte_carlo_player_projection
from data_processing import (
    compute_player_averages,
    compute_recent_averages,
    merge_all_stats
)


def run_simulation_for_matchup(matchup):
    away_team, home_team = parse_matchup(matchup)
    teams = [away_team, home_team]

    # Get lineup info (FantasyData starters + injury overrides)
    lineup_df = scrape_fantasydatanba_lineups()
    lineup_df = lineup_df[lineup_df['TEAM'].isin(teams)]

    # Get injuries and update status
    injuries = fetch_injury_report()
    if not injuries.empty:
        injuries = injuries[injuries['Team'].isin(teams)]
        injury_names = injuries['Athlete Name'].tolist()
        lineup_df = lineup_df[~lineup_df['PLAYER_NAME'].isin(injury_names)]

    # Add Player_ID and merge status
    for team in teams:
        tid = get_team_id(team)
        roster = fetch_team_roster(tid)
        if roster.empty:
            continue
        roster['Normalized'] = roster['PLAYER'].apply(str.lower)
        for idx in lineup_df[lineup_df['TEAM'] == team].index:
            name = lineup_df.at[idx, 'PLAYER_NAME'].lower()
            match = roster[roster['Normalized'].str.contains(name)]
            if not match.empty:
                lineup_df.at[idx, 'Player_ID'] = match.iloc[0]['PLAYER_ID']

    # Fetch player logs
    all_logs = []
    for _, row in lineup_df.iterrows():
        pid = row.get('Player_ID')
        pname = row['PLAYER_NAME']
        if not pd.isna(pid):
            logs = fetch_player_stats(pid, pname)
            if not logs.empty:
                logs['TEAM'] = row['TEAM']
                all_logs.append(logs)

    logs_df = pd.concat(all_logs, ignore_index=True)
    if logs_df.empty:
        print("No player logs fetched. Exiting.")
        return

    logs_df, reg_results = train_minutes_regression(logs_df)
    reg_min = logs_df.groupby("PLAYER_NAME")["REG_PRED_MIN"].mean().reset_index().rename(columns={"REG_PRED_MIN": "REG_MIN"})

    # Prepare simulation input
    season_avg = compute_player_averages(logs_df)
    recent_avg = compute_recent_averages(logs_df)
    sim_input = merge_all_stats(logs_df, season_avg, recent_avg, reg_min, lineup_df)

    # Run simulation
    results = monte_carlo_player_projection(sim_input)
    print("\n=== Simulated Player Projections ===")
    print(results.round(3).to_string(index=False))


if __name__ == "__main__":
    matchup = input("Enter NBA matchup (e.g. PHX @ DET): ").strip()
    run_simulation_for_matchup(matchup)
