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
    page_title="Jeu de l'Inspecteur - Graph Inspection Game", layout="wide"
)

st.title("🕵️‍♂️ Le Jeu de l'Inspecteur (Graph Inspection Game)")
st.caption(
    "Simulation interactive & Modélisation théorique des jeux sur graphes | MTYM 2026"
)

# --------------------------------------------------
# 2. Sélecteur de Mode (Mode de Jeu vs Mode Démo/Explication)
# --------------------------------------------------
st.sidebar.header("🕹️ Configuration du Mode")
app_mode = st.sidebar.radio(
    "Choisissez le mode de fonctionnement :",
    ["🎮 Mode Jeu (Challenge)", "📚 Mode Apprentissage (Explications & Maths)"],
)

st.sidebar.markdown("---")
st.sidebar.info("""
**Règles académiques :**
- **$s$** : Sommet Source (Départ)
- **$t$** : Sommet Puits (Destination)
- **$[l_e, u_e]$** : Bornes de coût pour l'arête $e$
- **Coût d'inspection** : 1.0 unité par arête inspectée.
""")

# --------------------------------------------------
# 3. Notice Théorique selon le mode
# --------------------------------------------------
with st.expander("📖 Concept Théorique & Guide du Problème", expanded=False):
    st.markdown("""
    ### 🎯 Définition du problème
    Soit un graphe orienté $G=(V, E)$ avec un couple $(s, t) \in V^2$. Chaque arête $e \in E$ possède une incertitude sur son coût réel $c(e) \in [l_e, u_e]$.
    
    L'**Inspecteur** doit trouver le chemin de coût minimal de $s$ à $t$. Il peut investir du budget pour inspecter des arêtes et révéler leur valeur exacte $c(e)$ avant de choisir son itinéraire.
    
    $$\text{Coût Total de la Stratégie} = \text{Nombre d'inspections} \times C_{\text{inspect}} + \text{Longueur du chemin final choisi}$$
    """)

# --------------------------------------------------
# 4. Initialisation du Graphe (Structure exacte et propre)
# --------------------------------------------------


def generate_graph_instance():
    G = nx.DiGraph()
    # Structure en couches sans aucun croisement d'arêtes
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
        secret_costs[(u, v)] = round(random.uniform(le, ue), 2)

    st.session_state.G = G
    st.session_state.edges_data = edges_data
    st.session_state.secret_costs = secret_costs
    st.session_state.inspected_edges = {}


if "G" not in st.session_state:
    generate_graph_instance()

# --------------------------------------------------
# 5. Boutons de Contrôle
# --------------------------------------------------
col_b1, col_b2 = st.columns(2)
with col_b1:
    if st.button("🎲 Générer une nouvelle instance", use_container_width=True):
        generate_graph_instance()
        st.rerun()

with col_b2:
    if st.button("🔄 Réinitialiser les inspections", use_container_width=True):
        st.session_state.inspected_edges = {}
        st.rerun()

st.divider()

# --------------------------------------------------
# 6. Affichage du Graphe & Contrôles
# --------------------------------------------------
col_graph, col_panel = st.columns([3, 2])

with col_graph:
    st.subheader("🗺️ Représentation du Réseau $G=(V, E)$")

    G = st.session_state.G
    fig, ax = plt.subplots(figsize=(8, 5))

    # Disposition géométrique stricte pour une netteté visuelle absolue
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
        node_color="#27AE60",
        node_size=1100,
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
    nx.draw_networkx_edges(
        G,
        pos,
        width=2.5,
        edge_color="#2C3E50",
        arrowsize=18,
        arrowstyle="->",
        ax=ax,
    )

    # Étiquettes d'arêtes adaptées au mode sélectionné
    edge_labels = {}
    for edge, (le, ue) in st.session_state.edges_data.items():
        if edge in st.session_state.inspected_edges:
            edge_labels[edge] = (
                f"Révélé: {st.session_state.inspected_edges[edge]}"
            )
        elif app_mode == "📚 Mode Apprentissage (Explications & Maths)":
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
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.9),
        ax=ax,
    )

    plt.axis("off")
    st.pyplot(fig)

with col_panel:
    if app_mode == "🎮 Mode Jeu (Challenge)":
        st.subheader("🎯 Panneau d'Inspection")

        available = [
            e
            for e in st.session_state.edges_data.keys()
            if e not in st.session_state.inspected_edges
        ]

        if available:
            selected_edge = st.selectbox(
                "Choisir une arête à inspecter :",
                options=available,
                format_func=lambda x: f"Arête ({x[0]} → {x[1]})",
            )

            if st.button("Inspecter l'arête 🕵️", use_container_width=True):
                val = st.session_state.secret_costs[selected_edge]
                st.session_state.inspected_edges[selected_edge] = val
                st.rerun()
        else:
            st.success("Toutes les arêtes ont été inspectées !")

        st.markdown("---")
        st.subheader("📊 Bilan de votre Stratégie")
        nb_insp = len(st.session_state.inspected_edges)
        st.write(f"• **Inspections effectuées :** `{nb_insp}` (Coût = `{nb_insp * 1.0}`)")

        if st.button(
            "🏆 Valider et Calculer le Score Final",
            type="primary",
            use_container_width=True,
        ):
            # Graph pour calcul du chemin réel
            real_g = nx.DiGraph()
            for e, c in st.session_state.secret_costs.items():
                real_g.add_edge(e[0], e[1], weight=c)

            path = nx.shortest_path(
                real_g, source="s", target="t", weight="weight"
            )
            cost_path = nx.shortest_path_length(
                real_g, source="s", target="t", weight="weight"
            )
            total_score = cost_path + (nb_insp * 1.0)

            st.success(f"""
            ### 🏁 Résultats :
            - **Plus court chemin réel ($s \\to t$) :** `{' → '.join(path)}`
            - **Longueur du chemin :** `{cost_path:.2f}`
            - **Coût Total (Chemin + Inspections) :** `{total_score:.2f}`
            """)

    else: # Mode Apprentissage
        st.subheader("📚 Analyse & Explications Mathématiques")
        st.info("Ce mode affiche les coûts secrets pour vous aider à comprendre l'impact de chaque décision d'inspection.")

        st.markdown("### 🧮 Valeurs Attendues (Espérance $\mathbb{E}[c(e)]$):")
        for (u, v), (le, ue) in st.session_state.edges_data.items():
            exp = (le + ue) / 2.0
            sec = st.session_state.secret_costs[(u, v)]
            st.write(f"- **({u} → {v})** : Intervalle `[{le}, {ue}]` | Moyenne = `{exp:.2f}` | **Réel = `{sec}`**")

        st.markdown("---")
        st.markdown("### 💡 Stratégie Optimale :")
        st.write("""
        1. Si l'incertitude $[l_e, u_e]$ d'une arête critique est très large, l'inspecter réduit le risque du pire scénario (Adversaire).
        2. Si le coût d'inspection (1.0) est supérieur au gain potentiel sur le chemin, il vaut mieux ne pas inspecter.
        """)
