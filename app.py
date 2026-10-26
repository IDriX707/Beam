import streamlit as st
import numpy as np
import plotly.graph_objects as go
import math

# ==========================================
# إعدادات الصفحة
# ==========================================
st.set_page_config(page_title="مثال المستند (Beam B1 & B2)", layout="wide")
st.title("🏗️ تطبيق المثال العملي (صفحة 65 - 71)")
st.write("هذا التطبيق يحاكي الحسابات اليدوية الموجودة في المستند للمخطط المرفق.")

# ==========================================
# 1. البيانات الأساسية (من صفحة 65)
# ==========================================
st.sidebar.header("📌 بيانات المثال")
Wus = st.sidebar.number_input("حمل البلاطة النهائي Wu_s (t/m²)", value=1.11, step=0.01)
O_Wt_B1 = st.sidebar.number_input("وزن الكمرة الذاتي B1 (t/m)", value=0.3125, step=0.01)
Wall_B1 = st.sidebar.number_input("حمل الحوائط B1 (t/m)", value=1.2, step=0.1)
O_Wt_B2 = st.sidebar.number_input("وزن الكمرة الذاتي B2 (t/m)", value=0.375, step=0.01)
Wall_B2 = st.sidebar.number_input("حمل الحوائط B2 (t/m)", value=1.2, step=0.1)

# الأحمال المركزة من الكمرات الثانوية
Point_Load_B2 = st.sidebar.number_input("الحمل المركز من B2 على B1 (t)", value=8.85, step=0.1)

# معاملات التوزيع (من صفحة 66)
st.sidebar.subheader("معاملات البلاطات (Ca & Ce)")
Ca_S1 = 0.67; Ce_S1 = 0.85 # Trapezoidal
Ca_S2 = 0.63; Ce_S2 = 0.81 # Trapezoidal
Ca_S3 = 0.582; Ce_S3 = 0.769 # Trapezoidal
Ca_S4 = 0.701; Ce_S4 = 0.881 # Trapezoidal

# ==========================================
# 2. حسابات الكمرة B1 (صفحة 68-69)
# ==========================================
st.header("1️⃣ تحليل الكمرة B1 (Edge Beam)")

# البحر الأول ab (4m) - يحمل من S1
Wa1_B1 = (Wus * (4/2) * (1/2)) + (1.4 * O_Wt_B1) + (1.4 * Wall_B1)
We1_B1 = (Wus * (4/2) * (2/3)) + (1.4 * O_Wt_B1) + (1.4 * Wall_B1)

# البحر الثاني bc (5m) - يحمل من S3
Wa2_B1 = (Wus * (5/2) * (1/2)) + (1.4 * O_Wt_B1) + (1.4 * Wall_B1)
We2_B1 = (Wus * (5/2) * (2/3)) + (1.4 * O_Wt_B1) + (1.4 * Wall_B1)

# البحر الثالث cd (1.5m) - كابولي (Cantilever)
Wa3_B1 = We3_B1 = (1.4 * O_Wt_B1) + (1.4 * Wall_B1)

col1, col2 = st.columns(2)
with col1:
    st.subheader("الأحمال المكافئة (Equivalent Loads)")
    st.write(f"**Part ab (4m):**")
    st.info(f"Wa1 = {Wa1_B1:.3f} t/m'  |  We1 = {We1_B1:.3f} t/m'")
    st.write(f"**Part bc (5m):**")
    st.info(f"Wa2 = {Wa2_B1:.3f} t/m'  |  We2 = {We2_B1:.3f} t/m'")
    st.write(f"**Part cd (1.5m Cantilever):**")
    st.info(f"Wa3 = We3 = {Wa3_B1:.3f} t/m'")

with col2:
    st.subheader("العزوم (Moment Values) - صفحة 69")
    # حساب العزوم التقريبية حسب المستند
    M_supp_G2 = max((We1_B1 * 4**2) / 9, (We2_B1 * 5**2) / 9) 
    M_pos_ab = (We1_B1 * 4**2) / 11
    M_pos_bc = (We2_B1 * 5**2) / 11
    M_cant = (Point_Load_B2 * 1.5) + (We3_B1 * 1.5**2 / 2) # عزم الكابولي عند G3
    
    st.success(f"أقصى عزم عند الركيزة الوسطى G2: **{M_supp_G2:.2f} m.t**")
    st.write(f"عزم موجب في البحر ab: {M_pos_ab:.2f} m.t")
    st.write(f"عزم موجب في البحر bc: {M_pos_bc:.2f} m.t")
    st.warning(f"عزم الكابولي عند G3 (بسبب الحمل المركز): **{M_cant:.2f} m.t**")

# رسم BMD للكمرة B1 (تقريبي ليتطابق مع الرسم)
x_b1 = np.linspace(0, 10.5, 500)
y_b1 = np.zeros_like(x_b1)
# شكل تقريبي للعزوم
y_b1[(x_b1 >= 0) & (x_b1 <= 4)] = -M_pos_ab * np.sin(np.pi * x_b1[(x_b1 >= 0) & (x_b1 <= 4)] / 4)
y_b1[(x_b1 > 4) & (x_b1 <= 9)] = -M_pos_bc * np.sin(np.pi * (x_b1[(x_b1 > 4) & (x_b1 <= 9)] - 4) / 5)
y_b1[(x_b1 > 9) & (x_b1 <= 10.5)] = -M_cant * (1 - (x_b1[(x_b1 > 9) & (x_b1 <= 10.5)] - 9)/1.5) # خطي للكابولي
y_b1[250] = M_supp_G2 # نقطة الركيزة

fig_b1 = go.Figure()
fig_b1.add_trace(go.Scatter(x=x_b1, y=y_b1, mode='lines', fill='tozeroy', name='BMD', line=dict(color='red', width=3)))
fig_b1.add_vline(x=4, line_dash="dash", line_color="green", annotation_text="G2")
fig_b1.add_vline(x=9, line_dash="dash", line_color="green", annotation_text="G3")
fig_b1.update_layout(title="B.M.D للكمرة B1 (مطابق لصفحة 69)", xaxis_title="Length (m)", yaxis_title="Moment (m.t)", template="plotly_white")
st.plotly_chart(fig_b1, use_container_width=True)


# ==========================================
# 3. حسابات الكمرة B2 (صفحة 70-71)
# ==========================================
st.header("2️⃣ تحليل الكمرة B2 (Internal Beam)")

# البحر الأول ab (4m) - يحمل من S1 (4m) و S2 (3m)
Wa1_B2 = (Wus * (4/2) * 0.5) + (Wus * (3/2) * Ca_S2) + (1.4 * O_Wt_B2) + (1.4 * Wall_B2)
We1_B2 = (Wus * (4/2) * (2/3)) + (Wus * (3/2) * Ce_S2) + (1.4 * O_Wt_B2) + (1.4 * Wall_B2)

# البحر الثاني bc (5m) - يحمل من S3 (5m) و S4 (3m)
Wa2_B2 = (Wus * (5/2) * 0.5) + (Wus * (3/2) * Ca_S4) + (1.4 * O_Wt_B2) + (1.4 * Wall_B2)
We2_B2 = (Wus * (4/2) * (2/3)) + (Wus * (3/2) * Ce_S4) + (1.4 * O_Wt_B2) + (1.4 * Wall_B2) # ملاحظة: صفحة 70 تستخدم 4m هنا بالخطأ أو لتبسيط، سنستخدم 5m للدقة
# تصحيح حسب المستند: We2 = 1.11*(5/2)*(2/3) + 1.11*(3/2)*0.769 + ...
We2_B2_corrected = (Wus * (5/2) * (2/3)) + (Wus * (3/2) * Ce_S4) + (1.4 * O_Wt_B2) + (1.4 * Wall_B2)

# البحر الثالث cd (1.5m) - كابولي
Wa3_B2 = We3_B2 = (1.4 * O_Wt_B2) + (1.4 * Wall_B2)

st.subheader("الأحمال المكافئة (Equivalent Loads) - صفحة 70")
st.info(f"**Part ab (4m):** Wa = {Wa1_B2:.3f} t/m' | We = {We1_B2:.3f} t/m'")
st.info(f"**Part bc (5m):** Wa = {Wa2_B2:.3f} t/m' | We = {We2_B2_corrected:.3f} t/m'")
st.info(f"**Part cd (1.5m):** Wa = We = {Wa3_B2:.3f} t/m'")

st.subheader("العزوم وقوى القص (صفحة 71)")
# Moments B2
M_supp_B2 = max((We1_B2 * 4**2)/9, (We2_B2_corrected * 5**2)/9)
M_pos_ab_B2 = (We1_B2 * 4**2)/11
M_pos_bc_B2 = (We2_B2_corrected * 5**2)/11
M_cant_B2 = (Point_Load_B2 * 1.5) + (We3_B2 * 1.5**2 / 2)

# Shears B2 (SFD)
Q1_B2 = 0.4 * Wa1_B2 * 4
Q2_B2 = 0.6 * Wa1_B2 * 4
Q3_B2 = 0.6 * Wa2_B2 * 5
Q4_B2 = 0.4 * Wa2_B2 * 5 + Point_Load_B2 # إضافة الحمل المركز على الكابولي

col3, col4 = st.columns(2)
with col3:
    st.success(f"عزم الركيزة G2: **{M_supp_B2:.2f} m.t**")
    st.write(f"عزم موجب ab: {M_pos_ab_B2:.2f} m.t")
    st.write(f"عزم موجب bc: {M_pos_bc_B2:.2f} m.t")
with col4:
    st.write(f"قص Q1 (يسار): {Q1_B2:.2f} t")
    st.write(f"قص Q2 (يمين G2): {Q2_B2:.2f} t")
    st.write(f"قص Q3 (يسار G3): {Q3_B2:.2f} t")
    st.warning(f"قص Q4 (كابولي): {Q4_B2:.2f} t")

# رسم SFD للكمرة B2
x_b2 = np.linspace(0, 10.5, 500)
y_b2 = np.zeros_like(x_b2)
y_b2[(x_b2 >= 0) & (x_b2 <= 4)] = np.linspace(Q1_B2, -Q2_B2, len(x_b2[(x_b2 >= 0) & (x_b2 <= 4)]))
y_b2[(x_b2 > 4) & (x_b2 <= 9)] = np.linspace(Q3_B2, -Q4_B2, len(x_b2[(x_b2 > 4) & (x_b2 <= 9)]))

fig_sfd = go.Figure()
fig_sfd.add_trace(go.Scatter(x=x_b2, y=y_b2, mode='lines', fill='tozeroy', name='SFD', line=dict(color='blue', width=3)))
fig_sfd.update_layout(title="S.F.D للكمرة B2 (مطابق لصفحة 71)", xaxis_title="Length (m)", yaxis_title="Shear (t)", template="plotly_white")
st.plotly_chart(fig_sfd, use_container_width=True)

# ==========================================
# 4. التصميم المبدئي
# ==========================================
st.header("3️⃣ التصميم المبدئي (Design)")
st.write("بناءً على أقصى عزم وقص تم حسابهما:")
Mu_design = max(M_supp_G2, M_cant, M_supp_B2) # أقصى عزم في النظام
Qu_design = max(Q4_B2, Q2_B2) # أقصى قص

st.write(f"أقصى عزم للتصميم **Mu = {Mu_design:.2f} m.t**")
st.write(f"أقصى قص للتصميم **Qu = {Qu_design:.2f} t**")

# حسابات تقريبية للحديد (بافتراض b=25cm, h=60cm, cover=4cm)
b = 25; h = 60; d = h - 4
fcu = 250; fy = 3600
C1 = 3.5; J = 0.8
As_req = (Mu_design * 100000) / (J * d * fy)
As_min = 0.0025 * b * d

st.info(f"مساحة الحديد المطلوبة للعزم: **{As_req:.2f} cm²**")
st.info(f"الحد الأدنى للحديد: **{As_min:.2f} cm²**")
if As_req > As_min:
    st.success("استخدم المساحة المطلوبة (As_req).")
else:
    st.warning("استخدم الحد الأدنى للحديد (As_min).")