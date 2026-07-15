import streamlit as st
import json, os

st.set_page_config(page_title="MLB 預測系統", layout="wide")
st.title("⚾ 2026 MLB 終極預測系統")

def load_data():
    if os.path.exists("latest_forecast.json"):
        with open("latest_forecast.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return None

data = load_data()
if data and "predictions" in data:
    for match, res in data["predictions"].items():
        st.markdown(f"### 🏟️ {match}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🏆 勝方 (勝率)", res["winner"], res["win_probability"])
        c1.metric("🚨 爆冷機率", str(res.get("upset_prob", "0%")))
        c2.metric("🥇 預測比分", res["most_likely"])
        c2.metric("🥈 次要比分", res["second_likely"])
        c3.metric("📊 盤口", f"{res['ou_line']} 分")
        c3.metric("🎯 推薦", res["ou_recommend"])
        c4.metric("📈 大分機率", res["over_prob"])
        c4.metric("📉 小分機率", res["under_prob"])
        st.write("---")
else:
    st.warning("⏳ 正在等待數據更新...")
