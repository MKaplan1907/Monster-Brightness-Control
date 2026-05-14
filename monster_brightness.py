import tkinter as tk
from tkinter import ttk
import ctypes
import ctypes.wintypes
import threading
import sys
import os

# ── Windows API setup ──────────────────────────────────────────────────────────
GDI32  = ctypes.windll.gdi32
USER32 = ctypes.windll.user32

RAMP_SIZE = 256

def set_gamma_brightness(level_pct: int):
    """
    level_pct: 0–200
    0–100  → normal gamma ramp scaled down
    100    → identity ramp (original)
    101–200 → boosted ramp (values clamped to 65535)
    """
    ramp = (ctypes.wintypes.WORD * (RAMP_SIZE * 3))()
    factor = level_pct / 100.0
    for i in range(RAMP_SIZE):
        val = int(i * 256 * factor)
        val = max(0, min(65535, val))
        ramp[i]               = val  # red
        ramp[i + RAMP_SIZE]   = val  # green
        ramp[i + RAMP_SIZE*2] = val  # blue
    hdc = USER32.GetDC(None)
    GDI32.SetDeviceGammaRamp(hdc, ramp)
    USER32.ReleaseDC(None, hdc)

def set_wmi_brightness(level_pct: int):
    """Set real backlight brightness (0–100) via WMI."""
    level = max(0, min(100, level_pct))
    try:
        import wmi
        w = wmi.WMI(namespace="wmi")
        methods = w.WmiMonitorBrightnessMethods()[0]
        methods.WmiSetBrightness(level, 0)
        return True
    except Exception:
        return False

def get_wmi_brightness():
    """Get current backlight brightness (0–100)."""
    try:
        import wmi
        w = wmi.WMI(namespace="wmi")
        b = w.WmiMonitorBrightness()[0]
        return b.CurrentBrightness
    except Exception:
        return 100

# ── GUI ────────────────────────────────────────────────────────────────────────
class MonsterBrightness(tk.Tk):
    BG      = "#0d0d0d"
    PANEL   = "#141414"
    BORDER  = "#2a2a2a"
    GREEN   = "#00e676"
    GREEN_D = "#00b050"
    TEXT    = "#e8e8e8"
    MUTED   = "#666666"
    RED     = "#ff4444"
    AMBER   = "#ffaa00"

    def __init__(self):
        super().__init__()
        self.title("MONSTER BRIGHTNESS CONTROL")
        self.geometry("520x560")
        self.resizable(False, False)
        self.configure(bg=self.BG)
        self.wm_attributes("-topmost", True)

        # Icon (M logo in window)
        try:
            self.iconbitmap(default="")
        except Exception:
            pass

        self._level   = tk.IntVar(value=get_wmi_brightness())
        self._dragging = False

        self._build_ui()
        self._apply(self._level.get())
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── Build UI ───────────────────────────────────────────────────────────────
    def _build_ui(self):
        pad = dict(padx=20)

        # ─ Header ─
        hdr = tk.Frame(self, bg=self.BG)
        hdr.pack(fill="x", padx=20, pady=(20,0))

        logo = tk.Label(hdr, text="M", font=("Consolas",22,"bold"),
                        bg=self.GREEN, fg=self.BG, width=2, relief="flat")
        logo.pack(side="left")

        tk.Label(hdr, text="  BRIGHTNESS CONTROL",
                 font=("Consolas",14,"bold"), bg=self.BG, fg=self.TEXT).pack(side="left")
        tk.Label(hdr, text="MONSTER LAPTOP",
                 font=("Consolas",8), bg=self.BG, fg=self.MUTED).pack(side="right", anchor="s", pady=4)

        tk.Frame(self, bg=self.BORDER, height=1).pack(fill="x", padx=20, pady=12)

        # ─ Big value display ─
        val_frame = tk.Frame(self, bg=self.PANEL, relief="flat", bd=0)
        val_frame.pack(fill="x", padx=20, pady=(0,4))
        tk.Frame(val_frame, bg=self.BORDER, height=1).pack(fill="x")

        inner = tk.Frame(val_frame, bg=self.PANEL, pady=18)
        inner.pack(fill="x", padx=20)

        self._pct_lbl = tk.Label(inner, text="100", font=("Consolas",56,"bold"),
                                  bg=self.PANEL, fg=self.GREEN, width=4, anchor="e")
        self._pct_lbl.pack(side="left")
        tk.Label(inner, text="%", font=("Consolas",22,"bold"),
                 bg=self.PANEL, fg=self.MUTED, anchor="sw").pack(side="left", pady=(22,0))

        right_info = tk.Frame(inner, bg=self.PANEL)
        right_info.pack(side="right", anchor="e")

        self._mode_lbl = tk.Label(right_info, text="NORMAL MODE",
                                   font=("Consolas",9,"bold"), bg=self.PANEL, fg=self.GREEN)
        self._mode_lbl.pack(anchor="e")
        self._nit_lbl  = tk.Label(right_info, text="≈ 300 nits",
                                   font=("Consolas",9), bg=self.PANEL, fg=self.MUTED)
        self._nit_lbl.pack(anchor="e", pady=(4,0))

        tk.Frame(val_frame, bg=self.BORDER, height=1).pack(fill="x")

        # ─ Slider ─
        tk.Frame(self, bg=self.BG, height=8).pack()
        tk.Label(self, text="PARLAKLIK SEVİYESİ  [ 0 — 200 ]",
                 font=("Consolas",8), bg=self.BG, fg=self.MUTED, anchor="w").pack(fill="x", padx=24)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("M.Horizontal.TScale",
                         troughcolor=self.BORDER, background=self.GREEN,
                         sliderthickness=22, troughrelief="flat", sliderlength=22)

        self._slider = ttk.Scale(self, from_=0, to=200, orient="horizontal",
                                  variable=self._level, style="M.Horizontal.TScale",
                                  command=self._on_slide)
        self._slider.pack(fill="x", padx=20, pady=(4,0))

        # Tick marks
        tick_f = tk.Frame(self, bg=self.BG)
        tick_f.pack(fill="x", padx=20)
        for val, label in [(0,"0"), (50,"50"), (100,"100★"), (150,"150"), (200,"200")]:
            tk.Label(tick_f, text=label, font=("Consolas",7),
                     bg=self.BG, fg=self.GREEN if val==100 else self.MUTED
                     ).place(relx=val/200, anchor="n")
        tick_f.configure(height=16)

        tk.Frame(self, bg=self.BG, height=6).pack()
        tk.Frame(self, bg=self.BORDER, height=1).pack(fill="x", padx=20)
        tk.Frame(self, bg=self.BG, height=8).pack()

        # ─ Preset buttons ─
        tk.Label(self, text="HIZLI PRESETLER",
                 font=("Consolas",8), bg=self.BG, fg=self.MUTED, anchor="w").pack(fill="x", padx=24)

        btn_f = tk.Frame(self, bg=self.BG)
        btn_f.pack(fill="x", padx=20, pady=(6,0))

        presets = [("🌙 GECe",20), ("💡 ECO",50), ("✦ NORMAL",100),
                   ("⚡ BOOST",140), ("🔥 ULTRA",200)]
        self._preset_btns = []
        for i,(label,val) in enumerate(presets):
            b = tk.Button(btn_f, text=label, font=("Consolas",8,"bold"),
                          bg=self.PANEL, fg=self.MUTED, relief="flat",
                          activebackground=self.GREEN, activeforeground=self.BG,
                          bd=0, padx=8, pady=8, cursor="hand2",
                          command=lambda v=val: self._set_preset(v))
            b.grid(row=0, column=i, sticky="ew", padx=3)
            btn_f.grid_columnconfigure(i, weight=1)
            self._preset_btns.append((b, val))

        tk.Frame(self, bg=self.BG, height=10).pack()
        tk.Frame(self, bg=self.BORDER, height=1).pack(fill="x", padx=20)
        tk.Frame(self, bg=self.BG, height=10).pack()

        # ─ Info bar ─
        self._info_lbl = tk.Label(self,
            text="ℹ  0–100% sistem parlaklığı · 101–200% gamma boost aktif",
            font=("Consolas",8), bg=self.BG, fg=self.MUTED,
            anchor="w", wraplength=480, justify="left")
        self._info_lbl.pack(fill="x", padx=24)

        tk.Frame(self, bg=self.BG, height=10).pack()

        # ─ Status bar ─
        status_f = tk.Frame(self, bg=self.PANEL)
        status_f.pack(fill="x", side="bottom")
        tk.Frame(status_f, bg=self.BORDER, height=1).pack(fill="x")
        row = tk.Frame(status_f, bg=self.PANEL, pady=8)
        row.pack(fill="x", padx=20)

        self._sys_lbl = tk.Label(row, text="SİSTEM: 100%",
                                  font=("Consolas",8), bg=self.PANEL, fg=self.MUTED)
        self._sys_lbl.pack(side="left")
        self._gam_lbl = tk.Label(row, text="GAMMA: +0%",
                                  font=("Consolas",8), bg=self.PANEL, fg=self.MUTED)
        self._gam_lbl.pack(side="left", padx=20)

        tk.Button(row, text="SIFIRLA", font=("Consolas",8,"bold"),
                  bg=self.PANEL, fg=self.RED, relief="flat", bd=0,
                  cursor="hand2", command=self._reset).pack(side="right")

    # ── Logic ──────────────────────────────────────────────────────────────────
    def _on_slide(self, _=None):
        v = int(self._level.get())
        threading.Thread(target=self._apply, args=(v,), daemon=True).start()

    def _set_preset(self, v):
        self._level.set(v)
        threading.Thread(target=self._apply, args=(v,), daemon=True).start()

    def _apply(self, v: int):
        # System backlight (0-100)
        sys_v = min(100, v)
        wmi_ok = set_wmi_brightness(sys_v)

        # Gamma boost (supports 0-200)
        set_gamma_brightness(v)

        self.after(0, self._update_ui, v, wmi_ok)

    def _update_ui(self, v: int, wmi_ok: bool):
        self._pct_lbl.config(text=str(v))

        # Color
        if v <= 25:
            c, mode = self.MUTED, "ECO MODE"
        elif v <= 100:
            c, mode = self.GREEN, "NORMAL MODE"
        elif v <= 140:
            c, mode = self.AMBER, "BOOST MODE"
        else:
            c, mode = self.RED, "ULTRA MODE"

        self._pct_lbl.config(fg=c)
        self._mode_lbl.config(text=mode, fg=c)
        self._nit_lbl.config(text=f"≈ {int(300 * v / 100)} nits tahmini")

        sys_v = min(100, v)
        gam_v = max(0, v - 100)
        self._sys_lbl.config(text=f"SİSTEM: {sys_v}%")
        self._gam_lbl.config(text=f"GAMMA: +{gam_v}%")

        status = "WMI ✓" if wmi_ok else "WMI yok – gamma modu"
        info_map = {
            (v<=25): "🌙 Düşük parlaklık – pil tasarrufu aktif. Karanlık ortam için ideal.",
            (26<=v<=100): f"ℹ  Sistem parlaklığı kontrol ediliyor ({status}). Normal kullanım aralığı.",
            (101<=v<=140): f"⚡ BOOST – Gamma katmanı devreye girdi. Sistem limiti aşıldı! ({status})",
            (v>140): f"🔥 ULTRA – Maksimum gamma boost aktif. Gözlerini koru! ({status})",
        }
        for cond, text in info_map.items():
            if cond:
                self._info_lbl.config(text=text)
                break

        # Highlight active preset button
        for btn, bval in self._preset_btns:
            if abs(bval - v) < 10:
                btn.config(bg=self.GREEN, fg=self.BG)
            else:
                btn.config(bg=self.PANEL, fg=self.MUTED)

    def _reset(self):
        self._level.set(100)
        threading.Thread(target=self._apply, args=(100,), daemon=True).start()

    def _on_close(self):
        # Restore gamma before exit
        try:
            set_gamma_brightness(100)
        except Exception:
            pass
        self.destroy()


if __name__ == "__main__":
    # Request admin for WMI brightness control
    try:
        if ctypes.windll.shell32.IsUserAnAdmin() == 0:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()
    except Exception:
        pass

    app = MonsterBrightness()
    app.mainloop()
