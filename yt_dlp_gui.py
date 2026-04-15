import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import subprocess
import threading
import urllib.request
import re, os, sys, json, queue, zipfile, tempfile, shutil

# ── DPI awareness ─────────────────────────────────────────────────────────────
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

APP_VERSION = "1.0.0"

# ── Paths ─────────────────────────────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

YTDLP_PATH  = os.path.join(BASE_DIR, "yt-dlp.exe")
FFMPEG_PATH = os.path.join(BASE_DIR, "ffmpeg.exe")
YTDLP_URL   = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
FFMPEG_URL  = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"  # fallback

# ── Colors ────────────────────────────────────────────────────────────────────
BG     = "#0d0d0d"
PANEL  = "#111111"
PANEL2 = "#0a0a0a"
BORDER = "#2a2a2a"
BDR2   = "#1e1e1e"
ACCENT = "#4a9eff"   # was #ff4444
GREEN  = "#4caf50"   # softer green
BLUE   = "#4a9eff"
AMBER  = "#ffaa00"
MUTED  = "#888888"   # lighter
TEXT   = "#cccccc"
TEXT2  = "#777777"   # lighter helper text
ERR    = "#e05555"   # red for errors only

FM  = ("Consolas", 10)
FM2 = ("Consolas", 9)
FU  = ("Segoe UI", 10)
FUS = ("Segoe UI", 9)
FT  = ("Segoe UI", 13, "bold")

# ── Strings ───────────────────────────────────────────────────────────────────
S = {
    "en": {
        "subtitle":        "Paste a YouTube link and download in best quality",
        "url":             "URL",
        "url_ph":          "https://www.youtube.com/watch?v=...",
        "save_to":         "Save to",
        "browse":          "📁  Browse",
        "prefix":          "Prefix",
        "prefix_opt":      "(optional)",
        "prefix_ph":       "e.g. 2024_",
        "fn_preview":      "Filename preview",
        "list_formats":    "🔍  List formats",
        "avail_formats":   "Available formats",
        "suggested":       "Suggested best video and audio",
        "video_id":        "Video ID",
        "audio_id":        "Audio ID",
        "dl_audio":        "♪  Download audio",
        "merge":           "⚡  Merge to MP4",
        "cmd_output":      "cmd output",
        "clear":           "clear",
        "url_missing":     "Please paste a YouTube URL first.",
        "ids_missing":     "Fill in both Video ID and Audio ID.",
        "dl_audio_log":    "Downloading best audio (m4a)...",
        "merging":         "Merging to MP4...",
        "merge_done":      "✓ Merge complete!",
        "err_vid":         "[ERROR] Video file not found:",
        "err_aud":         "[ERROR] Audio file not found:",
        "err_prog":        "[ERROR] Program not found:",
        "suggestion":      "Suggestion: Video={}, Audio={}",
    },
    "sv": {
        "subtitle":        "Klistra in en YouTube-länk och ladda ner i bästa kvalitet",
        "url":             "URL",
        "url_ph":          "https://www.youtube.com/watch?v=...",
        "save_to":         "Spara i",
        "browse":          "📁  Bläddra",
        "prefix":          "Prefix",
        "prefix_opt":      "(valfritt)",
        "prefix_ph":       "t.ex. 2024_",
        "fn_preview":      "Förhandsgranskning av filnamn",
        "list_formats":    "🔍  Lista format",
        "avail_formats":   "Tillgängliga format",
        "suggested":       "Föreslaget bästa video och ljud",
        "video_id":        "Video-ID",
        "audio_id":        "Ljud-ID",
        "dl_audio":        "♪  Ladda ned ljud",
        "merge":           "⚡  Slå ihop till MP4",
        "cmd_output":      "cmd-utdata",
        "clear":           "rensa",
        "url_missing":     "Klistra in en YouTube-URL först.",
        "ids_missing":     "Fyll i både Video-ID och Ljud-ID.",
        "dl_audio_log":    "Laddar ned bästa ljud (m4a)...",
        "merging":         "Slår ihop till MP4...",
        "merge_done":      "✓ Sammanslagning klar!",
        "err_vid":         "[FEL] Videofilen hittades inte:",
        "err_aud":         "[FEL] Ljudfilen hittades inte:",
        "err_prog":        "[FEL] Programmet hittades inte:",
        "suggestion":      "Förslag: Video={}, Ljud={}",
    }
}

# ── Util ──────────────────────────────────────────────────────────────────────
def get_ytdlp_version():
    try:
        r = subprocess.run([YTDLP_PATH, "--version"],
                           capture_output=True, text=True, timeout=6)
        return r.stdout.strip() or None
    except Exception:
        return None

def get_latest_ytdlp_version():
    try:
        req = urllib.request.Request(
            "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest",
            headers={"User-Agent": "yt-dlp-helper"})
        with urllib.request.urlopen(req, timeout=8) as r:
            return json.loads(r.read()).get("tag_name", "").strip() or None
    except Exception:
        return None

def get_ffmpeg_download_url():
    """Get fastest download URL for ffmpeg via GitHub API, fallback to gyan.dev."""
    try:
        req = urllib.request.Request(
            "https://api.github.com/repos/GyanD/codexffmpeg/releases/latest",
            headers={"User-Agent": "yt-dlp-helper"})
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read())
            for asset in data.get("assets", []):
                name = asset.get("name", "")
                if name.endswith("-essentials_build.zip"):
                    return asset["browser_download_url"]
    except Exception:
        pass
    # Fallback to gyan.dev
    return FFMPEG_URL

def get_ffmpeg_version():
    try:
        r = subprocess.run([FFMPEG_PATH, "-version"],
                           capture_output=True, text=True, timeout=6)
        m = re.search(r"ffmpeg version (\S+)", r.stdout)
        return m.group(1) if m else "found"
    except Exception:
        return None

# ─────────────────────────────────────────────────────────────────────────────
# Setup Dialog
# ─────────────────────────────────────────────────────────────────────────────
class SetupDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent   = parent
        self.q        = queue.Queue()
        self.ytdlp_ok = False
        self.ffmpeg_ok = False

        self.title("yt-dlp Helper — Setup & Updates")
        self.configure(bg=BG)
        self.resizable(False, True)
        self.protocol("WM_DELETE_WINDOW", lambda: parent.destroy())

        self._build()
        self._center()
        self._poll()
        threading.Thread(target=self._do_check, daemon=True).start()

    def _center(self):
        self.update_idletasks()
        w = 520
        # Use required height + buffer so nothing is clipped
        h = max(self.winfo_reqheight() + 40, 560)
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.minsize(w, h)
        w, h = 520, 540
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ── Queue poll (safe UI updates from threads) ──────────────────────────
    def _poll(self):
        try:
            while True:
                msg, *args = self.q.get_nowait()
                if msg == "ytdlp":
                    self._update_ytdlp(*args)
                elif msg == "ffmpeg":
                    self._update_ffmpeg(*args)
                elif msg == "progress":
                    which, pct = args
                    self._set_progress(which, pct)
                elif msg == "dl_done":
                    which = args[0]
                    if which == "ytdlp":
                        threading.Thread(target=self._recheck_ytdlp, daemon=True).start()
                    else:
                        threading.Thread(target=self._recheck_ffmpeg, daemon=True).start()
                elif msg == "dl_error":
                    messagebox.showerror("Download failed", args[0])
        except queue.Empty:
            pass
        self.after(100, self._poll)

    def _do_check(self):
        cur = get_ytdlp_version()
        lat = get_latest_ytdlp_version()
        self.q.put(("ytdlp", cur, lat))
        ffv = get_ffmpeg_version()
        self.q.put(("ffmpeg", ffv))

    def _recheck_ytdlp(self):
        cur = get_ytdlp_version()
        lat = get_latest_ytdlp_version()
        self.q.put(("ytdlp", cur, lat))

    def _recheck_ffmpeg(self):
        ffv = get_ffmpeg_version()
        self.q.put(("ffmpeg", ffv))

    # ── Build UI ──────────────────────────────────────────────────────────
    def _build(self):
        # Titlebar
        tb = tk.Frame(self, bg=PANEL, height=36)
        tb.pack(fill="x"); tb.pack_propagate(False)
        tk.Label(tb, text="yt-dlp Helper — Setup & Updates",
                 font=FUS, bg=PANEL, fg=MUTED).pack(expand=True)

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=24, pady=18)

        tk.Label(body, text="▶  SETUP & UPDATES", font=FT,
                 bg=BG, fg=ACCENT).pack(anchor="w")
        tk.Label(body,
                 text="yt-dlp Helper requires yt-dlp.exe and ffmpeg.exe.",
                 font=FUS, bg=BG, fg=TEXT2).pack(anchor="w", pady=(2, 16))

        # yt-dlp block (2-column)
        yf_left, yf_right = self._block(body)
        self._dep_name(yf_left, "yt-dlp.exe")
        self.y_dot, self.y_status = self._status_row(yf_left)
        self.y_ver  = self._ver_lbl(yf_left, "checking...")
        self.y_act  = tk.Frame(yf_right, bg=PANEL2)
        self.y_act.pack(anchor="e", pady=(0,0))

        # ffmpeg block (2-column)
        ff_left, ff_right = self._block(body)
        self._dep_name(ff_left, "ffmpeg.exe")
        self.f_dot, self.f_status = self._status_row(ff_left)
        self.f_ver  = self._ver_lbl(ff_left, "checking...")
        self.f_act  = tk.Frame(ff_right, bg=PANEL2)
        self.f_act.pack(anchor="e", pady=(0,0))

        # Divider
        tk.Frame(body, bg=BDR2, height=1).pack(fill="x", pady=14)

        # Footer — stacked: hint on top, button below
        foot = tk.Frame(body, bg=BG)
        foot.pack(fill="x")
        self.foot_hint = tk.Label(foot, text="Checking dependencies...",
                                  font=FUS, bg=BG, fg=MUTED, anchor="w")
        self.foot_hint.pack(fill="x", pady=(0, 6))
        foot_btn_row = tk.Frame(foot, bg=BG)
        foot_btn_row.pack(fill="x")
        self.cont_btn = tk.Button(
            foot_btn_row, text="Continue →", font=FU,
            bg=BORDER, fg="#444444", relief="flat", bd=0,
            padx=12, pady=6, cursor="arrow",
            command=self.destroy, state="disabled")
        self.cont_btn.pack(side="right")

    def _block(self, parent):
        f = tk.Frame(parent, bg=PANEL2, highlightthickness=1,
                     highlightbackground=BDR2)
        f.pack(fill="x", pady=(0, 8))
        inner = tk.Frame(f, bg=PANEL2)
        inner.pack(fill="x", padx=12, pady=8)
        # Left column: name + status + version
        left = tk.Frame(inner, bg=PANEL2)
        left.pack(side="left", fill="both", expand=True)
        # Right column: action button
        right = tk.Frame(inner, bg=PANEL2)
        right.pack(side="right", anchor="e")
        return left, right

    def _dep_name(self, p, txt):
        tk.Label(p, text=txt, font=FM, bg=PANEL2, fg=TEXT).pack(anchor="w")

    def _status_row(self, p):
        row = tk.Frame(p, bg=PANEL2); row.pack(anchor="w", pady=(2, 0))
        dot = tk.Label(row, text="●", font=("Segoe UI", 8), bg=PANEL2, fg=MUTED)
        dot.pack(side="left")
        lbl = tk.Label(row, text="Checking...", font=FUS, bg=PANEL2, fg=MUTED)
        lbl.pack(side="left", padx=(4, 0))
        return dot, lbl

    def _ver_lbl(self, p, txt):
        lbl = tk.Label(p, text=txt, font=FM2, bg=PANEL2, fg=MUTED)
        lbl.pack(anchor="w", pady=(1, 0))
        return lbl

    def _btn(self, parent, text, cmd, bg, fg):
        return tk.Button(parent, text=text, command=cmd, font=FUS,
                         bg=bg, fg=fg, relief="flat", bd=0,
                         padx=10, pady=4, cursor="hand2")

    def _progress_row(self, frame, which):
        for w in frame.winfo_children(): w.destroy()
        row = tk.Frame(frame, bg=PANEL2); row.pack(anchor="w", fill="x")
        bg_bar = tk.Frame(row, bg=BDR2, height=4, width=300)
        bg_bar.pack(side="left", padx=(0, 8)); bg_bar.pack_propagate(False)
        bar = tk.Frame(bg_bar, bg=BLUE, height=4); bar.place(x=0, y=0, height=4, width=0)
        pct = tk.Label(row, text="0%", font=FM2, bg=PANEL2, fg=BLUE)
        pct.pack(side="left")
        self._prog_bars[which] = (bar, pct, bg_bar)

    def _set_progress(self, which, pct):
        if which not in self._prog_bars: return
        bar, lbl, bg_bar = self._prog_bars[which]
        bar.place(width=int(300 * pct / 100))
        lbl.config(text=f"{pct}%")

    # ── State updates ─────────────────────────────────────────────────────
    def _update_ytdlp(self, current, latest):
        for w in self.y_act.winfo_children(): w.destroy()
        if current is None:
            self.y_dot.config(fg=ERR)
            self.y_status.config(text="Not found", fg=ERR)
            self.y_ver.config(text="— not installed")
            self.ytdlp_ok = False
            self._btn(self.y_act, "⬇  Download",
                      lambda: self._start_download("ytdlp"),
                      "#1a2a1a", GREEN).pack(side="left")
        elif latest and current != latest:
            self.y_dot.config(fg=AMBER)
            self.y_status.config(text="Update available", fg=AMBER)
            self.y_ver.config(text=f"{current}  →  {latest} available")
            self.ytdlp_ok = False
            self._btn(self.y_act, "↑  Update now",
                      lambda: self._start_download("ytdlp"),
                      "#1e1a0a", AMBER).pack(side="left")
        else:
            self.y_dot.config(fg=GREEN)
            self.y_status.config(text="Up to date", fg=GREEN)
            self.y_ver.config(text=f"version {current}")
            self.ytdlp_ok = True
            self._btn(self.y_act, "↑  Check for update",
                      lambda: threading.Thread(
                          target=self._recheck_ytdlp, daemon=True).start(),
                      BORDER, MUTED).pack(side="left")
        self._refresh_footer()

    def _update_ffmpeg(self, ffver):
        for w in self.f_act.winfo_children(): w.destroy()
        if ffver is None:
            self.f_dot.config(fg=ERR)
            self.f_status.config(text="Not found", fg=ERR)
            self.f_ver.config(text="— not installed")
            self.ffmpeg_ok = False
            self._btn(self.f_act, "⬇  Download",
                      lambda: self._start_download("ffmpeg"),
                      "#1a2a1a", GREEN).pack(side="left")
        else:
            self.f_dot.config(fg=GREEN)
            self.f_status.config(text="Found", fg=GREEN)
            self.f_ver.config(text=f"version {ffver}")
            self.ffmpeg_ok = True
        self._refresh_footer()

    def _refresh_footer(self):
        if self.ytdlp_ok and self.ffmpeg_ok:
            self.foot_hint.config(text="All dependencies OK", fg=GREEN)
            self.cont_btn.config(state="normal", bg=GREEN, fg=BG, cursor="hand2")
        elif not self.ytdlp_ok and not self.ffmpeg_ok:
            self.foot_hint.config(text="Download required files to continue", fg=ERR)
            self.cont_btn.config(state="disabled", bg=BORDER, fg="#444")
        elif not self.ytdlp_ok:
            self.foot_hint.config(text="Update yt-dlp to continue", fg=AMBER)
            self.cont_btn.config(state="disabled", bg=BORDER, fg="#444")
        else:
            self.foot_hint.config(text="Download ffmpeg to continue", fg=ERR)
            self.cont_btn.config(state="disabled", bg=BORDER, fg="#444")

    # ── Download ──────────────────────────────────────────────────────────
    def _start_download(self, which):
        self._prog_bars = {}
        if which == "ytdlp":
            self.y_dot.config(fg=BLUE)
            self.y_status.config(text="Downloading...", fg=BLUE)
            self.y_ver.config(text="— please wait")
            self._progress_row(self.y_act, "ytdlp")
        else:
            self.f_dot.config(fg=BLUE)
            self.f_status.config(text="Downloading...", fg=BLUE)
            self.f_ver.config(text="— please wait")
            self._progress_row(self.f_act, "ffmpeg")

        dest = YTDLP_PATH if which == "ytdlp" else FFMPEG_PATH
        url  = YTDLP_URL  if which == "ytdlp" else FFMPEG_URL

        def do_dl():
            try:
                def hook(count, block, total):
                    if total > 0:
                        pct = min(int(count * block * 100 / total), 100)
                        self.q.put(("progress", which, pct))

                if which == "ffmpeg":
                    # Get fastest URL (GitHub preferred, gyan.dev fallback)
                    ffmpeg_url = get_ffmpeg_download_url()
                    # Download zip to temp file, extract ffmpeg.exe
                    tmp = os.path.join(tempfile.gettempdir(), "ffmpeg_dl.zip")
                    urllib.request.urlretrieve(ffmpeg_url, tmp, hook)
                    with zipfile.ZipFile(tmp, 'r') as z:
                        # Find ffmpeg.exe inside zip (usually in bin/ subfolder)
                        candidates = [n for n in z.namelist()
                                      if n.endswith("bin/ffmpeg.exe") or
                                         n.lower() == "ffmpeg.exe"]
                        if not candidates:
                            raise Exception("ffmpeg.exe not found inside zip")
                        # Extract just ffmpeg.exe to BASE_DIR
                        member = candidates[0]
                        with z.open(member) as src_f,                              open(dest, 'wb') as dst_f:
                            shutil.copyfileobj(src_f, dst_f)
                    try:
                        os.remove(tmp)
                    except Exception:
                        pass
                else:
                    urllib.request.urlretrieve(url, dest, hook)

                self.q.put(("dl_done", which))
            except Exception as e:
                self.q.put(("dl_error", str(e)))

        threading.Thread(target=do_dl, daemon=True).start()


# ─────────────────────────────────────────────────────────────────────────────
# Main App
# ─────────────────────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("yt-dlp Helper")
        self.geometry("700x1000")
        self.configure(bg=BG)
        self.resizable(True, True)

        self.lang     = "en"
        self.formats  = {}
        self.out_dir  = tk.StringVar(value=os.path.expanduser("~\\Downloads"))
        self.url_var  = tk.StringVar()
        self.pfx_var  = tk.StringVar()
        self.vid_var  = tk.StringVar()
        self.aud_var  = tk.StringVar()

        self.pfx_var.trace_add("write", lambda *_: self._upd_preview())

        self._lbl_refs = {}  # key -> widget for lang refresh
        self._build()

        # Show setup dialog first
        self.withdraw()
        dlg = SetupDialog(self)
        self.wait_window(dlg)
        self.deiconify()

    def t(self, k):
        return S[self.lang].get(k, k)

    # ── Build ─────────────────────────────────────────────────────────────
    def _build(self):
        # Titlebar
        tb = tk.Frame(self, bg=PANEL, height=36)
        tb.pack(fill="x"); tb.pack_propagate(False)
        tk.Label(tb, text="yt-dlp Helper", font=FUS,
                 bg=PANEL, fg=TEXT).pack(side="left", padx=16)
        tk.Label(tb, text=f"v{APP_VERSION}", font=FM2,
                 bg=PANEL, fg=TEXT).pack(side="left")

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=24, pady=18)

        # Header
        hdr = tk.Frame(body, bg=BG); hdr.pack(fill="x", pady=(0, 16))
        left = tk.Frame(hdr, bg=BG); left.pack(side="left", fill="x", expand=True)
        tk.Label(left, text="▶  YT-DLP HELPER", font=FT,
                 bg=BG, fg=ACCENT).pack(anchor="w")
        self._r("subtitle", tk.Label(left, text=self.t("subtitle"),
                font=FUS, bg=BG, fg=TEXT)).pack(anchor="w", pady=(2, 0))

        # Lang toggle
        lf = tk.Frame(hdr, bg=PANEL, highlightthickness=1,
                      highlightbackground=BORDER)
        lf.pack(side="right")
        self.en_btn = tk.Button(lf, text="EN", font=FUS,
                                bg="#1e1e1e", fg=TEXT, relief="flat", bd=0,
                                padx=10, pady=4, cursor="hand2",
                                command=lambda: self._set_lang("en"))
        self.en_btn.pack(side="left")
        self.sv_btn = tk.Button(lf, text="SV", font=FUS,
                                bg=PANEL, fg=MUTED, relief="flat", bd=0,
                                padx=10, pady=4, cursor="hand2",
                                command=lambda: self._set_lang("sv"))
        self.sv_btn.pack(side="left")

        # URL
        self._r("url", tk.Label(body, text=self.t("url").upper(),
                font=FUS, bg=BG, fg=MUTED)).pack(anchor="w")
        url_f = tk.Frame(body, bg=ACCENT)
        url_f.pack(fill="x", pady=(4, 12))
        url_i = tk.Frame(url_f, bg=PANEL); url_i.pack(fill="x", padx=1, pady=1)
        self.url_entry = tk.Entry(url_i, textvariable=self.url_var,
                                  font=FM, bg=PANEL, fg=TEXT,
                                  insertbackground=TEXT, relief="flat", bd=6)
        self.url_entry.pack(fill="x")

        # Save to
        self._r("save_to", tk.Label(body, text=self.t("save_to").upper(),
                font=FUS, bg=BG, fg=MUTED)).pack(anchor="w")
        dir_row = tk.Frame(body, bg=BG); dir_row.pack(fill="x", pady=(4, 12))
        dir_i = tk.Frame(dir_row, bg=PANEL, highlightthickness=1,
                         highlightbackground=BORDER)
        dir_i.pack(side="left", fill="x", expand=True, padx=(0, 8))
        tk.Entry(dir_i, textvariable=self.out_dir, font=FM,
                 bg=PANEL, fg=TEXT, insertbackground=TEXT,
                 relief="flat", bd=6).pack(fill="x")
        self._r("browse", self._mkbtn(dir_row, self.t("browse"),
                self._browse, BORDER, MUTED)).pack(side="left")

        # Prefix + Preview
        pp = tk.Frame(body, bg=BG); pp.pack(fill="x", pady=(0, 14))
        pfx_col = tk.Frame(pp, bg=BG); pfx_col.pack(side="left")
        pfx_lbl_row = tk.Frame(pfx_col, bg=BG); pfx_lbl_row.pack(anchor="w")
        self._r("prefix", tk.Label(pfx_lbl_row, text=self.t("prefix"),
                font=FUS, bg=BG, fg=MUTED)).pack(side="left")
        self._r("prefix_opt", tk.Label(pfx_lbl_row,
                text=f" {self.t('prefix_opt')}",
                font=("Segoe UI", 8), bg=BG, fg=BORDER)).pack(side="left")
        pfx_i = tk.Frame(pfx_col, bg=PANEL, highlightthickness=1,
                         highlightbackground=BORDER)
        pfx_i.pack(fill="x", pady=(4, 0))
        tk.Entry(pfx_i, textvariable=self.pfx_var, width=14,
                 font=FM, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT, relief="flat", bd=6).pack()

        prev_col = tk.Frame(pp, bg=BG)
        prev_col.pack(side="left", fill="both", expand=True, padx=(12, 0))
        self._r("fn_preview", tk.Label(prev_col, text=self.t("fn_preview"),
                font=FUS, bg=BG, fg=MUTED)).pack(anchor="w")
        prev_box = tk.Frame(prev_col, bg=PANEL2, highlightthickness=1,
                            highlightbackground=BDR2)
        prev_box.pack(fill="x", pady=(4, 0))
        prev_i = tk.Frame(prev_box, bg=PANEL2)
        prev_i.pack(fill="x", padx=8, pady=6)
        tk.Label(prev_i, text="→ ", font=FM, bg=PANEL2, fg=TEXT).pack(side="left")
        self.pfx_prev  = tk.Label(prev_i, text="", font=FM, bg=PANEL2, fg=ACCENT)
        self.pfx_prev.pack(side="left")
        self.name_prev = tk.Label(prev_i, text="Video title.mp4",
                                   font=FM, bg=PANEL2, fg=TEXT)
        self.name_prev.pack(side="left")

        # List formats
        self._r("list_formats", self._mkbtn(body, self.t("list_formats"),
                self._list_formats, ACCENT, "white")).pack(anchor="w", pady=(0, 14))

        # Available formats label
        self._r("avail_formats", tk.Label(body, text=self.t("avail_formats"),
                font=FUS, bg=BG, fg=MUTED)).pack(anchor="w")

        # Treeview
        tbl = tk.Frame(body, bg=PANEL2, highlightthickness=1,
                       highlightbackground=BDR2)
        tbl.pack(fill="x", pady=(4, 14))
        sty = ttk.Style(); sty.theme_use("default")
        sty.configure("D.Treeview", background=PANEL2, foreground=TEXT,
                      fieldbackground=PANEL2, rowheight=22, font=FM2)
        sty.configure("D.Treeview.Heading", background=PANEL,
                      foreground=ACCENT, font=("Segoe UI", 9, "bold"),
                      relief="flat")
        sty.map("D.Treeview",
                background=[("selected", "#2a2a2a")],
                foreground=[("selected", ACCENT)])
        cols = ("id","ext","res","fps","size","vid","aud","note")
        self.tree = ttk.Treeview(tbl, columns=cols, show="headings",
                                  height=8, style="D.Treeview",
                                  selectmode="browse")
        hdrs = [("ID",45),("EXT",55),("Resolution",90),("FPS",40),
                ("Size",80),("Video",100),("Audio",80),("Info",160)]
        for col, (h, w) in zip(cols, hdrs):
            self.tree.heading(col, text=h)
            self.tree.column(col, width=w, anchor="w")
        self.tree.pack(fill="x")

        # Suggested best
        self._r("suggested", tk.Label(body, text=self.t("suggested"),
                font=FUS, bg=BG, fg=MUTED)).pack(anchor="w")
        sel = tk.Frame(body, bg=BG); sel.pack(fill="x", pady=(4, 0))

        def id_field(parent, var, key):
            col = tk.Frame(parent, bg=BG); col.pack(side="left", padx=(0, 8))
            self._r(key, tk.Label(col, text=self.t(key),
                    font=FUS, bg=BG, fg=MUTED)).pack(anchor="w")
            fi = tk.Frame(col, bg=PANEL, highlightthickness=1,
                          highlightbackground=BORDER)
            fi.pack(pady=(4, 0))
            tk.Entry(fi, textvariable=var, width=7, font=FM,
                     bg=PANEL, fg=GREEN, insertbackground=GREEN,
                     relief="flat", bd=4).pack()

        id_field(sel, self.vid_var, "video_id")
        id_field(sel, self.aud_var, "audio_id")

        btn_col = tk.Frame(sel, bg=BG); btn_col.pack(side="left")
        tk.Frame(btn_col, bg=BG, height=20).pack()
        br = tk.Frame(btn_col, bg=BG); br.pack()
        self._r("dl_audio", self._mkbtn(br, self.t("dl_audio"),
                self._download_audio, "#1e1a0a", AMBER)).pack(side="left", padx=(0, 6))
        self._r("merge", self._mkbtn(br, self.t("merge"),
                self._merge_by_id, "#1a1e2a", BLUE)).pack(side="left")

        # Divider
        tk.Frame(body, bg=BDR2, height=1).pack(fill="x", pady=14)

        # CMD output
        ch = tk.Frame(body, bg=BG); ch.pack(fill="x")
        self._r("cmd_output", tk.Label(ch, text=self.t("cmd_output"),
                font=FUS, bg=BG, fg=MUTED)).pack(side="left")
        self._r("clear", tk.Button(ch, text=self.t("clear"),
                command=self._clear_log, font=FUS, bg=BG, fg=BORDER,
                relief="flat", bd=0, cursor="hand2")).pack(side="right")
        self.log = scrolledtext.ScrolledText(
            body, font=FM, bg="#080808", fg=GREEN,
            insertbackground=GREEN, relief="flat", bd=0,
            wrap="word", state="disabled", height=5)
        self.log.pack(fill="x", expand=False, pady=(6, 0))

    # ── Widget registry ───────────────────────────────────────────────────
    def _r(self, key, widget):
        self._lbl_refs[key] = widget
        return widget

    def _mkbtn(self, parent, text, cmd, bg, fg=TEXT):
        return tk.Button(parent, text=text, command=cmd, font=FU,
                         bg=bg, fg=fg, activebackground=ACCENT,
                         activeforeground=BG, relief="flat", bd=0,
                         padx=12, pady=6, cursor="hand2")

    # ── Lang ──────────────────────────────────────────────────────────────
    def _set_lang(self, lang):
        self.lang = lang
        self.en_btn.config(bg="#1e1e1e" if lang=="en" else PANEL,
                           fg=TEXT if lang=="en" else MUTED)
        self.sv_btn.config(bg="#1e1e1e" if lang=="sv" else PANEL,
                           fg=TEXT if lang=="sv" else MUTED)
        for key, w in self._lbl_refs.items():
            txt = self.t(key)
            if not txt or txt == key: continue
            if isinstance(w, (tk.Label, tk.Button)):
                w.config(text=txt)

    # ── Preview ───────────────────────────────────────────────────────────
    def _upd_preview(self):
        self.pfx_prev.config(text=self.pfx_var.get())

    # ── Log ───────────────────────────────────────────────────────────────
    def _log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _clear_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    # ── Helpers ───────────────────────────────────────────────────────────
    def _get_url(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("", self.t("url_missing"))
        return url

    def _browse(self):
        d = filedialog.askdirectory(initialdir=self.out_dir.get())
        if d: self.out_dir.set(d)

    def _out_path(self, ext="%(ext)s"):
        d   = self.out_dir.get().strip() or os.path.expanduser("~\\Downloads")
        pfx = self.pfx_var.get().strip()
        return os.path.join(d, f"{pfx}%(title)s.{ext}")

    def _run(self, args, on_done=None):
        def worker():
            self._log(f"$ {' '.join(str(a) for a in args)}\n")
            try:
                proc = subprocess.Popen(
                    args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, encoding="utf-8", errors="replace",
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name=="nt" else 0)
                lines = []
                for line in proc.stdout:
                    self._log(line.rstrip()); lines.append(line)
                proc.wait()
                if on_done: on_done("".join(lines))
            except FileNotFoundError as e:
                self._log(f"{self.t('err_prog')} {e}")
        threading.Thread(target=worker, daemon=True).start()

    # ── Format parsing ────────────────────────────────────────────────────
    def _parse_formats(self, output):
        self.tree.delete(*self.tree.get_children())
        self.formats = {}
        best_v = (0, None)
        best_a = (0, None)
        for line in output.splitlines():
            m = re.match(r"^\s*(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(.*)", line)
            if not m: continue
            fid, ext, res, fps, rest = m.groups()
            parts = rest.split()
            fsize = parts[0] if parts and re.match(r"[\d.]+[KMG]iB", parts[0]) else "-"
            vc = "-"; ac = "-"
            note = " ".join(parts[-3:]) if len(parts) >= 3 else rest.strip()
            for p in parts:
                if p.startswith(("avc","vp","av0","hev")): vc = p
                elif p.startswith(("mp4a","opus")): ac = p
            self.tree.insert("", "end",
                             values=(fid, ext, res, fps, fsize, vc, ac, note))
            self.formats[fid] = {"ext": ext, "res": res}
            if vc != "-" and ac == "-" and "x" in res:
                try:
                    h = int(res.split("x")[1])
                    if h > best_v[0]: best_v = (h, fid)
                except: pass
            is_ao = "audio" in res.lower() or (vc=="-" and ac!="-")
            if is_ao and ac != "-":
                try:
                    tm = re.search(r"(\d+)k", rest)
                    sc = (int(tm.group(1)) if tm else 0) + (1000 if ext=="m4a" else 0)
                    if sc > best_a[0]: best_a = (sc, fid)
                except: pass
        if best_v[1]: self.vid_var.set(best_v[1])
        if best_a[1]: self.aud_var.set(best_a[1])
        if best_v[1] and best_a[1]:
            self._log(f"\n{self.t('suggestion').format(best_v[1], best_a[1])}")

    def _list_formats(self):
        url = self._get_url()
        if not url: return
        self._clear_log()
        self._run([YTDLP_PATH, "-F", url], on_done=self._parse_formats)



    def _download_audio(self):
        url = self._get_url()
        if not url: return
        a = self.aud_var.get().strip()
        fmt = a if a else "bestaudio"
        self._log(f"\n{self.t('dl_audio_log')}\n")
        self._run([YTDLP_PATH, "-f", fmt,
                   "--extract-audio", "--audio-format", "m4a",
                   "-o", self._out_path("m4a"), url])

    def _merge_by_id(self):
        url = self._get_url()
        if not url: return
        v = self.vid_var.get().strip(); a = self.aud_var.get().strip()
        if not v or not a:
            messagebox.showwarning("", self.t("ids_missing")); return
        d   = self.out_dir.get().strip() or os.path.expanduser("~\\Downloads")
        pfx = self.pfx_var.get().strip()
        vf  = os.path.join(d, f"_tmp_video_{v}.mp4")
        af  = os.path.join(d, f"_tmp_audio_{a}.m4a")
        out = os.path.join(d, f"{pfx}merged_{v}+{a}.mp4")
        self._log(f"\n{self.t('merging')}")

        def s1(_):
            self._run([YTDLP_PATH, "-f", a, "-o", af, url], on_done=s2)

        def s2(_):
            if not os.path.exists(vf):
                self._log(f"{self.t('err_vid')} {vf}"); return
            if not os.path.exists(af):
                self._log(f"{self.t('err_aud')} {af}"); return
            self._run([FFMPEG_PATH, "-i", vf, "-i", af,
                       "-c:v", "copy", "-c:a", "aac", "-y", out],
                      on_done=s3)

        def s3(_):
            self._log(f"\n{self.t('merge_done')}")
            for f in [vf, af]:
                try: os.remove(f)
                except: pass

        self._run([YTDLP_PATH, "-f", v, "-o", vf, url], on_done=s1)


if __name__ == "__main__":
    App().mainloop()
