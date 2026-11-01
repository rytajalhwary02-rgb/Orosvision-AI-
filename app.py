import streamlit as st
import numpy as np
from PIL import Image

# إعدادات الواجهة الإكلينيكية
st.set_page_config(
    page_title="OrosVision AI - Advanced Clinical Platform",
    page_icon="👁️",
    layout="wide"
)

st.title("👁️ OrosVision AI: نظام الفحص المبكر ومتابعة الجلوكوما المتقدم")
st.markdown("### Explainable AI-Driven Early Glaucoma Screening & Longitudinal Monitoring Platform")

# القائمة الجانبية للتنقل
app_mode = st.sidebar.selectbox(
    "🧭 أقسام المنصة الإكلينيكية:",
    [
        "📋 التاريخ المرضي والبيانات الإكلينيكية",
        "🔍 الفحص اللحظي والتحليل الذكي (XAI)",
        "📈 المتابعة الزمنية الدقيقة (Longitudinal Tracking)",
        "🎯 التوجيه الطبي والقرارات العاجلة"
    ]
)

# -------------------------------------------------------------
# 1. التاريخ المرضي والبيانات الإكلينيكية
# -------------------------------------------------------------
if app_mode == "📋 التاريخ المرضي والبيانات الإكلينيكية":
    st.header("📋 تسجيل التاريخ المرضي للمريض (Patient Medical History)")
    st.write("أدخلي بيانات المريض الأساسية وتاريخه الطبي لتخصيص خوارزمية التحليل وإصدار التقرير الإكلينيكي الشامل.")

    with st.form("patient_form"):
        col1, col2 = st.columns(2)
        with col1:
            patient_name = st.text_input("اسم المريض / الكود التعريفي:")
            patient_age = st.number_input("العمر:", min_value=1, max_value=120, value=45)
            gender = st.selectbox("الجنس:", ["ذكر", "أنثى"])
        with col2:
            has_diabetes = st.checkbox("تاريخ مصاحب لمرض السكري (Diabetes)")
            has_hypertension = st.checkbox("تاريخ مصاحب لارتفاع ضغط الدم (Hypertension)")
            family_history = st.checkbox("تاريخ عائلي للإصابة بالجلوكوما (Family History)")
        
        submitted = st.form_submit_button("حفظ التاريخ المرضي والانتقال للفحص")
        if submitted:
            st.success(f"✅ تم حفظ بيانات المريض ({patient_name}) بنجاح! يمكنك الآن الانتقال لقسم 'الفحص اللحظي' لإجراء التحليل.")

# -------------------------------------------------------------
# 2. الفحص اللحظي والتحليل الذكي المتغير
# -------------------------------------------------------------
elif app_mode == "🔍 الفحص اللحظي والتحليل الذكي (XAI)":
    st.header("🔍 فحص قاع العين والتحليل اللحظي المتغير")
    st.write("ارفعي صورة قاع العين (Fundus Image) وسيقوم النظام بتحليل الخصائص البصرية الحقيقية لإعطاء نسبة خطورة ديناميكية.")

    uploaded_file = st.file_uploader("اختر صورة قاع العين الحقيقية...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        col_img1, col_img2 = st.columns(2)
        
        with col_img1:
            st.subheader("📷 الصورة المرفوعة للمريض")
            image = Image.open(uploaded_file)
            st.image(image, use_container_width=True)

        with col_img2:
            st.subheader("🔬 نتيجة التحليل الذكي والخرائط الحرارية (Grad-CAM)")
            
            # خوارزمية ذكية تقرأ بكسلات الصورة الحقيقية لض
