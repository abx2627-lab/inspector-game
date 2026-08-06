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
    page_title="Graph Inspection Game - 2 Joueurs & Challenge",
    page_icon="🕵️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main-title { font-size: 2.2rem; font-weight: 800; color: #1E3A8A; text-align: center; }
    .sub-title { font-size: 1rem; color: #4B5563; text-align: center; margin-bottom: 20px; }
    .mode-box { background-color: #F3F4F6; padding: 15px; border-radius: 10px; border-left: 5px solid #2563EB; margin-bottom: 15px; }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-title">🕵️‍♂️ Le Jeu de l\'Inspecteur & de l\'Adversaire</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-title">Plateforme Interactive : Inspecteur vs Adversaire | MTYM 2026</div>',
    unsafe_allow_html=True,
)

# --------------------------------------------------
# 2. Barre Latérale & Paramètres
# --------------------------------------------------
st.sidebar.header("⚙️ Configuration du Jeu")

game_mode = st.sidebar.radio(
    "🎯 Choisissez le Mode de Jeu :",
    [
        "👥 Mode 2 Joueurs (Inspecteur vs Adversaire)",
        "⚔️ Mode Challenge Solo (vs IA)",
        "🛠️ Créateur de Réseau Personnalisé",
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

# --------------------------------------------------
# 3. Manuel des Règles du Mode 2 Joueurs
# --------------------------------------------------
with st.expander("📖 Règles du Mode 2 Joueurs (Inspecteur vs Adversaire)", expanded=False):
    st.markdown("""
    ### 📜 Déroulement d'une Partie à 2 Joueurs :
    1. **Rôle de l'Adversaire :** 
       * Il commence à jouer en premier dans la section dédiée.
       * Il définit les coûts secrets réels de chaque arête dans l'intervalle autorisé $[l_e, u_e]$.
       * **Objectif :** Piéger l'inspecteur en lui faisant payer de lourds frais d'inspection ou en l'orientant vers un chemin très coûteux.
       * Une fois terminé, il clique sur **"Verrouiller les Coûts"**.
    
    2. **Rôle de l'Inspecteur :**
       * Il joue en second sans voir les coûts fixés par l'Adversaire.
       * Il choisit quelles arêtes inspecter (en payant $C_{\\text{inspect}}$ par inspection).
       * Il sélectionne son itinéraire final de $s$ vers $t$.

    3. **Détermination du Vainqueur :**
       * **Victoire de l'Inspecteur :** S'il atteint la destination avec un coût global (Chemin + Inspections) proche du meilleur chemin théorique.
       * **Victoire de l'Adversaire :** S'il réussit à faire consommer trop de ressources à l'Inspecteur.
    """)

# --------------------------------------------------
# 4. Gestion de l'État de la Session (Session State)
# --------------------------------------------------


def init_default_graph():
    G = nx.DiGraph()
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
    init_default_graph()

# --------------------------------------------------
# 5. Créateur de Réseau Personnalisé
# --------------------------------------------------
if "Créateur" in game_mode:
    st.subheader("🛠️ Créateur de Réseau Personnalisé")
    st.info("Générez une nouvelle structure de réseau pour relancer un défi.")

    num_nodes = st.number_input(
        "Nombre de nœuds intermédiaires :", min_value=1, max_value=5, value=3
    )
    if st.button("Reconstruire le Réseau"):
        init_default_graph()
        st.success("Nouveau réseau initialisé avec succès !")
        st.rerun()

st.divider()

# --------------------------------------------------
# 6. Tour de l'Adversaire (Mode 2 Joueurs)
# --------------------------------------------------
if "👥 Mode 2 Joueurs" in game_mode and not st.session_state.adversary_locked:
    st.warning(
        "🦹 **Tour de l'Adversaire :** Réglez les coûts secrets pour piéger l'Inspecteur, puis verrouillez la configuration."
    )

    with st.form("adversary_form"):
        new_secrets = {}
        for e, (le, ue) in st.session_state.edges_data.items():
            new_secrets[e] = st.slider(
                f"Coût secret de l'arête ({e[0]} → {e[1]}) [Bornes: {le} - {ue}] :",
                min_value=float(le),
                max_value=float(ue),
                value=float(st.session_state.secret_costs[e]),
                step=0.1,
            )

        submit_adv = st.form_submit_button(
            "🔒 Verrouiller les Coûts & Passer à l'Inspecteur"
        )
        if submit_adv:
            st.session_state.secret_costs = new_secrets
            st.session_state.adversary_locked = True
            st.success("Coûts verrouillés ! C'est maintenant au tour de l'Inspecteur.")
            st.rerun()

# --------------------------------------------------
# 7. Affichage Graphique & Tour de l'Inspecteur
# --------------------------------------------------
col_graph, col_panel = st.columns([3, 2])

with col_graph:
    st.subheader("🗺️ Vision du Réseau (Inspecteur)")

    G = st.session_state.G
    pos = st.session_state.pos
    fig, ax = plt.subplots(figsize=(8, 5.2))

    # Dessin des Sommets
    nx.draw_networkx_nodes(
        G,
        pos,
        node_color="#2563EB",
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
        ax=ax,
    )

    # Dessin Neutre des Arêtes (Sans indiquer de chemin optimal)
    nx.draw_networkx_edges(
        G,
        pos,
        width=2.0,
        edge_color="#6B7280",
        arrowsize=18,
        arrowstyle="->",
        ax=ax,
    )

    # Étiquettes sur les Arêtes (Seul le coût inspecté est révélé)
    edge_labels = {}
    for edge, (le, ue) in st.session_state.edges_data.items():
        if edge in st.session_state.inspected_edges:
            edge_labels[edge] = (
                f"✅ Révélé: {st.session_state.inspected_edges[edge]}"
            )
        else:
            edge_labels[edge] = f"[{le}, {ue}]"

    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=edge_labels,
        font_size=9,
        rotate=False,
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#9CA3AF", alpha=0.95),
        ax=ax,
    )

    plt.axis("off")
    st.pyplot(fig)

with col_panel:
    st.subheader("🕵️ Panneau d'Inspection")

    nb_inspected = len(st.session_state.inspected_edges)
    total_inspect_cost = nb_inspected * inspection_cost_unit

    st.metric("Inspections réalisées", f"{nb_inspected}")
    st.metric("Frais d'inspection cumulés", f"{total_inspect_cost:.1f}")

    available_edges = [
        e
        for e in st.session_state.edges_data.keys()
        if e not in st.session_state.inspected_edges
    ]

    if available_edges and not st.session_state.game_over:
        selected_edge = st.selectbox(
            "Choisir l'arête à inspecter :",
            options=available_edges,
            format_func=lambda x: f"Inspecter ({x[0]} → {x[1]}) [Intervalle: {st.session_state.edges_data[x]}]",
        )

        if st.button("🔍 Exécuter l'inspection", type="primary", use_container_width=True):
            val = st.session_state.secret_costs[selected_edge]
            st.session_state.inspected_edges[selected_edge] = val
            st.session_state.history_log.append(
                f"Inspection de ({selected_edge[0]} → {selected_edge[1]}) : Coût réel = {val}"
            )
            st.rerun()

    st.markdown("---")
    st.subheader("🎯 Choix du Chemin Final")

    # Calcul de tous les chemins possibles s -> t
    all_paths = list(nx.all_simple_paths(G, source="s", target="t"))
    formatted_paths = [" → ".join(p) for p in all_paths]

    chosen_path_str = st.selectbox("Sélectionnez votre itinéraire final :", options=formatted_paths)
    chosen_path = all_paths[formatted_paths.index(chosen_path_str)]

    if st.button(
        "🏁 Valider l'Itinéraire & Révéler le Vainqueur",
        type="primary",
        use_container_width=True,
    ):
        st.session_state.game_over = True

        # Calcul du coût réel du chemin choisi par le joueur
        real_path_cost = sum(
            st.session_state.secret_costs[(u, v)]
            for u, v in zip(chosen_path[:-1], chosen_path[1:])
        )
        total_score = real_path_cost + total_inspect_cost

        # Calcul du vrai plus court chemin théorique
        real_graph = nx.DiGraph()
        for e, c in st.session_state.secret_costs.items():
            real_graph.add_edge(e[0], e[1], weight=c)

        true_opt_path = nx.shortest_path(
            real_graph, source="s", target="t", weight="weight"
        )
        true_opt_cost = nx.shortest_path_length(
            real_graph, source="s", target="t", weight="weight"
        )

        gap = total_score - true_opt_cost

        st.divider()
        st.markdown("### 📊 Résultats et Jugement Final :")

        if gap <= 1.5:
            st.balloons()
            st.success(f"""
            🎉 **Victoire de l'Inspecteur !**
            - **Itinéraire choisi :** `{' → '.join(chosen_path)}`
            - **Coût réel du chemin :** `{real_path_cost:.2f}`
            - **Frais d'inspection :** `{total_inspect_cost:.1f}`
            - **SCORE TOTAL :** `{total_score:.2f}`
            - *(Le vrai chemin le plus court était : `{' → '.join(true_opt_path)}` avec un coût de `{true_opt_cost:.2f}`)*
            """)
        else:
            st.error(f"""
            🦹 **Victoire de l'Adversaire !**
            - L'Adversaire a réussi son piège ! Vous avez dépensé trop de ressources ou pris un chemin coûteux.
            - **Votre SCORE TOTAL :** `{total_score:.2f}`
            - **Le vrai chemin le plus court était :** `{' → '.join(true_opt_path)}` pour un coût de `{true_opt_cost:.2f}` seulement !
            """)

# --------------------------------------------------
# 8. Commandes de Réinitialisation
# --------------------------------------------------
st.divider()
c1, c2 = st.columns(2)
with c1:
    if st.button("🎲 Nouvelle Partie (Réseau Aléatoire)", use_container_width=True):
        init_default_graph()
        st.rerun()

with c2:
    if st.button("🔓 Déverrouiller le Tour de l'Adversaire", use_container_width=True):
        st.session_state.adversary_locked = False
        st.session_state.game_over = False
        st.rerun()
