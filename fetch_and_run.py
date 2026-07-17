import math, random, json, requests
import numpy as np
from datetime import datetime
from collections import defaultdict
from bs4 import BeautifulSoup

class MLB_Advanced_System:
    def __init__(self):
        self.team_db = {
            "道奇": {"ERA": 3.1, "AVG": 0.265, "Tactical": 0.9, "Home_Adv": 1.05},
            "洋基": {"ERA": 3.3, "AVG": 0.260, "Tactical": 0.85, "Home_Adv": 1.02},
            "勇士": {"ERA": 3.2, "AVG": 0.258, "Tactical": 0.85, "Home_Adv": 1.03},
            "費城人": {"ERA": 3.4, "AVG": 0.255, "Tactical": 0.8, "Home_Adv": 1.02},
            "太空人": {"ERA": 3.5, "AVG": 0.250, "Tactical": 0.75, "Home_Adv": 1.01},
            "金鶯": {"ERA": 3.4, "AVG": 0.250, "Tactical": 0.8, "Home_Adv": 1.02},
            "教士": {"ERA": 3.6, "AVG": 0.248, "Tactical": 0.75, "Home_Adv": 1.01},
            "響尾蛇": {"ERA": 3.7, "AVG": 0.245, "Tactical": 0.75, "Home_Adv": 1.02},
            "大都會": {"ERA": 3.8, "AVG": 0.240, "Tactical": 0.7, "Home_Adv": 1.01},
            "釀酒人": {"ERA": 3.5, "AVG": 0.242, "Tactical": 0.75, "Home_Adv": 1.02},
            "守護者": {"ERA": 3.6, "AVG": 0.240, "Tactical": 0.75, "Home_Adv": 1.01},
            "皇家": {"ERA": 3.7, "AVG": 0.238, "Tactical": 0.7, "Home_Adv": 1.01},
            "雙城": {"ERA": 3.8, "AVG": 0.235, "Tactical": 0.7, "Home_Adv": 1.01},
            "紅襪": {"ERA": 3.6, "AVG": 0.242, "Tactical": 0.75, "Home_Adv": 1.02},
            "水手": {"ERA": 3.4, "AVG": 0.230, "Tactical": 0.7, "Home_Adv": 1.03},
            "老虎": {"ERA": 3.9, "AVG": 0.232, "Tactical": 0.65, "Home_Adv": 1.01},
            "遊騎兵": {"ERA": 4.0, "AVG": 0.230, "Tactical": 0.65, "Home_Adv": 1.01},
            "小熊": {"ERA": 3.9, "AVG": 0.235, "Tactical": 0.65, "Home_Adv": 1.01},
            "藍鳥": {"ERA": 4.1, "AVG": 0.228, "Tactical": 0.6, "Home_Adv": 1.01},
            "巨人": {"ERA": 4.0, "AVG": 0.230, "Tactical": 0.65, "Home_Adv": 1.02},
            "紅雀": {"ERA": 3.9, "AVG": 0.232, "Tactical": 0.65, "Home_Adv": 1.01},
            "光芒": {"ERA": 3.8, "AVG": 0.230, "Tactical": 0.7, "Home_Adv": 1.01},
            "紅人": {"ERA": 4.2, "AVG": 0.225, "Tactical": 0.6, "Home_Adv": 1.01},
            "海盜": {"ERA": 4.1, "AVG": 0.228, "Tactical": 0.6, "Home_Adv": 1.01},
            "國民": {"ERA": 4.3, "AVG": 0.220, "Tactical": 0.55, "Home_Adv": 1.0},
            "天使": {"ERA": 4.4, "AVG": 0.218, "Tactical": 0.55, "Home_Adv": 1.0},
            "馬林魚": {"ERA": 4.2, "AVG": 0.220, "Tactical": 0.55, "Home_Adv": 1.0},
            "運動家": {"ERA": 4.5, "AVG": 0.215, "Tactical": 0.5, "Home_Adv": 1.0},
            "洛磯": {"ERA": 4.7, "AVG": 0.225, "Tactical": 0.5, "Home_Adv": 1.05},
            "白襪": {"ERA": 4.8, "AVG": 0.210, "Tactical": 0.45, "Home_Adv": 1.0}
        }
        self.simulations = 100000

    def calculate_expectation(self, team_name, opponent_name):
        data = self.team_stats.get(team_name, {"ERA": 4.0, "AVG": 0.230, "Tactical": 0.5, "Home_Adv": 1.0})
        opp = self.team_stats.get(opponent_name, {"ERA": 4.0, "AVG": 0.230, "Tactical": 0.5, "Home_Adv": 1.0})
        base_lambda = (data["AVG"] / opp["ERA"]) * 10
        return max(base_lambda * data["Tactical"] * data["Home_Adv"], 0.1)

    def run(self):
        matchups = [{"away": "洋基", "home": "道奇"}, {"away": "勇士", "home": "費城人"}]
        results = {}
        for m in matchups:
            lam_a = self.calculate_expectation(m['away'], m['home'])
            lam_b = self.calculate_expectation(m['home'], m['away'])
            scores_a = np.random.poisson(lam_a, self.simulations)
            scores_b = np.random.poisson(lam_b, self.simulations)
            win_prob = np.mean(scores_a > scores_b)
            results[f"{m['away']} 對 {m['home']}"] = {
                "勝率": f"{max(win_prob, 1-win_prob):.2%}",
                "建議": "強攻" if self.team_stats[m['away']]["Tactical"] > 0.7 else "保守"
            }
        with open("latest_forecast.json", "w", encoding="utf-8") as f:
            json.dump({"last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "predictions": results}, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    MLB_Advanced_System().run()
