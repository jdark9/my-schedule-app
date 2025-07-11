import flet as ft
import datetime
import json

# --- بيانات الجداول والإجازات (لا تغيير هنا) ---
OFFICIAL_HOLIDAYS = [
    {'date': '2025-01-01', 'occasion': 'رأس السنة الميلادية'},
    {'date': '2025-01-07', 'occasion': 'عيد الميلاد المجيد'},
    {'date': '2025-01-25', 'occasion': 'ثورة 25 يناير وعيد الشرطة'},
    {'date': '2025-03-30', 'occasion': 'عيد الفطر المبارك'},
    {'date': '2025-04-21', 'occasion': 'شم النسيم'},
    {'date': '2025-05-01', 'occasion': 'عيد العمال'},
    {'date': '2025-06-05', 'occasion': 'وقفة عرفات'},
    {'date': '2025-06-06', 'occasion': 'عيد الأضحى'},
    {'date': '2025-06-30', 'occasion': 'ثورة 30 يونيو'},
    {'date': '2025-07-23', 'occasion': 'عيد ثورة 23 يوليو'},
    {'date': '2025-09-04', 'occasion': 'المولد النبوي الشريف'},
    {'date': '2025-10-06', 'occasion': 'عيد القوات المسلحة'}
]

STANDARD_ROTATION_PATTERN = [
    {'display': 'عمل (نهار)', 'bgcolor': "#fffde7", 'bgcolor_dark': "#4c472f"},
    {'display': 'عمل (نهار)', 'bgcolor': "#fffde7", 'bgcolor_dark': "#4c472f"},
    {'display': 'عمل (ليل)',  'bgcolor': "#e3f2fd", 'bgcolor_dark': "#3b4e60"},
    {'display': 'عمل (ليل)',  'bgcolor': "#e3f2fd", 'bgcolor_dark': "#3b4e60"},
    {'display': 'راحة',      'bgcolor': "#e8f5e9", 'bgcolor_dark': "#3c4e3e"},
    {'display': 'راحة',      'bgcolor': "#e8f5e9", 'bgcolor_dark': "#3c4e3e"},
    {'display': 'راحة',      'bgcolor': "#e8f5e9", 'bgcolor_dark': "#3c4e3e"},
    {'display': 'راحة',      'bgcolor': "#e8f5e9", 'bgcolor_dark': "#3c4e3e"}
]

DAYTIME_ROTATION_PATTERN = [
    {'display': 'عمل (نهاري)', 'bgcolor': "#fffde7", 'bgcolor_dark': "#4c472f"}, # Sunday
    {'display': 'عمل (نهاري)', 'bgcolor': "#fffde7", 'bgcolor_dark': "#4c472f"}, # Monday
    {'display': 'عمل (نهاري)', 'bgcolor': "#fffde7", 'bgcolor_dark': "#4c472f"}, # Tuesday
    {'display': 'عمل (نهاري)', 'bgcolor': "#fffde7", 'bgcolor_dark': "#4c472f"}, # Wednesday
    {'display': 'عمل (نهاري)', 'bgcolor': "#fffde7", 'bgcolor_dark': "#4c472f"}, # Thursday
    {'display': 'راحة',      'bgcolor': "#e8f5e9", 'bgcolor_dark': "#3c4e3e"}, # Friday
    {'display': 'راحة',      'bgcolor': "#e8f5e9", 'bgcolor_dark': "#3c4e3e"}  # Saturday
]

GROUP_CYCLE_START_DATES = {
    '1': datetime.date(2025, 6, 26), '2': datetime.date(2025, 6, 20),
    '3': datetime.date(2025, 6, 22), '4': datetime.date(2025, 6, 24)
}

# --- دالة حساب الجدول (لا تغيير هنا) ---
def generate_default_schedule(group_number):
    schedule = []
    start_of_year = datetime.date(datetime.date.today().year, 1, 1)
    
    current_rotation_pattern = DAYTIME_ROTATION_PATTERN if group_number == 'daytime' else STANDARD_ROTATION_PATTERN
    
    initial_pattern_offset = 0
    if group_number != 'daytime':
        cycle_start_date = GROUP_CYCLE_START_DATES[group_number]
        diff_days = (start_of_year - cycle_start_date).days
        initial_pattern_offset = diff_days % len(current_rotation_pattern)

    for i in range(366):
        current_day = start_of_year + datetime.timedelta(days=i)
        date_str = current_day.strftime('%Y-%m-%d')
        
        pattern_entry = {}
        if group_number == 'daytime':
            day_of_week = (current_day.weekday() + 1) % 7
            pattern_entry = current_rotation_pattern[day_of_week]
        else:
            day_in_cycle_index = (initial_pattern_offset + i) % len(current_rotation_pattern)
            pattern_entry = current_rotation_pattern[day_in_cycle_index]

        holiday = next((h for h in OFFICIAL_HOLIDAYS if h['date'] == date_str), None)
        
        day_info = {'date': date_str, 'day_of_week': current_day.strftime('%A')}

        if holiday:
            day_info.update({'display': f"عطلة: {holiday['occasion']}", 'bgcolor': "#6d4c41", 'bgcolor_dark': "#6d4c41"})
        else:
            day_info.update(pattern_entry)
        
        schedule.append(day_info)
    return schedule

# --- التطبيق الرئيسي ---
def main(page: ft.Page):
    
    page.title = "جدول تناوب المجموعات"
    page.direction = ft.TextDirection.RTL
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.bgcolor = "#f4f7f6"
    page.padding = 15
    
    selected_group_id = ft.Ref[str]()
    selected_group_id.current = "1"
    schedule_title = ft.Ref[ft.Text]()

    def on_page_load(e):
        """دالة تعمل عند تحميل الصفحة لأول مرة"""
        # تحميل بيانات المستخدم من التخزين
        annual_field.value = page.client_storage.get("app_data.annual") or "0"
        hours_field.value = page.client_storage.get("app_data.hours") or "0"
        vacation_field.value = page.client_storage.get("app_data.vacation") or "0"
        casual_field.value = page.client_storage.get("app_data.casual") or "0"
        
        # تحميل وضع المظهر
        page.theme_mode = page.client_storage.get("app_data.theme_mode") or "light"
        dark_mode_icon.icon = ft.icons.WB_SUNNY_ROUNDED if page.theme_mode == 'dark' else ft.icons.DARK_MODE_ROUNDED
        
        update_schedule_display(selected_group_id.current)
        page.update()

    def toggle_dark_mode(e):
        page.theme_mode = 'dark' if page.theme_mode == 'light' else 'light'
        e.control.icon = ft.icons.WB_SUNNY_ROUNDED if page.theme_mode == 'dark' else ft.icons.DARK_MODE_ROUNDED
        page.client_storage.set("app_data.theme_mode", page.theme_mode) # حفظ وضع المظهر
        update_schedule_display(selected_group_id.current)
        page.update()

    dark_mode_icon = ft.IconButton(icon=ft.icons.DARK_MODE_ROUNDED, on_click=toggle_dark_mode, tooltip="تبديل الوضع")

    annual_field = ft.TextField(label="سنوي", text_align=ft.TextAlign.CENTER)
    hours_field = ft.TextField(label="ساعات", text_align=ft.TextAlign.CENTER)
    vacation_field = ft.TextField(label="عطلة", text_align=ft.TextAlign.CENTER)
    casual_field = ft.TextField(label="عارضة", text_align=ft.TextAlign.CENTER)

    def save_user_data_clicked(e):
        # حفظ البيانات باستخدام التخزين المدمج
        page.client_storage.set("app_data.annual", annual_field.value)
        page.client_storage.set("app_data.hours", hours_field.value)
        page.client_storage.set("app_data.vacation", vacation_field.value)
        page.client_storage.set("app_data.casual", casual_field.value)
        
        page.snack_bar = ft.SnackBar(ft.Text("تم حفظ البيانات بنجاح!"), bgcolor=ft.colors.GREEN_700)
        page.snack_bar.open = True
        page.update()

    search_day_field = ft.TextField(label="اليوم")
    search_month_field = ft.TextField(label="الشهر")
    search_result_text = ft.Text(value="", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
    schedule_table_container = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True, spacing=5)
    
    def update_schedule_display(group_id):
        schedule_data = generate_default_schedule(group_id)
        schedule_table_container.controls.clear()
        today_str = datetime.date.today().strftime('%Y-%m-%d')
        start_index = next((i for i, day in enumerate(schedule_data) if day['date'] >= today_str), 0)
        arabic_weekdays = {"Saturday": "السبت", "Sunday": "الأحد", "Monday": "الإثنين", "Tuesday": "الثلاثاء", "Wednesday": "الأربعاء", "Thursday": "الخميس", "Friday": "الجمعة"}

        for day in schedule_data[start_index:]:
            is_dark = page.theme_mode == 'dark'
            bg_color = day['bgcolor_dark'] if is_dark else day['bgcolor']
            border_prop = ft.border.all(3, ft.colors.ORANGE_ACCENT_700) if day['date'] == today_str else None
            schedule_table_container.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(f"{day['date']}\n{arabic_weekdays.get(day['day_of_week'], '')}", text_align=ft.TextAlign.CENTER, size=12),
                        ft.Text(day['display'], text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD, size=14),
                    ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                    bgcolor=bg_color, padding=10, border_radius=8, border=border_prop
                )
            )
        page.update()

    def search_schedule_clicked(e):
        try:
            day, month = int(search_day_field.value), int(search_month_field.value)
            target_date = datetime.date(datetime.date.today().year, month, day)
            target_date_str = target_date.strftime('%Y-%m-%d')
            full_schedule = generate_default_schedule(selected_group_id.current)
            found_entry = next((d for d in full_schedule if d['date'] == target_date_str), None)
            if found_entry:
                search_result_text.value, search_result_text.color = f"في {target_date_str}: {found_entry['display']}", ft.colors.BLUE_500
            else:
                search_result_text.value, search_result_text.color = "لم يتم العثور على هذا التاريخ.", ft.colors.RED_500
        except (ValueError, TypeError):
            search_result_text.value, search_result_text.color = "يرجى إدخال يوم وشهر صالحين.", ft.colors.RED_500
        page.update()

    search_button = ft.ElevatedButton("بحث", icon=ft.icons.SEARCH, on_click=search_schedule_clicked, bgcolor="#03a9f4", color="white")

    def create_group_card(text, group_id, color):
        def on_card_click(e):
            clicked_group_id = e.control.data
            selected_group_id.current = clicked_group_id
            schedule_title.current.value = f"جدول المجموعة {text}"
            for col_wrapper in group_cards_container.controls:
                card_container = col_wrapper.controls[0]
                card_container.border = ft.border.all(3, ft.colors.ORANGE_ACCENT_700) if card_container.data == clicked_group_id else None
            update_schedule_display(clicked_group_id)

        return ft.Column(
            controls=[ft.Container(
                content=ft.Text(text, color=ft.colors.WHITE if color != "#fbc02d" else ft.colors.BLACK, weight=ft.FontWeight.BOLD, size=12),
                on_click=on_card_click, data=group_id, bgcolor=color, border_radius=8, padding=15, alignment=ft.alignment.center,
                border=ft.border.all(3, ft.colors.ORANGE_ACCENT_700) if group_id == selected_group_id.current else None
            )], col={"xs": 6, "sm": 4, "md": 2.4}
        )
    
    group_cards_container = ft.ResponsiveRow(
        controls=[
            create_group_card("1", "1", "#d32f2f"), create_group_card("2", "2", "#388e3c"),
            create_group_card("3", "3", "#1976d2"), create_group_card("4", "4", "#fbc02d"),
            create_group_card("النهاري", "daytime", "#546e7a")
        ], spacing=5, run_spacing=5
    )

    def create_card_container(*controls, **kwargs):
        return ft.Container(
            content=ft.Column(controls, spacing=10), padding=15, border_radius=10,
            bgcolor=ft.colors.with_opacity(0.05, ft.colors.BLACK), margin=ft.margin.only(bottom=15), **kwargs
        )

    page.on_load = on_page_load # استدعاء الدالة عند تحميل الصفحة

    page.add(
        ft.Row([ft.Text("جدول تناوب المجموعات", size=24, weight=ft.FontWeight.BOLD), ft.Row([dark_mode_icon])], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        create_card_container(
            ft.Text("إدارة رصيد الإجازات", size=18, weight=ft.FontWeight.BOLD),
            ft.ResponsiveRow([
                ft.Column([annual_field], col={"xs": 6, "sm": 3}), ft.Column([hours_field], col={"xs": 6, "sm": 3}),
                ft.Column([vacation_field], col={"xs": 6, "sm": 3}), ft.Column([casual_field], col={"xs": 6, "sm": 3}),
            ]),
            ft.ElevatedButton("حفظ البيانات", on_click=save_user_data_clicked, icon=ft.icons.SAVE, bgcolor="#28a745", color="white", width=page.width)
        ),
        ft.Container(
            content=ft.Text("مساحة إعلانية بانر", text_align=ft.TextAlign.CENTER, color=ft.colors.GREY_500),
            bgcolor=ft.colors.GREY_200, padding=30, border_radius=8, margin=ft.margin.symmetric(vertical=5)
        ),
        create_card_container(
            ft.Text("البحث عن يوم في التناوب", size=18, weight=ft.FontWeight.BOLD),
            ft.ResponsiveRow([
                ft.Column([search_day_field], col={"xs": 6, "sm": 4}), ft.Column([search_month_field], col={"xs": 6, "sm": 4}),
                ft.Column([search_button], col={"xs": 12, "sm": 4}),
            ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            search_result_text
        ),
        group_cards_container,
        ft.Divider(),
        ft.Text(f"جدول المجموعة {selected_group_id.current}", size=18, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, ref=schedule_title),
        ft.Container(content=schedule_table_container, expand=True)
    )

if __name__ == "__main__":
    ft.app(target=main)
