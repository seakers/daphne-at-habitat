import numpy as np
import matplotlib.pyplot as plt
import requests
import os
import json
import time
from datetime import datetime
# Simulation settings
real_time_mode = True  # Set to False to run as fast as possible
simulation_speed = 1.0  # 1.0 = real-time (1 second per step), 2.0 = 2x faster, etc.


# File path to the JSON file
json_file_path = 'jsonfile/sim_data.json'

# URL to post to
# url = 'https://daphne-at-lab.selva-research.com/api/at/receiveHeraFeed'
url = 'http://localhost:8002/api/at/receiveHeraFeed'


PARAMETER_INFO1 = {
    "ppO2": {"DisplayName": "Cabin_ppO2", "Id": 43, "ParameterGroup": "L1", "NominalValue": 163.81,
             "UpperCautionLimit": 175.0, "UpperWarningLimit": 185.0, "LowerCautionLimit": 155.0,
             "LowerWarningLimit": 145.0, "Divisor": 100, "Name": "ppO2", "Unit":"mmHg"},
    "ppCO2": {"DisplayName": "Cabin_ppCO2", "Id": 44, "ParameterGroup": "L1", "NominalValue": 0.4,
              "UpperCautionLimit": 4.5, "UpperWarningLimit": 6.0, "LowerCautionLimit": -1.0,
              "LowerWarningLimit": -2.0, "Divisor": 100, "Name": "ppCO2", "Unit":"mmHg"},
    "humidity": {"DisplayName": "Humidity", "Id": 45, "ParameterGroup": "L1", "NominalValue": 52,
              "UpperCautionLimit": 61, "UpperWarningLimit": 70, "LowerCautionLimit": 50,
              "LowerWarningLimit": 40, "Divisor": 1, "Name": "Humidity", "Unit":"L"},
    "ppO21": {"DisplayName": "Cabin_ppO2", "Id": 46, "ParameterGroup": "L2", "NominalValue": 163.81,
             "UpperCautionLimit": 175.0, "UpperWarningLimit": 185.0, "LowerCautionLimit": 155.0,
             "LowerWarningLimit": 145.0, "Divisor": 100, "Name": "ppO2", "Unit":"mmHg"},
    "ppCO21": {"DisplayName": "Cabin_ppCO2", "Id": 47, "ParameterGroup": "L2", "NominalValue": 0.4,
              "UpperCautionLimit": 4.5, "UpperWarningLimit": 6.0, "LowerCautionLimit": -1.0,
              "LowerWarningLimit": -2.0, "Divisor": 100, "Name": "ppCO2", "Unit":"mmHg"},
    "humidity1": {"DisplayName": "Humidity", "Id": 48, "ParameterGroup": "L2", "NominalValue": 52,
              "UpperCautionLimit": 61, "UpperWarningLimit": 70, "LowerCautionLimit": 50,
              "LowerWarningLimit": 40, "Divisor": 1, "Name": "Humidity", "Unit":"L"},
    "H2O": {"DisplayName": "H2O", "Id": 49, "ParameterGroup": "Crew", "NominalValue": 3.6,
              "UpperCautionLimit": 4.5, "UpperWarningLimit": 5.0, "LowerCautionLimit": 2.5,
              "LowerWarningLimit": 2.0, "Divisor": 1, "Name": "H2O", "Unit":"L"},
    "CabinTemperature": {"DisplayName": "Cabin Temperature", "Id": 49, "ParameterGroup": "L1", "NominalValue": 72.3,
              "UpperCautionLimit": 79.0, "UpperWarningLimit": 87.7, "LowerCautionLimit": 68,
              "LowerWarningLimit": 64, "Divisor": 1, "Name": "Cabin Temperature", "Unit":"L"},
    "CabinTemperature1": {"DisplayName": "Cabin Temperature", "Id": 49, "ParameterGroup": "L2", "NominalValue": 72.3,
              "UpperCautionLimit": 79.0, "UpperWarningLimit": 87.7, "LowerCautionLimit": 68,
              "LowerWarningLimit": 64, "Divisor": 1, "Name": "Cabin Temperature", "Unit":"L"},
     "SOXIE": {"DisplayName": "SOXIE Stack Temp", "Id": 49, "ParameterGroup": "", "NominalValue": 1481,
              "UpperCautionLimit": 1629, "UpperWarningLimit": 1670, "LowerCautionLimit": 1333,
              "LowerWarningLimit": 1292, "Divisor": 1, "Name": "SOXIE Stack Temp", "Unit":"L"},
    "MOXIE": {"DisplayName": "MOXIE Compressor Temp", "Id": 49, "ParameterGroup": "", "NominalValue": 160,
              "UpperCautionLimit": 170, "UpperWarningLimit": 180, "LowerCautionLimit": 140,
              "LowerWarningLimit": 120, "Divisor": 1, "Name": "MOXIE Compressor Temp", "Unit":"L"},
    
    
    # "temperature": {"DisplayName": "Cabin_Temperature", "Id": 46, "ParameterGroup": "L1", "NominalValue": 100,
    #           "UpperCautionLimit": 79.0, "UpperWarningLimit": 87.7, "LowerCautionLimit": 68.0,
    #           "LowerWarningLimit": 64.0, "Divisor": 1, "Name": "Cabin Temperature", "Unit":"F"},
    # "temperature": {"DisplayName": "Cabin_Temperature", "Id": 46, "ParameterGroup": "L1", "NominalValue": 100,
    #           "UpperCautionLimit": 79.0, "UpperWarningLimit": 87.7, "LowerCautionLimit": 68.0,
    #           "LowerWarningLimit": 64.0, "Divisor": 1, "Name": "Cabin Temperature", "Unit":"F"},
}

# 

PARAMETER_INFO = {
    "ppO2": PARAMETER_INFO1["ppO2"],
    "ppCO2": PARAMETER_INFO1["ppCO2"],
    "ppO21": PARAMETER_INFO1["ppO21"],
    "ppCO21": PARAMETER_INFO1["ppCO21"],
    # "H2O": PARAMETER_INFO1["H2O"],
    "humidity": PARAMETER_INFO1["humidity"],
    "humidity1": PARAMETER_INFO1["humidity1"],
    # "CabinTemperature": PARAMETER_INFO1["CabinTemperature"],
    # "CabinTemperature1": PARAMETER_INFO1["CabinTemperature1"],
    # "SOXIE": PARAMETER_INFO1["SOXIE"],
    # "MOXIE": PARAMETER_INFO1["MOXIE"],
}

cabin = {
    "ppO2": 165, 
    "ppCO2": 0.5, 
    "humidity": 52, 
    # "CabinTemperature": 80.0, 
     "ppO21": 165, 
    "ppCO21": 0.5, 
    "humidity1": 52, 
    # "CabinTemperature1": 80.0, 
    # "H2O": 3.5,
    # "SOXIE": 1480,
    # "MOXIE": 172,
}

# Simulate over time
time_steps = 10000
counter = [0]
def simulate_step(cabin):
    """
    Simulates one time step in the ECLSS system, applying failures and subsystem dynamics.
    """
    if counter[0] > 10:
        cabin = {
            "ppO2": 165, 
            "ppCO2": 6, 
            "humidity": 52, 
            "ppO21": 165, 
            "ppCO21": 6, 
            "humidity1": 52, 
   
        }
        return cabin

    counter[0] += 1
    return cabin

def post_json_to_url():
    try:
        # Read the JSON file
        with open(json_file_path, 'r') as file:
            json_data = json.load(file)  # Load JSON data from the file
            
        print(f"Sending request to: {url}")

        # Make the POST request
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=json_data, headers=headers, timeout=5)
        # response = requests.post(url, json=json_data)

        # Print the response status and data
        if response.status_code == 200:
            print("Success:", response.json())
        else:
            print("Failed:", response.status_code)
            # print(f"Response content: {response.text}")
    except KeyboardInterrupt:
        print("Stopped by user.")
    except Exception as e:
        print("An error occurred:", e)


def create_parameter_entry(param_name, cabin):
    """
    Creates a parameter entry for the JSON data structure.
    Args:
        param_name (str): The name of the parameter (e.g., "ppO2", "water").
        cabin (dict): The dictionary containing the current cabin state.
    Returns:
        dict: A dictionary representing the parameter entry for the JSON structure.
    """
    print(cabin)
    param_info = PARAMETER_INFO[param_name]
    current_value = cabin[param_name]

    current_value_display = current_value
    unit = param_info["Unit"]

    parameter_entry = {
        "SimulatedParameter": True,
        "DisplayName": param_info["DisplayName"],
        "DisplayValue": f"{current_value_display} {unit}",
        "Id": param_info["Id"],
        "Name": param_info["Name"],
        "ParameterGroup": param_info["ParameterGroup"],
        "NominalValue": param_info["NominalValue"],
        "UpperCautionLimit": param_info["UpperCautionLimit"],
        "UpperWarningLimit": param_info["UpperWarningLimit"],
        "LowerCautionLimit": param_info["LowerCautionLimit"],
        "LowerWarningLimit": param_info["LowerWarningLimit"],
        "Divisor": param_info["Divisor"],
        "Unit": unit,
        "SimValue": current_value_display,
        "noise": 0.01,
        "currentValue": current_value_display,
        "CurrentValue": current_value_display,
        "simulationValue": current_value_display,
        "Status": {
            "LowerWarning": current_value < param_info["LowerWarningLimit"],
            "LowerCaution": current_value < param_info["LowerCautionLimit"],
            "Nominal": param_info["LowerCautionLimit"] <= current_value <= param_info["UpperCautionLimit"],
            "UpperCaution": current_value > param_info["UpperCautionLimit"],
            "UpperWarning": current_value > param_info["UpperWarningLimit"],
            "UnderLimit": current_value < param_info["LowerWarningLimit"],
            "OverLimit": current_value > param_info["UpperWarningLimit"],
            "Caution": current_value < param_info["LowerCautionLimit"] or current_value > param_info["UpperCautionLimit"],
            "Warning": current_value < param_info["LowerWarningLimit"] or current_value > param_info["UpperWarningLimit"]
        },
        "HasDuplicationError": False,
        "DuplicationError": None
    }
    return parameter_entry

# Function to save JSON data with a unique filename
def create_json():
    """Save simulation telemetry data with a specific structured format."""
    folder_path = os.path.join(os.getcwd(), "jsonfile")
    os.makedirs(folder_path, exist_ok=True)  # Ensure the directory exists

    # Generate a timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"sim_data.json"
    file_path = os.path.join(folder_path, file_name)


    parameters_list = [create_parameter_entry(param_name, cabin) for param_name in PARAMETER_INFO]

    habitat_status = {
        "habitatStatus": {
            "Parameters": parameters_list,
            "MasterStatus": {
                "Caution": any(p["Status"]["Caution"] for p in parameters_list),
                "Warning": any(p["Status"]["Warning"] for p in parameters_list)
            },
            "HardwareList": [],
            "SimulationList": [],
            "Timestamp": datetime.now().strftime("MD %j %H:%M:%S")  # Mission day format
        }
    }

    # Save the JSON file
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(habitat_status, json_file, indent=4)

    print(f"JSON file saved at: {file_path}")

    post_json_to_url()


# Main simulation loop with controlled or unrestricted time steps
for t in range(time_steps):
    start_time = time.time()  # Record start time of the timestep

    # subsystems = check_limits_and_control(cabin, subsystems)
    cabin = simulate_step(cabin)
  
    # Save telemetry data
    create_json()
   
    if real_time_mode:
        elapsed_time = time.time() - start_time
        sleep_time = max(0, (1.0 / simulation_speed) - elapsed_time)  # Ensure non-negative sleep time
        time.sleep(sleep_time)  # Pause before next timestep


    

