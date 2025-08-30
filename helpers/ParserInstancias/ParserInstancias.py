import os
import random

def leer_archivo(ruta):

    ########################
    # Datos header
    encabezado = {}
    ########################

    ########################
    #Conjuntos
    NODOS           = set()
    NODOS_FANTASMA  = set()
    ARISTAS_REQ     = set()
    ARISTAS_NOREQ   = set()
    COORDENADAS     = set()
    RESTRICCIONES   = set()
    NODOS_INICIALES = set()
    NODOS_TERMINO   = set()
    #######################

    with open(ruta, 'r') as archivo:
        # Leer las primeras 8 líneas (clave: valor)
        for _ in range(8):
            linea = archivo.readline().strip()
            clave, valor = linea.split(':')
            encabezado[clave.strip()] = valor.strip()

        # Leer las líneas de aristas requeridas
        archivo.readline() # leer encabezado de seccion
        for _ in range(int(encabezado['ARISTAS_REQ'])):
            linea = archivo.readline().strip()
            tipo, nodo1, nodo2, costo_recorrer, costo_recolectar = linea.split()            
            if (tipo == 'uni'):
                ARISTAS_REQ.add((tipo, int(nodo1), int(nodo2), float(costo_recorrer), float(costo_recolectar)))
            else: 
                ARISTAS_REQ.add((tipo, int(nodo1), int(nodo2), float(costo_recorrer), float(costo_recolectar)))
                ARISTAS_REQ.add((tipo, int(nodo2), int(nodo1), float(costo_recorrer), float(costo_recolectar)))


        
        # Leer las líneas de aristas no requeridas
        archivo.readline() # leer encabezado de seccion
        for _ in range(int(encabezado['ARISTAS_NOREQ'])):
            linea = archivo.readline().strip()
            nodo1, nodo2 = linea.split()
            ARISTAS_NOREQ.add((int(nodo1), int(nodo2)))

        # Leer las coordenadas
        archivo.readline()        
        for _ in range(int(encabezado['VERTICES'])):
            linea = archivo.readline().strip()
            x, y = linea.split()
            COORDENADAS.add((float(x), float(y)))      
        
        # Leer las restricciones
        archivo.readline()
        for _ in range(int(encabezado['RESTRICCIONES'])):
            linea = archivo.readline().strip()
            nodo1, nodo2, nodo3 = linea.split()
            RESTRICCIONES.add((int(nodo1), int(nodo2), int(nodo3)))

        # Leer los nodos iniciales
        archivo.readline()
        for _ in range(int(encabezado['NODOS_INICIALES'])):
            linea = archivo.readline().strip()                
            NODOS_INICIALES.add((int(linea)))

        # Leer los nodos terminales
        archivo.readline()        
        for _ in range(int(encabezado['NODOS_TERMINO'])):
            linea = archivo.readline().strip()                
            NODOS_TERMINO.add((int(linea)))

    ###########################################################################
    #Extraccion de nodos reales
    nodos_temp = [(x[1], x[2]) for x in ARISTAS_REQ]
    numeros_unicos = set(numero for tupla in nodos_temp for numero in tupla)
    NODOS = numeros_unicos    
    ###########################################################################

    ###########################################################################
    #Extraccion de nodos fantasma
    nodos_fantasma_temp = ARISTAS_NOREQ
    numeros_unicos2 = set(numero for tupla in nodos_fantasma_temp for numero in tupla)
    NODOS_FANTASMA = numeros_unicos2
    ###########################################################################

    return encabezado, NODOS, NODOS_FANTASMA, ARISTAS_REQ, ARISTAS_NOREQ, COORDENADAS, RESTRICCIONES, NODOS_INICIALES, NODOS_TERMINO