import streamlit as st
from datetime import datetime

# --- 核心計分邏輯 (與原本相同) ---
class ChurchSchoolSystem:
    def __init__(self):
        self.shift_times = {
            "早班": datetime.strptime("09:30", "%H:%M").time(),
            "晚班": datetime.strptime("19:30", "%H:%M").time()
        }
        self.classes = ["門上", "門下", "服上", "服下"]

    def calculate_checkin_score(self, shift, checkin_time):
        target_time = self.shift_times.get(shift)
        
        dummy_date = datetime.today()
        target_dt = datetime.combine(dummy_date, target_time)
        checkin_dt = datetime.combine(dummy_date, checkin_time)
        
        delay_minutes = (checkin_dt - target_dt).total_seconds() / 60
        
        if delay_minutes <= 20:
            return 5, max(0, delay_minutes)
        elif delay_minutes <= 40:
            return 3, delay_minutes
        else:
            return 0, delay_minutes

    def calculate_weekly_score(self, data):
        checkin_score, delay = self.calculate_checkin_score(data["shift"], data["checkin_time"])
        
        devotional_score = min(data.get("devotional_days", 0), 7)
        material_score = 5 if data.get("read_material", False) else 0
        worship_score = 1 if data.get("sunday_worship", False) else 0
        cell_group_score = 1 if data.get("cell_group", False) else 0
        
        task_score = devotional_score + material_score + worship_score + cell_group_score
        total_score = checkin_score + task_score
        
        return {
            "遲到分鐘數": int(delay) if delay > 0 else 0,
            "報到得分": checkin_score,
            "任務得分": task_score,
            "本週總分": total_score
        }

# --- 網頁介面 (Streamlit) ---
system = ChurchSchoolSystem()

st.title("⛪ 教會學校報到系統")
st.write("請填寫以下資訊完成本週報到與計分。")

# 建立表單
with st.form("checkin_form"):
    name = st.text_input("學員姓名")
    
    col1, col2 = st.columns(2)
    with col1:
        class_group = st.selectbox("班級組別", system.classes)
    with col2:
        shift = st.selectbox("班別", ["早班", "晚班"])
        
    checkin_time = st.time_input("現在報到時間")
    
    st.markdown("### 📝 本週任務回報")
    devotional_days = st.slider("每日靈修天數 (天)", 0, 7, 0)
    read_material = st.checkbox("有閱讀指定教材")
    sunday_worship = st.checkbox("有參加主日崇拜")
    cell_group = st.checkbox("有參加週末小組聚會")
    
    # 提交按鈕
    submitted = st.form_submit_button("送出報到並計算成績")

# 按下按鈕後的動作
if submitted:
    if not name:
        st.warning("請輸入姓名喔！")
    else:
        # 整理資料送入系統計算
        student_data = {
            "name": name,
            "class_group": class_group,
            "shift": shift,
            "checkin_time": checkin_time,
            "devotional_days": devotional_days,
            "read_material": read_material,
            "sunday_worship": sunday_worship,
            "cell_group": cell_group
        }
        
        result = system.calculate_weekly_score(student_data)
        
        # 顯示結果
        st.success(f"🎉 報到成功！ {name} ({class_group}-{shift})")
        
        col_res1, col_res2, col_res3, col_res4 = st.columns(4)
        col_res1.metric("遲到時間", f"{result['遲到分鐘數']} 分鐘")
        col_res2.metric("報到得分", result['報到得分'])
        col_res3.metric("任務得分", result['任務得分'])
        col_res4.metric("🏆 本週總分", result['本週總分'])
