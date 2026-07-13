import streamlit as st
import json
import os
import time

st.set_page_config(page_title="MLB 深度多因子大數據預測", layout="wide")

def load_prediction_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f: return json.load(f)
    return None

st.title("🔮 2026 MLB 終極完全體智能預測系統")
st.subheader("融合：實時左右打歷史分流、先發/牛棚獨立防禦率、球場幾何效應、莊家大眾資金修正之 50,000 次蒙地卡羅精算")

TEAM_TRANSLATION = {
    "Yankees": "紐約洋基", "Red Sox": "波士頓紅襪", "Rays": "坦帕灣光芒", "Blue Jays": "多倫多藍鳥", "Orioles": "巴爾地摩金鶯",
    "Guardians": "克里夫蘭守護者", "Twins": "明尼蘇達雙城", "Tigers": "底特律老虎", "White Sox": "芝加哥白襪", "Royals": "堪薩斯皇家",
    "Astros": "休士頓太空人", "Mariners": "西雅圖水手", "Rangers": "德州遊騎兵", "Angels": "洛杉磯天使", "Athletics": "奧克蘭運動家",
    "Dodgers": "洛杉磯道奇", "Braves": "亞特蘭大勇士", "Phillies": "費城費城人", "Mets": "紐約大都會", "Marlins": "邁阿密馬林魚", "Nationals": "華盛頓國民",
    "Brewers": "密爾瓦基釀酒人", "Cubs": "芝加哥小熊", "Reds": "辛辛那提紅人", "Pirates": "匹茲堡海盜", "Cardinals": "聖路易紅雀",
    "Giants": "舊金山巨人", "Padres": "聖地牙哥教士", "Diamondbacks": "亞利桑那響尾蛇", "Rockies": "科羅拉多洛磯"
}

if st.button("🔄 點我即時同步數據"):
    st.toast("🚀 正在重新加載最新大數據...", icon="⚡")
    time.sleep(0.3)
    st.rerun()

json_file = "latest_forecast.json"
data = load_prediction_data(json_file)

if data is None:
    st.warning("⏳ 正在初始化首次預測數據，請稍候...")
else:
    st.success(f"📅 本日數據更新時間：{data.get('last_update', '未知')}")
    predictions = data.get("predictions", {})
    
    if not predictions:
        st.info("📅 今日暫無排定賽事，系統維持保底展示。")
        
    for match_name, res in predictions.items():
        teams = match_name.split(" vs ")
        team_a_zh = TEAM_TRANSLATION.get(teams[0], teams[0])
        team_b_zh = TEAM_TRANSLATION.get(teams[1], teams[1])
        winner_zh = TEAM_TRANSLATION.get(res["winner"], res["winner"])
        
        with st.container():
            st.markdown(f"### ⚾ 賽事對決：`{team_a_zh}` (主) VS `{team_b_zh}` (客)")
            
            # 1. 核心預測數據網格
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(label="🏆 預測勝方 (勝率)", value=winner_zh, delta=res["win_probability"])
                st.metric(label="🚨 莊家去泡沫爆冷率", value=res.get("upset_prob", "0.0%"))
            with col2:
                st.metric(label="🥇 第一高可能比分", value=res["most_likely"])
                st.metric(label="🥈 第二高可能比分", value=res["second_likely"])
            with col3:
                st.metric(label="📊 大小分盤口線", value=f"{res.get('ou_line', '8.5')} 分")
                st.metric(label="🎯 預測傾向結果", value=res.get("ou_recommend", "未定"))
            with col4:
                st.metric(label="📈 大分出現總機率", value=res.get("over_prob", "50.0%"))
                st.metric(label="📉 小分出現總機率", value=res.get("under_prob", "50.0%"))
            
            # 2. 5大因子即時雲端戰報面版 (加上安全防呆機制)
            with st.expander("📊 查看此場比賽「5大核心因子」即時大數據戰報"):
                c1, c2, c3 = st.columns(3)
                
                # 🛠️【終極防呆防線】安全將可能為 None 或字串的資料轉為浮點數，防止網頁報錯崩潰
                try:
                    raw_weather_mod = float(res.get('report_weather', 1.0))
                except:
                    raw_weather_mod = 1.0
                    
                with c1:
                    st.write(f"🌤️ **天候環境**：{res.get('report_weather_info', '中立穩定')}")
                    st.write(f"📉 **天候疲勞倍率**：{raw_weather_mod:.2f}x")
                with c2:
                    st.write(f"🏟️ **球場幾何效應指數**：{res.get('report_park', 100)}")
                    st.write(f"🎨 **主場優勢加成**：已自動注入 +4.0%")
                with c3:
                    st.write(f"👤 **當日抗投左右對戰加權打擊率 (OPS)**")
                    st.write(f" - {team_a_zh} 打線：`{res.get('report_ops_a', 0.730)}`")
                    st.write(f" - {team_b_zh} 打線：`{res.get('report_ops_b', 0.730)}`")
                    
                st.caption(f"💡 *防守分流精算資訊：{team_a_zh} 先發 ERA `{res.get('report_p_era_a', 4.0)}` / 牛棚 `{res.get('report_b_era_a', 4.0)}` ｜ {team_b_zh} 先發 ERA `{res.get('report_p_era_b', 4.0)}` / 牛棚 `{res.get('report_b_era_b', 4.0)}`*")
            
            st.write("---")
