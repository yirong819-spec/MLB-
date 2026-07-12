import streamlit as st
import json
import os

st.set_page_config(page_title="MLB 深度多因子大數據預測", layout="wide")
st.title("🔮 2026 MLB 12大因子智能預測系統")
st.subheader("結合：攻防數據、歷史對決、年齡、傷病、戰術、心理、恩怨、莊家賠率之萬次蒙地卡羅分析")

# 隊伍英翻中字典
TEAM_TRANSLATION = {
    "Yankees": "紐約洋基",
    "Dodgers": "洛杉磯道奇"
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
        
        for match_name, res in predictions.items():
            # 翻譯隊伍名
            teams = match_name.split(" vs ")
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
        st.error(f"網頁渲染失敗，可能 JSON 格式未完全同步：{e}")
