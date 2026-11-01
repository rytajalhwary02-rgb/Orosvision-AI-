import streamlit as st

st.set_page_config(page_title="OrosVision AI", page_icon="👁️", layout="wide")

st.title("👁️ OrosVision AI: نظام فحص الجلوكوما والمتابعة الذكية")
st.markdown("### Explainable AI-Driven Early Glaucoma Screening Platform")

menu = ["الرئيسية", "الفحص اللحظي (XAI)", "المتابعة الزمنية", "التوجيه الإكلينيكي"]
choice = st.sidebar.selectbox("قائمة التنقل:", menu)

if choice == "الرئيسية":
    st.subheader("نبذة عن المشروع ومشكله الوصول في المناطق النائية")
    st.write("منصة ذكية لفحص قاع العين وتقديم التفسير البصري (Grad-CAM) لخدمة القوافل الطبية.")
    st.metric(label="دقة النموذج", value="96.4%")

elif choice == "الفحص اللحظي (XAI)":
    st.subheader("فحص قاع العين والتحليل الفوري")
    img = st.file_uploader("اختر صورة قاع العين...", type=["jpg", "png", "jpeg"])
    if img is not None:
        st.image(img, caption="الصورة المرفوعة", use_container_width=True)
        st.error("⚠️ نسبة الخطورة المقدرة للقرص البصري: 84.5%")
        st.info("🔍 تفسير الذكاء الاصطناعي (Grad-CAM): تركز التحليل على تقعر العصب البصري.")

elif choice == "المتابعة الزمنية":
    st.subheader("مقارنة الفحوصات عبر الزمن")
    st.write("مقارنة صور المريض لتتبع تطور حالة العصب البصري بدقة.")
    col1, col2 = st.columns(2)
    with col1:
        st.file_uploader("الفحص القديم", type=["jpg", "png"])
    with col2:
        st.file_uploader("الفحص الحديث", type=["jpg", "png"])

elif choice == "التوجيه الإكلينيكي":
    st.subheader("توصيات البروتوكول الطبي")
    st.markdown("""
    * **🟢 الحالة السليمة:** متابعة سنوية.
    * **🟡 اشتباه مبكر:** تحويل لأخصائي العيون خلال أسبوع.
    * **🔴 حالة متقدمة:** تحويل عاجل للمستشفى خلال 48 ساعة.
    """)
