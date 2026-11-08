import os
import json
import time
import threading
import streamlit as st
from pypdf import PdfReader
import google.generativeai as genai

# 1. إعدادات الصفحة والتصميم الداكن الفخم
st.set_page_config(
    page_title="منصة ذكاء | ZokaAI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تصميم وتنسيق عصري مريح للعين مع بنرات الرعاية والتقييم
st.markdown("""
    <style>
    body, .main, .stMarkdown, p, div {
        font-family: 'Cairo', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .main {
        background-color: #0b0f19;
        color: #f3f4f6;
    }
    .stSidebar {
        background-color: #111827;
        direction: rtl;
        text-align: right;
    }
    h1, h2, h3 {
        color: #ffffff;
    }
    .stButton button {
        background: linear-gradient(135deg, #6366f1 0%, #3b82f6 100%);
        color: white;
        font-weight: bold;
        border-radius: 10px;
        border: none;
        padding: 0.6rem 1.4rem;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #4f46e5 0%, #2563eb 100%);
        box-shadow: 0 6px 15px rgba(59, 130, 246, 0.5);
        transform: translateY(-1px);
    }
    .dhikr-box {
        background-color: #161e2e;
        border: 1px solid #3b82f6;
        padding: 16px;
        border-radius: 12px;
        text-align: center;
        color: #60a5fa;
        font-size: 20px;
        font-weight: bold;
        margin-top: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
    }
    .styled-result-container {
        background-color: #161b22;
        padding: 35px;
        border-radius: 16px;
        border: 1px solid #30363d;
        color: #e6edf3;
        direction: rtl;
        text-align: right;
        font-size: 19px;
        line-height: 2.2;
    }
    .eng-card {
        background-color: #1e293b;
        border-left: 5px solid #38bdf8;
        padding: 20px;
        border-radius: 12px;
        direction: ltr;
        text-align: left;
        font-family: 'Segoe UI', Tahoma, Geneva, sans-serif;
        font-size: 19px;
        color: #38bdf8;
        font-weight: 600;
        margin-top: 18px;
        line-height: 1.8;
    }
    .ara-card {
        background-color: #0f172a;
        border-right: 5px solid #6366f1;
        padding: 20px;
        border-radius: 12px;
        direction: rtl;
        text-align: right;
        font-size: 19px;
        color: #f3f4f6;
        margin-top: 8px;
        margin-bottom: 22px;
        line-height: 2.1;
    }
    .alert-card {
        background-color: rgba(239, 68, 68, 0.1);
        border: 2px solid #ef4444;
        border-right: 8px solid #ef4444;
        padding: 20px;
        border-radius: 12px;
        direction: rtl;
        text-align: right;
        font-size: 19px;
        color: #fca5a5;
        font-weight: bold;
        margin-top: 18px;
        margin-bottom: 22px;
        line-height: 2.0;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.2);
    }
    .section-title {
        color: #60a5fa;
        font-size: 23px;
        font-weight: bold;
        border-bottom: 2px solid #1e3a8a;
        padding-bottom: 10px;
        margin-top: 35px;
        margin-bottom: 18px;
        direction: rtl;
        text-align: right;
    }
    .exam-question-card {
        background-color: #111827;
        border: 1px solid #374151;
        border-right: 6px solid #6366f1;
        padding: 24px;
        border-radius: 14px;
        margin-bottom: 25px;
        direction: ltr;
        text-align: left;
    }
    .hero-container {
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
        padding: 40px;
        border-radius: 20px;
        border: 1px solid #374151;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    }
    .hero-title {
        font-size: 38px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 15px;
    }
    .hero-subtitle {
        font-size: 20px;
        color: #9ca3af;
        margin-bottom: 25px;
        line-height: 1.8;
    }
    .feature-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 14px;
        text-align: center;
        margin-bottom: 20px;
        height: 100%;
    }
    .ad-banner-box {
        background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%);
        border: 1px dashed #6366f1;
        padding: 24px;
        border-radius: 16px;
        text-align: center;
        color: #c7d2fe;
        margin-top: 25px;
        margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

API_KEY = "AQ.Ab8RN6LCwss_COb_5rL2FZilZN9CJxIdriKZp8bVh5yB-EaqYw"

if API_KEY:
    genai.configure(api_key=API_KEY)

USERS_FILE = "users_db.json"
FEEDBACK_FILE = "feedback_db.json"
SPONSOR_FILE = "sponsor_db.json"
ADMIN_EMAIL = "admin@zoka.com"

BAD_WORDS = ["قذر", "لعنة", "وسخ", "شتم", "تبا"]

def contains_bad_word(text):
    for word in BAD_WORDS:
        if word in text:
            return True
    return False

def get_user_ip():
    try:
        headers = st.context.headers
        if "X-Forwarded-For" in headers:
            return headers["X-Forwarded-For"].split(",")[0]
        return headers.get("Host", "local_device")
    except Exception:
        return "default_device_ip"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return {}
    default_users = {
        ADMIN_EMAIL: {
            "name": "إبراهيم (المالك)",
            "password": "admin123",
            "pdf_count": 0,
            "is_admin": True,
            "device_ip": "admin_ip"
        }
    }
    save_users(default_users)
    return default_users

def save_users(users_data):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users_data, f, ensure_ascii=False, indent=4)

def load_feedback():
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_feedback(feedback_list):
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(feedback_list, f, ensure_ascii=False, indent=4)

def load_sponsors():
    if os.path.exists(SPONSOR_FILE):
        with open(SPONSOR_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_sponsors(sponsor_list):
    with open(SPONSOR_FILE, "w", encoding="utf-8") as f:
        json.dump(sponsor_list, f, ensure_ascii=False, indent=4)

def get_working_models():
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        flash_models = [m for m in available_models if 'flash' in m]
        pro_models = [m for m in available_models if 'pro' in m]
        return flash_models + pro_models + available_models
    except Exception:
        return ['models/gemini-1.5-flash', 'models/gemini-1.5-pro']

def format_stacked_cards(raw_text):
    lines = raw_text.split('\n')
    html_output = "<div class='styled-result-container'>"
    
    current_eng = ""
    
    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
            
        clean_line = line_str.replace("###", "").replace("**", "").replace("#", "").replace("$", "").strip()
        if not clean_line:
            continue
            
        clean_line = clean_line.replace("ENG:", "").replace("ARA:", "").replace("EG", "").replace("GB", "").strip()
        if not clean_line:
            continue
            
        if "ALERT:" in clean_line or "تنبيه خطير:" in clean_line or "⚠️" in clean_line:
            alert_text = clean_line.replace("ALERT:", "").replace("تنبيه خطير:", "").strip()
            html_output += f"<div class='alert-card'>🚨 تنبيه امتحان هام جداً: {alert_text}</div>"
        elif any(clean_line.startswith(x) for x in ["📌", "🔑", "🚀", "💡", "1.", "2.", "3.", "4.", "5."]) and len(clean_line) < 50:
            html_output += f"<div class='section-title'>{clean_line}</div>"
        else:
            if all(ord(c) < 128 for c in clean_line if c.isalpha()) and len(clean_line) > 10:
                current_eng = clean_line
            else:
                if current_eng:
                    html_output += f"<div class='eng-card'>🇬🇧 {current_eng}</div>"
                    current_eng = ""
                html_output += f"<div class='ara-card'>🇪🇬 {clean_line}</div>"
                
    html_output += "</div>"
    return html_output

def generate_ai_analysis(pdf_text, task_type, num_q):
    shortened_text = pdf_text[:8500]

    prompt = f"""
    You are an expert AI academic mentor for university students preparing for English exams.
    Analyze the text from the PDF and output the content strictly in pairs:
    1. First, output the exact original English technical sentence or paragraph as it appears in the PDF text (for exam preparation).
    2. Second, output the clear, friendly, and simplified Egyptian Arabic translation and explanation.
    
    CRITICAL RULES FOR MATH AND PHYSICS PROBLEMS:
    - If there are math or physics problems, formulas, or equations, explain thoroughly: where it came from, the core idea, the physical/mathematical rule used, and solve it step-by-step in a very simple Egyptian Arabic style.
    - DO NOT use LaTeX formatting or dollar signs ($). Write mathematical functions, powers, and expressions plainly (e.g., f(x) or 10^2).
    - Do NOT include prefixes like "ENG:" or "ARA:". Just write the text clearly.
    - For critical exam traps, start the line with "ALERT: [Important exam warning in Arabic]" so it gets highlighted in red.
    - Include {num_q} targeted exam questions at the end with answers.

    Task Type: {task_type}
    PDF Text:
    {shortened_text}
    """

    working_models = get_working_models()
    for model_name in working_models:
        try:
            model = genai.GenerativeModel(model_name)
            res = model.generate_content(prompt)
            if res and res.text:
                return res.text, None
        except Exception:
            continue
    return None, "فشل الاتصال بنماذج الذكاء الاصطناعي."

def generate_structured_exam(pdf_text, exam_type):
    num_mcq = 13 if exam_type == "Midterm (15 Questions - 60 Mins)" else 36
    num_essay = 2 if exam_type == "Midterm (15 Questions - 60 Mins)" else 4
    
    prompt = f"""
    You are an official university professor creating a technical exam in JSON format based on the provided text.
    You must output ONLY valid JSON matching this exact structure, with no markdown code blocks outside, or valid parseable JSON.
    
    Structure:
    {{
      "mcq": [
        {{
          "id": 1,
          "question": "Question text in English?",
          "options": ["Option A text", "Option B text", "Option C text", "Option D text"],
          "answer": "Option A text"
        }}
      ],
      "essay": [
        {{
          "id": 1,
          "question": "Essay question text in English?",
          "model_answer": "Expected detailed answer"
        }}
      ]
    }}
    
    Generate {num_mcq} MCQ questions and {num_essay} Essay questions entirely in English based on the text.

    PDF Text:
    {pdf_text[:9000]}
    """

    working_models = get_working_models()
    for model_name in working_models:
        try:
            model = genai.GenerativeModel(model_name)
            res = model.generate_content(prompt)
            if res and res.text:
                clean_json_str = res.text.replace("```json", "").replace("```", "").strip()
                exam_data = json.loads(clean_json_str)
                return exam_data, None
        except Exception:
            continue
    return None, "فشل توليد الامتحان المنظم."

# --- القائمة الجانبية (Sidebar) ---
st.sidebar.markdown("## 🎓 منصة **ذكاء (ZokaAI)**")
st.sidebar.markdown("---")

users_db = load_users()
current_ip = get_user_ip()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.user_name = ""

if not st.session_state.logged_in:
    auth_tab1, auth_tab2 = st.sidebar.tabs(["🔑 تسجيل الدخول", "📝 حساب جديد"])
    
    with auth_tab1:
        login_email = st.text_input("البريد الإلكتروني:", key="l_email")
        login_pass = st.text_input("كلمة المرور:", type="password", key="l_pass")
        if st.button("دخول المنصة"):
            if login_email in users_db and users_db[login_email]["password"] == login_pass:
                st.session_state.logged_in = True
                st.session_state.user_email = login_email
                st.session_state.user_name = users_db[login_email]["name"]
                st.sidebar.success("تم تسجيل الدخول بنجاح!")
                st.rerun()
            else:
                st.error("البريد أو كلمة المرور غير صحيحة.")
                
    with auth_tab2:
        reg_name = st.text_input("اسم المستخدم:", key="r_name")
        reg_email = st.text_input("البريد الإلكتروني:", key="r_email")
        reg_pass = st.text_input("كلمة المرور:", type="password", key="r_pass")
        
        accounts_from_this_device = sum(1 for u in users_db.values() if u.get("device_ip") == current_ip and not u.get("is_admin", False))
        
        if st.button("إنشاء الحساب الآن"):
            if reg_email and reg_pass and reg_name:
                if reg_email in users_db:
                    st.warning("هذا البريد مسجل مسبقاً.")
                elif accounts_from_this_device >= 2:
                    st.error("🚫 عذراً! تم الوصول للحد الأقصى لإنشاء الحسابات المجانية من هذا الجهاز (حسابين فقط).")
                else:
                    users_db[reg_email] = {
                        "name": reg_name,
                        "password": reg_pass,
                        "pdf_count": 0,
                        "is_admin": False,
                        "device_ip": current_ip,
                        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                    save_users(users_db)
                    st.success("تم إنشاء الحساب بنجاح! يمكنك تسجيل الدخول الآن.")
            else:
                st.warning("يرجى ملء جميع الحقول المطلوبة.")
else:
    st.sidebar.markdown(f"### 👋 أهلاً بك، **{st.session_state.user_name}**")
    st.sidebar.markdown(f"📧 `{st.session_state.user_email}`")
    
    current_user_data = users_db.get(st.session_state.user_email, {"pdf_count": 0})
    st.sidebar.success("🎁 الباقة: مجانية بالكامل بلا حدود 🚀")
    st.sidebar.info(f"📊 إجمالي ملفاتك المعالجة: **{current_user_data.get('pdf_count', 0)}** ملف")
    
    if st.session_state.user_email == ADMIN_EMAIL or users_db.get(st.session_state.user_email, {}).get("is_admin", False):
        st.sidebar.markdown("👑 **الصفة:** مدير المنصة (Admin)")
    
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.user_name = ""
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ خيارات التحليل المخصصة")
analysis_mode = st.sidebar.selectbox(
    "اختر نوع الخدمة المطلوبة:",
    [
        "🚀 تحليل شامل وكامل (الكل)",
        "📄 ملخص فقط",
        "❓ أسئلة واختبارات فقط",
        "🔑 كلمات مفتاحية ومصطلحات",
        "💡 ملاحظات وإرشادات"
    ]
)
num_questions = st.sidebar.slider("عدد أسئلة الاختبار:", min_value=5, max_value=30, value=10, step=5)

# --- الواجهة الرئيسية الاحترافية للموقع (Landing Page) ---
if not st.session_state.logged_in:
    st.markdown("""
        <div class="hero-container">
            <div class="hero-title">🎓 منصة ذكاء | ZokaAI</div>
            <div class="hero-subtitle">رفيقك الأكاديمي الخارق لطلاب الجامعات المصرية والعربية.<br>مجاناً 100% وبدون حدود لملفات الـ PDF، الشرح التفصيلي للمسائل، وقاعة الامتحانات الرسمية!</div>
        </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""
            <div class="feature-box">
                <h3>⚡ تحليل ثنائي اللغة</h3>
                <p style="color: #9ca3af; font-size: 15px;">نص إنجليزي أصلي للامتحانات + ترجمة وشرح بالعامية المصرية البسيطة.</p>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
            <div class="feature-box">
                <h3>🧮 شرح المسائل</h3>
                <p style="color: #9ca3af; font-size: 15px;">خطوات تفصيلية للرياضيات والفيزياء من الصفر حتى الفهم التام.</p>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
            <div class="feature-box">
                <h3>📝 قاعة الامتحانات</h3>
                <p style="color: #9ca3af; font-size: 15px;">اختبارات ميد تيرم وفاينل تفاعلية مع تصحيح فوري وتقييم ذكي.</p>
            </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown("""
            <div class="feature-box">
                <h3>🎁 مفتوح للجميع</h3>
                <p style="color: #9ca3af; font-size: 15px;">استخدام لا محدود للملفات والامتحانات لدعم كافة الطلاب.</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # المساحة الإعلانية المجهزة للمستقبل مع نموذج التواصل للرعاية
    st.markdown("""
        <div class="ad-banner-box">
            <h3>📢 هل ترغب في حجز مساحة إعلانية أو تقديم رعاية للمنصة؟</h3>
            <p style="color: #93c5fd; font-size: 16px;">وصل منشأتك التعليمية أو خدماتك للآلاف من طلاب الجامعات يومياً عبر منصة ZokaAI.</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.expander("🤝 اضغط هنا للتواصل معنا وحجز رعاية / إعلان"):
        sponsor_name = st.text_input("اسم الجهة / السنتر / الشركة:", key="sp_name")
        sponsor_contact = st.text_input("رقم الهاتف أو البريد للتواصل:", key="sp_contact")
        sponsor_msg = st.text_area("تفاصيل طلب الرعاية أو الإعلان:", key="sp_msg", height=100)
        
        if st.button("📩 إرسال طلب الرعاية للمالك"):
            if sponsor_name and sponsor_contact and sponsor_msg:
                sponsors = load_sponsors()
                sponsors.append({
                    "name": sponsor_name,
                    "contact": sponsor_contact,
                    "message": sponsor_msg,
                    "date": time.strftime("%Y-%m-%d %H:%M:%S")
                })
                save_sponsors(sponsors)
                st.success("تم إرسال طلبك بنجاح! سيتواصل معك مالك المنصة في أقرب وقت.")
            else:
                st.warning("يرجى ملء جميع الحقول المطلوبة.")

    st.markdown("<br>", unsafe_allow_html=True)
    total_users_count = len(users_db)
    total_files_processed = sum(u.get("pdf_count", 0) for u in users_db.values())
    
    st.markdown(f"""
        <div style="background-color: #111827; padding: 25px; border-radius: 16px; text-align: center; border: 1px solid #374151;">
            <h3 style="color: #60a5fa; margin-bottom: 10px;">📊 إحصائيات منصة ذكاء الحية</h3>
            <p style="font-size: 18px; color: #e6edf3;">تم تسجيل <b>{total_users_count}</b> طالباً واستخدام المنصة في معالجة وتحليل <b>{total_files_processed}</b> ملف محاضرة حتى الآن بنجاح تام! 🚀</p>
        </div>
    """, unsafe_allow_html=True)

else:
    st.title("📚 نظام ذكاء لتحليل المحاضرات وملفات الـ PDF")
    st.markdown("ملخصات ذكية ثنائية اللغة، شرح تفصيلي للمسائل، وقاعة امتحانات رسمية تفاعلية ومنظمة!")
    st.markdown("---")
    
    is_admin = (st.session_state.user_email == ADMIN_EMAIL or users_db.get(st.session_state.user_email, {}).get("is_admin", False))
    
    if is_admin:
        tab_main, tab_exam, tab_feedback, tab_admin = st.tabs(["🚀 تحليلات الـ PDF", "📝 قاعة الامتحانات الرسمية", "💡 التقييم واقتراح التطوير", "👑 لوحة تحكم المالك"])
    else:
        tab_main, tab_exam, tab_feedback = st.tabs(["🚀 تحليلات الـ PDF", "📝 قاعة الامتحانات الرسمية", "💡 التقييم واقتراح التطوير"])

    with tab_main:
        uploaded_file = st.file_uploader("📂 اختر ملف PDF للمحاضرة أو المذكرة للتحليل:", type=["pdf"])

        if uploaded_file is not None:
            with st.spinner("📄 جاري قراءة الملف وتنسيق النصوص بمسافات مريحة للشرح..."):
                try:
                    reader = PdfReader(uploaded_file)
                    text = ""
                    for page in reader.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text += extracted + "\n"
                    
                    if not text.strip():
                        st.error("عذراً، لم نتمكن من قراءة نص واضح من هذا الملف.")
                    else:
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            st.metric(label="📊 عدد الصفحات", value=len(reader.pages))
                        with c2:
                            st.metric(label="📝 حالة الملف", value="جاهز للتحليل الفوري ✅")
                        with c3:
                            st.metric(label="🎯 الخدمة المختارة", value=analysis_mode)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        if st.button("🚀 ابدأ التحليل الفائق وشرح المسائل بالتفصيل", use_container_width=True):
                            
                            dhikr_list = [
                                "✨ صلِّ على الحبيب محمد ﷺ",
                                "🌿 سبحان الله وبحمده، سبحان الله العظيم",
                                "💚 استغفر الله العظيم وأتوب إليه",
                                "🌸 لا إله إلا الله وحدَهُ لا شريك له",
                                "🤲 الحمد لله حمداً كثيراً طيباً مباركاً فيه",
                                "⭐ حسبي الله لا إله إلا هو عليه توكلت",
                                "💡 لا حول ولا قوة إلا بالله العلي العظيم"
                            ]
                            
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            dhikr_placeholder = st.empty()
                            
                            result_holder = {"text": None, "error": None}
                            
                            def run_ai():
                                res, err = generate_ai_analysis(text, analysis_mode, num_questions)
                                result_holder["text"] = res
                                result_holder["error"] = err

                            ai_thread = threading.Thread(target=run_ai)
                            ai_thread.start()
                            
                            progress_val = 5
                            start_time = time.time()
                            
                            while ai_thread.is_alive():
                                elapsed_sec = int(time.time() - start_time)
                                dhikr_idx = (elapsed_sec // 2) % len(dhikr_list)
                                
                                if progress_val < 95:
                                    progress_val += 5
                                
                                progress_bar.progress(progress_val)
                                status_text.markdown(f"**⏳ جاري تحليل المسائل وشرح الخطوات بوضوح... ({progress_val}%)**")
                                
                                dhikr_placeholder.markdown(f"""
                                    <div class='dhikr-box'>
                                        {dhikr_list[dhikr_idx]}
                                    </div>
                                """, unsafe_allow_html=True)
                                
                                time.sleep(0.12)
                            
                            progress_bar.progress(100)
                            status_text.markdown("**✨ تم الانتهاء بنجاح! 100%**")
                            dhikr_placeholder.empty()
                            
                            result_text = result_holder["text"]
                            error_details = result_holder["error"]
                            
                            if result_text:
                                if st.session_state.user_email in users_db:
                                    users_db[st.session_state.user_email]["pdf_count"] = users_db[st.session_state.user_email].get("pdf_count", 0) + 1
                                    save_users(users_db)
                                
                                st.success("⚡ تم إنجاز التحليل وشرح المسائل الرياضية بوضوح تام!")
                                st.markdown("---")
                                
                                st.markdown(f"## 📋 نتائج التحليل: {analysis_mode}")
                                
                                formatted_html = format_stacked_cards(result_text)
                                st.markdown(formatted_html, unsafe_allow_html=True)
                                
                                st.markdown("<br>", unsafe_allow_html=True)
                                
                                st.download_button(
                                    label="📥 تحميل التقرير كملف نصي (TXT)",
                                    data=result_text,
                                    file_name="ZokaAI_Detailed_Report.txt",
                                    mime="text/plain",
                                    use_container_width=True
                                )
                            else:
                                st.error(f"❌ حدث خطأ أثناء الاتصال بالنموذج: {error_details}")
                except Exception as e:
                    st.error(f"حدث خطأ أثناء معالجة الملف: {e}")

    with tab_exam:
        st.subheader("📝 قاعة الامتحانات التفاعلية المنظمة")
        st.markdown("كل سؤال في كارت مستقل، اختار الإجابة بضغطة زر، واكتب إجابات المقالي في المربعات المخصصة تحتها تماماً!")
        
        exam_pdf = st.file_uploader("📂 اختر ملف الـ PDF الخاص بالامتحان:", type=["pdf"], key="exam_file_upload_new")
        exam_type_choice = st.selectbox("اختر نموذج الامتحان:", ["Midterm (15 Questions - 60 Mins)", "Final Exam (40 Questions - 120 Mins)"], key="exam_type_select")
        
        if exam_pdf is not None:
            if st.button("🚀 تجهيز أسئلة الامتحان التفاعلي", use_container_width=True):
                with st.spinner("⏳ جاري صياغة أسئلة الاختياري والمقالي من الملف..."):
                    reader = PdfReader(exam_pdf)
                    exam_text = ""
                    for p in reader.pages:
                        if p.extract_text():
                            exam_text += p.extract_text() + "\n"
                    
                    exam_json, err = generate_structured_exam(exam_text, exam_type_choice)
                    if exam_json:
                        st.session_state['active_exam_json'] = exam_json
                        st.success("🎯 تم فتح الامتحان بنجاح! جاوب براحتك في الكروت أدناه.")
                        st.rerun()
                    else:
                        st.error(f"❌ خطأ: {err}")
        
        if 'active_exam_json' in st.session_state:
            st.markdown("---")
            st.markdown("### ⏱️ ورقة الامتحان التفاعلية")
            
            exam_data = st.session_state['active_exam_json']
            student_choices = {}
            student_essays = {}
            
            st.markdown("#### أولاً: أسئلة الاختيار من متعدد (MCQ)")
            for item in exam_data.get("mcq", []):
                q_id = item["id"]
                st.markdown(f"""
                <div class='exam-question-card'>
                    <div style="color: #60a5fa; font-weight: bold; margin-bottom: 8px;">Question {q_id}</div>
                    <div style="color: #f3f4f6; font-size: 18px; margin-bottom: 12px;">{item['question']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                choice = st.radio(
                    f"اختر الإجابة للسؤال {q_id}:",
                    item['options'],
                    key=f"mcq_{q_id}",
                    label_visibility="collapsed"
                )
                student_choices[q_id] = {"question": item['question'], "selected": choice, "correct": item['answer']}
                st.markdown("<br>", unsafe_allow_html=True)
            
            st.markdown("#### ثانياً: الأسئلة المقالية (Essay Questions)")
            for item in exam_data.get("essay", []):
                e_id = item["id"]
                st.markdown(f"""
                <div class='exam-question-card' style="border-right-color: #38bdf8;">
                    <div style="color: #38bdf8; font-weight: bold; margin-bottom: 8px;">Essay Question {e_id}</div>
                    <div style="color: #f3f4f6; font-size: 18px; margin-bottom: 12px;">{item['question']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                essay_ans = st.text_area(
                    f"اكتب إجابتك المقالية للسؤال {e_id} هنا:",
                    key=f"essay_{e_id}",
                    height=120,
                    placeholder="اكتب إجابتك بالتفصيل هنا..."
                )
                student_essays[e_id] = {"question": item['question'], "student_answer": essay_ans, "model_answer": item['model_answer']}
                st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("📤 تسليم الامتحان وتصحيحه فوراً", use_container_width=True):
                with st.spinner("🔍 جاري مراجعة إجابات الاختياري والمقالي بدقة..."):
                    mcq_total = len(exam_data.get("mcq", []))
                    mcq_score = 0
                    mcq_report = ""
                    
                    for q_id, data in student_choices.items():
                        is_correct = (data["selected"].strip().lower() == data["correct"].strip().lower())
                        if is_correct:
                            mcq_score += 1
                            mcq_report += f"- Question {q_id}: صحيح ✅ (اختيارك: {data['selected']})\n"
                        else:
                            mcq_report += f"- Question {q_id}: خطأ ❌ (اختيارك: {data['selected']} | الإجابة الصحيحة: {data['correct']})\n"
                    
                    essay_prompt = f"""
                    Grade the student's essay answers comparing them with the model answers.
                    
                    Data:
                    {json.dumps(student_essays, ensure_ascii=False)}
                    
                    Provide brief constructive feedback and evaluation for each essay question in friendly Egyptian Arabic.
                    """
                    
                    working_models = get_working_models()
                    essay_feedback = ""
                    for m_name in working_models:
                        try:
                            m = genai.GenerativeModel(m_name)
                            r = m.generate_content(essay_prompt)
                            if r and r.text:
                                essay_feedback = r.text
                                break
                        except:
                            continue
                    
                    st.markdown("---")
                    st.markdown("### 🏆 نتيجة الامتحان والتقييم النهائي:")
                    st.markdown(f"""
                    <div class='styled-result-container'>
                        <h3>📊 درجة أسئلة الاختيار من متعدد: {mcq_score} / {mcq_total}</h3>
                        <hr style="border-color: #30363d;">
                        <h4>📋 تفاصيل تقييم الاختياري:</h4>
                        <pre style="color: #e6edf3; font-family: inherit; white-space: pre-wrap;">{mcq_report}</pre>
                        <hr style="border-color: #30363d;">
                        <h4>📝 تقييم الأسئلة المقالية:</h4>
                        <p>{essay_feedback}</p>
                    </div>
                    """, unsafe_allow_html=True)

    with tab_feedback:
        st.subheader("💡 تقييم المنصة واقتراحات التطوير المستقبلية")
        st.markdown("رأيك وملاحظاتك هي المحرك الأساسي لتطوير ZokaAI لتكون المنصة الأولى في مصر والعالم العربي! 🚀")
        
        rating = st.select_slider("⭐️ ما هو تقييمك للمنصة حتى الآن؟", options=["⭐️", "⭐️⭐️", "⭐️⭐️⭐️", "⭐️⭐️⭐️⭐️", "⭐️⭐️⭐️⭐️⭐️"], value="⭐️⭐️⭐️⭐️⭐️")
        feature_request = st.text_input("✨ ما هي الميزات والخدمات الجديدة التي تتمنى إضافتها في التحديثات القادمة؟")
        user_msg = st.text_area("📝 انطباعك ورأيك العام لتطوير التجربة:", height=120, key="feedback_box_main")
        
        if st.button("📩 إرسال التقييم والاقتراحات للمطورين", key="send_feedback_btn"):
            if user_msg.strip() or feature_request.strip():
                if contains_bad_word(user_msg) or contains_bad_word(feature_request):
                    st.error("🚫 عذراً، الرسالة تحتوي على كلمات غير مسموح بها. يرجى الالتزام بالآداب العامة.")
                else:
                    feedbacks = load_feedback()
                    feedbacks.append({
                        "user_name": st.session_state.user_name,
                        "user_email": st.session_state.user_email,
                        "rating": rating,
                        "needed_features": feature_request,
                        "message": user_msg,
                        "date": time.strftime("%Y-%m-%d %H:%M:%S")
                    })
                    save_feedback(feedbacks)
                    st.success("شكراً لك من القلب! تم إرسال تقييمك واقتراحاتك لإدارة المنصة بنجاح. ❤️")
            else:
                st.warning("يرجى كتابة ملاحظة أو اقتراح قبل الإرسال.")

    if is_admin:
        with tab_admin:
            st.subheader("👑 لوحة تحكم مالك المنصة وإحصائيات الاستخدام")
            st.markdown("---")
            
            total_users = len(users_db)
            total_pdfs = sum(u.get("pdf_count", 0) for u in users_db.values())
            all_feedbacks = load_feedback()
            all_sponsors = load_sponsors()
            
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                st.metric(label="👥 إجمالي المستخدمين المسجلين", value=total_users)
            with col_b:
                st.metric(label="📄 إجمالي ملفات الـ PDF المعالجة", value=total_pdfs)
            with col_c:
                st.metric(label="💡 اقتراحات الطلاب المستلمة", value=len(all_feedbacks))
            with col_d:
                st.metric(label="🤝 طلبات الرعاية والإعلانات", value=len(all_sponsors))
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.markdown("### 🤝 طلبات الرعاية والإعلانات المستلمة")
            if all_sponsors:
                for sp in reversed(all_sponsors):
                    st.markdown(f"""
                    <div style="background-color: #1e1b4b; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-right: 5px solid #6366f1; text-align: right;">
                        <p style="margin:0; font-weight:bold; color: #38bdf8;">🏢 الجهة: {sp['name']} | 📞 التواصل: {sp['contact']} - <span style="color:#9ca3af; font-size:12px;">{sp['date']}</span></p>
                        <p style="margin-top:8px; color: #f3f4f6;">تفاصيل الطلب: {sp['message']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("لا توجد طلبات رعاية حتى الآن.")

            st.markdown("---")
            st.markdown("### 📋 قائمة المسجلين والأجهزة")
            user_table_data = []
            for email, details in users_db.items():
                user_table_data.append({
                    "اسم المستخدم": details.get("name", "غير معروف"),
                    "البريد الإلكتروني": email,
                    "معرف الجهاز/IP": details.get("device_ip", "غير محدد"),
                    "تاريخ التسجيل": details.get("created_at", "قديم"),
                    "عدد الـ PDFs المعالجة": details.get("pdf_count", 0),
                    "نوع الحساب": "مدير 👑" if details.get("is_admin", False) else "مستخدم مجاني 👤"
                })
            st.table(user_table_data)
            
            st.markdown("---")
            st.markdown("### 💡 تقييمات الطلاب واقتراحات التطوير المستلمة")
            if all_feedbacks:
                for fb in reversed(all_feedbacks):
                    st.markdown(f"""
                    <div style="background-color: #1f2937; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-right: 4px solid #3b82f6; text-align: right;">
                        <p style="margin:0; font-weight:bold; color: #60a5fa;">👤 {fb['user_name']} ({fb['user_email']}) | التقييم: {fb.get('rating', '⭐️⭐️⭐️⭐️⭐️')} - <span style="color:#9ca3af; font-size:12px;">{fb['date']}</span></p>
                        <p style="margin-top:5px; color: #38bdf8;">✨ ميزات يطلبها: {fb.get('needed_features', 'لا يوجد')}</p>
                        <p style="margin-top:5px; color: #f3f4f6;">الرسالة: {fb['message']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("لا توجد تقييمات أو اقتراحات مرسلة حتى الآن.")