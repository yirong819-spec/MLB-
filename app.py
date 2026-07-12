import streamlit as st
import json
import os

st.set_page_config(page_title="MLB 深度多因子大數據預測", layout="wide")
st.title("🔮 2026 MLB 12大因子智能預測系統")
st.subheader("結合：攻防數據、歷史對決、年齡、傷病、戰術、心理、恩怨、莊家賠率之萬次蒙地卡羅分析")

# 【核心修復】補齊 MLB 全聯盟 30 支球隊的英翻中字典，確保所有比賽都能正常顯示！
TEAM_TRANSLATION = {
    # 美國聯盟東區
    "Yankees": "紐約洋基",
    "Red Sox": "波士頓紅襪",
    "Rays": "坦帕灣光芒",
    "Blue Jays": "多倫多藍鳥",
    "Orioles": "巴爾地摩金鶯",
    # 美國聯盟中區
    "Guardians": "克里夫蘭守護者",
    "Twins": "明尼蘇達雙城",
    "Tigers": "底特律老虎",
    "White Sox": "芝加哥白襪",
    "Royals": "堪薩斯皇家",
    # 美國聯盟西區
    "Astros": "休士頓太空人",
    "Mariners": "西雅圖水手",
    "Rangers": "德州遊騎兵",
    "Angels": "洛杉磯天使",
    "Athletics": "奧克蘭運動家",
    
    # 國家聯盟東區
    "Dodgers": "洛杉磯道奇",
    "Braves": "亞特蘭大勇士",
    "Phillies": "費城費城人",
    "Mets": "紐約大都會",
    "Marlins": "邁阿密馬林魚",
    "Nationals": "華盛頓國民",
    # 國家聯盟中區
    "Brewers": "密爾瓦基釀酒人",
    "Cubs": "芝加哥小熊",
    "Reds": "辛辛那提紅人",
    "Pirates": "匹茲堡海盜",
    "Cardinals": "聖路易紅雀",
    # 國家聯盟西區
    "Giants": "舊金山巨人",
    "Padres": "聖地牙哥教士",
    "Diamondbacks": "亞利桑那響尾蛇",
    "Rockies": "科羅拉多洛磯"
}

if not os.path.exists("latest_forecast.json"):
    st.warning("⏳ 正在初始化首次預測數據，請稍候...")
    st.info("💡 請前往 GitHub 專案的 Actions 頁面點擊 'Run workflow'。")
else:
    try:
        with open("latest_forecast.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        st.success(f"📅 本日數據更新時間：{data.get('last_update', '未知')}")
        
        predictions = data.get("predictions", {})
        
        if not predictions:
            st.info("📅 今日暫無排定賽事，或系統正在等待雲端伺服器抓取最新賽程。")
        
        for match_name, res in predictions.items():
            # 分割對決名稱（例如 "Dodgers vs Yankees"）
            teams = match_name.split(" vs ")
            
            # 安全防護：如果在字典找不到中文，就直接顯示原本的英文名稱（.get 的第二個參數 x 意為找不到就用原本的名字）
            team_a_zh = TEAM_TRANSLATION.get(teams[0], teams[0])
            team_b_zh = TEAM_TRANSLATION.get(teams[1], teams[1])
            winner_zh = TEAM_TRANSLATION.get(res["winner"], res["winner"])
            
            # 用精美卡片展示每場比賽的五大結果
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
