import math
import random
import json
from datetime import datetime
from collections import defaultdict, Counter

# =====================================================================
# 1. 深度多因子預測核心演算法
# =====================================================================

class AdvancedEloRating:
    def __init__(self, initial_rating=1500, k_factor=32):
        self.ratings = defaultdict(lambda: initial_rating)
        self.k_factor = k_factor

    def get_expected_score(self, rating_a, rating_b):
        return 1 / (1 + 10**((rating_b - rating_a) / 400))

    def update_ratings(self, team_a, team_b, score_a, score_b, factors):
        rating_a = self.ratings[team_a]
        rating_b = self.ratings[team_b]
        
        # 考量因素 6: 場地優勢 (基本加成)
        home_adv = 50 if factors.get("is_home_a", False) else -50
        
        expected_a = self.get_expected_score(rating_a + home_adv, rating_b)
        actual_a = 1 if score_a > score_b else (0 if score_a < score_b else 0.5)
        
        self.ratings[team_a] += self.k_factor * (actual_a - expected_a)
        self.ratings[team_b] += self.k_factor * ((1 - actual_a) - (1 - expected_a))


class AdvancedPoissonPredictor:
    def __init__(self):
        # 考量因素 1 & 12: 近年實力、打擊率(attack)、防禦率(defense)、上壘率(OBP)的綜合初始實力
        self.team_base = defaultdict(lambda: {"attack": 1.0, "defense": 1.0})
        self.league_avg_runs = 4.5

    def set_team_base(self, team_name, attack, defense):
        self.team_base[team_name]["attack"] = attack
        self.team_base[team_name]["defense"] = defense

    def calculate_match_lambdas(self, team_a, team_b, elo_model, factors):
        """核心關鍵：將 12 大因素融合進卜瓦松分佈的 Lambda (期望得分) 計算中"""
        
        # 基礎攻防實力 (考量因素 1, 12)
        base_a = self.team_base[team_a]["attack"] * self.team_base[team_b]["defense"] * self.league_avg_runs
        base_b = self.team_base[team_b]["attack"] * self.team_base[team_a]["defense"] * self.league_avg_runs
        
        # 乘數初始化
        mod_a = 1.0
        mod_b = 1.0
        
        # 考量因素 2: 歷史對決結果 (心理/經驗優勢)
        if factors.get("historical_advantage") == team_a: mod_a *= 1.05; mod_b *= 0.95
        elif factors.get("historical_advantage") == team_b: mod_b *= 1.05; mod_a *= 0.95
            
        # 考量因素 3: 球員年齡結構 (年輕有活力/老將經驗)
        # 假設 A 隊體能較好，進攻微幅上升
        mod_a *= factors.get("age_factor_a", 1.0)
        mod_b *= factors.get("age_factor_b", 1.0)
        
        # 考量因素 4: 傷病風險 (主將缺陣會降低攻防實力)
        mod_a *= (1.0 - factors.get("injury_risk_a", 0.0))
        mod_b *= (1.0 - factors.get("injury_risk_b", 0.0))
        
        # 考量因素 5: 戰術相剋 (如：左投剋左打、飛球投手剋滾地球球場)
        if factors.get("tactical_counter") == team_a: mod_a *= 1.08; mod_b *= 0.92
        elif factors.get("tactical_counter") == team_b: mod_b *= 1.08; mod_a *= 0.92
            
        # 考量因素 6: 場地優勢 (主場加成，特殊球場如高原球場另加)
        if factors.get("is_home_a", False):
            mod_a *= (1.05 + factors.get("special_stadium_effect_a", 0.0))
        else:
            mod_b *= (1.05 + factors.get("special_stadium_effect_b", 0.0))
            
        # 考量因素 7: 隊伍的近期狀態 & Elo 積分連動
        rating_diff = elo_model.ratings[team_a] - elo_model.ratings[team_b]
        elo_mod = 1 + (rating_diff / 1200)
        mod_a *= elo_mod
        mod_b *= (2.0 - elo_mod)
        
        # 考量因素 10 & 11: 外加干擾壓力 (如連戰疲勞、背水一戰) 與 恩怨情仇 (德比大戰激發潛能)
        if factors.get("is_grudge_match", False):
            mod_a *= 1.03; mod_b *= 1.03 # 雙方通常打擊慾望強烈，分數易偏高
        mod_a *= (1.0 - factors.get("pressure_distraction_a", 0.0))
        mod_b *= (1.0 - factors.get("pressure_distraction_b", 0.0))
        
        # 確保 lambda 不會變成負數
        lambda_a = max(0.1, base_a * mod_a)
        lambda_b = max(0.1, base_b * mod_b)
        
        return lambda_a, lambda_b

    def _poisson_rvs(self, lam):
        if lam <= 0: return 0
        L = math.exp(-lam)
        k = 0; p = 1.0
        while p > L:
            k += 1
            p *= random.random()
        return k - 1

    def simulate_single_game(self, team_a, team_b, elo_model, factors):
        lambda_a, lambda_b = self.calculate_match_lambdas(team_a, team_b, elo_model, factors)
        score_a = self._poisson_rvs(lambda_a)
        score_b = self._poisson_rvs(lambda_b)
        
        # 延長賽處理
        while score_a == score_b:
            score_a += self._poisson_rvs(lambda_a / 9)
            score_b += self._poisson_rvs(lambda_b / 9)
        return score_a, score_b


# =====================================================================
# 2. 萬次蒙地卡羅綜合評估器
# =====================================================================

class MatchAnalyzer:
    def __init__(self, elo_model, poisson_model):
        self.elo = elo_model
        self.poisson = poisson_model

    def analyze_match(self, team_a, team_b, factors, num_simulations=10000):
        wins_a = 0
        scores_history = []
        
        # 考量因素 8 & 9: 賽事賠率與莊家心理
        # 從賠率中推導出「市場預期爆冷門檻」
        odds_a = factors.get("market_odds_a", 1.8)
        odds_b = factors.get("market_odds_b", 2.0)
        is_a_favorite = odds_a < odds_b
        
        for _ in range(num_simulations):
            score_a, score_b = self.poisson.simulate_single_game(team_a, team_b, self.elo, factors)
            scores_history.append((score_a, score_b))
            if score_a > score_b:
                wins_a += 1

        # 計算誰贏機率
        prob_a = wins_a / num_simulations
        prob_b = 1.0 - prob_a
        winner = team_a if prob_a > prob_b else team_b
        
        # 計算爆冷機率 (若弱勢方贏了，即為爆冷)
        if is_a_favorite:
            upset_probability = prob_b
        else:
            upset_probability = prob_a

        # 統計最可能比分、第二可能比分
        score_counts = Counter(scores_history)
        top_two_scores = score_counts.most_common(2)
        
        most_likely_score = f"{top_two_scores[0][0][0]} : {top_two_scores[0][0][1]}"
        second_likely_score = f"{top_two_scores[1][0][0]} : {top_two_scores[1][0][1]}" if len(top_two_scores) > 1 else "N/A"
        
        # 計算大小分 (以莊家開出的總分盤口為基準，例如 8.5 分)
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
# 3. 每日賽事動態輸入與自動執行存檔
# =====================================================================

if __name__ == "__main__":
    # 初始化模型
    elo = AdvancedEloRating()
    poisson = AdvancedPoissonPredictor()
    
    # 因素 1 & 12: 設定兩隊的近年實力基礎、打擊率、防禦率、上壘率綜合評估
    poisson.set_team_base("Yankees", attack=1.15, defense=0.85) # 洋基強攻
    poisson.set_team_base("Dodgers", attack=1.20, defense=0.80) # 道奇頂級攻防
    
    # 【每日核心配置區】你每天只需在這邊調整當天比賽的 12 大指標參數：
    todays_matches = [
        {
            "team_a": "Dodgers",
            "team_b": "Yankees",
            "factors": {
                "is_home_a": True,               # 因素 6: 道奇主場
                "historical_advantage": "Dodgers",# 因素 2: 歷史對戰道奇佔優
                "age_factor_a": 1.02,            # 因素 3: 道奇年齡結構紅利 (+2% 進攻)
                "age_factor_b": 0.99,            # 因素 3: 洋基老將略多疲勞 (-1% 進攻)
                "injury_risk_a": 0.05,           # 因素 4: 道奇微傷兵 (-5% 實力)
                "injury_risk_b": 0.00,           # 因素 4: 洋基陣容健康
                "tactical_counter": "Yankees",   # 因素 5: 戰術相剋 (洋基今晚先發投手剋道奇打線)
                "special_stadium_effect_a": 0.01,# 因素 6: 道奇球場夜間加成
                "is_grudge_match": True,         # 因素 11: 世仇大戰
                "pressure_distraction_a": 0.02,  # 因素 10: 道奇面臨媒體連敗輿論壓力
                "pressure_distraction_b": 0.00,  # 因素 10: 洋基客場無多餘包袱
                "market_odds_a": 1.65,           # 因素 8: 莊家開出道奇獨贏賠率
                "market_odds_b": 2.25,           # 因素 8: 莊家開出洋基獨贏賠率
                "over_under_line": 8.5           # 因素 9: 莊家開出的總分盤口
            }
        }
    ]

    analyzer = MatchAnalyzer(elo, poisson)
    forecast_results = {}

    for match in todays_matches:
        ta = match["team_a"]
        tb = match["team_b"]
        fac = match["factors"]
        
        # 進行 10,000 次蒙地卡羅高精確模擬
        result = analyzer.analyze_match(ta, tb, fac, num_simulations=10000)
        
        match_key = f"{ta} vs {tb}"
        forecast_results[match_key] = result

    # 打包成前端需要的 JSON 格式
    output = {
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "predictions": forecast_results
    }
    
    with open("latest_forecast.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
        
    print("📋 12大因子綜合預測 JSON 檔案已產出成功！")
