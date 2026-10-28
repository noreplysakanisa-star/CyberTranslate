import streamlit as st
import fitz  # PyMuPDF
from deep_translator import GoogleTranslator
import io
from PIL import Image
import time

# ==========================================
# 1. Page Configuration & Advanced CSS
# ==========================================
st.set_page_config(
    page_title="CyberTranslate AI | Motaz Al-Kade",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for a "Cyber" & "Professional" Look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&family=Poppins:wght@300;500;700&display=swap');

    /* Main Background & Font */
    .stApp {
        background: radial-gradient(circle at top right, #1e293b, #0f172a, #020617);
        font-family: 'Cairo', 'Poppins', sans-serif;
        color: #e2e8f0;
    }

    /* Headers Styling */
    h1, h2, h3, h4 {
        font-family: 'Cairo', sans-serif !important;
        font-weight: 700 !important;
        color: #38bdf8 !important;
        text-shadow: 0 0 15px rgba(56, 189, 248, 0.3);
    }

    /* File Uploader Styling */
    .stFileUploader {
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(10px);
        border: 2px dashed #38bdf8;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    .stFileUploader:hover {
        border-color: #818cf8;
        box-shadow: 0 0 25px rgba(129, 140, 248, 0.5);
    }

    /* Custom Card for Text */
    .text-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        border-left: 5px solid #38bdf8;
        padding: 25px;
        border-radius: 12px;
        margin-top: 10px;
        box-shadow: 0 10px 40px 0 rgba(0, 0, 0, 0.4);
        line-height: 2;
        font-size: 16px;
        color: #f1f5f9;
        direction: rtl;
        text-align: right;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        border-radius: 8px;
        color: #94a3b8;
        padding: 10px 20px;
        border: 1px solid #334155;
        transition: all 0.3s;
        font-family: 'Cairo', sans-serif;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #38bdf8, #818cf8) !important;
        color: #0f172a !important;
        font-weight: bold;
        border: none;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
    }

    /* Progress Bar Styling */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #38bdf8, #818cf8);
    }

    /* Luxury Credit Card */
    .credit-card {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(30, 41, 59, 0.9));
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 20px;
        padding: 25px;
        margin-top: 50px;
        text-align: center;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5), inset 0 0 20px rgba(56, 189, 248, 0.1);
        backdrop-filter: blur(10px);
    }
    .credit-title {
        color: #38bdf8;
        font-size: 20px;
        font-weight: 900;
        margin-bottom: 15px;
        text-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
    }
    .credit-name {
        color: #f1f5f9;
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 20px;
        letter-spacing: 1px;
    }
    .contact-badge {
        display: inline-block;
        background: rgba(56, 189, 248, 0.1);
        border: 1px solid rgba(56, 189, 248, 0.4);
        padding: 8px 20px;
        border-radius: 50px;
        margin: 5px;
        color: #e2e8f0;
        font-size: 15px;
        text-decoration: none;
        transition: all 0.3s ease;
    }
    .contact-badge:hover {
        background: rgba(56, 189, 248, 0.25);
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
        transform: translateY(-2px);
    }
    .contact-icon {
        margin-right: 8px;
        font-size: 18px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. Application Header
# ==========================================
st.markdown("<h1 style='text-align: center;'>🛡️ CyberTranslate AI</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; font-weight: 400 !important;'>Secure PDF Parsing & Intelligent Translation Engine</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8;'>Upload an English PDF to extract text, translate it to Arabic, and review images securely in-memory.</p>", unsafe_allow_html=True)
st.divider()

# ==========================================
# 3. Core Logic
# ==========================================
uploaded_file = st.file_uploader("📂 Drop your PDF file here", type=["pdf"])

if uploaded_file is not None:
    # Read into memory (Cyber Security Best Practice - no disk writes)
    file_bytes = uploaded_file.read()
    
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        st.success(f"✅ File loaded securely! Total Pages: {len(doc)}")
        
        translated_pages = {}
        
        # Cyber-style progress bar
        st.markdown("### ⚙️ Processing Pipeline")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for page_num in range(len(doc)):
            status_text.text(f"🔍 Analyzing & Translating Page {page_num + 1}/{len(doc)}...")
            page = doc.load_page(page_num)
            
            # 1. Extract Text
            text = page.get_text("text")
            
            # 2. Translate (with error handling & chunking)
            if text.strip():
                try:
                    translator = GoogleTranslator(source='en', target='ar')
                    
                    # Chunking text if it's too long (API limits)
                    max_chars = 4500
                    if len(text) > max_chars:
                        chunks = [text[i:i+max_chars] for i in range(0, len(text), max_chars)]
                        translated_chunks = []
                        for chunk in chunks:
                            translated_chunks.append(translator.translate(chunk))
                            time.sleep(0.3) # Slight delay to prevent rate limiting
                        translated_text = " ".join(translated_chunks)
                    else:
                        translated_text = translator.translate(text)
                        
                except Exception as trans_err:
                    translated_text = f"⚠️ [Translation Error: {str(trans_err)}]"
            else:
                translated_text = "(No readable text detected on this page. It might be an image-only page.)"
            
            translated_pages[page_num] = translated_text
            progress_bar.progress((page_num + 1) / len(doc))
            
        status_text.text("✅ Processing Complete! Review the results below.")
        
        # ==========================================
        # 4. Display Results
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
        st.error(f"❌ Critical Error: Unable to process the file. Details: {str(e)}")
        st.info("💡 Tip: Ensure the PDF is not password-protected or corrupted.")

# ==========================================
# 5. Luxury Credit & Contact Card
# ==========================================
st.markdown("""
<div class='credit-card'>
    <div class='credit-title'>💻 System Architecture & Development</div>
    <div class='credit-name'>Eng. Motaz Al-Kade</div>
    <p style='color: #94a3b8; margin-bottom: 20px;'>Cyber Security Engineer | AI & Data Science Enthusiast</p>
    
    <a href='https://wa.me/967739507539' target='_blank' class='contact-badge'>
        <span class='contact-icon'>📱</span> WhatsApp: +967 739 507 539
    </a>
    
    <a href='https://t.me/Motazalkade' target='_blank' class='contact-badge'>
        <span class='contact-icon'>✈️</span> Telegram: @Motazalkade
    </a>
</div>
""", unsafe_allow_html=True)