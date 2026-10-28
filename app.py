import streamlit as st
import fitz  # PyMuPDF
import deepl
import io
from PIL import Image
import time
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ==========================================
# 1. Page Configuration & Advanced CSS (Cyber Animations)
# ==========================================
st.set_page_config(
    page_title="CyberTranslate AI | Motaz Al-Kade",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&family=Poppins:wght@300;500;700&display=swap');
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes pulseGlow { 0% { box-shadow: 0 0 5px rgba(56, 189, 248, 0.2); } 50% { box-shadow: 0 0 20px rgba(56, 189, 248, 0.8); } 100% { box-shadow: 0 0 5px rgba(56, 189, 248, 0.2); } }
    @keyframes scanline { 0% { transform: translateY(-100%); } 100% { transform: translateY(100%); } }
    @keyframes floatCard { 0% { transform: translateY(0px); } 50% { transform: translateY(-8px); } 100% { transform: translateY(0px); } }

    .stApp { background: radial-gradient(circle at top right, #1e293b, #0f172a, #020617); font-family: 'Cairo', 'Poppins', sans-serif; color: #e2e8f0; }
    h1, h2, h3, h4 { font-family: 'Cairo', sans-serif !important; font-weight: 700 !important; color: #38bdf8 !important; text-shadow: 0 0 15px rgba(56, 189, 248, 0.3); }
    [data-testid="stSidebar"] { background-color: #0f172a !important; border-right: 1px solid #1e293b; }
    .sys-status { background: rgba(30, 41, 59, 0.5); border: 1px solid #334155; border-radius: 10px; padding: 15px; margin-bottom: 15px; position: relative; overflow: hidden; }
    .sys-status::after { content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(to bottom, transparent, rgba(56, 189, 248, 0.1), transparent); animation: scanline 3s linear infinite; }
    .status-dot { display: inline-block; width: 10px; height: 10px; background-color: #10b981; border-radius: 50%; margin-right: 10px; animation: pulseGlow 2s infinite; }
    .stFileUploader { background: rgba(30, 41, 59, 0.6); backdrop-filter: blur(10px); border: 2px dashed #38bdf8; border-radius: 15px; padding: 20px; transition: all 0.3s ease; }
    .stFileUploader:hover { border-color: #818cf8; box-shadow: 0 0 25px rgba(129, 140, 248, 0.5); }
    .text-card { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); border-left: 5px solid #38bdf8; padding: 25px; border-radius: 12px; margin-top: 10px; box-shadow: 0 10px 40px 0 rgba(0, 0, 0, 0.4); line-height: 2; font-size: 16px; color: #f1f5f9; direction: rtl; text-align: right; animation: fadeInUp 0.8s ease-out forwards; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] { background-color: #1e293b; border-radius: 8px; color: #94a3b8; padding: 10px 20px; border: 1px solid #334155; transition: all 0.3s; }
    .stTabs [aria-selected="true"] { background: linear-gradient(90deg, #38bdf8, #818cf8) !important; color: #0f172a !important; font-weight: bold; border: none; box-shadow: 0 0 15px rgba(56, 189, 248, 0.4); }
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #38bdf8, #818cf8); animation: pulseGlow 2s infinite; }
    
    .pro-credit-box { background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.95)); border: 2px solid rgba(56, 189, 248, 0.3); border-radius: 25px; padding: 40px 20px; margin: 60px auto; max-width: 700px; text-align: center; animation: floatCard 4s ease-in-out infinite; backdrop-filter: blur(15px); }
    .pro-title { color: #38bdf8; font-size: 18px; font-weight: 700; letter-spacing: 2px; margin-bottom: 10px; }
    .pro-name { color: #ffffff; font-size: 32px; font-weight: 900; margin-bottom: 5px; }
    .pro-role { color: #94a3b8; font-size: 16px; margin-bottom: 30px; }
    .pro-btn { display: inline-block; background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.5); color: #ffffff !important; padding: 12px 25px; border-radius: 50px; margin: 10px; text-decoration: none !important; transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
    .pro-btn:hover { background: linear-gradient(90deg, #38bdf8, #818cf8); color: #0f172a !important; transform: scale(1.1) translateY(-5px); box-shadow: 0 10px 25px rgba(56, 189, 248, 0.6); }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🖥️ System Status")
    status_placeholder = st.empty()
    status_placeholder.markdown("""<div class='sys-status'><span class='status-dot'></span> <b>Engine:</b> Online<br><span class='status-dot' style='background-color: #38bdf8;'></span> <b>Core:</b> DeepL AI<br><span class='status-dot' style='background-color: #818cf8;'></span> <b>Security:</b> In-Memory</div>""", unsafe_allow_html=True)
    st.markdown("### 📡 Network Logs")
    log_placeholder = st.empty()
    log_placeholder.code("Waiting for input...\n> _")

def create_translated_pdf(doc, translated_texts):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # مسار الخط المحلي (الذي تم رفعه على GitHub)
    font_path = "Amiri-Regular.ttf"
    pdfmetrics.registerFont(TTFont('Amiri', font_path))

    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=120)
        img_path = f"temp_page_{i}.png"
        pix.save(img_path)
        
        img_width = width - 80
        img_height = (pix.height / pix.width) * img_width
        if img_height > height * 0.5: 
            img_height = height * 0.5
            img_width = (pix.width / pix.height) * img_height
            
        c.drawImage(img_path, (width - img_width)/2, height - img_height - 30, width=img_width, height=img_height)
        os.remove(img_path)

        text_object = c.beginText()
        text_object.setTextOrigin(40, height - img_height - 50)
        text_object.setFont("Amiri", 12)
        
        words = translated_texts[i].split()
        line = ""
        y_position = height - img_height - 50
        
        for word in words:
            if pdfmetrics.stringWidth(line + " " + word, "Amiri", 12) < width - 80:
                line += word + " "
            else:
                text_object.textLine(line)
                line = word + " "
                y_position -= 18
                if y_position < 40:
                    c.drawText(text_object)
                    c.showPage()
                    c.setFont("Amiri", 12)
                    text_object = c.beginText()
                    text_object.setTextOrigin(40, height - 40)
                    y_position = height - 40

        if line:
            text_object.textLine(line)
        c.drawText(text_object)
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(40, height - 20, f"Translated Page {i+1} | Developed by Eng. Motaz Al-Kade")
        c.showPage()

    c.save()
    buffer.seek(0)
    return buffer

st.markdown("<h1 style='text-align: center;'>🛡️ CyberTranslate AI</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; font-weight: 400 !important;'>Secure PDF Parsing & Intelligent Translation Engine</h3>", unsafe_allow_html=True)
st.divider()

uploaded_file = st.file_uploader("📂 Drop your PDF file here", type=["pdf"])

if uploaded_file is not None:
    if "DEEPL_API_KEY" not in st.secrets:
        st.error("⚠️ Error: DeepL API Key not found in Streamlit Secrets.")
        st.stop()
        
    try:
        st.toast("🔐 Secure connection established.", icon="🛡️")
        time.sleep(0.5)
        
        deepl_key = st.secrets["DEEPL_API_KEY"]
        translator = deepl.Translator(deepl_key)
        
        file_bytes = uploaded_file.read()
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        
        st.success(f"✅ File loaded securely! Total Pages: {len(doc)}")
        log_placeholder.code(f"> File: {uploaded_file.name}\n> Size: {len(file_bytes)/1024:.1f} KB\n> Pages: {len(doc)}\n> Status: Ready")
        
        translated_pages = {}
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for page_num in range(len(doc)):
            status_text.markdown(f"<div style='color:#38bdf8; animation: pulseGlow 1s infinite;'>⚙️ Analyzing & Translating Page {page_num + 1}/{len(doc)}...</div>", unsafe_allow_html=True)
            log_placeholder.code(f"> Processing Page {page_num + 1}...\n> Extracting Text...\n> Calling DeepL API...")
            
            page = doc.load_page(page_num)
            text = page.get_text("text")
            
            if text.strip():
                try:
                    result = translator.translate_text(text, source_lang="EN", target_lang="AR")
                    translated_text = result.text
                except Exception as e:
                    translated_text = f"⚠️ Translation Error: {str(e)}"
            else:
                translated_text = "(No readable text detected on this page.)"
            
            translated_pages[page_num] = translated_text
            progress_bar.progress((page_num + 1) / len(doc))
            time.sleep(0.5)
            
        status_text.success("✅ Translation Complete! System Idle.")
        log_placeholder.code("> Status: Success\n> Engine: Idle\n> Awaiting next command...")
        
        with st.spinner("📦 Packaging secure PDF..."):
            pdf_buffer = create_translated_pdf(doc, translated_pages)
            st.download_button(
                label="📥 Download Translated PDF",
                data=pdf_buffer,
                file_name="Translated_CyberDoc.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        st.markdown("---")
        st.markdown("### 📊 Translation Results")
        tabs = st.tabs([f"📄 Page {i+1}" for i in range(len(doc))])
        
        for i, tab in enumerate(tabs):
            with tab:
                col1, col2 = st.columns([1, 1], gap="large")
                with col1:
                    st.markdown("<h4>🇸🇦 Translated Text</h4>", unsafe_allow_html=True)
                    st.markdown(f"<div class='text-card'>{translated_pages[i]}</div>", unsafe_allow_html=True)
                with col2:
                    st.markdown("<h4>🖼️ Original Page Visual</h4>", unsafe_allow_html=True)
                    page = doc.load_page(i)
                    pix = page.get_pixmap(dpi=150)
                    img = Image.open(io.BytesIO(pix.tobytes("png")))
                    st.image(img, use_container_width=True, caption=f"Original Page {i+1}")

    except Exception as e:
        st.error(f"❌ Critical System Error: {str(e)}")

html_card = """<div class="pro-credit-box"><div class="pro-title">💻 System Architecture & Development</div><div class="pro-name">Eng. Motaz Al-Kade</div><div class="pro-role">Cyber Security Engineer | AI & Data Science Enthusiast</div><a href="https://wa.me/967739507539" target="_blank" class="pro-btn"><span class="pro-icon">📱</span>WhatsApp: +967 739 507 539</a><a href="https://t.me/Motazalkade" target="_blank" class="pro-btn"><span class="pro-icon">✈️</span>Telegram: @Motazalkade</a></div>"""
st.markdown(html_card, unsafe_allow_html=True)
