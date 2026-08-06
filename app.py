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
    page_title="Graph Inspection Game - Explication & Démonstration",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main-title { font-size: 2.3rem; font-weight: 800; color: #1E3A8A; text-align: center; }
    .sub-title { font-size: 1.1rem; color: #4B5563; text-align: center; margin-bottom: 25px; }
    .teacher-card { background-color: #EFF6FF; border-left: 5px solid #2563EB; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
    .algo-box { background-color: #F3F4F6; border: 1px solid #D1D5DB; padding: 15px; border-radius: 8px; font-family: monospace; }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-title">🎓 Graph Inspection Game : Simulation et Analyse Théorique</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-title">Plateforme Académique de Démonstration pour l\'Évaluation du Projet | MTYM 2026</div>',
    unsafe_allow_html=True,
)

# --------------------------------------------------
# 2. Barre Latérale & Configuration Globale
# --------------------------------------------------
st.sidebar.header("⚙️ Configuration Globale")

difficulty = st.sidebar.selectbox(
    "📊 Difficulté du Graphe (Complexité IA) :",
    [
        "🟢 Facile (Graphe Simple - 5 Nœuds)",
        "🟡 Moyen (Diamant Multi-couches - 6 Nœuds)",
        "🔴 Difficile (Réseau Complexe & Dense - 7 Nœuds)",
    ],
    help="Modifie la structure topologique du problème pour tester l'algorithme.",
)

inspection_cost_unit = st.sidebar.slider(
    "💰 Coût d'inspection par arête (C_inspect) :",
    min_value=0.5,
    max_value=4.0,
    value=1.0,
    step=0.5,
)

display_mode = st.sidebar.radio(
    "👁️ Mode d'affichage des valeurs :",
    ["📚 Vue Théorique (Coûts secrets visibles)", "🕵️ Vue Simulateur (Graphe avec incertitude)"],
    help="La Vue Théorique permet aux enseignants d'évaluer directement l'écart entre l'estimé et l'optimum secret.",
)

st.sidebar.markdown("---")

# --------------------------------------------------
# 3. Section d'Explication pour le Jury et les Enseignants
# --------------------------------------------------
with st.expander("📖 Dossier Explicatif & Résolution du Problème (À l'attention des Évaluateurs)", expanded=True):
    st.markdown("""
    <div class="teacher-card">
    <h4>💡 Présentation Académique du Modèle</h4>
    Ce projet modélise le problème classique du <b>Graph Inspection Game</b> (Optimisation sous incertitude et Théorie des Jeux).
    </div>

    #### 1. Formulations Mathématiques du Problème
    * **Structure du Réseau :** Soit un graphe orienté $G = (V, E)$ avec un sommet source $s$ et un sommet puits $t$.
    * **Incertitude sur les Arêtes :** Chaque arête $e \in E$ possède un intervalle de coût connu $[l_e, u_e]$. Le coût réel $c(e) \in [l_e, u_e]$ est initialement **inconnu**.
    * **Le Dilemme de Décision :**
      L'agent peut payer un coût fixe $C_{\\text{inspect}}$ pour révéler la valeur exacte $c(e)$ avant de choisir son itinéraire final.

    #### 2. Stratégie de Résolution & Calculs Théoriques
    * **Espérance de Coût par Défaut :** En l'absence d'inspection, le coût estimé d'une arête non révélée est sa valeur moyenne : 
      $$\\mathbb{E}[c(e)] = \\frac{l_e + u_e}{2}$$
    * **Fonction d'Objectif Global :**
      $$\\min_{\\text{Stratégie}} \\left( \\sum_{e \\in E_{\\text{inspecté}}} C_{\\text{inspect}} + \\sum_{e \\in P_{\\text{choisi}}} c(e) \\right)$$
    """)

# --------------------------------------------------
# 4. Générateur Dynamique de Réseau
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
    else:  # Difficile
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
        le = round(random.uniform(1.0, 3.0), 1)
        ue = round(le + random.uniform(2.5, 6.5), 1)
        edges_data[(u, v)] = (le, ue)
        secret_costs[(u, v)] = round(random.uniform(le, ue), 2)

    st.session_state.G = G
    st.session_state.pos = pos
    st.session_state.edges_data = edges_data
    st.session_state.secret_costs = secret_costs
    st.session_state.inspected_edges = {}
    st.session_state.history_log = []


if "G" not in st.session_state or st.session_state.get("diff_current") != difficulty:
    st.session_state.diff_current = difficulty
    generate_topology(difficulty)

# --------------------------------------------------
# 5. Outils de Conception Personnalisée de Réseau
# --------------------------------------------------
st.subheader("🛠️ Module de Conception et d'Édition du Réseau")

col_design1, col_design2 = st.columns([2, 1])
with col_design1:
    st.info("Modifiez les bornes des arêtes pour tester différents scénarios d'inspection.")
    with st.expander("⚙️ Éditeur d'Intervalles des Arêtes", expanded=False):
        for e in list(st.session_state.edges_data.keys()):
            l_curr, u_curr = st.session_state.edges_data[e]
            c1, c2 = st.columns(2)
            new_l = c1.number_input(f"Borne Inf {e}", value=float(l_curr), step=0.5, key=f"l_{e}")
            new_u = c2.number_input(f"Borne Sup {e}", value=float(u_curr), step=0.5, key=f"u_{e}")
            if new_l < new_u:
                st.session_state.edges_data[e] = (new_l, new_u)

with col_design2:
    if st.button("🎲 Régénérer une instance aléatoire", use_container_width=True, type="primary"):
        generate_topology(difficulty)
        st.rerun()

    if st.button("🔄 Réinitialiser les inspections", use_container_width=True):
        st.session_state.inspected_edges = {}
        st.session_state.history_log = []
        st.rerun()

st.divider()

# --------------------------------------------------
# 6. Moteur de Calcul (Algorithme du Plus Court Chemin)
# --------------------------------------------------
def calculate_metrics():
    # 1. Graphe théorique réel (Secret)
    real_graph = nx.DiGraph()
    for e, c in st.session_state.secret_costs.items():
        real_graph.add_edge(e[0], e[1], weight=c)

    true_opt_path = nx.shortest_path(real_graph, source="s", target="t", weight="weight")
    true_opt_cost = nx.shortest_path_length(real_graph, source="s", target="t", weight="weight")

    # 2. Graphe estimé actuel (Selon les inspections faites)
    est_graph = nx.DiGraph()
    for e, (l, u) in st.session_state.edges_data.items():
        w = st.session_state.inspected_edges[e] if e in st.session_state.inspected_edges else (l + u) / 2.0
        est_graph.add_edge(e[0], e[1], weight=w)

    est_path = nx.shortest_path(est_graph, source="s", target="t", weight="weight")
    est_cost = nx.shortest_path_length(est_graph, source="s", target="t", weight="weight")

    return true_opt_path, true_opt_cost, est_path, est_cost

true_opt_path, true_opt_cost, est_path, est_cost = calculate_metrics()

# --------------------------------------------------
# 7. Affichage Graphique du Réseau & Module d'Inspection
# --------------------------------------------------
col_graph, col_panel = st.columns([3, 2])

with col_graph:
    st.subheader("🗺️ Représentation du Graphe de Décision $G=(V, E)$")

    G = st.session_state.G
    pos = st.session_state.pos
    fig, ax = plt.subplots(figsize=(8, 5))

    path_edges = list(zip(est_path[:-1], est_path[1:]))

    # Dessin des nœuds
    nx.draw_networkx_nodes(G, pos, node_color="#2563EB", node_size=1200, ax=ax, edgecolors="black", linewidths=1.5)
    nx.draw_networkx_labels(G, pos, font_size=13, font_weight="bold", font_color="white", ax=ax)

    # Arêtes standards
    nx.draw_networkx_edges(G, pos, width=2.0, edge_color="#9CA3AF", arrowsize=18, arrowstyle="->", ax=ax)

    # Surbrillance du chemin estimé actuel
    nx.draw_networkx_edges(G, pos, edgelist=path_edges, width=3.5, edge_color="#10B981", arrowsize=22, arrowstyle="->", ax=ax)

    # Étiquettes d'arêtes
    edge_labels = {}
    for edge, (le, ue) in st.session_state.edges_data.items():
        if edge in st.session_state.inspected_edges:
            edge_labels[edge] = f"✅ Révélé: {st.session_state.inspected_edges[edge]}"
        elif "Théorique" in display_mode:
            c_sec = st.session_state.secret_costs[edge]
            edge_labels[edge] = f"[{le}, {ue}]\n(Réel: {c_sec})"
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
    st.subheader("🧮 Analyse & Simulateur d'Inspection")

    nb_inspected = len(st.session_state.inspected_edges)
    total_inspect_cost = nb_inspected * inspection_cost_unit

    st.metric("Nombre d'inspections réalisées", f"{nb_inspected}")
    st.metric("Coût d'inspection cumulé", f"{total_inspect_cost:.1f}")
    st.markdown(f"**Chemin optimal estimé :** `{' → '.join(est_path)}` (Coût estimé = `{est_cost:.2f}`)")

    available_edges = [e for e in st.session_state.edges_data.keys() if e not in st.session_state.inspected_edges]

    if available_edges:
        selected_edge = st.selectbox(
            "Sélectionner une arête à inspecter :",
            options=available_edges,
            format_func=lambda x: f"Inspecter ({x[0]} → {x[1]}) [Bornes: {st.session_state.edges_data[x]}]",
        )

        if st.button("🔍 Exécuter l'inspection théorique", use_container_width=True, type="primary"):
            val = st.session_state.secret_costs[selected_edge]
            st.session_state.inspected_edges[selected_edge] = val
            st.session_state.history_log.append(f"Inspection de ({selected_edge[0]} → {selected_edge[1]}) : Coût réel révélé = {val}")
            st.rerun()

    st.markdown("---")
    st.subheader("📊 Comparatif de Résolution (Section Enseignant)")

    # Coût réel du chemin estimé actuellement
    real_cost_of_est_path = sum(st.session_state.secret_costs[e] for e in path_edges)
    total_score = real_cost_of_est_path + total_inspect_cost

    st.write(f"• **Vrai plus court chemin théorique :** `{' → '.join(true_opt_path)}`")
    st.write(f"• **Coût minimal absolu (Sans inspection) :** `{true_opt_cost:.2f}`")
    st.write(f"• **Coût réel du chemin sélectionné :** `{real_cost_of_est_path:.2f}`")
    st.write(f"• **Cout Total Final (Chemin + Inspections) :** `{total_score:.2f}`")

# --------------------------------------------------
# 8. Journal des Opérations Théoriques
# --------------------------------------------------
st.divider()
st.subheader("📜 Historique des Inspections Séquentielles")
if st.session_state.history_log:
    for entry in reversed(st.session_state.history_log):
        st.write(f"• {entry}")
else:
    st.info("Aucune inspection n'a encore été effectuée dans cette session d'étude.")
