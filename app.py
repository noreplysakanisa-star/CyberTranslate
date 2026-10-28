import streamlit as st
import fitz  # PyMuPDF
import deepl
import io
from PIL import Image

# ==========================================
# 1. Page Configuration & Advanced CSS
# ==========================================
st.set_page_config(
    page_title="CyberTranslate AI | Motaz Al-Kade",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&family=Poppins:wght@300;500;700&display=swap');
    .stApp { background: radial-gradient(circle at top right, #1e293b, #0f172a, #020617); font-family: 'Cairo', 'Poppins', sans-serif; color: #e2e8f0; }
    h1, h2, h3, h4 { font-family: 'Cairo', sans-serif !important; font-weight: 700 !important; color: #38bdf8 !important; text-shadow: 0 0 15px rgba(56, 189, 248, 0.3); }
    .stFileUploader { background: rgba(30, 41, 59, 0.6); backdrop-filter: blur(10px); border: 2px dashed #38bdf8; border-radius: 15px; padding: 20px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3); transition: all 0.3s ease; }
    .stFileUploader:hover { border-color: #818cf8; box-shadow: 0 0 25px rgba(129, 140, 248, 0.5); }
    .text-card { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); border-left: 5px solid #38bdf8; padding: 25px; border-radius: 12px; margin-top: 10px; box-shadow: 0 10px 40px 0 rgba(0, 0, 0, 0.4); line-height: 2; font-size: 16px; color: #f1f5f9; direction: rtl; text-align: right; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] { background-color: #1e293b; border-radius: 8px; color: #94a3b8; padding: 10px 20px; border: 1px solid #334155; transition: all 0.3s; font-family: 'Cairo', sans-serif; }
    .stTabs [aria-selected="true"] { background: linear-gradient(90deg, #38bdf8, #818cf8) !important; color: #0f172a !important; font-weight: bold; border: none; box-shadow: 0 0 15px rgba(56, 189, 248, 0.4); }
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #38bdf8, #818cf8); }
    @keyframes floatCard { 0% { transform: translateY(0px); box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5); } 50% { transform: translateY(-8px); box-shadow: 0 20px 40px rgba(56, 189, 248, 0.2); } 100% { transform: translateY(0px); box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5); } }
    .pro-credit-box { background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.95)); border: 2px solid rgba(56, 189, 248, 0.3); border-radius: 25px; padding: 40px 20px; margin: 60px auto; max-width: 700px; text-align: center; animation: floatCard 4s ease-in-out infinite; backdrop-filter: blur(15px); font-family: 'Cairo', sans-serif; }
    .pro-title { color: #38bdf8; font-size: 18px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 10px; }
    .pro-name { color: #ffffff; font-size: 32px; font-weight: 900; margin-bottom: 5px; text-shadow: 0 0 20px rgba(56, 189, 248, 0.6); }
    .pro-role { color: #94a3b8; font-size: 16px; margin-bottom: 30px; font-weight: 500; }
    .pro-btn { display: inline-block; background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.5); color: #ffffff !important; padding: 12px 25px; border-radius: 50px; margin: 10px; font-size: 16px; text-decoration: none !important; transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); font-weight: 600; }
    .pro-btn:hover { background: linear-gradient(90deg, #38bdf8, #818cf8); color: #0f172a !important; transform: scale(1.1) translateY(-5px); box-shadow: 0 10px 25px rgba(56, 189, 248, 0.6); border-color: transparent; }
    .pro-icon { margin-right: 10px; font-size: 20px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🛡️ CyberTranslate AI</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; font-weight: 400 !important;'>Secure PDF Parsing & Intelligent Translation Engine</h3>", unsafe_allow_html=True)
st.divider()

# ==========================================
# 2. Core Logic (DeepL Integration)
# ==========================================
uploaded_file = st.file_uploader("📂 Drop your PDF file here", type=["pdf"])

if uploaded_file is not None:
    # التحقق من وجود المفتاح السري
    if "DEEPL_API_KEY" not in st.secrets:
        st.error("⚠️ Error: DeepL API Key not found in Streamlit Secrets. Please add it in App Settings.")
        st.stop()
        
    try:
        # تهيئة محرك DeepL
        deepl_key = st.secrets["DEEPL_API_KEY"]
        translator = deepl.Translator(deepl_key)
        
        # قراءة الملف في الذاكرة
        file_bytes = uploaded_file.read()
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        
        st.success(f"✅ File loaded securely! Total Pages: {len(doc)}")
        
        translated_pages = {}
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for page_num in range(len(doc)):
            status_text.text(f"🔍 Translating Page {page_num + 1}/{len(doc)} via DeepL AI...")
            page = doc.load_page(page_num)
            text = page.get_text("text")
            
            if text.strip():
                try:
                    # ترجمة النص بالكامل باستخدام DeepL
                    result = translator.translate_text(text, source_lang="EN", target_lang="AR")
                    translated_text = result.text
                except deepl.QuotaExceededException:
                    translated_text = "⚠️ Error: DeepL API Quota Exceeded. Please check your account limits."
                except deepl.AuthorizationException:
                    translated_text = "⚠️ Error: Invalid DeepL API Key. Please check your Secrets configuration."
                except Exception as e:
                    translated_text = f"⚠️ Translation Error: {str(e)}"
            else:
                translated_text = "(No readable text detected on this page. It might be an image-only page.)"
            
            translated_pages[page_num] = translated_text
            progress_bar.progress((page_num + 1) / len(doc))
            
        status_text.text("✅ Processing Complete! Review the results below.")
        
        # ==========================================
        # 3. Display Results
        # ==========================================
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

# ==========================================
# 4. Luxury Credit & Contact Card
# ==========================================
html_card = """<div class="pro-credit-box"><div class="pro-title">💻 System Architecture & Development</div><div class="pro-name">Eng. Motaz Al-Kade</div><div class="pro-role">Cyber Security Engineer | AI & Data Science Enthusiast</div><a href="https://wa.me/967739507539" target="_blank" class="pro-btn"><span class="pro-icon">📱</span>WhatsApp: +967 739 507 539</a><a href="https://t.me/Motazalkade" target="_blank" class="pro-btn"><span class="pro-icon">✈️</span>Telegram: @Motazalkade</a></div>"""
st.markdown(html_card, unsafe_allow_html=True)
