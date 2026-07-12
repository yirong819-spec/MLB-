import math
import random
from collections import defaultdict

class EloRating:
    def __init__(self, initial_rating=1500, k_factor=32, home_field_advantage=50):
        self.ratings = defaultdict(lambda: initial_rating)
        self.k_factor = k_factor
        self.home_field_advantage = home_field_advantage

    def get_expected_score(self, rating_a, rating_b):
        # 計算 A 隊對抗 B 隊的預期勝率 (E_A)
        return 1 / (1 + 10**((rating_b - rating_a) / 400))

    def update_ratings(self, team_a, team_b, score_a, score_b, is_home_a=False):
        rating_a = self.ratings[team_a]
        rating_b = self.ratings[team_b]

        # 計算考量主場優勢後的積分
        adjusted_rating_a = rating_a + (self.home_field_advantage if is_home_a else 0)
        adjusted_rating_b = rating_b + (self.home_field_advantage if not is_home_a else 0)

        expected_a = self.get_expected_score(adjusted_rating_a, adjusted_rating_b)
        expected_b = self.get_expected_score(adjusted_rating_b, adjusted_rating_a)

        # 決定實際勝負結果 (平手各 0.5，棒球較少見但保留彈性)
        if score_a > score_b:
            actual_a, actual_b = 1, 0
        elif score_a < score_b:
            actual_a, actual_b = 0, 1
        else:
            actual_a, actual_b = 0.5, 0.5

        # 更新 Elo 積分
        self.ratings[team_a] += self.k_factor * (actual_a - expected_a)
        self.ratings[team_b] += self.k_factor * (actual_b - expected_b)

    def get_team_rating(self, team_name):
        return self.ratings[team_name]


class PoissonPredictor:
    def __init__(self):
        self.team_strengths = defaultdict(lambda: {"attack": 1.0, "defense": 1.0})
        self.league_avg_runs = 4.5  # 聯盟平均單場得分

    def set_team_strengths(self, team_name, attack_strength, defense_strength):
        self.team_strengths[team_name]["attack"] = attack_strength
        self.team_strengths[team_name]["defense"] = defense_strength

    def _poisson_rvs(self, lam):
        """使用高德納 (Knuth) 演算法手寫卜瓦松隨機抽樣，避免使用常態分佈近似導致的低分偏誤"""
        if lam <= 0:
            return 0
        L = math.exp(-lam)
        k = 0
        p = 1.0
        while p > L:
            k += 1
            p *= random.random()
        return k - 1

    def get_expected_runs(self, team_a, team_b, elo_model, is_home_a=False):
        # 基礎進防守與主客場因子
        home_advantage_factor = 1.05 if is_home_a else 1.0
        away_disadvantage_factor = 0.95 if not is_home_a else 1.0

        base_lambda_a = self.team_strengths[team_a]["attack"] * self.team_strengths[team_b]["defense"] * self.league_avg_runs * home_advantage_factor
        base_lambda_b = self.team_strengths[team_b]["attack"] * self.team_strengths[team_a]["defense"] * self.league_avg_runs * away_disadvantage_factor

        # 【優化】連動 Elo 積分：讓球隊近況實力差距按比例影響期望得分
        # 每差 100 分 Elo，預期得分調整約 10%
        rating_diff = elo_model.get_team_rating(team_a) - elo_model.get_team_rating(team_b)
        elo_modifier = 1 + (rating_diff / 1000)
        elo_modifier = max(0.5, min(1.5, elo_modifier)) # 設上下限防止極端值

        lambda_a = base_lambda_a * elo_modifier
        lambda_b = base_lambda_b * (2 - elo_modifier) # 相互制衡
        
        return max(0.1, lambda_a), max(0.1, lambda_b)

    def simulate_game_score(self, team_a, team_b, elo_model, is_home_a=False):
        lambda_a, lambda_b = self.get_expected_runs(team_a, team_b, elo_model, is_home_a)
        
        # 【優化】使用真實的卜瓦松分佈模擬得分，棒球比分不會再出現被強行四捨五入的狀況
        score_a = self._poisson_rvs(lambda_a)
        score_b = self._poisson_rvs(lambda_b)
        
        # 棒球賽制沒有平手，若平手則進行延長賽，直到分出勝負
        while score_a == score_b:
            # 延長賽模擬（各自加賽局的預期得分率，通常較低，這裡簡化為原lambda的 1/9）
            score_a += self._poisson_rvs(lambda_a / 9)
            score_b += self._poisson_rvs(lambda_b / 9)
            
        return score_a, score_b


class MonteCarloSimulator:
    def __init__(self, elo_model, poisson_model):
        self.elo = elo_model
        self.poisson = poisson_model

    def simulate_game(self, team_a, team_b, is_home_a=False):
        # 傳入 self.elo 以便在計算 lambda 時引入 Elo 動態加權
        score_a, score_b = self.poisson.simulate_game_score(team_a, team_b, self.elo, is_home_a)
        
        # 模擬完當下立刻更新 Elo
        self.elo.update_ratings(team_a, team_b, score_a, score_b, is_home_a)
        return team_a if score_a > score_b else team_b, score_a, score_b

    def simulate_series(self, team_a, team_b, num_games, home_team_schedule, initial_elo_ratings=None):
        if initial_elo_ratings:
            for team, rating in initial_elo_ratings.items():
                self.elo.ratings[team] = rating

        wins_a = 0
        wins_b = 0
        series_results = []

        for i in range(num_games):
            is_home_a = home_team_schedule[i] == team_a
            winner, score_a, score_b = self.simulate_game(team_a, team_b, is_home_a)
            series_results.append(f"Game {i+1}: {team_a} {score_a} - {team_b} {score_b} (Winner: {winner})")
            if winner == team_a:
                wins_a += 1
            else:
                wins_b += 1
        
        series_winner = team_a if wins_a > wins_b else team_b
        return series_winner, wins_a, wins_b, series_results

    def simulate_playoff_series(self, team_a, team_b, best_of):
        num_games = best_of
        needed_to_win = (best_of // 2) + 1
        
        if best_of == 3:
            schedule = [team_a, team_a, team_b]
        elif best_of == 5:
            schedule = [team_a, team_a, team_b, team_b, team_a]
        elif best_of == 7:
            schedule = [team_a, team_a, team_b, team_b, team_b, team_a, team_a]
        else:
            schedule = [team_a] * num_games

        wins_a = 0
        wins_b = 0
        for i in range(num_games):
            is_home_a = schedule[i] == team_a
            winner, _, _ = self.simulate_game(team_a, team_b, is_home_a)
            if winner == team_a:
                wins_a += 1
            else:
                wins_b += 1
            
            if wins_a == needed_to_win or wins_b == needed_to_win:
                break
        
        return team_a if wins_a > wins_b else team_b

    def simulate_mlb_playoffs(self, league_teams, num_simulations=1000):
        championship_wins = defaultdict(int)
        initial_elo_snapshot = {team: self.elo.get_team_rating(team) for league in league_teams.values() for team in league}

        for _ in range(num_simulations):
            for team, rating in initial_elo_snapshot.items():
                self.elo.ratings[team] = rating

            league_champions = []
            for league, teams in league_teams.items():
                # Wild Card Series (Best of 3)
                wc1_winner = self.simulate_playoff_series(teams[2], teams[5], 3)
                wc2_winner = self.simulate_playoff_series(teams[3], teams[4], 3)

                # Division Series (Best of 5)
                ds1_winner = self.simulate_playoff_series(teams[0], wc2_winner, 5)
                ds2_winner = self.simulate_playoff_series(teams[1], wc1_winner, 5)

                # League Championship Series (Best of 7)
                league_winner = self.simulate_playoff_series(ds1_winner, ds2_winner, 7)
                league_champions.append(league_winner)
            
            # World Series (Best of 7)
            ws_winner = self.simulate_playoff_series(league_champions[0], league_champions[1], 7)
            championship_wins[ws_winner] += 1

        return championship_wins


# 測試執行：
if __name__ == "__main__":
    elo = EloRating()
    poisson = PoissonPredictor()
    mc_simulator = MonteCarloSimulator(elo, poisson)

    # 初始化球隊數據
    poisson.set_team_strengths("Yankees", 1.1, 0.9)
    poisson.set_team_strengths("Red Sox", 0.9, 1.1)
    poisson.set_team_strengths("Dodgers", 1.2, 0.8)
    poisson.set_team_strengths("Giants", 0.8, 1.2)
    poisson.set_team_strengths("Astros", 1.15, 0.85)
    poisson.set_team_strengths("Rays", 1.05, 0.95)

    print("--- 完善版模擬器測試 ---")
    
    # 測試單場比賽（此時會自動處理平手延長賽，且得分基於真實卜瓦松分佈）
    sim_score_yankees, sim_score_redsox = poisson.simulate_game_score("Yankees", "Red Sox", elo, is_home_a=True)
    print(f"真實卜瓦松模擬單場 (洋基 vs 紅襪): 洋基 {sim_score_yankees} - 紅襪 {sim_score_redsox}")

    # 執行季後賽 1000 次蒙地卡羅模擬
    mlb_teams = {
        "AL": ["Yankees", "Astros", "Rays", "Blue Jays", "Guardians", "Mariners"],
        "NL": ["Dodgers", "Braves", "Phillies", "Brewers", "Padres", "Mets"]
    }
    for league in mlb_teams.values():
        for team in league:
            if team not in poisson.team_strengths:
                poisson.set_team_strengths(team, 1.0, 1.0)

    playoff_results = mc_simulator.simulate_mlb_playoffs(mlb_teams, num_simulations=1000)
    
    print("\n世界大賽奪冠機率統計 (1000次模擬):")
    for team, wins in sorted(playoff_results.items(), key=lambda item: item[1], reverse=True):
        print(f"{team}: {wins / 1000:.2%}")
# (請在此處上方貼上之前的三個 Class 程式碼...)

if __name__ == "__main__":
    elo = EloRating()
    poisson = PoissonPredictor()

    # 初始化球隊數據
    poisson.set_team_strengths("Yankees", 1.1, 0.9)
    poisson.set_team_strengths("Red Sox", 0.9, 1.1)
    poisson.set_team_strengths("Dodgers", 1.2, 0.8)
    poisson.set_team_strengths("Giants", 0.8, 1.2)

    mlb_teams = {
        "AL": ["Yankees", "Astros", "Rays", "Blue Jays", "Guardians", "Mariners"],
        "NL": ["Dodgers", "Braves", "Phillies", "Brewers", "Padres", "Mets"]
    }
    for league in mlb_teams.values():
        for team in league:
            if team not in poisson.team_strengths:
                poisson.set_team_strengths(team, 1.0, 1.0)

    from datetime import datetime
    sim = MonteCarloSimulator(elo, poisson)
    results = sim.simulate_mlb_playoffs(mlb_teams, num_simulations=5000)

    total_sims = sum(results.values())
    probs = {team: wins / total_sims for team, wins in results.items()}

    output = {
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "probabilities": probs
    }

    with open("latest_forecast.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    print("Data updated successfully!")
