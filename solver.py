import gurobipy as gp
import shutil
from gurobipy import * # type: ignore
from gurobipy import GRB # type: ignore
from helpers.ParserInstancias.ParserInstancias import leer_archivo
from helpers.TraductorInstancias.traductorDat import traducir_dat
from helpers.ConstructorRutas.ConstructorRutas import construir_grafo, construir_mapa_adyacencia, parsear_resultados_gurobi
from helpers.Visualizador.Visualizador import visualizar_grafo
from tabulate import tabulate
from abc import ABC, abstractmethod

import sys
import os
import copy
import time
from datetime import datetime


class FormatoInstancia(ABC):
    @abstractmethod
    def leer_instancia(self):
        pass

class FormatoA(FormatoInstancia):
    def leer_instancia(self):
        if carga_auto:
            nombre_archivo = "CasoRealChiquito.txt"
        else:
            nombre_archivo = sys.argv[1]
        ruta_absoluta = os.path.abspath(nombre_archivo)           
        ENCABEZADO, NODOS, NODOS_FANTASMA, ARISTAS_REQ, ARISTAS_NOREQ, COORDENADAS, RESTRICCIONES, NODOS_INICIALES, NODOS_TERMINO = leer_archivo(ruta_absoluta)
        return ENCABEZADO, NODOS, NODOS_FANTASMA, ARISTAS_REQ, ARISTAS_NOREQ, COORDENADAS, RESTRICCIONES, NODOS_INICIALES, NODOS_TERMINO

class FormatoB(FormatoInstancia):
    def leer_instancia(self):
        if carga_auto:
            nombre_archivo = "CasoRealChiquito.dat"
        else:
            nombre_archivo = sys.argv[1]
        ruta_absoluta = os.path.abspath(nombre_archivo)           
        NODOS, ARISTAS_REQ, ARISTAS_NOREQ, ARISTAS_REQ_UNIDIRECCIONALES, ARISTAS_REQ_BIDIRECCIONALES, NODOS_INICIALES = traducir_dat(ruta_absoluta)
        return NODOS, ARISTAS_REQ, ARISTAS_NOREQ, ARISTAS_REQ_UNIDIRECCIONALES, ARISTAS_REQ_BIDIRECCIONALES, NODOS_INICIALES

def formatear_encabezado(nombre_instancia,comentario,cantidad_nodos, cantidad_aristas_req, cantidad_aristas_noreq, cantidad_nodos_iniciales, cantidad_nodos_termino):
    encabezado = {
        "NOMBRE"            :nombre_instancia,
        "COMENTARIO"        :comentario,
        "VERTICES"          :cantidad_nodos,
        "ARISTAS_REQ"       :cantidad_aristas_req,
        "ARISTAS_NOREQ"     :cantidad_aristas_noreq,
        "RESTRICCIONES"     : 0,
        "NODOS_INICIALES"   :cantidad_nodos_iniciales,
        "NODOS_TERMINO"     :cantidad_nodos_termino
    }
    return encabezado

#####################################################
################ Panel de control ###################
# Cuando se ejecuta desde la línea de comandos se debe
# entregar la instancia como argumento, por lo que la carga
# automática se desactiva.
carga_auto = False  # True para llamar la instancia internamente, False para llamarla por parametro
debug = False # Mostrar informacion de instancia
tipo_formato = 'Corberan'  # 'DAT' o 'Corberan' 

if tipo_formato == 'Corberan':
    formatoA = FormatoA()
    ENCABEZADO, NODOS, NODOS_FANTASMA, ARISTAS_REQ, ARISTAS_NOREQ, COORDENADAS, RESTRICCIONES, NODOS_INICIALES, NODOS_TERMINO = formatoA.leer_instancia()
elif tipo_formato == 'DAT':
    formatoB = FormatoB()    
    NODOS, ARISTAS_REQ, ARISTAS_NOREQ, ARISTAS_REQ_UNIDIRECCIONALES, ARISTAS_REQ_BIDIRECCIONALES, NODOS_INICIALES = formatoB.leer_instancia()    
    ENCABEZADO = formatear_encabezado("Instancia de prueba", "test", len(NODOS), len(ARISTAS_REQ), len(ARISTAS_NOREQ), len(NODOS_INICIALES), len(NODOS))
else:
    raise ValueError('Formato no reconocido')
#####################################################


#####################################################
################# Datos de debug ####################
if debug:
    print()
    print()
    print()
    print("="*161)
    # Imprimir los headers
    for clave, valor in ENCABEZADO.items():
        print(f'{clave}: {valor}')
    # Imprimir datos de instancia
    datos_instancia = [
    ["Nodos", NODOS],
    #["Nodos Fantasma", NODOS_FANTASMA],
    ["Aristas Requeridas", ARISTAS_REQ],
    ["Aristas No Requeridas", ARISTAS_NOREQ],
    #["Coordenadas", COORDENADAS],
    #["Restricciones", RESTRICCIONES],
    ["Nodos Iniciales", NODOS_INICIALES],
    #["Nodos de Término", NODOS_TERMINO]
    ]
    tabla = tabulate(datos_instancia, headers=["Conjunto", "Elementos"], tablefmt="plain")
    print("="*161)
    print(tabla)
    print("="*161)
    print()
    print()
#####################################################

#####################################################
################## Resolución #######################
########### Método exacto: MILP + Gurobi ############

# Creación del modelo
model = gp.Model("ARP")  # type: ignore



# Parámetros
arcos_req_bidireccionales = []
arcos_noreq = []
costos_recorrer_noreq = {}
if (tipo_formato == "Corberan"):
    arcos_req = [(x[1], x[2]) for x in ARISTAS_REQ]
    arcos_req_unidireccionales = [(x[1], x[2]) for x in ARISTAS_REQ if x[0] == "uni"]
    arcos_req_bidireccionales = [((x[1], x[2]),(x[2], x[1])) for x in ARISTAS_REQ if x[0] != "uni"]

    costos_recorrer_req  = {(i, j): recorrer for (_, i, j, recorrer, _) in ARISTAS_REQ}
    costos_recolectar_req = {(i, j): recolectar for (_, i, j, _, recolectar) in ARISTAS_REQ}

    if ARISTAS_NOREQ:
        ejemplo = next(iter(ARISTAS_NOREQ))
        if len(ejemplo) >= 5:
            arcos_noreq = [(x[1], x[2]) for x in ARISTAS_NOREQ]
            costos_recorrer_noreq = {(i, j): recorrer for (_, i, j, recorrer, _) in ARISTAS_NOREQ}
        elif len(ejemplo) == 3:
            arcos_noreq = [(i, j) for (i, j, _) in ARISTAS_NOREQ]
            costos_recorrer_noreq = {(i, j): costo for (i, j, costo) in ARISTAS_NOREQ}
        else:
            arcos_noreq = [(i, j) for (i, j) in ARISTAS_NOREQ]
            costos_recorrer_noreq = {(i, j): 0 for (i, j) in arcos_noreq}

    conjunto_inicio = list(NODOS_INICIALES)
    if (NODOS_TERMINO.__len__() == 0): #type: ignore
        conjunto_termino = list(NODOS)
    else:
        conjunto_termino = list(NODOS_TERMINO) #type: ignore

else:#arreglar pendiente
    arcos_req = [(x[0], x[1]) for x in ARISTAS_REQ]
    arcos_req_unidireccionales = [(x[0], x[1]) for x in ARISTAS_REQ_UNIDIRECCIONALES] # type: ignore
    arcos_req_bidireccionales_temp = [(x[0], x[1]) for x in ARISTAS_REQ_BIDIRECCIONALES] # type: ignore

    for i in range(0, len(arcos_req_bidireccionales_temp), 2):
        par = (arcos_req_bidireccionales_temp[i], arcos_req_bidireccionales_temp[i+1])
        arcos_req_bidireccionales.append(par)
    costos_recolectar_req = {(i, j): recolectar for (i, j, recolectar) in ARISTAS_REQ}
    arcos_noreq = [(i, j) for (i, j, _) in ARISTAS_NOREQ]
    costos_recorrer_noreq = {(i, j): costo for (i, j, costo) in ARISTAS_NOREQ}
    conjunto_inicio = list(NODOS_INICIALES)
    conjunto_termino = list(NODOS)

# Variables de decisión
# x = model.addVars(arcos_req, vtype=GRB.INTEGER, lb=0, name="x")
# s_i = model.addVars(conjunto_inicio, vtype=GRB.BINARY, name="s_i")
# t_i = model.addVars(conjunto_termino, vtype=GRB.BINARY, name="t_i")
# Variables de decisión
x = model.addVars(arcos_req, vtype=GRB.INTEGER, lb=0, name="x")
y = model.addVars(arcos_noreq, vtype=GRB.INTEGER, lb=0, name="y")
s_i = {k: model.addVar(vtype=GRB.BINARY, name=f"s_i[{k}]") if k in conjunto_inicio else 0 for k in NODOS}
t_i = {k: model.addVar(vtype=GRB.BINARY, name=f"t_i[{k}]") if k in conjunto_termino else 0 for k in NODOS}

start_time = time.time_ns()
# Función objetivo
model.setObjective(
    gp.quicksum(costos_recorrer_req[i, j] * x[i, j] for (i, j) in arcos_req)
    + gp.quicksum(costos_recorrer_noreq[i, j] * y[i, j] for (i, j) in arcos_noreq),
    GRB.MINIMIZE,
)  # type: ignore

# Restricciones
# B.1 - Visitar todos los arcos requeridos
model.addConstrs((x[i, j] >= 1 for (i, j) in arcos_req if (i, j) in arcos_req_unidireccionales and i != j), name="VisitarTodosArcos")

# B.2 - Visitar todos los arcos bidireccionales requeridos
model.addConstrs((x[i, j] + x[k, m] >= 1 for ((i, j), (k, m)) in arcos_req_bidireccionales), name='VisitarTodosArcosBidireccionales')

# B.3 - Balance de flujo
model.addConstrs(
    gp.quicksum(x[i, j] for i, j in arcos_req if i == k)
    + gp.quicksum(y[i, j] for i, j in arcos_noreq if i == k)
    - gp.quicksum(x[j, i] for j, i in arcos_req if i == k)
    - gp.quicksum(y[j, i] for j, i in arcos_noreq if i == k)
    == s_i.get(k, 0) - t_i.get(k, 0)
    for k in NODOS
)

# B.4 - Conjunto de inicio
model.addConstr(gp.quicksum(s_i[i] for i in conjunto_inicio) == 1, name="NodoInicial") # type: ignore

# B.5 - Conjunto de termino
model.addConstr(gp.quicksum(t_i[j] for j in conjunto_termino) == 1, name="NodoTerminal") # type: ignore


def run_solver(ruta_instancia: str) -> None:
    nombre_instancia = os.path.splitext(os.path.basename(ruta_instancia))[0]
    nombre_carpeta = "output"
    os.makedirs(nombre_carpeta, exist_ok=True)

    try:
        # Optimización del modelo
        model.optimize()
        # Datos debug de Salida
        #model.write('csSolver.lp')
        tiempo_modelo_ns = time.time_ns() - start_time

        # Imprimir los valores de las variables de decisión
        # for v in model.getVars():
        #     print('%s %g' % (v.VarName, v.X))

        # Parsear resultados
        output = [('%s %g' % (v.VarName, v.X)) for v in model.getVars()]
        resultados_x = [entrada.split() for entrada in output if entrada.startswith('x')]
        vars_y_valores = [(v.VarName, v.X) for v in model.getVars()]
        nodo_inicial_raw = [var for var, valor in vars_y_valores if var.startswith('s_i') and valor == 1]
        nodo_terminal_raw = [var for var, valor in vars_y_valores if var.startswith('t_i') and valor == 1]
        nodo_inicial = int(nodo_inicial_raw[0].split('[')[1].split(']')[0])
        nodo_terminal = int(nodo_terminal_raw[0].split('[')[1].split(']')[0])

        # Construir grafo
        grafo = construir_grafo(ARISTAS_REQ)
        mapa_resultados = parsear_resultados_gurobi(resultados_x)
        largo_ruta_a_ciegas = sum(valor for clave, valor in mapa_resultados.items() if valor == 1)
        # print("El largo de la ruta a ciegas es:", largo_ruta_a_ciegas)
        # print("El tiempo del modelo fue:", tiempo_modelo_ns, "nanosegundos")
        mapa_adyacencia = construir_mapa_adyacencia(grafo, mapa_resultados)
        mapa_adyacencia_copia = mapa_adyacencia.copy()

        # Obtener la fecha y hora actual
        ahora = datetime.now()
        fecha_str = ahora.strftime('%Y-%m-%d_%H-%M-%S')

        # Crear la ruta del archivo de resultados
        ruta_archivo = os.path.join(nombre_carpeta, f"{nombre_instancia}.txt")
        nombre_archivo = os.path.join(nombre_carpeta, f"{nombre_instancia}")

        # costo_recoleccion = 0
        costo_recoleccion = sum(arista[4] for arista in ARISTAS_REQ)
        #
        costo_recorrer = (
            sum(costos_recorrer_req[i, j] * x[i, j].X for (i, j) in arcos_req)
            + sum(costos_recorrer_noreq[i, j] * y[i, j].X for (i, j) in arcos_noreq)
        )
        costo_pasada = costo_recorrer - costo_recoleccion

        multiplicidad_path = os.path.join(nombre_carpeta, f"{nombre_instancia}.txt")
        x_multiplicidad = { (i, j): int(round(x[i, j].X)) for (i, j) in arcos_req }
        y_multiplicidad = { (i, j): int(round(y[i, j].X)) for (i, j) in arcos_noreq }
        with open(multiplicidad_path, 'w') as f_mul:
            f_mul.write("Arco_i Arco_j VecesRecorrido\n")
            f_mul.write("============================\n")
            for (i, j) in sorted(x_multiplicidad.keys()):
                f_mul.write(f"{i} {j} {x_multiplicidad[(i, j)]}\n")
            for (i, j) in sorted(y_multiplicidad.keys()):
                f_mul.write(f"{i} {j} {y_multiplicidad[(i, j)]}\n")
        # print(f"Archivo con multiplicidad de arcos guardado en: {multiplicidad_path}")

        # Escribir en el archivo
        # with open(ruta_archivo, 'w') as f:
            # f.write("Nombre instancia: "+ ENCABEZADO['NOMBRE'] + "\n")
            # f.write("Costo: " + str(costo_pasada) + "\n")
            # f.write("Longitud ruta: " + str(len(ruta)) + "\n") # type: ignore␊
            # f.write("Longitud ruta: " + str(sum(x_multiplicidad.values()) + sum(y_multiplicidad.values())) + "\n")
            # f.write("Nodo inicial: " + str(nodo_inicial) + "\n")
            # f.write("Nodo terminal: " + str(nodo_terminal) + "\n")
            # f.write("Tiempo de modelo: " + str(tiempo_modelo_ns) + "\n")
            # f.write("Tiempo de backtracking: " + str(elapsed_time_ns) + "\n")
            # f.write("La ruta es la siguiente: " + "\n")
            # f.write(str(ruta) + "\n")
            # f.write("Mapa de resultados: " + str(mapa_resultados) + "\n")

            #archivo_salida << "Costo recoleccion: " << suma_recoleccion << endl;
            #archivo_salida << "Costo recorrer: " << suma_recorrer << endl;
            #archivo_salida << "Costo pesos pasada: " << costo_pesos_pasada << endl;
            #archivo_salida << "Mejor costo: " << mejor_solucion.costo_camino << endl;

        # print(f"Se ha creado la carpeta {nombre_carpeta} y se ha escrito en el archivo {fecha_str}.txt")

        # show_grafico = True
        # visualizar_grafo(mapa_adyacencia_copia, ruta, show_grafico, nombre_archivo) # type: ignore

    except Exception as e:
        log_path = os.path.join(nombre_carpeta, "{nombre_instancia}_error.log")
        with open(log_path, "w") as log_file:
            log_file.write(str(e))
        print("Error al optimizar el modelo")







#LAST UPDATE

if __name__ == "__main__":
    # Se espera que la ruta a la instancia se entregue como argumento
    # al ejecutar el script, por ejemplo:
    #   python solver.py instances/instance_01_M.txt
    run_solver(sys.argv[1])