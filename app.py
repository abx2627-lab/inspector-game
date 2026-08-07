import math
import random
import networkx as nx
import plotly.graph_objects as go
import streamlit as st

# ==========================================
# CONFIGURATION DE LA PAGE STREAMLIT
# ==========================================
st.set_page_config(
    page_title="Jeu du Plus Court Chemin (1v1)",
    page_layout="wide",
    initial_sidebar_state="expanded",
)

# Style CSS personnalisé
st.markdown(
    """
<style>
    .main-header { font-size: 2.2rem; font-weight: bold; color: #1E3A8A; text-align: center; margin-bottom: 1rem; }
    .score-card { background-color: #F3F4F6; padding: 1rem; border-radius: 10px; text-align: center; border: 1px solid #E5E7EB; }
    .role-badge-inspector { background-color: #3B82F6; color: white; padding: 0.3rem 0.8rem; border-radius: 20px; font-weight: bold; }
    .role-badge-adversary { background-color: #EF4444; color: white; padding: 0.3rem 0.8rem; border-radius: 20px; font-weight: bold; }
</style>
""",
    unsafe_allow_scope=True,
)


# ==========================================
# FONCTIONS UTILITAIRES DE GÉNÉRATION DU GRAPH
# ==========================================
def generate_game_graph(num_nodes=8, edge_prob=0.45):
    """Génère un graphe connexe positionné circulairement."""
    while True:
        G = nx.erdos_renyi_graph(n=num_nodes, p=edge_prob, seed=None)
        if nx.is_connected(G):
            break

    # Positionnement en cercle pour une meilleure lisibilité
    pos = {}
    for i in range(num_nodes):
        angle = 2 * math.pi * i / num_nodes
        pos[i] = (math.cos(angle), math.sin(angle))

    edges_data = {}
    for u, v in G.edges():
        edges_data[(u, v)] = {
            "poids_reel": random.randint(3, 15),
            "poids_affiche": None,
            "inspecte": False,
        }

    return G, pos, edges_data


def calculate_real_shortest_path(G, edges_data, source, target):
    """Calcule la distance réelle du plus court chemin."""
    G_temp = nx.Graph()
    for (u, v), data in edges_data.items():
        G_temp.add_edge(u, v, weight=data["poids_reel"])
    try:
        path = nx.shortest_path(
            G_temp, source=source, target=target, weight="weight"
        )
        length = nx.shortest_path_length(
            G_temp, source=source, target=target, weight="weight"
        )
        return path, length
    except nx.NetworkXNoPath:
        return [], float("inf")


# ==========================================
# INITIALISATION DE LA SESSION (STATE)
# ==========================================
if "game_started" not in st.session_state:
    st.session_state.game_started = False

if "score_inspector" not in st.session_state:
    st.session_state.score_inspector = 0

if "score_adversary" not in st.session_state:
    st.session_state.score_adversary = 0

if "current_round" not in st.session_state:
    st.session_state.current_round = 1

if "max_rounds" not in st.session_state:
    st.session_state.max_rounds = 5

if "current_phase" not in st.session_state:
    st.session_state.current_phase = "ADVERSARY_TURN"

if "last_result_msg" not in st.session_state:
    st.session_state.last_result_msg = None


def start_new_round():
    """Initialise un nouveau round avec un nouveau graphe."""
    G, pos, edges_data = generate_game_graph(num_nodes=8)
    nodes = list(G.nodes())
    source, target = random.sample(nodes, 2)

    st.session_state.G = G
    st.session_state.pos = pos
    st.session_state.edges_data = edges_data
    st.session_state.source = source
    st.session_state.target = target
    st.session_state.current_phase = "ADVERSARY_TURN"

    # Calcul du trajet optimal réel pour vérification interne
    _, real_len = calculate_real_shortest_path(
        G, edges_data, source, target
    )
    st.session_state.real_shortest_len = real_len


if not st.session_state.game_started:
    start_new_round()
    st.session_state.game_started = True


# ==========================================
# RENDU DU GRAPHE AVEC PLOTLY
# ==========================================
def draw_graph(G, pos, edges_data, source, target, show_real_weights=False):
    edge_x, edge_y = [], []
    annotations = []

    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

        # Informations sur le poids
        data = edges_data.get((u, v)) or edges_data.get((v, u))
        is_ins = data["inspecte"]

        if show_real_weights or is_ins:
            lbl = f"<b>{data['poids_reel']}</b>"
            color = "#10B981" if is_ins else "#6B7280"
        elif data["poids_affiche"] is not None:
            lbl = f"<i>{data['poids_affiche']}</i>"
            color = "#EF4444"
        else:
            lbl = "?"
            color = "#9CA3AF"

        annotations.append(
            dict(
                x=(x0 + x1) / 2,
                y=(y0 + y1) / 2,
                text=lbl,
                showarrow=False,
                font=dict(size=14, color=color),
                bgcolor="white",
                bordercolor=color,
                borderwidth=1,
                borderpad=3,
            )
        )

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=2, color="#CBD5E1"),
        hoverinfo="none",
        mode="lines",
    )

    node_x, node_y, node_color, node_text, node_size = [], [], [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(f"Sommet {node}")

        if node == source:
            node_color.append("#10B981")  # Vert pour Départ
            node_size.append(35)
        elif node == target:
            node_color.append("#F59E0B")  # Orange pour Arrivée
            node_size.append(35)
        else:
            node_color.append("#3B82F6")  # Bleu par défaut
            node_size.append(25)

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        hoverinfo="text",
        text=[str(n) for n in G.nodes()],
        textposition="middle center",
        textfont=dict(color="white", size=12, family="Arial Black"),
        marker=dict(size=node_size, color=node_color, line=dict(width=2, color="white")),
    )

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            showlegend=False,
            hovermode="closest",
            margin=dict(b=0, l=0, r=0, t=0),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            annotations=annotations,
            height=450,
        ),
    )
    return fig


# ==========================================
# INTERFACE UTILISATEUR (UI)
# ==========================================
st.markdown(
    "<div class='main-header'>⚔️ Duel du Plus Court Chemin (1v1)</div>",
    unsafe_allow_scope=True,
)

# Tableau des scores
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        f"<div class='score-card'><h3>🔵 Inspecteur</h3><h2>{st.session_state.score_inspector} pts</h2></div>",
        unsafe_allow_scope=True,
    )
with col2:
    st.markdown(
        f"<div class='score-card'><h3>🏆 Round</h3><h2>{st.session_state.current_round} / {st.session_state.max_rounds}</h2></div>",
        unsafe_allow_scope=True,
    )
with col3:
    st.markdown(
        f"<div class='score-card'><h3>🔴 Adversaire</h3><h2>{st.session_state.score_adversary} pts</h2></div>",
        unsafe_allow_scope=True,
    )

st.divider()

# Message de résultat du round précédent
if st.session_state.last_result_msg:
    msg = st.session_state.last_result_msg
    if msg["type"] == "win":
        st.success(msg["text"])
    else:
        st.error(msg["text"])

# Fin de la partie
if st.session_state.current_round > st.session_state.max_rounds:
    st.balloons()
    st.header("🏁 Partie terminée !")
    if st.session_state.score_inspector > st.session_state.score_adversary:
        st.success("🎉 Victoire finale de l'INSPECTEUR 🔵 !")
    elif st.session_state.score_adversary > st.session_state.score_inspector:
        st.error("🦹 Victoire finale de l'ADVERSAIRE 🔴 !")
    else:
        st.info("🤝 Match nul parfait !")

    if st.button("🔄 Recommencer une nouvelle partie"):
        st.session_state.score_inspector = 0
        st.session_state.score_adversary = 0
        st.session_state.current_round = 1
        st.session_state.last_result_msg = None
        start_new_round()
        st.rerun()

    st.stop()


# Informations du round en cours
st.info(
    f"📍 **Objectif du Round :** Relier le sommet **{st.session_state.source}** (Vert) au sommet **{st.session_state.target}** (Orange)."
)

col_graph, col_controls = st.columns([2, 1])

# ------------------------------------------
# PHASE 1 : TOUR DE L'ADVERSAIRE
# ------------------------------------------
if st.session_state.current_phase == "ADVERSARY_TURN":
    with col_graph:
        st.subheader("🔴 Tour de l'Adversaire : Falsification du Graphe")
        fig = draw_graph(
            st.session_state.G,
            st.session_state.pos,
            st.session_state.edges_data,
            st.session_state.source,
            st.session_state.target,
            show_real_weights=True,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_controls:
        st.markdown(
            " Vous voyez les **vrais poids** (en vert/gris). Définissez les valeurs affichées que verra l'Inspecteur pour le piéger."
        )

        with st.form("adversary_form"):
            fake_weights = {}
            for (u, v), data in st.session_state.edges_data.items():
                fake_weights[(u, v)] = st.number_input(
                    f"Arête ({u} - {v}) [Réel: {data['poids_reel']}]",
                    min_value=1,
                    max_value=30,
                    value=data["poids_reel"],
                    key=f"edge_{u}_{v}",
                )

            submit_adv = st.form_submit_button("🔒 Valider le Piège")

            if submit_adv:
                for edge, val in fake_weights.items():
                    st.session_state.edges_data[edge]["poids_affiche"] = val
                st.session_state.current_phase = "INSPECTOR_TURN"
                st.session_state.last_result_msg = None
                st.rerun()

# ------------------------------------------
# PHASE 2 : TOUR DE L'INSPECTEUR
# ------------------------------------------
elif st.session_state.current_phase == "INSPECTOR_TURN":
    with col_graph:
        st.subheader("🔵 Tour de l'Inspecteur : Recherche du Plus Court Chemin")
        fig = draw_graph(
            st.session_state.G,
            st.session_state.pos,
            st.session_state.edges_data,
            st.session_state.source,
            st.session_state.target,
            show_real_weights=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_controls:
        st.markdown(
            " 🕵️ **Inspectez** des arêtes pour vérifier leur vrai poids, puis proposez votre **chemin final**."
        )

        # Module d'inspection
        st.markdown("#### 🔍 Inspection d'une arête")
        uninspected_edges = [
            f"{u} - {v}"
            for (u, v), d in st.session_state.edges_data.items()
            if not d["inspecte"]
        ]

        if uninspected_edges:
            selected_edge = st.selectbox(
                "Choisir une arête à inspecter :", uninspected_edges
            )
            if st.button("🔎 Inspecter"):
                u, v = map(int, selected_edge.split(" - "))
                if (u, v) in st.session_state.edges_data:
                    st.session_state.edges_data[(u, v)]["inspecte"] = True
                else:
                    st.session_state.edges_data[(v, u)]["inspecte"] = True
                st.rerun()
        else:
            st.write("Toutes les arêtes ont été inspectées !")

        st.divider()

        # Validation du chemin final
        st.markdown("#### 🚀 Saisie du Chemin Final")
        nodes_list = list(st.session_state.G.nodes())

        path_input = st.text_input(
            "Chemin (ex: 0, 2, 5) :",
            value=f"{st.session_state.source}, {st.session_state.target}",
        )

        if st.button("🏁 Soumettre le Chemin"):
            try:
                user_path = [
                    int(x.strip()) for x in path_input.split(",") if x.strip() != ""
                ]

                # Validation de la structure du chemin
                is_valid = True
                if (
                    len(user_path) < 2
                    or user_path[0] != st.session_state.source
                    or user_path[-1] != st.session_state.target
                ):
                    is_valid = False

                user_length = 0
                for i in range(len(user_path) - 1):
                    u, v = user_path[i], user_path[i + 1]
                    if st.session_state.G.has_edge(u, v):
                        data = st.session_state.edges_data.get(
                            (u, v)
                        ) or st.session_state.edges_data.get((v, u))
                        user_length += data["poids_reel"]
                    else:
                        is_valid = False
                        break

                if not is_valid:
                    st.warning(
                        "⚠️ Chemin invalide ! Assurez-vous qu'il s'agit d'une suite d'arêtes existantes du départ à l'arrivée."
                    )
                else:
                    # CALCUL DU GAP ET LOGIQUE DE SCORE PONDÉRÉE & ÉQUILIBRÉE
                    real_opt = st.session_state.real_shortest_len
                    gap = abs(user_length - real_opt)

                    # Compter les inspections réalisées
                    nb_ins = sum(
                        1
                        for d in st.session_state.edges_data.values()
                        if d["inspecte"]
                    )

                    # --------------------------------------------------
                    # LOGIQUE DES POINTS PONDÉRÉE ET ÉQUILIBRÉE
                    # --------------------------------------------------
                    if gap <= 1.5:
                        # Succès de l'Inspecteur : Calcul pondéré selon l'économie d'inspections
                        total_edges = len(st.session_state.edges_data)
                        gain_ins = max(10, int((total_edges - (2 * nb_ins)) * 5))

                        st.session_state.score_inspector += gain_ins
                        st.session_state.last_result_msg = {
                            "type": "win",
                            "text": f"🎉 Round {st.session_state.current_round} : Trajet réussi ! Distance = {user_length} (Optimum = {real_opt}). (+{gain_ins} pts pour l'Inspecteur 🔵, 0 pt pour l'Adversaire)",
                        }
                    else:
                        # Faute de l'Inspecteur : Gain pondéré et plafonné pour l'Adversaire (Max 30 pts)
                        gain_adv = min(30, int(10 + (gap * 5)))

                        st.session_state.score_adversary += gain_adv
                        st.session_state.last_result_msg = {
                            "type": "loss",
                            "text": f"🦹 Round {st.session_state.current_round} : Piège réussi par l'Adversaire ! Chemin choisi = {user_length} (Optimum = {real_opt}). (+{gain_adv} pts pour l'Adversaire 🔴, 0 pt pour l'Inspecteur)",
                        }

                    # Passage au round suivant
                    st.session_state.current_round += 1
                    start_new_round()
                    st.rerun()

            except ValueError:
                st.error(
                    "Entrée invalide. Format attendu : des numéros de sommets séparés par des virgules."
                )
