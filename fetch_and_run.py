import json, requests, math
import numpy as np
from datetime import datetime
from bs4 import BeautifulSoup

class MLB_SuperAnalyzer:
    def __init__(self):
        # 30 支隊伍完整數據庫 (包含戰術風格)
        self.team_stats = {
            "道奇": {"ERA": 3.1, "AVG": 0.265, "Style": "Power"},
            "洋基": {"ERA": 3.3, "AVG": 0.260, "Style": "Power"},
            "勇士": {"ERA": 3.2, "AVG": 0.258, "Style": "SmallBall"},
            "費城人": {"ERA": 3.4, "AVG": 0.255, "Style": "Defensive"},
            "太空人": {"ERA": 3.5, "AVG": 0.250, "Style": "Power"},
            "金鶯": {"ERA": 3.4, "AVG": 0.250, "Style": "SmallBall"},
            "教士": {"ERA": 3.6, "AVG": 0.248, "Style": "SmallBall"},
            "響尾蛇": {"ERA": 3.7, "AVG": 0.245, "Style": "SmallBall"},
            "大都會": {"ERA": 3.8, "AVG": 0.240, "Style": "Power"},
            "釀酒人": {"ERA": 3.5, "AVG": 0.242, "Style": "Defensive"},
            "守護者": {"ERA": 3.6, "AVG": 0.240, "Style": "Defensive"},
            "皇家": {"ERA": 3.7, "AVG": 0.238, "Style": "Power"},
            "雙城": {"ERA": 3.8, "AVG": 0.235, "Style": "Power"},
            "紅襪": {"ERA": 3.6, "AVG": 0.242, "Style": "Power"},
            "水手": {"ERA": 3.4, "AVG": 0.230, "Style": "Defensive"},
            "老虎": {"ERA": 3.9, "AVG": 0.232, "Style": "SmallBall"},
            "遊騎兵": {"ERA": 4.0, "AVG": 0.230, "Style": "Power"},
            "小熊": {"ERA": 3.9, "AVG": 0.235, "Style": "SmallBall"},
            "藍鳥": {"ERA": 4.1, "AVG": 0.228, "Style": "Power"},
            "巨人": {"ERA": 4.0, "AVG": 0.230, "Style": "Defensive"},
            "紅雀": {"ERA": 3.9, "AVG": 0.232, "Style": "SmallBall"},
            "光芒": {"ERA": 3.8, "AVG": 0.230, "Style": "Defensive"},
            "紅人": {"ERA": 4.2, "AVG": 0.225, "Style": "Power"},
            "海盜": {"ERA": 4.1, "AVG": 0.228, "Style": "SmallBall"},
            "國民": {"ERA": 4.3, "AVG": 0.220, "Style": "SmallBall"},
            "天使": {"ERA": 4.4, "AVG": 0.218, "Style": "Power"},
            "馬林魚": {"ERA": 4.2, "AVG": 0.220, "Style": "Defensive"},
            "運動家": {"ERA": 4.5, "AVG": 0.215, "Style": "Power"},
            "洛磯": {"ERA": 4.7, "AVG": 0.225, "Style": "Power"},
            "白襪": {"ERA": 4.8, "AVG": 0.210, "Style": "SmallBall"}
        }
        self.simulations = 100000

    def get_tactical_clash(self, style1, style2):
        matrix = {("Power", "Defensive"): 1.15, ("SmallBall", "Power"): 1.1, ("Defensive", "SmallBall"): 1.1}
        return matrix.get((style1, style2), 1.0)

    def run(self):
        matchups = [{"away": "洋基", "home": "道奇"}, {"away": "勇士", "home": "費城人"}]
        results = {}
        for m in matchups:
            t1, t2 = self.team_stats.get(m['away']), self.team_stats.get(m['home'])
            lam_a = (t1["AVG"] / t2["ERA"]) * 10 * self.get_tactical_clash(t1["Style"], t2["Style"])
            lam_b = (t2["AVG"] / t1["ERA"]) * 10 * self.get_tactical_clash(t2["Style"], t1["Style"])
            s_a = np.random.poisson(lam_a, self.simulations)
            s_b = np.random.poisson(lam_b, self.simulations)
            vals, counts = np.unique(np.column_stack((s_a, s_b)), axis=0, return_counts=True)
            top = vals[np.argsort(counts)[-2:]][::-1]
            win_prob = np.mean(s_a > s_b)
            results[f"{m['away']} 對 {m['home']}"] = {
                "勝率": f"{max(win_prob, 1-win_prob):.2%}",
                "最可能比分": f"{top[0][0]}:{top[0][1]}",
                "次要比分": f"{top[1][0]}:{top[1][1]}",
                "錯誤機率": f"{1 - max(win_prob, 1-win_prob):.2%}",
                "戰術分析": f"{t1['Style']} VS {t2['Style']} - 戰術權重校準完成"
            }
        with open("latest_forecast.json", "w", encoding="utf-8") as f:
            json.dump({"last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "predictions": results}, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    MLB_SuperAnalyzer().run()
