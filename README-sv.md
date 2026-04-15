# yt-dlp Helper

**Version:** 1.0.0  
**Datum:** 2026-04-15  
**Plattform:** Windows  

Ett mörkt, lättanvänt GUI för att ladda ner YouTube-videor och ljud i valfri kvalitet — utan att behöva terminalen.

---

## Krav

Programmet laddar automatiskt ner sina beroenden vid första start:

- **yt-dlp.exe** — nedladdningsmotor
- **ffmpeg.exe** — används för att slå ihop video och ljud

Du behöver *inte* installera något manuellt.

---

## Kom igång

### Alternativ A — Kör som .exe (rekommenderat)

Ladda ner `yt_dlp_gui.exe` och lägg den i en egen mapp, t.ex.:

```
C:\Users\dittnamn\yt-dlp-helper\
└── yt_dlp_gui.exe
```

Dubbelklicka på `yt_dlp_gui.exe`. Klart.

### Alternativ B — Kör som Python-skript

Kräver Python 3.13 eller senare.

```powershell
cd "C:\Users\dittnamn\yt-dlp-helper"
python yt_dlp_gui.py
```

---

## Bygga .exe själv (från källkoden)

> Gör detta om du vill distribuera programmet utan att mottagaren behöver Python.

**Steg 1 — Installera PyInstaller** (engångsjobb):

```powershell
pip install pyinstaller
```

**Steg 2 — Bygg .exe**:

```powershell
cd "C:\Users\dittnamn\yt-dlp-helper"
pyinstaller --onefile --windowed yt_dlp_gui.py
```

Färdig fil hamnar i:

```
dist\yt_dlp_gui.exe
```

Flytta den till programmappen. Inga andra filer behövs.

---

## ⚠️ Windows SmartScreen

Första gången du kör `.exe`-filen kan Windows visa en blå varningsruta:

> *"Windows skyddade din dator"*

Det beror på att filen saknar en dyr kod-signering, inte på att den är farlig.

**Så här kör du ändå:**

1. Klicka på **"Mer information"**
2. Klicka på **"Kör ändå"**

Du behöver bara göra detta en gång per dator.

---

## ⚠️ Antivirus

`.exe`-filer byggda med PyInstaller flaggas ibland felaktigt av antivirusprogram (t.ex. Windows Defender) som misstänkta. Det är ett välkänt falskt larm — PyInstaller packar ihop Python-kod på ett sätt som liknar hur viss skadlig kod förpackas, men filen innehåller ingenting skadligt.

Om ditt antivirusprogram blockerar filen:

- Lägg till ett undantag för `yt_dlp_gui.exe` i ditt antivirusprogram, eller
- Kör istället från källkoden med `python yt_dlp_gui.py` (se Alternativ B ovan)

---

## Användning

### 1. Starta — Setup-dialogen

Vid första start visas en dialog som kontrollerar att yt-dlp och ffmpeg finns.  
Saknas de, klicka **Download** för respektive program. Dialogrutan sköter allt.  
När båda är OK lyser **Continue →** grönt.

### 2. Klistra in URL

Klistra in en YouTube-länk i URL-fältet.

### 3. Välj mapp

Klicka **📁 Bläddra** för att välja var filen ska sparas.  
Standard är `Downloads`.

### 4. Prefix (valfritt)

Lägg till ett prefix som sätts före filnamnet, t.ex. `2024_`.  
Förhandsgranskning visas direkt i gränssnittet.

### 5. Lista format

Klicka **🔍 Lista format**.  
Programmet hämtar alla tillgängliga video- och ljudformat från YouTube och visar dem i tabellen.  
Bästa video och bästa ljud väljs automatiskt.

### 6. Ladda ner

| Knapp | Vad den gör |
|---|---|
| **⬇ Download as MP4** | Laddar ner video + ljud separat och slår ihop till en MP4-fil |
| **♪ Ladda ned ljud** | Laddar ner bara ljudet som `.m4a` |

---

## Språk

Programmet stöder **engelska** och **svenska**.  
Växla med knapparna **EN / SV** uppe till höger.

---

## Mappstruktur

```
yt-dlp-helper\
├── yt_dlp_gui.exe      ← programmet (eller yt_dlp_gui.py)
├── yt-dlp.exe          ← laddas ner automatiskt
└── ffmpeg.exe          ← laddas ner automatiskt
```

---

## Kända begränsningar

- Fungerar endast på **Windows**
- ffmpeg uppdateras inte automatiskt — ladda ner på nytt via setup-dialogen vid behov
- Filnamnet vid manuell sammanslagning (MP4) innehåller format-ID:n, inte YouTube-titeln

---

## Versionshistorik

| Version | Datum | Notering |
|---|---|---|
| 1.0.0 | 2026-04-15 | Första version |
