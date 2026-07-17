import streamlit as st
import json, os

st.set_page_config(page_title="MLB 終極分析", layout="wide")
st.title("⚾ 2026 MLB 終極完全體分析系統")

def load_data():
    if os.path.exists("latest_forecast.json"):
        with open("latest_forecast.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return None

data = load_data()

if data and "predictions" in data and data["predictions"]:
    st.write(f"最後更新: {data.get('last_update')}")
    
    # 遍歷新格式的數據
    for match, res in data["predictions"].items():
        with st.container():
            st.markdown(f"### 🏟️ {match}")
            c1, c2 = st.columns(2)
            
            # 使用修正後的欄位名稱：對應 fetch_and_run.py 中的 "勝率" 和 "建議"
            c1.metric("📊 預測勝率", res["勝率"])
            c2.metric("💡 戰術建議", res["建議"])
            st.divider()
else:
    st.warning("⏳ 數據正在進行 10 萬次模擬計算中，請稍候...")
