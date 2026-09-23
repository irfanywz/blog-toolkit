import customtkinter as ctk
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image
import pillow_avif
import os, sys, threading, re, configparser, pystray
from pystray import MenuItem as item

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Konfigurasi Tema Global CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class MasterImageTools(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)
        self.title("Image Tools SatSet Pro")
        self.geometry("700x460")
        self.resizable(False, False)
        
        self.icon_path = resource_path("logo.ico")
        if os.path.exists(self.icon_path):
            self.iconbitmap(self.icon_path)

        self.config_dir = os.path.dirname(os.path.abspath(__file__))

        # --- HEADER TITLE ---
        header_lbl = ctk.CTkLabel(
            self, 
            text="⚡ IMAGE TOOLS SATSET", 
            font=("Arial Bold", 16)
        )
        header_lbl.pack(pady=(12, 5))

        # --- MAIN CONTAINER (Card Layout Kiri & Kanan) ---
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Panel Kiri (Single Converter)
        self.left_card = ctk.CTkFrame(main_container, corner_radius=16, fg_color=("#2b2b2b", "#1a1d24"))
        self.left_card.pack(side="left", fill="both", expand=True, padx=(0, 8), pady=5)
        self.left_card.pack_propagate(False)

        # Panel Kanan (Anim Media Maker)
        self.right_card = ctk.CTkFrame(main_container, corner_radius=16, fg_color=("#2b2b2b", "#1a1d24"))
        self.right_card.pack(side="right", fill="both", expand=True, padx=(8, 0), pady=5)
        self.right_card.pack_propagate(False)

        # Inisialisasi Konten Tool di dalam Kartu
        self.init_single_tool(self.left_card)
        self.init_anim_tool(self.right_card)

        self.protocol('WM_DELETE_WINDOW', self.hide_window)
        self.create_tray_icon()

    # ==================== KIRI: SINGLE AVIF CONVERTER ====================
    def init_single_tool(self, parent):
        ctk.CTkLabel(parent, text="🖼️ Single AVIF Converter", font=("Arial Bold", 13), text_color="#3abff8").pack(pady=(15, 8))

        self.config_file_single = os.path.join(self.config_dir, "settings.ini")
        self.config_single = configparser.ConfigParser()
        self.load_settings_single()

        # Drop Area dengan Border Elegan
        self.drop_area_s = ctk.CTkFrame(parent, width=300, height=140, corner_radius=12, border_width=2, border_color="#3abff8", fg_color=("#3a3a3a", "#222630"))
        self.drop_area_s.pack(padx=12, pady=5)
        self.drop_area_s.pack_propagate(False)
        self.lbl_s = ctk.CTkLabel(self.drop_area_s, text="📂 DROP FOTO DISINI\n(JPG, PNG, WEBP, BMP)", font=("Arial", 11, "bold"), justify="center", text_color="#a6adbb")
        self.lbl_s.place(relx=0.5, rely=0.5, anchor="center")
        
        self.drop_area_s.drop_target_register(DND_FILES)
        self.drop_area_s.dnd_bind('<<Drop>>', self.do_convert_single)

        self.q_slider = ctk.CTkSlider(parent, from_=1, to=100, height=14, button_color="#3abff8", button_hover_color="#0284c7")
        self.q_slider.set(self.saved_q)
        self.q_slider.configure(command=self.save_q)
        self.q_slider.pack(padx=15, pady=12, fill="x")
        
        self.status_s = ctk.CTkLabel(parent, text=f"Quality: {self.saved_q}%", font=("Arial", 11), text_color="#9ca3af")
        self.status_s.pack()

        self.p_bar_s = ctk.CTkProgressBar(parent, height=5, progress_color="#3abff8")
        self.p_bar_s.pack(padx=15, pady=10, fill="x")
        self.p_bar_s.set(0)

    def load_settings_single(self):
        if os.path.exists(self.config_file_single):
            self.config_single.read(self.config_file_single)
            self.saved_q = int(self.config_single.get("CFG", "q", fallback=70))
        else: 
            self.saved_q = 70

    def save_q(self, v):
        q = int(v)
        self.status_s.configure(text=f"Quality: {q}%")
        if not self.config_single.has_section("CFG"): self.config_single.add_section("CFG")
        self.config_single.set("CFG", "q", str(q))
        with open(self.config_file_single, "w") as f: self.config_single.write(f)

    def do_convert_single(self, e):
        files = [f[0] if f[0] else f[1] for f in re.findall(r'\{(.*?)\}|(\S+)', e.data)]
        valid = [f for f in files if f.lower().endswith(('.jpg','.jpeg','.png','.webp','.bmp'))]
        if valid: threading.Thread(target=self.work_single, args=(valid,), daemon=True).start()

    def work_single(self, files):
        q = int(self.q_slider.get())
        for i, p in enumerate(files):
            try:
                self.after(0, lambda idx=i: self.status_s.configure(text=f"Proses {idx+1}/{len(files)}..."))
                img = Image.open(p).convert("RGBA")
                img.save(os.path.splitext(p)[0] + ".avif", "AVIF", quality=q)
                self.after(0, lambda progress=(i + 1) / len(files): self.p_bar_s.set(progress))
            except Exception:
                pass
                
        self.after(0, lambda: self.status_s.configure(text="BERHASIL!"))
        self.after(2000, lambda: self.status_s.configure(text=f"Quality: {int(self.q_slider.get())}%"))
        self.after(2000, lambda: self.p_bar_s.set(0))


    # ==================== KANAN: ANIM MEDIA MAKER ====================
    def init_anim_tool(self, parent):
        ctk.CTkLabel(parent, text="🎞️ Anim Media Maker", font=("Arial Bold", 13), text_color="#f43f5e").pack(pady=(15, 8))

        self.config_file_anim = os.path.join(self.config_dir, "settings_anim.ini")
        self.config_anim = configparser.ConfigParser()
        self.load_settings_anim()

        self.drop_area_a = ctk.CTkFrame(parent, width=300, height=95, corner_radius=12, border_width=2, border_color="#f43f5e", fg_color=("#3a3a3a", "#222630"))
        self.drop_area_a.pack(padx=12, pady=5)
        self.drop_area_a.pack_propagate(False)
        self.lbl_a = ctk.CTkLabel(self.drop_area_a, text="🎞️ DROP BANYAK FOTO\n(Urut Berdasarkan Nama)", font=("Arial", 11, "bold"), justify="center", text_color="#a6adbb")
        self.lbl_a.place(relx=0.5, rely=0.5, anchor="center")
        
        self.drop_area_a.drop_target_register(DND_FILES)
        self.drop_area_a.dnd_bind('<<Drop>>', self.do_process_anim)

        self.format_picker = ctk.CTkSegmentedButton(parent, values=["AVIF", "WebP"], command=self.save_format, selected_color="#f43f5e", selected_hover_color="#e11d48")
        self.format_picker.set(self.saved_format)
        self.format_picker.pack(padx=15, pady=6, fill="x")

        # Slider Durasi Berbasis Detik (0.1s - 3.0s)
        self.dur_slider = ctk.CTkSlider(parent, from_=0.1, to=3.0, number_of_steps=29, height=14, button_color="#f43f5e", button_hover_color="#e11d48")
        self.dur_slider.set(self.saved_dur)
        self.dur_slider.configure(command=self.save_dur)
        self.dur_slider.pack(padx=15, pady=6, fill="x")
        
        self.status_a = ctk.CTkLabel(parent, text=f"Format: {self.saved_format} | Delay: {self.saved_dur:.1f} detik", font=("Arial", 10), text_color="#9ca3af")
        self.status_a.pack(pady=2)

        self.p_bar_a = ctk.CTkProgressBar(parent, height=5, progress_color="#f43f5e")
        self.p_bar_a.pack(padx=15, pady=8, fill="x")
        self.p_bar_a.set(0)

    def load_settings_anim(self):
        if os.path.exists(self.config_file_anim):
            self.config_anim.read(self.config_file_anim)
            self.saved_dur = float(self.config_anim.get("CFG", "dur", fallback=0.5))
            self.saved_format = self.config_anim.get("CFG", "format", fallback="AVIF")
        else: 
            self.saved_dur = 0.5
            self.saved_format = "AVIF"

    def save_dur(self, v):
        dur = float(v)
        self.update_status_anim()
        if not self.config_anim.has_section("CFG"): self.config_anim.add_section("CFG")
        self.config_anim.set("CFG", "dur", str(dur))
        with open(self.config_file_anim, "w") as f: self.config_anim.write(f)

    def save_format(self, val):
        self.update_status_anim()
        if not self.config_anim.has_section("CFG"): self.config_anim.add_section("CFG")
        self.config_anim.set("CFG", "format", val)
        with open(self.config_file_anim, "w") as f: self.config_anim.write(f)

    def update_status_anim(self, custom_msg=None):
        if custom_msg:
            self.status_a.configure(text=custom_msg)
        else:
            fmt = self.format_picker.get()
            dur = float(self.dur_slider.get())
            self.status_a.configure(text=f"Format: {fmt} | Delay: {dur:.1f} detik")

    def do_process_anim(self, e):
        files = [f[0] if f[0] else f[1] for f in re.findall(r'\{(.*?)\}|(\S+)', e.data)]
        valid = [f for f in files if f.lower().endswith(('.jpg','.jpeg','.png','.webp'))]
        if len(valid) > 1:
            valid.sort()
            threading.Thread(target=self.work_anim, args=(valid,), daemon=True).start()
        else:
            self.after(0, lambda: self.update_status_anim("Minimal 2+ foto bro!"))

    def work_anim(self, files):
        try:
            self.after(0, lambda: self.update_status_anim("Merakit animasi..."))
            duration_ms = int(float(self.dur_slider.get()) * 1000)
            chosen_format = self.format_picker.get()
            
            images = []
            for i, p in enumerate(files):
                img = Image.open(p).convert("RGBA")
                images.append(img)
                progress = (i + 1) / len(files) * 0.8
                self.after(0, lambda prog=progress: self.p_bar_a.set(prog))

            ext = ".avif" if chosen_format == "AVIF" else ".webp"
            output_path = os.path.join(os.path.dirname(files[0]), f"animated_output{ext}")
            
            images[0].save(
                output_path,
                format=chosen_format,
            
                save_all=True,
                append_images=images[1:],
                duration=duration_ms,
                loop=0
            )

            self.after(0, lambda: self.p_bar_a.set(1.0))
            self.after(0, lambda: self.update_status_anim("BERHASIL DIRAKIT!"))
        except Exception:
            self.after(0, lambda: self.update_status_anim("Gagal Merakit!"))
        
        self.after(3000, lambda: self.update_status_anim())
        self.after(3000, lambda: self.p_bar_a.set(0))


    # ==================== SYSTEM TRAY ====================
    def create_tray_icon(self):
        if os.path.exists(self.icon_path):
            icon_img = Image.open(self.icon_path)
        else:
            icon_img = Image.new('RGB', (64, 64), color=(30, 144, 255))
            
        menu = (item('Show', self.show_window, default=True), item('Exit', self.exit_app))
        self.tray_icon = pystray.Icon("image_tools", icon_img, "Image Tools SatSet", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def hide_window(self): 
        self.withdraw()

    def show_window(self):
        self.deiconify()
        self.focus_force()

    def exit_app(self):
        self.tray_icon.stop()
        self.destroy()
        os._exit(0)

if __name__ == "__main__":
    MasterImageTools().mainloop()