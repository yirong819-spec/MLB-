import streamlit as st
import json
import pandas as pd
import os

st.set_page_config(page_title="MLB 季後賽預測", layout="wide")
st.title("🏆 2026 MLB 季後賽自動預測系統")

if not os.path.exists("latest_forecast.json"):
    st.warning("⏳ 正在初始化首次預測數據，請稍候...")
    st.info("💡 請前往 GitHub 專案的 Actions 頁面點擊 'Run workflow' 產生初始數據。")
else:
    try:
        with open("latest_forecast.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        st.success(f"📅 本日數據更新時間：{data.get('last_update', '未知')}")
        
        df = pd.DataFrame(list(data.get("probabilities", {}).items()), columns=["球隊", "奪冠機率"])
        df = df.sort_values(by="奪冠機率", ascending=False).reset_index(drop=True)
        df["奪冠機率%"] = df["奪冠機率"].map(lambda x: f"{x:.2%}")
        
        st.write("### 📊 世界大賽奪冠機率排行")
        st.dataframe(df[["球隊", "奪冠機率%"]], use_container_width=True)
        st.write("### 📈 預測勝率圖表")
        st.bar_chart(data=df, x="球隊", y="奪冠機率", use_container_width=True)
    except Exception as e:
        st.error(f"讀取數據失敗：{e}")
