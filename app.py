import streamlit as st
import json
import os

st.set_page_config(page_title="MLB 深度多因子大數據預測", layout="wide")

def load_prediction_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return None
    return None

st.title("🔮 2026 MLB 終極完全體智能預測系統")

data = load_prediction_data("latest_forecast.json")

if data is None or "predictions" not in data or not data["predictions"]:
    st.warning("⏳ 正在初始化數據或數據載入中，請稍候...")
else:
    predictions = data["predictions"]
    for match_full_key, res in predictions.items():
        # 安全取得數據，防止 Key 不存在或值為 None
        winner = res.get("winner", "未定")
        win_prob = res.get("win_probability", "50.0%")
        upset_prob = res.get("upset_prob", "0.0%")
        most_likely = res.get("most_likely", "0 : 0")
        second_likely = res.get("second_likely", "0 : 0")
        ou_line = res.get("ou_line", "8.5")
        ou_rec = res.get("ou_recommend", "未定")
        over_prob = res.get("over_prob", "50.0%")
        under_prob = res.get("under_prob", "50.0%")

        with st.container():
            st.markdown(f"### ⚾ 賽事：{match_full_key}")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(label="🏆 預測勝方", value=winner)
                st.metric(label="🚨 爆冷門機率", value=upset_prob)
            with col2:
                st.metric(label="🥇 第一高可能比分", value=most_likely)
                st.metric(label="🥈 第二高可能比分", value=second_likely)
            with col3:
                st.metric(label="📊 大小分盤口", value=f"{ou_line} 分")
                st.metric(label="🎯 預測傾向", value=ou_rec)
            with col4:
                st.metric(label="📈 大分出現機率", value=over_prob)
                st.metric(label="📉 小分出現機率", value=under_prob)
            st.write("---")
