from datetime import datetime, timedelta

class ChurchSchoolSystem:
    def __init__(self):
        # 設定班別基準時間
        self.shift_times = {
            "早班": datetime.strptime("09:30", "%H:%M").time(),
            "晚班": datetime.strptime("19:30", "%H:%M").time()
        }
        # 班級列表
        self.classes = ["門上", "門下", "服上", "服下"]

    def calculate_checkin_score(self, shift, checkin_time_str):
        """計算報到分數"""
        target_time = self.shift_times.get(shift)
        checkin_time = datetime.strptime(checkin_time_str, "%H:%M").time()
        
        # 為了計算時間差，將其轉換為 datetime 物件（假設為同一天）
        dummy_date = datetime.today()
        target_dt = datetime.combine(dummy_date, target_time)
        checkin_dt = datetime.combine(dummy_date, checkin_time)
        
        # 計算遲到分鐘數
        delay_minutes = (checkin_dt - target_dt).total_seconds() / 60
        
        if delay_minutes <= 20: # 包含提早到、準時、遲到20分內
            return 5, max(0, delay_minutes)
        elif delay_minutes <= 40:
            return 3, delay_minutes
        else:
            return 0, delay_minutes

    def calculate_weekly_score(self, data):
        """
        計算學員單週總分
        data 範例: 
        {
            "name": "張三", "class_group": "門上", "shift": "早班", 
            "checkin_time": "09:45", "devotional_days": 5, 
            "read_material": True, "sunday_worship": True, "cell_group": False
        }
        """
        # 1. 計算報到分數
        checkin_score, delay = self.calculate_checkin_score(data["shift"], data["checkin_time"])
        
        # 2. 計算問卷分數
        devotional_score = min(data.get("devotional_days", 0), 7) # 每天1分，最多7分
        material_score = 5 if data.get("read_material", False) else 0
        worship_score = 1 if data.get("sunday_worship", False) else 0
        cell_group_score = 1 if data.get("cell_group", False) else 0
        
        task_score = devotional_score + material_score + worship_score + cell_group_score
        
        # 3. 加總
        total_score = checkin_score + task_score
        
        return {
            "學員": data["name"],
            "班別": f'{data["class_group"]} - {data["shift"]}',
            "遲到分鐘數": int(delay) if delay > 0 else 0,
            "報到得分": checkin_score,
            "任務得分": task_score,
            "本週總分": total_score
        }

# ================= 測試執行 =================
if __name__ == "__main__":
    system = ChurchSchoolSystem()
    
    # 模擬一位學生：門上早班，09:45報到 (遲到15分 -> 5分)，靈修5天，有讀教材，有主日，無小組
    student_a = {
        "name": "約翰",
        "class_group": "門上",
        "shift": "早班",
        "checkin_time": "09:45",
        "devotional_days": 5,
        "read_material": True,
        "sunday_worship": True,
        "cell_group": False
    }
    
    # 模擬另一位學生：服下晚班，20:05報到 (遲到35分 -> 3分)，靈修7天，無教材，有主日，有小組
    student_b = {
        "name": "瑪麗",
        "class_group": "服下",
        "shift": "晚班",
        "checkin_time": "20:05",
        "devotional_days": 7,
        "read_material": False,
        "sunday_worship": True,
        "cell_group": True
    }

    print(system.calculate_weekly_score(student_a))
    # 預期總分: 5(報到) + 5(靈修) + 5(教材) + 1(主日) + 0(小組) = 16分
    
    print(system.calculate_weekly_score(student_b))
    # 預期總分: 3(報到) + 7(靈修) + 0(教材) + 1(主日) + 1(小組) = 12分