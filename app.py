import matplotlib

matplotlib.use("Agg")  # Protection backend GUI

import math
import random
import matplotlib.pyplot as plt
import networkx as nx
import streamlit as st

# --------------------------------------------------
# 1. Configuration de la page Streamlit
# --------------------------------------------------
st.set_page_config(
    page_title="Graph Inspection Game - 25 Unique Setups",
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

if "current_setup_num" not in st.session_state:
    st.session_state.current_setup_num = 1


def generate_setup_graph(setup_number=1):
    """
    Génère 25 structures de graphes TOTALEMENT DISTINCTES.
    """
    G = nx.DiGraph()
    random.seed(setup_number * 12345)

    # 1. Nombre de nœuds intermédiaires
    num_intermediate = 2 + (setup_number % 5) + (setup_number // 9)
    intermediate_nodes = [
        chr(97 + i) for i in range(num_intermediate)
    ]  # ['a', 'b', ...]

    # 2. Placement spatial (positions) dynamique unique par setup
    pos = {"s": (0.0, 0.5), "t": (3.0, 0.5)}

    num_layers = 1 + (setup_number % 3)
    nodes_per_layer = math.ceil(num_intermediate / num_layers)

    for idx, node in enumerate(intermediate_nodes):
        layer_idx = (idx // nodes_per_layer) + 1
        x = round(layer_idx * (2.4 / (num_layers + 1)), 2)

        pos_in_layer = idx % nodes_per_layer
        y = round(
            1.2 - (pos_in_layer * (2.4 / max(1, nodes_per_layer - 1 + 0.1))), 2
        )
        if nodes_per_layer == 1:
            y = 0.5
        pos[node] = (x, y)

    # 3. Création des arêtes
    edges = []

    first_layer_nodes = [
        n
        for n in intermediate_nodes
        if pos[n][0] == min(pos[m][0] for m in intermediate_nodes)
    ]
    for n in first_layer_nodes:
        edges.append(("s", n))

    last_layer_nodes = [
        n
        for n in intermediate_nodes
        if pos[n][0] == max(pos[m][0] for m in intermediate_nodes)
    ]
    for n in last_layer_nodes:
        edges.append((n, "t"))

    for i, u in enumerate(intermediate_nodes):
        for j, v in enumerate(intermediate_nodes):
            if pos[u][0] < pos[v][0]:
                if (i + j + setup_number) % 2 == 0:
                    edges.append((u, v))

    if not edges:
        edges = [("s", "a"), ("a", "t")]

    edges = list(set(edges))
    G.add_edges_from(edges)

    edges_data = {}
    secret_costs = {}

    for u, v in G.edges():
        le = round(random.uniform(1.0, 3.0), 1)
        ue = round(le + random.uniform(2.0, 6.0), 1)
        edges_data[(u, v)] = (le, ue)
        secret_costs[(u, v)] = round(random.uniform(le, ue), 2)

    st.session_state.G = G
    st.session_state.pos = pos
    st.session_state.edges_data = edges_data
    st.session_state.secret_costs = secret_costs
    st.session_state.inspected_edges = {}
    st.session_state.history_log = []
    st.session_state.adversary_locked = True
    st.session_state.game_over = False
    st.session_state.current_setup_num = setup_number


if "G" not in st.session_state:
    generate_setup_graph(1)

# --------------------------------------------------
# Fonction Générique d'Affichage du Graphe avec Flèches
# --------------------------------------------------
def render_graph_plot(highlight_path=None, show_secrets=False):
    G = st.session_state.G
    pos = st.session_state.pos
    fig, ax = plt.subplots(figsize=(8, 5))

    # Convertir le chemin sous forme d'arêtes à surligner
    path_edges = []
    if highlight_path and len(highlight_path) > 1:
        path_edges = list(zip(highlight_path[:-1], highlight_path[1:]))

    # Arêtes normales vs Arêtes du chemin optimal
    normal_edges = [e for e in G.edges() if e not in path_edges]

    # Nœuds
    nx.draw_networkx_nodes(
        G, pos, node_color="#2563EB", node_size=1200, ax=ax, edgecolors="black"
    )
    nx.draw_networkx_labels(
        G,
        pos,
        font_size=12,
        font_weight="bold",
        font_color="white",
        ax=ax,
    )

    # Arêtes standards avec flèches
    nx.draw_networkx_edges(
        G,
        pos,
        edgelist=normal_edges,
        width=2.0,
        edge_color="#6B7280",
        arrowstyle="-|>",
        arrowsize=20,
        ax=ax,
    )

    # Arêtes du chemin optimal en surbrillance (Flèches rouges/oranges)
    if path_edges:
        nx.draw_networkx_edges(
            G,
            pos,
            edgelist=path_edges,
            width=4.0,
            edge_color="#DC2626",
            arrowstyle="-|>",
            arrowsize=25,
            ax=ax,
        )

    # Étiquettes sur les arêtes
    edge_labels = {}
    for edge, (le, ue) in st.session_state.edges_data.items():
        if show_secrets:
            sec = st.session_state.secret_costs[edge]
            edge_labels[edge] = f"🔑 {sec}\n[{le}, {ue}]"
        elif edge in st.session_state.inspected_edges:
            edge_labels[edge] = f"✅ {st.session_state.inspected_edges[edge]}"
        else:
            edge_labels[edge] = f"[{le}, {ue}]"

    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=edge_labels,
        font_size=8,
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#9CA3AF"),
        ax=ax,
    )
    plt.axis("off")
    return fig


# --------------------------------------------------
# 3. Barre Latérale : Sélection du Mode
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

    selected_setup = st.slider(
        "⚡ Sélection rapide du Setup (1 à 25) :",
        min_value=1,
        max_value=25,
        value=st.session_state.current_setup_num,
        step=1,
    )

    if selected_setup != st.session_state.current_setup_num:
        generate_setup_graph(selected_setup)
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
            n_l = c1.number_input(
                f"Borne inf ({e[0]}→{e[1]})", value=float(le), step=0.5
            )
            n_u = c2.number_input(
                f"Borne sup ({e[0]}→{e[1]})", value=float(ue), step=0.5
            )
            if n_l < n_u:
                st.session_state.edges_data[e] = (n_l, n_u)
        if st.form_submit_button("💾 Enregistrer la Structure"):
            st.success("Réseau mis à jour !")
            st.rerun()

# ==================================================
# MODE 4 : EXPLICATION & SOLUTION (PROFESSEURS)
# ==================================================
elif app_mode == "📖 4. Mode Explication & Solution (Professeurs)":
    st.subheader("📖 Espace Pédagogique & Solution du Modèle")

    # Sélection du Setup pour examen rapide par le professeur
    col_prof_sel, col_prof_blank = st.columns([2, 1])
    with col_prof_sel:
        prof_setup = st.selectbox(
            "📍 Choisir le Setup à analyser (1 à 25) :",
            options=list(range(1, 26)),
            index=st.session_state.current_setup_num - 1,
        )
        if prof_setup != st.session_state.current_setup_num:
            generate_setup_graph(prof_setup)
            st.rerun()

    st.markdown(
        """
    <div class="teacher-box">
    <h4>🎓 Présentation Théorique du Graph Inspection Game</h4>
    <ul>
    <li><b>Objectif :</b> Parcourir le réseau du puit $s$ au puit $t$ avec le coût total minimal.</li>
    <li><b>Information Incomplète :</b> Les poids réels $c(e)$ sont cachés dans l'intervalle $[l_e, u_e]$.</li>
    <li><b>Trade-off :</b> Payer un coût d'inspection $C_{inspect}$ pour lever l'incertitude sur une arête vs Prendre le risque de passer sans inspecter.</li>
    </ul>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Calcul du chemin optimal réel basé sur les coûts secrets
    real_graph = nx.DiGraph()
    for e, c in st.session_state.secret_costs.items():
        real_graph.add_edge(e[0], e[1], weight=c)

    true_path = nx.shortest_path(
        real_graph, source="s", target="t", weight="weight"
    )
    true_cost = nx.shortest_path_length(
        real_graph, source="s", target="t", weight="weight"
    )

    # Résumé de la solution
    c_s1, c_s2 = st.columns(2)
    with c_s1:
        st.success(f"🏆 **Plus Court Chemin Réel :** `{' → '.join(true_path)}`")
    with c_s2:
        st.success(f"💰 **Coût Minimal Absolu :** `{true_cost:.2f}`")

    # Affichage de la Carte avec le Chemin Fléché
    st.markdown(
        f"### 🗺️ Carte du Setup {st.session_state.current_setup_num} (Chemin Optimal Fléché en Rouge)"
    )
    fig_teacher = render_graph_plot(
        highlight_path=true_path, show_secrets=True
    )
    st.pyplot(fig_teacher)

    st.markdown("---")

# ==================================================
# AFFICHAGE DU GRAPHE ET PANNEAU DE JEU (MODES 1, 2, 3)
# ==================================================
if app_mode != "📖 4. Mode Explication & Solution (Professeurs)":

    if st.session_state.last_result_msg:
        if st.session_state.last_result_msg["type"] == "win":
            st.success(st.session_state.last_result_msg["text"])
            st.balloons()
        else:
            st.error(st.session_state.last_result_msg["text"])

    col_graph, col_panel = st.columns([3, 2])

    with col_graph:
        st.subheader(
            f"🗺️ Vision du Réseau — Setup {st.session_state.current_setup_num}"
        )
        fig_game = render_graph_plot(show_secrets=False)
        st.pyplot(fig_game)

    with col_panel:
        if app_mode == "🤖 2. Mode Challenge vs IA":
            st.markdown(
                f'<div class="score-box-single">🏆 Score Joueur : <span class="score-val">{st.session_state.score_inspector} pts</span></div>',
                unsafe_allow_html=True,
            )
        else:
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

        avail = [
            e
            for e in st.session_state.edges_data.keys()
            if e not in st.session_state.inspected_edges
        ]
        if avail:
            e_sel = st.selectbox(
                "Inspecter une arête :",
                options=avail,
                format_func=lambda x: f"({x[0]} → {x[1]}) [{st.session_state.edges_data[x]}]",
            )
            if st.button(
                "🔍 Lancer Inspection", type="primary", use_container_width=True
            ):
                st.session_state.inspected_edges[e_sel] = (
                    st.session_state.secret_costs[e_sel]
                )
                st.rerun()

        st.markdown("---")
        st.subheader("🏁 Choix du Chemin Final")
        all_p = list(
            nx.all_simple_paths(st.session_state.G, source="s", target="t")
        )
        p_str = [" → ".join(p) for p in all_p]
        c_p_str = st.selectbox("Sélectionner l'itinéraire :", options=p_str)
        c_p = all_p[p_str.index(c_p_str)]

        if st.button(
            "🏁 Valider & Passer au Setup Suivant",
            type="primary",
            use_container_width=True,
        ):
            r_cost = sum(
                st.session_state.secret_costs[(u, v)]
                for u, v in zip(c_p[:-1], c_p[1:])
            )
            tot_score = r_cost + c_tot_ins

            real_g = nx.DiGraph()
            for e, c in st.session_state.secret_costs.items():
                real_g.add_edge(e[0], e[1], weight=c)
            t_cost = nx.shortest_path_length(
                real_g, source="s", target="t", weight="weight"
            )

            gap = tot_score - t_cost
            max_possible_inspections = len(st.session_state.edges_data)

            gain_inspector = (max_possible_inspections - nb_ins) * 10
            gain_adversary = nb_ins * 10

            if gap <= 1.5:
                st.session_state.score_inspector += gain_inspector
                st.session_state.score_adversary = 0
                st.session_state.last_result_msg = {
                    "type": "win",
                    "text": f"🎉 Victoire de l'Inspecteur ! (+{gain_inspector} pts) | Total: {st.session_state.score_inspector} pts",
                }
            else:
                st.session_state.score_adversary += gain_adversary
                st.session_state.score_inspector = 0
                st.session_state.last_result_msg = {
                    "type": "loss",
                    "text": f"🦹 Victoire de l'Adversaire ! (+{gain_adversary} pts) | Total: {st.session_state.score_adversary} pts",
                }

            next_setup = (st.session_state.current_setup_num % 25) + 1
            generate_setup_graph(next_setup)
            st.rerun()

# --------------------------------------------------
# 4. Boutons de Réinitialisation Globale
# --------------------------------------------------
st.divider()
c_r1, c_r2 = st.columns(2)
with c_r1:
    if st.button(
        "🎲 Régénérer ce Setup (Conserver les Scores)",
        use_container_width=True,
    ):
        generate_setup_graph(st.session_state.current_setup_num)
        st.session_state.last_result_msg = None
        st.rerun()

with c_r2:
    if st.button(
        "🔄 Réinitialiser Tout (Cartes + Scores à 0)", use_container_width=True
    ):
        st.session_state.score_inspector = 0
        st.session_state.score_adversary = 0
        st.session_state.last_result_msg = None
        generate_setup_graph(1)
        st.rerun()
