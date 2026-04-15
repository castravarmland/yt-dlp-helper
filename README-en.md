# yt-dlp Helper

**Version:** 1.0.0  
**Date:** 2026-04-15  
**Platform:** Windows  

A dark, easy-to-use GUI for downloading YouTube videos and audio in any quality — no terminal needed.

---

## Requirements

The program automatically downloads its dependencies on first launch:

- **yt-dlp.exe** — download engine
- **ffmpeg.exe** — used to merge video and audio

You do *not* need to install anything manually.

---

## Getting Started

### Option A — Run as .exe (recommended)

Download `yt_dlp_gui.exe` and place it in its own folder, e.g.:

```
C:\g9_Program\yt_dlp_helper_2\
└── yt_dlp_gui.exe
```

Double-click `yt_dlp_gui.exe`. Done.

### Option B — Run as a Python script

Requires Python 3.13 or later.

```powershell
cd "C:\g9_Program\yt_dlp_helper_2"
python yt_dlp_gui.py
```

---

## Building the .exe yourself (from source)

> Do this if you want to distribute the program without the recipient needing Python.

**Step 1 — Install PyInstaller** (one-time):

```powershell
pip install pyinstaller
```

**Step 2 — Build the .exe**:

```powershell
cd "C:\g9_Program\yt_dlp_helper_2"
pyinstaller --onefile --windowed yt_dlp_gui.py
```

The finished file will be at:

```
dist\yt_dlp_gui.exe
```

Move it to the program folder. No other files are needed.

---

## ⚠️ Windows SmartScreen

The first time you run the `.exe`, Windows may show a blue warning dialog:

> *"Windows protected your PC"*

This happens because the file lacks an expensive code-signing certificate — not because it is dangerous.

**How to run it anyway:**

1. Click **"More info"**
2. Click **"Run anyway"**

You only need to do this once per computer.

---

## ⚠️ Antivirus

`.exe` files built with PyInstaller are sometimes incorrectly flagged by antivirus software (including Windows Defender) as suspicious. This is a well-known false positive — PyInstaller packages Python code in a way that superficially resembles how some malware is packed, but the file contains nothing harmful.

If your antivirus blocks the file:

- Add an exception for `yt_dlp_gui.exe` in your antivirus settings, or
- Run from source instead using `python yt_dlp_gui.py` (see Option B above)

---

## Usage

### 1. Launch — Setup dialog

On first launch, a dialog checks that yt-dlp and ffmpeg are present.  
If missing, click **Download** for each program. The dialog handles everything.  
When both are ready, **Continue →** lights up green.

### 2. Paste a URL

Paste a YouTube link into the URL field.

### 3. Choose a folder

Click **📁 Browse** to select where the file should be saved.  
Default is `Downloads`.

### 4. Prefix (optional)

Add a prefix to prepend to the filename, e.g. `2024_`.  
A live preview is shown in the interface.

### 5. List formats

Click **🔍 List formats**.  
The program fetches all available video and audio formats from YouTube and displays them in the table.  
The best video and audio are selected automatically.

### 6. Download

| Button | What it does |
|---|---|
| **⬇ Download as MP4** | Downloads video + audio separately and merges them into one MP4 file |
| **♪ Download audio** | Downloads audio only as `.m4a` |

---

## Language

The program supports **English** and **Swedish**.  
Switch with the **EN / SV** buttons in the top right.

---

## Folder structure

```
yt_dlp_helper_2\
├── yt_dlp_gui.exe      ← the program (or yt_dlp_gui.py)
├── yt-dlp.exe          ← downloaded automatically
└── ffmpeg.exe          ← downloaded automatically
```

---

## Known limitations

- Windows only
- ffmpeg does not self-update — re-download via the setup dialog if needed
- The filename when merging manually (MP4) contains format IDs, not the YouTube title

---

## Changelog

| Version | Date | Notes |
|---|---|---|
| 1.0.0 | 2026-04-15 | First release |
