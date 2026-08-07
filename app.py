import matplotlib

matplotlib.use("Agg")  # Protection backend GUI

import math
import random
import matplotlib.pyplot as plt
import networkx as nx
import streamlit as st

# --------------------------------------------------
# 1. Configuration de la page Streamlit & Style CSS
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
    /* Titres & En-têtes */
    .main-title { 
        font-size: 2.5rem; 
        font-weight: 800; 
        color: #1E3A8A; 
        text-align: center; 
        margin-bottom: 5px;
    }
    .sub-title { 
        font-size: 1.1rem; 
        color: #4B5563; 
        text-align: center; 
        margin-bottom: 25px; 
    }
    
    /* Cartes de Contenu Stylisées */
    .custom-card {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.03);
    }
    
    .teacher-box { 
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        border-left: 6px solid #2563EB; 
        padding: 18px; 
        border-radius: 10px; 
        margin-bottom: 20px;
        color: #1E293B;
    }
    
    /* Tableaux de Scores Harmonieux */
    .score-container {
        display: flex;
        gap: 10px;
        margin-bottom: 15px;
    }
    .score-box { 
        flex: 1;
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%); 
        color: #FFFFFF; 
        padding: 15px; 
        border-radius: 12px; 
        text-align: center; 
        box-shadow: 0px 4px 8px rgba(37, 99, 235, 0.2);
    }
    .score-title {
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        opacity: 0.9;
    }
    .score-val {
        color: #FBBF24;
        font-size: 1.8rem;
        font-weight: 900;
        margin-top: 5px;
    }
    </style>
""",
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

    num_intermediate = 2 + (setup_number % 5) + (setup_number // 9)
    intermediate_nodes = [chr(97 + i) for i in range(num_intermediate)]

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
# Fonction Rendu Visuel du Graphe (Matplotlib)
# --------------------------------------------------
def render_graph_plot(highlight_path=None, show_secrets=False):
    G = st.session_state.G
    pos = st.session_state.pos
    fig, ax = plt.subplots(figsize=(8.5, 5.2))

    path_edges = []
    if highlight_path and len(highlight_path) > 1:
        path_edges = list(zip(highlight_path[:-1], highlight_path[1:]))

    normal_edges = [e for e in G.edges() if e not in path_edges]

    # Nœuds avec bordure élégante
    nx.draw_networkx_nodes(
        G,
        pos,
        node_color="#2563EB",
        node_size=1300,
        ax=ax,
        edgecolors="#1E3A8A",
        linewidths=2,
    )
    nx.draw_networkx_labels(
        G, pos, font_size=12, font_weight="bold", font_color="white", ax=ax
    )

    # Arêtes normales (Flèches grises)
    nx.draw_networkx_edges(
        G,
        pos,
        edgelist=normal_edges,
        width=2.2,
        edge_color="#9CA3AF",
        arrowstyle="-|>",
        arrowsize=22,
        ax=ax,
    )

    # Arêtes du chemin optimal en surbrillance (Flèches rouges/oranges)
    if path_edges:
        nx.draw_networkx_edges(
            G,
            pos,
            edgelist=path_edges,
            width=4.5,
            edge_color="#DC2626",
            arrowstyle="-|>",
            arrowsize=28,
            ax=ax,
        )

    # Étiquettes de poids
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
        font_size=8.5,
        bbox=dict(
            boxstyle="round,pad=0.3",
            fc="#FFFFFF",
            ec="#CBD5E1",
            lw=1,
        ),
        ax=ax,
    )
    plt.axis("off")
    plt.tight_layout()
    return fig


# --------------------------------------------------
# 3. En-tête Principal
# --------------------------------------------------
st.markdown(
    '<div class="main-title">🕵️‍♂️ Graph Inspection Game</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-title">Plateforme Interactive & Pédagogique | MTYM 2026</div>',
    unsafe_allow_html=True,
)

# --------------------------------------------------
# 4. Barre Latérale Globale (Contrôles Globaux)
# --------------------------------------------------
st.sidebar.header("⚙️ Configuration Globale")

# SELECTION DE MODE
app_mode = st.sidebar.radio(
    "🎯 Choisir le Mode :",
    [
        "👥 1. Joueur vs Joueur",
        "🤖 2. Challenge vs IA",
        "🛠️ 3. Concepteur de Réseau",
        "📖 4. Explication & Solution (Professeurs)",
    ],
)

st.sidebar.markdown("---")

# CURSEUR SETUP DISPONIBLE POUR TOUS LES MODES
selected_setup = st.sidebar.slider(
    "📍 Sélection du Setup (1 à 25) :",
    min_value=1,
    max_value=25,
    value=st.session_state.current_setup_num,
    step=1,
)

if selected_setup != st.session_state.current_setup_num:
    generate_setup_graph(selected_setup)
    st.session_state.last_result_msg = None
    st.rerun()

inspection_cost_unit = st.sidebar.slider(
    "💰 Coût d'inspection (C_inspect) :",
    min_value=0.5,
    max_value=4.0,
    value=1.0,
    step=0.5,
)

st.sidebar.markdown("---")

# --------------------------------------------------
# 5. Rendu Selon le Mode
# --------------------------------------------------

# ==================================================
# MODE 4 : EXPLICATION & SOLUTION (PROFESSEURS)
# ==================================================
if app_mode == "📖 4. Explication & Solution (Professeurs)":
    st.markdown("### 📖 Espace Pédagogique & Analyse Complète")

    st.markdown(
        """
    <div class="teacher-box">
    <h4>🎓 Fondements du Modèle Théorique</h4>
    <ul>
        <li><b>Contexte :</b> Résolution d'un chemin de $s$ à $t$ en situation d'information incomplète.</li>
        <li><b>Données :</b> Chaque arête $e$ possède un coût secret $c(e)$ confiné dans l'intervalle connu $[l_e, u_e]$.</li>
        <li><b>Arbitrage Pédagogique :</b> Payer un coût fixe d'inspection $C_{inspect}$ pour lever le doute ou assumer l'incertitude.</li>
    </ul>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Calcul du chemin réel optimal
    real_graph = nx.DiGraph()
    for e, c in st.session_state.secret_costs.items():
        real_graph.add_edge(e[0], e[1], weight=c)

    true_path = nx.shortest_path(
        real_graph, source="s", target="t", weight="weight"
    )
    true_cost = nx.shortest_path_length(
        real_graph, source="s", target="t", weight="weight"
    )

    c_s1, c_s2 = st.columns(2)
    with c_s1:
        st.success(f"🏆 **Plus Court Chemin Théorique :** `{' → '.join(true_path)}`")
    with c_s2:
        st.success(f"💰 **Coût Minimal Absolu :** `{true_cost:.2f}`")

    st.markdown(
        f"#### 🗺️ Carte du Setup {st.session_state.current_setup_num} (Chemin Optimal Fléché)"
    )
    fig_teacher = render_graph_plot(
        highlight_path=true_path, show_secrets=True
    )
    st.pyplot(fig_teacher)

# ==================================================
# MODES 1, 2, 3 (ESPACE INTERACTIF ET JEU)
# ==================================================
else:
    if st.session_state.last_result_msg:
        if st.session_state.last_result_msg["type"] == "win":
            st.success(st.session_state.last_result_msg["text"])
            st.balloons()
        else:
            st.error(st.session_state.last_result_msg["text"])

    col_graph, col_panel = st.columns([3, 2])

    # Colonne Gauche : Carte
    with col_graph:
        st.markdown(
            f"### 🗺️ Carte du Réseau — Setup {st.session_state.current_setup_num}"
        )
        fig_game = render_graph_plot(show_secrets=False)
        st.pyplot(fig_game)

    # Colonne Droite : Panneau Interactif
    with col_panel:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)

        if app_mode == "🤖 2. Challenge vs IA":
            st.markdown(
                f"""
            <div class="score-container">
                <div class="score-box">
                    <div class="score-title">🏆 Score Joueur</div>
                    <div class="score-val">{st.session_state.score_inspector} pts</div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        elif app_mode == "👥 1. Joueur vs Joueur":
            st.markdown(
                f"""
            <div class="score-container">
                <div class="score-box">
                    <div class="score-title">🕵️ Inspecteur</div>
                    <div class="score-val">{st.session_state.score_inspector} pts</div>
                </div>
                <div class="score-box" style="background: linear-gradient(135deg, #DC2626 0%, #EF4444 100%);">
                    <div class="score-title">🦹 Adversaire</div>
                    <div class="score-val">{st.session_state.score_adversary} pts</div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        # MODE 3 : CONCEPTEUR
        if app_mode == "🛠️ 3. Concepteur de Réseau":
            st.markdown("#### 🛠️ Édition des Bornes du Réseau")
            with st.form("creator_form"):
                for e, (le, ue) in st.session_state.edges_data.items():
                    c1, c2 = st.columns(2)
                    n_l = c1.number_input(
                        f"Min ({e[0]}→{e[1]})", value=float(le), step=0.5
                    )
                    n_u = c2.number_input(
                        f"Max ({e[0]}→{e[1]})", value=float(ue), step=0.5
                    )
                    if n_l < n_u:
                        st.session_state.edges_data[e] = (n_l, n_u)
                if st.form_submit_button("💾 Sauvegarder"):
                    st.success("Bornes mises à jour !")
                    st.rerun()

        # ACTIONS ET INSPECTIONS
        st.markdown("#### 🕵️ Actions d'Inspection")
        nb_ins = len(st.session_state.inspected_edges)
        c_tot_ins = nb_ins * inspection_cost_unit

        st.caption(
            f"Inspections : **{nb_ins}** | Frais accumulés : **{c_tot_ins:.1f}**"
        )

        avail = [
            e
            for e in st.session_state.edges_data.keys()
            if e not in st.session_state.inspected_edges
        ]
        if avail:
            e_sel = st.selectbox(
                "Choisir une arête à inspecter :",
                options=avail,
                format_func=lambda x: f"({x[0]} → {x[1]}) [{st.session_state.edges_data[x]}]",
            )
            if st.button(
                "🔍 Inspecter l'Arête",
                type="primary",
                use_container_width=True,
            ):
                st.session_state.inspected_edges[e_sel] = (
                    st.session_state.secret_costs[e_sel]
                )
                st.rerun()

        st.markdown("---")
        st.markdown("#### 🏁 Validation du Trajet")
        all_p = list(
            nx.all_simple_paths(st.session_state.G, source="s", target="t")
        )
        p_str = [" → ".join(p) for p in all_p]
        c_p_str = st.selectbox("Sélectionner l'itinéraire final :", options=p_str)
        c_p = all_p[p_str.index(c_p_str)]

        if st.button(
            "🚀 Valider le Trajet", type="primary", use_container_width=True
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
                    "text": f"🎉 Excellent choix ! (+{gain_inspector} pts) | Total : {st.session_state.score_inspector} pts",
                }
            else:
                st.session_state.score_adversary += gain_adversary
                st.session_state.score_inspector = 0
                st.session_state.last_result_msg = {
                    "type": "loss",
                    "text": f"🦹 Chemin sous-optimal ! (+{gain_adversary} pts Adversaire)",
                }

            next_setup = (st.session_state.current_setup_num % 25) + 1
            generate_setup_graph(next_setup)
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------
# 6. Boutons de Réinitialisation Bas de Page
# --------------------------------------------------
st.divider()
c_r1, c_r2 = st.columns(2)
with c_r1:
    if st.button("🎲 Régénérer ce Setup", use_container_width=True):
        generate_setup_graph(st.session_state.current_setup_num)
        st.session_state.last_result_msg = None
        st.rerun()

with c_r2:
    if st.button("🔄 Remise à Zéro Complète", use_container_width=True):
        st.session_state.score_inspector = 0
        st.session_state.score_adversary = 0
        st.session_state.last_result_msg = None
        generate_setup_graph(1)
        st.rerun()
