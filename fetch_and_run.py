import math, random, json, requests
from datetime import datetime
from collections import defaultdict

class MLB_Advanced_System:
    def __init__(self):
        # 1. 全聯盟 30 隊資料庫 (整合左右投對抗 ERA)
        self.team_db = {
            "道奇": {"L_ERA": 3.1, "R_ERA": 3.3, "AVG": 0.265, "戰術": 0.9},
            "洋基": {"L_ERA": 3.3, "R_ERA": 3.5, "AVG": 0.260, "戰術": 0.85},
            "勇士": {"L_ERA": 3.2, "R_ERA": 3.4, "AVG": 0.258, "戰術": 0.8},
            # ... (需補齊全聯盟 30 隊數據)
            "白襪": {"L_ERA": 4.8, "R_ERA": 5.0, "AVG": 0.210, "戰術": 0.4}
        }
        self.elo = defaultdict(lambda: 1500, {k: 1500 for k in self.team_db.keys()})

    def get_live_data(self):
        """
        模擬獲取機制：
        這裡會串接賽事、先發投手與賠率數據。
        系統會回傳包含 {away, home, away_pitcher_hand, home_pitcher_hand, market_odds} 的清單。
        """
        return [
            {"away": "洋基", "home": "道奇", "a_p_hand": "R", "h_p_hand": "L", "market_prob": 0.52},
            {"away": "勇士", "home": "費城人", "a_p_hand": "L", "h_p_hand": "R", "market_prob": 0.48}
        ]

    def poisson_sim(self, lam):
        L = math.exp(-lam)
        k, p = 0, 1.0
        while p > L:
            k += 1
            p *= random.random()
        return k - 1

    def run(self):
        matchups = self.get_live_data()
        results = {}
        for m in matchups:
            a_data = self.team_db[m['away']]
            h_data = self.team_db[m['home']]
            
            # 先發投手對抗調整
            a_era = a_data["L_ERA"] if m['a_p_hand'] == "L" else a_data["R_ERA"]
            h_era = h_data["L_ERA"] if m['h_p_hand'] == "L" else h_data["R_ERA"]
            
            wins_a = 0
            # 100,000 次蒙地卡羅模擬
            for _ in range(100000):
                lam_a = (self.elo[m['away']]/1500) * (a_data["AVG"]/h_era*10) * a_data["戰術"]
                lam_b = (self.elo[m['home']]/1500) * (h_data["AVG"]/a_era*10) * h_data["戰術"]
                
                # 結合市場賠率校準 (Market Odds Adjustment)
                if self.poisson_sim(lam_a) * m['market_prob'] > self.poisson_sim(lam_b) * (1-m['market_prob']):
                    wins_a += 1
            
            prob = wins_a / 100000
            results[f"{m['away']} 對 {m['home']}"] = {
                "勝率": f"{prob:.2%}",
                "戰術建議": "強攻" if a_data["戰術"] > 0.7 else "保守"
            }
        
        with open("latest_forecast.json", "w", encoding="utf-8") as f:
            json.dump({"last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "predictions": results}, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    MLB_Advanced_System().run()
