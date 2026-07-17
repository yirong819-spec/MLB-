import streamlit as st
import json, os

# 1. 頁面配置設定
st.set_page_config(page_title="MLB 預測系統", layout="wide")

# 2. 定義資料讀取函數 (確保在呼叫前已定義)
def load_data():
    file_path = "latest_forecast.json"
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"檔案讀取錯誤: {e}")
            return None
    return None

# 3. 標題
st.title("🔮 2026 MLB 終極完全體智能預測系統")

# 4. 執行讀取
data = load_data()

# 5. 渲染邏輯
if data and "predictions" in data and len(data["predictions"]) > 0:
    predictions = data["predictions"]
    st.write(f"最後更新時間: {data.get('last_update', '未知')}")
    
    for match_name, res in predictions.items():
        with st.container():
            st.markdown(f"### ⚾ 賽事：{match_name}")
            col1, col2, col3, col4 = st.columns(4)
            
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
    st.warning("⏳ 目前暫無賽事數據，請檢查系統狀態。")
