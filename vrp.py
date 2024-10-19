import random
import math
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Parser para leer el archivo VRPPD
def parse_vrppd_file(file_path):
    nodes = []
    depot = None
    in_coord_section = False

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith("NODE_COORD_SECTION"):
                in_coord_section = True
            elif "SECTION" in line and in_coord_section:
                break  
            elif in_coord_section and line != "":
                parts = line.split()
                node_id = int(parts[0])
                x = float(parts[1])
                y = float(parts[2])
                if depot is None:
                    depot = {'id': node_id, 'x': x, 'y': y, 'is_depot': True}
                else:
                    nodes.append({'id': node_id, 'x': x, 'y': y, 'is_depot': False})

    return depot, nodes


def distancia(nodo_a, nodo_b):
    return math.sqrt((nodo_a['x'] - nodo_b['x'])**2 + (nodo_a['y'] - nodo_b['y'])**2)


def construir_ruta(clientes, deposito):
    return [deposito] + random.sample(clientes, len(clientes)) + [deposito]


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


def grasp_vrp(deposito, clientes, metodo="2-opt", num_iteraciones=100):
    mejor_ruta = None
    mejor_costo = float('inf')

    start_time = time.time()

    for _ in range(num_iteraciones):
        ruta_inicial = construir_ruta(clientes, deposito)
        if metodo == "2-opt":
            ruta_optimizada = busqueda_local_2opt(ruta_inicial)
        elif metodo == "swap":
            ruta_optimizada = busqueda_local_swap(ruta_inicial)
        else:
            raise ValueError("Método de búsqueda local no válido. Usa '2-opt' o 'swap'.")

        costo = sum(distancia(ruta_optimizada[i], ruta_optimizada[i+1]) for i in range(len(ruta_optimizada) - 1))

        if costo < mejor_costo:
            mejor_ruta = ruta_optimizada
            mejor_costo = costo

    tiempo_total = time.time() - start_time
    return mejor_ruta, mejor_costo, tiempo_total

def animar_ruta(i, ruta, line):
    if i < len(ruta) - 1:
        x_coords = [nodo['x'] for nodo in ruta[:i+1]]
        y_coords = [nodo['y'] for nodo in ruta[:i+1]]
        line.set_data(x_coords, y_coords)
    return line,

def visualizar_ruta_animada(ruta):
    fig, ax = plt.subplots()
    ax.set_title("Construcción de la Ruta Paso a Paso")
    ax.set_xlabel("Coordenada X")
    ax.set_ylabel("Coordenada Y")

    
    for nodo in ruta:
        color = 'red' if nodo['is_depot'] else 'blue'
        ax.scatter(nodo['x'], nodo['y'], color=color)
        ax.text(nodo['x'], nodo['y'], f"{nodo['id']}", fontsize=9)

    
    line, = ax.plot([], [], linestyle='-', marker='o', color='green')

   
    ani = animation.FuncAnimation(
        fig, animar_ruta, frames=len(ruta), fargs=(ruta, line),
        interval=500, repeat=False
    )

    plt.show()


file_path = "mpdpsl20-1a.vrppd"  


deposito, clientes = parse_vrppd_file(file_path)


metodo = "2-opt"  # 2-opt o swap
mejor_ruta, mejor_costo, tiempo_total = grasp_vrp(deposito, clientes, metodo=metodo, num_iteraciones=1000)


print(f"Mejor ruta: {[n['id'] for n in mejor_ruta]}")
print(f"Costo: {mejor_costo}")
print(f"Tiempo total: {tiempo_total:.2f} segundos")


visualizar_ruta_animada(mejor_ruta)
