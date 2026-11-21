import time
import cv2
import numpy as np
from PIL import Image
import streamlit as st
import torch
import torch.nn as nn
from torchvision import models, transforms

# -------------------------------------------------------------
# إعدادات الصفحة
# -------------------------------------------------------------
st.set_page_config(
    page_title="OrosVision AI",
    page_icon="🕯️",
    layout="wide"
)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
THRESHOLD = 0.42
WEIGHTS_PATH = "best_glaucoma_clahe_finetuned.pth"


# -------------------------------------------------------------
# تحميل الموديل الحقيقي + CLAHE + Grad-CAM
# -------------------------------------------------------------
@st.cache_resource
def load_glaucoma_model(weights_path: str):
    model = models.resnet18(weights=None)
    in_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(in_features, 1)
    )
    state_dict = torch.load(weights_path, map_location=DEVICE)
    model.load_state_dict(state_dict)
    model.to(DEVICE)
    model.eval()
    return model


class GradCAM:
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        self._register_hooks()

    def _register_hooks(self):
        def forward_hook(module, inp, out):
            self.activations = out.detach()

        def backward_hook(module, grad_in, grad_out):
            self.gradients = grad_out[0].detach()

        self.target_layer.register_forward_hook(forward_hook)
        self.target_layer.register_full_backward_hook(backward_hook)

    def generate(self, input_tensor):
        self.model.zero_grad()
        output = self.model(input_tensor)
        prob = torch.sigmoid(output)[0, 0].item()

        output[0, 0].backward()
        weights = self.gradients.mean(dim=(2, 3), keepdim=True)
        cam = (weights * self.activations).sum(dim=1, keepdim=True)
        cam = torch.relu(cam).squeeze().cpu().numpy()

        if cam.max() > 0:
            cam = (cam - cam.min()) / (cam.max() - cam.min())
        return cam, prob


def apply_clahe_rgb(pil_img: Image.Image, clip_limit: float = 2.0, tile_grid_size=(8, 8)) -> Image.Image:
    rgb = np.array(pil_img.convert("RGB"))
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    l_ch, a_ch, b_ch = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    cl = clahe.apply(l_ch)
    merged = cv2.merge((cl, a_ch, b_ch))
    return Image.fromarray(cv2.cvtColor(merged, cv2.COLOR_LAB2RGB))


_preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])


def compute_three_way_breakdown(p_glaucoma: float):
    """
    يحسب:
    - احتمالية الجلوكوما (من الموديل)
    - احتمالية الحالة السليمة (1 - p_glaucoma)
    - مؤشر مراجعة / احتمالات أخرى: يرتفع عندما تكون النسبتان متقاربتين حول المنتصف (عدم حسم واضح)
    """
    p_normal_raw = 1.0 - p_glaucoma

    # درجة الغموض/التقارب: تكون أعلى ما يمكن عندما p_glaucoma قريبة من 0.50
    certainty = abs(p_glaucoma - 0.5) * 2.0  # من 0 (حيرة تامة) إلى 1 (حسم تام)
    ambiguity_weight = (1.0 - certainty) * 0.45  # أقصى وزن للمؤشر التالت عند الحيرة

    other_review = ambiguity_weight
    glaucoma_adj = p_glaucoma * (1.0 - ambiguity_weight)
    normal_adj = p_normal_raw * (1.0 - ambiguity_weight)

    total = glaucoma_adj + normal_adj + other_review
    return {
        "glaucoma_pct": (glaucoma_adj / total) * 100.0,
        "normal_pct": (normal_adj / total) * 100.0,
        "other_pct": (other_review / total) * 100.0,
    }


def run_real_inference(pil_img: Image.Image, threshold: float = THRESHOLD):
    model = load_glaucoma_model(WEIGHTS_PATH)
    grad_cam = GradCAM(model, model.layer4[-1])

    clahe_img = apply_clahe_rgb(pil_img)
    resized_clahe = np.array(clahe_img.resize((224, 224)))
    inp = _preprocess(clahe_img).unsqueeze(0).to(DEVICE)

    with torch.enable_grad():
        cam, prob = grad_cam.generate(inp)

    pred_label = 1 if prob >= threshold else 0
    heatmap = cv2.resize(cam, (224, 224))
    colored_cam = cv2.applyColorMap(np.uint8(255 * heatmap), cv2.COLORMAP_JET)
    colored_cam = cv2.cvtColor(colored_cam, cv2.COLOR_BGR2RGB)
    overlay = np.uint8(0.55 * resized_clahe + 0.45 * colored_cam)

    breakdown = compute_three_way_breakdown(prob)

    return {
        "pred_label": pred_label,
        "prob": float(prob),
        "clahe_img": Image.fromarray(resized_clahe),
        "overlay_img": Image.fromarray(overlay),
        "glaucoma_pct": breakdown["glaucoma_pct"],
        "normal_pct": breakdown["normal_pct"],
        "other_pct": breakdown["other_pct"],
    }


# -------------------------------------------------------------
# التنقل والواجهة
# -------------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "splash"

if st.session_state.page == "splash":
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #0d3b66;'>👁️ OrosVision AI</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #2e6930;'>رُؤيةٌ تَستَبِقُ الظَّلام</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #555;'>منصة الذكاء الاصطناعي التفسيري للفحص المبكر للجلوكوما</p>", unsafe_allow_html=True)

    _, col2, _ = st.columns([1, 1, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⚕️ الدخول إلى المنصة الطبية", use_container_width=True):
            st.session_state.page = "intake"
            st.rerun()
    st.stop()

st.title("🕯️ OrosVision AI: Clinical Intelligence Platform")
nav1, nav2, nav3, nav4 = st.columns(4)
with nav1:
    if st.button("١ـ بيانَات المريض 📝", use_container_width=True):
        st.session_state.page = "intake"
with nav2:
    if st.button("٢ـ الفحص الذّكي (AI) 🔍", use_container_width=True):
        st.session_state.page = "screening"
with nav3:
    if st.button("٣ـ المُتابعة الزمنِية 📈", use_container_width=True):
        st.session_state.page = "temporal"
with nav4:
    if st.button("٤ـ التوعِية الطبية 🔅", use_container_width=True):
        st.session_state.page = "awareness"

st.markdown("---")

if st.session_state.page == "intake":
    st.header("📝 التسجيل الإكلينيكي للمريض")
    with st.form("patient_intake_form"):
        col1, col2 = st.columns(2)
        with col1:
            p_name = st.text_input("اسم المريض / كود الملف *")
            p_age = st.number_input("العمر *", min_value=1, max_value=120, value=45)
        with col2:
            p_gender = st.selectbox("الجنس", ["ذكر", "أنثى"])
            p_phone = st.text_input("رقم للتواصل / ملاحظات")

        st.markdown("### 🧬 التاريخ المرضي وعوامل الخطورة:")
        c1, c2, c3 = st.columns(3)
        with c1:
            has_diabetes = st.checkbox("مرض السكري (Diabetes)")
        with c2:
            has_hypertension = st.checkbox("ارتفاع ضغط الدم (Hypertension)")
        with c3:
            has_family = st.checkbox("تاريخ عائلي للإصابة بالجلوكوما")

        eye_notes = st.text_area("الأدوية الحالية أو ملاحظات إكلينيكية (مثل: إنسولين، قطرات ضغط العين...)")

        if st.form_submit_button("حفظ والانتقال للفحص ➡️"):
            if not p_name.strip():
                st.error("❌ يرجى إدخال اسم المريض أو كود الملف أولاً.")
            else:
                st.session_state["patient_name"] = p_name.strip()
                st.session_state["has_diabetes"] = has_diabetes
                st.session_state["has_hypertension"] = has_hypertension
                st.session_state["has_family"] = has_family
                st.session_state["eye_notes"] = eye_notes.strip()
                st.session_state["intake_complete"] = True
                st.success("✅ تم حفظ البيانات بنجاح.")
                time.sleep(0.5)
                st.session_state.page = "screening"
                st.rerun()

elif st.session_state.page == "screening":
    st.header("🔍 الفحص اللحظي لقاع العين والتحليل التفسيري (Grad-CAM)")

    if not st.session_state.get("intake_complete", False):
        st.warning("⚠️ يرجى إدخال بيانات المريض أولاً في صفحة التسجيل.")
        if st.button("الانتقال لصفحة التسجيل ⬅️"):
            st.session_state.page = "intake"
            st.rerun()
    else:
        p_name = st.session_state.get("patient_name", "غير محدد")
        has_dia = st.session_state.get("has_diabetes", False)
        has_hyp = st.session_state.get("has_hypertension", False)
        has_fam = st.session_state.get("has_family", False)
        notes = st.session_state.get("eye_notes", "")

        risk_factors = []
        if has_dia or "سكري" in notes.lower() or "إنسولين" in notes.lower() or "انسولين" in notes.lower():
            risk_factors.append("السكري / أدوية السكري")
        if has_hyp:
            risk_factors.append("ارتفاع ضغط الدم")
        if has_fam:
            risk_factors.append("تاريخ عائلي للجلوكوما")

        st.markdown(
            f"**المريض:** {p_name} | **عوامل الخطورة المسجلة:** "
            f"{'، '.join(risk_factors) if risk_factors else 'لا يوجد عوامل خطورة مسجلة'}"
        )

        uploaded_file = st.file_uploader("ارفع صورة قاع العين (Fundus Image)...", type=["jpg", "jpeg", "png"])

        if uploaded_file is not None:
            raw_img = Image.open(uploaded_file).convert("RGB")
            try:
                with st.spinner("جاري تطبيق CLAHE وتشغيل ResNet18 وتوليد Grad-CAM..."):
                    out = run_real_inference(raw_img, threshold=THRESHOLD)

                col_a, col_b = st.columns(2)
                with col_a:
                    st.subheader("📷 الصورة بعد تحسين الإضاءة (CLAHE)")
                    st.image(out["clahe_img"], use_container_width=True)
                with col_b:
                    st.subheader("🧠 خريطة التركيز البصري (Grad-CAM)")
                    st.image(out["overlay_img"], use_container_width=True)

                st.markdown("---")
                m1, m2, m3 = st.columns(3)
                m1.metric("احتمالية جلوكوما (Glaucoma)", f"{out['glaucoma_pct']:.1f}%")
                m2.metric("احتمالية سليم (Normal)", f"{out['normal_pct']:.1f}%")
                m3.metric("احتمالية عدم حسم / مراجعة أو أسباب أخرى", f"{out['other_pct']:.1f}%")

                st.caption(
                    f"العتبة المعتمدة من Validation: {THRESHOLD:.2f} | "
                    f"احتمال الموديل الخام قبل التوزيع: {out['prob']:.4f}"
                )

                if out["pred_label"] == 1:
                    st.error(
                        "⚠️ **تنبيه فحص مبدئي:** نتيجة الموديل تتجاوز العتبة المعتمدة (0.42) وتشير لاشتباه جلوكوما. "
                        "يُنصح بمراجعة طبيب عيون مختص."
                    )
                elif out["other_pct"] >= 25.0:
                    st.warning(
                        "⚠️ **نتيجة غير حاسمة / تحتاج مراجعة:** النسبتان متقاربتان نسبياً، مما يرفع مؤشر المراجعة "
                        "أو احتمالية وجود تغيرات/أسباب بصرية أخرى تستدعي فحصاً متخصصاً."
                    )
                else:
                    st.success(
                        "✅ **نتيجة فحص مبدئي:** المؤشر يميل بوضوح نحو الحالة السليمة مع ضرورة المتابعة الدورية."
                    )

                if risk_factors:
                    st.info(
                        "📌 **ملاحظة من الملف الإكلينيكي:** تم تسجيل ("
                        + "، ".join(risk_factors)
                        + "). يُنصح بأخذ هذه العوامل في الاعتبار عند المتابعة الطبية."
                    )

            except FileNotFoundError:
                st.error(
                    f"❌ لم يتم العثور على ملف الأوزان: `{WEIGHTS_PATH}`. "
                    "ارفعي `best_glaucoma_clahe_finetuned.pth` بجانب `app.py`."
                )

elif st.session_state.page == "temporal":
    st.header("📈 المتابعة الزمنية (مقارنة صورتين)")
    col_old, col_new = st.columns(2)
    with col_old:
        old_file = st.file_uploader("صورة فحص سابقة", type=["jpg", "jpeg", "png"], key="temp_old")
        if old_file:
            st.image(apply_clahe_rgb(Image.open(old_file)), caption="الفحص السابق (بعد CLAHE)", use_container_width=True)
    with col_new:
        new_file = st.file_uploader("صورة فحص أحدث", type=["jpg", "jpeg", "png"], key="temp_new")
        if new_file:
            st.image(apply_clahe_rgb(Image.open(new_file)), caption="الفحص الأحدث (بعد CLAHE)", use_container_width=True)

elif st.session_state.page == "awareness":
    st.header("📚 التوعية الطبية حول الجلوكوما")
    st.markdown("""
    * **الجلوكوما (المياه الزرقاء):** تؤثر على العصب البصري وغالباً ترتبط بارتفاع ضغط العين، وقد تتطور دون أعراض واضحة في البداية.
    * **أهمية الفحص المبكر:** الكشف المبكر والمتابعة المنتظمة يساعدان في الحفاظ على الرؤية.
    * **التفسير البصري (`Grad-CAM`):** يوضح المناطق التي ركّز عليها النموذج لدعم شفافية الفحص.
    """)
