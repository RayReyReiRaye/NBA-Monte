# Constants for controlling behavior
API_DELAY = 1.0
MIN_USAGE_THRESHOLD = 8
MAX_GAMES_LOOKBACK = 40

# Mappings for team abbreviation inconsistencies
TEAM_ABBR_MAP = {
    "NY": "NYK",
    "SA": "SAS",
    # Add more mappings if needed
}

# Custom manual name overrides
CUSTOM_PLAYER_MAP = {
    "Miles Mcbride": "Miles McBride"
    # Extend this map as needed for name mismatches
}

# Thresholds for prop simulation output
PROP_THRESHOLDS = {
    "PTS": [10, 15, 20],
    "REB": [6, 8, 10],
    "AST": [3, 5, 7],
    "FG3M": [1, 2, 3],
    "BLK": [1],
    "STL": [1]
}

# Columns used across the simulation
STAT_COLUMNS = [
    'MIN','FGM','FGA','FG_PCT','FG3M','FG3A','FG3_PCT','FTM','FTA','FT_PCT',
    'OREB','DREB','REB','AST','STL','BLK','TOV','PF','PTS','PLUS_MINUS'
]

