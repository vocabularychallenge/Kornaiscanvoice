from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from gtts import gTTS
from io import BytesIO
from pathlib import Path
import re, subprocess, tempfile, shutil

ROOT=Path(__file__).parent
app=FastAPI(title='KornAiStudio Scan & Voice')
class Speech(BaseModel):
    text:str
    slow:bool=False
    name:str='kornai_voice'

@app.get('/')
def home(): return FileResponse(ROOT/'index.html')
@app.get('/manifest.webmanifest')
def manifest(): return FileResponse(ROOT/'manifest.webmanifest',media_type='application/manifest+json')
@app.get('/sw.js')
def sw(): return FileResponse(ROOT/'sw.js',media_type='application/javascript')
@app.get('/icon.svg')
def icon(): return FileResponse(ROOT/'icon.svg',media_type='image/svg+xml')

@app.post('/api/tts')
def tts(req:Speech):
    if not req.text.strip(): raise HTTPException(400,'กรุณาใส่ข้อความ')
    if len(req.text)>15000: raise HTTPException(400,'ข้อความยาวเกิน 15,000 ตัวอักษร')
    chunks=[]
    for line in req.text.splitlines():
        line=line.strip()
        if not line: continue
        # Keep English and Thai sections separate, preserving order
        for chunk in re.findall(r'[\u0E00-\u0E7F][\u0E00-\u0E7F\s\d.,!?()\-]*|[A-Za-z][^\u0E00-\u0E7F]*',line):
            chunk=chunk.strip()
            if chunk: chunks.append((chunk,'th' if re.search(r'[\u0E00-\u0E7F]',chunk) else 'en'))
    if not chunks: raise HTTPException(400,'ไม่พบข้อความภาษาอังกฤษหรือภาษาไทย')
    try:
        with tempfile.TemporaryDirectory() as tmp:
            inputs=[]
            for i,(txt,lang) in enumerate(chunks):
                path=Path(tmp)/f'{i:04}.mp3'
                gTTS(text=txt,lang=lang,slow=req.slow).save(str(path))
                inputs.append(path)
            if len(inputs)==1: data=inputs[0].read_bytes()
            else:
                if not shutil.which('ffmpeg'): raise HTTPException(503,'ต้องติดตั้ง ffmpeg บนเซิร์ฟเวอร์เพื่อรวมเสียง')
                lst=Path(tmp)/'files.txt'
                lst.write_text(''.join(f"file '{p.as_posix()}'\n" for p in inputs),encoding='utf-8')
                out=Path(tmp)/'output.mp3'
                p=subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(lst),'-c:a','libmp3lame','-q:a','4',str(out)],capture_output=True,text=True,timeout=180)
                if p.returncode: raise HTTPException(500,'รวมเสียงไม่สำเร็จ: '+p.stderr[:250])
                data=out.read_bytes()
        safe=re.sub(r'[^\w\-\u0E00-\u0E7F ]','_',req.name).strip()[:80] or 'kornai_voice'
        return Response(data,media_type='audio/mpeg',headers={'Content-Disposition':f'attachment; filename="voice.mp3"','X-Suggested-Filename':safe+'.mp3'})
    except HTTPException: raise
    except Exception as e: raise HTTPException(502,'สร้างเสียงไม่สำเร็จ: '+str(e)[:160])
