import math
import random
import json
import os
import requests
from datetime import datetime, timedelta
from collections import defaultdict, Counter

class MLBDataFetcher:
    def __init__(self):
        # 從環境變數安全讀取 API Key
        self.api_key = os.getenv("MLB_API_KEY")
        self.headers = {"User-Agent": "Mozilla/5.0", "x-apisports-key": self.api_key}
        self.park_factors = {"Rockies": 112, "Red Sox": 109, "Reds": 105, "Dodgers": 103, "Yankees": 102, "Braves": 101, "Astros": 101, "Phillies": 102, "Orioles": 98, "Padres": 96, "Guardians": 99, "Brewers": 100, "Mariners": 95, "Twins": 99, "Tigers": 97, "Mets": 96, "Royals": 98, "Diamondbacks": 99, "Cubs": 101, "Cardinals": 98, "Rays": 97, "Rangers": 100, "Giants": 95, "Pirates": 99, "Blue Jays": 100, "Angels": 101, "Nationals": 99, "Marlins": 96, "Athletics": 97, "White Sox": 101}
        self.name_map = {"New York Yankees": "Yankees", "Los Angeles Dodgers": "Dodgers", "Atlanta Braves": "Braves", "Philadelphia Phillies": "Phillies", "Houston Astros": "Astros", "Baltimore Orioles": "Orioles", "Tampa Bay Rays": "Rays", "Toronto Blue Jays": "Blue Jays", "Boston Red Sox": "Red Sox", "Cleveland Guardians": "Guardians", "Minnesota Twins": "Twins", "Detroit Tigers": "Tigers", "Seattle Mariners": "Mariners", "Texas Rangers": "Rangers", "Los Angeles Angels": "Angels", "Oakland Athletics": "Athletics", "New York Mets": "Mets", "Milwaukee Brewers": "Brewers", "Chicago Cubs": "Cubs", "Cincinnati Reds": "Reds", "Pittsburgh Pirates": "Pirates", "St. Louis Cardinals": "Cardinals", "Miami Marlins": "Marlins", "Washington Nationals": "Nationals", "San Francisco Giants": "Giants", "San Diego Padres": "Padres", "Arizona Diamondbacks": "Diamondbacks", "Colorado Rockies": "Rockies", "Chicago White Sox": "White Sox", "Kansas City Royals": "Royals"}

    def fetch_api_data(self, date_str):
        url = f"https://v1.baseball.api-sports.io/games?league=1&season=2026&date={date_str}"
        try:
            res = requests.get(url, headers=self.headers, timeout=10)
            return res.json().get("response", []) if res.status_code == 200 else []
        except: return []

class AdvancedEloRating:
    def __init__(self):
        self.ratings = defaultdict(lambda: 1500, {"Dodgers": 1615, "Yankees": 1585, "Braves": 1560, "Phillies": 1575, "Astros": 1550, "Orioles": 1565, "Padres": 1545, "Diamondbacks": 1525, "Mets": 1520, "Brewers": 1540, "Guardians": 1525, "Royals": 1515, "Twins": 1510, "Red Sox": 1505, "Mariners": 1515, "Tigers": 1500, "Rangers": 1495, "Cubs": 1490, "Blue Jays": 1485, "Giants": 1480, "Cardinals": 1485, "Rays": 1490, "Reds": 1475, "Pirates": 1460, "Nationals": 1450, "Angels": 1440, "Marlins": 1430, "Oakland": 1420, "Rockies": 1410, "White Sox": 1350})

class PoissonPredictor:
    def simulate_game(self, team_a, team_b, elo, factors):
        # 你的 50,000 次模擬核心
        score_a, score_b = 0, 0
        for _ in range(9):
            score_a += sum(random.random() < 0.2 for _ in range(3))
            score_b += sum(random.random() < 0.2 for _ in range(3))
        return score_a, score_b

if __name__ == "__main__":
    fetcher = MLBDataFetcher()
    elo = AdvancedEloRating()
    poisson = PoissonPredictor()
    
    # 執行流程
    today = datetime.now().strftime("%Y-%m-%d")
    raw_games = fetcher.fetch_api_data(today)
    
    forecast_results = {} # 這裡填入你的解析結果
    
    output = {
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "force_refresh_token": str(random.randint(100000, 999999)),
        "predictions": forecast_results,
        "historical_elo": dict(elo.ratings)
    }
    
    with open("latest_forecast.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    print("DONE")
