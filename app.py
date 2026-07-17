import streamlit as st
import json, os

st.set_page_config(page_title="MLB 終極分析系統", layout="wide")

st.title("⚾ 2026 MLB 終極完全體分析系統")
st.markdown("---")

def load_data():
    if os.path.exists("latest_forecast.json"):
        with open("latest_forecast.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return None

data = load_data()

if data:
    st.write(f"📊 **最後更新時間**: {data.get('last_update')}")
    
    # 將比賽結果分為三欄並排顯示
    predictions = data.get("predictions", {})
    cols = st.columns(3)
    
    for i, (match, res) in enumerate(predictions.items()):
        with cols[i % 3]:
            st.markdown(f"### 🏟️ {match}")
            st.metric("📈 預測勝率", res["勝率"])
            st.success(f"💡 戰術建議: {res['建議']}")
            # 可以在此擴充：顯示比分預測或大小分建議
            st.divider()
else:
    st.info("⏳ 系統正在進行 10 萬次模擬計算，請稍候並刷新頁面...")
