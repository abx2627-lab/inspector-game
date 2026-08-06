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
    page_title="Graph Inspection Game - Simulator & Challenge",
    page_icon="🕵️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS pour embellir l'interface
st.markdown(
    """
    <style>
    .main-title { font-size: 2.4rem; font-weight: 800; color: #1E3A8A; text-align: center; margin-bottom: 5px; }
    .sub-title { font-size: 1.1rem; color: #4B5563; text-align: center; margin-bottom: 25px; }
    .card { background-color: #F3F4F6; padding: 15px; border-radius: 10px; border-left: 5px solid #2563EB; margin-bottom: 15px; }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-title">🕵️‍♂️ Le Jeu de l\'Inspecteur (Graph Inspection Challenge)</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-title">Plateforme Interactive de Théorie des Jeux & Optimisation sous Incertitude | MTYM 2026</div>',
    unsafe_allow_html=True,
)

# --------------------------------------------------
# 2. Barre Latérale & Paramétrage
# --------------------------------------------------
st.sidebar.header("⚙️ Configuration du Jeu")

game_mode = st.sidebar.radio(
    "🎯 Mode de Jeu :",
    ["⚔️ Mode Challenge (Brouillard de Guerre)", "📚 Mode Apprentissage (Démo)"],
    help="En Mode Challenge, les coûts secrets et le chemin optimal restent cachés jusqu'à la fin !",
)

difficulty = st.sidebar.selectbox(
    "📊 Topologie du Network :",
    [
        "🟢 Facile (Réseau Linéaire - 5 Nœuds)",
        "🟡 Moyen (Diamant Multi-couches - 6 Nœuds)",
        "🔴 Difficile (Réseau Dense & Complexe - 7 Nœuds)",
    ],
)

inspection_cost_unit = st.sidebar.slider(
    "💰 Coût d'inspection par arête (C_inspect) :",
    min_value=0.5,
    max_value=4.0,
    value=1.0,
    step=0.5,
)

st.sidebar.markdown("---")

# --------------------------------------------------
# 3. Manuel Théorique & Guide d'Utilisation
# --------------------------------------------------
with st.expander("📖 Manuel d'Instructions & Concept Théorique", expanded=False):
    st.markdown("""
    ### 🎓 Principes du Graph Inspection Game
    Dans ce problème d'optimisation sous incertitude, un **Inspecteur** doit voyager de la source $s$ au puits $t$.
    
    #### 1. Rôles et Règles :
    * **Les Arêtes $e \in E$ :** Ont un coût incertain compris dans l'intervalle $[l_e, u_e]$.
    * **L'Inspection :** Vous pouvez payer un coût $C_{\\text{inspect}}$ pour révéler le coût exact $c(e)$ d'une arête.
    * **Le Dilemme :** Inspecter trop d'arêtes augmente inutilement les frais. Ne pas inspecter risque de vous faire emprunter un chemin très coûteux !
    
    #### 2. Calcul du Score Final :
    $$\\text{Score Final} = \\text{Coût Réel du Chemin Emprunté} + (\\text{Nombre d'Inspections} \\times C_{\\text{inspect}})$$
    """)

# --------------------------------------------------
# 4. Génération Dynamique des Topologies de Graphe
# --------------------------------------------------


def generate_topology(diff):
    G = nx.DiGraph()

    if "Facile" in diff:
        edges = [("s", "a"), ("s", "b"), ("a", "t"), ("b", "t"), ("a", "b")]
        pos = {"s": (0, 0.5), "a": (1, 1.0), "b": (1, 0.0), "t": (2, 0.5)}
    elif "Moyen" in diff:
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
    else:
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

    G.add_edges_from(edges)
    edges_data = {}
    secret_costs = {}

    random.seed()
    for u, v in G.edges():
        le = round(random.uniform(1.0, 3.5), 1)
        ue = round(le + random.uniform(2.0, 7.5), 1)
        edges_data[(u, v)] = (le, ue)
        secret_costs[(u, v)] = round(random.uniform(le, ue), 2)

    st.session_state.G = G
    st.session_state.pos = pos
    st.session_state.edges_data = edges_data
    st.session_state.secret_costs = secret_costs
    st.session_state.inspected_edges = {}
    st.session_state.history_log = []
    st.session_state.game_over = False


if "G" not in st.session_state or st.session_state.get("diff_current") != difficulty:
    st.session_state.diff_current = difficulty
    generate_topology(difficulty)

# --------------------------------------------------
# 5. Commandes Principales
# --------------------------------------------------
col_b1, col_b2, col_b3 = st.columns([2, 2, 1])
with col_b1:
    if st.button(
        "🎲 Générer un Nouveau Problème",
        use_container_width=True,
        type="primary",
    ):
        generate_topology(difficulty)
        st.rerun()

with col_b2:
    if st.button("🔄 Réinitialiser la Séquence", use_container_width=True):
        st.session_state.inspected_edges = {}
        st.session_state.history_log = []
        st.session_state.game_over = False
        st.rerun()

with col_b3:
    st.metric(
        "Arêtes Révélées",
        f"{len(st.session_state.inspected_edges)} / {len(st.session_state.edges_data)}",
    )

st.divider()

# --------------------------------------------------
# 6. Calculs du Chemin Estimé et de l'Incertitude
# --------------------------------------------------


def get_estimated_graph():
    g_temp = nx.DiGraph()
    for e, (l, u) in st.session_state.edges_data.items():
        w = (
            st.session_state.inspected_edges[e]
            if e in st.session_state.inspected_edges
            else (l + u) / 2.0
        )
        g_temp.add_edge(e[0], e[1], weight=w)
    return g_temp


g_est = get_estimated_graph()
est_path = nx.shortest_path(g_est, source="s", target="t", weight="weight")
est_cost = nx.shortest_path_length(g_est, source="s", target="t", weight="weight")

# Taux de certitude
total_edges_count = len(st.session_state.edges_data)
inspected_count = len(st.session_state.inspected_edges)
certainty_ratio = (
    inspected_count / total_edges_count if total_edges_count > 0 else 0
)

# --------------------------------------------------
# 7. Rendu Visuel du Graphe et Panneau
# --------------------------------------------------
col_graph, col_panel = st.columns([3, 2])

with col_graph:
    st.subheader("🗺️ Vision du Réseau")

    G = st.session_state.G
    pos = st.session_state.pos
    fig, ax = plt.subplots(figsize=(8, 5.2))

    path_edges = list(zip(est_path[:-1], est_path[1:]))

    # Dessin des Sommets
    nx.draw_networkx_nodes(
        G,
        pos,
        node_color="#10B981",
        node_size=1200,
        ax=ax,
        edgecolors="black",
        linewidths=1.5,
    )
    nx.draw_networkx_labels(
        G,
        pos,
        font_size=13,
        font_weight="bold",
        font_color="white",
        font_family="sans-serif",
        ax=ax,
    )

    # Arêtes Générales
    nx.draw_networkx_edges(
        G,
        pos,
        width=2.0,
        edge_color="#9CA3AF",
        arrowsize=18,
        arrowstyle="->",
        ax=ax,
    )

    # Arêtes du Chemin Estimé en Surbrillance
    nx.draw_networkx_edges(
        G,
        pos,
        edgelist=path_edges,
        width=4.0,
        edge_color="#2563EB",
        arrowsize=22,
        arrowstyle="->",
        ax=ax,
    )

    # Etiquettes sur les Arêtes
    edge_labels = {}
    for edge, (le, ue) in st.session_state.edges_data.items():
        if edge in st.session_state.inspected_edges:
            edge_labels[edge] = (
                f"✅ Révélé: {st.session_state.inspected_edges[edge]}"
            )
        elif "Apprentissage" in game_mode:
            c_sec = st.session_state.secret_costs[edge]
            edge_labels[edge] = f"[{le}, {ue}]\n(Secret: {c_sec})"
        else:
            edge_labels[edge] = f"[{le}, {ue}]"

    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=edge_labels,
        font_size=9,
        rotate=False,
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#6B7280", alpha=0.95),
        ax=ax,
    )

    plt.axis("off")
    st.pyplot(fig)

with col_panel:
    st.subheader("🕵️ Actions de l'Inspecteur")

    st.progress(
        certainty_ratio, text=f"Niveau de Certitude du Réseau : {certainty_ratio * 100:.1f}%"
    )

    nb_inspected = len(st.session_state.inspected_edges)
    total_inspection_cost = nb_inspected * inspection_cost_unit

    p1, p2 = st.columns(2)
    p1.metric("Frais d'Inspection", f"{total_inspection_cost:.1f}")
    p2.metric("Longueur Estimée", f"{est_cost:.2f}")

    st.markdown(f"**Itinéraire Recommandé :** `{' → '.join(est_path)}`")

    available_edges = [
        e
        for e in st.session_state.edges_data.keys()
        if e not in st.session_state.inspected_edges
    ]

    if available_edges and not st.session_state.game_over:
        selected_edge = st.selectbox(
            "Sélectionnez une arête à inspecter :",
            options=available_edges,
            format_func=lambda x: f"Inspecter ({x[0]} → {x[1]}) [Bornes: {st.session_state.edges_data[x]}]",
        )

        l_sel, u_sel = st.session_state.edges_data[selected_edge]
        variance_sel = (u_sel - l_sel) ** 2 / 12.0
        st.caption(
            f"💡 **Indice de Priorité (Variance) :** `{variance_sel:.2f}` "
            + ("🔥 Élevée" if variance_sel > 1.5 else "💤 Faible")
        )

        if st.button(
            "Inspecter cette arête 🔍", use_container_width=True, type="primary"
        ):
            val = st.session_state.secret_costs[selected_edge]
            st.session_state.inspected_edges[selected_edge] = val
            st.session_state.history_log.append(
                f"Inspection de ({selected_edge[0]} → {selected_edge[1]}) : Coût réel révélé = {val}"
            )
            st.rerun()
    elif st.session_state.game_over:
        st.warning("Partie terminée ! Lancez un nouveau problème pour continuer.")

    st.markdown("---")

    if st.button(
        "🏁 Valider l'Itinéraire Final & Clôturer",
        type="primary",
        use_container_width=True,
    ):
        st.session_state.game_over = True

        real_graph = nx.DiGraph()
        for e, c in st.session_state.secret_costs.items():
            real_graph.add_edge(e[0], e[1], weight=c)

        true_path = nx.shortest_path(
            real_graph, source="s", target="t", weight="weight"
        )
        true_cost = nx.shortest_path_length(
            real_graph, source="s", target="t", weight="weight"
        )

        player_path_real_cost = sum(
            st.session_state.secret_costs[e]
            for e in zip(est_path[:-1], est_path[1:])
        )
        score_total = player_path_real_cost + total_inspection_cost

        gap = score_total - true_cost
        if gap <= 0.5:
            rank = "🎖️ Grand Maître de l'Inspection (Parfait !)"
        elif gap <= 2.5:
            rank = "🥇 Inspecteur Stratège Émérite"
        elif gap <= 5.0:
            rank = "🥈 Inspecteur Prudent"
        else:
            rank = "🥉 Inspecteur Inefficace (Surcoût élevé)"

        st.success(f"""
        ### 📊 Rapport d'Évaluation Final :
        - **Rang obtenu :** {rank}
        - **Itinéraire Emprunté :** `{' → '.join(est_path)}`
        - **Longueur Réelle du Chemin :** `{player_path_real_cost:.2f}`
        - **Vrai Chemin Optimal :** `{' → '.join(true_path)}` (Coût Réel = `{true_cost:.2f}`)
        - **SCORE TOTAL (Chemin + Inspections) :** `{score_total:.2f}`
        """)

# --------------------------------------------------
# 8. Historique des Actions
# --------------------------------------------------
st.divider()
st.subheader("📜 Historique de la Séquence")
if st.session_state.history_log:
    for item in reversed(st.session_state.history_log):
        st.write(f"• {item}")
else:
    st.info("Aucune inspection réalisée dans la séquence actuelle.")
