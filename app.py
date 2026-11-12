import streamlit as st
from gtts import gTTS
from io import BytesIO
import re, tempfile, subprocess, shutil
from pathlib import Path

st.set_page_config(page_title='KornAiStudio Scan & Voice',page_icon='🎙️',layout='centered')
st.markdown('''<style>.stApp{background:#f5f8ff}h1,h2,h3{color:#164da9}div.stButton>button[kind="primary"]{background:#195bc7;border-radius:12px}div[data-testid="stVerticalBlockBorderWrapper"]{border-radius:18px}</style>''',unsafe_allow_html=True)
st.title('🎙️ KornAiStudio Scan & Voice')
st.caption('เว็บใหม่แยกจาก texttospeedkorn · สร้างเสียง Google gTTS · ดาวน์โหลด MP3')

def segments(text):
    result=[]
    for line in text.splitlines():
        line=line.strip()
        if not line: continue
        # Separate Thai and non-Thai runs while keeping their original order.
        for chunk in re.findall(r'[\u0E00-\u0E7F][\u0E00-\u0E7F\s\d.,!?()\-–—:;]*|[A-Za-z][^\u0E00-\u0E7F]*',line):
            chunk=chunk.strip()
            if chunk: result.append((chunk,'th' if re.search(r'[\u0E00-\u0E7F]',chunk) else 'en'))
    return result

def make_mp3(text,slow):
    chunks=segments(text)
    if not chunks: raise ValueError('ไม่พบข้อความภาษาอังกฤษหรือภาษาไทย')
    if len(chunks)>100: raise ValueError('ข้อความมีช่วงภาษามากเกินไป กรุณาแบ่งเป็นตอน')
    with tempfile.TemporaryDirectory() as tmp:
        paths=[]
        for i,(words,lang) in enumerate(chunks):
            # gTTS handles long input by splitting it internally.
            path=Path(tmp)/f'{i:04d}.mp3'
            gTTS(text=words,lang=lang,slow=slow).save(str(path))
            paths.append(path)
        if len(paths)==1: return paths[0].read_bytes()
        if not shutil.which('ffmpeg'):
            raise RuntimeError('เซิร์ฟเวอร์ยังไม่มี FFmpeg สำหรับรวมเสียง กรุณาติดตั้ง packages.txt')
        listing=Path(tmp)/'concat.txt'
        listing.write_text(''.join(f"file '{p.as_posix()}'\n" for p in paths),encoding='utf-8')
        output=Path(tmp)/'combined.mp3'
        result=subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(listing),'-c:a','libmp3lame','-q:a','4',str(output)],capture_output=True,text=True,timeout=180)
        if result.returncode: raise RuntimeError('รวมเสียงไม่สำเร็จ: '+result.stderr[:300])
        return output.read_bytes()

with st.container(border=True):
    text=st.text_area('ข้อความภาษาอังกฤษและภาษาไทย',height=260,placeholder='Once upon a time...\nกาลครั้งหนึ่ง...',key='text')
    st.caption(f'{len(text):,} / 15,000 ตัวอักษร')
    name=st.text_input('ชื่อไฟล์ MP3',value='นิทานสองภาษา')
    slow=st.checkbox('อ่านช้า')
    if st.button('🔊 สร้าง MP3',type='primary',use_container_width=True):
        if not text.strip(): st.warning('กรุณาใส่ข้อความ')
        elif len(text)>15000: st.error('ข้อความเกิน 15,000 ตัวอักษร')
        else:
            try:
                with st.spinner('กำลังสร้างเสียงภาษาอังกฤษและไทย...'):
                    st.session_state.mp3=make_mp3(text,slow)
                st.success('สร้าง MP3 สำเร็จ')
            except Exception as e:
                st.session_state.pop('mp3',None)
                st.error(f'สร้าง MP3 ไม่สำเร็จ: {e}')
    if st.session_state.get('mp3'):
        st.audio(st.session_state.mp3,format='audio/mp3')
        safe=re.sub(r'[\\/:*?"<>|]','_',name).strip().removesuffix('.mp3') or 'kornai_voice'
        st.download_button('⬇️ ดาวน์โหลด MP3',data=st.session_state.mp3,file_name=safe+'.mp3',mime='audio/mpeg',type='primary',use_container_width=True)
        st.info('ต้องการส่ง LINE, WhatsApp, Messenger หรืออีเมล: ดาวน์โหลดไฟล์ แล้วใช้เมนูแชร์ไฟล์ในโทรศัพท์')

with st.expander('📷 ภาพถ่าย → ข้อความ (OCR)'):
    photo=st.file_uploader('ถ่ายภาพหรือเลือกรูปตัวหนังสือ',type=['png','jpg','jpeg'])
    if photo:
        st.image(photo,caption='ภาพที่เลือก',use_container_width=True)
        st.info('OCR ภาษาไทย–อังกฤษยังไม่เปิดใช้งานในรุ่น Streamlit นี้ เพื่อไม่ให้แสดงผลลัพธ์ที่ไม่จริง')
with st.expander('🎤 บันทึกเสียงของฉัน'):
    audio=st.audio_input('บันทึกเสียง')
    if audio:
        st.audio(audio)
        st.download_button('⬇️ ดาวน์โหลดเสียงต้นฉบับ WAV',audio.getvalue(),file_name='my_voice.wav',mime='audio/wav')
        st.caption('การแปลงเสียงบันทึกเป็น MP3 ยังไม่พร้อมในรุ่นนี้')
with st.expander('🌐 แปลภาษา / 🎨 ภาพประกอบ'):
    st.info('ระบบแปลภาษาและสร้างภาพ AI ยังไม่เชื่อมต่อในรุ่นนี้ ต้องใช้บริการเพิ่มเติม จึงยังไม่เปิดปุ่มที่ใช้งานไม่ได้')
st.caption('gTTS ต้องเชื่อมต่ออินเทอร์เน็ต · แพ็กเกจ Streamlit Community Cloud ฟรีมีข้อจำกัดการใช้งาน · ไม่ใช่การรับประกันการให้บริการ')
