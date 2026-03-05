import flet as ft
import os
import datetime
from supabase import create_client, Client

# --- SUPABASE BAĞLANTISI (Kanka bilgilerin eklendi!) ---
URL = "https://xinzzxdsetbsxjzrvytt.supabase.co"
KEY = "sb_publishable_hXxHVAZlTrwSnkXtgJjOUg_UQthNDcn"
supabase: Client = create_client(URL, KEY)

def main(page: ft.Page):
    load_data()
    page.title = "Nisa & Batu Private"
    page.theme_mode = "dark"
    page.padding = 0
    page.spacing = 0

    # --- Veri Çekme Fonksiyonu ---
    def load_data():
        notes_box.controls.clear()
        errors_box.controls.clear()
        try:
            # Veritabanından en son kayıtları çekiyoruz
            res = supabase.table("notes").select("*").order("id", desc=True).execute()
            for item in res.data:
                # Tarih formatlama (Yıl-Ay-Gün'ü çekiyoruz)
                tarih = item['created_at'][:10] if item.get('created_at') else "Yeni"
                info = f"⭐ Puan: {item['puan']}/10" if item['tur'] == "not" else "🚨 Sabıka Kaydı"
                
                card = ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(f"Kime: {item['kime']}", weight="bold", size=14),
                            ft.Text(tarih, size=11, color="grey")
                        ], alignment="spaceBetween"),
                        ft.Text(item['mesaj'], size=15),
                        ft.Text(info, color="amber" if item['tur'] == "not" else "red", size=12, weight="bold"),
                    ], spacing=5),
                    bgcolor="rgba(0,0,0,0.85)", 
                    padding=12, 
                    border_radius=10, 
                    border=ft.border.all(1, "#333333")
                )
                
                if item['tur'] == "error":
                    errors_box.controls.append(card)
                else:
                    notes_box.controls.append(card)
            page.update()
        except Exception as ex:
            print(f"Veri çekme hatası: {ex}")

    # --- Değişkenler ---
    current_person = ""
    is_hatalisin = False
    notes_box = ft.Column(spacing=10)
    errors_box = ft.Column(spacing=10)
    note_field = ft.TextField(label="Mesajın...", multiline=True)
    rating_slider = ft.Slider(min=1, max=10, divisions=9, label="{value} Puan", value=5)

    def save_data(e):
        if not note_field.value.strip(): return
        
        # VERİTABANINA KAYDETME
        supabase.table("notes").insert({
            "kime": current_person,
            "tur": "error" if is_hatalisin else "not",
            "puan": int(rating_slider.value) if not is_hatalisin else 0,
            "mesaj": note_field.value
        }).execute()
        
        note_field.value = ""
        dialog.open = False
        load_data() # Listeyi tazele

    dialog = ft.AlertDialog(
        title=ft.Text("Kayıt Oluştur"),
        content=ft.Column([], tight=True, spacing=20),
        actions=[
            ft.TextButton("İptal", on_click=lambda _: setattr(dialog, "open", False) or page.update()),
            ft.ElevatedButton("Gönder", on_click=save_data, bgcolor="blue", color="white"),
        ],
    )
    page.overlay.append(dialog)

    def open_action(e):
        nonlocal current_person, is_hatalisin
        current_person = e.control.data["name"]
        is_hatalisin = e.control.data["type"] == "error"
        dialog.content.controls.clear()
        if not is_hatalisin:
            dialog.content.controls.append(ft.Text("Günlük Puan (1-10):", size=14, color="amber"))
            dialog.content.controls.append(rating_slider)
        dialog.content.controls.append(note_field)
        dialog.title.value = f"{current_person} -> {'HATA' if is_hatalisin else 'NOT'}"
        dialog.open = True
        page.update()

    def create_profile(name, img_name, color):
        return ft.Container(
            content=ft.Column([
                ft.Image(src=img_name, width=120, height=120, fit="cover", border_radius=60),
                ft.Text(name, size=22, weight="bold"),
                ft.ElevatedButton("Not", on_click=open_action, data={"name":name, "type":"note"}, bgcolor=color, color="white", width=140),
                ft.ElevatedButton("Hata!", on_click=open_action, data={"name":name, "type":"error"}, bgcolor="red", color="white", width=140),
            ], horizontal_alignment="center", spacing=8),
            padding=15, bgcolor="rgba(30, 30, 30, 0.85)", border_radius=20
        )

    # --- ANA YAPI (STACK) ---
    main_view = ft.Stack([
        ft.Image(src="arka_plan.JPG", width=2500, height=2500, fit="cover", opacity=0.4),
        ft.Container(
            content=ft.Column([
                ft.Text("✨ Nisa & Batu Private ✨", size=32, weight="bold"),
                ft.Row([
                    create_profile("Nisa", "nisa.JPG", "pink"),
                    create_profile("Batu", "batu.JPG", "blue"),
                ], alignment="center", spacing=30),
                ft.Divider(height=30, color="white24"),
                ft.Row([
                    ft.Column([
                        ft.Text("📩 Gelen Kutusu", size=20, weight="bold", color="blue200"),
                        notes_box
                    ], expand=True, scroll="adaptive"),
                    ft.VerticalDivider(width=10),
                    ft.Column([
                        ft.Text("🚨 Sabıka Kaydı", size=20, weight="bold", color="red200"),
                        errors_box
                    ], expand=True, scroll="adaptive"),
                ], expand=True, vertical_alignment="start")
            ], horizontal_alignment="center", spacing=20),
            padding=30, expand=True
        )
    ], expand=True)

    page.add(main_view)
    load_data()
     # Açılışta verileri çek

ft.app(target=main, assets_dir="assets")