import matplotlib

matplotlib.use("Agg")

import random
import matplotlib.pyplot as plt
import networkx as nx
import streamlit as st

# --------------------------------------------------
# 1. Configuration de la page
# --------------------------------------------------
st.set_page_config(
    page_title="Jeu de l'Inspecteur - Simulation MTYM 2026", layout="wide"
)

st.title("🕵️‍♂️ Le Jeu de l'Inspecteur sur un Graphe")
st.caption("Simulation interactive & Modélisation de la théorie des jeux")

# --------------------------------------------------
# 2. Manuel d'instructions & Définition du Problème
# --------------------------------------------------
with st.expander("📖 Concept et Règles du Jeu (Notice Théorique)", expanded=False):
    st.markdown("""
    ### 🎯 Modèle du Jeu (Graph Inspection Game)
    On considère un graphe orienté/non-orienté $G = (V, E)$ avec un sommet source **s** et un sommet puits **t**.
    
    * **Les Intervalle de Coût :** Pour chaque arête $e \in E$, le coût réel $c(e)$ est inconnu au départ, mais appartient à un intervalle connu $[l_e, u_e]$.
    * **Le Rôle de l'Inspecteur :** Vous pouvez choisir d'inspecter certaines arêtes pour révéler leur coût exact $c(e)$, moyennant un coût de test/inspection.
    * **L'Objectif :** Trouver une stratégie d'inspection qui minimise le coût total :
      $$\text{Coût Total} = \text{Nombre d'inspections} \times \text{Coût d'inspection} + \text{Longueur du plus court chemin } s \to t$$
    """)

# --------------------------------------------------
# 3. Génération du Graphe et de l'État
# --------------------------------------------------


def generate_level():
    # Graphe fixe et bien structuré pour garantir une topologie propre sans croisement
    G = nx.DiGraph()

    # Structure en couches claire de s à t
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

    random.seed()
    for u, v in G.edges():
        le = round(random.uniform(1.0, 3.0), 1)
        ue = round(le + random.uniform(2.0, 5.0), 1)
        edges_data[(u, v)] = (le, ue)
        # Coût réel tiré dans l'intervalle [le, ue]
        secret_costs[(u, v)] = round(random.uniform(le, ue), 2)

    st.session_state.G = G
    st.session_state.edges_data = edges_data
    st.session_state.secret_costs = secret_costs
    st.session_state.inspected_edges = {}
    st.session_state.inspection_cost_per_edge = 1.0


if "G" not in st.session_state:
    generate_level()

# --------------------------------------------------
# 4. Commandes Principales
# --------------------------------------------------
col1, col2 = st.columns(2)
with col1:
    if st.button("🎲 Générer une nouvelle instance", use_container_width=True):
        generate_level()
        st.rerun()

with col2:
    if st.button("🔄 Réinitialiser l'inspection", use_container_width=True):
        st.session_state.inspected_edges = {}
        st.rerun()

st.divider()

# --------------------------------------------------
# 5. Affichage du Graphe & Panneau d'action
# --------------------------------------------------
col_graph, col_control = st.columns([3, 2])

with col_graph:
    st.subheader("🗺️ Représentation du Réseau")

    G = st.session_state.G
    fig, ax = plt.subplots(figsize=(8, 5))

    # Disposition manuelle (Layout) pour une lisibilité parfaite sans chevauchement
    pos = {
        "s": (0, 0.5),
        "a": (1, 1.0),
        "b": (1, 0.0),
        "c": (2, 0.5),
        "t": (3, 0.5),
    }

    nx.draw_networkx_nodes(
        G,
        pos,
        node_color="#2ECC71",
        node_size=1000,
        ax=ax,
        edgecolors="black",
    )
    nx.draw_networkx_labels(
        G, pos, font_size=14, font_weight="bold", font_color="white", ax=ax
    )

    # Dessiner les flèches
    nx.draw_networkx_edges(
        G,
        pos,
        width=2.5,
        edge_color="#34495E",
        arrowsize=20,
        arrowstyle="->",
        ax=ax,
    )

    # Étiquettes d'arêtes
    edge_labels = {}
    for edge, (le, ue) in st.session_state.edges_data.items():
        if edge in st.session_state.inspected_edges:
            edge_labels[edge] = f"r = {st.session_state.inspected_edges[edge]}"
        else:
            edge_labels[edge] = f"[{le}, {ue}]"

    nx.draw_networkx_edge_labels(
        G, pos, edge_labels=edge_labels, font_size=10, rotate=False, ax=ax
    )

    plt.axis("off")
    st.pyplot(fig)

with col_control:
    st.subheader("⚙️ Actions de l'Inspecteur")

    available_edges = [
        e
        for e in st.session_state.edges_data.keys()
        if e not in st.session_state.inspected_edges
    ]

    if available_edges:
        selected_edge = st.selectbox(
            "Arête à inspecter :",
            options=available_edges,
            format_func=lambda x: f"Arête ({x[0]} → {x[1]})",
        )

        if st.button("Inspecter cette arête 🕵️", use_container_width=True):
            val = st.session_state.secret_costs[selected_edge]
            st.session_state.inspected_edges[selected_edge] = val
            st.rerun()
    else:
        st.info("Toutes les arêtes ont été inspectées !")

    st.markdown("---")
    st.subheader("📊 Évaluation de la Stratégie")

    num_inspections = len(st.session_state.inspected_edges)
    st.write(f"• **Arêtes inspectées :** {num_inspections} / {len(G.edges())}")

    # Calcul du plus court chemin selon les valeurs actuelles (estimées ou révélées)
    weight_graph = nx.DiGraph()
    for (u, v), (le, ue) in st.session_state.edges_data.items():
        if (u, v) in st.session_state.inspected_edges:
            w = st.session_state.inspected_edges[(u, v)]
        else:
            w = (le + ue) / 2.0  # Valeur attendue / Pire cas selon le scénario
        weight_graph.add_edge(u, v, weight=w)

    shortest_path = nx.shortest_path(
        weight_graph, source="s", target="t", weight="weight"
    )
    path_cost = nx.shortest_path_length(
        weight_graph, source="s", target="t", weight="weight"
    )

    st.write(
        f"• **Plus court chemin estimé ($s \\to t$) :** `{' → '.join(shortest_path)}`"
    )
    st.write(f"• **Coût du chemin :** `{path_cost:.2f}`")

    if st.button("🏆 Calculer le Coût Réel Final", type="primary"):
        # Calcul du vrai plus court chemin avec TOUTES les valeurs réelles
        real_graph = nx.DiGraph()
        for e, c in st.session_state.secret_costs.items():
            real_graph.add_edge(e[0], e[1], weight=c)

        real_path = nx.shortest_path(
            real_graph, source="s", target="t", weight="weight"
        )
        real_cost = nx.shortest_path_length(
            real_graph, source="s", target="t", weight="weight"
        )

        st.success(f"""
        **Résultat Final du Jeu :**
        - Plus court chemin réel : `{' → '.join(real_path)}`
        - Longueur réelle : `{real_cost:.2f}`
        - Coût total de votre stratégie : `{real_cost + num_inspections * 1.0:.2f}`
        """)
