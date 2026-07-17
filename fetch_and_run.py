    def run(self):
        # 使用當前日期
        date_str = datetime.now().strftime('%Y-%m-%d')
        url = f"https://v1.baseball.api-sports.io/games?league=1&season=2026&date={date_str}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=20)
            res_json = response.json()
            
            # --- 除錯核心：將 API 回傳結構印到 Log 中 ---
            print(f"API URL: {url}")
            print(f"API Response: {res_json}")
            
            games = res_json.get("response", [])
            print(f"抓取到的比賽數量: {len(games)}")
            
            if not games:
                print("API 沒有回傳任何賽事資料，請檢查 API Key 是否有效或日期是否正確。")
                return 

        except Exception as e:
            print(f"發生錯誤: {e}")
            return
            
        # ... (後續的模擬邏輯) ...
