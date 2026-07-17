import math, random, json
from datetime import datetime
from collections import defaultdict

class MLB_System:
    def __init__(self):
        # 隊伍名稱已全數中文化
        self.elo = defaultdict(lambda: 1500, {
            "道奇": 1615, "洋基": 1585, "勇士": 1560, "費城人": 1575, "太空人": 1550, 
            "金鶯": 1565, "教士": 1545, "響尾蛇": 1525, "大都會": 1520, "釀酒人": 1540, 
            "守護者": 1525, "皇家": 1515, "雙城": 1510, "紅襪": 1505, "水手": 1515, 
            "老虎": 1500, "遊騎兵": 1495, "小熊": 1490, "藍鳥": 1485, "巨人": 1480, 
            "紅雀": 1485, "光芒": 1490, "紅人": 1475, "海盜": 1460, "國民": 1450, 
            "天使": 1440, "馬林魚": 1430, "運動家": 1420, "洛磯": 1410, "白襪": 1350
        })
        self.park_factors = {"洛磯": 1.12, "紅襪": 1.09, "紅人": 1.05, "道奇": 1.03, "洋基": 1.02}

    def get_matchups(self):
        # 手動設定今日賽程（中文）
        return [
            {"away": "洋基", "home": "道奇", "away_split": 1.05, "home_split": 0.95},
            {"away": "勇士", "home": "費城人", "away_split": 1.0, "home_split": 1.0}
        ]

    def poisson_sim(self, lam):
        L = math.exp(-lam)
        k, p = 0, 1.0
        while p > L:
            k += 1
            p *= random.random()
        return k - 1

    def run(self):
        matchups = self.get_matchups()
        results = {}
        for m in matchups:
            a_factor = self.park_factors.get(m['away'], 1.0) * m['away_split']
            h_factor = self.park_factors.get(m['home'], 1.0) * m['home_split']
            
            wins_a = 0
            for _ in range(50000):
                lam_a = (self.elo[m['away']] / 1500) * 2.2 * a_factor
                lam_b = (self.elo[m['home']] / 1500) * 2.2 * h_factor
                if self.poisson_sim(lam_a) > self.poisson_sim(lam_b):
                    wins_a += 1
            
            prob = wins_a / 50000
            # 輸出格式同步中文化
            results[f"{m['away']} 對 {m['home']}"] = {
                "winner": m['away'] if prob > 0.5 else m['home'],
                "win_probability": f"{max(prob, 1-prob):.2%}",
                "upset_prob": f"{min(prob, 1-prob):.2%}",
                "most_likely": f"{random.randint(2,6)} : {random.randint(1,4)}",
                "ou_line": "8.5", 
                "ou_recommend": "大分" if prob > 0.5 else "小分"
            }
        
        with open("latest_forecast.json", "w", encoding="utf-8") as f:
            json.dump({"last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "predictions": results}, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    MLB_System().run()
