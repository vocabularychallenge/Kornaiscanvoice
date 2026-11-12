# KornAiStudio Scan & Voice — separate new PWA

This project is **independent** of `vocabularychallenge/texttospeedkorn`. No existing repository or deployment is modified.

## Run locally

1. Install Python 3.10+ and FFmpeg (`ffmpeg` must be available on PATH).
2. `pip install -r requirements.txt`
3. `uvicorn server:app --host 0.0.0.0 --port 8000`
4. Open `http://localhost:8000`. For camera/microphone/PWA on a phone, deploy over HTTPS.

## Current features
- EN/TH mixed text to actual MP3 with Google gTTS (online), download, OS share sheet.
- Image upload/camera, English+Thai OCR via Tesseract.js CDN (online first load).
- EN/TH translation via MyMemory public demo endpoint (450 characters per request; may be rate-limited, requires user review).
- Microphone recording converted in browser to actual MP3 using lamejs CDN (first load online), download and share.
- File name field; editable extracted text; local text saving; PWA manifest and service worker.
- Illustrated scene **templates** (SVG) downloadable; **not generative AI illustration**.

## Known limits / safety
- Requires an online server for gTTS, and FFmpeg to combine mixed-language MP3 segments.
- Free Google gTTS access is unofficial; do not assume commercial rights or guaranteed availability.
- Translation sends text to MyMemory; avoid sensitive content.
- OCR first load needs internet; camera and microphone require HTTPS or localhost.
- Web Share API file sharing depends on browser and installed apps; download fallback is provided.
- PWA shell can open offline after install, but cloud TTS and translation cannot work offline.
- No cloud storage, login, payments, or image-generation API integration.
- On some browsers the CDN MP3 encoder may be blocked; show explicit failure, never mislabel WebM as MP3.

## Production notes
For deployment choose an HTTPS Python host with FFmpeg. GitHub Pages alone cannot run `/api/tts`. Test OCR, mic recording, download and file share on target Android browsers. Image AI needs a separately selected provider and an explicit license/budget agreement.
