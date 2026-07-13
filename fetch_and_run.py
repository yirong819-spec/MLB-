import math
import random
import json
import os
from datetime import datetime
from collections import defaultdict, Counter
import requests

# =====================================================================
# 1. MLB 官方即時數據 API 串接模組
# =====================================================================

class MLBDataFetcher:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def fetch_team_stats(self):
        """建立 30 支球隊的基礎攻防數據庫 (依據近年真實大聯盟數據基準)"""
        stats = defaultdict(lambda: {"attack": 1.0, "defense": 1.0})
        base_weights = {
            "Yankees": (1.18, 0.85), "Dodgers": (1.22, 0.81), "Braves": (1.12, 0.87),
            "Phillies": (1.14, 0.86), "Astros": (1.15, 0.89), "Orioles": (1.17, 0.90),
            "Rays": (1.02, 0.91), "Blue Jays": (1.04, 0.93), "Red Sox": (1.06, 0.95),
            "Guardians": (1.03, 0.88), "Twins": (1.07, 0.94), "Tigers": (1.01, 0.92),
            "Mariners": (0.96, 0.84), "Rangers": (1.05, 0.96), "Angels": (0.98, 1.05),
            "Athletics": (0.94, 1.08), "Mets": (1.09, 0.93), "Brewers": (1.04, 0.89),
            "Cubs": (1.02, 0.93), "Reds": (1.01, 0.98), "Pirates": (0.95, 0.96),
            "Cardinals": (0.99, 0.97), "Marlins": (0.93, 1.04), "Nationals": (0.95, 1.06),
            "Giants": (0.97, 0.93), "Padres": (1.11, 0.91), "Diamondbacks": (1.10, 0.95),
            "Rockies": (0.96, 1.15), "White Sox": (0.91, 1.18), "Royals": (1.05, 0.92)
        }
        for team, (att, deff) in base_weights.items():
            stats[team] = {"attack": att, "defense": deff}
        return stats

    def generate_realistic_factors(self, team_home, team_away, elo_rating_a, elo_rating_b):
        """
        【完善重點】拒絕純隨機！依據兩隊真實實力差與 Elo 評分，動態推導出貼切真實世界的 12 大因子
        """
        # 根據 Elo 實力差計算基礎勝率預期
        elo_diff = elo_rating_a - elo_rating_b
        expected_prob_a = 1 / (1 + 10**((-elo_diff) / 400))
        
        # 動態反推貼近拉斯維加斯盤口的真實賠率 (加上 5% 抽水)
        market_odds_a = round(max(1.10, min(4.00, 1.05 / expected_prob_a)), 2)
        market_odds_b = round(max(1.10, min(4.00, 1.05 / (1.0 - expected_prob_a))), 2)
        
        # 歷史優勢：實力強者或近況佳者有較高機率獲得歷史對戰優勢
        historical = team_home if expected_prob_a > 0.55 else (team_away if expected_prob_a < 0.45 else "None")
        
        # 心理壓力：強隊若輸球壓力較大，或強強對話時激發同區恩怨局 (Grudge Match)
        is_grudge = abs(elo_diff) < 80  # 實力伯仲之間時更容易形成勢均力敵的恩怨大戰
        
        # 傷兵與干擾因子改為微幅的良性擾動 (波動範圍縮小，確保預測穩定性)
        seed_a = random.seed(datetime.now().microsecond + 1)
        injury_a = round(random.uniform(0.01, 0.04), 3)
        injury_b = round(random.uniform(0.01, 0.04), 3)
        
        # 特定球場效應：例如洛磯山脈高海拔打者天堂
        stadium_effect = 0.05 if team_home == "Rockies" else 0.0
        
        # 大小分盤口動態設定
        ou_line = 7.5 if (elo_rating_a + elo_rating_b) > 3050 else 8.5
        if team_home == "Rockies": ou_line = 10.5 # 庫爾斯球場修正
        
        return {
            "is_home_a": True,
            "historical_advantage": historical,
            "age_factor_a": round(random.uniform(0.99, 1.01), 3),
            "age_factor_b": round(random.uniform(0.99, 1.01), 3),
            "injury_risk_a": injury_a,
            "injury_risk_b": injury_b,
            "tactical_counter": "None" if abs(elo_diff) > 150 else random.choice([team_home, team_away, "None"]),
            "special_stadium_effect_a": stadium_effect,
            "is_grudge_match": is_grudge,
            "pressure_distraction_a": round(random.uniform(0.0, 0.02), 3),
            "pressure_distraction_b": round(random.uniform(0.0, 0.02), 3),
            "market_odds_a": market_odds_a,
            "market_odds_b": market_odds_b,
            "over_under_line": ou_line
        }

    def fetch_todays_schedule_and_odds(self, elo_model):
        """實時下載或動態生成全聯盟賽事日程"""
        matches = []
        today_str = datetime.now().strftime("%Y-%m-%d")
        url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={today_str}"
        
        name_map = {
            "New York Yankees": "Yankees", "Los Angeles Dodgers": "Dodgers", "Atlanta Braves": "Braves",
            "Philadelphia Phillies": "Phillies", "Houston Astros": "Astros", "Baltimore Orioles": "Orioles",
            "Tampa Bay Rays": "Rays", "Toronto Blue Jays": "Blue Jays", "Boston Red Sox": "Red Sox",
            "Cleveland Guardians": "Guardians", "Minnesota Twins": "Twins", "Detroit Tigers": "Tigers",
            "Seattle Mariners": "Mariners", "Texas Rangers": "Rangers", "Los Angeles Angels": "Angels",
            "Oakland Athletics": "Athletics", "Sacramento Athletics": "Athletics", "New York Mets": "Mets", 
            "Milwaukee Brewers": "Brewers", "Chicago Cubs": "Cubs", "Cincinnati Reds": "Reds",
            "Pittsburgh Pirates": "Pirates", "St. Louis Cardinals": "Cardinals", "Miami Marlins": "Marlins",
            "Washington Nationals": "Nationals", "San Francisco Giants": "Giants", "San Diego Padres": "Padres",
            "Arizona Diamondbacks": "Diamondbacks", "Colorado Rockies": "Rockies", "Chicago White Sox": "White Sox",
            "Kansas City Royals": "Royals"
        }

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                dates = data.get("dates", [])
                if dates:
                    games = dates[0].get("games", [])
                    for game in games:
                        away_name = game.get("teams", {}).get("away", {}).get("team", {}).get("name")
                        home_name = game.get("teams", {}).get("home", {}).get("team", {}).get("name")
                        team_away = name_map.get(away_name)
                        team_home = name_map.get(home_name)
                        
                        if team_away and team_home:
                            fac = self.generate_realistic_factors(team_home, team_away, elo_model.ratings[team_home], elo_model.ratings[team_away])
                            matches.append({"team_a": team_home, "team_b": team_away, "factors": fac})
        except Exception as e:
            print(f"⚠️ 讀取 MLB 官方即時賽程時遭遇不穩定性: {e}")
            
        # 安全保底隨機組合展示模式 (確保非賽季期間網頁依然維持多隊精準模擬)
        if not matches:
            print("💡 偵測到今日官方無排定賽事，啟動全自動多隊模擬展示模式...")
            all_teams = list(name_map.values())
            random.shuffle(all_teams)
            for i in range(0, 14, 2):
                ta, tb = all_teams[i], all_teams[i+1]
                fac = self.generate_realistic_factors(ta, tb, elo_model.ratings[ta], elo_model.ratings[tb])
                matches.append({"team_a": ta, "team_b": tb, "factors": fac})
        return matches

# =====================================================================
# 2. 深度多因子大數據演算核心
# =====================================================================

class AdvancedEloRating:
    def __init__(self, initial_rating=1500):
        # 初始化 30 支球隊真實的歷史基準 ELO，拉開強弱隊差距，讓模擬更貼切真實
        real_elo_base = {
            "Dodgers": 1610, "Yankees": 1580, "Braves": 1560, "Phillies": 1570, "Astros": 1550, "Orioles": 1565,
            "Padres": 1540, "Diamondbacks": 1530, "Mets": 1525, "Brewers": 1535, "Guardians": 1520, "Royals": 1515,
            "Twins": 1510, "Red Sox": 1505, "Mariners": 1510, "Tigers": 1500, "Rangers": 1495, "Cubs": 1490,
            "Blue Jays": 1485, "Giants": 1480, "Cardinals": 1485, "Rays": 1490, "Reds": 1475, "Pirates": 1460,
            "Nationals": 1450, "Angels": 1440, "Marlins": 1430, "Oakland": 1420, "Rockies": 1410, "White Sox": 1350
        }
        self.ratings = defaultdict(lambda: initial_rating)
        for t, r in real_elo_base.items():
            self.ratings[t] = r

    def load_historical_elo(self):
        if os.path.exists("latest_forecast.json"):
            try:
                with open("latest_forecast.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    old_elo = data.get("historical_elo", {})
                    for team, r in old_elo.items():
                        self.ratings[team] = r
            except:
                pass


class AdvancedPoissonPredictor:
    def __init__(self, fetched_stats):
        self.team_base = fetched_stats
        self.league_avg_runs = 4.43 # 大聯盟歷年真實場均得分基準

    def calculate_match_lambdas(self, team_a, team_b, elo_model, factors):
        # 基礎攻防期望值計算
        base_a = self.team_base[team_a]["attack"] * self.team_base[team_b]["defense"] * self.league_avg_runs
        base_b = self.team_base[team_b]["attack"] * self.team_base[team_a]["defense"] * self.league_avg_runs
        
        mod_a, mod_b = 1.0, 1.0
        
        # 歷史優勢加成
        if factors.get("historical_advantage") == team_a: mod_a *= 1.03; mod_b *= 0.97
        elif factors.get("historical_advantage") == team_b: mod_b *= 1.03; mod_a *= 0.97
            
        # 年齡與傷兵擾動
        mod_a *= factors.get("age_factor_a", 1.0)
        mod_b *= factors.get("age_factor_b", 1.0)
        mod_a *= (1.0 - factors.get("injury_risk_a", 0.0))
        mod_b *= (1.0 - factors.get("injury_risk_b", 0.0))
        
        # 主場基本優勢與特殊球場加成
        if factors.get("is_home_a", False):
            mod_a *= (1.04 + factors.get("special_stadium_effect_a", 0.0))
            if factors.get("special_stadium_effect_a", 0.0) > 0: mod_b *= 1.05 # 庫爾斯球場客隊也會多得分
        
        # Elo 實力差動態修正 Lambda
        rating_diff = elo_model.ratings[team_a] - elo_model.ratings[team_b]
        elo_mod = 1 + (rating_diff / 1500)
        mod_a *= elo_mod
        mod_b *= (2.0 - elo_mod)
        
        return max(0.2, base_a * mod_a), max(0.2, base_b * mod_b)

    def _poisson_rvs(self, lam):
        if lam <= 0: return 0
        L = math.exp(-lam)
        k, p = 0, 1.0
        while p > L:
            k += 1
            p *= random.random()
        return k - 1

    def simulate_single_game(self, team_a, team_b, elo_model, factors):
        lambda_a, lambda_b = self.calculate_match_lambdas(team_a, team_b, elo_model, factors)
        score_a = self._poisson_rvs(lambda_a)
        score_b = self._poisson_rvs(lambda_b)
        
        # 棒球沒有平手，進入延長賽模擬 (降低攻防基底，模擬延長賽突破僵局制或投手消耗戰)
        innings = 9
        while score_a == score_b and innings < 15:
            innings += 1
            score_a += self._poisson_rvs(lambda_a / 9.0)
            score_b += self._poisson_rvs(lambda_b / 9.0)
        if score_a == score_b: # 萬一打到15局還平手，強行分勝負
            if random.random() > 0.5: score_a += 1
            else: score_b += 1
            
        return score_a, score_b


class MatchAnalyzer:
    def __init__(self, elo_model, poisson_model):
        self.elo = elo_model
        self.poisson = poisson_model

    def analyze_match(self, team_a, team_b, factors, num_simulations=10000):
        wins_a = 0
        scores_history = []
        odds_a = factors.get("market_odds_a", 1.8)
        odds_b = factors.get("market_odds_b", 2.0)
        
        # 根據我們前面推導的精準賠率定義誰是真正的莊家看好方
        is_a_favorite = odds_a < odds_b
        
        for _ in range(num_simulations):
            score_a, score_b = self.poisson.simulate_single_game(team_a, team_b, self.elo, factors)
            scores_history.append((score_a, score_b))
            if score_a > score_b:
                wins_a += 1

        prob_a = wins_a / num_simulations
        prob_b = 1.0 - prob_a
        
        # 預測勝方以模擬機率高者為準
        winner = team_a if prob_a > prob_b else team_b
        
        # 【精準定義爆冷率】如果模擬勝方跟莊家看好方相反，或者莊家看好方的輸球機率，才是精確的爆冷門率
        if is_a_favorite:
            upset_probability = prob_b
        else:
            upset_probability = prob_a

        score_counts = Counter(scores_history)
        top_two_scores = score_counts.most_common(2)
        
        most_likely_score = f"{top_two_scores[0][0][0]} : {top_two_scores[0][0][1]}"
        second_likely_score = f"{top_two_scores[1][0][0]} : {top_two_scores[1][0][1]}" if len(top_two_scores) > 1 else "N/A"
        
        ou_line = factors.get("over_under_line", 8.5)
        over_count = sum(1 for sa, sb in scores_history if (sa + sb) > ou_line)
        over_prob = over_count / num_simulations
        ou_result = f"大分 (機率 {over_prob:.1%})" if over_prob >= 0.5 else f"小分 (機率 {1-over_prob:.1%})"

        return {
            "winner": winner,
            "win_probability": f"{max(prob_a, prob_b):.2%}",
            "most_likely": most_likely_score,
            "second_likely": second_likely_score,
            "over_under": f"{ou_result} [盤口: {ou_line}]",
            "upset_prob": f"{upset_probability:.2%}"
        }

# =====================================================================
# 3. 每日自動化運算主流程
# =====================================================================

if __name__ == "__main__":
    print("🚀 啟動 2026 MLB 終極優化大數據分析站...")
    
    elo = AdvancedEloRating()
    elo.load_historical_elo()
    
    fetcher = MLBDataFetcher()
    fetched_stats = fetcher.fetch_team_stats()
    todays_matches = fetcher.fetch_todays_schedule_and_odds(elo)
    
    poisson = AdvancedPoissonPredictor(fetched_stats)
    analyzer = MatchAnalyzer(elo, poisson)
    
    forecast_results = {}
    for match in todays_matches:
        ta = match["team_a"]
        tb = match["team_b"]
        fac = match["factors"]
        
        result = analyzer.analyze_match(ta, tb, fac, num_simulations=10000)
        match_key = f"{ta} vs {tb}"
        forecast_results[match_key] = result

    # 強制每次寫入隨機打卡序號，強迫 GitHub Actions 必須推流更新
    output = {
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "force_refresh_token": f"{random.randint(100000, 999999)}-{datetime.now().microsecond}",
        "predictions": forecast_results,
        "historical_elo": dict(elo.ratings)
    }
    
    with open("latest_forecast.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
        
    print(f"🏁 終極優化版分析完成！今日共模擬並更新了 {len(todays_matches)} 場球賽。")
