import random
import copy
class Nodo:
    def __init__(self, id):
        self.id = id
        self.saliente = []
        self.entrante = []

class Arco:
    def __init__(self, id, costo_recorrido, costo_recoleccion, obligatoria, origen, destino, bidireccional):
        self.id = id
        self.costo_recorrido = costo_recorrido
        self.costo_recoleccion = costo_recoleccion
        self.obligatoria = obligatoria
        self.origen = origen
        self.destino = destino
        self.bidireccional = bidireccional

class Grafo:
    def __init__(self):
        self.nodos = {}
        self.arcos = {}

def construir_grafo(arcos):
    grafo = Grafo()
    IdArco = 0
    for arco in arcos:
        bi_or_uni, origen, destino, costo_recorrido, costo_recoleccion = arco

        if origen not in grafo.nodos:
            grafo.nodos[origen] = Nodo(origen)

        if destino not in grafo.nodos:
            grafo.nodos[destino] = Nodo(destino)

        arco = Arco(IdArco, costo_recorrido, costo_recoleccion, True, grafo.nodos[origen], grafo.nodos[destino], bi_or_uni == "bi")

        grafo.arcos[IdArco] = arco

        grafo.nodos[origen].saliente.append(arco)
        grafo.nodos[destino].entrante.append(arco)

        IdArco += 1

    return grafo



def parsear_resultados_gurobi(resultados_gurobi):
    mapa = {}
    for resultado in resultados_gurobi:
        # Extraemos los nodos del resultado
        nodos = resultado[0][2:-1].split(',')
        nodo_inicial = int(nodos[0])
        nodo_final = int(nodos[1])

        # Extraemos la cantidad de veces que se recorre el arco
        y = int(resultado[1])

        # Usamos la tupla (nodo_inicial, nodo_final) como clave en el mapa
        mapa[(nodo_inicial, nodo_final)] = y
    return mapa


def construir_mapa_adyacencia(grafo, mapa_resultados):
    mapa_adyacencia = {}
    for id, nodo in grafo.nodos.items():
        mapa_adyacencia[nodo.id] = []
        for arco in nodo.saliente:            
            cantidad = mapa_resultados[(nodo.id, arco.destino.id)]
            if cantidad > 0:
                mapa_adyacencia[nodo.id].append([arco.destino.id,cantidad])
    return mapa_adyacencia

def es_transicion_valida(nodo_inicial, nodo_adyacente, camino, restricciones):
    # Verifica la restricción de no regresar al nodo anterior
    if nodo_adyacente == camino[-2] if len(camino) > 1 else None:
        return False

    # Agregar mas restricciones

    return True


restricciones = {}
def backtrack(metodo_random, limite_paso_salida, mapa_adyacencia, nodo_inicial, nodo_final, relaxed_solver, camino=None):
    if camino is None:
        camino = [nodo_inicial]

    # Caso base: encontramos una solución
    if nodo_inicial == nodo_final and limite_paso_salida <= 0:
        if sum([len(mapa_adyacencia[x]) for x in mapa_adyacencia]) == 0:
            return camino
        else:
            return None

    # Caso base: no hay más nodos para explorar
    if len(mapa_adyacencia[nodo_inicial]) == 0:
        print("Se acabaron los nodos, pero no estamos en el nodo final.")
        print("Pensar si se puede arreglar esta solucion.")# es posible que estemos al lado del nodo final y solo requiera agregar un arcos mas 
        print(camino)
        return None

    indices = list(range(len(mapa_adyacencia[nodo_inicial])))
    if metodo_random:
        random.shuffle(indices)
    else:  
        indices = sorted(indices, key=lambda i: mapa_adyacencia[nodo_inicial][i][1], reverse=True)
        
    for i in indices:
        indice_nodo_elegido = i 

        adyacente, recorrido = mapa_adyacencia[nodo_inicial][indice_nodo_elegido]
        
        if (not relaxed_solver):
            if not es_transicion_valida(nodo_inicial, adyacente, camino, restricciones):
                continue

        camino.append(adyacente)

        if adyacente == nodo_final:
            limite_paso_salida -= 1

        mapa_adyacencia_copia = copy.deepcopy(mapa_adyacencia)
        
        recorrido -= 1        
        if recorrido == 0:
            del mapa_adyacencia_copia[nodo_inicial][indice_nodo_elegido]
        else:
            mapa_adyacencia_copia[nodo_inicial][indice_nodo_elegido][1] = recorrido

        # Llamada recursiva
        resultado = backtrack(metodo_random, limite_paso_salida, mapa_adyacencia_copia, adyacente, nodo_final, relaxed_solver, camino)

        # Si encontramos una solución, la retornamos
        if resultado:
            return resultado

        # Si no encontramos una solución, hacemos backtrack
        camino.pop()
        if adyacente == nodo_final:
            limite_paso_salida += 1

    # Si exploramos todas las opciones y no encontramos una solución, retornamos None
    return None