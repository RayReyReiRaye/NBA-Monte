import pandas as pd
from nba_api.stats.endpoints import (
    commonteamroster, playergamelog, teamgamelog,
    leaguedashteamstats, leaguedashplayerstats
)
from nba_api.stats.static import teams
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from utils import normalize_player_name, apply_api_delay
from config import TEAM_ABBR_MAP

# Global caches
roster_cache = {}
gamelog_cache = {}

def get_team_id(abbreviation):
    teams_list = teams.get_teams()
    team = next((t for t in teams_list if t['abbreviation'].upper() == abbreviation.upper()), None)
    return team['id'] if team else None

def fetch_team_roster(team_id, season='2024-25', retries=3):
    if not team_id:
        return pd.DataFrame()
    if team_id in roster_cache:
        return roster_cache[team_id]
    for _ in range(retries):
        try:
            roster = commonteamroster.CommonTeamRoster(team_id=team_id, season=season)
            df = roster.get_data_frames()[0]
            if not df.empty:
                roster_cache[team_id] = df
                apply_api_delay()
                return df
        except Exception:
            apply_api_delay()
    return pd.DataFrame()

def fetch_player_stats(player_id, player_name, season='2024-25'):
    try:
        stats = playergamelog.PlayerGameLog(player_id=player_id, season=season)
        df = stats.get_data_frames()[0]
        df['PLAYER_NAME'] = player_name
        apply_api_delay()
        return df
    except Exception:
        apply_api_delay()
        return pd.DataFrame()

def fetch_team_gamelogs(team_id, season='2024-25'):
    if not team_id:
        return pd.DataFrame()
    if team_id in gamelog_cache:
        return gamelog_cache[team_id]
    try:
        gamelog = teamgamelog.TeamGameLog(team_id=team_id, season=season)
        df = gamelog.get_data_frames()[0]
        gamelog_cache[team_id] = df
        apply_api_delay()
        return df
    except Exception:
        apply_api_delay()
        return pd.DataFrame()

def fetch_injury_report():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://www.espn.com/nba/injuries")

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "Table")))
    except Exception:
        driver.quit()
        return pd.DataFrame()
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    data = []
    for section in soup.select('.Table__Scroller'):
        team_name = section.find_previous('h2').text.strip()
        rows = section.select('tbody tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 4:
                player = cols[0].text.strip()
                est_return = cols[2].text.strip()
                status = cols[3].text.strip()
                data.append([team_name, player, status, est_return])

    df = pd.DataFrame(data, columns=["Team", "Athlete Name", "Status", "Est. Return Date"])
    df["Athlete Name"] = df["Athlete Name"].apply(normalize_player_name)
    return df

def scrape_fantasydatanba_lineups():
    url = "https://fantasydata.com/nba/starting-lineups"
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "lineups")))
    except Exception:
        driver.quit()
        return pd.DataFrame()

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    lineup_data = []
    games = soup.select("#lineups .game")
    for game in games:
        logos = game.select(".header img.logo")
        if len(logos) < 2:
            continue
        away_team = logos[0]["src"].split("/")[-1].split(".")[0]
        home_team = logos[1]["src"].split("/")[-1].split(".")[0]
        away_team = TEAM_ABBR_MAP.get(away_team, away_team)
        home_team = TEAM_ABBR_MAP.get(home_team, home_team)

        for side, team in zip(["away", "home"], [away_team, home_team]):
            section = game.select_one(f".lineup .{side}")
            if not section:
                continue
            mode = None
            for entry in section.select(".text-nowrap"):
                if entry.find("strong"):
                    header = entry.find("strong").text.strip()
                    if header == "Starters":
                        mode = "starter"
                    elif header == "Injuries":
                        mode = "injury"
                    continue
                player_tag = entry.find("a")
                if player_tag:
                    player_name = normalize_player_name(player_tag.text.strip())
                    status = "Available" if mode == "starter" else "Unavailable"
                    lineup_data.append({
                        "PLAYER_NAME": player_name,
                        "TEAM": team,
                        "Probable_Starter": mode == "starter",
                        "FD_Status": status
                    })
    return pd.DataFrame(lineup_data)
