import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

#Each systme uses the user inputs to compute an estimate discomfort
# using fuzzy logic.

# WEATHER SYSTEM  (temperature + rain -> weather)
temperature = ctrl.Antecedent(np.arange(0, 11, 1), 'temperature')
rain        = ctrl.Antecedent(np.arange(0, 11, 1), 'rain')
weather     = ctrl.Consequent(np.arange(0, 11, 1), 'weather')
temperature['cold']  = fuzz.trimf(temperature.universe, [0, 0, 4])
temperature['mild']  = fuzz.trimf(temperature.universe, [2, 5, 8])
temperature['hot']   = fuzz.trimf(temperature.universe, [6, 10, 10])
rain['none']   = fuzz.trimf(rain.universe, [0, 0, 3])
rain['light']  = fuzz.trimf(rain.universe, [2, 5, 7])
rain['heavy']  = fuzz.trimf(rain.universe, [6, 10, 10])
weather['good']     = fuzz.trimf(weather.universe, [0, 0, 4])
weather['moderate'] = fuzz.trimf(weather.universe, [3, 5, 7])
weather['bad']      = fuzz.trimf(weather.universe, [6, 10, 10])

# Rules
weather_rules = [
    ctrl.Rule(temperature['hot'] & rain['none'],   weather['moderate']),
    ctrl.Rule(temperature['hot'] & rain['light'],  weather['good']),
    ctrl.Rule(temperature['hot'] & rain['heavy'],  weather['bad']),
    ctrl.Rule(temperature['mild'] & rain['none'], weather['good']),
    ctrl.Rule(temperature['mild'] & rain['light'], weather['moderate']),
    ctrl.Rule(temperature['mild'] & rain['heavy'], weather['bad']),
    ctrl.Rule(temperature['cold'] & rain['none'],  weather['moderate']),
    ctrl.Rule(temperature['cold'] & rain['light'], weather['bad']),
    ctrl.Rule(temperature['cold'] & rain['heavy'], weather['bad'])
]

# NOISE SYSTEM (crowd + traffic -> noise)
crowd   = ctrl.Antecedent(np.arange(0, 11, 1), 'crowd')
traffic = ctrl.Antecedent(np.arange(0, 11, 1), 'traffic')
noise   = ctrl.Consequent(np.arange(0, 11, 1), 'noise')
crowd['low']    = fuzz.trimf(crowd.universe, [0, 0, 4])
crowd['medium'] = fuzz.trimf(crowd.universe, [2, 5, 8])
crowd['high']   = fuzz.trimf(crowd.universe, [6, 10, 10])
traffic['light']  = fuzz.trimf(traffic.universe, [0, 0, 4])
traffic['medium'] = fuzz.trimf(traffic.universe, [2, 5, 8])
traffic['heavy']  = fuzz.trimf(traffic.universe, [6, 10, 10])
noise['quiet'] = fuzz.trimf(noise.universe, [0, 0, 4])
noise['normal'] = fuzz.trimf(noise.universe, [3, 5, 7])
noise['loud'] = fuzz.trimf(noise.universe, [6, 10, 10])
noise_rules = [
    ctrl.Rule(crowd['high']   & traffic['heavy'],  noise['loud']),
    ctrl.Rule(crowd['high']   & traffic['medium'], noise['loud']),
    ctrl.Rule(crowd['high']   & traffic['light'], noise['normal']),
    ctrl.Rule(crowd['medium'] & traffic['heavy'],  noise['loud']),
    ctrl.Rule(crowd['medium'] & traffic['medium'],  noise['normal']),
    ctrl.Rule(crowd['medium'] & traffic['light'],  noise['quiet']),
    ctrl.Rule(crowd['low']    & traffic['heavy'],  noise['normal']),
    ctrl.Rule(crowd['low']    & traffic['medium'],  noise['quiet']),
    ctrl.Rule(crowd['low']    & traffic['light'],  noise['quiet'])
]

# SAFETY SYSTEM (crowd + vigilance -> safety)
vigilance = ctrl.Antecedent(np.arange(0, 11, 1), 'vigilance')
safety    = ctrl.Consequent(np.arange(0, 11, 1), 'safety')
vigilance['low']    = fuzz.trimf(vigilance.universe, [0, 0, 4])
vigilance['medium'] = fuzz.trimf(vigilance.universe, [2, 5, 8])
vigilance['high']   = fuzz.trimf(vigilance.universe, [6, 10, 10])
safety['unsafe'] = fuzz.trimf(safety.universe, [6, 10, 10])
safety['unsure'] = fuzz.trimf(safety.universe, [3, 5, 7])
safety['safe']   = fuzz.trimf(safety.universe, [0, 0, 4])
safety_rules = [
    ctrl.Rule(crowd['high']   & vigilance['low'],    safety['unsafe']),
    ctrl.Rule(crowd['high']   & vigilance['medium'],   safety['safe']),
    ctrl.Rule(crowd['high']   & vigilance['high'],   safety['unsure']),
    ctrl.Rule(crowd['medium'] & vigilance['low'], safety['unsure']),
    ctrl.Rule(crowd['medium'] & vigilance['medium'], safety['safe']),
    ctrl.Rule(crowd['medium'] & vigilance['high'], safety['safe']),
    ctrl.Rule(crowd['low']    & vigilance['low'],   safety['unsure']),
    ctrl.Rule(crowd['low']    & vigilance['medium'],    safety['safe']),
    ctrl.Rule(crowd['low']    & vigilance['high'],    safety['safe'])
]

# BUILD CONTROLLERS
weather_ctrl = ctrl.ControlSystem(weather_rules)
noise_ctrl   = ctrl.ControlSystem(noise_rules)
safety_ctrl  = ctrl.ControlSystem(safety_rules)
weather_sim = ctrl.ControlSystemSimulation(weather_ctrl)
noise_sim   = ctrl.ControlSystemSimulation(noise_ctrl)
safety_sim  = ctrl.ControlSystemSimulation(safety_ctrl)

# PUBLIC FUNCTIONS FOR FLASK
def compute_weather(temp_value, rain_value):
    weather_sim.input['temperature'] = temp_value
    weather_sim.input['rain'] = rain_value
    weather_sim.compute()
    return weather_sim.output['weather']

def compute_noise(crowd_value, traffic_value):
    noise_sim.input['crowd'] = crowd_value
    noise_sim.input['traffic'] = traffic_value
    noise_sim.compute()
    return noise_sim.output['noise']

def compute_safety(crowd_value, vigilance_value):
    safety_sim.input['crowd'] = crowd_value
    safety_sim.input['vigilance'] = vigilance_value
    safety_sim.compute()
    return safety_sim.output['safety']


#print(f"tEST AMOUNT: {compute_noise(5, 10)}")  # Example test