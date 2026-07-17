import streamlit as st
import json, os

st.set_page_config(page_title="MLB 終極分析", layout="wide")
st.title("🔮 2026 MLB 終極完全體智能預測系統")

def load_data():
    if os.path.exists("latest_forecast.json"):
        with open("latest_forecast.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return None

data = load_data()

if data and "predictions" in data and data["predictions"]:
    st.write(f"最後更新: {data.get('last_update')}")
    for match, res in data["predictions"].items():
        with st.container():
            st.markdown(f"### ⚾ {match}")
            c1, c2, c3 = st.columns(3)
            c1.metric("🏆 勝隊", res["winner"], f"{res['win_probability']}")
            c2.metric("🥇 比分預測", res["most_likely"])
            c3.metric("🎯 推薦", res["ou_recommend"])
            st.divider()
else:
    st.warning("⏳ 系統待機中：等待今日 API 數據更新...")
