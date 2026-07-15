import streamlit as st
import json, os

st.set_page_config(page_title="MLB 預測系統", layout="wide")
st.title("🔮 2026 MLB 終極完全體智能預測系統")

def load_data():
    if os.path.exists("latest_forecast.json"):
        try:
            with open("latest_forecast.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return None
    return None

data = load_data()

# --- 核心修正：自動遍歷所有賽事 ---
if data and "predictions" in data and len(data["predictions"]) > 0:
    predictions = data["predictions"]
    
    # 動態產生每一個比賽的容器
    for match_name, res in predictions.items():
        with st.container():
            st.markdown(f"### ⚾ 賽事：{match_name}")
            col1, col2, col3, col4 = st.columns(4)
            
            # 使用 .get() 確保不會因為缺欄位而崩潰
            col1.metric("🏆 預測勝方", res.get("winner", "未定"))
            col1.metric("🚨 爆冷門機率", res.get("upset_prob", "0%"))
            
            col2.metric("🥇 第一可能比分", res.get("most_likely", "0:0"))
            col2.metric("🥈 第二可能比分", res.get("second_likely", "0:0"))
            
            col3.metric("📊 大小分盤口", f"{res.get('ou_line', '8.5')} 分")
            col3.metric("🎯 推薦方向", res.get("ou_recommend", "無"))
            
            col4.metric("📈 大分機率", res.get("over_prob", "50%"))
            col4.metric("📉 小分機率", res.get("under_prob", "50%"))
            
            st.write("---")
else:
    st.warning("⏳ 目前沒有賽事數據，請檢查 GitHub Action 執行狀態。")
