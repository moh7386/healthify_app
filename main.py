import flet as ft
import json
import os
import time
import threading
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Callable, Dict, List

BG = "#0F1115"
CARD = "#1A1F29"
CARD_2 = "#232A36"
CARD_3 = "#293241"
ACCENT = "#00E5A8"
ACCENT_2 = "#00C896"
TEXT = "#FFFFFF"
TEXT2 = "#AAB2C0"
TEXT3 = "#7C8596"
BLUE = "#64B5F6"
ORANGE = "#FFB74D"
GREEN = "#81C784"
RED = "#EF5350"
DB_FILE = "healthify_db.json"


@dataclass
class UserProfile:
    name: str = ""
    age: int = 25
    gender: str = "Male"
    height: float = 170.0
    weight: float = 70.0
    activity_level: str = "Moderate"
    goal: str = "Maintain"
    is_setup: bool = False


def _default_db() -> Dict[str, Any]:
    return {
        "user": asdict(UserProfile()),
        "weight_history": [],
        "calorie_history": [],
        "last_meal_plan": [],
        "last_workout_plan": [],
        "last_analysis": {},
    }


def _load_db() -> Dict[str, Any]:
    if not os.path.exists(DB_FILE):
        return _default_db()
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            db = json.load(f)
        if not isinstance(db, dict):
            return _default_db()
    except Exception:
        return _default_db()
    base = _default_db()
    base.update(db)
    return base


def _save_db(db: Dict[str, Any]) -> None:
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


def load_user() -> UserProfile:
    db = _load_db()
    try:
        return UserProfile(**db.get("user", asdict(UserProfile())))
    except Exception:
        return UserProfile()


def save_user(user: UserProfile) -> None:
    db = _load_db()
    db["user"] = asdict(user)
    today = datetime.now().strftime("%a")
    history = db.setdefault("weight_history", [])
    history.append({"day": today, "weight": float(user.weight)})
    db["weight_history"] = history[-14:]
    _save_db(db)


def save_last_meals(meals: List[Dict[str, Any]]) -> None:
    db = _load_db()
    db["last_meal_plan"] = meals
    _save_db(db)


def save_last_workouts(workouts: List[Dict[str, Any]]) -> None:
    db = _load_db()
    db["last_workout_plan"] = workouts
    _save_db(db)


def save_last_analysis(result: Dict[str, Any]) -> None:
    db = _load_db()
    db["last_analysis"] = result
    _save_db(db)


def calculate_health(user: UserProfile) -> Dict[str, Any]:
    height_m = max(user.height / 100.0, 0.01)
    bmi = round(user.weight / (height_m ** 2), 1)

    if bmi < 18.5:
        bmi_status = "Underweight"
    elif bmi < 25:
        bmi_status = "Normal"
    elif bmi < 30:
        bmi_status = "Overweight"
    else:
        bmi_status = "Obese"

    if user.gender == "Male":
        bmr = (10 * user.weight) + (6.25 * user.height) - (5 * user.age) + 5
    else:
        bmr = (10 * user.weight) + (6.25 * user.height) - (5 * user.age) - 161

    activity = {
        "Sedentary": 1.2,
        "Light": 1.375,
        "Moderate": 1.55,
        "Active": 1.725,
        "Very Active": 1.9,
    }

    tdee = bmr * activity.get(user.activity_level, 1.55)

    if user.goal == "Lose Weight":
        target = tdee - 500
    elif user.goal == "Gain Weight":
        target = tdee + 300
    else:
        target = tdee

    target = int(target)
    protein = int((target * 0.30) / 4)
    carbs = int((target * 0.40) / 4)
    fats = int((target * 0.30) / 9)

    return {
        "bmi": bmi,
        "bmi_status": bmi_status,
        "bmr": int(bmr),
        "tdee": int(tdee),
        "target_calories": target,
        "protein": protein,
        "carbs": carbs,
        "fats": fats,
    }


def health_tip(metrics: Dict[str, Any], goal: str) -> str:
    if metrics["bmi_status"] == "Underweight":
        return "Increase calories gradually and focus on protein-rich meals."
    if metrics["bmi_status"] in ("Overweight", "Obese"):
        return "Reduce ultra-processed foods and add 20–30 minutes cardio daily."
    if goal == "Lose Weight":
        return "Keep portions controlled and prioritize vegetables and lean protein."
    if goal == "Gain Weight":
        return "Use calorie-dense healthy meals and strength training."
    return "Maintain consistency with sleep, water, and balanced meals."


def build_meal_plan(user: UserProfile, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
    cal = metrics["target_calories"]
    if user.goal == "Lose Weight":
        meals = [
            {
                "type": "Breakfast",
                "name": "Greek Yogurt & Berries",
                "cal": int(cal * 0.22),
                "desc": "High protein, light carbs, great start for fat loss.",
                "img": "https://images.unsplash.com/photo-1490645935967-10de6ba17061?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "type": "Lunch",
                "name": "Grilled Chicken Salad",
                "cal": int(cal * 0.30),
                "desc": "Lean protein with fiber-rich greens.",
                "img": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "type": "Dinner",
                "name": "Salmon & Vegetables",
                "cal": int(cal * 0.30),
                "desc": "Omega-3 fats and a balanced finish.",
                "img": "https://images.unsplash.com/photo-1467003909585-2f8a72700288?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "type": "Snack",
                "name": "Apple & Almonds",
                "cal": int(cal * 0.18),
                "desc": "Light snack to control hunger.",
                "img": "https://images.unsplash.com/photo-1498837167922-ddd27525d352?q=80&w=1200&auto=format&fit=crop",
            },
        ]
    elif user.goal == "Gain Weight":
        meals = [
            {
                "type": "Breakfast",
                "name": "Oatmeal, Peanut Butter & Banana",
                "cal": int(cal * 0.26),
                "desc": "Energy-dense and perfect for bulking.",
                "img": "https://images.unsplash.com/photo-1517673400267-0251440c45dc?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "type": "Lunch",
                "name": "Chicken Rice Bowl",
                "cal": int(cal * 0.31),
                "desc": "Balanced carbs and protein for mass gain.",
                "img": "https://images.unsplash.com/photo-1512058564366-18510be2db19?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "type": "Dinner",
                "name": "Steak, Potatoes & Veggies",
                "cal": int(cal * 0.31),
                "desc": "Higher calories to support recovery.",
                "img": "https://images.unsplash.com/photo-1547592180-85f173990554?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "type": "Snack",
                "name": "Nuts, Dates & Milk",
                "cal": int(cal * 0.17),
                "desc": "Easy extra calories during the day.",
                "img": "https://images.unsplash.com/photo-1499186028654-75ad3e1d45f9?q=80&w=1200&auto=format&fit=crop",
            },
        ]
    else:
        meals = [
            {
                "type": "Breakfast",
                "name": "Oatmeal & Berries",
                "cal": int(cal * 0.24),
                "desc": "Balanced carbs and fiber for energy.",
                "img": "https://images.unsplash.com/photo-1517673132405-a56a62b18caf?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "type": "Lunch",
                "name": "Chicken Salad Bowl",
                "cal": int(cal * 0.30),
                "desc": "Protein-rich and satisfying.",
                "img": "https://images.unsplash.com/photo-1547592180-85f173990554?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "type": "Dinner",
                "name": "Salmon & Rice",
                "cal": int(cal * 0.30),
                "desc": "Healthy fats with clean carbs.",
                "img": "https://images.unsplash.com/photo-1467003909585-2f8a72700288?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "type": "Snack",
                "name": "Fruit & Nuts",
                "cal": int(cal * 0.14),
                "desc": "Light snack to keep balance.",
                "img": "https://images.unsplash.com/photo-1498837167922-ddd27525d352?q=80&w=1200&auto=format&fit=crop",
            },
        ]
    return meals


def build_workout_plan(user: UserProfile) -> List[Dict[str, Any]]:
    if user.goal == "Lose Weight":
        return [
            {"day": "Day 1", "title": "Cardio Blast", "dur": "30m", "level": "Medium", "cal": 320, "img": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?q=80&w=1200&auto=format&fit=crop"},
            {"day": "Day 2", "title": "Strength & Core", "dur": "40m", "level": "Medium", "cal": 350, "img": "https://images.unsplash.com/photo-1518611012118-696072aa579a?q=80&w=1200&auto=format&fit=crop"},
            {"day": "Day 3", "title": "Walk + Mobility", "dur": "25m", "level": "Easy", "cal": 120, "img": "https://images.unsplash.com/photo-1495195134817-aeb325a55b65?q=80&w=1200&auto=format&fit=crop"},
            {"day": "Day 4", "title": "Lower Body HIIT", "dur": "35m", "level": "Hard", "cal": 380, "img": "https://images.unsplash.com/photo-1518611012118-696072aa579a?q=80&w=1200&auto=format&fit=crop"},
            {"day": "Day 5", "title": "Upper Body", "dur": "40m", "level": "Medium", "cal": 330, "img": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?q=80&w=1200&auto=format&fit=crop"},
            {"day": "Day 6", "title": "Long Walk", "dur": "45m", "level": "Easy", "cal": 180, "img": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?q=80&w=1200&auto=format&fit=crop"},
            {"day": "Day 7", "title": "Recovery", "dur": "20m", "level": "Easy", "cal": 80, "img": "https://images.unsplash.com/photo-1506126613408-eca07ce68773?q=80&w=1200&auto=format&fit=crop"},
        ]
    if user.goal == "Gain Weight":
        return [
            {"day": "Day 1", "title": "Strength Push", "dur": "45m", "level": "Medium", "cal": 300, "img": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?q=80&w=1200&auto=format&fit=crop"},
            {"day": "Day 2", "title": "Upper Body", "dur": "50m", "level": "Hard", "cal": 380, "img": "https://images.unsplash.com/photo-1518611012118-696072aa579a?q=80&w=1200&auto=format&fit=crop"},
            {"day": "Day 3", "title": "Rest + Stretch", "dur": "20m", "level": "Easy", "cal": 60, "img": "https://images.unsplash.com/photo-1506126613408-eca07ce68773?q=80&w=1200&auto=format&fit=crop"},
            {"day": "Day 4", "title": "Lower Body", "dur": "50m", "level": "Hard", "cal": 390, "img": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?q=80&w=1200&auto=format&fit=crop"},
            {"day": "Day 5", "title": "Full Body", "dur": "45m", "level": "Medium", "cal": 340, "img": "https://images.unsplash.com/photo-1518611012118-696072aa579a?q=80&w=1200&auto=format&fit=crop"},
            {"day": "Day 6", "title": "Mobility", "dur": "25m", "level": "Easy", "cal": 90, "img": "https://images.unsplash.com/photo-1495195134817-aeb325a55b65?q=80&w=1200&auto=format&fit=crop"},
            {"day": "Day 7", "title": "Recovery", "dur": "20m", "level": "Easy", "cal": 70, "img": "https://images.unsplash.com/photo-1506126613408-eca07ce68773?q=80&w=1200&auto=format&fit=crop"},
        ]
    return [
        {"day": "Day 1", "title": "Cardio", "dur": "30m", "level": "Medium", "cal": 250, "img": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?q=80&w=1200&auto=format&fit=crop"},
        {"day": "Day 2", "title": "Strength", "dur": "40m", "level": "Medium", "cal": 320, "img": "https://images.unsplash.com/photo-1518611012118-696072aa579a?q=80&w=1200&auto=format&fit=crop"},
        {"day": "Day 3", "title": "Rest", "dur": "20m", "level": "Easy", "cal": 60, "img": "https://images.unsplash.com/photo-1506126613408-eca07ce68773?q=80&w=1200&auto=format&fit=crop"},
        {"day": "Day 4", "title": "Lower Body", "dur": "40m", "level": "Medium", "cal": 300, "img": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?q=80&w=1200&auto=format&fit=crop"},
        {"day": "Day 5", "title": "Upper Body", "dur": "40m", "level": "Medium", "cal": 300, "img": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?q=80&w=1200&auto=format&fit=crop"},
        {"day": "Day 6", "title": "Walking / Mobility", "dur": "30m", "level": "Easy", "cal": 120, "img": "https://images.unsplash.com/photo-1495195134817-aeb325a55b65?q=80&w=1200&auto=format&fit=crop"},
        {"day": "Day 7", "title": "Recovery", "dur": "20m", "level": "Easy", "cal": 70, "img": "https://images.unsplash.com/photo-1506126613408-eca07ce68773?q=80&w=1200&auto=format&fit=crop"},
    ]


def build_weight_history(current_weight: float) -> List[float]:
    offsets = [-0.8, -0.5, -0.3, -0.1, 0.0, 0.1, 0.2]
    return [round(current_weight + x, 1) for x in offsets]


def build_calorie_history(target: int) -> List[int]:
    offsets = [-140, -80, -30, 0, 60, 30, 90]
    return [int(target + x) for x in offsets]


def build_basic_chart(title: str, labels: List[str], values: List[float], accent: str = ACCENT) -> ft.Container:
    max_v = max(values) if values else 1
    bars: List[ft.Control] = []

    for label, value in zip(labels, values):
        height = max(18, int((value / max_v) * 140))
        bars.append(
            ft.Column(
                [
                    ft.Container(height=height, width=18, border_radius=7, bgcolor=accent),
                    ft.Text(label, size=11, color=TEXT2),
                    ft.Text(str(value), size=10, color=TEXT3),
                ],
                alignment=ft.MainAxisAlignment.END,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=6,
            )
        )

    return card(
        ft.Column(
            [
                ft.Text(title, size=18, weight="bold", color=TEXT),
                ft.Container(height=8),
                ft.Row(
                    bars,
                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
                    vertical_alignment=ft.CrossAxisAlignment.END,
                    height=220,
                ),
            ],
            spacing=4,
        )
    )


def shadow_card(
    content: ft.Control,
    padding: int = 18,
    height: int | None = None,
    expand: bool = False,
) -> ft.Container:
    return ft.Container(
        expand=expand,
        height=height,
        padding=padding,
        bgcolor=CARD,
        border_radius=24,
        shadow=ft.BoxShadow(
            blur_radius=20,
            spread_radius=0,
            color="#1A000000",
            offset=ft.Offset(0, 8),
        ),
        content=content,
    )


def card(content: ft.Control) -> ft.Container:
    return shadow_card(content)


def section_header(title: str, subtitle: str = "") -> ft.Column:
    items: List[ft.Control] = [ft.Text(title, size=22, weight="bold", color=TEXT)]
    if subtitle:
        items.append(ft.Text(subtitle, size=13, color=TEXT2))
    return ft.Column(items, spacing=4)


def stat_chip(label: str, value: str, accent: str = ACCENT) -> ft.Container:
    return ft.Container(
        expand=True,
        padding=14,
        border_radius=18,
        bgcolor=CARD_2,
        border=ft.Border.all(1, accent),
        content=ft.Column(
            [
                ft.Text(value, size=22, weight="bold", color=accent),
                ft.Text(label, size=12, color=TEXT2),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )


def quick_action(icon: str, label: str, on_click: Callable[[Any], None]) -> ft.Container:
    return ft.Container(
        expand=True,
        padding=14,
        border_radius=18,
        bgcolor=CARD_2,
        ink=True,
        on_click=on_click,
        content=ft.Column(
            [
                ft.Container(
                    width=44,
                    height=44,
                    border_radius=14,
                    bgcolor="#203040",
                    alignment=ft.Alignment.CENTER,
                    content=ft.Icon(icon, color=ACCENT, size=24),
                ),
                ft.Text(label, size=12, color=TEXT, text_align=ft.TextAlign.CENTER),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )


def nav_bar(index: int, go: Callable[[str], None]) -> ft.NavigationBar:
    routes = ["/dashboard", "/meals", "/workout", "/analysis", "/stats", "/profile"]
    return ft.NavigationBar(
        selected_index=index,
        bgcolor=CARD,
        indicator_color="#243341",
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Home"),
            ft.NavigationBarDestination(icon=ft.Icons.RESTAURANT, label="Meals"),
            ft.NavigationBarDestination(icon=ft.Icons.FITNESS_CENTER, label="Workout"),
            ft.NavigationBarDestination(icon=ft.Icons.CAMERA_ALT, label="AI"),
            ft.NavigationBarDestination(icon=ft.Icons.BAR_CHART, label="Stats"),
            ft.NavigationBarDestination(icon=ft.Icons.PERSON, label="Profile"),
        ],
        on_change=lambda e: go(routes[e.control.selected_index]),
    )


def meal_card(item: Dict[str, Any]) -> ft.Container:
    return shadow_card(
        ft.Row(
            [
                ft.Image(
                    src=item["img"],
                    width=108,
                    height=108,
                    fit=ft.BoxFit.COVER,
                    border_radius=ft.BorderRadius.all(18),
                    error_content=ft.Container(
                        width=108,
                        height=108,
                        border_radius=ft.BorderRadius.all(18),
                        bgcolor=CARD_3,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Icon(ft.Icons.RESTAURANT, color=ACCENT, size=32),
                    ),
                ),
                ft.Column(
                    [
                        ft.Text(item["type"], size=12, color=ACCENT, weight="bold"),
                        ft.Text(item["name"], size=18, color=TEXT, weight="bold"),
                        ft.Text(f'{item["cal"]} kcal', size=13, color=TEXT2),
                        ft.Text(
                            item["desc"],
                            size=12,
                            color=TEXT3,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                    ],
                    expand=True,
                    spacing=8,
                ),
            ],
            spacing=18,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )


def workout_card(item: Dict[str, Any]) -> ft.Container:
    level_color = GREEN if item["level"] == "Easy" else ORANGE if item["level"] == "Medium" else RED
    return shadow_card(
        ft.Row(
            [
                ft.Image(
                    src=item["img"],
                    width=94,
                    height=94,
                    fit=ft.BoxFit.COVER,
                    border_radius=ft.BorderRadius.all(18),
                    error_content=ft.Container(
                        width=94,
                        height=94,
                        border_radius=ft.BorderRadius.all(18),
                        bgcolor=CARD_3,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Icon(ft.Icons.FITNESS_CENTER, color=ACCENT, size=32),
                    ),
                ),
                ft.Column(
                    [
                        ft.Text(f"{item['day']} • {item['title']}", size=18, color=TEXT, weight="bold"),
                        ft.Row(
                            [
                                ft.Icon(ft.Icons.TIMER, size=16, color=TEXT2),
                                ft.Text(item["dur"], size=12, color=TEXT2),
                                ft.Container(width=10),
                                ft.Icon(ft.Icons.LOCAL_FIRE_DEPARTMENT, size=16, color=TEXT2),
                                ft.Text(f'{item["cal"]} kcal', size=12, color=TEXT2),
                            ],
                            spacing=4,
                        ),
                        ft.Container(
                            padding=10,
                            border_radius=999,
                            bgcolor="#202B22" if level_color == GREEN else "#33281F" if level_color == ORANGE else "#342022",
                            content=ft.Text(item["level"], size=11, color=level_color, weight="bold"),
                        ),
                    ],
                    expand=True,
                    spacing=8,
                ),
            ],
            spacing=18,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )


def meal_banner(title: str, subtitle: str, image: str) -> ft.Container:
    return shadow_card(
        ft.Container(
            height=190,
            border_radius=22,
            content=ft.Stack(
                controls=[
                    ft.Image(
                        src=image,
                        expand=True,
                        fit=ft.BoxFit.COVER,
                        border_radius=ft.BorderRadius.all(22),
                        error_content=ft.Container(
                            expand=True,
                            border_radius=ft.BorderRadius.all(22),
                            bgcolor=CARD_3,
                            alignment=ft.Alignment.CENTER,
                            content=ft.Icon(ft.Icons.RESTAURANT, color=ACCENT, size=42),
                        ),
                    ),
                    ft.Container(
                        expand=True,
                        border_radius=ft.BorderRadius.all(22),
                        gradient=ft.LinearGradient(
                            begin=ft.Alignment.TOP_CENTER,
                            end=ft.Alignment.BOTTOM_CENTER,
                            colors=["#00000011", "#000000CC"],
                        ),
                    ),
                    ft.Container(
                        expand=True,
                        padding=18,
                        alignment=ft.Alignment.BOTTOM_LEFT,
                        content=ft.Column(
                            [
                                ft.Container(
                                    padding=8,
                                    border_radius=999,
                                    bgcolor="#00000055",
                                    content=ft.Text(title, size=12, weight="bold", color=TEXT),
                                ),
                                ft.Text(subtitle, size=24, weight="bold", color=TEXT),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                            horizontal_alignment=ft.CrossAxisAlignment.START,
                        ),
                    ),
                ]
            ),
        ),
        padding=0,
    )


class SplashView(ft.View):
    def __init__(self, go: Callable[[str], None]):
        super().__init__(route="/", bgcolor=BG)
        self.go = go
        self.hero = ft.Container(
            expand=True,
            opacity=0,
            animate_opacity=900,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                [
                    ft.Container(
                        width=120,
                        height=120,
                        border_radius=ft.BorderRadius.all(40),
                        gradient=ft.LinearGradient(colors=[ACCENT, "#1DD6A7"]),
                        alignment=ft.Alignment.CENTER,
                        content=ft.Icon(ft.Icons.FAVORITE, size=60, color=BG),
                    ),
                    ft.Text("Healthify", size=42, weight="bold", color=TEXT),
                    ft.Text("Premium Health Tracker", size=14, color=TEXT2),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )
        self.controls = [self.hero]

    def did_mount(self):
        self.hero.opacity = 1
        self.update()

        def delayed():
            time.sleep(2.2)
            user = load_user()
            self.go("/dashboard" if user.is_setup else "/welcome")

        threading.Thread(target=delayed, daemon=True).start()


class WelcomeView(ft.View):
    def __init__(self, go: Callable[[str], None]):
        super().__init__(route="/welcome", bgcolor=BG, scroll="auto")
        self.go = go
        user = load_user()

        def field(label: str, value: str = "") -> ft.TextField:
            return ft.TextField(
                label=label,
                value=value,
                filled=True,
                fill_color=CARD_2,
                border_color="#334155",
                focused_border_color=ACCENT,
                border_radius=18,
                color=TEXT,
            )

        def dropdown(label: str, value: str, options: List[str]) -> ft.Dropdown:
            return ft.Dropdown(
                label=label,
                value=value,
                filled=True,
                fill_color=CARD_2,
                border_color="#334155",
                focused_border_color=ACCENT,
                border_radius=18,
                color=TEXT,
                options=[ft.DropdownOption(opt, opt) for opt in options],
            )

        self.name = field("Name", user.name)
        self.age = field("Age", str(user.age))
        self.gender = dropdown("Gender", user.gender, ["Male", "Female"])
        self.height = field("Height (cm)", str(user.height))
        self.weight = field("Weight (kg)", str(user.weight))
        self.activity = dropdown("Activity Level", user.activity_level, ["Sedentary", "Light", "Moderate", "Active", "Very Active"])
        self.goal = dropdown("Goal", user.goal, ["Lose Weight", "Maintain", "Gain Weight"])

        self.controls = [
            ft.Container(
                padding=20,
                content=ft.Column(
                    [
                        shadow_card(
                            ft.Column(
                                [
                                    ft.Text("Welcome to Healthify", size=30, weight="bold", color=TEXT),
                                    ft.Text("Set up your profile to generate a smart plan.", size=13, color=TEXT2),
                                ],
                                spacing=8,
                            ),
                            padding=22,
                        ),
                        self.name,
                        ft.Row([self.age, self.gender], spacing=12),
                        ft.Row([self.height, self.weight], spacing=12),
                        self.activity,
                        self.goal,
                        ft.Container(height=6),
                        ft.Container(
                            height=54,
                            border_radius=18,
                            ink=True,
                            on_click=self.save_profile,
                            gradient=ft.LinearGradient(colors=[ACCENT, ACCENT_2]),
                            alignment=ft.Alignment.CENTER,
                            content=ft.Text("Generate My Plan", size=16, weight="bold", color=BG),
                        ),
                    ],
                    spacing=15,
                ),
            )
        ]

    def save_profile(self, e):
        try:
            user = UserProfile(
                name=(self.name.value or "").strip() or "User",
                age=max(1, int(float(self.age.value))),
                gender=self.gender.value or "Male",
                height=float(self.height.value),
                weight=float(self.weight.value),
                activity_level=self.activity.value or "Moderate",
                goal=self.goal.value or "Maintain",
                is_setup=True,
            )
        except Exception:
            return
        save_user(user)
        self.go("/dashboard")


class DashboardView(ft.View):
    def __init__(self, go: Callable[[str], None]):
        super().__init__(route="/dashboard", bgcolor=BG, scroll="auto")
        self.navigation_bar = nav_bar(0, go)
        self.go = go
        self.user = load_user()
        self.metrics = calculate_health(self.user)
        tip = health_tip(self.metrics, self.user.goal)
        meal_plan = build_meal_plan(self.user, self.metrics)
        workout_plan = build_workout_plan(self.user)
        save_last_meals(meal_plan)
        save_last_workouts(workout_plan)

        self.controls = [
            ft.Container(
                padding=20,
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text(f"Hello, {self.user.name} 👋", size=30, weight="bold", color=TEXT),
                                        ft.Text("Your premium health dashboard", size=13, color=TEXT2),
                                    ],
                                    spacing=7,
                                ),
                                ft.Container(
                                    width=58,
                                    height=58,
                                    border_radius=18,
                                    bgcolor=CARD,
                                    alignment=ft.Alignment.CENTER,
                                    content=ft.Icon(ft.Icons.PERSON, color=ACCENT, size=30),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),

                        ft.ResponsiveRow(
                            [
                                ft.Column(
                                    [shadow_card(ft.Column([ft.Text("BMI", color=TEXT2), ft.Text(str(self.metrics["bmi"]), size=36, weight="bold", color=ACCENT), ft.Text(self.metrics["bmi_status"], color=TEXT)], spacing=7))],
                                    col={"xs": 6},
                                ),
                                ft.Column(
                                    [shadow_card(ft.Column([ft.Text("Calories", color=TEXT2), ft.Text(str(self.metrics["target_calories"]), size=36, weight="bold", color=ACCENT), ft.Text("Daily Target", color=TEXT)], spacing=7))],
                                    col={"xs": 6},
                                ),
                            ],
                            run_spacing=12,
                        ),

                        shadow_card(
                            ft.Column(
                                [
                                    ft.Text("Daily Macros", size=18, weight="bold", color=TEXT),
                                    ft.Row(
                                        [
                                            stat_chip("Protein", f'{self.metrics["protein"]}g', BLUE),
                                            stat_chip("Carbs", f'{self.metrics["carbs"]}g', GREEN),
                                            stat_chip("Fats", f'{self.metrics["fats"]}g', ORANGE),
                                        ],
                                        spacing=12,
                                    ),
                                ],
                                spacing=14,
                            )
                        ),

                        shadow_card(
                            ft.Row(
                                [
                                    ft.Container(
                                        width=74,
                                        height=74,
                                        border_radius=ft.BorderRadius.all(22),
                                        bgcolor="#223246",
                                        alignment=ft.Alignment.CENTER,
                                        content=ft.Icon(ft.Icons.WATER_DROP, color=BLUE, size=38),
                                    ),
                                    ft.Column(
                                        [
                                            ft.Text("Water Intake", color=TEXT2),
                                            ft.Text("1.5 / 3.0 Liters", size=24, weight="bold", color=TEXT),
                                        ],
                                        spacing=6,
                                    ),
                                ],
                                spacing=18,
                            )
                        ),

                        shadow_card(
                            ft.Column(
                                [
                                    ft.Text("Today's Workout", size=18, weight="bold", color=TEXT),
                                    ft.Image(
                                        src="https://images.unsplash.com/photo-1517836357463-d25dfeac3438?q=80&w=1200&auto=format&fit=crop",
                                        height=180,
                                        fit=ft.BoxFit.COVER,
                                        border_radius=ft.BorderRadius.all(18),
                                        error_content=ft.Container(
                                            height=180,
                                            border_radius=ft.BorderRadius.all(18),
                                            bgcolor=CARD_3,
                                            alignment=ft.Alignment.CENTER,
                                            content=ft.Icon(ft.Icons.FITNESS_CENTER, color=ACCENT, size=42),
                                        ),
                                    ),
                                    ft.Text("HIIT Cardio • 30 mins • 320 kcal", color=TEXT2),
                                ],
                                spacing=14,
                            )
                        ),

                        ft.Text("Quick Actions", size=20, weight="bold", color=TEXT),
                        ft.ResponsiveRow(
                            [
                                ft.Column([quick_action("restaurant", "Meals", lambda e: go("/meals"))], col={"xs": 6}),
                                ft.Column([quick_action("fitness_center", "Workout", lambda e: go("/workout"))], col={"xs": 6}),
                                ft.Column([quick_action("camera_alt", "AI Analysis", lambda e: go("/analysis"))], col={"xs": 6}),
                                ft.Column([quick_action("bar_chart", "Stats", lambda e: go("/stats"))], col={"xs": 6}),
                                ft.Column([quick_action("person", "Profile", lambda e: go("/profile"))], col={"xs": 12}),
                            ],
                            run_spacing=12,
                        ),

                        shadow_card(
                            ft.Column(
                                [
                                    ft.Text("Smart Tip", size=18, weight="bold", color=TEXT),
                                    ft.Text(tip, size=13, color=TEXT2),
                                ],
                                spacing=8,
                            )
                        ),
                    ],
                    spacing=18,
                ),
            )
        ]


class MealsView(ft.View):
    def __init__(self, go: Callable[[str], None]):
        super().__init__(route="/meals", bgcolor=BG, scroll="auto")
        self.navigation_bar = nav_bar(1, go)
        user = load_user()
        metrics = calculate_health(user)
        meals = build_meal_plan(user, metrics)
        save_last_meals(meals)

        self.controls = [
            ft.Container(
                padding=20,
                content=ft.Column(
                    [
                        section_header("Meal Plan", "A daily plan tailored to your goal."),
                        meal_banner(
                            "Smart Nutrition",
                            f'{metrics["target_calories"]} kcal/day',
                            "https://images.unsplash.com/photo-1490645935967-10de6ba17061?q=80&w=1200&auto=format&fit=crop",
                        ),
                        shadow_card(
                            ft.Column(
                                [
                                    ft.Text("Daily Nutrition Target", size=18, weight="bold", color=TEXT),
                                    ft.Text(f'{metrics["target_calories"]} kcal', size=32, weight="bold", color=ACCENT),
                                    ft.Text(f'Protein {metrics["protein"]}g • Carbs {metrics["carbs"]}g • Fats {metrics["fats"]}g', color=TEXT2),
                                ],
                                spacing=8,
                            )
                        ),
                        meal_card(meals[0]),
                        meal_card(meals[1]),
                        meal_card(meals[2]),
                        meal_card(meals[3]),
                    ],
                    spacing=16,
                ),
            )
        ]


class WorkoutView(ft.View):
    def __init__(self, go: Callable[[str], None]):
        super().__init__(route="/workout", bgcolor=BG, scroll="auto")
        self.navigation_bar = nav_bar(2, go)
        user = load_user()
        workouts = build_workout_plan(user)
        save_last_workouts(workouts)

        self.controls = [
            ft.Container(
                padding=20,
                content=ft.Column(
                    [
                        section_header("Weekly Workout", "Balanced cardio, strength, and recovery."),
                        shadow_card(
                            ft.Column(
                                [
                                    ft.Text("Weekly Summary", size=18, weight="bold", color=TEXT),
                                    ft.Text("7-day routine with progressive load and recovery.", color=TEXT2),
                                ],
                                spacing=8,
                            )
                        ),
                        workout_card(workouts[0]),
                        workout_card(workouts[1]),
                        workout_card(workouts[2]),
                        workout_card(workouts[3]),
                        workout_card(workouts[4]),
                        workout_card(workouts[5]),
                        workout_card(workouts[6]),
                    ],
                    spacing=16,
                ),
            )
        ]


class AnalysisView(ft.View):
    def __init__(self, go: Callable[[str], None]):
        super().__init__(route="/analysis", bgcolor=BG, scroll="auto")
        self.navigation_bar = nav_bar(3, go)
        self.user = load_user()
        self.metrics = calculate_health(self.user)
        self.result_box = ft.Container(visible=False)
        self.upload_box = ft.Container(
            height=220,
            border_radius=24,
            gradient=ft.LinearGradient(colors=["#17202A", "#202A36"]),
            border=ft.Border.all(1, "#2A3544"),
            alignment=ft.Alignment.CENTER,
            ink=True,
            on_click=self.mock_analyze,
            content=ft.Column(
                [
                    ft.Container(
                        width=74,
                        height=74,
                        border_radius=ft.BorderRadius.all(24),
                        bgcolor="#233246",
                        alignment=ft.Alignment.CENTER,
                        content=ft.Icon(ft.Icons.CAMERA_ALT, color=ACCENT, size=40),
                    ),
                    ft.Text("Tap to analyze food photo", size=18, weight="bold", color=TEXT),
                    ft.Text("Mock analyzer ready for later AI integration.", size=13, color=TEXT2),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        self.controls = [
            ft.Container(
                padding=20,
                content=ft.Column(
                    [
                        section_header("Food Analysis", "Ready for future AI photo analysis."),
                        shadow_card(
                            ft.Column(
                                [
                                    ft.Text("Current Health Context", size=18, weight="bold", color=TEXT),
                                    ft.Text(f'BMI {self.metrics["bmi"]} • {self.metrics["bmi_status"]}', color=TEXT2),
                                    ft.Text(f'Target {self.metrics["target_calories"]} kcal/day', color=TEXT2),
                                ],
                                spacing=6,
                            )
                        ),
                        self.upload_box,
                        self.result_box,
                    ],
                    spacing=16,
                ),
            )
        ]

    def mock_analyze(self, e):
        self.upload_box.content = ft.Column(
            [
                ft.ProgressRing(color=ACCENT),
                ft.Text("Analyzing...", color=TEXT2),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.update()

        def process():
            time.sleep(1.4)
            result = {
                "name": "Grilled Steak & Veggies",
                "calories": 650,
                "protein": 48,
                "carbs": 34,
                "fat": 26,
                "score": 86,
            }
            save_last_analysis(result)
            self.upload_box.visible = False
            self.result_box.visible = True
            self.result_box.content = shadow_card(
                ft.Column(
                    [
                        ft.Text("Analysis Result", size=18, weight="bold", color=TEXT),
                        ft.Text(result["name"], size=24, weight="bold", color=ACCENT),
                        ft.Row(
                            [
                                stat_chip("Calories", f'{result["calories"]}'),
                                stat_chip("Protein", f'{result["protein"]}g', BLUE),
                            ],
                            spacing=12,
                        ),
                        ft.Row(
                            [
                                stat_chip("Carbs", f'{result["carbs"]}g', GREEN),
                                stat_chip("Fat", f'{result["fat"]}g', ORANGE),
                            ],
                            spacing=12,
                        ),
                        shadow_card(
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.HEALTH_AND_SAFETY, color=ACCENT, size=34),
                                    ft.Column(
                                        [
                                            ft.Text("Health Score", color=TEXT2),
                                            ft.Text(f'{result["score"]}/100', size=28, weight="bold", color=TEXT),
                                        ],
                                        spacing=2,
                                    ),
                                ],
                                spacing=16,
                            ),
                            padding=16,
                        ),
                    ],
                    spacing=14,
                )
            )
            self.update()

        threading.Thread(target=process, daemon=True).start()


class StatsView(ft.View):
    def __init__(self, go: Callable[[str], None]):
        super().__init__(route="/stats", bgcolor=BG, scroll="auto")
        self.navigation_bar = nav_bar(4, go)
        user = load_user()
        metrics = calculate_health(user)
        db = _load_db()

        weight_history = db.get("weight_history") or []
        if not weight_history:
            weights = build_weight_history(user.weight)
            weight_history = [{"day": d, "weight": w} for d, w in zip(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], weights)]

        calorie_history = db.get("calorie_history") or []
        if not calorie_history:
            calories = build_calorie_history(metrics["target_calories"])
            calorie_history = [{"day": d, "calories": c} for d, c in zip(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], calories)]

        w_labels = [x["day"] for x in weight_history[-7:]]
        w_values = [float(x["weight"]) for x in weight_history[-7:]]
        c_labels = [x["day"] for x in calorie_history[-7:]]
        c_values = [int(x["calories"]) for x in calorie_history[-7:]]
        adherence = 92 if user.goal == "Maintain" else 88 if user.goal == "Lose Weight" else 84

        self.controls = [
            ft.Container(
                padding=20,
                content=ft.Column(
                    [
                        section_header("Stats", "Track your progress and consistency."),
                        ft.ResponsiveRow(
                            [
                                ft.Column([shadow_card(ft.Column([ft.Text("Adherence", color=TEXT2), ft.Text(f"{adherence}%", size=34, weight="bold", color=ACCENT)], spacing=8))], col={"xs": 6}),
                                ft.Column([shadow_card(ft.Column([ft.Text("Active Days", color=TEXT2), ft.Text("24", size=34, weight="bold", color=ACCENT)], spacing=8))], col={"xs": 6}),
                            ],
                            run_spacing=12,
                        ),
                        build_basic_chart("Weight History", w_labels, w_values, BLUE),
                        build_basic_chart("Calories History", c_labels, c_values, ACCENT),
                        shadow_card(
                            ft.Column(
                                [
                                    ft.Text("Achievements", size=18, weight="bold", color=TEXT),
                                    ft.Row(
                                        [
                                            stat_chip("Streak", "12 days", BLUE),
                                            stat_chip("Workouts", "28", GREEN),
                                            stat_chip("Meals Logged", "64", ORANGE),
                                        ],
                                        spacing=12,
                                    ),
                                ],
                                spacing=14,
                            )
                        ),
                    ],
                    spacing=16,
                ),
            )
        ]


class ProfileView(ft.View):
    def __init__(self, go: Callable[[str], None]):
        super().__init__(route="/profile", bgcolor=BG, scroll="auto")
        self.navigation_bar = nav_bar(5, go)
        self.go = go
        self.user = load_user()

        def field(label: str, value: str) -> ft.TextField:
            return ft.TextField(
                label=label,
                value=value,
                filled=True,
                fill_color=CARD_2,
                border_color="#334155",
                focused_border_color=ACCENT,
                border_radius=18,
                color=TEXT,
            )

        def dropdown(label: str, value: str, options: List[str]) -> ft.Dropdown:
            return ft.Dropdown(
                label=label,
                value=value,
                filled=True,
                fill_color=CARD_2,
                border_color="#334155",
                focused_border_color=ACCENT,
                border_radius=18,
                color=TEXT,
                options=[ft.DropdownOption(opt, opt) for opt in options],
            )

        self.name = field("Name", self.user.name)
        self.age = field("Age", str(self.user.age))
        self.gender = dropdown("Gender", self.user.gender, ["Male", "Female"])
        self.height = field("Height (cm)", str(self.user.height))
        self.weight = field("Weight (kg)", str(self.user.weight))
        self.activity = dropdown("Activity Level", self.user.activity_level, ["Sedentary", "Light", "Moderate", "Active", "Very Active"])
        self.goal = dropdown("Goal", self.user.goal, ["Lose Weight", "Maintain", "Gain Weight"])

        self.controls = [
            ft.Container(
                padding=20,
                content=ft.Column(
                    [
                        section_header("Profile", "Edit and save your health settings."),
                        shadow_card(
                            ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Container(
                                                width=72,
                                                height=72,
                                                border_radius=ft.BorderRadius.all(24),
                                                bgcolor="#223246",
                                                alignment=ft.Alignment.CENTER,
                                                content=ft.Icon(ft.Icons.PERSON, color=ACCENT, size=38),
                                            ),
                                            ft.Column(
                                                [
                                                    ft.Text(self.user.name or "User", size=22, weight="bold", color=TEXT),
                                                    ft.Text(f"Goal: {self.user.goal}", color=TEXT2),
                                                ],
                                                spacing=5,
                                            ),
                                        ],
                                        spacing=16,
                                    ),
                                    ft.Container(height=8),
                                    self.name,
                                    ft.Row([self.age, self.gender], spacing=12),
                                    ft.Row([self.height, self.weight], spacing=12),
                                    self.activity,
                                    self.goal,
                                    ft.Container(height=6),
                                    ft.Container(
                                        height=54,
                                        border_radius=18,
                                        ink=True,
                                        on_click=self.save_profile,
                                        gradient=ft.LinearGradient(colors=[ACCENT, ACCENT_2]),
                                        alignment=ft.Alignment.CENTER,
                                        content=ft.Text("Save Profile", size=16, weight="bold", color=BG),
                                    ),
                                ],
                                spacing=14,
                            )
                        ),
                        shadow_card(
                            ft.Column(
                                [
                                    ft.Text("Current Snapshot", size=18, weight="bold", color=TEXT),
                                    ft.Row(
                                        [
                                            stat_chip("Age", str(self.user.age), BLUE),
                                            stat_chip("Weight", f"{self.user.weight} kg", GREEN),
                                        ],
                                        spacing=12,
                                    ),
                                    ft.Row(
                                        [
                                            stat_chip("Height", f"{self.user.height} cm", ORANGE),
                                            stat_chip("Goal", self.user.goal, ACCENT),
                                        ],
                                        spacing=12,
                                    ),
                                ],
                                spacing=14,
                            )
                        ),
                    ],
                    spacing=16,
                ),
            )
        ]

    def save_profile(self, e):
        try:
            updated = UserProfile(
                name=(self.name.value or "").strip() or "User",
                age=max(1, int(float(self.age.value))),
                gender=self.gender.value or "Male",
                height=float(self.height.value),
                weight=float(self.weight.value),
                activity_level=self.activity.value or "Moderate",
                goal=self.goal.value or "Maintain",
                is_setup=True,
            )
        except Exception:
            return

        save_user(updated)
        self.go("/dashboard")


def main(page: ft.Page):
    page.title = "Healthify"
    page.bgcolor = BG
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 430
    page.window.height = 932
    page.padding = 0
    page.spacing = 0

    def go(route: str):
        page.views.clear()
        if route == "/":
            page.views.append(SplashView(go))
        elif route == "/welcome":
            page.views.append(WelcomeView(go))
        elif route == "/dashboard":
            page.views.append(DashboardView(go))
        elif route == "/meals":
            page.views.append(MealsView(go))
        elif route == "/workout":
            page.views.append(WorkoutView(go))
        elif route == "/analysis":
            page.views.append(AnalysisView(go))
        elif route == "/stats":
            page.views.append(StatsView(go))
        elif route == "/profile":
            page.views.append(ProfileView(go))
        page.update()

    def view_pop(e):
        if len(page.views) > 1:
            page.views.pop()
            go(page.views[-1].route)

    page.on_view_pop = view_pop
    go("/")


if __name__ == "__main__":
    ft.run(main)