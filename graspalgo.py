import matplotlib.pyplot as plt
import matplotlib.animation as animation
import math
import random
import time  


def parse_vrppd_file(file_path):
    nodes = []
    depots = []
    in_coord_section = False
    in_match_section = False

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()

            if line.startswith("NODE_COORD_SECTION"):
                in_coord_section = True
                in_match_section = False
            elif line.startswith("NODE_MATCH_SECTION"):
                in_match_section = True
                in_coord_section = False
            elif in_coord_section and line != "":
                parts = line.split()
                node_id = int(parts[0])
                x = float(parts[1])
                y = float(parts[2])
                nodes.append({'id': node_id, 'x': x, 'y': y, 'is_depot': False})
            elif in_match_section and "DEPOT" in line:
                depot_id = int(line.split(":")[1].strip())
                depots.append(depot_id)

    for node in nodes:
        if node['id'] in depots:
            node['is_depot'] = True

    return nodes


def distancia(nodo_a, nodo_b):
    return math.sqrt((nodo_a['x'] - nodo_b['x'])**2 + (nodo_a['y'] - nodo_b['y'])**2)


def calcular_distancia_total(ruta):
    return sum(distancia(ruta[i], ruta[i+1]) for i in range(len(ruta) - 1))


def construir_ruta_multidepot(nodos):
    ruta_depot_1 = []
    ruta_depot_2 = []
    
    
    inicio_depot_1 = next(nodo for nodo in nodos if nodo['is_depot'] and nodo['id'] == 16)
    inicio_depot_2 = next(nodo for nodo in nodos if nodo['is_depot'] and nodo['id'] == 10)

    
    nodos_clientes = [nodo for nodo in nodos if not nodo['is_depot']]

    
    for cliente in nodos_clientes:
        if random.choice([True, False]):  
            ruta_depot_1.append(cliente)
        else:
            ruta_depot_2.append(cliente)
    
    
    return [inicio_depot_1] + ruta_depot_1 + [inicio_depot_1], [inicio_depot_2] + ruta_depot_2 + [inicio_depot_2]


def busqueda_local_2opt(ruta):
    mejorado = True
    while mejorado:
        mejorado = False
        for i in range(1, len(ruta) - 2):
            for j in range(i + 1, len(ruta) - 1):
                if distancia(ruta[i], ruta[i+1]) + distancia(ruta[j], ruta[j+1]) > distancia(ruta[i], ruta[j]) + distancia(ruta[i+1], ruta[j+1]):
                    ruta[i+1:j+1] = reversed(ruta[i+1:j+1])
                    mejorado = True
    return ruta


def busqueda_local_swap(ruta):
    
    if len(ruta) > 3:
        i, j = random.sample(range(1, len(ruta) - 1), 2)  
        ruta[i], ruta[j] = ruta[j], ruta[i]  
    return ruta


def grasp_multidepot(nodos, num_iteraciones):
    mejor_ruta_depot_1 = None
    mejor_ruta_depot_2 = None
    mejor_costo = float('inf')

    
    start_time = time.time()

    for _ in range(num_iteraciones):
        
        ruta_1, ruta_2 = construir_ruta_multidepot(nodos)
        
        
        ruta_1_optimizada = busqueda_local_2opt(ruta_1)#busqueda_local_swap
        ruta_2_optimizada = busqueda_local_2opt(ruta_2)#busqueda_local_2opt

        
        costo_total = calcular_distancia_total(ruta_1_optimizada) + calcular_distancia_total(ruta_2_optimizada)

        # Si encontramos una mejor solución, la guardamos
        if costo_total < mejor_costo:
            mejor_ruta_depot_1 = ruta_1_optimizada
            mejor_ruta_depot_2 = ruta_2_optimizada
            mejor_costo = costo_total

    
    tiempo_total = time.time() - start_time

    return mejor_ruta_depot_1, mejor_ruta_depot_2, mejor_costo, tiempo_total


def animar_ruta(i, ruta, line):
    if i < len(ruta) - 1:
        x_coords = [nodo['x'] for nodo in ruta[:i+1]]
        y_coords = [nodo['y'] for nodo in ruta[:i+1]]
        line.set_data(x_coords, y_coords)
    return line,


def visualizar_ruta_animada(nodos, ruta, title):
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlim(0, 120)
    ax.set_ylim(0, 120)

    
    for nodo in nodos:
        if nodo['is_depot']:
            ax.scatter(nodo['x'], nodo['y'], color='red', s=100, label=f'Depósito {nodo["id"]}')
        else:
            ax.scatter(nodo['x'], nodo['y'], color='blue', s=100, label=f'Cliente {nodo["id"]}')
    
    
    for nodo in nodos:
        ax.text(nodo['x'] + 0.2, nodo['y'] + 0.2, f'{nodo["id"]}', fontsize=12, color='black')
    
    
    line, = ax.plot([], [], marker='o', color='green')

    
    ani = animation.FuncAnimation(fig, animar_ruta, frames=len(ruta), fargs=(ruta, line),
                                  interval=500, repeat=False)

    plt.title(title)
    plt.xlabel('Coordenada X')
    plt.ylabel('Coordenada Y')
    plt.grid(True)
    plt.show()


nodos = parse_vrppd_file('mpdpsl20-1a.vrppd')


mejor_ruta_1, mejor_ruta_2, mejor_costo, tiempo_total = grasp_multidepot(nodos, num_iteraciones=10000)


print(f"Tiempo total de ejecución de GRASP: {tiempo_total:.2f} segundos")


visualizar_ruta_animada(nodos, mejor_ruta_1, "Mejor Ruta - Depósito 1 (GRASP)")
visualizar_ruta_animada(nodos, mejor_ruta_2, "Mejor Ruta - Depósito 2 (GRASP)")