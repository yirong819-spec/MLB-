import streamlit as st
import json, os

st.set_page_config(page_title="MLB 專業模擬分析", layout="wide")
st.title("⚾ 2026 MLB 專家級戰術模擬系統")

def load_data():
    if os.path.exists("latest_forecast.json"):
        with open("latest_forecast.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return None

data = load_data()

if data and "predictions" in data:
    st.write(f"📊 **最後更新**: {data.get('last_update')}")
    
    # 遍歷所有比賽預測
    for match, res in data["predictions"].items():
        with st.container():
            st.markdown(f"### 🏟️ {match}")
            c1, c2, c3, c4 = st.columns(4)
            
            # 使用正確的 Key：勝率、最可能比分、錯誤率、戰術分析
            c1.metric("📈 預測勝率", res["勝率"])
            c2.metric("🎯 最可能比分", res["最可能比分"])
            c3.metric("⚠️ 預測錯誤率", res["錯誤率"])
            c4.info(f"戰術分析\n\n{res['戰術分析']}")
            
            st.divider()
else:
    st.warning("⏳ 系統正在進行 10 萬次模擬，請稍候重整...")
