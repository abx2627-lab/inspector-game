import matplotlib

matplotlib.use("Agg")  # لمنع أخطاء واجهة الرسم على الخوادم السحابية

import random
import matplotlib.pyplot as plt
import networkx as nx
import streamlit as st

# --------------------------------------------------
# 1. إعدادات الصفحة
# --------------------------------------------------
st.set_page_config(
    page_title="لعبة المفتش - Graph Inspection Game", layout="wide"
)

st.title("🕵️‍♂️ لعبة المفتش (The Inspector's Game)")
st.caption("محاكاة تفاعلية وتوليد مراحل عشوائية | MTYM 2026")

# --------------------------------------------------
# 2. إدارة حالة الجلسة (Session State)
# --------------------------------------------------


def generate_new_level():
    """توليد مرحلة جديدة بعقد وأضلاع وتكاليف عشوائية"""
    num_nodes = random.randint(4, 7)
    # إنشاء رسم بياني عشوائي متصل
    G = nx.erdos_renyi_graph(n=num_nodes, p=0.6, seed=random.randint(1, 10000))

    # التأكد من أن الرسم البياني متصل (Connected)
    while not nx.is_connected(G):
        G = nx.erdos_renyi_graph(
            n=num_nodes, p=0.6, seed=random.randint(1, 10000)
        )

    # إعادة تسمية العقد لتصبح s (البداية) و t (النهاية) وباقي الحروف
    mapping = {0: "s", num_nodes - 1: "t"}
    alphabet = "abcdefghijklmn"
    idx = 0
    for node in G.nodes():
        if node not in mapping:
            mapping[node] = alphabet[idx]
            idx += 1
    G = nx.relabel_nodes(G, mapping)

    # توليد مجالات تكلفة وتكاليف سرية عشوائية لكل ضلع
    edges_data = {}
    secret_costs = {}
    for u, v in G.edges():
        le = round(random.uniform(1.0, 3.0), 1)
        ue = round(le + random.uniform(1.5, 4.0), 1)
        edges_data[(u, v)] = (le, ue)
        secret_costs[(u, v)] = round(random.uniform(le, ue), 2)

    st.session_state.G = G
    st.session_state.edges_data = edges_data
    st.session_state.secret_costs = secret_costs
    st.session_state.inspected_edges = {}
    st.session_state.game_over = False
    st.session_state.attempts = 0


# تهيئة المرحلة لأول مرة إن لم تكن موجودة
if "G" not in st.session_state:
    generate_new_level()

# --------------------------------------------------
# 3. شريط التحكم والأزرار الرئيسية
# --------------------------------------------------
col_ctrl1, col_ctrl2 = st.columns(2)

with col_ctrl1:
    if st.button("🎲 مرحلة عشوائية جديدة", use_container_width=True):
        generate_new_level()
        st.rerun()

with col_ctrl2:
    if st.button("🔄 إعادة المحاولة (نفس المرحلة)", use_container_width=True):
        st.session_state.inspected_edges = {}
        st.session_state.game_over = False
        st.session_state.attempts = 0
        st.rerun()

st.divider()

# --------------------------------------------------
# 4. عرض الرسم البياني والتفاعلات
# --------------------------------------------------
col_graph, col_actions = st.columns([3, 2])

with col_graph:
    st.subheader("🗺️ خريطة الشبكة الحالية")

    G = st.session_state.G
    fig, ax = plt.subplots(figsize=(6, 4))
    pos = nx.spring_layout(G, seed=42)

    # رسم العقد والأضلع
    nx.draw_networkx_nodes(
        G, pos, node_color="skyblue", node_size=700, ax=ax
    )
    nx.draw_networkx_labels(
        G, pos, font_size=12, font_family="sans-serif", ax=ax
    )
    nx.draw_networkx_edges(G, pos, width=2, edge_color="gray", ax=ax)

    # كتابة مجالات التكلفة على الأضلع
    labels = {}
    for edge, (le, ue) in st.session_state.edges_data.items():
        if edge in st.session_state.inspected_edges:
            labels[edge] = f"Cost: {st.session_state.inspected_edges[edge]}"
        else:
            labels[edge] = f"[{le}, {ue}]"

    nx.draw_networkx_edge_labels(
        G, pos, edge_labels=labels, font_size=9, ax=ax
    )
    plt.axis("off")
    st.pyplot(fig)

with col_actions:
    st.subheader("🔍 خيارات التفتيش (Inspection)")

    edge_list = list(st.session_state.edges_data.keys())
    selected_edge = st.selectbox(
        "اختر الضلع المراد كشف تكلفته السرية:",
        options=edge_list,
        format_func=lambda x: f"الضلع ({x[0]} ↔ {x[1]})",
    )

    if st.button("فحص الضلع 🕵️"):
        cost = st.session_state.secret_costs[selected_edge]
        st.session_state.inspected_edges[selected_edge] = cost
        st.session_state.attempts += 1
        st.success(
            f"تم كشف التكلفة السرية للضلع {selected_edge}: **{cost}**"
        )
        st.rerun()

    st.write(f"**عدد محاولات الفحص:** {st.session_state.attempts}")

    if st.session_state.inspected_edges:
        st.markdown("### 📋 التكاليف المكتشفة:")
        for edge, val in st.session_state.inspected_edges.items():
            st.write(f"- الضلع **{edge}**: التكلفة = `{val}`")
