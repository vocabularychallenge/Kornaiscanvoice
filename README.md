# KornAiStudio — Streamlit + PWA (separate new project)

## Two distinct deployments
1. Deploy `app.py` with `requirements.txt` and `packages.txt` to a NEW Streamlit Community Cloud app. This is the real MP3 engine. Do not deploy `server.py` to Streamlit.
2. Upload only the CONTENTS of `pwa/` to a NEW GitHub Pages repository or to a dedicated subfolder on GitHub Pages. The PWA shell installs on phones and opens the separate Streamlit app.
3. Open the PWA, paste the new Streamlit app URL, and save.

**Important:** PWA is a launcher, not an offline MP3 engine. Streamlit audio generation requires internet. This is not an embedded native Streamlit PWA. The existing `texttospeedkorn` repository remains unchanged.

Other features (OCR, image AI, speech-to-text, recorded voice to MP3) are not completed in this version.

## Custom app icon
The supplied KornAiStudio logo is used for 192x192 and 512x512 PWA icons.
