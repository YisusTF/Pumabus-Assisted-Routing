from heapq import heappush, heappop
from collections import defaultdict
import os

#Translation in process

full_stops_txt = "BackEnd/vertices.txt"   # Estacion,Linea
transitions_txt  = "BackEnd/aristas.txt"    # Est1,Est2,Tiempo  
#transbord = True
t_transbordo = 2  

def load_data():
    if not os.path.exists(full_stops_txt) or not os.path.exists(transitions_txt):
        raise FileNotFoundError("Error while loading .txt files")
    station_to_lines = load_stops(full_stops_txt)       #Full Dictionary
    edges = load_road(transitions_txt)
    adj = build_graph(station_to_lines, edges)
    return station_to_lines, adj


#Get info form txt
def load_stops(path):
    station_to_lines = defaultdict(set)
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"): 
                continue
            est, ln = line.split(",")
            station_to_lines[est].add(ln)
    return station_to_lines

def load_road(path):
    edges = []
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            a, b, w = line.split(",")
            edges.append((a, b, int(w)))
    return edges

# Grafo 
def build_graph(station_to_lines, edges):
    adj = defaultdict(list)

    def add(u, v, w):
        adj[u].append((v, w))
        #adj[v].append((u, w))   Its a directed graph

    for a, b, w in edges:
        a_has = ":" in a
        b_has = ":" in b
        if a_has and b_has:
            add(a, b, w)
        elif (not a_has) and (not b_has):
            common = station_to_lines[a].intersection(station_to_lines[b])
            for ln in common:
                add(f"{a}:{ln}", f"{b}:{ln}", w)
        else:
            if a_has:
                _, ln = a.split(":", 1)
                if ln in station_to_lines.get(b, set()):
                    add(a, f"{b}:{ln}", w)
            else:
                _, ln = b.split(":", 1)
                if ln in station_to_lines.get(a, set()):
                    add(f"{a}:{ln}", b, w)

    #if transbordos:
    for est, lines in station_to_lines.items():
        ls = sorted(lines)
        for i in range(len(ls)):
            for j in range(i + 1, len(ls)):
                u, v = f"{est}:{ls[i]}", f"{est}:{ls[j]}"
                add(u, v, t_transbordo)

    return adj

# UCS 
def ucs(adj, start, goal):
    pq = [(0, start)]
    best = {start: 0}
    parent = {start: None}
    while pq:
        cost, u = heappop(pq)
        if u == goal:
            path = []
            while u is not None:
                path.append(u)
                u = parent[u]
            path.reverse()
            return cost, path
        if cost > best.get(u, float("inf")):
            continue
        for v, w in adj.get(u, []):
            nc = cost + w
            if nc < best.get(v, float("inf")):
                best[v] = nc
                parent[v] = u
                heappush(pq, (nc, v))
    return None, []

# Opciones
def select_line(station_to_lines):
    every_stop = sorted({ln for ls in station_to_lines.values() for ln in ls})
    print("\nAvaliable lines:")
    for i, ln in enumerate(every_stop, 1):
        print(f"  {i}) {ln}")
    while True:
        s = input("Select a line: ").strip()
        if s.isdigit() and 1 <= int(s) <= len(every_stop):
            return every_stop[int(s) - 1]
        print("Just one number D:")

def select_stop_inLine(ln, station_to_lines):
    ests = [e for e, ls in station_to_lines.items() if ln in ls]
    #ests = sorted([e for e, ls in station_to_lines.items() if ln in ls])
    print(f"\nStations from {ln}:")
    for i, est in enumerate(ests, 1):
        print(f"  {i}) {est}")
    while True:
        s = input("Select a station: ").strip()
        if s.isdigit():
            idx = int(s)
            if 1 <= idx <= len(ests):
                return ests[idx - 1]
        print("Just a number D:")
