import streamlit as st
import json
import os
import time

st.set_page_config(page_title="MLB 深度多因子大數據預測", layout="wide")

# =====================================================================
# ⚡ 核心優化：建立自動過期的資料讀取機制 (快取設定為 600 秒 = 10 分鐘)
# =====================================================================
@st.cache_data(ttl=600)  # 每 10 分鐘網頁就會強迫自己重新讀取 GitHub 的最新 JSON 檔
def load_prediction_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

st.title("🔮 2026 MLB 12大因子智能預測系統")
st.subheader("結合：攻防數據、歷史對決、年齡、傷病、戰術、心理、恩怨、莊家賠率之萬次蒙地卡羅分析")

# 全聯盟 30 支球隊的英翻中字典
TEAM_TRANSLATION = {
    "Yankees": "紐約洋基", "Red Sox": "波士頓紅襪", "Rays": "坦帕灣光芒", "Blue Jays": "多倫多藍鳥", "Orioles": "巴爾地摩金鶯",
    "Guardians": "克里夫蘭守護者", "Twins": "明尼蘇達雙城", "Tigers": "底特律老虎", "White Sox": "芝加哥白襪", "Royals": "堪薩斯皇家",
    "Astros": "休士頓太空人", "Mariners": "西雅圖水手", "Rangers": "德州遊騎兵", "Angels": "洛杉磯天使", "Athletics": "奧克蘭運動家",
    "Dodgers": "洛杉磯道奇", "Braves": "亞特蘭大勇士", "Phillies": "費城費城人", "Mets": "紐約大都會", "Marlins": "邁阿密馬林魚", "Nationals": "華盛頓國民",
    "Brewers": "密爾瓦基釀酒人", "Cubs": "芝加哥小熊", "Reds": "辛辛那提紅人", "Pirates": "匹茲堡海盜", "Cardinals": "聖路易紅雀",
    "Giants": "舊金山巨人", "Padres": "聖地牙哥教士", "Diamondbacks": "亞利桑那響尾蛇", "Rockies": "科羅拉多洛磯"
}

# ---------------------------------------------------------------------
# 🔘 介面優化：在網頁最上方直接做一個「一鍵即時更新」按鈕
# ---------------------------------------------------------------------
col_space, col_btn = st.columns([4, 1])
with col_btn:
    if st.button("🔄 點我即時同步數據"):
        st.cache_data.clear() # 點擊後，立刻清除這台手機的網頁快取
        st.toast("🚀 已成功強制同步最新大數據預測！", icon="✅")
        time.sleep(0.5)
        st.rerun() # 立即重整網頁畫面

# 讀取數據
json_file = "latest_forecast.json"
data = load_prediction_data(json_file)

if data is None:
    st.warning("⏳ 正在初始化首次預測數據，請稍候...")
    st.info("💡 請前往 GitHub 專案的 Actions 頁面點擊 'Run workflow'。")
else:
    try:
        st.success(f"📅 本日數據更新時間：{data.get('last_update', '未知')}")
        
        predictions = data.get("predictions", {})
        
        if not predictions:
            st.info("📅 今日暫無排定賽事，或系統正在等待雲端伺服器抓取最新賽程。")
        
        # 渲染對戰卡片
        for match_name, res in predictions.items():
            teams = match_name.split(" vs ")
            team_a_zh = TEAM_TRANSLATION.get(teams[0], teams[0])
            team_b_zh = TEAM_TRANSLATION.get(teams[1], teams[1])
            winner_zh = TEAM_TRANSLATION.get(res["winner"], res["winner"])
            
            with st.container():
                st.write(f"### ⚾ 賽事對決：{team_a_zh} VS {team_b_zh}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(label="🏆 預測勝方 (預估勝率)", value=winner_zh, delta=res["win_probability"])
                    st.metric(label="🚨 爆冷門機率", value=res["upset_prob"])
                with col2:
                    st.metric(label="🥇 第一高可能比分", value=res["most_likely"])
                    st.metric(label="🥈 第二高可能比分", value=res["second_likely"])
                with col3:
                    st.metric(label="📈 大小分預測", value=res["over_under"])
                
                st.write("---")
                
    except Exception as e:
        st.error(f"網頁渲染失敗，請確認 GitHub 端的數據是否已同步更新：{e}")
