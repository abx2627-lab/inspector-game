import matplotlib

matplotlib.use("Agg")  # Protection backend GUI

import random
import matplotlib.pyplot as plt
import networkx as nx
import streamlit as st

# --------------------------------------------------
# 1. Configuration & Style CSS
# --------------------------------------------------
st.set_page_config(
    page_title="Graph Inspection Game - Geometrized Setups",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main-title { 
        font-size: 2.2rem; 
        font-weight: 800; 
        color: #1E3A8A; 
        text-align: center; 
        margin-bottom: 5px;
    }
    .sub-title { 
        font-size: 1.0rem; 
        color: #4B5563; 
        text-align: center; 
        margin-bottom: 20px; 
    }
    .setup-badge {
        background-color: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-radius: 8px;
        padding: 8px 12px;
        color: #1E40AF;
        font-weight: 600;
        margin-bottom: 15px;
        text-align: center;
    }
    .custom-card {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 15px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.03);
    }
    .teacher-box { 
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        border-left: 6px solid #2563EB; 
        padding: 16px; 
        border-radius: 10px; 
        margin-bottom: 15px;
        color: #1E293B;
    }
    .score-container {
        display: flex;
        gap: 10px;
        margin-bottom: 15px;
    }
    .score-box { 
        flex: 1;
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%); 
        color: #FFFFFF; 
        padding: 12px; 
        border-radius: 10px; 
        text-align: center; 
    }
    .score-title { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; }
    .score-val { color: #FBBF24; font-size: 1.6rem; font-weight: 800; }
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


# --------------------------------------------------
# 3. Générateur de Setups Géométriques Ordonnés
# --------------------------------------------------
def build_geometric_setup(setup_number=1):
    """
    Génère 25 topologies très claires basées sur des formes géométriques.
    - 1 à 5 : Séries-Parallèles & Losanges
    - 6 à 10 : Diamants & Hexagones
    - 11 à 15 : Grilles / Lattices
    - 16 à 20 : Polyèdres & Planaires Triangulés
    - 21 à 25 : Structuration Papillon (Butterfly) & Réseaux Complexes
    """
    G = nx.DiGraph()
    pos = {}
    family_name = ""

    random.seed(setup_number * 98765)

    # ---------------------------------------------------------
    # FAMILLE 1 : Série-Parallèle (Setups 1-5)
    # ---------------------------------------------------------
    if 1 <= setup_number <= 5:
        family_name = "Série-Parallèle & Losanges"
        n_parallel = 2 + (setup_number % 3)
        pos["s"] = (0.0, 0.5)
        pos["t"] = (3.0, 0.5)

        if setup_number in [1, 2]:
            # Simple couche parallèle
            nodes = [chr(97 + i) for i in range(n_parallel)]
            for i, n in enumerate(nodes):
                pos[n] = (1.5, 1.0 - (i * (1.0 / max(1, n_parallel - 1))))
                G.add_edge("s", n)
                G.add_edge(n, "t")
        else:
            # Double couche parallèle
            pos["a"] = (1.0, 0.8)
            pos["b"] = (1.0, 0.2)
            pos["c"] = (2.0, 0.8)
            pos["d"] = (2.0, 0.2)
            G.add_edges_from(
                [
                    ("s", "a"),
                    ("s", "b"),
                    ("a", "c"),
                    ("a", "d"),
                    ("b", "c"),
                    ("b", "d"),
                    ("c", "t"),
                    ("d", "t"),
                ]
            )

    # ---------------------------------------------------------
    # FAMILLE 2 : Diamants & Hexagones Imbriqués (Setups 6-10)
    # ---------------------------------------------------------
    elif 6 <= setup_number <= 10:
        family_name = "Diamants & Hexagones Centrés"
        pos["s"] = (0.0, 0.5)
        pos["t"] = (4.0, 0.5)

        # Structure à double diamant
        pos["a"] = (1.0, 0.9)
        pos["b"] = (1.0, 0.1)
        pos["m"] = (2.0, 0.5)  # Centre
        pos["c"] = (3.0, 0.9)
        pos["d"] = (3.0, 0.1)

        edges = [
            ("s", "a"),
            ("s", "b"),
            ("a", "m"),
            ("b", "m"),
            ("m", "c"),
            ("m", "d"),
            ("c", "t"),
            ("d", "t"),
        ]
        if setup_number > 7:
            edges.extend([("a", "c"), ("b", "d")])  # Arêtes transversales
        G.add_edges_from(edges)

    # ---------------------------------------------------------
    # FAMILLE 3 : Grilles / Lattices (Setups 11-15)
    # ---------------------------------------------------------
    elif 11 <= setup_number <= 15:
        family_name = "Grille Rectangulaire (Lattice)"
        pos["s"] = (0.0, 0.5)
        pos["t"] = (3.0, 0.5)

        # Grille 2x3 ou 3x3
        pos["a1"] = (1.0, 0.9)
        pos["a2"] = (1.0, 0.1)
        pos["b1"] = (2.0, 0.9)
        pos["b2"] = (2.0, 0.1)

        edges = [
            ("s", "a1"),
            ("s", "a2"),
            ("a1", "b1"),
            ("a2", "b2"),
            ("a1", "a2"),
            ("b1", "b2"),
            ("b1", "t"),
            ("b2", "t"),
        ]
        if setup_number >= 13:
            pos["m"] = (1.5, 0.5)
            edges.extend([("a1", "m"), ("a2", "m"), ("m", "b1"), ("m", "b2")])

        G.add_edges_from(edges)

    # ---------------------------------------------------------
    # FAMILLE 4 : Polyèdres Planaires Triangulés (Setups 16-20)
    # ---------------------------------------------------------
    elif 16 <= setup_number <= 20:
        family_name = "Polyèdre & Triangulation Planaires"
        pos["s"] = (0.0, 0.5)
        pos["t"] = (3.5, 0.5)

        pos["top"] = (1.75, 1.1)
        pos["bot"] = (1.75, -0.1)
        pos["m1"] = (1.0, 0.5)
        pos["m2"] = (2.5, 0.5)

        edges = [
            ("s", "top"),
            ("s", "m1"),
            ("s", "bot"),
            ("top", "m2"),
            ("m1", "m2"),
            ("bot", "m2"),
            ("top", "t"),
            ("m2", "t"),
            ("bot", "t"),
        ]
        G.add_edges_from(edges)

    # ---------------------------------------------------------
    # FAMILLE 5 : Réseaux Papillon & Complexe (Setups 21-25)
    # ---------------------------------------------------------
    else:
        family_name = "Structure Papillon (Butterfly)"
        pos["s"] = (0.0, 0.5)
        pos["t"] = (3.0, 0.5)

        pos["u1"] = (0.8, 0.9)
        pos["d1"] = (0.8, 0.1)
        pos["u2"] = (2.2, 0.9)
        pos["d2"] = (2.2, 0.1)

        # Crossings (Papillon)
        edges = [
            ("s", "u1"),
            ("s", "d1"),
            ("u1", "u2"),
            ("d1", "d2"),
            ("u1", "d2"),
            ("d1", "u2"),
            ("u2", "t"),
            ("d2", "t"),
        ]
        G.add_edges_from(edges)

    # Génération des bornes [le, ue] et valeurs réelles
    edges_data = {}
    secret_costs = {}

    for u, v in G.edges():
        le = round(random.uniform(1.0, 4.0), 1)
        ue = round(le + random.uniform(2.0, 5.0), 1)
        edges_data[(u, v)] = (le, ue)
        secret_costs[(u, v)] = round(random.uniform(le, ue), 2)

    st.session_state.G = G
    st.session_state.pos = pos
    st.session_state.edges_data = edges_data
    st.session_state.secret_costs = secret_costs
    st.session_state.family_name = family_name
    st.session_state.inspected_edges = {}
    st.session_state.current_setup_num = setup_number


if "G" not in st.session_state:
    build_geometric_setup(1)


# --------------------------------------------------
# 4. Rendu Visuel du Graphe (Haute Lisibilité)
# --------------------------------------------------
def render_clear_graph_plot(highlight_path=None, show_secrets=False):
    G = st.session_state.G
    pos = st.session_state.pos

    fig, ax = plt.subplots(figsize=(9, 5.5))

    path_edges = []
    if highlight_path and len(highlight_path) > 1:
        path_edges = list(zip(highlight_path[:-1], highlight_path[1:]))

    normal_edges = [e for e in G.edges() if e not in path_edges]

    # Nœuds avec grande taille et bordures épaisses
    nx.draw_networkx_nodes(
        G,
        pos,
        node_color="#1E40AF",
        node_size=1600,
        ax=ax,
        edgecolors="#1E3A8A",
        linewidths=2.5,
    )
    nx.draw_networkx_labels(
        G, pos, font_size=12, font_weight="bold", font_color="white", ax=ax
    )

    # Arêtes normales (Flèches grises bien nettes)
    nx.draw_networkx_edges(
        G,
        pos,
        edgelist=normal_edges,
        width=2.5,
        edge_color="#64748B",
        arrowstyle="-|>",
        arrowsize=24,
        ax=ax,
    )

    # Arêtes du chemin optimal en surbrillance
    if path_edges:
        nx.draw_networkx_edges(
            G,
            pos,
            edgelist=path_edges,
            width=4.5,
            edge_color="#DC2626",
            arrowstyle="-|>",
            arrowsize=30,
            ax=ax,
        )

    # Étiquettes de poids très lisibles (Box blanche contour arrondi)
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
        font_size=9.5,
        font_weight="bold",
        bbox=dict(
            boxstyle="round,pad=0.4",
            fc="#FFFFFF",
            ec="#94A3B8",
            lw=1.5,
        ),
        ax=ax,
    )

    # Délimitation nette
    x_vals = [p[0] for p in pos.values()]
    y_vals = [p[1] for p in pos.values()]
    ax.set_xlim(min(x_vals) - 0.4, max(x_vals) + 0.4)
    ax.set_ylim(min(y_vals) - 0.4, max(y_vals) + 0.4)

    plt.axis("off")
    plt.tight_layout()
    return fig


# --------------------------------------------------
# 5. En-tête Principal
# --------------------------------------------------
st.markdown(
    '<div class="main-title">📐 Graph Inspection Game</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-title">Setups Géométriques Ordonnés & Intervalles Clairs</div>',
    unsafe_allow_html=True,
)

# --------------------------------------------------
# 6. Barre Latérale Globale (Accessible dans TOUS les modes)
# --------------------------------------------------
st.sidebar.header("⚙️ Configuration Globale")

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

selected_setup = st.sidebar.slider(
    "📍 Sélection du Setup (1 à 25) :",
    min_value=1,
    max_value=25,
    value=st.session_state.current_setup_num,
    step=1,
)

if selected_setup != st.session_state.current_setup_num:
    build_geometric_setup(selected_setup)
    st.session_state.last_result_msg = None
    st.rerun()

inspection_cost_unit = st.sidebar.slider(
    "💰 Coût d'inspection (C_inspect) :",
    min_value=0.5,
    max_value=4.0,
    value=1.0,
    step=0.5,
)

# --------------------------------------------------
# 7. Rendu Selon le Mode Actif
# --------------------------------------------------

# ==================================================
# MODE 4 : EXPLICATION & SOLUTION (PROFESSEURS)
# ==================================================
if app_mode == "📖 4. Explication & Solution (Professeurs)":
    st.markdown("### 📖 Espace Pédagogique & Solution Théorique")

    st.markdown(
        f"""
    <div class="teacher-box">
        <h4>📐 Setup N°{st.session_state.current_setup_num} — Modèle Géométrique : {st.session_state.family_name}</h4>
        <p>Les arêtes affichent la valeur exacte 🔑 $c(e)$ ainsi que l'intervalle théorique $[l_e, u_e]$.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

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
        st.success(f"🏆 **Plus Court Chemin Révélé :** `{' → '.join(true_path)}`")
    with c_s2:
        st.success(f"💰 **Coût Réel Minimal :** `{true_cost:.2f}`")

    fig_teacher = render_clear_graph_plot(
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

    with col_graph:
        st.markdown(
            f'<div class="setup-badge">Setup {st.session_state.current_setup_num} / 25 — Structure : <b>{st.session_state.family_name}</b></div>',
            unsafe_allow_html=True,
        )
        fig_game = render_clear_graph_plot(show_secrets=False)
        st.pyplot(fig_game)

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

        if app_mode == "🛠️ 3. Concepteur de Réseau":
            st.markdown("#### 🛠️ Modification des Bornes")
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
                if st.form_submit_button("💾 Enregistrer"):
                    st.success("Bornes enregistrées !")
                    st.rerun()

        st.markdown("#### 🕵️ Actions d'Inspection")
        nb_ins = len(st.session_state.inspected_edges)
        c_tot_ins = nb_ins * inspection_cost_unit
        st.caption(
            f"Inspections réalisées : **{nb_ins}** | Frais : **{c_tot_ins:.1f}**"
        )

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
                "🔍 Inspecter l'Arête",
                type="primary",
                use_container_width=True,
            ):
                st.session_state.inspected_edges[e_sel] = (
                    st.session_state.secret_costs[e_sel]
                )
                st.rerun()

        st.markdown("---")
        st.markdown("#### 🏁 Validation du Chemin")
        all_p = list(
            nx.all_simple_paths(st.session_state.G, source="s", target="t")
        )
        p_str = [" → ".join(p) for p in all_p]
        c_p_str = st.selectbox(
            "Sélectionner votre itinéraire final :", options=p_str
        )
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
            if gap <= 1.5:
                gain = (len(st.session_state.edges_data) - nb_ins) * 10
                st.session_state.score_inspector += gain
                st.session_state.last_result_msg = {
                    "type": "win",
                    "text": f"🎉 Trajet optimal sélectionné ! (+{gain} pts)",
                }
            else:
                st.session_state.score_adversary += 20
                st.session_state.last_result_msg = {
                    "type": "loss",
                    "text": "🦹 Trajet sous-optimal (+20 pts Adversaire)",
                }

            next_setup = (st.session_state.current_setup_num % 25) + 1
            build_geometric_setup(next_setup)
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------
# 8. Réinitialisation
# --------------------------------------------------
st.divider()
c_r1, c_r2 = st.columns(2)
with c_r1:
    if st.button("🎲 Réinitialiser ce Setup", use_container_width=True):
        build_geometric_setup(st.session_state.current_setup_num)
        st.session_state.last_result_msg = None
        st.rerun()

with c_r2:
    if st.button("🔄 Remise à Zéro Complète", use_container_width=True):
        st.session_state.score_inspector = 0
        st.session_state.score_adversary = 0
        st.session_state.last_result_msg = None
        build_geometric_setup(1)
        st.rerun()
