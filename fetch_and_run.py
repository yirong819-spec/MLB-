import math, random, json, os, requests, time
from datetime import datetime
from collections import defaultdict, Counter

class MLBDataFetcher:
    def __init__(self):
        self.api_key = os.getenv("MLB_API_KEY")
        with open('config.json', 'r', encoding='utf-8') as f:
            cfg = json.load(f)
            self.park_factors = cfg["park_factors"]
            self.name_map = cfg["name_map"]
            self.elo_data = cfg["historical_elo"]

    def call_api(self, url):
        for _ in range(3):
            try:
                res = requests.get(url, headers={"x-apisports-key": self.api_key}, timeout=10)
                if res.status_code == 200: return res.json()
            except: time.sleep(5)
        return None

class AdvancedEloRating:
    def __init__(self, elo_data):
        self.ratings = defaultdict(lambda: 1500, elo_data)

class PoissonPredictor:
    def __init__(self):
        self.league_avg_runs = 4.45
    
    def simulate_single_game(self, team_a, team_b, elo_model, factors):
        # 這裡放入你原本的蒙地卡羅 Poisson 核心邏輯
        return random.randint(0, 8), random.randint(0, 8)

if __name__ == "__main__":
    if not os.getenv("MLB_API_KEY"):
        print("Error: MLB_API_KEY not found"); exit(1)
        
    fetcher = MLBDataFetcher()
    elo = AdvancedEloRating(fetcher.elo_data)
    poisson = PoissonPredictor()
    
    # --- 這裡執行你原本的數據抓取與計算迴圈 ---
    # 計算完後的結果存入 forecast_results
    forecast_results = {} 
    
    output = {
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "force_refresh_token": f"{random.randint(100000, 999999)}",
        "predictions": forecast_results,
        "historical_elo": dict(elo.ratings)
    }
    
    with open("latest_forecast.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    print("DONE")
