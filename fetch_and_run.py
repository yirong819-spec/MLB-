import math, random, json
from datetime import datetime
from collections import defaultdict

class MLB_Advanced_System:
    def __init__(self):
        # 完整 30 隊資料庫：包含左投/右投對抗 ERA、打擊率與戰術傾向
        self.team_db = {
            "道奇": {"L_ERA": 3.1, "R_ERA": 3.3, "AVG": 0.265, "戰術": 0.9},
            "洋基": {"L_ERA": 3.3, "R_ERA": 3.5, "AVG": 0.260, "戰術": 0.85},
            "勇士": {"L_ERA": 3.2, "R_ERA": 3.4, "AVG": 0.258, "戰術": 0.8},
            "費城人": {"L_ERA": 3.4, "R_ERA": 3.6, "AVG": 0.255, "戰術": 0.8},
            "太空人": {"L_ERA": 3.5, "R_ERA": 3.7, "AVG": 0.250, "戰術": 0.75},
            "金鶯": {"L_ERA": 3.4, "R_ERA": 3.6, "AVG": 0.250, "戰術": 0.8},
            "教士": {"L_ERA": 3.6, "R_ERA": 3.8, "AVG": 0.248, "戰術": 0.7},
            "響尾蛇": {"L_ERA": 3.7, "R_ERA": 3.9, "AVG": 0.245, "戰術": 0.75},
            "大都會": {"L_ERA": 3.8, "R_ERA": 4.0, "AVG": 0.240, "戰術": 0.65},
            "釀酒人": {"L_ERA": 3.5, "R_ERA": 3.7, "AVG": 0.242, "戰術": 0.7},
            "守護者": {"L_ERA": 3.6, "R_ERA": 3.8, "AVG": 0.240, "戰術": 0.75},
            "皇家": {"L_ERA": 3.7, "R_ERA": 3.9, "AVG": 0.238, "戰術": 0.6},
            "雙城": {"L_ERA": 3.8, "R_ERA": 4.0, "AVG": 0.235, "戰術": 0.65},
            "紅襪": {"L_ERA": 3.6, "R_ERA": 3.8, "AVG": 0.242, "戰術": 0.7},
            "水手": {"L_ERA": 3.4, "R_ERA": 3.6, "AVG": 0.230, "戰術": 0.7},
            "老虎": {"L_ERA": 3.9, "R_ERA": 4.1, "AVG": 0.232, "戰術": 0.6},
            "遊騎兵": {"L_ERA": 4.0, "R_ERA": 4.2, "AVG": 0.230, "戰術": 0.65},
            "小熊": {"L_ERA": 3.9, "R_ERA": 4.1, "AVG": 0.235, "戰術": 0.6},
            "藍鳥": {"L_ERA": 4.1, "R_ERA": 4.3, "AVG": 0.228, "戰術": 0.55},
            "巨人": {"L_ERA": 4.0, "R_ERA": 4.2, "AVG": 0.230, "戰術": 0.6},
            "紅雀": {"L_ERA": 3.9, "R_ERA": 4.1, "AVG": 0.232, "戰術": 0.65},
            "光芒": {"L_ERA": 3.8, "R_ERA": 4.0, "AVG": 0.230, "戰術": 0.7},
            "紅人": {"L_ERA": 4.2, "R_ERA": 4.4, "AVG": 0.225, "戰術": 0.55},
            "海盜": {"L_ERA": 4.1, "R_ERA": 4.3, "AVG": 0.228, "戰術": 0.5},
            "國民": {"L_ERA": 4.3, "R_ERA": 4.5, "AVG": 0.220, "戰術": 0.5},
            "天使": {"L_ERA": 4.4, "R_ERA": 4.6, "AVG": 0.218, "戰術": 0.5},
            "馬林魚": {"L_ERA": 4.2, "R_ERA": 4.4, "AVG": 0.220, "戰術": 0.5},
            "運動家": {"L_ERA": 4.5, "R_ERA": 4.7, "AVG": 0.215, "戰術": 0.4},
            "洛磯": {"L_ERA": 4.7, "R_ERA": 4.9, "AVG": 0.225, "戰術": 0.4},
            "白襪": {"L_ERA": 4.8, "R_ERA": 5.0, "AVG": 0.210, "戰術": 0.4}
        }
        self.elo = defaultdict(lambda: 1500, {k: 1500 for k in self.team_db.keys()})

    def poisson_sim(self, lam):
        L = math.exp(-lam)
        k, p = 0, 1.0
        while p > L:
            k += 1
            p *= random.random()
        return k - 1

    def run(self):
        # 此處為每日賽程輸入介面，若未來自動抓取成功，此清單將由爬蟲填入
        matchups = [
            {"away": "洋基", "home": "道奇", "a_p_hand": "R", "h_p_hand": "L", "market_prob": 0.52}
        ]
        results = {}
        for m in matchups:
            a_data = self.team_db.get(m['away'], {"L_ERA": 4.0, "R_ERA": 4.0, "AVG": 0.230, "戰術": 0.5})
            h_data = self.team_db.get(m['home'], {"L_ERA": 4.0, "R_ERA": 4.0, "AVG": 0.230, "戰術": 0.5})
            
            a_eff_era = a_data["L_ERA"] if m['a_p_hand'] == "L" else a_data["R_ERA"]
            h_eff_era = h_data["L_ERA"] if m['h_p_hand'] == "L" else h_data["R_ERA"]
            
            wins_a = 0
            # 嚴格執行 10 萬次蒙地卡羅模擬
            for _ in range(100000):
                lam_a = (self.elo[m['away']]/1500) * (a_data["AVG"]/h_eff_era*10) * a_data["戰術"]
                lam_b = (self.elo[m['home']]/1500) * (h_data["AVG"]/a_eff_era*10) * h_data["戰術"]
                
                # 結合市場賠率校準因子
                if self.poisson_sim(lam_a) * m['market_prob'] > self.poisson_sim(lam_b) * (1-m['market_prob']):
                    wins_a += 1
            
            prob = wins_a / 100000
            results[f"{m['away']} 對 {m['home']}"] = {
                "勝率": f"{prob:.2%}",
                "建議": "強攻" if a_data["戰術"] > 0.7 else "保守"
            }
        
        with open("latest_forecast.json", "w", encoding="utf-8") as f:
            json.dump({"last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "predictions": results}, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    MLB_Advanced_System().run()
