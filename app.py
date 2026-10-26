import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# ==========================================
# 0. إعدادات الصفحة
# ==========================================
st.set_page_config(page_title="RC Slab & Beam Designer", layout="wide")
st.title("🏗️ النظام الشامل: تحليل وتوزيع الأحمال ورسم المخططات")
st.markdown("تطبيق كامل مبني على الكود المصري والمستند المرفق لتحليل البلاطات والكمرات.")

# ==========================================
# 1. المدخلات (Sidebar)
# ==========================================
st.sidebar.header("1. المواد والخصائص (Materials)")
fcu = st.sidebar.number_input("مقاومة الخرسانة Fcu (kg/cm²)", value=250)
fy = st.sidebar.number_input("مقاومة الحديد Fy (kg/cm²)", value=3600)
gamma_rc = st.sidebar.number_input("كثافة الخرسانة (t/m³)", value=2.5)
gamma_wall = st.sidebar.number_input("كثافة الجدار (t/m³)", value=1.8)

st.sidebar.header("2. الأحمال (Loads)")
t_s = st.sidebar.number_input("سماكة البلاطة t_s (cm)", value=12)
dl_sup = st.sidebar.number_input("أحمال التشطيبات (t/m²)", value=0.15)
ll = st.sidebar.number_input("الحمل الحي L.L (t/m²)", value=0.30)
gamma_d = st.sidebar.number_input("معامل التصعيد الميت (Dead Factor)", value=1.4)
gamma_l = st.sidebar.number_input("معامل التصعيد الحي (Live Factor)", value=1.6)

st.sidebar.header("3. الحوائط والكمرات")
t_w = st.sidebar.number_input("سماكة الجدار (m)", value=0.25)
h_w = st.sidebar.number_input("ارتفاع الجدار (m)", value=2.7)
b_beam = st.sidebar.number_input("عرض الكمرة b (cm)", value=25)
h_beam = st.sidebar.number_input("عمق الكمرة h (cm)", value=60)

# ==========================================
# 2. الحسابات الأساسية (Core Calculations)
# ==========================================
# وزن الحائط لكل متر طولي
wall_load_linear = t_w * h_w * gamma_wall

# وزن الكمرة الذاتي لكل متر طولي
beam_self_wt = (b_beam / 100) * (h_beam / 100) * gamma_rc

# حمل البلاطة النهائي (Wu)
slab_dead = (t_s / 100) * gamma_rc + dl_sup
Wu_s = (gamma_d * slab_dead) + (gamma_l * ll)

# المعاملات المضافة للكمرات (وزن ذاتي + حوائط)
beam_added_load = gamma_d * (beam_self_wt + wall_load_linear)

# ==========================================
# 3. تعريف هندسة المبنى (مأخوذة من الصورة المرفقة)
# ==========================================
# إحداثيات المحاور (X و Y) بالمتر
X_grid = [0, 6, 9, 10]
Y_grid = [0, 4, 9, 10.5] # من أعلى لأسفل

# تعريف البلاطات بناءً على الإحداثيات (x1, y1, x2, y2)
slabs_geom = {
    "S1": (0, 0, 6, 4),
    "S2": (6, 0, 9, 4),
    "S3": (0, 4, 6, 9),
    "S4": (6, 4, 9, 9),
    "S5": (9, 0, 10, 9),  # كابولي
    "S6": (0, 9, 6, 10.5) # كابولي
}

# دالة لحساب معاملات التوزيع (Ca & Ce) ص16-17
def get_distribution_coeffs(Lx, Ly):
    r = Ly / Lx
    if r >= 2.0:
        return 1.0, 1.0, "One-Way" # 1.0 تعني حمل خطي مباشر
    else:
        # معادلات تقريبية لمنحرف ومثلث
        Ca = 1 - (1 / (2 * r))
        Ce = (4 * r**2 - 1) / (6 * r**3)
        return Ca, Ce, "Two-Way"

# ==========================================
# 4. رسم المخطط وخطوط الأحمال (Yield Lines)
# ==========================================
st.header("📍 أولاً: مخطط البلاطات وتوزيع الأحمال (Yield Lines)")
fig_plan = go.Figure()

# رسم محاور الأعمدة
for x in X_grid:
    fig_plan.add_shape(type="line", x0=x, y0=0, x1=x, y1=Y_grid[-1], line=dict(color="gray", width=1, dash="dot"))
for y in Y_grid:
    fig_plan.add_shape(type="line", x0=0, y0=y, x1=X_grid[-1], y1=y, line=dict(color="gray", width=1, dash="dot"))

# رسم البلاطات وخطوط التوزيع
for name, (x1, y1, x2, y2) in slabs_geom.items():
    Lx = x2 - x1
    Ly = y2 - y1
    cx, cy = (x1+x2)/2, (y1+y2)/2
    
    # رسم حواف البلاطة
    fig_plan.add_shape(type="rect", x0=x1, y0=y1, x1=x2, y1=y2, line=dict(color="black", width=2))
    fig_plan.add_annotation(x=cx, y=cy, text=name, showarrow=False, font=dict(size=14, color="red"))
    
    # رسم خطوط التوزيع (Yield Lines) 45 درجة
    if Ly > Lx:
        # خطوط مائلة من الزوايا
        dist = Lx / 2
        fig_plan.add_trace(go.Scatter(x=[x1, x1+dist, x1], y=[y1, y1+dist, y2], mode="lines", line=dict(color="green", width=1.5), showlegend=False))
        fig_plan.add_trace(go.Scatter(x=[x2, x2-dist, x2], y=[y1, y1+dist, y2], mode="lines", line=dict(color="green", width=1.5), showlegend=False))
        fig_plan.add_trace(go.Scatter(x=[x1+dist, x2-dist], y=[y1+dist, y1+dist], mode="lines", line=dict(color="green", width=1.5), showlegend=False))
    else:
        dist = Ly / 2
        fig_plan.add_trace(go.Scatter(x=[x1, x1+dist, x2], y=[y1, y1+dist, y1], mode="lines", line=dict(color="green", width=1.5), showlegend=False))
        fig_plan.add_trace(go.Scatter(x=[x1, x1+dist, x2], y=[y2, y2-dist, y2], mode="lines", line=dict(color="green", width=1.5), showlegend=False))
        fig_plan.add_trace(go.Scatter(x=[x1+dist, x1+dist], y=[y1+dist, y2-dist], mode="lines", line=dict(color="green", width=1.5), showlegend=False))

# رسم الأعمدة
for x in X_grid:
    for y in Y_grid:
        if (x,y) != (X_grid[-1], Y_grid[-1]): # استبعاد الزاوية
            fig_plan.add_trace(go.Scatter(x=[x], y=[y], mode="markers", marker=dict(symbol="square", size=12, color="black"), showlegend=False))

fig_plan.update_layout(title="مخطط البلاطات وخطوط توزيع الأحمال", xaxis_title="X (m)", yaxis_title="Y (m)", 
                       yaxis=dict(autorange="reversed"), template="plotly_white", height=500, margin=dict(l=20, r=20, t=40, b=20))
st.plotly_chart(fig_plan, use_container_width=True)

# ==========================================
# 5. حسابات أحمال الكمرات (مطابقة للمستند ص 68-71)
# ==========================================
st.header("📊 ثانياً: الأحمال على الكمرات")
beams_data = {
    "B1 (Edge - X=0)": {"type": "continuous", "spans": [4, 5, 1.5], "loads_Wa": [], "loads_We": []},
    "B2 (Internal - X=6)": {"type": "continuous", "spans": [4, 5, 1.5], "loads_Wa": [], "loads_We": []},
    "B3 (Edge - X=9)": {"type": "continuous", "spans": [4, 5, 1.5], "loads_Wa": [], "loads_We": []}
}

# توزيع أحمال S1 و S2 على B1 (في المستند S1 و S2 لهما نفس التحميل تقريباً)
# S1 (6x4) -> Two-way (Ca=0.67, Ce=0.85)
Ca1, Ce1, _ = get_distribution_coeffs(6, 4)
Wa_S1 = (Wu_s * 4 / 2) * Ca1 # التحليل في اتجاه البحر الأصغر
We_S1 = (Wu_s * 4 / 2) * Ce1

# S3 (6x5) -> Two-way (Ca=0.58, Ce=0.77)
Ca3, Ce3, _ = get_distribution_coeffs(6, 5)
Wa_S3 = (Wu_s * 5 / 2) * Ca3
We_S3 = (Wu_s * 5 / 2) * Ce3

# إضافة أحمال الكمرة B1 (البحر الأول يحمل من S1، الثاني من S3)
beams_data["B1 (Edge - X=0)"]["loads_Wa"] = [Wa_S1 + beam_added_load, Wa_S3 + beam_added_load, beam_added_load]
beams_data["B1 (Edge - X=0)"]["loads_We"] = [We_S1 + beam_added_load, We_S3 + beam_added_load, beam_added_load]

# عرض جدول الأحمال
data_table = []
for b_name, b_info in beams_data.items():
    for i, (L, Wa, We) in enumerate(zip(b_info["spans"], b_info["loads_Wa"], b_info["loads_We"])):
        data_table.append({"Beam": b_name, "Span (m)": L, "Wa (t/m)": round(Wa, 3), "We (t/m)": round(We, 3)})

st.table(pd.DataFrame(data_table))

# ==========================================
# 6. التحليل الإنشائي ورسم المخططات (BMD & SFD)
# ==========================================
st.header("📈 ثالثاً: تحليل الكمرات (BMD & SFD)")

selected_beam = st.selectbox("اختر الكمرة لعرض مخططاتها:", list(beams_data.keys()))
b_info = beams_data[selected_beam]

# حساب العزوم والقص (التحليل التقريبي للكمرات المستمرة)
# بناءً على ص31 وص33 من المستند
spans = b_info["spans"]
Wes = b_info["loads_We"]
Was = b_info["loads_Wa"]

# حساب العزوم (تقريبي)
M_supports = []
M_spans = []

for i in range(len(spans)):
    # عزم الركيزة الوسطى (إذا كان هناك بحر تالي)
    if i < len(spans) - 1:
        M_sup = max((Wes[i] * spans[i]**2) / 9, (Wes[i+1] * spans[i+1]**2) / 9)
        M_supports.append(M_sup)
    else:
        M_supports.append(0) # الكابولي أو النهاية
        
    # عزم منتصف البحر
    if i == 0:
        M_pos = (Wes[i] * spans[i]**2) / 11
    else:
        M_pos = (Wes[i] * spans[i]**2) / 11
    M_spans.append(M_pos)

# حساب القص (بناءً على ص33)
Q_maxs = []
for i in range(len(spans)):
    q_left = 0.4 * Was[i] * spans[i] if i == 0 else 0.6 * Was[i-1] * spans[i-1]
    q_right = 0.6 * Was[i] * spans[i]
    Q_maxs.append(max(q_left, q_right))

# رسم BMD
x_coords = []
y_moments = []

current_x = 0
for i in range(len(spans)):
    L = spans[i]
    W = Wes[i]
    
    # إحداثيات البحر
    x_span = np.linspace(current_x, current_x + L, 50)
    x_coords.extend(x_span)
    
    # معادلة القطع المكافئ التقريبية
    if i == 0:
        y_span = M_supports[i] * ((x_span - current_x) / L)**2 - M_spans[i] * 4 * ((x_span - current_x) / L) * (1 - (x_span - current_x) / L)
    else:
        y_span = M_supports[i-1] * (1 - (x_span - current_x) / L)**2 - M_spans[i] * 4 * ((x_span - current_x) / L) * (1 - (x_span - current_x) / L)
    
    # الكابولي
    if i == len(spans) - 1 and L == 1.5:
        y_span = - (W * (x_span - current_x)**2) / 2 - M_supports[i-1] * ((x_span - current_x) / L) 
        
    y_moments.extend(y_span)
    current_x += L

fig_bmd = go.Figure()
fig_bmd.add_trace(go.Scatter(x=x_coords, y=y_moments, mode="lines", fill="tozeroy", line=dict(color="red", width=3), name="BMD"))
fig_bmd.update_layout(title=f"Bending Moment Diagram (BMD) for {selected_beam}", xaxis_title="Distance (m)", yaxis_title="Moment (t.m)", template="plotly_white", height=400)
st.plotly_chart(fig_bmd, use_container_width=True)

# رسم SFD
fig_sfd = go.Figure()
current_x = 0
for i in range(len(spans)):
    L = spans[i]
    Q_left = 0.4 * Was[i] * L if i == 0 else 0.6 * Was[i-1] * spans[i-1]
    Q_right = 0.6 * Was[i] * L
    
    fig_sfd.add_trace(go.Scatter(x=[current_x, current_x + L], y=[Q_left, -Q_right], mode="lines", line=dict(color="blue", width=3), showlegend=False))
    current_x += L

fig_sfd.update_layout(title=f"Shear Force Diagram (SFD) for {selected_beam}", xaxis_title="Distance (m)", yaxis_title="Shear (t)", template="plotly_white", height=400)
st.plotly_chart(fig_sfd, use_container_width=True)

# ==========================================
# 7. التصميم المبدئي
# ==========================================
st.header("🛠️ رابعاً: التصميم المبدئي (Flexural & Shear)")
Mu_max = max(M_spans + M_supports)
Qu_max = max(Q_maxs)

d = h_beam - 5
Mu_kgcm = Mu_max * 100000
As_req = Mu_kgcm / (0.8 * d * fy)
As_min = 0.0025 * b_beam * d

col1, col2, col3 = st.columns(3)
col1.metric("أقصى عزم (t.m)", f"{Mu_max:.2f}")
col2.metric("أقصى قص (t)", f"{Qu_max:.2f}")
col3.metric("مساحة الحديد (cm²)", f"{max(As_req, As_min):.2f}")

if As_req > As_min:
    st.success(f"التصميم آمن. مساحة الحديد المطلوبة {As_req:.2f} cm²")
else:
    st.info(f"استخدم الحد الأدنى للحديد {As_min:.2f} cm²")
