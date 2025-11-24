from flask import Flask, render_template, request
import sys
import os
from copy import deepcopy

#Backend
ruta_backend = os.path.join(os.path.dirname(__file__), 'BackEnd')
sys.path.append(ruta_backend)
from UCS_P import load_data, ucs
from fuzzy import compute_weather, compute_noise, compute_safety

def apply_penalties(adj, penalty_dict):
    adj_mod = deepcopy(adj)
    for node, edges in adj_mod.items():
        p = penalty_dict.get(node, 0)  # default: no penalty
        for i, (neighbor, w) in enumerate(edges):
            adj_mod[node][i] = (neighbor, w + p)
    return adj_mod

def compute_penalties(adj, user_weights):
    # --- Static simulated environmental variables ---
    temp = 27        # Celsius
    rain = 0.15      # probability
    crowd = 0.55     # 0–1
    traffic = 0.35   # 0–1
    vigilance = 0.42 # 0–1

    # --- User preference weights (0–1) ---
    w_weather = user_weights["w_weather"]
    w_noise   = user_weights["w_noise"]
    w_safety  = user_weights["w_safety"]

    # --- Compute discomfort 0–10 ---
    weather_disc = compute_weather(temp, rain)
    noise_disc   = compute_noise(crowd, traffic)
    safety_disc  = compute_safety(crowd, vigilance)

    # --- Weighted discomfort ---
    weather_w = weather_disc * w_weather
    noise_w   = noise_disc   * w_noise
    safety_w  = safety_disc  * w_safety
    avg_discomfort = (weather_w + noise_w + safety_w) / 3
    multiplier = 1 + (avg_discomfort / 10)

    # --- Penalty per node ---
    penalties = {}
    for node in adj.keys():
        penalties[node] = multiplier

    return penalties


app = Flask(__name__)

@app.route("/")
def index():
    stops_to_routes, _ = load_data()

    routes = sorted({r for routes in stops_to_routes.values() for r in routes})

    route_to_stops = {}
    for est, lineas in stops_to_routes.items():
        for linea in lineas:
            route_to_stops.setdefault(linea, []).append(est)

    # Sort stations alphabetically
    for linea in route_to_stops:
        route_to_stops[linea].sort()

    return render_template("index.html",
                           routes=routes,
                           route_to_stops=route_to_stops)

@app.route("/buscar", methods=["POST"])
def buscar():
    ruta_o = request.form["ruta_origen"]
    est_o  = request.form["estacion_origen"]
    ruta_d = request.form["ruta_destino"]
    est_d  = request.form["estacion_destino"]

    start = f"{est_o}:{ruta_o}"
    goal  = f"{est_d}:{ruta_d}"

    station_to_lines, adj = load_data()

    if start not in adj or goal not in adj:
        return render_template("resultado.html",
                               encontrado=False,
                               mensaje="We couldn't find one of the stations in the graph. HOW DID YOU EVEN MANAGE TO DO THAT?")
    user_weights = {
        "w_weather": float(request.form.get("w_weather", 0)),
        "w_noise": float(request.form.get("w_noise", 0)),
        "w_safety": float(request.form.get("w_safety", 0))
    }   
    
    fuzzy_search = ("fuzzy_active" in request.form and request.form["fuzzy_active"] == "on")
    if fuzzy_search:
        penalties = compute_penalties(adj, user_weights)
        adj_use = apply_penalties(adj,penalties)
    else:
        adj_use = adj
        
    costo, ruta = ucs(adj_use, start, goal)

    if not ruta:
        return render_template("resultado.html",
                               encontrado=False,
                               mensaje="We couldn't find a proper route for you, sorry!")
    pasos = []
    for n in ruta:
        est, ln = n.split(":")
        pasos.append((est, ln))

    return render_template("resultado.html",
                           encontrado=True,
                           costo=costo,
                           pasos=pasos)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
