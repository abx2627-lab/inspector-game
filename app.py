import matplotlib

matplotlib.use("Agg")

import random
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import streamlit as st

# --------------------------------------------------
# 1. Configuration de la page
# --------------------------------------------------
st.set_page_config(
    page_title="Inspector's Game - Dashboard Séquentiel",
    page_icon="🕵️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Style CSS personnalise pour ameliorer l'UI
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        text-align: center;
        color: #7f8c8d;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #1E88E5;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-header">🕵️‍♂️ Inspection Game Platform (Graph Theory & AI)</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-header">Simulation dynamique séquentielle : Inspecteur vs. Adversaire Stratégique | MTYM 2026</div>',
    unsafe_allow_html=True,
)

# --------------------------------------------------
# 2. Configuration dans la Barre Latérale (Sidebar)
# --------------------------------------------------
st.sidebar.header("⚙️ Configuration de la Partie")

# Choix de la strategie de l'Adversaire
adversary_mode = st.sidebar.selectbox(
    "🦹 Stratégie de l'Adversaire :",
    [
        "Pire des Cas / Piège (Worst-Case)",
        "Équilibré (Moyenne + Variance)",
        "Aléatoire (Random)",
    ],
    help="Définit comment l'Adversaire choisit le coût secret dans l'intervalle [l_e, u_e]",
)

inspection_cost_param = st.sidebar.slider(
    "💰 Coût unitaire d'inspection (C_inspect) :",
    min_value=0.5,
    max_value=3.0,
    value=1.0,
    step=0.5,
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📖 Guide Rapide")
st.sidebar.info("""
- **Objectif :** Trouver le chemin $s \\to t$ en minimisant la somme du coût du chemin et des frais d'inspection.
- **Principe Séquentiel :** Inspectez une arête à la fois. Observez si la décision modifie l'itinéraire optimal.
""")

# --------------------------------------------------
# 3. Moteur du Jeu et Génération d'Instance
# --------------------------------------------------


def init_game_instance():
    G = nx.DiGraph()
    # Graphe a structure claire en couches (sans croisement d'aretes)
    edges = [
        ("s", "a"),
        ("s", "b"),
        ("a", "c"),
        ("b", "c"),
        ("a", "t"),
        ("b", "t"),
        ("c", "t"),
    ]
    G.add_edges_from(edges)

    edges_data = {}
    secret_costs = {}

    for u, v in G.edges():
        le = round(random.uniform(1.0, 3.0), 1)
        ue = round(le + random.uniform(2.5, 6.0), 1)
        edges_data[(u, v)] = (le, ue)

        # Attribution des couts secrets selon l'Adversaire selectionne
        if "Worst-Case" in adversary_mode:
            c_secret = round(
                ue if random.random() > 0.3 else (le + ue) / 2, 2
            )
        elif "Équilibré" in adversary_mode:
            c_secret = round(random.triangular(le, ue, (le + ue) / 2), 2)
        else:
            c_secret = round(random.uniform(le, ue), 2)

        secret_costs[(u, v)] = c_secret

    st.session_state.G = G
    st.session_state.edges_data = edges_data
    st.session_state.secret_costs = secret_costs
    st.session_state.inspected_edges = {}
    st.session_state.history_log = []
    st.session_state.inspector_score = 0
    st.session_state.adversary_score = 0
    st.session_state.cost_history = []


if "G" not in st.session_state:
    init_game_instance()

# --------------------------------------------------
# 4. Commandes et Actions Principales
# --------------------------------------------------
col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    if st.button(
        "🎲 Générer une nouvelle instance du réseau",
        use_container_width=True,
        type="primary",
    ):
        init_game_instance()
        st.rerun()

with col_btn2:
    if st.button("🔄 Réinitialiser les inspections", use_container_width=True):
        st.session_state.inspected_edges = {}
        st.session_state.history_log = []
        st.session_state.inspector_score = 0
        st.session_state.adversary_score = 0
        st.session_state.cost_history = []
        st.rerun()

st.divider()

# --------------------------------------------------
# 5. Calculs des Chemins Optimaux
# --------------------------------------------------


def compute_shortest_path():
    g_temp = nx.DiGraph()
    for e, (l, u) in st.session_state.edges_data.items():
        w = (
            st.session_state.inspected_edges[e]
            if e in st.session_state.inspected_edges
            else (l + u) / 2.0
        )
        g_temp.add_edge(e[0], e[1], weight=w)

    path = nx.shortest_path(g_temp, source="s", target="t", weight="weight")
    cost = nx.shortest_path_length(
        g_temp, source="s", target="t", weight="weight"
    )
    return path, cost, g_temp


path_current, cost_current, g_current = compute_shortest_path()

# --------------------------------------------------
# 6. Affichage du Graphe & Panneau Interactif
# --------------------------------------------------
col_graph, col_panel = st.columns([3, 2])

with col_graph:
    st.subheader("🗺️ Représentation du Réseau & Chemin Optimal")

    G = st.session_state.G
    fig, ax = plt.subplots(figsize=(8, 5))

    pos = {
        "s": (0, 0.5),
        "a": (1, 1.0),
        "b": (1, 0.0),
        "c": (2, 0.5),
        "t": (3, 0.5),
    }

    # Preparation des aretes du chemin actuel pour mise en relief
    path_edges = list(zip(path_current[:-1], path_current[1:]))

    # Dessiner les sommets
    nx.draw_networkx_nodes(
        G,
        pos,
        node_color="#2ECC71",
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

    # Dessiner toutes les aretes
    nx.draw_networkx_edges(
        G,
        pos,
        width=2,
        edge_color="#BDC3C7",
        arrowsize=18,
        arrowstyle="->",
        ax=ax,
    )

    # Mettre en surbrillance verte les aretes du chemin actuel
    nx.draw_networkx_edges(
        G,
        pos,
        edgelist=path_edges,
        width=4,
        edge_color="#27AE60",
        arrowsize=20,
        arrowstyle="->",
        ax=ax,
    )

    # Etiquettes d'aretes
    edge_labels = {}
    for edge, (le, ue) in st.session_state.edges_data.items():
        if edge in st.session_state.inspected_edges:
            edge_labels[edge] = (
                f"Révélé: {st.session_state.inspected_edges[edge]}"
            )
        else:
            edge_labels[edge] = f"[{le}, {ue}]"

    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=edge_labels,
        font_size=9,
        rotate=False,
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.9),
        ax=ax,
    )

    plt.axis("off")
    st.pyplot(fig)

with col_panel:
    st.subheader("⚔️ Actions & Séquence")

    # Tableau de bord des metriques
    m1, m2 = st.columns(2)
    m1.metric("Inspections Réalisées", len(st.session_state.inspected_edges))
    m2.metric(
        "Frais d'inspection",
        f"{len(st.session_state.inspected_edges) * inspection_cost_param:.1f}",
    )

    st.markdown(
        f"**Chemin estimé actuel :** `{' → '.join(path_current)}` | Coût = `{cost_current:.2f}`"
    )

    available_edges = [
        e
        for e in st.session_state.edges_data.keys()
        if e not in st.session_state.inspected_edges
    ]

    if available_edges:
        selected_edge = st.selectbox(
            "Étape suivante : Choisir l'arête à inspecter :",
            options=available_edges,
            format_func=lambda x: f"Inspecter ({x[0]} → {x[1]})",
        )

        if st.button(
            "Exécuter l'inspection 🔍",
            use_container_width=True,
            type="primary",
        ):
            val = st.session_state.secret_costs[selected_edge]
            st.session_state.inspected_edges[selected_edge] = val

            # Calcul du nouveau chemin
            path_next, cost_next, _ = compute_shortest_path()

            # Analyse de la pertinence de l'inspection
            if path_current != path_next:
                msg = f"🎉 **Succès !** L'inspection de ({selected_edge[0]} → {selected_edge[1]}) = {val} a permis de modifier l'itinéraire optimal !"
                st.session_state.inspector_score += 1
                status = "success"
            else:
                msg = f"⚠️ **Inspection Inutile !** ({selected_edge[0]} → {selected_edge[1]}) = {val} n'a pas changé le chemin le plus court. Vous avez perdu {inspection_cost_param} en frais !"
                st.session_state.adversary_score += 1
                status = "warning"

            st.session_state.history_log.append((status, msg))
            st.session_state.cost_history.append(
                cost_next
                + (
                    len(st.session_state.inspected_edges)
                    * inspection_cost_param
                )
            )
            st.rerun()
    else:
        st.success("Toutes les arêtes ont été inspectées !")

    # Display des scores
    sc1, sc2 = st.columns(2)
    sc1.metric("Score Inspecteur 🕵️", st.session_state.inspector_score)
    sc2.metric("Pénalités Adversaire 🦹", st.session_state.adversary_score)

# --------------------------------------------------
# 7. Section d'Analyse Séquentielle & Graphiques (Bottom Area)
# --------------------------------------------------
st.divider()

col_hist, col_chart = st.columns([1, 1])

with col_hist:
    st.subheader("📜 Historique des Décisions")
    if st.session_state.history_log:
        for status, log in reversed(st.session_state.history_log):
            if status == "success":
                st.success(log)
            else:
                st.warning(log)
    else:
        st.info("Aucune inspection réalisée dans cette séquence pour le moment.")

with col_chart:
    st.subheader("📈 Évolution du Coût Total de la Stratégie")
    if st.session_state.cost_history:
        fig_chart, ax_chart = plt.subplots(figsize=(6, 3))
        ax_chart.plot(
            range(1, len(st.session_state.cost_history) + 1),
            st.session_state.cost_history,
            marker="o",
            color="#1E88E5",
            linewidth=2,
        )
        ax_chart.set_xlabel("Étape d'inspection")
        ax_chart.set_ylabel("Coût Total Estimé")
        ax_chart.grid(True, linestyle="--", alpha=0.6)
        st.pyplot(fig_chart)
    else:
        st.info(
            "Le graphique d'évolution du coût s'affichera après votre première inspection."
        )
