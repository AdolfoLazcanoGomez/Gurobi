import os

def traducir_dat(ruta):

    ########################
    # Datos header
    encabezado = {}
    ########################

    ########################
    #Conjuntos
    NODOS           = set()
    ARISTAS_REQ     = set()
    ARISTAS_NOREQ   = set()
    NODOS_INICIALES = set()
    ARISTAS_REQ_UNIDIRECCIONALES = set()
    ARISTAS_REQ_BIDIRECCIONALES = []
    #######################

    
    
    with open(ruta, 'r') as archivo:
        #archivo.readline() # leer encabezado de seccion

        for linea in archivo:
            if ";" in linea:
                break
            numeros = linea.split()  
            for num in numeros:
                NODOS.add(int(num))

        archivo.readline() # leer ;
        archivo.readline() # leer encabezado de seccion
        archivo.readline() # leer encabezado de seccion
        for linea in archivo:
            if ";" in linea:
                break
            numeros = linea.split()  
            nodo1, nodo2, peso = linea.split()
            peso = float(peso)
            if peso.is_integer():
                ARISTAS_NOREQ.add((int(nodo1), int(nodo2), int(peso)))
            else:
                ARISTAS_REQ.add((int(nodo1), int(nodo2), float(peso)))

        archivo.readline() # leer ;
        archivo.readline() # leer encabezado de seccion
        for linea in archivo:
            if ";" in linea:
                break
            numeros = linea.split()  
            for num in numeros:
                NODOS_INICIALES.add(int(num))
                
        archivo.readline() # leer ;
        archivo.readline() # leer encabezado de seccion
        for linea in archivo:
            if ";" in linea:
                break
            numeros = linea.replace('(', '').replace(')', '').split(',')            
            numeros = set([int(num.strip()) for num in numeros])
            for fila in ARISTAS_REQ:                                 
                fila_set = set(fila[:2])
                if fila_set == numeros: 
                    ARISTAS_REQ_UNIDIRECCIONALES.add(fila)  

        archivo.readline() # leer ;
        archivo.readline() # leer encabezado de seccion
        for linea in archivo:
            if ";" in linea:
                break
            numeros = linea.replace('(', '').replace(')', '').split(',')            
            numeros = [int(num.strip()) for num in numeros]
            for fila in ARISTAS_REQ:   
                fila_list = list(fila[:2])                              
                if fila_list == numeros: 
                    ARISTAS_REQ_BIDIRECCIONALES.append(fila)  

    return NODOS, ARISTAS_REQ, ARISTAS_NOREQ, ARISTAS_REQ_UNIDIRECCIONALES, ARISTAS_REQ_BIDIRECCIONALES, NODOS_INICIALES