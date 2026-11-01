import streamlit as st
import numpy as np
from PIL import Image

# إعدادات الواجهة الراقية
st.set_page_config(
    page_title="OrosVision AI - Care & Clinical Platform",
    page_icon="👁️",
    layout="wide"
)

# تصميم بصري هادئ ومريح
st.markdown("""
    <style>
    .main { background-color: #fafbfc; }
    .stAlert { border-radius: 12px; }
    h1, h2, h3 { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #1e293b; }
    </style>
""", unsafe_allow_html=True)

st.title("👁️ OrosVision AI: نحمي بصراً.. لنضيء حياةً 🤍")
st.markdown("### *Explainable AI-Driven Early Glaucoma Screening & Longitudinal Monitoring Platform*")
st.markdown("---")

# القائمة الجانبية بتصميم راقٍ
app_mode = st.sidebar.selectbox(
    "🧭 رحلتنا الإكلينيكية:",
    [
        "🔍 الفحص اللحظي والتحليل التفسيري (XAI)",
        "📈 المتابعة الزمنية الدافئة (Longitudinal Tracking)",
        "📋 التوجيه الإنساني والقرارات الطبية"
    ]
)

# -------------------------------------------------------------
# 1. الفحص اللحظي وتحليل الذكاء الاصطناعي
# -------------------------------------------------------------
if app_mode == "🔍 الفحص اللحظي والتحليل التفسيري (XAI)":
    st.header("🔍 الفحص اللحظي والاطمئنان على سلامة العصب البصري")
    st.write("أهلاً بكِ. نحن هنا لنحول كل صورة إلى رسالة أمان واضحة ودقيقة.")

    with st.expander("📝 ملف المريض والتاريخ الإكلينيكي (لضمان رعاية مخصصة)"):
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            p_name = st.text_input("اسم المريض أو الكود التعريفي:")
            p_age = st.number_input("العمر:", min_value=1, max_value=120, value=45)
        with col_p2:
            has_dm = st.checkbox("تاريخ مصاحب لمرض السكري (Diabetes)")
            has_htn = st.checkbox("تاريخ ارتفاع ضغط الدم (Hypertension)")

    st.markdown("---")
    uploaded_file = st.file_uploader("الرجاء اختيار صورة قاع العين الحقيقية (Fundus Image)...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        col_img1, col_img2 = st.columns(2)
        
        with col_img1:
            st.subheader("📷 صورة قاع العين المرفوعة")
            image = Image.open(uploaded_file)
            st.image(image, use_container_width=True)

        with col_img2:
            st.subheader("🔬 قراءة الذكاء الاصطناعي والتقرير التفسيري")
            
            # معالجة حقيقية وآمنة للصورة لإعطاء النسبة فور
