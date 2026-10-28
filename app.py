import streamlit as st
import fitz  # PyMuPDF
import deepl
import io
from PIL import Image
import time
import os
import base64
from weasyprint import HTML

# ==========================================
# 1. Page Configuration & Advanced CSS
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
    @keyframes spin { 100% { transform: rotate(360deg); } }

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

# ==========================================
# دالة إنشاء PDF بتصميم احترافي (مطابق للملف)
# ==========================================
def create_designed_pdf(doc, translated_texts):
    html_content = """
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
        body { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; margin: 0; padding: 0; background-color: #ffffff; }
        .page { page-break-after: always; padding: 40px; box-sizing: border-box; height: 100vh; display: flex; flex-direction: column; }
        .title { color: #1e3a8a; font-size: 28pt; font-weight: bold; margin-bottom: 10px; border-bottom: 2px solid #1e3a8a; padding-bottom: 10px; }
        .subtitle { color: #64748b; font-size: 14pt; margin-bottom: 20px; }
        .image-container { text-align: center; margin-bottom: 20px; }
        .image-container img { max-width: 100%; max-height: 40vh; object-fit: contain; border-radius: 10px; }
        .text-container { font-size: 12pt; line-height: 1.8; color: #334155; flex-grow: 1; }
        .footer { text-align: center; font-size: 10pt; color: #94a3b8; margin-top: 20px; border-top: 1px solid #e2e8f0; padding-top: 10px; }
        .highlight { color: #0ea5e9; font-weight: bold; }
    </style>
    </head>
    <body>
    """
    
    for i, page in enumerate(doc):
        # 1. استخراج الصورة
        pix = page.get_pixmap(dpi=150)
        img_bytes = pix.tobytes("png")
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        
        # 2. محاولة استخراج العنوان (أول سطر في النص الإنجليزي)
        text_english = page.get_text("text")
        lines = text_english.strip().split('\n')
        title = lines[0].strip() if lines else f"Page {i+1}"
        
        # 3. تجهيز النص المترجم
        text_arabic = translated_texts[i]
        
        # 4. بناء الصفحة
        html_content += f"""
        <div class="page">
            <div class="title">{title}</div>
            <div class="image-container">
                <img src="data:image/png;base64,{img_base64}">
            </div>
            <div class="text-container">
                {text_arabic}
            </div>
            <div class="footer">Translated Page {i+1} | Developed by Eng. Motaz Al-Kade</div>
        </div>
        """
        
    html_content += "</body></html>"
    
    pdf_buffer = io.BytesIO()
    HTML(string=html_content).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    
    return pdf_buffer

# ==========================================
# 3. Main App Logic
# ==========================================
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
        
        # Overlay
        overlay_placeholder = st.empty()
        overlay_placeholder.markdown(f"""
        <div style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.8); z-index: 9999; display: flex; justify-content: center; align-items: center; backdrop-filter: blur(5px);">
            <div style="background: linear-gradient(135deg, #0f172a, #1e293b); padding: 40px; border-radius: 20px; border: 2px solid #38bdf8; box-shadow: 0 0 50px rgba(56, 189, 248, 0.5); text-align: center; max-width: 500px; animation: floatCard 3s infinite;">
                <div style="font-size: 50px; margin-bottom: 20px; animation: spin 2s linear infinite; display: inline-block;">⚙️</div>
                <h2 style="color: #38bdf8; margin-bottom: 10px;">AI Engine Processing</h2>
                <p style="color: #94a3b8;">Extracting data and translating securely...</p>
                <div style="width: 100%; height: 10px; background: #334155; border-radius: 5px; overflow: hidden; margin-top: 20px;">
                    <div style="width: 50%; height: 100%; background: linear-gradient(90deg, #38bdf8, #818cf8); animation: pulseGlow 1s infinite;"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
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
            
        overlay_placeholder.empty()
        status_text.success("✅ Translation Complete! System Idle.")
        log_placeholder.code("> Status: Success\n> Engine: Idle\n> Awaiting next command...")
        st.toast("✅ Translation Completed Successfully!", icon="🎉")
        
        # إنشاء PDF وعرض زر التحميل
        with st.spinner("📦 Packaging beautifully formatted PDF..."):
            pdf_buffer = create_designed_pdf(doc, translated_pages)
            st.download_button(
                label="📥 Download Designed PDF (Arabic)",
                data=pdf_buffer,
                file_name="Translated_Designed_Doc.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary"
            )
            st.info("💡 **Tip:** This PDF is generated with the original images and has perfect Arabic text formatting.")
        
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
        if 'overlay_placeholder' in locals():
            overlay_placeholder.empty()

html_card = """<div class="pro-credit-box"><div class="pro-title">💻 System Architecture & Development</div><div class="pro-name">Eng. Motaz Al-Kade</div><div class="pro-role">Cyber Security Engineer | AI & Data Science Enthusiast</div><a href="https://wa.me/967739507539" target="_blank" class="pro-btn"><span class="pro-icon">📱</span>WhatsApp: +967 739 507 539</a><a href="https://t.me/Motazalkade" target="_blank" class="pro-btn"><span class="pro-icon">✈️</span>Telegram: @Motazalkade</a></div>"""
st.markdown(html_card, unsafe_allow_html=True)
