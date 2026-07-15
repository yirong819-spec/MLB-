import streamlit as st
import json
import os

st.set_page_config(page_title="MLB 深度多因子大數據預測", layout="wide")

def load_prediction_data(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return None
    return None

st.title("🔮 2026 MLB 終極完全體智能預測系統")

data = load_prediction_data("latest_forecast.json")

if not data or "predictions" not in data or not data["predictions"]:
    st.warning("⏳ 正在初始化數據或無賽事預測數據，請稍候...")
else:
    predictions = data["predictions"]
    for match_full_key, res in predictions.items():
        # --- 防禦性讀取：確保數值不會傳入 None ---
        winner = res.get("winner") or "未定"
        win_prob = res.get("win_probability") or "50.0%"
        
        # 這裡就是你原本報錯的地方，加上了防禦
        upset_prob = res.get("upset_prob") if res.get("upset_prob") is not None else "0.0%"
        
        most_likely = res.get("most_likely") or "0 : 0"
        second_likely = res.get("second_likely") or "0 : 0"
        ou_line = res.get("ou_line") or "8.5"
        ou_rec = res.get("ou_recommend") or "未定"
        over_prob = res.get("over_prob") or "50.0%"
        under_prob = res.get("under_prob") or "50.0%"

        with st.container():
            st.markdown(f"### ⚾ 賽事：{match_full_key}")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(label="🏆 預測勝方", value=winner)
                st.metric(label="🚨 爆冷門機率", value=str(upset_prob))
            with col2:
                st.metric(label="🥇 第一高可能比分", value=str(most_likely))
                st.metric(label="🥈 第二高可能比分", value=str(second_likely))
            with col3:
                st.metric(label="📊 大小分盤口", value=f"{ou_line} 分")
                st.metric(label="🎯 預測傾向", value=str(ou_rec))
            with col4:
                st.metric(label="📈 大分出現機率", value=str(over_prob))
                st.metric(label="📉 小分出現機率", value=str(under_prob))
            st.write("---")
