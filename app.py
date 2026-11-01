import streamlit as st
import numpy as np
from PIL import Image
import pandas as pd
import time

# إعدادات الصفحة وتصميم الواجهة
st.set_page_config(
    page_title="OrosVision AI - Glaucoma Screening",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تخصيص التصميم والألوان (CSS) لتظهر بشكل أكاديمي واحترافي
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        background-color: #0d6efd;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #0b5ed7;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# الشريط الجانبي للتنقل بين أقسام المنصة
st.sidebar.image("https://img.icons8.com/color/96/experimental-idea--v2.png", width=80)
st.sidebar.title("OrosVision AI")
st.sidebar.markdown("---")
app_mode = st.sidebar.radio(
    "اختر القسم:",
    ["🏠 الرئيسية ونبذة المشروع", "🔍 الفحص والتشخيص اللحظي (XAI)", "📈 المتابعة الزمنية والمقارنة", "📋 دليل التوجيه الإكلينيكي"]
)

# -------------------------------------------------------------
# 1. الصفحة الرئيسية
# -------------------------------------------------------------
if app_mode == "🏠 الرئيسية ونبذة المشروع":
    st.title("👁️ منصة التشخيص ومتابعة الجلوكوما المبكر المعتمد على الذكاء الاصطناعي التفسيري")
    st.markdown("### Explainable AI-Driven Early Glaucoma Screening & Monitoring Platform")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **المشكلة الأساس
        
