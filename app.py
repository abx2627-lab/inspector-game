import matplotlib

matplotlib.use("Agg")  # Éviter les erreurs d'interface graphique sur le serveur

import random
import matplotlib.pyplot as plt
import networkx as nx
import streamlit as st

# --------------------------------------------------
# 1. Configuration de la page
# --------------------------------------------------
st.set_page_config(
    page_title="Jeu de l'Inspecteur - Graph Inspection Game", layout="wide"
)

st.title("🕵️‍♂️ Le Jeu de l'Inspecteur (Graph Inspection)")
st.caption("Simulation interactive de théorie des graphes | MTYM 2026")

# --------------------------------------------------
# 2. Guide d'utilisation / Manuel d'instructions
# --------------------------------------------------
with st.expander("📖 Manuel d'instructions & Règles du jeu", expanded=False):
    st.markdown("""
    ### 🎯 Objectif du jeu
    Vous êtes un inspecteur chargé de découvrir les coûts cachés des arêtes dans un réseau (graphe) reliant un point de départ **s** à une destination **t**.

    ### 🕹️ Comment jouer ?
    1. **Observer le réseau :** Chaque arête possède un intervalle de coût initial `[Min, Max]`.
    2. **Inspecter une arête :** Sélectionnez une arête dans le menu déroulant et cliquez sur **"Inspecter l'arête 🕵️"**.
    3. **Condition de succès/échec :**
       * 🟢 **Succès :** Si le coût réel découvert est **inférieur ou égal au coût moyen** prévu pour cette arête, l'inspection est réussie ! Vous passez automatiquement au niveau suivant (génération d'une nouvelle carte).
       * 🔴 **Échec :** Si le coût réel s'avère **supérieur au coût moyen**, l'inspection échoue. Vous devrez retenter votre chance sur le même niveau ou réinitialiser.
    4. **Boutons de contrôle :**
       * **🎲 Nouveau niveau aléatoire :** Génère un tout nouveau réseau avec des nœuds bien espacés.
       * **🔄 Réinitialiser le niveau :** Recommence la partie sur le même réseau actuel.
    """)

# --------------------------------------------------
# 3. Gestion de l'état de la session (Session State)
# --------------------------------------------------


def generate_new_level():
    """Générer un nouveau niveau aléatoire avec un positionnement clair des nœuds"""
    num_nodes = random.randint(4, 6)

    # Créer un graphe orienté/non-orienté connexe
    G = nx.erdos_renyi_graph(n=num_nodes, p=0.6, seed=random.randint(1, 10000))
    while not nx.is_connected(G):
        G = nx.erdos_renyi_graph(
            n=num_nodes, p=0.6, seed=random.randint(1, 10000)
        )

    # Renommer les nœuds
    mapping = {0: "s", num_nodes - 1: "t"}
    alphabet = "abcdefghijklmn"
    idx = 0
    for node in list(G.nodes()):
        if node not in mapping:
            mapping[node] = alphabet[idx]
            idx += 1
    G = nx.relabel_nodes(G, mapping)

    # Générer les données d'arêtes (intervalles et coûts secrets)
    edges_data = {}
    secret_costs = {}
    for u, v in G.edges():
        le = round(random.uniform(1.0, 3.0), 1)
        ue = round(le + random.uniform(2.0, 5.0), 1)

        # Standardiser la clé de l'arête pour éviter les erreurs de correspondance
        edge_key = tuple(sorted([str(u), str(v)]))
        edges_data[edge_key] = (le, ue)
        secret_costs[edge_key] = round(random.uniform(le, ue), 2)

    st.session_state.G = G
    st.session_state.edges_data = edges_data
    st.session_state.secret_costs = secret_costs
    st.session_state.inspected_edges = {}
    st.session_state.last_result = None
    st.session_state.attempts = 0


if "G" not in st.session_state:
    generate_new_level()

# --------------------------------------------------
# 4. Commandes principales (Boutons)
# --------------------------------------------------
col_ctrl1, col_ctrl2 = st.columns(2)

with col_ctrl1:
    if st.button(
        "🎲 Nouveau niveau aléatoire", use_container_width=True, type="primary"
    ):
        generate_new_level()
        st.rerun()

with col_ctrl2:
    if st.button("🔄 Réinitialiser ce niveau", use_container_width=True):
        st.session_state.inspected_edges = {}
        st.session_state.last_result = None
        st.session_state.attempts = 0
        st.rerun()

st.divider()

# --------------------------------------------------
# 5. Affichage du Graphe et des Actions
# --------------------------------------------------
col_graph, col_actions = st.columns([3, 2])

with col_graph:
    st.subheader("🗺️ Carte du réseau")

    G = st.session_state.G
    fig, ax = plt.subplots(figsize=(7, 5))

    # Disposition avec espacement accru pour éviter le chevauchement des arêtes
    pos = nx.spring_layout(G, k=1.2, seed=42)

    # Dessiner les nœuds et arêtes
    nx.draw_networkx_nodes(
        G,
        pos,
        node_color="#4A90E2",
        node_size=800,
        ax=ax,
        edgecolors="black",
        linewidths=1.5,
    )
    nx.draw_networkx_labels(
        G,
        pos,
        font_size=12,
        font_weight="bold",
        font_color="white",
        font_family="sans-serif",
        ax=ax,
    )
    nx.draw_networkx_edges(G, pos, width=2, edge_color="#7F8C8D", ax=ax)

    # Étiquettes des coûts sur les arêtes
    labels = {}
    for (u, v), (le, ue) in st.session_state.edges_data.items():
        edge_key = tuple(sorted([str(u), str(v)]))
        if edge_key in st.session_state.inspected_edges:
            labels[(u, v)] = f"Coût: {st.session_state.inspected_edges[edge_key]}"
        else:
            labels[(u, v)] = f"[{le}, {ue}]"

    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=labels,
        font_size=9,
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8),
        ax=ax,
    )

    plt.axis("off")
    st.pyplot(fig)

with col_actions:
    st.subheader("🔍 Panneau d'Inspection")

    # Affichage du dernier résultat s'il existe
    if st.session_state.last_result:
        res_type, res_msg = st.session_state.last_result
        if res_type == "success":
            st.success(res_msg)
        else:
            st.error(res_msg)

    # Liste déroulante des arêtes
    edge_options = list(st.session_state.edges_data.keys())
    selected_edge = st.selectbox(
        "Choisissez l'arête à inspecter :",
        options=edge_options,
        format_func=lambda x: f"Arête ({x[0]} ↔ {x[1]})",
    )

    # Bouton d'inspection avec vérification de succès/échec
    if st.button("Inspecter l'arête 🕵️", use_container_width=True):
        st.session_state.attempts += 1
        secret_cost = st.session_state.secret_costs[selected_edge]
        le, ue = st.session_state.edges_data[selected_edge]
        avg_cost = (le + ue) / 2.0

        st.session_state.inspected_edges[selected_edge] = secret_cost

        # Logique de décision : Succès ou Échec
        if secret_cost <= avg_cost:
            st.session_state.last_result = (
                "success",
                f"🎉 **Inspection réussie !** Le coût découvert pour ({selected_edge[0]} ↔ {selected_edge[1]}) est de {secret_cost} (≤ moyenne {avg_cost:.1f}). Un nouveau niveau aléatoire a été généré !",
            )
            generate_new_level()
        else:
            st.session_state.last_result = (
                "error",
                f"❌ **Inspection échouée !** Le coût découvert pour ({selected_edge[0]} ↔ {selected_edge[1]}) est de {secret_cost} (> moyenne {avg_cost:.1f}). Réessayez !",
            )

        st.rerun()

    st.write(f"**Nombre d'inspections réalisées :** {st.session_state.attempts}")

    if st.session_state.inspected_edges:
        st.markdown("### 📋 Historique des arêtes inspectées :")
        for edge, val in st.session_state.inspected_edges.items():
            st.write(f"- Arête **({edge[0]} ↔ {edge[1]})** : Coût = `{val}`")
