import time
import re
from unidecode import unidecode
from thefuzz import process, fuzz
from config import CUSTOM_PLAYER_MAP, API_DELAY

# Simple name normalization to help with fuzzy matching
def normalize_player_name(name: str) -> str:
    name = unidecode(name).strip().lower()
    for suffix in [" iii", " jr.", " sr."]:
        if name.endswith(suffix):
            name = name.replace(suffix, "")
    return CUSTOM_PLAYER_MAP.get(name.title(), name.title())

# Fuzzy match for name discrepancies between data sources
def fuzzy_match_name(user_input: str, valid_names: list, threshold=85) -> str:
    user_input_norm = normalize_player_name(user_input)
    valid_names_norm = [normalize_player_name(v) for v in valid_names]
    norm_to_original = dict(zip(valid_names_norm, valid_names))
    result = process.extractOne(user_input_norm, valid_names_norm, scorer=fuzz.token_sort_ratio)
    if result:
        match, score = result
        if score >= threshold:
            return norm_to_original[match]
    return user_input

# Delay for rate-limiting API calls
def apply_api_delay():
    time.sleep(API_DELAY)

# Splits a matchup string into away/home teams
def parse_matchup(matchup: str):
    if "@" in matchup:
        return [t.strip() for t in matchup.split("@")]  # away @ home
    elif "vs" in matchup:
        return [t.strip() for t in matchup.split("vs")]  # home vs away
    return None, None
