# app.py 保持你目前的結構，但增加一點過期提醒
import streamlit as st
import json, os
from datetime import datetime

# ... (你的原設定與 load_data 函數) ...

data = load_data()
st.title("🔮 2026 MLB 終極完全體智能預測系統")

if data and data.get("predictions"):
    st.write(f"最後更新時間: {data.get('last_update', '未知')}")
    # ... (你的原本 for 迴圈邏輯) ...
else:
    st.warning("⚠️ 目前無賽事數據，請檢查 API 連結狀態或是否處於無賽程日。")
