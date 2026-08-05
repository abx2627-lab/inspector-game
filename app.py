import matplotlib

matplotlib.use("Agg")

import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import random
import scipy.optimize as opt

# ---------------------------------------------------------
# 1. إعدادات الصفحة والواجهة
# ---------------------------------------------------------
st.set_page_config(page_title="لعبة المفتش - Graph Inspection Game", layout="wide")

st.title("🕵️‍♂️ لعبة المفتش (The Inspector's Game)")
st.caption("محاكاة تفاعلية لمسألة MTYM 2026 - نظريات البيانيات وعلم الألعاب")

# ---------------------------------------------------------
# 2. بناء البياني المأخوذ من مثال المسألة
# ---------------------------------------------------------
@st.cache_data
def build_sample_graph():
    G = nx.Graph()
    # إضافة الأضلاع مع مجالات التكلفة ]ℓe, ue[
    edges_data = [
        ('s', 'a', 1.0, 3.0),
        ('a', 't', 1.0, 3.0),
        ('s', 't', 1.0, 5.0),
        ('s', 'b', 4.0, 6.0),
        ('b', 't', 4.0, 6.0)
    ]
    for u, v, l, u_val in edges_data:
        G.add_edge(u, v, l=l, u=u_val)
    return G

G = build_sample_graph()

# مواضع العقد للرسم المرئي (Layout)
pos = {
    's': (0, 0),
    'a': (1, 1),
    'b': (1, -1),
    't': (2, 0)
}

# ---------------------------------------------------------
# 3. إدارة حالة اللعبة (Session State)
# ---------------------------------------------------------
if 'secret_costs' not in st.session_state:
    st.session_state.secret_costs = {}
    st.session_state.game_generated = False

# ---------------------------------------------------------
# 4. القائمة الجانبية (Sidebar) - تحكم اللعبة
# ---------------------------------------------------------
st.sidebar.header("⚙️ لوحة التحكم")

if st.sidebar.button("🎲 توليد تكاليف سرية جديدة (دور الخصم)"):
    # الخصم يختار تكاليف سرية داخل المجالات
    st.session_state.secret_costs = {
        (u, v): round(random.uniform(d['l'], d['u']), 2) 
        for u, v, d in G.edges(data=True)
    }
    st.session_state.game_generated = True
    st.sidebar.success("تم اختيار التكاليف السرية بنجاح!")

st.sidebar.subheader("🔍 دور المفتش")
selected_edges = []
st.sidebar.write("اختر الأضلاع التي تريد لمعاينتها $D$:")

for u, v in G.edges():
    edge_label = f"الضلع ({u} ➔ {v}) - المجال: ]{G[u][v]['l']}, {G[u][v]['u']}"
    if st.sidebar.checkbox(edge_label, key=f"edge_{u}_{v}"):
        selected_edges.append((u, v))

# ---------------------------------------------------------
# 5. عرض الرسم البياني التفاعلي
# ---------------------------------------------------------
col1, col2 = st.columns([1.2, 0.8])

with col1:
    st.subheader("🕸️ شبكة الطرق والمجالات")
    fig, ax = plt.subplots(figsize=(7, 5))
    
    # ألوان الأضلاع: حمراء للمعاينة D، سوداء للعادية
    edge_colors = []
    edge_widths = []
    for u, v in G.edges():
        if (u, v) in selected_edges or (v, u) in selected_edges:
            edge_colors.append('#E74C3C')  # أحمر للأضلاع المفحوصة D
            edge_widths.append(4)
        else:
            edge_colors.append('#7F8C8D')
            edge_widths.append(2)
            
    # رسم العقد والأضلاع
    nx.draw_networkx_nodes(G, pos, node_color='#2ECC71', node_size=1200, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=14, font_weight='bold', font_color='white', ax=ax)
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=edge_widths, ax=ax)
    
    # وضع تسميات المجالات فوق الأضلاع
    edge_labels = {}
    for u, v, d in G.edges(data=True):
        if st.session_state.game_generated and ((u, v) in selected_edges or (v, u) in selected_edges):
            # كشف التكلفة السرية للضلع إذا عاينه المفتش
            c_val = st.session_state.secret_costs.get((u, v), st.session_state.secret_costs.get((v, u)))
            edge_labels[(u, v)] = f"]{d['l']}, {d['u']}[\n★ c={c_val}"
        else:
            edge_labels[(u, v)] = f"]{d['l']}, {d['u']}["
            
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10, ax=ax)
    
    plt.axis('off')
    st.pyplot(fig)

# ---------------------------------------------------------
# 6. قسم النتائج وتقييم المفتش
# ---------------------------------------------------------
with col2:
    st.subheader("📊 لوحة التحليل والتخمين")
    
    if not st.session_state.game_generated:
        st.warning("⚠️ اضغط على زر 'توليد تكاليف سرية جديدة' لبدء جولة جديدة!")
    else:
        st.info("🔓 الأضلاع باللون الأحمر تم كشف قيمها السرية للمفتش.")
        
        # جميع المسارات الممكنة من s إلى t
        all_paths = list(nx.all_simple_paths(G, source='s', target='t'))
        
        # حساب التكاليف الحقيقية لكل مسار
        path_costs = {}
        for path in all_paths:
            cost = 0
            for i in range(len(path)-1):
                u, v = path[i], path[i+1]
                c_val = st.session_state.secret_costs.get((u, v), st.session_state.secret_costs.get((v, u)))
                cost += c_val
            path_costs[" ➔ ".join(path)] = round(cost, 2)
            
        true_shortest_path = min(path_costs, key=path_costs.get)
        
        st.write("---")
        st.write("🎯 **اختيار المفتش للمسار:**")
        chosen_path = st.selectbox("بناءً على التكاليف المكشوفة، أي مسار تخمن أنه الأقصر؟", list(path_costs.keys()))
        
        if st.button("🏆 التحقق من النتيجة (Verify)"):
            st.write("---")
            st.write("### 📜 التكاليف الحقيقية للمسارات (عند الخصم):")
            for p_name, p_cost in path_costs.items():
                if p_name == true_shortest_path:
                    st.success(f"**{p_name}**: {p_cost} (أقصر مسار حقيقي ✨)")
                else:
                    st.write(f"**{p_name}**: {p_cost}")
                    
            if chosen_path == true_shortest_path:
                st.balloons()
                st.success("🎉 **إجابة صحيحة!** نجح المفتش في تحديد أقصر مسار!")
            else:
                st.error("❌ **إجابة خاطئة!** لقد خُدع المفتش بسبب نقص المعلومات في $D$.")
