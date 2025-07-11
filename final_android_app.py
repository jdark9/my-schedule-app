import flet as ft
import datetime
import json
from pathlib import Path

# --- بيانات التناوب والإجازات (نفس المنطق السابق) ---
# يمكنك نسخ ولصق كل بيانات التناوب والإجازات هنا
# ...
# سنستخدم دالة مبسطة كمثال
def get_day_status(target_date):
    if target_date.weekday() < 4: # الإثنين - الخميس
        return {'display': 'عمل (نهاري)', 'color': ft.colors.ORANGE_300}
    elif target_date.weekday() == 4: # الجمعة
        return {'display': 'عمل (ليل)', 'color': ft.colors.BLUE_300}
    else: # السبت والأحد
        return {'display': 'راحة', 'color': ft.colors.GREEN_300}

# --- إدارة بيانات المستخدم ---
DATA_FILE = Path("user_data.json")

def load_user_data():
    """تحميل بيانات المستخدم من ملف JSON"""
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # قيم افتراضية إذا لم يكن الملف موجودًا
        return {"annual": "0", "hours": "0", "vacation": "0", "casual": "0"}

def save_user_data(data):
    """حفظ بيانات المستخدم في ملف JSON"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- بناء واجهة التطبيق ---
def main(page: ft.Page):
    page.title = "جدول التناوب وإدارة الإجازات"
    page.rtl = True
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.padding = 20
    page.bgcolor = "#f4f7f6" # لون الخلفية مثل HTML

    # --- لإعلانات AdSense (يعمل فقط في نسخة الويب) ---
    # 1. إضافة كود AdSense الرئيسي إلى رأس الصفحة
    # استبدل "your-adsense-client-id" بالمعرف الخاص بك
    page.head.controls.append(ft.html.Literal(
        """
        <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-your-adsense-client-id"
     crossorigin="anonymous"></script>
        """
    ))

    # --- تحميل البيانات عند بدء التشغيل ---
    user_data = load_user_data()

    # --- حقول إدخال البيانات ---
    annual_field = ft.TextField(label="سنوي", value=user_data["annual"], text_align=ft.TextAlign.CENTER)
    hours_field = ft.TextField(label="ساعات", value=user_data["hours"], text_align=ft.TextAlign.CENTER)
    vacation_field = ft.TextField(label="عطلة", value=user_data["vacation"], text_align=ft.TextAlign.CENTER)
    casual_field = ft.TextField(label="عارضة", value=user_data["casual"], text_align=ft.TextAlign.CENTER)

    # --- دالة الحفظ ---
    def save_button_clicked(e):
        data_to_save = {
            "annual": annual_field.value,
            "hours": hours_field.value,
            "vacation": vacation_field.value,
            "casual": casual_field.value,
        }
        save_user_data(data_to_save)
        # إظهار رسالة تأكيد
        page.snack_bar = ft.SnackBar(
            content=ft.Text("تم حفظ البيانات بنجاح!", text_align=ft.TextAlign.RIGHT),
            bgcolor=ft.colors.GREEN_700
        )
        page.snack_bar.open = True
        page.update()

    # --- تصميم حاوية تشبه تصميم HTML ---
    def create_card_container(content):
        return ft.Container(
            content=content,
            padding=20,
            border_radius=10,
            bgcolor=ft.colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.colors.with_opacity(0.1, ft.colors.BLACK),
                offset=ft.Offset(0, 4),
            ),
            margin=ft.margin.only(bottom=20)
        )

    # --- بناء الواجهة ---
    page.add(
        ft.Text("جدول تناوب المجموعات", size=28, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
        
        # حاوية جدول إدخال البيانات
        create_card_container(
            ft.Column([
                ft.Text("إدارة رصيد الإجازات", size=20, weight=ft.FontWeight.BOLD),
                ft.Row(controls=[annual_field, hours_field, vacation_field, casual_field]),
                ft.Container(height=10),
                ft.ElevatedButton("حفظ البيانات", on_click=save_button_clicked, icon=ft.icons.SAVE),
            ])
        ),
        
        # حاوية إعلان AdSense (كمثال)
        create_card_container(
            ft.Container(
                content=ft.Text("مساحة إعلانية (320x100)", text_align=ft.TextAlign.CENTER),
                bgcolor=ft.colors.GREY_200,
                padding=20,
                alignment=ft.alignment.center,
                # يمكنك إضافة كود الإعلان الخاص بالوحدة هنا إذا كان التطبيق ويب
            )
        ),

        # حاوية جدول التناوب
        create_card_container(
            ft.Column([
                ft.Text("جدول الأيام القادمة", size=20, weight=ft.FontWeight.BOLD),
                # يمكنك بناء جدول التناوب هنا بنفس الطريقة التي تعلمناها
                # ...
                ft.Text(f"اليوم ({datetime.date.today()}): {get_day_status(datetime.date.today())['display']}", size=16),
                ft.Text(f"غدًا ({datetime.date.today() + datetime.timedelta(days=1)}): {get_day_status(datetime.date.today() + datetime.timedelta(days=1))['display']}", size=16)

            ])
        )
    )

# تشغيل التطبيق
ft.app(target=main)