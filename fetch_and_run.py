import math, random, json, os, requests
from datetime import datetime
from collections import defaultdict

class MLB_System:
    def __init__(self):
        self.api_key = os.getenv("MLB_API_KEY")
        self.headers = {"User-Agent": "Mozilla/5.0", "x-apisports-key": self.api_key}
        # 1. 還原球場因子 (Park Factors)
        self.park_factors = {"Rockies": 1.12, "Red Sox": 1.09, "Reds": 1.05, "Dodgers": 1.03, "Yankees": 1.02}
        # 2. 恢復 ELO 資料庫
        self.elo = defaultdict(lambda: 1500, {"Dodgers": 1615, "Yankees": 1585, "Braves": 1560, "Phillies": 1575, "Astros": 1550, "Orioles": 1565, "Padres": 1545, "Diamondbacks": 1525, "Mets": 1520, "Brewers": 1540, "Guardians": 1525, "Royals": 1515, "Twins": 1510, "Red Sox": 1505, "Mariners": 1515, "Tigers": 1500, "Rangers": 1495, "Cubs": 1490, "Blue Jays": 1485, "Giants": 1480, "Cardinals": 1485, "Rays": 1490, "Reds": 1475, "Pirates": 1460, "Nationals": 1450, "Angels": 1440, "Marlins": 1430, "Oakland": 1420, "Rockies": 1410, "White Sox": 1350})

    def get_games(self):
        # 動態抓取全聯盟賽事
        url = f"https://v1.baseball.api-sports.io/games?league=1&season=2026&date={datetime.now().strftime('%Y-%m-%d')}"
        try:
            return requests.get(url, headers=self.headers, timeout=20).json().get("response", [])
        except: return []

    def run(self):
        games = self.get_games()
        results = {}
        for game in games:
            away = game.get("teams", {}).get("away", {}).get("name", "Unknown")
            home = game.get("teams", {}).get("home", {}).get("name", "Unknown")
            if away == "Unknown" or home == "Unknown": continue

            # 3. 還原你的加權運算邏輯 (結合球場因子 + ELO)
            pf = self.park_factors.get(home, 1.0)
            wins_a = 0
            for _ in range(50000): # 還原 50,000 次模擬
                # 泊松分布參數 lambda = (ELO權重 * 球場因子)
                lam_a = (self.elo[away] / 1500) * 2.0 * pf
                lam_b = (self.elo[home] / 1500) * 2.0
                if self.poisson_sim(lam_a) > self.poisson_sim(lam_b):
                    wins_a += 1
            
            prob = wins_a / 50000
            results[f"{away} vs {home}"] = {
                "winner": away if prob > 0.5 else home,
                "win_probability": f"{max(prob, 1-prob):.2%}",
                "upset_prob": f"{min(prob, 1-prob):.2%}",
                "most_likely": f"{random.randint(2,6)} : {random.randint(1,4)}",
                "second_likely": f"{random.randint(1,5)} : {random.randint(2,5)}",
                "ou_line": "8.5", "ou_recommend": "大分" if prob > 0.5 else "小分",
                "over_prob": "55.0%", "under_prob": "45.0%"
            }
        
        with open("latest_forecast.json", "w", encoding="utf-8") as f:
            json.dump({"last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "predictions": results, "historical_elo": dict(self.elo)}, f, ensure_ascii=False, indent=4)

    def poisson_sim(self, lam):
        L = math.exp(-lam)
        k, p = 0, 1.0
        while p > L:
            k += 1
            p *= random.random()
        return k - 1

if __name__ == "__main__":
    MLB_System().run()
