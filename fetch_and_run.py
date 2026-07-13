import math
import random
import json
import os
from datetime import datetime
from collections import defaultdict, Counter
import requests

class MLBDataFetcher:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.park_factors = {
            "Rockies": 112, "Red Sox": 109, "Reds": 105, "Dodgers": 103, "Yankees": 102,
            "Braves": 101, "Astros": 101, "Phillies": 102, "Orioles": 98, "Padres": 96,
            "Guardians": 99, "Brewers": 100, "Mariners": 95, "Twins": 99, "Tigers": 97,
            "Mets": 96, "Royals": 98, "Diamondbacks": 99, "Cubs": 101, "Cardinals": 98,
            "Rays": 97, "Rangers": 100, "Giants": 95, "Pirates": 99, "Blue Jays": 100,
            "Angels": 101, "Nationals": 99, "Marlins": 96, "Athletics": 97, "White Sox": 101
        }
        self.public_teams = ["Dodgers", "Yankees", "Cubs", "Red Sox", "Braves"]

    def fetch_team_base_tactics(self):
        tactics = defaultdict(lambda: "平衡作戰流")
        styles = {
            "Dodgers": "大砲轟炸流", "Yankees": "大砲轟炸流", "Braves": "速度壓迫流",
            "Phillies": "投手鐵壁流", "Astros": "小球戰術流", "Orioles": "速度壓迫流",
            "Padres": "小球戰術流", "Guardians": "速度壓迫流", "Mariners": "投手鐵壁流",
            "Rockies": "大砲轟炸流"
        }
        for t, s in styles.items(): tactics[t] = s
        return tactics

    def parse_real_weather(self, weather_str):
        if not weather_str: return 1.0
        w_lower = weather_str.lower()
        if "dome" in w_lower or "indoor" in w_lower or "roof closed" in w_lower: return 1.0
        fatigue_multiplier = 1.0
        if "degrees" in w_lower:
            try:
                temp = int(w_lower.split(" degrees")[0].split()[-1])
                if temp > 90: fatigue_multiplier += 0.15
                elif temp < 55: fatigue_multiplier += 0.10
            except: pass
        if "rain" in w_lower or "humidity" in w_lower or "drizzle" in w_lower: fatigue_multiplier += 0.05
        return fatigue_multiplier

    def fetch_player_split_stats(self, player_id, pitcher_hand):
        split_group = "vsLeft" if pitcher_hand == "L" else "vsRight"
        url = f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats?stats=statSplits&group=batting"
        try:
            res = requests.get(url, headers=self.headers, timeout=4).json()
            splits = res.get("stats", [{}])[0].get("splits", [])
            for s in splits:
                if s.get("split", {}).get("name") == split_group:
                    stat = s.get("stat", {})
                    ops = float(stat.get("ops", 0.730))
                    avg = float(stat.get("avg", 0.250))
                    slg = float(stat.get("slg", 0.410))
                    iso = max(0.05, slg - avg)
                    return ops, iso
        except:
            pass
        return 0.730, 0.160

    def fetch_team_bullpen_era(self, team_id_or_name):
        base_bullpen_era = {
            "Dodgers": 3.65, "Yankees": 3.80, "Braves": 3.50, "Phillies": 3.55, "Astros": 3.90,
            "Orioles": 3.75, "Padres": 3.40, "Guardians": 3.20, "Mariners": 3.30, "Brewers": 3.45,
            "Mets": 4.10, "Rangers": 4.25, "Cubs": 3.95, "Red Sox": 4.30, "Twins": 3.85,
            "Tigers": 3.60, "Giants": 4.00, "Rays": 3.70, "Diamondbacks": 4.15, "Royals": 3.90,
            "Rockies": 5.10, "White Sox": 4.90, "Marlins": 4.40, "A's": 4.20, "Pirates": 4.05
        }
        return base_bullpen_era.get(team_id_or_name, 3.95)

    def fetch_todays_schedule_and_odds(self, elo_model):
        matches = []
        today_str = datetime.now().strftime("%Y-%m-%d")
        url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={today_str}&hydrate=weather,lineups"
        
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
        
        tactics_db = self.fetch_team_base_tactics()

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
                            w_info = game.get("weather", {}).get("condition", "75 Degrees, Clear")
                            w_mod = self.parse_real_weather(w_info)
                            p_factor = self.park_factors.get(team_home, 100)
                            
                            bullpen_era_home = self.fetch_team_bullpen_era(team_home)
                            bullpen_era_away = self.fetch_team_bullpen_era(team_away)
                            
                            pitcher_hand_home = "R"
                            pitcher_hand_away = "R"
                            real_era_home_pitcher = 3.90
                            real_era_away_pitcher = 4.10
                            
                            try:
                                hp = game.get("teams", {}).get("home", {}).get("probablePitcher", {})
                                if hp:
                                    p_res = requests.get(f"https://statsapi.mlb.com/api/v1/people/{hp.get('id')}?hydrate=stats(group=[pitching],types=[season])", headers=self.headers, timeout=4).json()
                                    pitcher_hand_home = p_res.get("people", [{}])[0].get("pitchHand", {}).get("code", "R")
                                    real_era_home_pitcher = float(p_res.get("people", [{}])[0].get("stats", [{}])[0].get("splits", [{}])[0].get("stat", {}).get("era", 3.90))
                            except: pass

                            try:
                                ap = game.get("teams", {}).get("away", {}).get("probablePitcher", {})
                                if ap:
                                    p_res = requests.get(f"https://statsapi.mlb.com/api/v1/people/{ap.get('id')}?hydrate=stats(group=[pitching],types=[season])", headers=self.headers, timeout=4).json()
                                    pitcher_hand_away = p_res.get("people", [{}])[0].get("pitchHand", {}).get("code", "R")
                                    real_era_away_pitcher = float(p_res.get("people", [{}])[0].get("stats", [{}])[0].get("splits", [{}])[0].get("stat", {}).get("era", 4.10))
                            except: pass

                            lineups = game.get("lineups", {})
                            real_ops_home, real_iso_home = 0.745, 0.165
                            real_ops_away, real_iso_away = 0.735, 0.155
                            
                            home_lineup = lineups.get("homePlayers", [])
                            if home_lineup:
                                stats_list = [self.fetch_player_split_stats(p.get("id"), pitcher_hand_away) for p in home_lineup]
                                real_ops_home = sum(s[0] for s in stats_list) / len(stats_list)
                                real_iso_home = sum(s[1] for s in stats_list) / len(stats_list)
                            
                            away_lineup = lineups.get("awayPlayers", [])
                            if away_lineup:
                                stats_list = [self.fetch_player_split_stats(p.get("id"), pitcher_hand_home) for p in away_lineup]
                                real_ops_away = sum(s[0] for s in stats_list) / len(stats_list)
                                real_iso_away = sum(s[1] for s in stats_list) / len(stats_list)

                            base_ou = 8.5
                            if p_factor > 105: base_ou = 9.5
                            if p_factor > 110: base_ou = 11.5
                            elif p_factor < 96: base_ou = 7.5
                            
                            elo_diff = elo_model.ratings[team_home] - elo_model.ratings[team_away]
                            expected_prob_a = 1 / (1 + 10**((-elo_diff) / 400))
                            market_odds_a = round(max(1.10, min(4.00, 1.05 / expected_prob_a)), 2)
                            market_odds_b = round(max(1.10, min(4.00, 1.05 / (1.0 - expected_prob_a))), 2)

                            matches.append({
                                "team_a": team_home, "team_b": team_away,
                                "weather_info": w_info,
                                "factors": {
                                    "weather_modifier": w_mod,
                                    "park_factor": p_factor,
                                    "tactics_a": tactics_db[team_home], "tactics_b": tactics_db[team_away],
                                    "market_odds_a": market_odds_a, "market_odds_b": market_odds_b,
                                    "over_under_line": base_ou,
                                    "is_home_a": True,
                                    "player_ops_a": real_ops_home, "player_ops_b": real_ops_away,
                                    "player_iso_a": real_iso_home, "player_iso_b": real_iso_away,
                                    "pitcher_era_a": real_era_home_pitcher, "pitcher_era_b": real_era_away_pitcher,
                                    "bullpen_era_a": bullpen_era_home, "bullpen_era_b": bullpen_era_away,
                                    "is_public_a": team_home in self.public_teams,
                                    "is_public_b": team_away in self.public_teams
                                }
                            })
        except Exception as e:
            print(f"Error: {e}")
            
        if not matches:
            all_teams = list(name_map.values())
            random.shuffle(all_teams)
            dummy_weathers = ["82 Degrees, Clear", "72 Degrees, Dome"]
            for i in range(0, 14, 2):
                ta, tb = all_teams[i], all_teams[i+1]
                w_str = random.choice(dummy_weathers)
                p_fac = self.park_factors.get(ta, 100)
                matches.append({
                    "team_a": ta, "team_b": tb,
                    "weather_info": w_str,
                    "factors": {
                        "weather_modifier": self.parse_real_weather(w_str),
                        "park_factor": p_fac,
                        "tactics_a": tactics_db[ta], "tactics_b": tactics_db[tb],
                        "market_odds_a": 1.75, "market_odds_b": 2.15,
                        "over_under_line": 10.5 if ta == "Rockies" else (7.5 if p_fac < 96 else 8.5),
                        "is_home_a": True,
                        "player_ops_a": round(random.uniform(0.720, 0.810), 3), 
                        "player_ops_b": round(random.uniform(0.690, 0.780), 3),
                        "player_iso_a": round(random.uniform(0.130, 0.220), 3),
                        "player_iso_b": round(random.uniform(0.120, 0.200), 3),
                        "pitcher_era_a": round(random.uniform(2.60, 4.80), 2),
                        "pitcher_era_b": round(random.uniform(2.90, 5.20), 2),
                        "bullpen_era_a": round(random.uniform(3.20, 4.50), 2),
                        "bullpen_era_b": round(random.uniform(3.30, 4.80), 2),
                        "is_public_a": ta in self.public_teams,
                        "is_public_b": tb in self.public_teams
                    }
                })
        return matches

class AdvancedEloRating:
    def __init__(self, initial_rating=1500):
        real_elo_base = {
            "Dodgers": 1615, "Yankees": 1585, "Braves": 1560, "Phillies": 1575, "Astros": 1550, "Orioles": 1565,
            "Padres": 1545, "Diamondbacks": 1525, "Mets": 1520, "Brewers": 1540, "Guardians": 1525, "Royals": 1515,
            "Twins": 1510, "Red Sox": 1505, "Mariners": 1515, "Tigers": 1500, "Rangers": 1495, "Cubs": 1490,
            "Blue Jays": 1485, "Giants": 1480, "Cardinals": 1485, "Rays": 1490, "Reds": 1475, "Pirates": 1460,
            "Nationals": 1450, "Angels": 1440, "Marlins": 1430, "Oakland": 1420, "Rockies": 1410, "White Sox": 1350
        }
        self.ratings = defaultdict(lambda: initial_rating)
        for t, r in real_elo_base.items(): self.ratings[t] = r

    def load_historical_elo(self):
        if os.path.exists("latest_forecast.json"):
            try:
                with open("latest_forecast.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    old_elo = data.get("historical_elo", {})
                    for team, r in old_elo.items(): self.ratings[team] = r
            except: pass

class AdvancedPoissonPredictor:
    def __init__(self):
        self.league_avg_runs = 4.45
        self.league_avg_ops = 0.730
        self.league_avg_era = 4.00

    def calculate_match_lambdas(self, team_a, team_b, elo_model, factors, inning):
        p_ops_a = factors.get("player_ops_a", 0.730)
        p_ops_b = factors.get("player_ops_b", 0.730)
        p_iso_a = factors.get("player_iso_a", 0.160)
        p_iso_b = factors.get("player_iso_b", 0.160)
        
        if inning <= 6:
            current_era_a = factors.get("pitcher_era_a", 4.00)
            current_era_b = factors.get("pitcher_era_b", 4.00)
            fatigue_mod = factors.get("weather_modifier", 1.0)
            if inning > 4:
                current_era_a *= (1 + (inning - 4) * 0.05 * fatigue_mod)
                current_era_b *= (1 + (inning - 4) * 0.05 * fatigue_mod)
        else:
            current_era_a = factors.get("bullpen_era_a", 4.00)
            current_era_b = factors.get("bullpen_era_b", 4.00)
        
        park_mod = factors.get("park_factor", 100) / 100.0
        if park_mod < 1.0:
            iso_impact_a = 1.0 - (0.160 - p_iso_a) * (1.0 - park_mod) * 2.0
            iso_impact_b = 1.0 - (0.160 - p_iso_b) * (1.0 - park_mod) * 2.0
            park_mod_a = park_mod * max(0.85, iso_impact_a)
            park_mod_b = park_mod * max(0.85, iso_impact_b)
        else:
            park_mod_a = park_mod
            park_mod_b = park_mod
        
        base_a = (current_era_b / self.league_avg_era) * (p_ops_a / self.league_avg_ops) * self.league_avg_runs * park_mod_a
        base_b = (current_era_a / self.league_avg_era) * (p_ops_b / self.league_avg_ops) * self.league_avg_runs * park_mod_b
        
        lambda_a = base_a / 9.0
        lambda_b = base_b / 9.0
        
        if factors.get("is_home_a", False): lambda_a *= 1.04
        else: lambda_b *= 1.04
            
        if inning >= 7:
            tac_a, tac_b = factors.get("tactics_a"), factors.get("tactics_b")
            if tac_a == "小球戰術流" and tac_b == "投手鐵壁流": lambda_a *= 1.04
            if tac_b == "小球戰術流" and tac_a == "投手鐵壁流": lambda_b *= 1.04
            
        rating_diff = elo_model.ratings[team_a] - elo_model.ratings[team_b]
        elo_mod = 1 + (rating_diff / 1500)
        lambda_a *= elo_mod
        lambda_b *= (2.0 - elo_mod)
        
        return max(0.01, lambda_a), max(0.01, lambda_b)

    def _poisson_rvs(self, lam):
        if lam <= 0: return 0
        L = math.exp(-lam)
        k, p = 0, 1.0
        while p > L:
            k += 1
            p *= random.random()
        return k - 1

    def simulate_single_game(self, team_a, team_b, elo_model, factors):
        score_a = 0
        score_b = 0
        for inning in range(1, 10):
            lam_a, lam_b = self.calculate_match_lambdas(team_a, team_b, elo_model, factors, inning)
            score_a += self._poisson_rvs(lam_a)
            score_b += self._poisson_rvs(lam_b)
            
        innings = 9
        while score_a == score_b and innings < 15:
            innings += 1
            lam_a_ext, lam_b_ext = self.calculate_match_lambdas(team_a, team_b, elo_model, factors, 10)
            score_a += self._poisson_rvs(lam_a_ext * 1.20)
            score_b += self._poisson_rvs(lam_b_ext * 1.20)
            
        if score_a == score_b:
            if random.random() > 0.5: score_a += 1
            else: score_b += 1
        return score_a, score_b

class MatchAnalyzer:
    def __init__(self, elo_model, poisson_model):
        self.elo = elo_model
        self.poisson = poisson_model

    def analyze_match(self, team_a, team_b, factors, num_simulations=50000):
        wins_a = 0
        scores_history = []
        odds_a = factors.get("market_odds_a", 1.8)
        odds_b = factors.get("market_odds_b", 2.0)
        
        if factors.get("is_public_a", False) and odds_a < odds_b:
            adjusted_market_prob_a = (1.05 / odds_a) - 0.04
        else:
            adjusted_market_prob_a = (1.05 / odds_a)
            
        is_a_favorite = adjusted_market_prob_a > 0.5
        
        for _ in range(num_simulations):
            score_a, score_b = self.poisson.simulate_single_game(team_a, team_b, self.elo, factors)
            scores_history.append((score_a, score_b))
            if score_a > score_b: wins_a += 1

        prob_a = wins_a / num_simulations
        prob_b = 1.0 - prob_a
        winner = team_a if prob_a > prob_b else team_b
        upset_probability = prob_b if is_a_favorite else prob_a

        score_counts = Counter(scores_history)
        top_two_scores = score_counts.most_common(2)
        most_likely = f"{top_two_scores[0][0][0]} : {top_two_scores[0][0][1]}"
        second_likely = f"{top_two_scores[1][0][0]} : {top_two_scores[1][0][1]}"
        
        ou_line = factors.get("over_under_line", 8.5)
        over_count = sum(1 for sa, sb in scores_history if (sa + sb) > ou_line)
        over_prob = over_count / num_simulations
        ou_result = f"大分 ({over_prob:.1%})" if over_prob >= 0.5 else f"小分 ({1-over_prob:.1%})"

        return {
            "winner": winner,
            "win_probability": f"{max(prob_a, prob_b):.2%}",
            "most_likely": most_likely,
            "second_likely": second_likely,
            "over_under": f"{ou_result} [Line: {ou_line}]",
            "upset_prob": f"{upset_probability:.2%}"
        }

if __name__ == "__main__":
    elo = AdvancedEloRating()
    elo.load_historical_elo()
    fetcher = MLBDataFetcher()
    todays_matches = fetcher.fetch_todays_schedule_and_odds(elo)
    poisson = AdvancedPoissonPredictor()
    analyzer = MatchAnalyzer(elo, poisson)
    
    forecast_results = {}
    for match in todays_matches:
        ta = match["team_a"]
        tb = match["team_b"]
        fac = match["factors"]
        result = analyzer.analyze_match(ta, tb, fac, num_simulations=50000)
        forecast_results[f"{ta} vs {tb}"] = result

    output =
