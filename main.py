import asyncio
import io
import json
import os
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

import flet as ft

# =========================================================
# THEME & CONFIGURATION
# =========================================================

# Theme Colors
PAGE_BG = "#0B0D12"
BG = "#0F1115"
CARD = "#151C2C"
CARD2 = "#1B2437"
CARD3 = "#222C40"

ACCENT = "#12E3B5"
ACCENT2 = "#0FD1A3"
BLUE = "#5DAEFF"
ORANGE = "#FFB84D"
RED = "#FF5C70"
GREEN = "#79D98A"
PURPLE = "#9C7DFF"

TEXT = "#FFFFFF"
SUB = "#9CA3AF"
MUTED = "#7C8596"

DB_FILE = "healthify_db.json"
GEMINI_MODEL = "gemini-2.5-flash"

# Global Language State
LANG = "ar"

TRANSLATIONS = {
    "ar": {
        "dashboard": "الرئيسية",
        "meals": "الوجبات",
        "workout": "التمارين",
        "analysis": "تحليل AI",
        "stats": "الإحصائيات",
        "profile": "الملف",
        "welcome": "مرحباً بك في Healthify",
        "welcome_sub": "صحة ذكية، تصميم فاخر، وتحليل مدعوم بالذكاء الاصطناعي",
        "today_summary": "ملخصك الصحي اليومي",
        "quick_actions": "اختصارات سريعة",
        "water": "شرب الماء",
        "today_workout": "تمرين اليوم",
        "smart_tip": "نصيحة ذكية",
        "generate_plan": "إنشاء الخطة",
        "name": "الاسم",
        "age": "العمر",
        "gender": "الجنس",
        "height": "الطول (سم)",
        "weight": "الوزن (كجم)",
        "activity": "مستوى النشاط",
        "goal": "الهدف",
        "api_key": "مفتاح Gemini API (اختياري)",
        "lose_weight": "تنحيف",
        "maintain": "تثبيت",
        "gain_weight": "زيادة وزن",
        "save_profile": "حفظ الملف",
        "dashboard_title": "لوحة المتابعة",
        "dashboard_sub": "مؤشراتك اليومية وملخصك الصحي",
        "daily_macros": "الماكروز اليومية",
        "daily_target": "الهدف اليومي",
        "meal_plan": "خطة الوجبات",
        "nutrition_smart": "التغذية الذكية",
        "daily_nutrition_target": "الهدف الغذائي اليومي",
        "weekly_workout": "جدول التمارين الأسبوعي",
        "weekly_summary": "روتين أسبوعي متوازن بين الكارديو والقوة والراحة",
        "food_analysis": "تحليل الطعام بالذكاء الاصطناعي",
        "analysis_ready": "جاهز للتحليل بالذكاء الاصطناعي",
        "pick_image": "اختيار صورة",
        "analyze": "تحليل الصورة",
        "analysis_result": "نتيجة التحليل",
        "health_score": "الدرجة الصحية",
        "stats_title": "الإحصائيات",
        "stats_sub": "تابع التقدم والالتزام",
        "profile_title": "الملف الشخصي",
        "profile_sub": "عدّل البيانات واحفظها",
        "change_lang": "EN",
        "camera_hint": "اضغط لاختيار صورة الطعام",
        "choose_image": "اختيار صورة",
        "ai_missing": "تحليل تجريبي. أضف مفتاح API في الملف الشخصي لتحليل حقيقي.",
        "ai_ready_msg": "جاهز! سيتم استخدام الذكاء الاصطناعي لتحليل الوجبة.",
        "analysis_error": "حدث خطأ أثناء التحليل",
        "missing_pillow": "تعذر التحليل: مكتبة Pillow غير مثبتة.",
        "current_snapshot": "الملخص الحالي",
        "achievements": "الإنجازات",
        "weight_history": "سجل الوزن",
        "calories_history": "سجل السعرات",
        "current_age": "العمر",
        "current_weight": "الوزن",
        "current_height": "الطول",
        "current_goal": "الهدف الحالي",
        "adherence": "الالتزام",
        "active_days": "أيام النشاط",
        "streak": "سلسلة",
        "workouts_logged": "التمارين",
        "meals_logged": "الوجبات المسجلة",
        "bmi": "BMI",
        "calories": "السعرات",
        "protein": "البروتين",
        "carbs": "الكارب",
        "fat": "الدهون",
        "male": "ذكر",
        "female": "أنثى",
        "sedentary": "خامل",
        "light": "خفيف",
        "moderate": "متوسط",
        "active": "نشط",
        "very_active": "نشط جداً",
        "easy": "سهل",
        "medium": "متوسط",
        "hard": "صعب",
        "day": "اليوم",
        "analyzing": "جارٍ التحليل...",
        "heart_rate": "النبض",
        "sleep": "النوم",
    },
    "en": {
        "dashboard": "Dashboard",
        "meals": "Meals",
        "workout": "Workout",
        "analysis": "AI Analysis",
        "stats": "Stats",
        "profile": "Profile",
        "welcome": "Welcome to Healthify",
        "welcome_sub": "Smart health, premium design, AI analysis",
        "today_summary": "Your daily health summary",
        "quick_actions": "Quick Actions",
        "water": "Water Intake",
        "today_workout": "Today's Workout",
        "smart_tip": "Smart Tip",
        "generate_plan": "Generate My Plan",
        "name": "Name",
        "age": "Age",
        "gender": "Gender",
        "height": "Height (cm)",
        "weight": "Weight (kg)",
        "activity": "Activity Level",
        "goal": "Goal",
        "api_key": "Gemini API Key (Optional)",
        "lose_weight": "Lose Weight",
        "maintain": "Maintain",
        "gain_weight": "Gain Weight",
        "save_profile": "Save Profile",
        "dashboard_title": "Dashboard",
        "dashboard_sub": "Your daily health summary",
        "daily_macros": "Daily Macros",
        "daily_target": "Daily Target",
        "meal_plan": "Meal Plan",
        "nutrition_smart": "Smart Nutrition",
        "daily_nutrition_target": "Daily Nutrition Target",
        "weekly_workout": "Weekly Workout",
        "weekly_summary": "Balanced weekly routine with cardio, strength, and recovery",
        "food_analysis": "AI Food Analysis",
        "analysis_ready": "Ready for AI-powered analysis",
        "pick_image": "Pick Image",
        "analyze": "Analyze Image",
        "analysis_result": "Analysis Result",
        "health_score": "Health Score",
        "stats_title": "Stats",
        "stats_sub": "Track your consistency and progress",
        "profile_title": "Profile",
        "profile_sub": "Edit and save your settings",
        "change_lang": "عربي",
        "camera_hint": "Tap to choose a food photo",
        "choose_image": "Choose Image",
        "ai_missing": "Mock analysis. Add API Key in Profile for real AI.",
        "ai_ready_msg": "Ready! AI will be used to analyze this meal.",
        "analysis_error": "Error during analysis",
        "missing_pillow": "Pillow library missing.",
        "current_snapshot": "Current Snapshot",
        "achievements": "Achievements",
        "weight_history": "Weight History",
        "calories_history": "Calories History",
        "current_age": "Age",
        "current_weight": "Weight",
        "current_height": "Height",
        "current_goal": "Current Goal",
        "adherence": "Adherence",
        "active_days": "Active Days",
        "streak": "Streak",
        "workouts_logged": "Workouts",
        "meals_logged": "Meals Logged",
        "bmi": "BMI",
        "calories": "Calories",
        "protein": "Protein",
        "carbs": "Carbs",
        "fat": "Fat",
        "male": "Male",
        "female": "Female",
        "sedentary": "Sedentary",
        "light": "Light",
        "moderate": "Moderate",
        "active": "Active",
        "very_active": "Very Active",
        "easy": "Easy",
        "medium": "Medium",
        "hard": "Hard",
        "day": "Day",
        "analyzing": "Analyzing...",
        "heart_rate": "Heart Rate",
        "sleep": "Sleep",
    },
}

def t(key: str) -> str:
    return TRANSLATIONS.get(LANG, TRANSLATIONS["en"]).get(key, key)

def safe_int(val: Any, default: int) -> int:
    try: return int(float(val))
    except (ValueError, TypeError): return default

def safe_float(val: Any, default: float) -> float:
    try: return float(val)
    except (ValueError, TypeError): return default

def toggle_language(page: ft.Page):
    """Safely toggles the language and triggers a full page rebuild with RTL support."""
    global LANG
    LANG = "en" if LANG == "ar" else "ar"
    page.rtl = (LANG == "ar")
    current = page.route or "/dashboard"
    page.route = "/_refresh" 
    page.update()
    page.go(current)

# =========================================================
# MODEL / STORAGE
# =========================================================
@dataclass
class UserProfile:
    name: str = ""
    age: int = 25
    gender: str = "Male"
    height: float = 170.0
    weight: float = 70.0
    activity_level: str = "Moderate"
    goal: str = "Maintain"
    api_key: str = "AIzaSyAAGfzm8M0PUW9xZCf8FUbKJnSw19buePA"
    is_setup: bool = False

def default_db() -> Dict[str, Any]:
    return {
        "user": asdict(UserProfile()),
        "weight_history": [],
        "calorie_history": [],
        "last_meal_plan": [],
        "last_workout_plan": [],
        "last_analysis": {},
    }

def load_db() -> Dict[str, Any]:
    if not os.path.exists(DB_FILE):
        return default_db()
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            db = json.load(f)
        if not isinstance(db, dict): return default_db()
    except Exception:
        return default_db()
    base = default_db()
    base.update(db)
    return base

def save_db(db: Dict[str, Any]) -> None:
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def load_user() -> UserProfile:
    try:
        return UserProfile(**load_db().get("user", asdict(UserProfile())))
    except Exception:
        return UserProfile()

def save_user(user: UserProfile) -> None:
    db = load_db()
    db["user"] = asdict(user)
    hist = db.setdefault("weight_history", [])
    hist.append({"day": datetime.now().strftime("%a"), "weight": float(user.weight)})
    db["weight_history"] = hist[-14:]
    save_db(db)

def save_analysis(result: Dict[str, Any]) -> None:
    db = load_db()
    db["last_analysis"] = result
    save_db(db)

def save_meals(meals: List[Dict[str, Any]]) -> None:
    db = load_db()
    db["last_meal_plan"] = meals
    save_db(db)

def save_workouts(workouts: List[Dict[str, Any]]) -> None:
    db = load_db()
    db["last_workout_plan"] = workouts
    save_db(db)

# =========================================================
# HEALTH LOGIC
# =========================================================
def normalize_gender(value: Optional[str]) -> str:
    return "Male" if value in ("Male", "ذكر") else "Female"

def normalize_activity(value: Optional[str]) -> str:
    mapping = {
        "Sedentary": "Sedentary", "خامل": "Sedentary",
        "Light": "Light", "خفيف": "Light",
        "Moderate": "Moderate", "متوسط": "Moderate",
        "Active": "Active", "نشط": "Active",
        "Very Active": "Very Active", "نشط جداً": "Very Active",
    }
    return mapping.get(value, "Moderate")

def normalize_goal(value: Optional[str]) -> str:
    mapping = {
        "Lose Weight": "Lose Weight", "تنحيف": "Lose Weight",
        "Maintain": "Maintain", "تثبيت": "Maintain",
        "Gain Weight": "Gain Weight", "زيادة وزن": "Gain Weight",
    }
    return mapping.get(value, "Maintain")

def calculate_metrics(user: UserProfile) -> Dict[str, Any]:
    h_m = max(user.height / 100.0, 0.01)
    bmi = round(user.weight / (h_m ** 2), 1)

    if bmi < 18.5: bmi_status = "Underweight"
    elif bmi < 25: bmi_status = "Normal"
    elif bmi < 30: bmi_status = "Overweight"
    else: bmi_status = "Obese"

    if user.gender == "Male":
        bmr = (10 * user.weight) + (6.25 * user.height) - (5 * user.age) + 5
    else:
        bmr = (10 * user.weight) + (6.25 * user.height) - (5 * user.age) - 161

    activity = {"Sedentary": 1.2, "Light": 1.375, "Moderate": 1.55, "Active": 1.725, "Very Active": 1.9}
    tdee = bmr * activity.get(user.activity_level, 1.55)

    if user.goal == "Lose Weight": target = tdee - 500
    elif user.goal == "Gain Weight": target = tdee + 300
    else: target = tdee

    target = int(max(target, 1200)) # Prevent dangerously low calories
    protein = int((target * 0.30) / 4)
    carbs = int((target * 0.40) / 4)
    fats = int((target * 0.30) / 9)

    return {
        "bmi": bmi, "bmi_status": bmi_status,
        "bmr": int(bmr), "tdee": int(tdee),
        "target_calories": target,
        "protein": protein, "carbs": carbs, "fats": fats,
    }

def health_tip(metrics: Dict[str, Any], goal: str) -> str:
    if LANG == "ar":
        if metrics["bmi_status"] == "Underweight": return "ارفع السعرات تدريجياً وركّز على البروتين عالي الجودة."
        if metrics["bmi_status"] in ("Overweight", "Obese"): return "قلل الأطعمة المصنعة وأضف كارديو يومياً لنتائج أسرع."
        if goal == "Lose Weight": return "تحكم في الحصص وابدأ وجبتك دائماً بالخضار والبروتين."
        if goal == "Gain Weight": return "استخدم أطعمة عالية الكثافة (مكسرات، زبدة الفول) مع تمارين المقاومة."
        return "حافظ على روتين ثابت يشمل النوم 7 ساعات، شرب الماء، والتوازن الغذائي."
    else:
        if metrics["bmi_status"] == "Underweight": return "Increase calories gradually and focus on high-quality protein."
        if metrics["bmi_status"] in ("Overweight", "Obese"): return "Reduce ultra-processed foods and add daily cardio."
        if goal == "Lose Weight": return "Keep portions controlled and prioritize lean protein first."
        if goal == "Gain Weight": return "Use calorie-dense healthy meals (nuts, peanut butter) and strength training."
        return "Maintain consistency with 7 hours of sleep, water intake, and nutritional balance."

def meal_plan_for(user: UserProfile, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
    cal = metrics["target_calories"]
    if user.goal == "Lose Weight":
        return [
            {"type": "Breakfast" if LANG=="en" else "الفطور", "name": "Greek Yogurt & Berries" if LANG == "en" else "زبادي يوناني وتوت", "cal": int(cal * 0.22), "desc": "High protein and light carbs." if LANG == "en" else "بروتين عالي وكارب خفيف، مثالي للصباح.", "img": "https://images.unsplash.com/photo-1490645935967-10de6ba17061?q=80&w=1200&auto=format&fit=crop"},
            {"type": "Lunch" if LANG=="en" else "الغداء", "name": "Grilled Chicken Salad" if LANG == "en" else "سلطة دجاج مشوي", "cal": int(cal * 0.30), "desc": "Lean protein with fiber." if LANG == "en" else "بروتين خفيف مع ألياف تملأ المعدة.", "img": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?q=80&w=1200&auto=format&fit=crop"},
            {"type": "Dinner" if LANG=="en" else "العشاء", "name": "Salmon & Vegetables" if LANG == "en" else "سلمون وخضار", "cal": int(cal * 0.30), "desc": "Omega-3 fats and balanced finish." if LANG == "en" else "دهون مفيدة (أوميغا 3) وتوازن ممتاز.", "img": "https://images.unsplash.com/photo-1467003909585-2f8a72700288?q=80&w=1200&auto=format&fit=crop"},
            {"type": "Snack" if LANG=="en" else "سناك", "name": "Apple & Almonds" if LANG == "en" else "تفاح ولوز", "cal": int(cal * 0.18), "desc": "Light snack to control hunger." if LANG == "en" else "سناك خفيف لتقليل الشعور بالجوع.", "img": "https://images.unsplash.com/photo-1498837167922-ddd27525d352?q=80&w=1200&auto=format&fit=crop"},
        ]
    if user.goal == "Gain Weight":
        return [
            {"type": "Breakfast" if LANG=="en" else "الفطور", "name": "Oatmeal, PB & Banana" if LANG == "en" else "شوفان وزبدة الفول السوداني والموز", "cal": int(cal * 0.26), "desc": "Energy-dense." if LANG == "en" else "عالي السعرات والطاقة.", "img": "https://images.unsplash.com/photo-1517673400267-0251440c45dc?q=80&w=1200&auto=format&fit=crop"},
            {"type": "Lunch" if LANG=="en" else "الغداء", "name": "Chicken Rice Bowl" if LANG == "en" else "طبق أرز بالدجاج", "cal": int(cal * 0.31), "desc": "Balanced carbs and protein." if LANG == "en" else "توازن رائع بين الكارب والبروتين للنمو العضلي.", "img": "https://images.unsplash.com/photo-1512058564366-18510be2db19?q=80&w=1200&auto=format&fit=crop"},
            {"type": "Dinner" if LANG=="en" else "العشاء", "name": "Steak & Potatoes" if LANG == "en" else "ستيك وبطاطس", "cal": int(cal * 0.31), "desc": "Higher calories for recovery." if LANG == "en" else "سعرات عالية لدعم التعافي بعد التمرين.", "img": "https://images.unsplash.com/photo-1547592180-85f173990554?q=80&w=1200&auto=format&fit=crop"},
            {"type": "Snack" if LANG=="en" else "سناك", "name": "Nuts & Dates" if LANG == "en" else "مكسرات وتمر", "cal": int(cal * 0.17), "desc": "Easy extra calories." if LANG == "en" else "سعرات إضافية سهلة ومفيدة جداً.", "img": "https://images.unsplash.com/photo-1499186028654-75ad3e1d45f9?q=80&w=1200&auto=format&fit=crop"},
        ]
    return [
        {"type": "Breakfast" if LANG=="en" else "الفطور", "name": "Oatmeal & Berries" if LANG == "en" else "شوفان وتوت", "cal": int(cal * 0.24), "desc": "Balanced carbs and fiber." if LANG == "en" else "كربوهيدرات متوازنة وغنية بالألياف.", "img": "https://images.unsplash.com/photo-1517673132405-a56a62b18caf?q=80&w=1200&auto=format&fit=crop"},
        {"type": "Lunch" if LANG=="en" else "الغداء", "name": "Chicken Salad Bowl" if LANG == "en" else "طبق سلطة بالدجاج", "cal": int(cal * 0.30), "desc": "Protein-rich and satisfying." if LANG == "en" else "غني بالبروتين وصحي ومُشبع.", "img": "https://images.unsplash.com/photo-1547592180-85f173990554?q=80&w=1200&auto=format&fit=crop"},
        {"type": "Dinner" if LANG=="en" else "العشاء", "name": "Salmon & Rice" if LANG == "en" else "سلمون وأرز", "cal": int(cal * 0.30), "desc": "Healthy fats with clean carbs." if LANG == "en" else "دهون صحية مع كارب نظيف للحفاظ على الوزن.", "img": "https://images.unsplash.com/photo-1467003909585-2f8a72700288?q=80&w=1200&auto=format&fit=crop"},
        {"type": "Snack" if LANG=="en" else "سناك", "name": "Fruit & Nuts" if LANG == "en" else "فواكه ومكسرات", "cal": int(cal * 0.14), "desc": "Light snack to keep balance." if LANG == "en" else "سناك خفيف للتوازن طوال اليوم.", "img": "https://images.unsplash.com/photo-1498837167922-ddd27525d352?q=80&w=1200&auto=format&fit=crop"},
    ]

def workout_plan_for(user: UserProfile) -> List[Dict[str, Any]]:
    lvl = {"easy": t("easy"), "medium": t("medium"), "hard": t("hard")}
    if user.goal == "Lose Weight":
        return [
            {"day": f"{t('day')} 1", "title": "Cardio Blast" if LANG == "en" else "كارديو عالي الشدة", "dur": "30m", "level_key": "medium", "level_text": lvl["medium"], "cal": 320, "img": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?q=80&w=1200&auto=format&fit=crop"},
            {"day": f"{t('day')} 2", "title": "Strength & Core" if LANG == "en" else "قوة وعضلات بطن", "dur": "40m", "level_key": "medium", "level_text": lvl["medium"], "cal": 350, "img": "https://images.unsplash.com/photo-1518611012118-696072aa579a?q=80&w=1200&auto=format&fit=crop"},
            {"day": f"{t('day')} 3", "title": "Walk + Mobility" if LANG == "en" else "مشي وتمطيط", "dur": "25m", "level_key": "easy", "level_text": lvl["easy"], "cal": 120, "img": "https://images.unsplash.com/photo-1495195134817-aeb325a55b65?q=80&w=1200&auto=format&fit=crop"},
            {"day": f"{t('day')} 4", "title": "Lower Body HIIT" if LANG == "en" else "تمارين سفلية عالية الشدة", "dur": "35m", "level_key": "hard", "level_text": lvl["hard"], "cal": 380, "img": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?q=80&w=1200&auto=format&fit=crop"},
            {"day": f"{t('day')} 5", "title": "Upper Body" if LANG == "en" else "تمارين علوية", "dur": "40m", "level_key": "medium", "level_text": lvl["medium"], "cal": 330, "img": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?q=80&w=1200&auto=format&fit=crop"},
            {"day": f"{t('day')} 6", "title": "Long Walk" if LANG == "en" else "مشي طويل", "dur": "45m", "level_key": "easy", "level_text": lvl["easy"], "cal": 180, "img": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?q=80&w=1200&auto=format&fit=crop"},
            {"day": f"{t('day')} 7", "title": "Recovery" if LANG == "en" else "استشفاء وراحة", "dur": "20m", "level_key": "easy", "level_text": lvl["easy"], "cal": 80, "img": "https://images.unsplash.com/photo-1506126613408-eca07ce68773?q=80&w=1200&auto=format&fit=crop"},
        ]
    if user.goal == "Gain Weight":
        return [
            {"day": f"{t('day')} 1", "title": "Strength Push" if LANG == "en" else "تمارين الدفع (Push)", "dur": "45m", "level_key": "medium", "level_text": lvl["medium"], "cal": 300, "img": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?q=80&w=1200&auto=format&fit=crop"},
            {"day": f"{t('day')} 2", "title": "Strength Pull" if LANG == "en" else "تمارين السحب (Pull)", "dur": "50m", "level_key": "hard", "level_text": lvl["hard"], "cal": 380, "img": "https://images.unsplash.com/photo-1518611012118-696072aa579a?q=80&w=1200&auto=format&fit=crop"},
            {"day": f"{t('day')} 3", "title": "Rest + Stretch" if LANG == "en" else "راحة وتمطيط", "dur": "20m", "level_key": "easy", "level_text": lvl["easy"], "cal": 60, "img": "https://images.unsplash.com/photo-1506126613408-eca07ce68773?q=80&w=1200&auto=format&fit=crop"},
            {"day": f"{t('day')} 4", "title": "Legs & Core" if LANG == "en" else "أرجل وبطن (Legs)", "dur": "50m", "level_key": "hard", "level_text": lvl["hard"], "cal": 390, "img": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?q=80&w=1200&auto=format&fit=crop"},
            {"day": f"{t('day')} 5", "title": "Full Body" if LANG == "en" else "جسم كامل شامل", "dur": "45m", "level_key": "medium", "level_text": lvl["medium"], "cal": 340, "img": "https://images.unsplash.com/photo-1518611012118-696072aa579a?q=80&w=1200&auto=format&fit=crop"},
            {"day": f"{t('day')} 6", "title": "Mobility" if LANG == "en" else "تمارين مرونة", "dur": "25m", "level_key": "easy", "level_text": lvl["easy"], "cal": 90, "img": "https://images.unsplash.com/photo-1495195134817-aeb325a55b65?q=80&w=1200&auto=format&fit=crop"},
            {"day": f"{t('day')} 7", "title": "Recovery" if LANG == "en" else "استشفاء وراحة", "dur": "20m", "level_key": "easy", "level_text": lvl["easy"], "cal": 70, "img": "https://images.unsplash.com/photo-1506126613408-eca07ce68773?q=80&w=1200&auto=format&fit=crop"},
        ]
    return [
        {"day": f"{t('day')} 1", "title": "Cardio" if LANG == "en" else "كارديو", "dur": "30m", "level_key": "medium", "level_text": lvl["medium"], "cal": 250, "img": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?q=80&w=1200&auto=format&fit=crop"},
        {"day": f"{t('day')} 2", "title": "Strength" if LANG == "en" else "قوة (مقاومة)", "dur": "40m", "level_key": "medium", "level_text": lvl["medium"], "cal": 320, "img": "https://images.unsplash.com/photo-1518611012118-696072aa579a?q=80&w=1200&auto=format&fit=crop"},
        {"day": f"{t('day')} 3", "title": "Rest" if LANG == "en" else "راحة كاملة", "dur": "20m", "level_key": "easy", "level_text": lvl["easy"], "cal": 60, "img": "https://images.unsplash.com/photo-1506126613408-eca07ce68773?q=80&w=1200&auto=format&fit=crop"},
        {"day": f"{t('day')} 4", "title": "Lower Body" if LANG == "en" else "تمارين سفلية", "dur": "40m", "level_key": "medium", "level_text": lvl["medium"], "cal": 300, "img": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?q=80&w=1200&auto=format&fit=crop"},
        {"day": f"{t('day')} 5", "title": "Upper Body" if LANG == "en" else "تمارين علوية", "dur": "40m", "level_key": "medium", "level_text": lvl["medium"], "cal": 300, "img": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?q=80&w=1200&auto=format&fit=crop"},
        {"day": f"{t('day')} 6", "title": "Walking / Mobility" if LANG == "en" else "مشي / مرونة", "dur": "30m", "level_key": "easy", "level_text": lvl["easy"], "cal": 120, "img": "https://images.unsplash.com/photo-1495195134817-aeb325a55b65?q=80&w=1200&auto=format&fit=crop"},
        {"day": f"{t('day')} 7", "title": "Recovery" if LANG == "en" else "استشفاء", "dur": "20m", "level_key": "easy", "level_text": lvl["easy"], "cal": 70, "img": "https://images.unsplash.com/photo-1506126613408-eca07ce68773?q=80&w=1200&auto=format&fit=crop"},
    ]

# =========================================================
# AI FOOD ANALYZER
# =========================================================
def extract_json_object(text: str) -> Dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except Exception:
        m = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if m:
            return json.loads(m.group(0))
        raise

class GeminiFoodAnalyzer:
    @staticmethod
    def analyze(api_key: str, image_bytes: bytes, mime_type: str = "image/jpeg") -> Dict[str, Any]:
        if not api_key:
            return {"error": "no_key"}
        
        try:
            import google.generativeai as genai
        except ImportError:
            return {"error": "missing_genai"}
            
        try:
            from PIL import Image as PILImage
        except ImportError:
            return {"error": "missing_pillow"}

        try:
            genai.configure(api_key=api_key.strip())
            model = genai.GenerativeModel(GEMINI_MODEL)
            prompt = (
                "Analyze this meal image and return ONLY a valid JSON object with these exact keys: "
                "name (string), calories (number), protein_g (number), carbs_g (number), fat_g (number), "
                "health_score (number out of 100), short_advice (string). "
                f"Write the 'short_advice' completely in {'Arabic' if LANG == 'ar' else 'English'}. "
                "Provide highly realistic nutritional estimates based on the visual portion size."
            )
            image = PILImage.open(io.BytesIO(image_bytes))
            response = model.generate_content([prompt, image])
            data = extract_json_object(getattr(response, "text", "") or "{}")
            
            return {
                "name": str(data.get("name", "وجبة غير معروفة" if LANG == "ar" else "Unknown Meal")),
                "calories": int(float(data.get("calories", 0) or 0)),
                "protein_g": int(float(data.get("protein_g", 0) or 0)),
                "carbs_g": int(float(data.get("carbs_g", 0) or 0)),
                "fat_g": int(float(data.get("fat_g", 0) or 0)),
                "health_score": int(float(data.get("health_score", 0) or 0)),
                "short_advice": str(data.get("short_advice", "")),
            }
        except Exception as ex:
            return {"error": str(ex)}

# =========================================================
# UI HELPERS (RESPONSIVE DESKTOP/WEB)
# =========================================================
def shell(body: ft.Control) -> ft.Container:
    """A responsive container that handles scrolling correctly on Desktop/Web."""
    return ft.Container(
        expand=True,
        content=ft.Column(
            controls=[
                ft.Container(
                    width=1400,
                    padding=ft.padding.only(left=24, top=24, right=24, bottom=110),
                    alignment=ft.alignment.top_center,
                    content=body
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
    )

def nav_bar(index: int, go: Callable[[str], None]) -> ft.NavigationBar:
    routes = ["/dashboard", "/meals", "/workout", "/analysis", "/stats", "/profile"]
    labels = [t("dashboard"), t("meals"), t("workout"), t("analysis"), t("stats"), t("profile")]
    icons = [ft.Icons.HOME, ft.Icons.RESTAURANT, ft.Icons.FITNESS_CENTER, ft.Icons.CAMERA_ALT, ft.Icons.BAR_CHART, ft.Icons.PERSON]

    return ft.NavigationBar(
        selected_index=index,
        bgcolor=CARD,
        indicator_color="#243341",
        destinations=[ft.NavigationBarDestination(icon=icons[i], label=labels[i]) for i in range(6)],
        on_change=lambda e: go(routes[e.control.selected_index]),
    )

def lang_chip(page: ft.Page) -> ft.Container:
    return ft.Container(
        ink=True,
        on_click=lambda e: toggle_language(page),
        padding=ft.padding.symmetric(horizontal=12, vertical=8),
        border_radius=999,
        bgcolor=CARD2,
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.LANGUAGE, size=16, color=ACCENT),
                ft.Text(t("change_lang"), size=12, weight="bold", color=TEXT),
            ],
            spacing=6,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
    )

def header(page: ft.Page, title_text: str, sub_text: str) -> ft.Row:
    return ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Column(
                controls=[
                    ft.Text(title_text, size=32, weight="bold", color=TEXT),
                    ft.Text(sub_text, size=13, color=SUB),
                ],
                spacing=6,
                expand=True,
            ),
            lang_chip(page),
        ],
    )

def stat_chip(label: str, value: str, accent: str = ACCENT) -> ft.Container:
    return ft.Container(
        expand=True, padding=16, border_radius=18, bgcolor=CARD2, border=ft.border.all(1, accent),
        content=ft.Column(
            controls=[
                ft.Text(value, size=24, weight="bold", color=accent, text_align=ft.TextAlign.CENTER),
                ft.Text(label, size=13, color=SUB, text_align=ft.TextAlign.CENTER),
            ],
            alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6,
        ),
    )

def quick_btn(icon: Any, label: str, route: str, go: Callable[[str], None]) -> ft.Container:
    return ft.Container(
        expand=True, height=130, border_radius=24, bgcolor=CARD, ink=True, on_click=lambda e: go(route),
        content=ft.Column(
            controls=[
                ft.Container(width=52, height=52, border_radius=16, bgcolor="#213043", alignment=ft.Alignment(0, 0), content=ft.Icon(icon, size=26, color=ACCENT)),
                ft.Text(label, size=14, weight="bold", color=TEXT, text_align=ft.TextAlign.CENTER),
            ],
            alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10,
        ),
    )

def image_card(src: str, width: Optional[int] = 110, height: Optional[int] = 110, icon: Any = ft.Icons.IMAGE, icon_color: str = ACCENT) -> ft.Container:
    return ft.Container(
        width=width, height=height, border_radius=18, bgcolor=CARD3, clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Image(src=src, fit=ft.ImageFit.COVER, error_content=ft.Container(expand=True, alignment=ft.Alignment(0, 0), content=ft.Icon(icon, color=icon_color, size=42))),
    )

def chart_bars(title_text: str, labels: List[str], values: List[float], accent: str = ACCENT) -> ft.Container:
    max_v = max(max(values) if values else 1, 1) # Prevent division by zero
    bars = []
    for lbl, val in zip(labels, values):
        h = max(18, int((val / max_v) * 160))
        bars.append(
            ft.Column(
                controls=[
                    ft.Container(height=h, width=20, border_radius=8, bgcolor=accent),
                    ft.Text(lbl, size=11, color=SUB),
                    ft.Text(str(val), size=10, color=MUTED),
                ],
                alignment=ft.MainAxisAlignment.END, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6,
            )
        )
    return ft.Container(
        bgcolor=CARD, border_radius=24, padding=24, shadow=ft.BoxShadow(blur_radius=20, spread_radius=0, color="#1A000000", offset=ft.Offset(0, 8)),
        content=ft.Column(
            controls=[
                ft.Text(title_text, size=18, weight="bold", color=TEXT),
                ft.Container(height=10),
                ft.Row(controls=bars, alignment=ft.MainAxisAlignment.SPACE_AROUND, vertical_alignment=ft.CrossAxisAlignment.END, height=240),
            ],
            spacing=6,
        ),
    )

# =========================================================
# SCREENS
# =========================================================
class SplashView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/", bgcolor=PAGE_BG, scroll=None)
        self.page = page
        self.controls = [self.build_body()]

    def build_body(self) -> ft.Control:
        return ft.Container(
            expand=True, alignment=ft.Alignment(0, 0), padding=ft.padding.all(20),
            content=ft.Column(
                controls=[
                    ft.Container(
                        width=140, height=140, border_radius=40, gradient=ft.LinearGradient(colors=[ACCENT, ACCENT2]),
                        alignment=ft.Alignment(0, 0), content=ft.Icon(ft.Icons.FAVORITE, size=64, color=BG),
                    ),
                    ft.Container(height=24),
                    ft.Text("Healthify", size=48, weight="bold", color=TEXT),
                    ft.Text(t("welcome_sub"), size=15, color=SUB),
                    ft.Container(height=24),
                    ft.ProgressRing(color=ACCENT),
                ],
                alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=14,
            ),
        )

    def did_mount(self):
        async def _next():
            await asyncio.sleep(1.5)
            user = load_user()
            self.page.go("/dashboard" if user.is_setup else "/welcome")
        self.page.run_task(_next)

class WelcomeView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/welcome", bgcolor=PAGE_BG, scroll=None)
        self.page = page
        user = load_user()

        def tf(label, val): return ft.TextField(label=label, value=val, filled=True, fill_color=CARD2, border_color="#334155", focused_border_color=ACCENT, border_radius=18, color=TEXT)
        def drop(label, val, opts): return ft.Dropdown(label=label, value=val, filled=True, fill_color=CARD2, border_color="#334155", focused_border_color=ACCENT, border_radius=18, color=TEXT, options=[ft.dropdown.Option(x) for x in opts])

        self.name_in = tf(t("name"), user.name)
        self.age_in = tf(t("age"), str(user.age))
        self.gender_in = drop(t("gender"), "Male" if user.gender == "Male" else "Female", ["Male", "Female"])
        self.height_in = tf(t("height"), str(user.height))
        self.weight_in = tf(t("weight"), str(user.weight))
        self.activity_in = drop(t("activity"), "Moderate", ["Sedentary", "Light", "Moderate", "Active", "Very Active"])
        self.goal_in = drop(t("goal"), "Maintain", ["Lose Weight", "Maintain", "Gain Weight"])

        self.controls = [self.build_body()]

    def build_body(self) -> ft.Control:
        def save_profile(e):
            updated = UserProfile(
                name=(self.name_in.value or "").strip() or "User",
                age=max(1, safe_int(self.age_in.value, 25)),
                gender=normalize_gender(self.gender_in.value),
                height=max(50.0, safe_float(self.height_in.value, 170.0)),
                weight=max(20.0, safe_float(self.weight_in.value, 70.0)),
                activity_level=normalize_activity(self.activity_in.value),
                goal=normalize_goal(self.goal_in.value),
                is_setup=True,
                api_key=load_user().api_key 
            )
            save_user(updated)
            self.page.go("/dashboard")

        body = ft.Column(
            controls=[
                ft.Container(
                    bgcolor=CARD, border_radius=24, padding=24, shadow=ft.BoxShadow(blur_radius=20, spread_radius=0, color="#1A000000", offset=ft.Offset(0, 8)),
                    content=ft.Column(
                        controls=[
                            ft.Text(t("welcome"), size=34, weight="bold", color=TEXT),
                            ft.Text(t("welcome_sub"), size=14, color=SUB),
                        ],
                        spacing=8,
                    ),
                ),
                self.name_in,
                ft.Row(controls=[ft.Container(expand=True, content=self.age_in), ft.Container(expand=True, content=self.gender_in)], spacing=16),
                ft.Row(controls=[ft.Container(expand=True, content=self.height_in), ft.Container(expand=True, content=self.weight_in)], spacing=16),
                self.activity_in,
                self.goal_in,
                ft.Container(height=10),
                ft.Container(
                    height=60, border_radius=18, gradient=ft.LinearGradient(colors=[ACCENT, ACCENT2]), alignment=ft.Alignment(0, 0), ink=True, on_click=save_profile,
                    content=ft.Text(t("generate_plan"), size=18, weight="bold", color=BG),
                ),
                ft.Container(
                    height=60, border_radius=18, bgcolor=CARD2, alignment=ft.Alignment(0, 0), ink=True, on_click=lambda e: toggle_language(self.page),
                    content=ft.Text(t("change_lang"), size=16, weight="bold", color=TEXT),
                ),
            ],
            spacing=16,
        )
        return shell(ft.Container(width=700, content=body))

class DashboardView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/dashboard", bgcolor=PAGE_BG, scroll=None)
        self.page = page
        self.navigation_bar = nav_bar(0, self.page.go)
        self.controls = [self.build_body()]

    def build_body(self) -> ft.Control:
        user = load_user()
        metrics = calculate_metrics(user)
        tip = health_tip(metrics, user.goal)
        status_color = ORANGE if metrics["bmi_status"] in ("Underweight", "Overweight", "Obese") else ACCENT
        
        def meal_info_row(title_text, value_text, icon, color):
            return ft.Container(
                expand=True, padding=16, border_radius=20, bgcolor=CARD2,
                content=ft.Row(
                    controls=[
                        ft.Container(width=48, height=48, border_radius=16, bgcolor="#233246", alignment=ft.Alignment(0, 0), content=ft.Icon(icon, color=color, size=24)),
                        ft.Column(controls=[ft.Text(title_text, size=13, color=SUB), ft.Text(value_text, size=18, weight="bold", color=TEXT)], spacing=4),
                    ], spacing=16
                )
            )

        body = ft.Column(
            controls=[
                header(self.page, t("dashboard_title"), t("dashboard_sub")),
                ft.Container(
                    bgcolor=CARD, border_radius=24, padding=24, shadow=ft.BoxShadow(blur_radius=20, spread_radius=0, color="#1A000000", offset=ft.Offset(0, 8)),
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Column(
                                        controls=[
                                            ft.Text(f'{t("welcome").split(" في")[0] if LANG == "ar" else "Hello"}, {user.name or "User"}!', size=28, weight="bold", color=TEXT),
                                            ft.Text(t("today_summary"), size=14, color=SUB),
                                        ], expand=True, spacing=4,
                                    ),
                                    ft.Container(width=64, height=64, border_radius=20, bgcolor="#223246", alignment=ft.Alignment(0, 0), content=ft.Icon(ft.Icons.PERSON, color=ACCENT, size=32)),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.Container(
                                padding=12, border_radius=16, bgcolor="#2A2F3A",
                                content=ft.Text(f'BMI {metrics["bmi"]} • {metrics["bmi_status"]}', size=14, color=status_color, weight="bold"),
                            ),
                        ], spacing=16,
                    ),
                ),
                ft.ResponsiveRow(
                    controls=[
                        ft.Column(col={"xs": 6, "sm": 6, "md": 3}, controls=[stat_chip(t("bmi"), str(metrics["bmi"]), ACCENT)]),
                        ft.Column(col={"xs": 6, "sm": 6, "md": 3}, controls=[stat_chip(t("daily_target"), str(metrics["target_calories"]), ACCENT)]),
                        ft.Column(col={"xs": 6, "sm": 6, "md": 3}, controls=[stat_chip(t("protein"), f'{metrics["protein"]}g', BLUE)]),
                        ft.Column(col={"xs": 6, "sm": 6, "md": 3}, controls=[stat_chip(t("carbs"), f'{metrics["carbs"]}g', GREEN)]),
                    ], run_spacing=16, spacing=16,
                ),
                ft.ResponsiveRow(
                    controls=[
                        ft.Column(
                            col={"xs": 12, "md": 6},
                            controls=[
                                ft.Container(
                                    bgcolor=CARD, border_radius=24, padding=24, expand=True, shadow=ft.BoxShadow(blur_radius=20, spread_radius=0, color="#1A000000", offset=ft.Offset(0, 8)),
                                    content=ft.Column(
                                        controls=[
                                            ft.Text(t("daily_macros"), size=20, weight="bold", color=TEXT),
                                            ft.Row(controls=[stat_chip(t("protein"), f'{metrics["protein"]}g', BLUE), stat_chip(t("carbs"), f'{metrics["carbs"]}g', GREEN), stat_chip(t("fat"), f'{metrics["fats"]}g', ORANGE)], spacing=12),
                                        ], spacing=16,
                                    ),
                                )
                            ]
                        ),
                        ft.Column(
                            col={"xs": 12, "md": 6},
                            controls=[
                                ft.Container(
                                    bgcolor=CARD, border_radius=24, padding=24, expand=True, shadow=ft.BoxShadow(blur_radius=20, spread_radius=0, color="#1A000000", offset=ft.Offset(0, 8)),
                                    content=ft.Column(
                                        controls=[
                                            ft.Text(t("today_workout"), size=20, weight="bold", color=TEXT),
                                            image_card("https://images.unsplash.com/photo-1517836357463-d25dfeac3438?q=80&w=1200&auto=format&fit=crop", width=None, height=130, icon=ft.Icons.FITNESS_CENTER),
                                            ft.Text("HIIT Cardio • 30 mins • 320 kcal" if LANG == "en" else "كارديو HIIT • 30 دقيقة • 320 سعرة", size=14, color=SUB),
                                        ], spacing=14,
                                    ),
                                )
                            ]
                        )
                    ], run_spacing=16, spacing=16
                ),
                ft.ResponsiveRow(
                    controls=[
                        ft.Column(col={"xs": 12, "md": 4}, controls=[meal_info_row(t("water"), "1.5 / 3.0 L" if LANG == "en" else "1.5 / 3.0 لتر", ft.Icons.WATER_DROP, BLUE)]),
                        ft.Column(col={"xs": 12, "md": 4}, controls=[meal_info_row(t("heart_rate"), "78 BPM", ft.Icons.FAVORITE, RED)]),
                        ft.Column(col={"xs": 12, "md": 4}, controls=[meal_info_row(t("sleep"), "7.5 Hours" if LANG == "en" else "7.5 ساعات", ft.Icons.BEDTIME, PURPLE)]),
                    ], run_spacing=16, spacing=16
                ),
                ft.Text(t("quick_actions"), size=22, weight="bold", color=TEXT),
                ft.ResponsiveRow(
                    controls=[
                        ft.Column(col={"xs": 6, "sm": 6, "md": 3}, controls=[quick_btn(ft.Icons.RESTAURANT, t("meals"), "/meals", self.page.go)]),
                        ft.Column(col={"xs": 6, "sm": 6, "md": 3}, controls=[quick_btn(ft.Icons.FITNESS_CENTER, t("workout"), "/workout", self.page.go)]),
                        ft.Column(col={"xs": 6, "sm": 6, "md": 3}, controls=[quick_btn(ft.Icons.CAMERA_ALT, t("analysis"), "/analysis", self.page.go)]),
                        ft.Column(col={"xs": 6, "sm": 6, "md": 3}, controls=[quick_btn(ft.Icons.BAR_CHART, t("stats"), "/stats", self.page.go)]),
                    ], run_spacing=16, spacing=16,
                ),
                ft.Container(
                    bgcolor=CARD, border_radius=24, padding=24, shadow=ft.BoxShadow(blur_radius=20, spread_radius=0, color="#1A000000", offset=ft.Offset(0, 8)),
                    content=ft.Column(controls=[ft.Text(t("smart_tip"), size=20, weight="bold", color=TEXT), ft.Text(tip, size=15, color=SUB)], spacing=8),
                ),
            ],
            spacing=24,
        )
        return shell(body)

class AnalysisView(ft.View):
    def __init__(self, page: ft.Page, file_picker: ft.FilePicker):
        super().__init__(route="/analysis", bgcolor=PAGE_BG, scroll=None)
        self.page = page
        self.file_picker = file_picker
        self.navigation_bar = nav_bar(3, self.page.go)

        self.selected_path: str = ""
        self.selected_bytes: bytes = b""
        self.loading = False
        self.result: Optional[Dict[str, Any]] = None

        self.file_picker.on_result = self.on_pick
        self.controls = [self.build_body()]

    def redraw(self):
        self.controls = [self.build_body()]
        self.update()

    def pick_image(self, e):
        self.file_picker.pick_files(allow_multiple=False)

    def on_pick(self, e):
        if not getattr(e, "files", None): return
        picked = e.files[0]
        self.selected_path = getattr(picked, "path", "") or ""
        self.selected_bytes = b""
        if self.selected_path and os.path.exists(self.selected_path):
            try:
                with open(self.selected_path, "rb") as f:
                    self.selected_bytes = f.read()
            except Exception:
                pass
        self.result = None
        self.loading = False
        self.redraw()

    def start_analysis(self, e):
        if not self.selected_path:
            self.pick_image(e)
            return
        self.loading = True
        self.result = None
        self.redraw()
        self.page.run_task(self.analyze_task)

    async def analyze_task(self):
        await asyncio.sleep(0.05) 
        user = load_user()
        
        if not self.selected_path or not os.path.exists(self.selected_path):
            self.loading = False
            self.redraw()
            return
            
        try:
            if not self.selected_bytes:
                with open(self.selected_path, "rb") as f:
                    self.selected_bytes = f.read()
                    
            res = await asyncio.to_thread(GeminiFoodAnalyzer.analyze, user.api_key, self.selected_bytes)
            
            if "error" in res:
                err = res["error"]
                self.result = {
                    "name": "Mock Meal" if LANG == "en" else "وجبة تجريبية",
                    "calories": 650, "protein_g": 48, "carbs_g": 34, "fat_g": 26, "health_score": 86,
                }
                if err == "no_key":
                    self.result["short_advice"] = t("ai_missing")
                elif err == "missing_pillow":
                    self.result["short_advice"] = t("missing_pillow")
                else:
                    self.result["short_advice"] = f"{t('analysis_error')}: {err}"
            else:
                self.result = res
                
        except Exception as ex:
            self.result = {"name": t("analysis_error"), "calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0, "health_score": 0, "short_advice": str(ex)}
            
        save_analysis(self.result or {})
        self.loading = False
        self.redraw()

    def build_body(self) -> ft.Control:
        user = load_user()
        metrics = calculate_metrics(user)
        has_key = bool(user.api_key.strip())

        if self.loading:
            upload_content = ft.Column(
                controls=[ft.ProgressRing(color=ACCENT), ft.Text(t("analyzing"), color=SUB, size=16)],
                alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16,
            )
        elif self.selected_path:
            upload_content = ft.Column(
                controls=[
                    ft.Icon(ft.Icons.IMAGE, size=56, color=ACCENT),
                    ft.Text(os.path.basename(self.selected_path), size=16, color=TEXT, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(t("pick_image"), size=14, color=MUTED),
                ],
                alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10,
            )
        else:
            upload_content = ft.Column(
                controls=[
                    ft.Icon(ft.Icons.CAMERA_ALT, size=64, color=ACCENT),
                    ft.Text(t("camera_hint"), size=22, weight="bold", color=TEXT),
                ],
                alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10,
            )

        result_control = ft.Container(height=1)
        if self.result:
            result_control = ft.Container(
                bgcolor=CARD, border_radius=24, padding=24, shadow=ft.BoxShadow(blur_radius=20, spread_radius=0, color="#1A000000", offset=ft.Offset(0, 8)),
                content=ft.Column(
                    controls=[
                        ft.Text(t("analysis_result"), size=20, weight="bold", color=TEXT),
                        ft.Text(self.result["name"], size=28, weight="bold", color=ACCENT),
                        ft.ResponsiveRow(
                            controls=[
                                ft.Column(col={"xs": 6, "md": 3}, controls=[stat_chip(t("calories"), str(self.result["calories"]), BLUE)]),
                                ft.Column(col={"xs": 6, "md": 3}, controls=[stat_chip(t("protein"), f'{self.result["protein_g"]}g', BLUE)]),
                                ft.Column(col={"xs": 6, "md": 3}, controls=[stat_chip(t("carbs"), f'{self.result["carbs_g"]}g', GREEN)]),
                                ft.Column(col={"xs": 6, "md": 3}, controls=[stat_chip(t("fat"), f'{self.result["fat_g"]}g', ORANGE)]),
                            ], spacing=12, run_spacing=12
                        ),
                        ft.Container(
                            bgcolor=CARD2, border_radius=20, padding=20,
                            content=ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.HEALTH_AND_SAFETY, color=ACCENT, size=46),
                                    ft.Column(controls=[ft.Text(t("health_score"), size=14, color=SUB), ft.Text(f'{self.result["health_score"]}/100', size=32, weight="bold", color=TEXT)], spacing=2),
                                ], spacing=18,
                            ),
                        ),
                        ft.Text(self.result.get("short_advice", ""), size=16, color=SUB),
                    ], spacing=20,
                ),
            )

        body = ft.Column(
            controls=[
                header(self.page, t("food_analysis"), t("analysis_ready")),
                ft.Container(
                    bgcolor=CARD, border_radius=24, padding=24, shadow=ft.BoxShadow(blur_radius=20, spread_radius=0, color="#1A000000", offset=ft.Offset(0, 8)),
                    content=ft.Column(
                        controls=[
                            ft.Text(t("analysis_ready"), size=20, weight="bold", color=TEXT),
                            ft.Text(f'BMI {metrics["bmi"]} • {metrics["bmi_status"]} | {metrics["target_calories"]} kcal/day', size=15, color=SUB),
                            ft.Text(t("ai_ready_msg") if has_key else t("ai_missing"), size=13, color=GREEN if has_key else ORANGE),
                        ], spacing=8,
                    ),
                ),
                ft.Container(
                    height=300, border_radius=24, gradient=ft.LinearGradient(colors=["#17202A", "#202A36"]), border=ft.border.all(1, "#2A3544"),
                    alignment=ft.Alignment(0, 0), ink=True, on_click=self.pick_image, content=upload_content,
                ),
                ft.Row(
                    controls=[
                        ft.Container(expand=True, content=ft.Container(height=60, border_radius=20, bgcolor=ACCENT, alignment=ft.Alignment(0, 0), ink=True, on_click=self.pick_image, content=ft.Text(t("pick_image"), size=16, weight="bold", color=BG))),
                        ft.Container(expand=True, content=ft.Container(height=60, border_radius=20, bgcolor=CARD2, border=ft.border.all(1, "#334155"), alignment=ft.Alignment(0, 0), ink=True, on_click=self.start_analysis, content=ft.Text(t("analyze"), size=16, weight="bold", color=TEXT))),
                    ], spacing=16,
                ),
                result_control,
            ], spacing=24,
        )
        return shell(body)

class MealsView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/meals", bgcolor=PAGE_BG, scroll=None)
        self.page = page
        self.navigation_bar = nav_bar(1, self.page.go)
        self.controls = [self.build_body()]

    def build_body(self) -> ft.Control:
        user = load_user()
        metrics = calculate_metrics(user)
        meals = meal_plan_for(user, metrics)
        save_meals(meals) 

        def meals_banner(title_text, sub_text, image_url):
            return ft.Container(
                bgcolor=CARD, border_radius=24, shadow=ft.BoxShadow(blur_radius=20, spread_radius=0, color="#1A000000", offset=ft.Offset(0, 8)), clip_behavior=ft.ClipBehavior.HARD_EDGE,
                content=ft.Container(
                    height=240,
                    content=ft.Stack(
                        controls=[
                            ft.Container(expand=True, content=ft.Image(src=image_url, fit=ft.ImageFit.COVER)),
                            ft.Container(expand=True, gradient=ft.LinearGradient(begin=ft.Alignment(0, -1), end=ft.Alignment(0, 1), colors=["#00000010", "#000000CC"])),
                            ft.Container(
                                expand=True, padding=24, alignment=ft.Alignment(-1, 1) if LANG == "en" else ft.Alignment(1, 1),
                                content=ft.Column(
                                    controls=[
                                        ft.Container(padding=10, border_radius=999, bgcolor="#00000055", content=ft.Text(title_text, size=13, weight="bold", color=TEXT)),
                                        ft.Text(sub_text, size=28, weight="bold", color=TEXT),
                                    ], alignment=ft.MainAxisAlignment.END, horizontal_alignment=ft.CrossAxisAlignment.START if LANG == "en" else ft.CrossAxisAlignment.END,
                                ),
                            ),
                        ]
                    ),
                ),
            )
            
        def meal_card(item):
            return ft.Container(
                bgcolor=CARD, border_radius=24, padding=20, shadow=ft.BoxShadow(blur_radius=20, spread_radius=0, color="#1A000000", offset=ft.Offset(0, 8)),
                content=ft.Row(
                    controls=[
                        image_card(item["img"], width=110, height=110, icon=ft.Icons.RESTAURANT),
                        ft.Column(
                            controls=[
                                ft.Text(item["type"], size=13, color=ACCENT, weight="bold"),
                                ft.Text(item["name"], size=20, color=TEXT, weight="bold"),
                                ft.Text(f'{item["cal"]} kcal', size=14, color=SUB),
                                ft.Text(item["desc"], size=13, color=MUTED, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                            ], expand=True, spacing=6,
                        ),
                    ], spacing=20, vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )

        body = ft.Column(
            controls=[
                header(self.page, t("meal_plan"), t("nutrition_smart")),
                meals_banner(t("nutrition_smart"), f'{metrics["target_calories"]} kcal/day', "https://images.unsplash.com/photo-1490645935967-10de6ba17061?q=80&w=1200&auto=format&fit=crop"),
                ft.Container(
                    bgcolor=CARD, border_radius=24, padding=24, shadow=ft.BoxShadow(blur_radius=20, spread_radius=0, color="#1A000000", offset=ft.Offset(0, 8)),
                    content=ft.Column(
                        controls=[
                            ft.Text(t("daily_nutrition_target"), size=20, weight="bold", color=TEXT),
                            ft.Text(f'{metrics["target_calories"]} kcal', size=36, weight="bold", color=ACCENT),
                            ft.Text(f'{t("protein")} {metrics["protein"]}g • {t("carbs")} {metrics["carbs"]}g • {t("fat")} {metrics["fats"]}g', size=15, color=SUB),
                        ], spacing=10,
                    ),
                ),
                ft.ResponsiveRow(controls=[ft.Column(col={"xs": 12, "md": 6}, controls=[meal_card(m)]) for m in meals], run_spacing=16, spacing=16),
            ], spacing=24,
        )
        return shell(body)

class WorkoutView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/workout", bgcolor=PAGE_BG, scroll=None)
        self.page = page
        self.navigation_bar = nav_bar(2, self.page.go)
        self.controls = [self.build_body()]

    def build_body(self) -> ft.Control:
        user = load_user()
        workouts = workout_plan_for(user)
        save_workouts(workouts) 

        def workout_card(item):
            level_color = GREEN if item["level_key"] == "easy" else ORANGE if item["level_key"] == "medium" else RED
            return ft.Container(
                bgcolor=CARD, border_radius=24, padding=20, shadow=ft.BoxShadow(blur_radius=20, spread_radius=0, color="#1A000000", offset=ft.Offset(0, 8)),
                content=ft.Row(
                    controls=[
                        image_card(item["img"], width=100, height=100, icon=ft.Icons.FITNESS_CENTER),
                        ft.Column(
                            controls=[
                                ft.Text(f'{item["day"]} • {item["title"]}', size=20, color=TEXT, weight="bold"),
                                ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.TIMER, size=16, color=SUB), ft.Text(item["dur"], size=14, color=SUB), ft.Container(width=12),
                                        ft.Icon(ft.Icons.LOCAL_FIRE_DEPARTMENT, size=16, color=SUB), ft.Text(f'{item["cal"]} kcal', size=14, color=SUB),
                                    ], spacing=6,
                                ),
                                ft.Container(
                                    padding=10, border_radius=999, bgcolor="#202B22" if level_color == GREEN else "#33281F" if level_color == ORANGE else "#342022",
                                    content=ft.Text(item["level_text"], size=12, color=level_color, weight="bold"),
                                ),
                            ], expand=True, spacing=8,
                        ),
                    ], spacing=20, vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )

        body = ft.Column(
            controls=[
                header(self.page, t("weekly_workout"), t("weekly_summary")),
                ft.Container(
                    bgcolor=CARD, border_radius=24, padding=24, shadow=ft.BoxShadow(blur_radius=20, spread_radius=0, color="#1A000000", offset=ft.Offset(0, 8)),
                    content=ft.Column(controls=[ft.Text(t("weekly_summary"), size=20, weight="bold", color=TEXT), ft.Text("7-day routine with progressive load and recovery." if LANG == "en" else "روتين 7 أيام متدرج بين القوة والراحة.", size=15, color=SUB)], spacing=10),
                ),
                ft.ResponsiveRow(controls=[ft.Column(col={"xs": 12, "md": 6}, controls=[workout_card(w)]) for w in workouts], run_spacing=16, spacing=16),
            ], spacing=24,
        )
        return shell(body)

class StatsView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/stats", bgcolor=PAGE_BG, scroll=None)
        self.page = page
        self.navigation_bar = nav_bar(4, self.page.go)
        self.controls = [self.build_body()]

    def build_body(self) -> ft.Control:
        user = load_user()
        metrics = calculate_metrics(user)
        db = load_db()

        weight_history = db.get("weight_history") or []
        if not weight_history:
            weights = [round(user.weight + x, 1) for x in (-0.8, -0.5, -0.3, -0.1, 0.0, 0.1, 0.2)]
            weight_history = [{"day": d, "weight": w} for d, w in zip(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], weights)]

        calorie_history = db.get("calorie_history") or []
        if not calorie_history:
            cals = [int(metrics["target_calories"] + x) for x in (-140, -80, -30, 0, 60, 30, 90)]
            calorie_history = [{"day": d, "calories": c} for d, c in zip(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], cals)]

        w_labels = [x["day"] for x in weight_history[-7:]]
        w_values = [float(x["weight"]) for x in weight_history[-7:]]
        c_labels = [x["day"] for x in calorie_history[-7:]]
        c_values = [int(x["calories"]) for x in calorie_history[-7:]]
        adherence = 92 if user.goal == "Maintain" else 88 if user.goal == "Lose Weight" else 84

        body = ft.Column(
            controls=[
                header(self.page, t("stats_title"), t("stats_sub")),
                ft.ResponsiveRow(
                    controls=[
                        ft.Column(col={"xs": 12, "md": 6}, controls=[stat_chip(t("adherence"), f"{adherence}%", ACCENT)]),
                        ft.Column(col={"xs": 12, "md": 6}, controls=[stat_chip(t("active_days"), "24", ACCENT)]),
                    ], run_spacing=16, spacing=16
                ),
                ft.ResponsiveRow(
                    controls=[
                        ft.Column(col={"xs": 12, "md": 6}, controls=[chart_bars(t("weight_history"), w_labels, w_values, BLUE)]),
                        ft.Column(col={"xs": 12, "md": 6}, controls=[chart_bars(t("calories_history"), c_labels, c_values, ACCENT)]),
                    ], run_spacing=16, spacing=16
                ),
                ft.Container(
                    bgcolor=CARD, border_radius=24, padding=24, shadow=ft.BoxShadow(blur_radius=20, spread_radius=0, color="#1A000000", offset=ft.Offset(0, 8)),
                    content=ft.Column(
                        controls=[
                            ft.Text(t("achievements"), size=20, weight="bold", color=TEXT),
                            ft.ResponsiveRow(
                                controls=[
                                    ft.Column(col={"xs": 12, "md": 4}, controls=[stat_chip(t("streak"), "12", BLUE)]),
                                    ft.Column(col={"xs": 12, "md": 4}, controls=[stat_chip(t("workouts_logged"), "28", GREEN)]),
                                    ft.Column(col={"xs": 12, "md": 4}, controls=[stat_chip(t("meals_logged"), "64", ORANGE)]),
                                ], run_spacing=16, spacing=16
                            ),
                        ], spacing=16,
                    ),
                ),
            ], spacing=24,
        )
        return shell(body)

class ProfileView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/profile", bgcolor=PAGE_BG, scroll=None)
        self.page = page
        self.user = load_user()
        self.navigation_bar = nav_bar(5, self.page.go)
        self.controls = [self.build_body()]

    def build_body(self) -> ft.Control:
        def field(label: str, value: str, password: bool = False) -> ft.TextField:
            return ft.TextField(label=label, value=value, filled=True, fill_color=CARD2, border_color="#334155", focused_border_color=ACCENT, border_radius=20, color=TEXT, password=password, can_reveal_password=password)

        def dropdown(label: str, value: str, options: List[str]) -> ft.Dropdown:
            return ft.Dropdown(label=label, value=value, filled=True, fill_color=CARD2, border_color="#334155", focused_border_color=ACCENT, border_radius=20, color=TEXT, options=[ft.dropdown.Option(opt) for opt in options])

        name = field(t("name"), self.user.name)
        age = field(t("age"), str(self.user.age))
        gender = dropdown(t("gender"), "Male" if self.user.gender == "Male" else "Female", ["Male", "Female"] if LANG == "en" else ["ذكر", "أنثى"])
        height = field(t("height"), str(self.user.height))
        weight = field(t("weight"), str(self.user.weight))
        activity = dropdown(t("activity"), self.user.activity_level, ["Sedentary", "Light", "Moderate", "Active", "Very Active"] if LANG == "en" else ["خامل", "خفيف", "متوسط", "نشط", "نشط جداً"])
        goal = dropdown(t("goal"), self.user.goal, ["Lose Weight", "Maintain", "Gain Weight"] if LANG == "en" else ["تنحيف", "تثبيت", "زيادة وزن"])
        api_key = field(t("api_key"), self.user.api_key, password=True)

        def save_profile(e):
            updated = UserProfile(
                name=(name.value or "").strip() or "User",
                age=max(1, safe_int(age.value, 25)),
                gender=normalize_gender(gender.value),
                height=max(50.0, safe_float(height.value, 170.0)),
                weight=max(20.0, safe_float(weight.value, 70.0)),
                activity_level=normalize_activity(activity.value),
                goal=normalize_goal(goal.value),
                api_key=(api_key.value or "").strip(),
                is_setup=True,
            )
            save_user(updated)
            self.page.go("/dashboard")

        body = ft.Column(
            controls=[
                header(self.page, t("profile_title"), t("profile_sub")),
                ft.ResponsiveRow(
                    controls=[
                        ft.Column(
                            col={"xs": 12, "md": 6},
                            controls=[
                                ft.Container(
                                    bgcolor=CARD, border_radius=24, padding=24, expand=True, shadow=ft.BoxShadow(blur_radius=20, spread_radius=0, color="#1A000000", offset=ft.Offset(0, 8)),
                                    content=ft.Column(
                                        controls=[
                                            ft.Row(
                                                controls=[
                                                    ft.Container(width=72, height=72, border_radius=20, bgcolor="#223246", alignment=ft.Alignment(0, 0), content=ft.Icon(ft.Icons.PERSON, color=ACCENT, size=36)),
                                                    ft.Column(controls=[ft.Text(self.user.name or "User", size=24, weight="bold", color=TEXT), ft.Text(f'{t("goal")}: {self.user.goal}', size=14, color=SUB)], spacing=4),
                                                ], spacing=20,
                                            ),
                                            ft.Container(height=8),
                                            name,
                                            ft.Row(controls=[ft.Container(expand=True, content=age), ft.Container(expand=True, content=gender)], spacing=16),
                                            ft.Row(controls=[ft.Container(expand=True, content=height), ft.Container(expand=True, content=weight)], spacing=16),
                                            activity,
                                            goal,
                                            ft.Container(height=8),
                                            api_key, 
                                            ft.Container(
                                                height=60, border_radius=20, gradient=ft.LinearGradient(colors=[ACCENT, ACCENT2]), alignment=ft.Alignment(0, 0), ink=True, on_click=save_profile,
                                                content=ft.Text(t("save_profile"), size=16, weight="bold", color=BG),
                                            ),
                                        ], spacing=16,
                                    ),
                                )
                            ]
                        ),
                        ft.Column(
                            col={"xs": 12, "md": 6},
                            controls=[
                                ft.Container(
                                    bgcolor=CARD, border_radius=24, padding=24, expand=True, shadow=ft.BoxShadow(blur_radius=20, spread_radius=0, color="#1A000000", offset=ft.Offset(0, 8)),
                                    content=ft.Column(
                                        controls=[
                                            ft.Text(t("current_snapshot"), size=20, weight="bold", color=TEXT),
                                            ft.Row(controls=[stat_chip(t("current_age"), str(self.user.age), BLUE), stat_chip(t("current_weight"), f"{self.user.weight} kg", GREEN)], spacing=16),
                                            ft.Row(controls=[stat_chip(t("current_height"), f"{self.user.height} cm", ORANGE), stat_chip(t("current_goal"), self.user.goal, ACCENT)], spacing=16),
                                        ], spacing=16,
                                    ),
                                )
                            ]
                        )
                    ], run_spacing=16, spacing=16
                )
            ], spacing=24,
        )
        return shell(body)

# =========================================================
# MAIN / ROUTING
# =========================================================
def main(page: ft.Page):
    page.title = "Healthify"
    page.bgcolor = PAGE_BG
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.spacing = 0
    page.rtl = (LANG == "ar")

    try:
        page.window.width = 1400
        page.window.height = 920
        page.window.resizable = True
    except Exception:
        pass

    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    page.update()

    def build_view(route: str) -> ft.View:
        if route == "/": return SplashView(page)
        if route == "/welcome": return WelcomeView(page)
        if route == "/dashboard": return DashboardView(page)
        if route == "/meals": return MealsView(page)
        if route == "/workout": return WorkoutView(page)
        if route == "/analysis": return AnalysisView(page, file_picker)
        if route == "/stats": return StatsView(page)
        if route == "/profile": return ProfileView(page)
        return DashboardView(page)

    def route_change(e):
        page.views.clear()
        page.views.append(build_view(page.route or "/"))
        page.update()

    def view_pop(e):
        if len(page.views) > 1:
            page.views.pop()
            page.go(page.views[-1].route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go("/")

if __name__ == "__main__":
    ft.app(target=main)
