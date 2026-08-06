import matplotlib

matplotlib.use("Agg")  # Protection backend GUI

import random
import matplotlib.pyplot as plt
import networkx as nx
import streamlit as st

# --------------------------------------------------
# 1. Configuration de la page Streamlit
# --------------------------------------------------
st.set_page_config(
    page_title="Graph Inspection Game - 4 Modes",
    page_icon="🕵️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main-title { font-size: 2.2rem; font-weight: 800; color: #1E3A8A; text-align: center; }
    .sub-title { font-size: 1rem; color: #4B5563; text-align: center; margin-bottom: 20px; }
    .teacher-box { background-color: #EFF6FF; border-left: 5px solid #2563EB; padding: 15px; border-radius: 8px; margin-bottom: 15px; }
    
    /* Style du score très clair et lisible */
    .score-box-single { 
        background-color: #1E3A8A; 
        color: #FFFFFF; 
        border: 2px solid #3B82F6; 
        padding: 12px; 
        border-radius: 10px; 
        text-align: center; 
        font-weight: bold; 
        font-size: 1.2rem;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
    }
    .score-val {
        color: #FBBF24;
        font-size: 1.5rem;
        font-weight: 900;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-title">🕵️‍♂️ Graph Inspection Game</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-title">Plateforme Interactive & Pédagogique | MTYM 2026</div>',
    unsafe_allow_html=True,
)

# --------------------------------------------------
# 2. Gestion des États Globaux (Session State)
# --------------------------------------------------
if "score_inspector" not in st.session_state:
    st.session_state.score_inspector = 0

if "score_adversary" not in st.session_state:
    st.session_state.score_adversary = 0

if "last_result_msg" not in st.session_state:
    st.session_state.last_result_msg = None


def generate_graph(difficulty="Moyen"):
    G = nx.DiGraph()
    if difficulty == "Facile":
        edges = [("s", "a"), ("s", "b"), ("a", "t"), ("b", "t"), ("a", "b")]
        pos = {"s": (0, 0.5), "a": (1, 1.0), "b": (1, 0.0), "t": (2, 0.5)}
    elif difficulty == "Difficile":
        edges = [
            ("s", "a"),
            ("s", "b"),
            ("a", "c"),
            ("b", "d"),
            ("c", "d"),
            ("c", "t"),
            ("d", "t"),
            ("a", "d"),
        ]
        pos = {
            "s": (0, 0.5),
            "a": (1, 1.0),
            "b": (1, 0.0),
            "c": (2, 1.0),
            "d": (2, 0.0),
            "t": (3, 0.5),
        }
    else:  # Moyen
        edges = [
            ("s", "a"),
            ("s", "b"),
            ("a", "c"),
            ("b", "c"),
            ("a", "t"),
            ("b", "t"),
            ("c", "t"),
        ]
        pos = {
            "s": (0, 0.5),
            "a": (1, 1.0),
            "b": (1, 0.0),
            "c": (2, 0.5),
            "t": (3, 0.5),
        }

    G.add_edges_from(edges)
    edges_data = {}
    secret_costs = {}
    random.seed()

    for u, v in G.edges():
        le = round(random.uniform(1.0, 3.0), 1)
        ue = round(le + random.uniform(2.5, 6.0), 1)
        edges_data[(u, v)] = (le, ue)
        secret_costs[(u, v)] = round(random.uniform(le, ue), 2)

    st.session_state.G = G
    st.session_state.pos = pos
    st.session_state.edges_data = edges_data
    st.session_state.secret_costs = secret_costs
    st.session_state.inspected_edges = {}
    st.session_state.history_log = []
    st.session_state.adversary_locked = False
    st.session_state.game_over = False


if "G" not in st.session_state:
    generate_graph("Moyen")

# --------------------------------------------------
# 3. القائمة الجانبية: الأطوار الأربعة المستقلة
# --------------------------------------------------
st.sidebar.header("🎯 Sélection du Mode")

app_mode = st.sidebar.radio(
    "Choisissez le mode de fonctionnement :",
    [
        "👥 1. Mode Joueur vs Joueur",
        "🤖 2. Mode Challenge vs IA",
        "🛠️ 3. Concepteur de Réseau",
        "📖 4. Mode Explication & Solution (Professeurs)",
    ],
)

inspection_cost_unit = st.sidebar.slider(
    "💰 Coût d'une inspection (C_inspect) :",
    min_value=0.5,
    max_value=4.0,
    value=1.0,
    step=0.5,
)

st.sidebar.markdown("---")

# ==================================================
# MODE 1 : JOUEUR VS JOUEUR
# ==================================================
if app_mode == "👥 1. Mode Joueur vs Joueur":
    st.subheader("👥 Mode 2 Joueurs : Inspecteur vs Adversaire")

    if not st.session_state.adversary_locked:
        st.warning(
            "🦹 **Étape 1 : Tour de l'Adversaire.** Réglez les coûts secrets puis verrouillez."
        )
        with st.form("adv_form_m1"):
            new_sec = {}
            for e, (le, ue) in st.session_state.edges_data.items():
                new_sec[e] = st.slider(
                    f"Coût secret ({e[0]} → {e[1]}) [{le} - {ue}] :",
                    min_value=float(le),
                    max_value=float(ue),
                    value=float(st.session_state.secret_costs[e]),
                    step=0.1,
                )
            if st.form_submit_button("🔒 Verrouiller et Passer à l'Inspecteur"):
                st.session_state.secret_costs = new_sec
                st.session_state.adversary_locked = True
                st.session_state.last_result_msg = None
                st.rerun()
    else:
        st.info(
            "🕵️ **Étape 2 : Tour de l'Inspecteur.** Inspectez et choisissez votre chemin."
        )

# ==================================================
# MODE 2 : CHALLENGE VS IA
# ==================================================
elif app_mode == "🤖 2. Mode Challenge vs IA":
    st.subheader("🤖 Mode Challenge contre l'Intelligence Artificielle")

    diff_choice = st.selectbox(
        "📊 Niveau de difficulté de l'IA :",
        ["Facile", "Moyen", "Difficile"],
        index=1,
    )

    if st.button("🎲 Générer un nouveau défi IA"):
        generate_graph(diff_choice)
        st.session_state.adversary_locked = True
        st.session_state.last_result_msg = None
        st.rerun()

# ==================================================
# MODE 3 : CONCEPTEUR DE RÉSEAU
# ==================================================
elif app_mode == "🛠️ 3. Concepteur de Réseau":
    st.subheader("🛠️ Concepteur et Modélisateur de Réseau")
    st.info(
        "Modifiez manuellement les bornes [l_e, u_e] pour tester des topologies spécifiques."
    )

    with st.form("creator_form"):
        for e, (le, ue) in st.session_state.edges_data.items():
            c1, c2 = st.columns(2)
            n_l = c1.number_input(f"Borne inf ({e[0]}→{e[1]})", value=float(le), step=0.5)
            n_u = c2.number_input(f"Borne sup ({e[0]}→{e[1]})", value=float(ue), step=0.5)
            if n_l < n_u:
                st.session_state.edges_data[e] = (n_l, n_u)
        if st.form_submit_button("💾 Enregistrer la Structure"):
            st.success("Réseau mis à jour !")
            st.rerun()

# ==================================================
# MODE 4 : EXPLICATION & SOLUTION (POUR PROFESSEURS)
# ==================================================
elif app_mode == "📖 4. Mode Explication & Solution (Professeurs)":
    st.subheader("📖 Espace Pédagogique & Solution pour l'Évaluation")

    st.markdown("""
    <div class="teacher-card">
    <h4>🎓 Présentation du Problème Mathématique</h4>
    Ce projet modélise la prise de décision sous incertitude via le <b>Graph Inspection Game</b>.
    <ul>
    <li><b>Objectif :</b> Trouver le chemin optimal de $s$ à $t$ tout en minimisant les coûts d'inspection.</li>
    <li><b>Espérance de coût :</b> $\\mathbb{E}[c(e)] = \\frac{l_e + u_e}{2}$ pour les arêtes non révélées.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🔑 Solution Théorique en Temps Réel (Coûts Secrets) :")

    real_graph = nx.DiGraph()
    for e, c in st.session_state.secret_costs.items():
        real_graph.add_edge(e[0], e[1], weight=c)

    true_path = nx.shortest_path(real_graph, source="s", target="t", weight="weight")
    true_cost = nx.shortest_path_length(real_graph, source="s", target="t", weight="weight")

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.success(f"🏆 **Plus Court Chemin Réel :** `{' → '.join(true_path)}`")
    with col_s2:
        st.success(f"💰 **Coût Minimal Absolu :** `{true_cost:.2f}`")

    st.markdown("---")

# ==================================================
# AFFICHAGE DU GRAPHE ET DU PANNEAU (POUR MODES 1, 2, 3)
# ==================================================
if app_mode != "📖 4. Mode Explication & Solution (Professeurs)":

    # Message du résultat du niveau précédent (si disponible)
    if st.session_state.last_result_msg:
        if st.session_state.last_result_msg["type"] == "win":
            st.success(st.session_state.last_result_msg["text"])
            st.balloons()
        else:
            st.error(st.session_state.last_result_msg["text"])

    col_graph, col_panel = st.columns([3, 2])

    with col_graph:
        st.subheader("🗺️ Vision du Réseau")
        G = st.session_state.G
        pos = st.session_state.pos
        fig, ax = plt.subplots(figsize=(8, 5))

        nx.draw_networkx_nodes(G, pos, node_color="#2563EB", node_size=1200, ax=ax, edgecolors="black")
        nx.draw_networkx_labels(G, pos, font_size=12, font_weight="bold", font_color="white", ax=ax)
        nx.draw_networkx_edges(G, pos, width=2.0, edge_color="#6B7280", arrowsize=18, ax=ax)

        edge_labels = {}
        for edge, (le, ue) in st.session_state.edges_data.items():
            if edge in st.session_state.inspected_edges:
                edge_labels[edge] = f"✅ {st.session_state.inspected_edges[edge]}"
            else:
                edge_labels[edge] = f"[{le}, {ue}]"

        nx.draw_networkx_edge_labels(
            G, pos, edge_labels=edge_labels, font_size=9,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#9CA3AF"), ax=ax
        )
        plt.axis("off")
        st.pyplot(fig)

    with col_panel:
        # Affichage du Score
        if app_mode == "🤖 2. Mode Challenge vs IA":
            # Mode IA : Seul le score du Joueur est affiché avec les nouvelles couleurs
            st.markdown(
                f'<div class="score-box-single">🏆 Score Joueur : <span class="score-val">{st.session_state.score_inspector} pts</span></div>',
                unsafe_allow_html=True,
            )
        else:
            # Mode Joueur vs Joueur : Les deux scores sont affichés
            sc_col1, sc_col2 = st.columns(2)
            with sc_col1:
                st.markdown(
                    f'<div class="score-box-single">🕵️ Inspecteur<br><span class="score-val">{st.session_state.score_inspector} pts</span></div>',
                    unsafe_allow_html=True,
                )
            with sc_col2:
                st.markdown(
                    f'<div class="score-box-single">🦹 Adversaire<br><span class="score-val">{st.session_state.score_adversary} pts</span></div>',
                    unsafe_allow_html=True,
                )

        st.markdown("---")
        st.subheader("🕵️ Actions & Décisions")
        nb_ins = len(st.session_state.inspected_edges)
        c_tot_ins = nb_ins * inspection_cost_unit

        st.metric("Inspections effectuées", f"{nb_ins}")
        st.metric("Frais d'inspection", f"{c_tot_ins:.1f}")

        avail = [e for e in st.session_state.edges_data.keys() if e not in st.session_state.inspected_edges]
        if avail:
            e_sel = st.selectbox("Inspecter une arête :", options=avail, format_func=lambda x: f"({x[0]} → {x[1]}) [{st.session_state.edges_data[x]}]")
            if st.button("🔍 Lancer Inspection", type="primary", use_container_width=True):
                st.session_state.inspected_edges[e_sel] = st.session_state.secret_costs[e_sel]
                st.rerun()

        st.markdown("---")
        st.subheader("🏁 Choix du Chemin Final")
        all_p = list(nx.all_simple_paths(G, source="s", target="t"))
        p_str = [" → ".join(p) for p in all_p]
        c_p_str = st.selectbox("Sélectionner l'itinéraire :", options=p_str)
        c_p = all_p[p_str.index(c_p_str)]

        if st.button("🏁 Valider & Passer au Niveau Suivant", type="primary", use_container_width=True):
            r_cost = sum(st.session_state.secret_costs[(u, v)] for u, v in zip(c_p[:-1], c_p[1:]))
            tot_score = r_cost + c_tot_ins

            real_g = nx.DiGraph()
            for e, c in st.session_state.secret_costs.items():
                real_g.add_edge(e[0], e[1], weight=c)
            t_path = nx.shortest_path(real_g, source="s", target="t", weight="weight")
            t_cost = nx.shortest_path_length(real_g, source="s", target="t", weight="weight")

            gap = tot_score - t_cost
            max_possible_inspections = len(st.session_state.edges_data)

            gain_inspector = (max_possible_inspections - nb_ins) * 10
            gain_adversary = nb_ins * 10

            if gap <= 1.5:
                st.session_state.score_inspector += gain_inspector
                st.session_state.score_adversary = 0
                st.session_state.last_result_msg = {
                    "type": "win",
                    "text": f"🎉 Victoire de l'Inspecteur ! (+{gain_inspector} pts) | Total: {st.session_state.score_inspector} pts"
                }
            else:
                st.session_state.score_adversary += gain_adversary
                st.session_state.score_inspector = 0
                st.session_state.last_result_msg = {
                    "type": "loss",
                    "text": f"🦹 Victoire de l'Adversaire ! (+{gain_adversary} pts) | Total: {st.session_state.score_adversary} pts"
                }

            # Génération immédiate du niveau suivant
            generate_graph("Moyen")
            if app_mode == "🤖 2. Mode Challenge vs IA":
                st.session_state.adversary_locked = True
            st.rerun()

# --------------------------------------------------
# 4. Boutons de Réinitialisation Globale
# --------------------------------------------------
st.divider()
c_r1, c_r2 = st.columns(2)
with c_r1:
    if st.button("🎲 Régénérer la Carte (Conserver les Scores)", use_container_width=True):
        generate_graph("Moyen")
        if app_mode == "🤖 2. Mode Challenge vs IA":
            st.session_state.adversary_locked = True
        st.session_state.last_result_msg = None
        st.rerun()

with c_r2:
    if st.button("🔄 Réinitialiser Tout (Cartes + Scores à 0)", use_container_width=True):
        st.session_state.score_inspector = 0
        st.session_state.score_adversary = 0
        st.session_state.last_result_msg = None
        generate_graph("Moyen")
        st.rerun()
