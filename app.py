import matplotlib

matplotlib.use("Agg")  # Protection backend GUI

import random
import time
import matplotlib.pyplot as plt
import networkx as nx
import streamlit as st

# --------------------------------------------------
# 1. Configuration & Style CSS avec Animations
# --------------------------------------------------
st.set_page_config(
    page_title="Graph Inspection Game - 10 Unique Figures",
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
    .phase-indicator {
        background-color: #FEF3C7;
        border: 1px solid #FCD34D;
        border-radius: 8px;
        padding: 10px;
        color: #92400E;
        font-weight: bold;
        text-align: center;
        margin-bottom: 15px;
    }
    .round-badge {
        background-color: #F3E8FF;
        border: 1px solid #D8B4FE;
        color: #6B21A8;
        font-weight: bold;
        padding: 6px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 12px;
    }

    /* --------------------------------------------------
       ANIMATIONS FINALES DU MATCH (PAS DE BALLONS)
    -------------------------------------------------- */
    @keyframes pulseGlowBlue {
        0% { box-shadow: 0 0 15px #3B82F6; transform: scale(1); }
        50% { box-shadow: 0 0 35px #60A5FA; transform: scale(1.02); }
        100% { box-shadow: 0 0 15px #3B82F6; transform: scale(1); }
    }

    @keyframes pulseGlowRed {
        0% { box-shadow: 0 0 15px #EF4444; transform: scale(1); }
        50% { box-shadow: 0 0 35px #F87171; transform: scale(1.02); }
        100% { box-shadow: 0 0 15px #EF4444; transform: scale(1); }
    }

    .victory-card-blue {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%);
        border: 3px solid #60A5FA;
        border-radius: 20px;
        padding: 35px;
        text-align: center;
        color: white;
        margin-bottom: 25px;
        animation: pulseGlowBlue 2s infinite ease-in-out;
    }

    .victory-card-red {
        background: linear-gradient(135deg, #18181B 0%, #7F1D1D 100%);
        border: 3px solid #F87171;
        border-radius: 20px;
        padding: 35px;
        text-align: center;
        color: white;
        margin-bottom: 25px;
        animation: pulseGlowRed 2s infinite ease-in-out;
    }

    .victory-card-draw {
        background: linear-gradient(135deg, #18181B 0%, #4C1D95 100%);
        border: 3px solid #A78BFA;
        border-radius: 20px;
        padding: 35px;
        text-align: center;
        color: white;
        margin-bottom: 25px;
    }

    /* Animation Pluie d'Emojis */
    @keyframes dropEmojis {
        0% { opacity: 0; transform: translateY(-50px) scale(0.5); }
        50% { opacity: 1; transform: translateY(0px) scale(1.2); }
        100% { opacity: 0; transform: translateY(50px) scale(0.8); }
    }
    .emoji-rain {
        font-size: 3rem;
        text-align: center;
        margin: 10px 0;
        animation: dropEmojis 1.5s ease-in-out infinite alternate;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --------------------------------------------------
# 2. Gestion des États Globaux
# --------------------------------------------------
if "score_inspector" not in st.session_state:
    st.session_state.score_inspector = 0

if "score_adversary" not in st.session_state:
    st.session_state.score_adversary = 0

if "current_round" not in st.session_state:
    st.session_state.current_round = 1

if "game_over" not in st.session_state:
    st.session_state.game_over = False

if "last_result_msg" not in st.session_state:
    st.session_state.last_result_msg = None

if "current_setup_num" not in st.session_state:
    st.session_state.current_setup_num = 1

if "pvp_phase" not in st.session_state:
    st.session_state.pvp_phase = "adversary_turn"


# --------------------------------------------------
# 3. Générateur des Topologies Uniques
# --------------------------------------------------
def build_10_unique_setups(setup_number=1):
    G = nx.DiGraph()
    pos = {}
    shape_title = ""

    random.seed(setup_number * 12345)

    if setup_number == 1:
        shape_title = "1. Carré Parallèle"
        pos = {"s": (0.0, 0.5), "a": (1.5, 1.2), "b": (1.5, -0.2), "t": (3.0, 0.5)}
        G.add_edges_from([("s", "a"), ("s", "b"), ("a", "t"), ("b", "t")])

    elif setup_number == 2:
        shape_title = "2. Losange à Diagonale"
        pos = {"s": (0.0, 0.5), "a": (1.5, 1.2), "b": (1.5, -0.2), "t": (3.0, 0.5)}
        G.add_edges_from(
            [("s", "a"), ("s", "b"), ("a", "b"), ("a", "t"), ("b", "t")]
        )

    elif setup_number == 3:
        shape_title = "3. Double Diamant (Nœud Central 'm')"
        pos = {
            "s": (0.0, 0.5),
            "a": (1.0, 1.2),
            "b": (1.0, -0.2),
            "m": (2.0, 0.5),
            "c": (3.0, 1.2),
            "d": (3.0, -0.2),
            "t": (4.0, 0.5),
        }
        G.add_edges_from(
            [
                ("s", "a"),
                ("s", "b"),
                ("a", "m"),
                ("b", "m"),
                ("m", "c"),
                ("m", "d"),
                ("c", "t"),
                ("d", "t"),
            ]
        )

    elif setup_number == 4:
        shape_title = "4. Grille 2x2 (Lattice)"
        pos = {
            "s": (0.0, 1.0),
            "a": (1.5, 1.0),
            "b": (0.0, 0.0),
            "t": (1.5, 0.0),
        }
        G.add_edges_from(
            [("s", "a"), ("s", "b"), ("a", "t"), ("b", "t"), ("a", "b")]
        )

    elif setup_number == 5:
        shape_title = "5. Roue / Hub Central"
        pos = {
            "s": (0.0, 0.5),
            "center": (1.8, 0.5),
            "top": (1.8, 1.4),
            "bot": (1.8, -0.4),
            "t": (3.6, 0.5),
        }
        G.add_edges_from(
            [
                ("s", "top"),
                ("s", "center"),
                ("s", "bot"),
                ("top", "center"),
                ("bot", "center"),
                ("center", "t"),
                ("top", "t"),
                ("bot", "t"),
            ]
        )

    elif setup_number == 6:
        shape_title = "6. Papillon (Croisements en X)"
        pos = {
            "s": (0.0, 0.5),
            "u1": (1.0, 1.2),
            "d1": (1.0, -0.2),
            "u2": (2.4, 1.2),
            "d2": (2.4, -0.2),
            "t": (3.4, 0.5),
        }
        G.add_edges_from(
            [
                ("s", "u1"),
                ("s", "d1"),
                ("u1", "u2"),
                ("d1", "d2"),
                ("u1", "d2"),
                ("d1", "u2"),
                ("u2", "t"),
                ("d2", "t"),
            ]
        )

    elif setup_number == 7:
        shape_title = "7. Cascade avec Raccourcis (Bypass)"
        pos = {
            "s": (0.0, 0.5),
            "a": (1.0, 1.2),
            "b": (2.0, 0.5),
            "c": (3.0, 1.2),
            "t": (4.0, 0.5),
        }
        G.add_edges_from(
            [
                ("s", "a"),
                ("a", "b"),
                ("b", "c"),
                ("c", "t"),
                ("s", "b"),
                ("b", "t"),
            ]
        )

    elif setup_number == 8:
        shape_title = "8. Pentagone Fendu"
        pos = {
            "s": (0.0, 0.5),
            "a": (1.0, 1.2),
            "b": (1.0, -0.2),
            "c": (2.2, 0.5),
            "t": (3.2, 0.5),
        }
        G.add_edges_from(
            [
                ("s", "a"),
                ("s", "b"),
                ("a", "b"),
                ("a", "c"),
                ("b", "c"),
                ("c", "t"),
            ]
        )

    elif setup_number == 9:
        shape_title = "9. Hexagone avec Traversée"
        pos = {
            "s": (0.0, 0.5),
            "a": (1.2, 1.3),
            "b": (1.2, -0.3),
            "c": (2.6, 1.3),
            "d": (2.6, -0.3),
            "t": (3.8, 0.5),
        }
        G.add_edges_from(
            [
                ("s", "a"),
                ("s", "b"),
                ("a", "c"),
                ("b", "d"),
                ("a", "d"),
                ("c", "t"),
                ("d", "t"),
            ]
        )

    elif setup_number == 10:
        shape_title = "10. Diamants Parallèles (Double Piste)"
        pos = {
            "s": (0.0, 0.5),
            "u1": (1.2, 1.4),
            "u2": (2.4, 1.4),
            "d1": (1.2, -0.4),
            "d2": (2.4, -0.4),
            "t": (3.6, 0.5),
        }
        G.add_edges_from(
            [
                ("s", "u1"),
                ("s", "d1"),
                ("u1", "u2"),
                ("d1", "d2"),
                ("u2", "t"),
                ("d2", "t"),
            ]
        )

    edges_data = {}
    secret_costs = {}

    for u, v in G.edges():
        le = round(random.uniform(1.0, 3.5), 1)
        ue = round(le + random.uniform(2.0, 5.0), 1)
        edges_data[(u, v)] = (le, ue)
        secret_costs[(u, v)] = round(random.uniform(le, ue), 2)

    st.session_state.G = G
    st.session_state.pos = pos
    st.session_state.edges_data = edges_data
    st.session_state.secret_costs = secret_costs
    st.session_state.shape_title = shape_title
    st.session_state.inspected_edges = {}
    st.session_state.current_setup_num = setup_number
    st.session_state.pvp_phase = "adversary_turn"


if "G" not in st.session_state:
    build_10_unique_setups(1)


def reset_full_match():
    st.session_state.score_inspector = 0
    st.session_state.score_adversary = 0
    st.session_state.current_round = 1
    st.session_state.game_over = False
    st.session_state.last_result_msg = None
    build_10_unique_setups(1)


# --------------------------------------------------
# 4. Rendu Visuel du Graphe
# --------------------------------------------------
def render_clear_graph_plot(highlight_path=None, show_secrets=False):
    G = st.session_state.G
    pos = st.session_state.pos

    fig, ax = plt.subplots(figsize=(9, 5.2))

    path_edges = []
    if highlight_path and len(highlight_path) > 1:
        path_edges = list(zip(highlight_path[:-1], highlight_path[1:]))

    normal_edges = [e for e in G.edges() if e not in path_edges]

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
        G, pos, font_size=11, font_weight="bold", font_color="white", ax=ax
    )

    nx.draw_networkx_edges(
        G,
        pos,
        edgelist=normal_edges,
        width=2.4,
        edge_color="#64748B",
        arrowstyle="-|>",
        arrowsize=22,
        ax=ax,
    )

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

    edge_labels = {}
    for edge, (le, ue) in st.session_state.edges_data.items():
        if show_secrets:
            sec = st.session_state.secret_costs[edge]
            edge_labels[edge] = f"🔑 {sec}\n[{le}]"
        elif edge in st.session_state.inspected_edges:
            edge_labels[edge] = f"✅ {st.session_state.inspected_edges[edge]}"
        else:
            edge_labels[edge] = f"[{le}, {ue}]"

    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=edge_labels,
        font_size=9.0,
        font_weight="bold",
        bbox=dict(
            boxstyle="round,pad=0.35",
            fc="#FFFFFF",
            ec="#94A3B8",
            lw=1.2,
        ),
        ax=ax,
    )

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
    '<div class="main-title">📐 Graph Inspection Game - Match 1v1</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-title">10 Figures Géométriques — Affrontement en 5 Rounds</div>',
    unsafe_allow_html=True,
)

# --------------------------------------------------
# 6. Barre Latérale Globale
# --------------------------------------------------
st.sidebar.header("⚙️ Configuration Globale")

app_mode = st.sidebar.radio(
    "🎯 Choisir le Mode :",
    [
        "👥 1. Joueur vs Joueur (5 Rounds)",
        "🤖 2. Challenge vs IA",
        "🛠️ 3. Concepteur de Réseau",
        "📖 4. Explication & Solution (Professeurs)",
    ],
)

st.sidebar.markdown("---")

selected_setup = st.sidebar.slider(
    "📍 Sélection du Setup (1 à 10) :",
    min_value=1,
    max_value=10,
    value=st.session_state.current_setup_num,
    step=1,
)

if selected_setup != st.session_state.current_setup_num:
    build_10_unique_setups(selected_setup)
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

# MODE 4 : EXPLICATION & SOLUTION
if app_mode == "📖 4. Explication & Solution (Professeurs)":
    st.markdown("### 📖 Espace Pédagogique & Solution Théorique")

    st.markdown(
        f"""
    <div class="teacher-box">
        <h4>📐 Setup N°{st.session_state.current_setup_num} — {st.session_state.shape_title}</h4>
        <p>Coûts réels 🔑 c(e) et bornes théoriques [l_e, u_e].</p>
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
        st.success(f"🏆 **Chemin Optimal Théorique :** `{' → '.join(true_path)}`")
    with c_s2:
        st.success(f"💰 **Coût Réel Minimal :** `{true_cost:.2f}`")

    fig_teacher = render_clear_graph_plot(
        highlight_path=true_path, show_secrets=True
    )
    st.pyplot(fig_teacher)

# MODES INTERACTIFS (1, 2, 3)
else:
    # --------------------------------------------------
    # ÉCRAN DE FIN DE MATCH ANIMÉ
    # --------------------------------------------------
    if st.session_state.game_over and app_mode == "👥 1. Joueur vs Joueur (5 Rounds)":
        score_ins = st.session_state.score_inspector
        score_adv = st.session_state.score_adversary

        if score_ins > score_adv:
            card_style = "victory-card-blue"
            emojis = "🔵 🏆 ⚡ 🔵 🏆 ⚡ 🔵"
            title = "👑 GRAND VAINQUEUR : L'INSPECTEUR BLEU !"
            sub = f"Domination tactique après 5 rounds ! Score final : **{score_ins} pts** vs {score_adv} pts."
        elif score_adv > score_ins:
            card_style = "victory-card-red"
            emojis = "🔴 🦹 🔥 🔴 🦹 🔥 🔴"
            title = "👑 GRAND VAINQUEUR : L'ADVERSAIRE ROUGE !"
            sub = f"Stratégie parfaite de dissimulation ! Score final : **{score_adv} pts** vs {score_ins} pts."
        else:
            card_style = "victory-card-draw"
            emojis = "🤝 ⚔️ 🤝 ⚔️ 🤝"
            title = "🤝 ÉGALITÉ STRATÉGIQUE !"
            sub = f"Un duel parfaitement équilibré. Les deux joueurs terminent à **{score_ins} pts**."

        st.markdown(
            f"""
        <div class="{card_style}">
            <div class="emoji-rain">{emojis}</div>
            <h1 style="font-size: 2.5rem; margin: 10px 0;">{title}</h1>
            <p style="font-size: 1.3rem; opacity: 0.9;">{sub}</p>
            <div style="margin-top: 20px; font-weight: bold; letter-spacing: 2px;">
                MATCH EN 5 ROUNDS TERMINÉ
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button(
                "🔄 Lancer un Nouveau Match 1v1",
                type="primary",
                use_container_width=True,
            ):
                reset_full_match()
                st.rerun()

    # --------------------------------------------------
    # EN COURS DE PARTIE
    # --------------------------------------------------
    else:
        if st.session_state.last_result_msg:
            if st.session_state.last_result_msg["type"] == "win":
                st.success(st.session_state.last_result_msg["text"])
            else:
                st.error(st.session_state.last_result_msg["text"])

        col_graph, col_panel = st.columns([3, 2])

        show_costs_on_graph = (
            app_mode == "👥 1. Joueur vs Joueur (5 Rounds)"
            and st.session_state.pvp_phase == "adversary_turn"
        )

        with col_graph:
            st.markdown(
                f'<div class="setup-badge">Setup {st.session_state.current_setup_num} / 10 — Topologie : <b>{st.session_state.shape_title}</b></div>',
                unsafe_allow_html=True,
            )
            fig_game = render_clear_graph_plot(show_secrets=show_costs_on_graph)
            st.pyplot(fig_game)

        with col_panel:
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)

            if app_mode == "👥 1. Joueur vs Joueur (5 Rounds)":
                st.markdown(
                    f'<div class="round-badge">⚔️ Round {st.session_state.current_round} / 5</div>',
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f"""
                <div class="score-container">
                    <div class="score-box">
                        <div class="score-title">🔵 Inspecteur</div>
                        <div class="score-val">{st.session_state.score_inspector} pts</div>
                    </div>
                    <div class="score-box" style="background: linear-gradient(135deg, #DC2626 0%, #EF4444 100%);">
                        <div class="score-title">🔴 Adversaire</div>
                        <div class="score-val">{st.session_state.score_adversary} pts</div>
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )
            elif app_mode == "🤖 2. Challenge vs IA":
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

            # --------------------------------------------------
            # PHASE 1 : TOUR DE L'ADVERSAIRE
            # --------------------------------------------------
            if (
                app_mode == "👥 1. Joueur vs Joueur (5 Rounds)"
                and st.session_state.pvp_phase == "adversary_turn"
            ):
                st.markdown(
                    '<div class="phase-indicator">🦹 PHASE 1 : Tour de l\'Adversaire (Rouge 🔴)</div>',
                    unsafe_allow_html=True,
                )
                st.info(
                    "Fixez en secret les coûts $c(e)$ de chaque arête avant de passer la main !"
                )

                with st.form("adversary_form"):
                    for e, (le, ue) in st.session_state.edges_data.items():
                        curr_val = st.session_state.secret_costs.get(e, le)
                        st.session_state.secret_costs[e] = round(
                            st.slider(
                                f"Coût arête ({e[0]} → {e[1]})",
                                min_value=float(le),
                                max_value=float(ue),
                                value=float(curr_val),
                                step=0.1,
                            ),
                            2,
                        )

                    if st.form_submit_button(
                        "🔒 Valider les coûts secrets & Passer la main"
                    ):
                        st.session_state.pvp_phase = "inspector_turn"
                        st.rerun()

            # --------------------------------------------------
            # PHASE 2 : TOUR DE L'INSPECTEUR / AUTRES MODES
            # --------------------------------------------------
            else:
                if app_mode == "👥 1. Joueur vs Joueur (5 Rounds)":
                    st.markdown(
                        '<div class="phase-indicator">🕵️ PHASE 2 : Tour de l\'Inspecteur (Bleu 🔵)</div>',
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
                    nx.all_simple_paths(
                        st.session_state.G, source="s", target="t"
                    )
                )
                p_str = [" → ".join(p) for p in all_p]
                c_p_str = st.selectbox(
                    "Sélectionner votre itinéraire final :", options=p_str
                )
                c_p = all_p[p_str.index(c_p_str)]

                if st.button(
                    "🚀 Valider le Trajet",
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

                    # --------------------------------------------------
                    # LOGIQUE DES POINTS CORRIGÉE
                    # --------------------------------------------------
                    if gap <= 1.5:
                        # Succès de l'Inspecteur -> Il marque, l'Adversaire gagne 0
                        gain_ins = (len(st.session_state.edges_data) - nb_ins) * 10
                        st.session_state.score_inspector += gain_ins
                        st.session_state.last_result_msg = {
                            "type": "win",
                            "text": f"🎉 Round {st.session_state.current_round} : Trajet optimal ! (+{gain_ins} pts pour l'Inspecteur 🔵, 0 pt pour l'Adversaire)",
                        }
                    else:
                        # Faute de l'Inspecteur -> L'Adversaire emporte les points du piège !
                        # Bonus de base (20 pts) + Pénalité proportionnelle à l'erreur commise
                        gain_adv = int(20 + (gap * 10))
                        st.session_state.score_adversary += gain_adv
                        st.session_state.last_result_msg = {
                            "type": "loss",
                            "text": f"🦹 Round {st.session_state.current_round} : Erreur de l'Inspecteur ! (+{gain_adv} pts attribués à l'Adversaire 🔴)",
                        }

                    # Gestion de la progression des rounds
                    if app_mode == "👥 1. Joueur vs Joueur (5 Rounds)":
                        if st.session_state.current_round >= 5:
                            st.session_state.game_over = True
                        else:
                            st.session_state.current_round += 1
                            next_setup = (
                                st.session_state.current_setup_num % 10
                            ) + 1
                            build_10_unique_setups(next_setup)
                    else:
                        next_setup = (
                            st.session_state.current_setup_num % 10
                        ) + 1
                        build_10_unique_setups(next_setup)

                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------
# 8. Réinitialisation
# --------------------------------------------------
st.divider()
c_r1, c_r2 = st.columns(2)
with c_r1:
    if st.button("🎲 Réinitialiser ce Setup", use_container_width=True):
        build_10_unique_setups(st.session_state.current_setup_num)
        st.session_state.last_result_msg = None
        st.rerun()

with c_r2:
    if st.button("🔄 Remise à Zéro du Match", use_container_width=True):
        reset_full_match()
        st.rerun()
