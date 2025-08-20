import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
def visualizar_grafo(mapa_adyacencia, camino, show_grafico, nombre_archivo):
    G = nx.DiGraph()  # Crear un grafo dirigido
    
    # Añadir arcos al grafo
    for nodo, adyacentes in mapa_adyacencia.items():
        for adyacente in adyacentes:
            G.add_edge(nodo, adyacente[0])

    # Calcular la posición de los nodos para visualizar
    pos = nx.kamada_kawai_layout(G)
    nx.draw(G, pos, with_labels=True)

    # Dibujar todos los nodos y arcos
    nx.draw_networkx_nodes(G, pos, node_color='yellow')
    nx.draw_networkx_edges(G, pos, edge_color='gray')

    # Calcular los colores para los arcos del camino
    cmap = cm.get_cmap('cool')  # Puedes cambiar a cualquier otro mapa de colores
    colores = [cmap(i) for i in np.linspace(0, 1, len(camino)-1)]
    edge_labels = {(camino[i], camino[i+1]): str(i+1) for i in range(len(camino)-1)}
    
    # Dibujar los arcos del camino con colores gradientes
    for i in range(len(camino)-1):
        nx.draw_networkx_edges(G, pos,
                            edgelist=[(camino[i], camino[i+1])],
                            edge_color=colores[i]) # type: ignore
        #nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    edge_labels = {}
    for i in range(len(camino)-1):
        edge = (camino[i], camino[i+1])
        if edge in edge_labels:
            edge_labels[edge].append(str(i+1))
        else:
            edge_labels[edge] = [str(i+1)]

# Calcular la posición de las etiquetas a lo largo del arco y dibujarlas
    for edge in edge_labels:
        x = (pos[edge[0]][0] + pos[edge[1]][0]) / 2
        y = (pos[edge[0]][1] + pos[edge[1]][1]) / 2
        for i, label in enumerate(edge_labels[edge]):
            offset = 0.03 * i  # Ajustar la offset como sea necesario
            label_pos = (x + offset, y + offset)
            plt.text(label_pos[0], label_pos[1], label, color='black')

    plt.savefig(nombre_archivo + '-GraficoMapa.png')
    if show_grafico:
        plt.show()  # Mostrar la visualización
