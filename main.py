import asyncio
import io
import json
import os
import re
import random
import shutil
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Callable, Dict, Optional

import flet as ft

# =========================================================
# THEME & CONFIGURATION
# =========================================================
DB_FILE = "healthify_db.json"
GEMINI_MODEL = "gemini-2.5-flash"
LANG = "ar"
ASSETS_DIR = "assets"
DEFAULTS_DIR = os.path.join(ASSETS_DIR, "defaults")

ADMIN_USER = "admin"
ADMIN_PASS = "123456"

for d in [ASSETS_DIR, os.path.join(ASSETS_DIR, "uploads"), DEFAULTS_DIR]:
    if not os.path.exists(d):
        os.makedirs(d)

def get_colors(is_dark: bool) -> dict:
    return {
        "PAGE_BG": "#0C0F12" if is_dark else "#F8F9FB",
        "CARD": "#181C25" if is_dark else "#FFFFFF",
        "CARD2": "#222733" if is_dark else "#F0F2F5",
        "CARD3": "#2D3445" if is_dark else "#E4E7EB",
        "TEXT": "#F3F4F6" if is_dark else "#111827",
        "SUB": "#9CA3AF" if is_dark else "#6B7280",
        "MUTED": "#6B7280" if is_dark else "#9CA3AF",
        "ACCENT": "#D4AF37" if is_dark else "#C59B27", 
        "ACCENT2": "#F3E5AB",
        "BLUE": "#3B82F6",
        "ORANGE": "#F59E0B",
        "RED": "#EF4444",
        "GREEN": "#10B981",
        "PURPLE": "#8B5CF6",
        "SHADOW": "#40000000" if is_dark else "#1A000000",
        "GLASS": "#AA181C25" if is_dark else "#EEFFFFFF"
    }

T_AR = {
    "dashboard": "الرئيسية", "meals": "الوجبات", "workout": "التمارين", "analysis": "تحليل AI", "stats": "الإحصائيات", "profile": "الملف",
    "welcome": "Healthify Pro", "welcome_sub": "صحة ذكية، تصميم فاخر", "today_summary": "ملخصك الصحي اليومي", 
    "quick_actions": "اختصارات سريعة", "water": "شرب الماء", "today_workout": "تمرين اليوم", "smart_tip": "نصيحة ذكية", 
    "generate_plan": "إنشاء الخطة الأسبوعية", "name": "الاسم", "age": "العمر", "gender": "الجنس", "height": "الطول (سم)", "weight": "الوزن (كجم)", 
    "activity": "مستوى النشاط", "goal": "الهدف", "api_key": "مفتاح Gemini API", "lose_weight": "تنحيف", "maintain": "تثبيت", 
    "gain_weight": "زيادة وزن", "save_profile": "حفظ وتحديث الخطة", "dashboard_title": "لوحة المتابعة", "dashboard_sub": "مؤشراتك اليومية وملخصك الصحي", 
    "daily_macros": "الماكروز اليومية", "daily_target": "الهدف اليومي", "meal_plan": "خطة الوجبات الأسبوعية", "nutrition_smart": "تغذية مخصصة لأهدافك", 
    "daily_nutrition_target": "الهدف الغذائي اليومي", "weekly_workout": "جدول التمارين الأسبوعي", "weekly_summary": "روتين أسبوعي متوازن",
    "food_analysis": "تحليل الطعام الذكي", "analysis_ready": "ارفع صورة طعامك لمعرفة مكوناته", "pick_image": "اختيار صورة طعام", "analyze": "تحليل الصورة", 
    "analysis_result": "النتيجة الذكية", "health_score": "التقييم الصحي", "stats_title": "الإحصائيات", "stats_sub": "تابع التقدم والالتزام", 
    "profile_title": "الملف الشخصي", "profile_sub": "عدّل بياناتك ليتم تحديث الخطة تلقائياً", "change_lang": "EN",
    "analyzing": "جاري تحليل الصورة بالذكاء الاصطناعي...", "error": "حدث خطأ", "current_goal": "الهدف", 
    "bmi": "مؤشر الكتلة", "calories": "سعرات", "protein": "بروتين", "carbs": "كارب", "fat": "دهون",
    "admin_panel": "لوحة الإدارة", "admin_login": "دخول المشرف", "admin_username": "المستخدم", "admin_password": "كلمة المرور", 
    "login": "دخول", "back": "عودة", "admin_dashboard": "لوحة تحكم الإدارة", 
    "admin_overview": "نظرة عامة", "admin_workouts": "التمارين", "admin_users": "إدارة الأعضاء", "admin_meals": "الوجبات",
    "add_meal": "إضافة وجبة جديدة", "edit_meal": "تعديل الوجبة", "delete": "حذف", "save": "حفظ", "cancel": "إلغاء",
    "meal_name": "اسم الوجبة", "meal_cal": "السعرات", "meal_desc": "الوصف", "upload_local_img": "اسم الصورة محلياً", "meal_type": "نوع الوجبة", "meal_goal": "الهدف المناسب",
    "add_workout": "إضافة تمرين", "edit_workout": "تعديل التمرين", "workout_title": "اسم التمرين", "workout_dur": "المدة (دقائق)", "workout_level": "المستوى",
    "easy": "مبتدئ", "medium": "متوسط", "hard": "متقدم", "day": "اليوم", "confirm_delete": "هل أنت متأكد من الحذف؟", "yes": "نعم", "no": "لا",
    "day_1": "اليوم 1", "day_2": "اليوم 2", "day_3": "اليوم 3", "day_4": "اليوم 4", "day_5": "اليوم 5", "day_6": "اليوم 6", "day_7": "اليوم 7",
    "pick_local_file": "رفع صورة"
}

T_EN = {
    "dashboard": "Dashboard", "meals": "Meals", "workout": "Workout", "analysis": "AI Analysis", "stats": "Stats", "profile": "Profile",
    "welcome": "Healthify Pro", "welcome_sub": "Smart health, premium design", "today_summary": "Daily Summary",
    "quick_actions": "Quick Actions", "water": "Water", "today_workout": "Today's Workout", "smart_tip": "Smart Tip", 
    "generate_plan": "Generate Weekly Plan", "name": "Name", "age": "Age", "gender": "Gender", "height": "Height (cm)", "weight": "Weight (kg)", 
    "activity": "Activity Level", "goal": "Goal", "api_key": "Gemini API Key", "lose_weight": "Lose Weight", "maintain": "Maintain", 
    "gain_weight": "Gain Weight", "save_profile": "Save & Auto-Update", "dashboard_title": "Dashboard", "dashboard_sub": "Your daily metrics", 
    "daily_macros": "Daily Macros", "daily_target": "Daily Target", "meal_plan": "Weekly Meal Plan", "nutrition_smart": "Tailored to your goals", 
    "weekly_workout": "Weekly Workout", "weekly_summary": "Balanced routine",
    "food_analysis": "AI Food Analysis", "analysis_ready": "Upload food image to analyze", "pick_image": "Pick Food Image", "analyze": "Analyze", 
    "analysis_result": "Smart Result", "health_score": "Health Score", "stats_title": "Stats", "stats_sub": "Track progress", 
    "profile_title": "Profile", "profile_sub": "Edit details to update plan", "change_lang": "عربي",
    "analyzing": "AI is analyzing image...", "error": "Error occurred", "current_goal": "Goal", 
    "bmi": "BMI", "calories": "Calories", "protein": "Protein", "carbs": "Carbs", "fat": "Fat",
    "admin_panel": "Admin Panel", "admin_login": "Admin Login", "admin_username": "Username", "admin_password": "Password", 
    "login": "Login", "back": "Back", "admin_dashboard": "Admin Dashboard", 
    "admin_overview": "Overview", "admin_workouts": "Workouts", "admin_users": "Users", "admin_meals": "Meals",
    "add_meal": "Add New Meal", "edit_meal": "Edit Meal", "delete": "Delete", "save": "Save", "cancel": "Cancel",
    "meal_name": "Meal Name", "meal_cal": "Calories", "meal_desc": "Description", "upload_local_img": "Local Image Name", "meal_type": "Meal Type", "meal_goal": "Target Goal",
    "add_workout": "Add Workout", "edit_workout": "Edit Workout", "workout_title": "Title", "workout_dur": "Duration (m)", "workout_level": "Level",
    "easy": "Beginner", "medium": "Intermediate", "hard": "Advanced", "day": "Day", "confirm_delete": "Are you sure to delete?", "yes": "Yes", "no": "No",
    "day_1": "Day 1", "day_2": "Day 2", "day_3": "Day 3", "day_4": "Day 4", "day_5": "Day 5", "day_6": "Day 6", "day_7": "Day 7",
    "pick_local_file": "Upload Image"
}

TRANSLATIONS = {"ar": T_AR, "en": T_EN}

def t(key: str) -> str: 
    return TRANSLATIONS.get(LANG, TRANSLATIONS["en"]).get(key, key)

def safe_int(val: Any, default: int) -> int:
    try: return int(float(val))
    except (ValueError, TypeError): return default

def safe_float(val: Any, default: float) -> float:
    try: return float(val)
    except (ValueError, TypeError): return default

# =========================================================
# MODEL / STORAGE & MASTER DATA
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
    api_key: str = ""
    is_setup: bool = False

DEFAULT_MEALS = [
    {"id": "m1", "name": "سلطة كينوا ودجاج", "cal": 350, "desc": "غنية بالألياف والبروتين", "type": "الغداء", "goal": "Lose Weight", "img": "defaults/m1.png"},
    {"id": "m2", "name": "شوفان بالتوت البري", "cal": 280, "desc": "طاقة صباحية خفيفة", "type": "الفطور", "goal": "Lose Weight", "img": "defaults/m2.png"},
    {"id": "m3", "name": "سلمون مشوي مع هليون", "cal": 400, "desc": "أوميجا 3 منخفض الكارب", "type": "العشاء", "goal": "Lose Weight", "img": "defaults/m3.png"},
    {"id": "m4", "name": "زبادي يوناني ولوز", "cal": 150, "desc": "سناك بروتين", "type": "سناك", "goal": "Lose Weight", "img": "defaults/m4.png"},
    {"id": "m6", "name": "باستا بيستو بالدجاج", "cal": 750, "desc": "كربوهيدرات معقدة", "type": "الغداء", "goal": "Gain Weight", "img": "defaults/m5.png"},
    {"id": "m7", "name": "سموثي زبدة الفول والموز", "cal": 600, "desc": "سائل عالي السعرات", "type": "الفطور", "goal": "Gain Weight", "img": "defaults/m6.png"},
    {"id": "m10", "name": "ساندويتش ديك رومي", "cal": 450, "desc": "توازن مثالي للعمل", "type": "الغداء", "goal": "Maintain", "img": "defaults/m7.png"},
]

DEFAULT_WORKOUTS = [
    {"id": "w1", "title": "HIIT كارديو حارق", "dur": 30, "level": "hard", "cal": 400, "img": "defaults/w1.png"},
    {"id": "w2", "title": "مقاومة جزء علوي", "dur": 45, "level": "medium", "cal": 350, "img": "defaults/w2.png"},
    {"id": "w3", "title": "مشي سريع (جهاز)", "dur": 40, "level": "easy", "cal": 250, "img": "defaults/w3.png"},
]

def default_db() -> Dict[str, Any]:
    return {
        "user": asdict(UserProfile()), 
        "weight_history": [], 
        "master_meals": DEFAULT_MEALS.copy(),
        "master_workouts": DEFAULT_WORKOUTS.copy(),
        "weekly_plan": {"meals": {}, "workouts": {}} 
    }

def load_db() -> Dict[str, Any]:
    if not os.path.exists(DB_FILE): return default_db()
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f: 
            db = json.load(f)
            if "master_meals" not in db: db["master_meals"] = DEFAULT_MEALS.copy()
            if "master_workouts" not in db: db["master_workouts"] = DEFAULT_WORKOUTS.copy()
            if "weekly_plan" not in db: db["weekly_plan"] = {"meals": {}, "workouts": {}}
            return db
    except Exception: return default_db()

def save_db(db: Dict[str, Any]) -> None:
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f: 
            json.dump(db, f, ensure_ascii=False, indent=2)
    except Exception: pass

def load_user() -> UserProfile:
    try: return UserProfile(**load_db().get("user", asdict(UserProfile())))
    except Exception: return UserProfile()

def save_user(user: UserProfile) -> None:
    db = load_db()
    db["user"] = asdict(user)
    hist = db.setdefault("weight_history", [])
    hist.append({"day": datetime.now().strftime("%a"), "weight": float(user.weight)})
    db["weight_history"] = hist[-14:]
    save_db(db)

def clear_user_data() -> None:
    db = load_db()
    db["user"] = asdict(UserProfile())
    db["weekly_plan"] = {"meals": {}, "workouts": {}}
    db["weight_history"] = []
    save_db(db)

# =========================================================
# HEALTH LOGIC
# =========================================================
def normalize_gender(value: Optional[str]) -> str: 
    return "Male" if value in ("Male", "ذكر") else "Female"

def normalize_activity(value: Optional[str]) -> str:
    m = {"Sedentary": "Sedentary", "خامل": "Sedentary", "Light": "Light", "خفيف": "Light", "Moderate": "Moderate", "متوسط": "Moderate", "Active": "Active", "نشط": "Active", "Very Active": "Very Active", "نشط جداً": "Very Active"}
    return m.get(value, "Moderate")

def auto_determine_goal(weight: float, height: float) -> str:
    h_m = max(height / 100.0, 0.01)
    bmi = weight / (h_m ** 2)
    if bmi < 18.5: return "Gain Weight"
    elif bmi < 25.0: return "Maintain"
    else: return "Lose Weight"

def calculate_metrics(user: UserProfile) -> Dict[str, Any]:
    h_m = max(user.height / 100.0, 0.01)
    bmi = round(user.weight / (h_m ** 2), 1)
    bmi_status = "Underweight" if bmi < 18.5 else "Normal" if bmi < 25 else "Overweight" if bmi < 30 else "Obese"
    
    if user.gender == "Male": bmr = (10 * user.weight) + (6.25 * user.height) - (5 * user.age) + 5
    else: bmr = (10 * user.weight) + (6.25 * user.height) - (5 * user.age) - 161

    tdee = bmr * {"Sedentary": 1.2, "Light": 1.375, "Moderate": 1.55, "Active": 1.725, "Very Active": 1.9}.get(user.activity_level, 1.55)
    
    if user.goal == "Lose Weight": target = tdee - 500
    elif user.goal == "Gain Weight": target = tdee + 300
    else: target = tdee

    target = int(max(target, 1200))
    return {
        "bmi": bmi, "bmi_status": bmi_status, "bmr": int(bmr), "tdee": int(tdee), 
        "target_calories": target, "protein": int((target * 0.30) / 4), 
        "carbs": int((target * 0.40) / 4), "fats": int((target * 0.30) / 9)
    }

def generate_weekly_plan(user: UserProfile):
    db = load_db()
    goal = user.goal
    
    suitable_meals = [m for m in db["master_meals"] if m.get("goal") == goal]
    if len(suitable_meals) < 3: suitable_meals = db["master_meals"]

    breakfsts = [m for m in suitable_meals if m.get("type") in ("الفطور", "Breakfast")]
    lunches = [m for m in suitable_meals if m.get("type") in ("الغداء", "Lunch")]
    dinners = [m for m in suitable_meals if m.get("type") in ("العشاء", "Dinner")]
    snacks = [m for m in suitable_meals if m.get("type") in ("سناك", "Snack")]

    if not breakfsts: breakfsts = suitable_meals
    if not lunches: lunches = suitable_meals
    if not dinners: dinners = suitable_meals
    if not snacks: snacks = suitable_meals

    all_workouts = db.get("master_workouts", [])
    if not all_workouts: all_workouts = DEFAULT_WORKOUTS

    weekly_meals = {}
    weekly_workouts = {}

    for day in range(1, 8):
        daily_m = [
            random.choice(breakfsts),
            random.choice(lunches),
            random.choice(dinners),
            random.choice(snacks)
        ]
        weekly_meals[str(day)] = daily_m
        
        if day % 3 == 0:
            w = next((x for x in all_workouts if x.get("level") == "easy"), random.choice(all_workouts))
        else:
            w = random.choice(all_workouts)
        weekly_workouts[str(day)] = w

    db["weekly_plan"] = {"meals": weekly_meals, "workouts": weekly_workouts}
    save_db(db)

# =========================================================
# AI FOOD ANALYZER
# =========================================================
class GeminiFoodAnalyzer:
    @staticmethod
    def analyze(api_key: str, image_bytes: bytes) -> Dict[str, Any]:
        if not api_key: return {"error": "no_key"}
        try:
            import google.generativeai as genai
            from PIL import Image as PILImage
            genai.configure(api_key=api_key.strip())
            model = genai.GenerativeModel(GEMINI_MODEL)
            prompt = (
                "Analyze this meal image and return ONLY a valid JSON object with these exact keys: "
                "name (string), calories (number), protein_g (number), carbs_g (number), fat_g (number), "
                "health_score (number out of 100), short_advice (string). "
                f"Write the 'short_advice' and 'name' completely in {'Arabic' if LANG == 'ar' else 'English'}. "
            )
            image = PILImage.open(io.BytesIO(image_bytes))
            res = model.generate_content([prompt, image]).text.strip()
            
            bt = "`" * 3
            pattern = r"^" + bt + r"(?:json)?\s*|\s*" + bt + r"$"
            cleaned = re.sub(pattern, "", res, flags=re.IGNORECASE)
            
            try: 
                return json.loads(cleaned)
            except Exception:
                m = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
                return json.loads(m.group(0)) if m else {}
        except Exception as ex: 
            return {"error": str(ex)}

# =========================================================
# UI HELPERS (المحاذاة المركزية الصارمة)
# =========================================================
def shell(body: ft.Control, c: dict) -> ft.Container:
    return ft.Container(
        expand=True, bgcolor=c["PAGE_BG"], 
        content=ft.Column(
            controls=[ft.Container(padding=ft.padding.only(left=20, top=24, right=20, bottom=110), content=body)], 
            scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True
        )
    )

def nav_bar(index: int, go: Callable[[str], None], c: dict) -> ft.Container:
    routes = ["/dashboard", "/meals", "/workout", "/analysis", "/profile"]
    labels = [t("dashboard"), t("meals"), t("workout"), t("analysis"), t("profile")]
    icons = [ft.Icons.HOME_ROUNDED, ft.Icons.RESTAURANT_MENU_ROUNDED, ft.Icons.FITNESS_CENTER_ROUNDED, ft.Icons.CAMERA_ENHANCE_ROUNDED, ft.Icons.PERSON_ROUNDED]
    
    tabs = []
    for i in range(5):
        is_sel = (i == index)
        color = c["ACCENT"] if is_sel else c["SUB"]
        bg = c["CARD3"] if is_sel else "transparent"
        tabs.append(
            ft.Container(
                content=ft.Column([ft.Icon(icons[i], color=color, size=24), ft.Text(labels[i], size=10, color=color, weight="bold" if is_sel else "normal")], alignment=ft.MainAxisAlignment.CENTER, spacing=2),
                padding=ft.padding.symmetric(horizontal=10, vertical=8), border_radius=16, bgcolor=bg, ink=True, on_click=lambda e, r=routes[i]: go(r)
            )
        )
        
    return ft.Container(
        bottom=20, left=20, right=20, height=80, border_radius=24, bgcolor=c["CARD"],
        shadow=ft.BoxShadow(blur_radius=30, color=c["SHADOW"], offset=ft.Offset(0, 10)),
        content=ft.Row(tabs, alignment=ft.MainAxisAlignment.SPACE_AROUND, vertical_alignment=ft.CrossAxisAlignment.CENTER)
    )

def header(page: ft.Page, title_text: str, sub_text: str) -> ft.Row:
    c = get_colors(page.theme_mode == ft.ThemeMode.DARK)
    t_icon = ft.Icons.LIGHT_MODE_ROUNDED if page.theme_mode == ft.ThemeMode.DARK else ft.Icons.DARK_MODE_ROUNDED
    return ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Column(controls=[ft.Text(title_text, size=32, weight="bold", color=c["TEXT"]), ft.Text(sub_text, size=14, color=c["SUB"])], spacing=4, expand=True),
            ft.Row([
                ft.IconButton(icon=ft.Icons.ADMIN_PANEL_SETTINGS_ROUNDED, icon_color=c["MUTED"], on_click=lambda e: page.go("/admin_login")),
                ft.IconButton(icon=t_icon, icon_color=c["ACCENT"], on_click=getattr(page, "toggle_theme", None)), 
            ], spacing=5),
        ],
    )

def stat_card(icon, title: str, val: str, color: str, c: dict) -> ft.Container:
    return ft.Container(
        expand=True, padding=20, border_radius=24, bgcolor=c["CARD"],
        border=ft.border.all(1, c["CARD3"]),
        content=ft.Column([
            ft.Container(width=48, height=48, border_radius=14, bgcolor=f"{color}22", content=ft.Icon(icon, color=color, size=24), alignment=ft.Alignment(0,0)),
            ft.Text(val, size=24, weight="w800", color=c["TEXT"]),
            ft.Text(title, size=13, color=c["SUB"])
        ], spacing=8)
    )

def safe_image(src: str) -> Optional[ft.DecorationImage]:
    return ft.DecorationImage(src=src, fit=ft.ImageFit.COVER) if src else None

def get_black_btn_text(text: str) -> ft.Control:
    return ft.Text(text, color="black", weight="bold", size=16)

# =========================================================
# APP VIEWS
# =========================================================
class SplashView(ft.View):
    def __init__(self, page: ft.Page):
        self.c = get_colors(page.theme_mode == ft.ThemeMode.DARK)
        super().__init__(route="/splash", bgcolor=self.c["PAGE_BG"], scroll=None)
        self.page = page
        
        self.controls = [
            ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                content=ft.Column([
                    ft.Icon(ft.Icons.HEALTH_AND_SAFETY_ROUNDED, size=100, color=self.c["ACCENT"]),
                    ft.Text("Healthify Pro", size=45, weight="w900", color=self.c["TEXT"]),
                    ft.Text("تطبيق ذكي لإدارة صحتك", size=16, color=self.c["SUB"]),
                    ft.Container(height=30),
                    ft.ProgressRing(color=self.c["ACCENT"], stroke_width=4, width=40, height=40)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, spacing=10)
            )
        ]

    def did_mount(self):
        self.page.run_task(self.go_next)

    async def go_next(self):
        await asyncio.sleep(2.5) 
        user = load_user()
        if not user.is_setup:
            self.page.go("/welcome")
        else:
            self.page.go("/dashboard")

class WelcomeView(ft.View):
    def __init__(self, page: ft.Page):
        self.c = get_colors(page.theme_mode == ft.ThemeMode.DARK)
        super().__init__(route="/welcome", bgcolor=self.c["PAGE_BG"], scroll=None)
        self.page = page
        user = load_user()

        def tf(label, val): return ft.TextField(label=label, value=val, filled=True, fill_color=self.c["CARD"], border_color=self.c["CARD3"], focused_border_color=self.c["ACCENT"], border_radius=16, color=self.c["TEXT"])
        def drop(label, val, opts): return ft.Dropdown(label=label, value=val, filled=True, fill_color=self.c["CARD"], border_color=self.c["CARD3"], focused_border_color=self.c["ACCENT"], border_radius=16, color=self.c["TEXT"], options=[ft.dropdown.Option(x) for x in opts])

        self.name_in = tf(t("name"), user.name)
        self.age_in = tf(t("age"), str(user.age))
        self.gender_in = drop(t("gender"), "Male" if user.gender == "Male" else "Female", ["Male", "Female", "ذكر", "أنثى"])
        self.height_in = tf(t("height"), str(user.height))
        self.weight_in = tf(t("weight"), str(user.weight))
        self.activity_in = drop(t("activity"), "Moderate", ["Sedentary", "Light", "Moderate", "Active", "Very Active"])
        self.controls = [self.build_body()]

    def build_body(self) -> ft.Control:
        def save_profile(e):
            w = max(20.0, safe_float(self.weight_in.value, 70.0))
            h = max(50.0, safe_float(self.height_in.value, 170.0))
            smart_goal = auto_determine_goal(w, h)
            updated = UserProfile(
                name=(self.name_in.value or "").strip() or "User", age=max(1, safe_int(self.age_in.value, 25)),
                gender=normalize_gender(self.gender_in.value), height=h,
                weight=w, activity_level=normalize_activity(self.activity_in.value),
                goal=smart_goal, is_setup=True, api_key=load_user().api_key 
            )
            save_user(updated)
            generate_weekly_plan(updated)
            self.page.go("/dashboard")

        form_card = ft.Container(
            width=480,
            bgcolor=self.c["CARD"], border_radius=24, padding=30, border=ft.border.all(1, self.c["CARD3"]),
            shadow=ft.BoxShadow(blur_radius=30, color=self.c["SHADOW"]),
            content=ft.Column(
                controls=[
                    ft.Column(controls=[
                        ft.Icon(ft.Icons.FAVORITE_ROUNDED, size=50, color=self.c["ACCENT"]),
                        ft.Text(t("welcome"), size=32, weight="w900", color=self.c["TEXT"]), 
                        ft.Text(t("welcome_sub"), size=14, color=self.c["SUB"])
                    ], spacing=6, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Container(height=10),
                    self.name_in, 
                    ft.Row(controls=[ft.Container(expand=True, content=self.age_in), ft.Container(expand=True, content=self.gender_in)], spacing=15),
                    ft.Row(controls=[ft.Container(expand=True, content=self.height_in), ft.Container(expand=True, content=self.weight_in)], spacing=15),
                    self.activity_in, 
                    ft.Container(height=10),
                    ft.ElevatedButton(content=get_black_btn_text(t("generate_plan")), bgcolor=self.c["ACCENT"], height=60, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=16)), on_click=save_profile),
                ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.STRETCH
            )
        )
        return shell(ft.Row([form_card], alignment=ft.MainAxisAlignment.CENTER), self.c)

class DashboardView(ft.View):
    def __init__(self, page: ft.Page):
        self.c = get_colors(page.theme_mode == ft.ThemeMode.DARK)
        super().__init__(route="/dashboard", bgcolor=self.c["PAGE_BG"], scroll=None)
        self.page = page
        self.user = load_user()
        self.metrics = calculate_metrics(self.user)
        self.smart_tip_text = ft.Text("حافظ على شرب الماء والنوم الكافي للوصول لهدفك.", size=16, color=self.c["TEXT"])
        self.controls = [
            ft.Stack([
                shell(self.build_body(), self.c),
                nav_bar(0, self.page.go, self.c)
            ], expand=True)
        ]

    def did_mount(self):
        self.page.run_task(self.fetch_smart_tip)

    async def fetch_smart_tip(self):
        if not self.user.api_key.strip(): return
        try:
            self.smart_tip_text.value = "جاري استنتاج نصيحة مخصصة..." if LANG == 'ar' else "Generating AI tip..."
            self.update()
            import google.generativeai as genai
            genai.configure(api_key=self.user.api_key.strip())
            model = genai.GenerativeModel(GEMINI_MODEL)
            prompt = f"أنت مدرب صحي محترف. اكتب نصيحة قصيرة جدا (جملة واحدة فقط) للمستخدم. عمره {self.user.age}، هدفه {self.user.goal}. باللغة {'العربية' if LANG=='ar' else 'English'} وبدون أي تنسيق."
            response = await asyncio.to_thread(model.generate_content, prompt)
            if response and response.text:
                self.smart_tip_text.value = response.text.strip()
                self.update()
        except Exception: pass

    def build_body(self) -> ft.Control:
        return ft.Column(
            controls=[
                header(self.page, t("dashboard_title"), t("dashboard_sub")),
                ft.Container(height=10),
                ft.ResponsiveRow([
                    ft.Column(col={"xs": 6, "md": 3}, controls=[stat_card(ft.Icons.MONITOR_WEIGHT_ROUNDED, t("bmi"), str(self.metrics["bmi"]), self.c["ACCENT"], self.c)]),
                    ft.Column(col={"xs": 6, "md": 3}, controls=[stat_card(ft.Icons.LOCAL_FIRE_DEPARTMENT_ROUNDED, t("daily_target"), str(self.metrics["target_calories"]), self.c["ORANGE"], self.c)]),
                    ft.Column(col={"xs": 6, "md": 3}, controls=[stat_card(ft.Icons.SET_MEAL_ROUNDED, t("protein"), f'{self.metrics["protein"]}g', self.c["BLUE"], self.c)]),
                    ft.Column(col={"xs": 6, "md": 3}, controls=[stat_card(ft.Icons.GRAIN_ROUNDED, t("carbs"), f'{self.metrics["carbs"]}g', self.c["GREEN"], self.c)]),
                ], run_spacing=20, spacing=20),
                
                ft.Container(height=20),
                ft.Container(
                    bgcolor=self.c["CARD"], border_radius=24, padding=30, border=ft.border.all(1, self.c["CARD3"]),
                    content=ft.Row([
                        ft.Container(width=60, height=60, border_radius=20, bgcolor=f'{self.c["ACCENT"]}22', content=ft.Icon(ft.Icons.AUTO_AWESOME_ROUNDED, color=self.c["ACCENT"], size=30)),
                        ft.Column([
                            ft.Text(t("smart_tip"), size=14, weight="bold", color=self.c["ACCENT"]),
                            self.smart_tip_text
                        ], expand=True, spacing=4)
                    ])
                ),
            ], spacing=20,
        )

class MealsView(ft.View):
    def __init__(self, page: ft.Page):
        self.c = get_colors(page.theme_mode == ft.ThemeMode.DARK)
        super().__init__(route="/meals", bgcolor=self.c["PAGE_BG"], scroll=None)
        self.page = page
        self.db = load_db()
        self.selected_day = "1"
        self.controls = [
            ft.Stack([
                shell(self.build_body(), self.c),
                nav_bar(1, self.page.go, self.c)
            ], expand=True)
        ]

    def build_body(self):
        plan = self.db.get("weekly_plan", {}).get("meals", {})
        meals = plan.get(self.selected_day, [])
        
        day_tabs = []
        for d in range(1, 8):
            ds = str(d)
            is_sel = (ds == self.selected_day)
            day_tabs.append(
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=20, vertical=10), border_radius=20,
                    bgcolor=self.c["ACCENT"] if is_sel else self.c["CARD"],
                    content=ft.Text(t(f"day_{d}"), weight="bold", color="black" if is_sel else self.c["SUB"]),
                    ink=True, on_click=lambda e, d_str=ds: self.change_day(d_str)
                )
            )

        cards = []
        for m in meals:
            cards.append(ft.Column(col={"xs": 12, "md": 6, "lg": 4}, controls=[
                ft.Container(
                    bgcolor=self.c["CARD"], border_radius=24, padding=20, border=ft.border.all(1, self.c["CARD3"]),
                    content=ft.Row([
                        ft.Container(width=100, height=100, border_radius=18, image=safe_image(m.get("img")), bgcolor=self.c["CARD3"]),
                        ft.Column([
                            ft.Container(padding=ft.padding.symmetric(horizontal=10, vertical=4), border_radius=8, bgcolor=f'{self.c["ACCENT"]}22', content=ft.Text(m.get("type", "Meal"), size=12, color=self.c["ACCENT"], weight="bold")),
                            ft.Text(m["name"], size=20, weight="w800", color=self.c["TEXT"]), 
                            ft.Text(m.get("desc", ""), size=13, color=self.c["SUB"]),
                            ft.Text(f'{m["cal"]} kcal', size=14, weight="bold", color=self.c["ORANGE"]),
                        ], expand=True, spacing=6)
                    ])
                )
            ]))
            
        return ft.Column([
            header(self.page, t("meal_plan"), t("nutrition_smart")),
            ft.Row(day_tabs, scroll=ft.ScrollMode.AUTO, spacing=10),
            ft.Container(height=10),
            ft.ResponsiveRow(cards, run_spacing=20, spacing=20)
        ])

    def change_day(self, day_str):
        self.selected_day = day_str
        self.controls[0].controls[0] = shell(self.build_body(), self.c)
        self.update()

class WorkoutView(ft.View):
    def __init__(self, page: ft.Page):
        self.c = get_colors(page.theme_mode == ft.ThemeMode.DARK)
        super().__init__(route="/workout", bgcolor=self.c["PAGE_BG"], scroll=None)
        self.page = page
        self.db = load_db()
        self.controls = [
            ft.Stack([
                shell(self.build_body(), self.c),
                nav_bar(2, self.page.go, self.c)
            ], expand=True)
        ]

    def build_body(self):
        plan = self.db.get("weekly_plan", {}).get("workouts", {})
        
        cards = []
        for d in range(1, 8):
            w = plan.get(str(d), {})
            if not w: continue
            
            lvl_color = self.c["GREEN"] if w.get("level") == "easy" else self.c["ORANGE"] if w.get("level") == "medium" else self.c["RED"]
            
            cards.append(ft.Column(col={"xs": 12, "md": 6, "lg": 4}, controls=[
                ft.Container(
                    bgcolor=self.c["CARD"], border_radius=24, padding=20, border=ft.border.all(1, self.c["CARD3"]),
                    content=ft.Row([
                        ft.Container(width=90, height=90, border_radius=18, image=safe_image(w.get("img")), bgcolor=self.c["CARD3"]),
                        ft.Column([
                            ft.Text(f'{t("day")} {d}', size=14, color=self.c["ACCENT"], weight="bold"),
                            ft.Text(w.get("title",""), size=20, weight="w800", color=self.c["TEXT"]), 
                            ft.Row([
                                ft.Icon(ft.Icons.TIMER_ROUNDED, size=16, color=self.c["SUB"]), ft.Text(f'{w.get("dur",0)} min', size=13, color=self.c["SUB"]),
                                ft.Icon(ft.Icons.LOCAL_FIRE_DEPARTMENT_ROUNDED, size=16, color=self.c["SUB"]), ft.Text(f'{w.get("cal",0)} kcal', size=13, color=self.c["SUB"])
                            ]),
                            ft.Container(padding=ft.padding.symmetric(horizontal=8, vertical=2), border_radius=6, border=ft.border.all(1, lvl_color), content=ft.Text(t(w.get("level","")), size=10, color=lvl_color))
                        ], expand=True, spacing=6)
                    ])
                )
            ]))
            
        return ft.Column([
            header(self.page, t("weekly_workout"), t("weekly_summary")),
            ft.Container(height=10),
            ft.ResponsiveRow(cards, run_spacing=20, spacing=20)
        ])

class AnalysisView(ft.View):
    def __init__(self, page: ft.Page):
        self.c = get_colors(page.theme_mode == ft.ThemeMode.DARK)
        super().__init__(route="/analysis", bgcolor=self.c["PAGE_BG"], scroll=None)
        self.page = page
        self.result = None
        self.loading = False
        
        self.fp = ft.FilePicker(on_result=self.on_pick)
        self.page.overlay.append(self.fp)
        
        self.controls = [
            ft.Stack([
                shell(self.build_body(), self.c),
                nav_bar(3, self.page.go, self.c)
            ], expand=True)
        ]

    def on_pick(self, e):
        if not e.files: return
        self.start_analysis(e.files[0].path)
        
    def start_analysis(self, path):
        self.loading = True
        self.update_ui()
        self.page.run_task(self.analyze_task, path)
        
    async def analyze_task(self, path):
        user = load_user()
        try:
            with open(path, "rb") as f:
                img_bytes = f.read()
            res = await asyncio.to_thread(GeminiFoodAnalyzer.analyze, user.api_key, img_bytes)
            if "error" in res:
                self.result = {"name": "غير متوفر / خطأ", "calories": 0, "short_advice": "تأكد من إعداد مفتاح API في الملف الشخصي."}
            else:
                self.result = res
        except Exception as ex:
            self.result = {"name": "خطأ", "short_advice": str(ex)}
            
        self.loading = False
        self.update_ui()

    def update_ui(self):
        self.controls[0].controls[0] = shell(self.build_body(), self.c)
        self.update()

    def build_body(self):
        content = [header(self.page, t("food_analysis"), t("analysis_ready")), ft.Container(height=20)]
        
        if self.loading:
            content.append(ft.Container(
                alignment=ft.alignment.center, padding=100,
                content=ft.Column([
                    ft.ProgressRing(color=self.c["ACCENT"], stroke_width=6, width=60, height=60), 
                    ft.Container(height=20),
                    ft.Text(t("analyzing"), color=self.c["SUB"], size=18)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            ))
        elif self.result:
            score = self.result.get("health_score", 0)
            score_color = self.c["GREEN"] if score > 75 else self.c["ORANGE"] if score > 40 else self.c["RED"]
            
            def macro_ring(label, val, color):
                return ft.Container(
                    expand=True, bgcolor=self.c["CARD2"], border_radius=20, padding=20,
                    content=ft.Column([
                        ft.Stack([
                            ft.ProgressRing(value=1.0, color=f"{color}22", width=60, height=60, stroke_width=8),
                            ft.ProgressRing(value=min(1.0, val/100) if val else 0.5, color=color, width=60, height=60, stroke_width=8),
                            ft.Container(width=60, height=60, alignment=ft.Alignment(0,0), content=ft.Text(f"{val}g", weight="bold", size=14, color=self.c["TEXT"]))
                        ]),
                        ft.Text(label, color=self.c["SUB"], size=14)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                )

            res_card = ft.Container(
                width=550,
                bgcolor=self.c["CARD"], padding=35, border_radius=24, border=ft.border.all(1, self.c["CARD3"]),
                shadow=ft.BoxShadow(blur_radius=30, color=self.c["SHADOW"]),
                content=ft.Column([
                    ft.Row([
                        ft.Column([
                            ft.Text(t("analysis_result"), color=self.c["ACCENT"], size=14, weight="bold"),
                            ft.Text(self.result.get("name", "وجبة صحية"), size=36, weight="w900", color=self.c["TEXT"]),
                            ft.Text(f'{self.result.get("calories", 0)} kcal', size=24, color=self.c["ORANGE"], weight="bold"),
                        ], expand=True),
                        ft.Stack([
                            ft.ProgressRing(value=1.0, color=f"{score_color}22", width=100, height=100, stroke_width=12),
                            ft.ProgressRing(value=score/100, color=score_color, width=100, height=100, stroke_width=12),
                            ft.Container(width=100, height=100, alignment=ft.Alignment(0,0), content=ft.Column([
                                ft.Text(str(score), weight="w900", size=28, color=self.c["TEXT"]),
                                ft.Text("/100", size=10, color=self.c["SUB"])
                            ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER))
                        ])
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    
                    ft.Container(height=20),
                    ft.Text(self.result.get("short_advice", ""), color=self.c["SUB"], size=18, italic=True),
                    ft.Container(height=30),
                    
                    ft.Row([
                        macro_ring(t("protein"), self.result.get('protein_g', 0), self.c["BLUE"]),
                        macro_ring(t("carbs"), self.result.get('carbs_g', 0), self.c["GREEN"]),
                        macro_ring(t("fat"), self.result.get('fat_g', 0), self.c["RED"]),
                    ], spacing=20)
                ])
            )
            content.append(ft.Row([res_card], alignment=ft.MainAxisAlignment.CENTER))
            
        content.append(ft.Container(height=40))
        content.append(
            ft.Container(
                alignment=ft.alignment.center,
                content=ft.ElevatedButton(
                    content=ft.Row([ft.Icon(ft.Icons.CAMERA_ALT_ROUNDED, color="#000000"), get_black_btn_text(t("pick_image"))], alignment=ft.MainAxisAlignment.CENTER),
                    on_click=lambda e: self.fp.pick_files(file_type=ft.FilePickerFileType.IMAGE), 
                    bgcolor=self.c["ACCENT"], height=60, 
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20), padding=ft.padding.symmetric(horizontal=40))
                )
            )
        )
        return ft.Column(content)

class ProfileView(ft.View):
    def __init__(self, page: ft.Page):
        self.c = get_colors(page.theme_mode == ft.ThemeMode.DARK)
        super().__init__(route="/profile", bgcolor=self.c["PAGE_BG"], scroll=None)
        self.page = page
        self.user = load_user()
        self.controls = [
            ft.Stack([
                shell(self.build_body(), self.c),
                nav_bar(4, self.page.go, self.c)
            ], expand=True)
        ]

    def build_body(self) -> ft.Control:
        def field(label, val, pwd=False): return ft.TextField(label=label, value=val, filled=True, fill_color=self.c["CARD"], border_color=self.c["CARD3"], focused_border_color=self.c["ACCENT"], border_radius=16, color=self.c["TEXT"], password=pwd, can_reveal_password=pwd)
        def dropdown(label, val, opts): return ft.Dropdown(label=label, value=val, filled=True, fill_color=self.c["CARD"], border_color=self.c["CARD3"], focused_border_color=self.c["ACCENT"], border_radius=16, color=self.c["TEXT"], options=[ft.dropdown.Option(opt) for opt in opts])

        name = field(t("name"), self.user.name)
        age = field(t("age"), str(self.user.age))
        gender_opts = ["Male", "Female"] if LANG == "en" else ["ذكر", "أنثى"]
        activity_opts = ["Sedentary", "Light", "Moderate", "Active", "Very Active"] if LANG == "en" else ["خامل", "خفيف", "متوسط", "نشط", "نشط جداً"]
        
        gender = dropdown(t("gender"), "Male" if self.user.gender == "Male" else "Female", gender_opts)
        height = field(t("height"), str(self.user.height))
        weight = field(t("weight"), str(self.user.weight))
        activity = dropdown(t("activity"), self.user.activity_level, activity_opts)
        api_key = field(t("api_key"), self.user.api_key, pwd=True)

        def save_profile(e):
            w = max(20.0, safe_float(weight.value, 70.0))
            h = max(50.0, safe_float(height.value, 170.0))
            smart_goal = auto_determine_goal(w, h)
            updated = UserProfile(
                name=(name.value or "").strip() or "User", age=max(1, safe_int(age.value, 25)),
                gender=normalize_gender(gender.value), height=h,
                weight=w, activity_level=normalize_activity(activity.value),
                goal=smart_goal, api_key=(api_key.value or "").strip(), is_setup=True,
            )
            save_user(updated)
            generate_weekly_plan(updated)
            self.page.go("/dashboard")

        form_card = ft.Container(
            width=500,
            bgcolor=self.c["CARD"], border_radius=24, padding=30, border=ft.border.all(1, self.c["CARD3"]),
            shadow=ft.BoxShadow(blur_radius=30, color=self.c["SHADOW"]),
            content=ft.Column(
                controls=[
                    ft.Row([
                        ft.Container(width=65, height=60, border_radius=16, bgcolor=f'{self.c["ACCENT"]}22', alignment=ft.Alignment(0, 0), content=ft.Icon(ft.Icons.PERSON, color=self.c["ACCENT"], size=32)),
                        ft.Column(controls=[ft.Text(self.user.name or "User", size=24, weight="bold", color=self.c["TEXT"]), ft.Text(f'{t("goal")}: {t(self.user.goal)}', size=14, color=self.c["SUB"])], spacing=2),
                    ], spacing=15),
                    ft.Container(height=10),
                    name, ft.Row([ft.Container(expand=True, content=age), ft.Container(expand=True, content=gender)], spacing=20),
                    ft.Row([ft.Container(expand=True, content=height), ft.Container(expand=True, content=weight)], spacing=20),
                    activity, api_key, 
                    ft.Container(height=10),
                    ft.ElevatedButton(content=get_black_btn_text(t("save_profile")), bgcolor=self.c["ACCENT"], height=60, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)), on_click=save_profile),
                    ft.Container(height=55, border_radius=16, bgcolor=self.c["CARD2"], alignment=ft.Alignment(0, 0), ink=True, on_click=getattr(self.page, "toggle_lang", None), content=ft.Text(t("change_lang"), size=14, weight="bold", color=self.c["TEXT"])),
                ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.STRETCH
            ),
        )
        
        return ft.Column([
            header(self.page, t("profile_title"), t("profile_sub")),
            ft.Container(height=20),
            ft.Row([form_card], alignment=ft.MainAxisAlignment.CENTER)
        ])

# =========================================================
# ADMIN PANEL VIEWS
# =========================================================
class AdminLoginView(ft.View):
    def __init__(self, page: ft.Page):
        self.c = get_colors(page.theme_mode == ft.ThemeMode.DARK)
        super().__init__(route="/admin_login", bgcolor=self.c["PAGE_BG"], scroll=None)
        self.page = page
        
        u_in = ft.TextField(label=t("admin_username"), border_color=self.c["CARD3"], color=self.c["TEXT"], border_radius=12)
        p_in = ft.TextField(label=t("admin_password"), password=True, can_reveal_password=True, border_color=self.c["CARD3"], color=self.c["TEXT"], border_radius=12)
        err = ft.Text("", color=self.c["RED"], size=13)
        
        def do_login(e):
            if u_in.value == ADMIN_USER and p_in.value == ADMIN_PASS: 
                self.page.go("/admin_dashboard")
            else:
                err.value = "بيانات الدخول غير صحيحة" if LANG == 'ar' else "Invalid credentials"
                self.update()
                
        form_card = ft.Container(
            width=400,
            bgcolor=self.c["CARD"], padding=35, border_radius=24, 
            shadow=ft.BoxShadow(blur_radius=30, color=self.c["SHADOW"]),
            content=ft.Column([
                ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS_ROUNDED, size=60, color=self.c["ACCENT"]), 
                ft.Text(t("admin_login"), size=28, weight="bold", color=self.c["TEXT"]), 
                ft.Container(height=10), u_in, p_in, err, 
                ft.Container(height=10),
                ft.ElevatedButton(content=get_black_btn_text(t("login")), bgcolor=self.c["ACCENT"], height=50, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)), on_click=do_login), 
                ft.TextButton(t("back"), on_click=lambda e: self.page.go("/dashboard"))
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
        )
                
        self.controls = [
            ft.Container(
                expand=True, alignment=ft.alignment.center, padding=20,
                content=ft.Row([form_card], alignment=ft.MainAxisAlignment.CENTER)
            )
        ]

class AdminDashboardView(ft.View):
    def __init__(self, page: ft.Page):
        self.c = get_colors(page.theme_mode == ft.ThemeMode.DARK)
        super().__init__(route="/admin_dashboard", bgcolor=self.c["PAGE_BG"], scroll=None, padding=0)
        self.page = page
        self.db = load_db()
        
        self.active_tf_for_upload = None
        self.admin_fp = ft.FilePicker(on_result=self.on_file_picked)
        self.page.overlay.append(self.admin_fp)

        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            indicator_color=self.c["ACCENT"],
            label_color=self.c["ACCENT"],
            unselected_label_color=self.c["SUB"],
            tabs=[self.build_overview_tab(), self.build_users_tab(), self.build_meals_tab(), self.build_workouts_tab()],
            expand=True
        )
        
        self.controls = [
            ft.Container(
                expand=True, padding=24,
                content=ft.Column([
                    ft.Row([
                        ft.Row([
                            ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS, color=self.c["ACCENT"], size=40),
                            ft.Text(t("admin_dashboard"), size=32, weight="bold", color=self.c["TEXT"]),
                        ], spacing=10),
                        ft.IconButton(ft.Icons.EXIT_TO_APP_ROUNDED, icon_color=self.c["RED"], on_click=lambda e: self.page.go("/dashboard"))
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(color=self.c["CARD3"], height=30),
                    self.tabs
                ])
            )
        ]

    def _show_snack(self, msg, color):
        self.page.open(ft.SnackBar(content=ft.Text(msg, color="white"), bgcolor=color))

    def on_file_picked(self, e: ft.FilePickerResultEvent):
        if e.files and self.active_tf_for_upload:
            try:
                src = e.files[0].path
                filename = e.files[0].name
                dest = os.path.join(ASSETS_DIR, filename)
                shutil.copy2(src, dest)
                self.active_tf_for_upload.value = filename
                self.active_tf_for_upload.value = filename
                self.active_tf_for_upload.update()
                self._show_snack("تم رفع الصورة بنجاح" if LANG=='ar' else "Image Uploaded", self.c["GREEN"])
            except Exception as ex:
                self._show_snack(f"خطأ في الرفع: {ex}", self.c["RED"])

    def trigger_upload(self, e, target_tf):
        self.active_tf_for_upload = target_tf
        self.admin_fp.pick_files(allow_multiple=False, file_type=ft.FilePickerFileType.IMAGE)

    def build_overview_tab(self):
        meals_count = len(self.db.get("master_meals", []))
        workouts_count = len(self.db.get("master_workouts", []))
        
        return ft.Tab(
            text=t("admin_overview"),
            icon=ft.Icons.PIE_CHART_ROUNDED,
            content=ft.Column([
                ft.Container(height=20),
                ft.ResponsiveRow([
                    ft.Column(col={"xs": 12, "md": 6, "lg": 4}, controls=[
                        stat_card(ft.Icons.RESTAURANT_MENU, "إجمالي الوجبات في القاعدة", str(meals_count), self.c["ORANGE"], self.c)
                    ]),
                    ft.Column(col={"xs": 12, "md": 6, "lg": 4}, controls=[
                        stat_card(ft.Icons.FITNESS_CENTER, "إجمالي التمارين في القاعدة", str(workouts_count), self.c["GREEN"], self.c)
                    ]),
                ], run_spacing=20, spacing=20),
            ])
        )

    def build_users_tab(self):
        user_data = self.db.get("user", {})
        is_setup = user_data.get("is_setup", False)
        
        if not is_setup:
            content = ft.Container(
                alignment=ft.alignment.center, expand=True,
                content=ft.Text("لا يوجد ملف شخصي مسجل حالياً.", size=18, color=self.c["SUB"])
            )
        else:
            def delete_user_action(e):
                clear_user_data()
                self.db = load_db()
                self.tabs.tabs[1] = self.build_users_tab()
                self.update()
                self._show_snack("تم حذف بيانات العضو وتصفير النظام", self.c["GREEN"])
                
            card_content = ft.Container(
                width=550,
                bgcolor=self.c["CARD"], padding=30, border_radius=20, border=ft.border.all(1, self.c["CARD3"]),
                content=ft.Column([
                    ft.Row([
                        ft.Container(width=70, height=70, border_radius=20, bgcolor=f'{self.c["ACCENT"]}22', alignment=ft.Alignment(0,0), content=ft.Icon(ft.Icons.PERSON, color=self.c["ACCENT"], size=35)),
                        ft.Column([
                            ft.Text(user_data.get("name", "مستخدم"), size=24, weight="bold", color=self.c["TEXT"]),
                            ft.Text(f'الهدف: {t(user_data.get("goal",""))}', color=self.c["SUB"], size=14)
                        ])
                    ], spacing=20),
                    ft.Container(height=20),
                    ft.Divider(color=self.c["CARD3"]),
                    ft.Container(height=10),
                    ft.Row([
                        ft.Text(f'الجنس: {t(user_data.get("gender",""))}', color=self.c["TEXT"]),
                        ft.Text(f'العمر: {user_data.get("age","")} سنة', color=self.c["TEXT"]),
                        ft.Text(f'الوزن: {user_data.get("weight","")} كجم', color=self.c["TEXT"]),
                        ft.Text(f'الطول: {user_data.get("height","")} سم', color=self.c["TEXT"])
                    ], spacing=30, wrap=True),
                    ft.Container(height=30),
                    ft.ElevatedButton(
                        text="تصفير بيانات العضو",
                        icon=ft.Icons.DELETE_FOREVER,
                        color="white",
                        bgcolor=self.c["RED"], 
                        on_click=delete_user_action,
                        height=50
                    )
                ])
            )
            content = ft.Row([card_content], alignment=ft.MainAxisAlignment.CENTER)

        return ft.Tab(
            text=t("admin_users"),
            icon=ft.Icons.PEOPLE_ROUNDED,
            content=ft.Column([ft.Container(height=20), content], expand=True)
        )

    def build_meals_tab(self):
        meals = self.db.get("master_meals", [])
        list_view = ft.ListView(expand=True, spacing=15)
        
        def open_dialog(meal=None):
            is_edit = bool(meal)
            m_id = meal["id"] if is_edit else str(uuid.uuid4())
            name_tf = ft.TextField(label=t("meal_name"), value=meal["name"] if is_edit else "", border_radius=12, color=self.c["TEXT"])
            cal_tf = ft.TextField(label=t("meal_cal"), value=str(meal["cal"]) if is_edit else "", border_radius=12, color=self.c["TEXT"])
            desc_tf = ft.TextField(label=t("meal_desc"), value=meal["desc"] if is_edit else "", border_radius=12, color=self.c["TEXT"])
            img_tf = ft.TextField(label=t("upload_local_img"), value=meal.get("img", "") if is_edit else "", border_radius=12, color=self.c["TEXT"])
            
            upload_btn = ft.ElevatedButton(
                text=t("pick_local_file"),
                icon=ft.Icons.UPLOAD_FILE,
                color="black",
                bgcolor=self.c["ACCENT"], 
                on_click=lambda e: self.trigger_upload(e, img_tf)
            )

            type_dp = ft.Dropdown(label=t("meal_type"), value=meal["type"] if is_edit else "الفطور", options=[ft.dropdown.Option(x) for x in ["الفطور", "الغداء", "العشاء", "سناك", "Breakfast", "Lunch", "Dinner", "Snack"]], border_radius=12, color=self.c["TEXT"])
            goal_dp = ft.Dropdown(label=t("meal_goal"), value=meal.get("goal", "Maintain") if is_edit else "Maintain", options=[ft.dropdown.Option(x) for x in ["Lose Weight", "Maintain", "Gain Weight"]], border_radius=12, color=self.c["TEXT"])

            def save_clk(e):
                new_m = {
                    "id": m_id, "name": name_tf.value, "cal": safe_int(cal_tf.value, 0),
                    "desc": desc_tf.value, "type": type_dp.value, "goal": goal_dp.value, "img": img_tf.value
                }
                if is_edit:
                    idx = next((i for i, x in enumerate(self.db["master_meals"]) if x["id"] == m_id), -1)
                    if idx >= 0: self.db["master_meals"][idx] = new_m
                else:
                    self.db["master_meals"].insert(0, new_m)
                
                save_db(self.db)
                self.page.close(dlg)
                self.tabs.tabs[2] = self.build_meals_tab() 
                self._show_snack("تم حفظ الوجبة بنجاح", self.c["GREEN"])
                self.update()

            dlg = ft.AlertDialog(
                title=ft.Text(t("edit_meal") if is_edit else t("add_meal")),
                content=ft.Container(
                    width=320, 
                    content=ft.Column([
                        name_tf, 
                        ft.Row([ft.Container(cal_tf, expand=True), ft.Container(type_dp, expand=True)], spacing=10), 
                        desc_tf, 
                        ft.Row([ft.Container(img_tf, expand=True), upload_btn], spacing=10), 
                        goal_dp
                    ], tight=True)
                ),
                actions=[
                    ft.TextButton(t("cancel"), on_click=lambda e: self.page.close(dlg)),
                    ft.ElevatedButton(content=get_black_btn_text(t("save")), on_click=save_clk, bgcolor=self.c["ACCENT"])
                ], actions_alignment=ft.MainAxisAlignment.END, bgcolor=self.c["CARD"]
            )
            self.page.open(dlg)

        def del_meal(m_id):
            self.db["master_meals"] = [m for m in self.db["master_meals"] if m["id"] != m_id]
            save_db(self.db)
            self.tabs.tabs[2] = self.build_meals_tab()
            self._show_snack("تم حذف الوجبة بنجاح", self.c["RED"])
            self.update()

        for m in meals:
            list_view.controls.append(
                ft.Container(
                    bgcolor=self.c["CARD"], padding=16, border_radius=16, border=ft.border.all(1, self.c["CARD3"]),
                    content=ft.Row([
                        ft.Container(width=70, height=70, border_radius=12, image=safe_image(m.get("img")), bgcolor=self.c["CARD3"]),
                        ft.Column([
                            ft.Text(m["name"], weight="bold", color=self.c["TEXT"], size=18),
                            ft.Row([
                                ft.Container(padding=ft.padding.symmetric(horizontal=8, vertical=4), border_radius=6, bgcolor=f'{self.c["ACCENT"]}22', content=ft.Text(m.get("type",""), size=11, color=self.c["ACCENT"])),
                                ft.Text(f'🔥 {m["cal"]} kcal', color=self.c["ORANGE"], size=13, weight="bold"),
                                ft.Text(f'🎯 {m.get("goal","")}', color=self.c["SUB"], size=12)
                            ], spacing=10, wrap=True)
                        ], expand=True, spacing=5),
                        ft.Row([
                            ft.IconButton(ft.Icons.EDIT_ROUNDED, icon_color=self.c["BLUE"], tooltip=t("edit_meal"), on_click=lambda e, meal=m: open_dialog(meal)),
                            ft.IconButton(ft.Icons.DELETE_ROUNDED, icon_color=self.c["RED"], tooltip=t("delete"), on_click=lambda e, mid=m["id"]: del_meal(mid))
                        ])
                    ])
                )
            )

        return ft.Tab(
            text=t("admin_meals"),
            icon=ft.Icons.RESTAURANT_MENU,
            content=ft.Column([
                ft.Container(height=10),
                ft.Row([
                    ft.ElevatedButton(text=t("add_meal"), icon=ft.Icons.ADD_CIRCLE_ROUNDED, color="black", bgcolor=self.c["ACCENT"], height=45, on_click=lambda e: open_dialog())
                ]),
                ft.Container(height=10),
                list_view
            ], expand=True)
        )

    def build_workouts_tab(self):
        workouts = self.db.get("master_workouts", [])
        list_view = ft.ListView(expand=True, spacing=15)
        
        def open_dialog(wk=None):
            is_edit = bool(wk)
            w_id = wk["id"] if is_edit else str(uuid.uuid4())
            title_tf = ft.TextField(label=t("workout_title"), value=wk["title"] if is_edit else "", border_radius=12, color=self.c["TEXT"])
            dur_tf = ft.TextField(label=t("workout_dur"), value=str(wk["dur"]) if is_edit else "", border_radius=12, color=self.c["TEXT"])
            cal_tf = ft.TextField(label=t("meal_cal"), value=str(wk.get("cal",0)) if is_edit else "", border_radius=12, color=self.c["TEXT"])
            img_tf = ft.TextField(label=t("upload_local_img"), value=wk.get("img", "") if is_edit else "", border_radius=12, color=self.c["TEXT"])
            
            upload_btn = ft.ElevatedButton(
                text=t("pick_local_file"),
                icon=ft.Icons.UPLOAD_FILE,
                color="black",
                bgcolor=self.c["ACCENT"], 
                on_click=lambda e: self.trigger_upload(e, img_tf)
            )

            level_dp = ft.Dropdown(label=t("workout_level"), value=wk["level"] if is_edit else "medium", options=[ft.dropdown.Option(x) for x in ["easy", "medium", "hard"]], border_radius=12, color=self.c["TEXT"])

            def save_clk(e):
                new_w = {
                    "id": w_id, "title": title_tf.value, "dur": safe_int(dur_tf.value, 0), "cal": safe_int(cal_tf.value, 0),
                    "level": level_dp.value, "img": img_tf.value
                }
                if is_edit:
                    idx = next((i for i, x in enumerate(self.db["master_workouts"]) if x["id"] == w_id), -1)
                    if idx >= 0: self.db["master_workouts"][idx] = new_w
                else:
                    self.db["master_workouts"].insert(0, new_w)
                
                save_db(self.db)
                self.page.close(dlg)
                self.tabs.tabs[3] = self.build_workouts_tab() 
                self._show_snack("تم حفظ التمرين بنجاح", self.c["GREEN"])
                self.update()

            dlg = ft.AlertDialog(
                title=ft.Text(t("edit_workout") if is_edit else t("add_workout")),
                content=ft.Container(
                    width=320, 
                    content=ft.Column([
                        title_tf, 
                        ft.Row([ft.Container(dur_tf, expand=True), ft.Container(cal_tf, expand=True)], spacing=10), 
                        level_dp, 
                        ft.Row([ft.Container(img_tf, expand=True), upload_btn], spacing=10)
                    ], tight=True)
                ),
                actions=[
                    ft.TextButton(t("cancel"), on_click=lambda e: self.page.close(dlg)),
                    ft.ElevatedButton(content=get_black_btn_text(t("save")), on_click=save_clk, bgcolor=self.c["ACCENT"])
                ], actions_alignment=ft.MainAxisAlignment.END, bgcolor=self.c["CARD"]
            )
            self.page.open(dlg)

        def del_workout(w_id):
            self.db["master_workouts"] = [w for w in self.db["master_workouts"] if w["id"] != w_id]
            save_db(self.db)
            self.tabs.tabs[3] = self.build_workouts_tab()
            self._show_snack("تم حذف التمرين بنجاح", self.c["RED"])
            self.update()

        for w in workouts:
            lvl_color = self.c["GREEN"] if w.get("level") == "easy" else self.c["ORANGE"] if w.get("level") == "medium" else self.c["RED"]
            list_view.controls.append(
                ft.Container(
                    bgcolor=self.c["CARD"], padding=16, border_radius=16, border=ft.border.all(1, self.c["CARD3"]),
                    content=ft.Row([
                        ft.Container(width=70, height=70, border_radius=12, image=safe_image(w.get("img")), bgcolor=self.c["CARD3"]),
                        ft.Column([
                            ft.Text(w["title"], weight="bold", color=self.c["TEXT"], size=18),
                            ft.Row([
                                ft.Container(padding=ft.padding.symmetric(horizontal=8, vertical=4), border_radius=6, border=ft.border.all(1, lvl_color), content=ft.Text(t(w.get("level","")), size=10, color=lvl_color)),
                                ft.Text(f'⏱️ {w.get("dur",0)} min', color=self.c["SUB"], size=13),
                                ft.Text(f'🔥 {w.get("cal",0)} kcal', color=self.c["SUB"], size=13)
                            ], spacing=10, wrap=True)
                        ], expand=True, spacing=5),
                        ft.Row([
                            ft.IconButton(ft.Icons.EDIT_ROUNDED, icon_color=self.c["BLUE"], tooltip=t("edit_workout"), on_click=lambda e, wk=w: open_dialog(wk)),
                            ft.IconButton(ft.Icons.DELETE_ROUNDED, icon_color=self.c["RED"], tooltip=t("delete"), on_click=lambda e, wid=w["id"]: del_workout(wid))
                        ])
                    ])
                )
            )

        return ft.Tab(
            text=t("admin_workouts"),
            icon=ft.Icons.FITNESS_CENTER_ROUNDED,
            content=ft.Column([
                ft.Container(height=10),
                ft.Row([
                    ft.ElevatedButton(content=ft.Row([ft.Icon(ft.Icons.ADD_CIRCLE_ROUNDED, color="#000000"), ft.Text(t("add_workout"), color="#000000", weight="bold")]), bgcolor=self.c["ACCENT"], height=45, on_click=lambda e: open_dialog())
                ]),
                ft.Container(height=10),
                list_view
            ], expand=True)
        )

# =========================================================
# MAIN ENTRY
# =========================================================
def main(page: ft.Page):
    page.title = "Healthify Pro"
    c = get_colors(True)
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(font_family="Segoe UI")
    page.bgcolor = c["PAGE_BG"]
    page.rtl = (LANG == "ar")
    page.padding = 0
    page.window.width = 1200
    page.window.height = 800
    page.window.icon = "icon.png"

    def handle_theme(e=None):
        is_dark = page.theme_mode == ft.ThemeMode.DARK
        page.theme_mode = ft.ThemeMode.LIGHT if is_dark else ft.ThemeMode.DARK
        new_c = get_colors(not is_dark)
        page.bgcolor = new_c["PAGE_BG"]
        page.views.clear()
        page.views.append(build_view(page.route or "/dashboard"))
        page.update()

    def handle_lang(e=None):
        global LANG
        LANG = "en" if LANG == "ar" else "ar"
        page.rtl = (LANG == "ar")
        page.views.clear()
        page.views.append(build_view(page.route or "/dashboard"))
        page.update()

    page.toggle_theme = handle_theme
    page.toggle_lang = handle_lang

    def build_view(route: str) -> ft.View:
        if route == "/splash": return SplashView(page)
        if route == "/welcome": return WelcomeView(page)
        if route == "/dashboard": return DashboardView(page)
        if route == "/meals": return MealsView(page)
        if route == "/workout": return WorkoutView(page)
        if route == "/analysis": return AnalysisView(page)
        if route == "/profile": return ProfileView(page)
        if route == "/admin_login": return AdminLoginView(page)
        if route == "/admin_dashboard": return AdminDashboardView(page)
        
        user = load_user()
        if not user.is_setup: return WelcomeView(page)
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
    
    load_db()
    page.go("/splash")

if __name__ == "__main__":
    ft.app(target=main, assets_dir=ASSETS_DIR)
