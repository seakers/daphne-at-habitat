import numpy as np
import matplotlib.pyplot as plt
import requests
import os
import json
import time
from datetime import datetime
from CDRA import CDRAState, timestep, control, update_cabin_concentration, plot_results
from simulation_config import *

# Unit conversion functions - matching the referenced simulator exactly
def mmhg_to_kg_per_kg_air(co2_mmhg: float) -> float:
    """
    Convert CO2 partial pressure from mmHg to kg/kg air.
    Matches the referenced simulator implementation exactly.
    
    Args:
        co2_mmhg: CO2 partial pressure in mmHg
        
    Returns:
        CO2 concentration in kg/kg air
    """
    # Convert mmHg to Pa (1 mmHg = 133.322 Pa)
    co2_pa = co2_mmhg * 133.322
    
    # Use ideal gas law: n/V = P/(RT)
    # Then convert to mass ratio: (n_CO2 * M_CO2) / (n_air * M_air)
    # Since we're working with ratios, we can simplify
    co2_mol_per_mol_air = co2_pa / (STANDARD_PRESSURE_MMHG * 133.322)
    
    # Convert to mass ratio
    co2_kg_per_kg_air = co2_mol_per_mol_air * (MOLAR_MASS_CO2 / MOLAR_MASS_AIR)
    
    return co2_kg_per_kg_air

def kg_per_kg_air_to_mmhg(co2_kg_per_kg_air: float) -> float:
    """
    Convert CO2 concentration from kg/kg air to mmHg.
    Matches the referenced simulator implementation exactly.
    
    Args:
        co2_kg_per_kg_air: CO2 concentration in kg/kg air
        
    Returns:
        CO2 partial pressure in mmHg
    """
    # Convert mass ratio to molar ratio
    co2_mol_per_mol_air = co2_kg_per_kg_air * (MOLAR_MASS_AIR / MOLAR_MASS_CO2)
    
    # Convert to partial pressure in Pa
    co2_pa = co2_mol_per_mol_air * (STANDARD_PRESSURE_MMHG * 133.322)
    
    # Convert Pa to mmHg
    co2_mmhg = co2_pa / 133.322
    
    return co2_mmhg

# Initialize CDRA state
cdra_state = CDRAState()

# Convert initial CO2 from mmHg to kg/kg for CDRA simulation using proper conversion
cdra_state.co2_content = mmhg_to_kg_per_kg_air(CO2_CONTENT_INIT)

# Override CDRA failure scenarios with config
from CDRA import FAILURE_SCENARIO
FAILURE_SCENARIO.update(CDRA_FAILURES)

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
              "LowerWarningLimit": 120, "Divisor": 1, "Name": "MOXIE Compressor Temp", "Unit":"L"}
}

PARAMETER_INFO = {
    "ppO2": PARAMETER_INFO1["ppO2"],
    "ppCO2": PARAMETER_INFO1["ppCO2"],
    "ppO21": PARAMETER_INFO1["ppO21"],
    "ppCO21": PARAMETER_INFO1["ppCO21"],
    "humidity": PARAMETER_INFO1["humidity"],
    "humidity1": PARAMETER_INFO1["humidity1"]
}

# Initialize cabin state with dynamic ppCO2 from CDRA
cabin = {
    "ppO2": 165, 
    "ppCO2": 0.5,  # Will be updated dynamically by CDRA
    "humidity": 52, 
    "ppO21": 165, 
    "ppCO21": 0.5,  # Will be updated dynamically by CDRA
    "humidity1": 52, 
}


def simulate_step(cdra_state):
    """
    Simulates one time step in the ECLSS system, applying failures and subsystem dynamics.
    Now integrates CDRA simulation for dynamic ppCO2 updates.
    """
    try:
        # Apply CDRA control and simulation
        control(cdra_state)
        
        # Get CO2 concentration from CDRA simulation
        C_out, flow = timestep(cdra_state)
        update_cabin_concentration(cdra_state, C_out, flow)
        
        # Convert CO2 content (kg/kg) to partial pressure (mmHg)
        # Using the proper conversion function that matches the referenced simulator
        ppco2_mmhg = kg_per_kg_air_to_mmhg(cdra_state.co2_content)
        
        # Update cabin state with dynamic values from CDRA
        cabin.update({
            "ppO2": 165, 
            "ppCO2": round(ppco2_mmhg, 2),  # Dynamic from CDRA
            "humidity": 52, 
            "ppO21": 165, 
            "ppCO21": round(ppco2_mmhg, 2),  # Dynamic from CDRA
            "humidity1": 52, 
        })
        
        # Update CDRA state time
        cdra_state.time += 1
        
        # Debug output every 100 steps
        if cdra_state.time % 100 == 0:
            print(f"Step {cdra_state.time}: CO2 content = {cdra_state.co2_content:.6f}, ppCO2 = {ppco2_mmhg:.2f} mmHg")
 
            
    except Exception as e:
        print(f"Error in CDRA simulation step: {e}")
        # Fallback to static values if CDRA fails
        cabin.update({
            "ppCO2": 0.5,
            "ppCO21": 0.5,
        })
    
    return 

def post_json_to_url():
    try:
        # Read the JSON file
        with open(JSON_FILE_PATH, 'r') as file:
            json_data = json.load(file)  # Load JSON data from the file
            
        print(f"Sending request to: {TELEMETRY_URL}")

        # Make the POST request
        headers = {'Content-Type': 'application/json'}
        response = requests.post(TELEMETRY_URL, json=json_data, headers=headers, timeout=5)

        # Print the response status and data
        if response.status_code == 200:
            print("Success:", response.json())
        else:
            print("Failed:", response.status_code)
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

def plot_cdra_debug():
    """Plot CDRA simulation results for debugging"""
    if cdra_state.time > 0 and ENABLE_PLOTTING:  # Only plot if we have data and plotting is enabled
        print("Generating CDRA debug plots...")
        plot_results(cdra_state)
        print("Plots displayed. Close plot windows to continue.")

def main():
    # Main simulation loop with controlled timing and telemetry frequency
    print(f"Starting integrated CDRA simulation...")
    print(f"Real-time mode: {REAL_TIME_MODE}")
    print(f"Simulation speed: {SIMULATION_SPEED}x (steps per real second)")
    print(f"Telemetry frequency: {TELEMETRY_FREQUENCY_HZ} Hz (posts per real second)")
    print(f"Total steps: {TIME_STEPS}")

    # Calculate timing parameters
    steps_per_telemetry_cycle = int(SIMULATION_SPEED / TELEMETRY_FREQUENCY_HZ)
    telemetry_cycle_duration = 1.0 / TELEMETRY_FREQUENCY_HZ  # seconds per telemetry cycle

    print(f"Steps per telemetry cycle: {steps_per_telemetry_cycle}")
    print(f"Telemetry cycle duration: {telemetry_cycle_duration:.3f} seconds")

    telemetry_counter = 0
    cycle_start_time = time.time()

    for t in range(TIME_STEPS):
        # Update cabin state with CDRA simulation
        cabin = simulate_step(cdra_state)
        
        # If real-time mode is enabled, post telemetry after completing the required number of steps
        if REAL_TIME_MODE:
            # Only create and post telemetry after completing the required number of steps
            if (t + 1) % steps_per_telemetry_cycle == 0:
                # Save telemetry data
                create_json()
                telemetry_counter += 1
                # Calculate how much time has passed in this cycle
                current_time = time.time()
                elapsed_in_cycle = current_time - cycle_start_time
                
                # Sleep for the remaining time to maintain real-world timing
                sleep_time = max(0, telemetry_cycle_duration - elapsed_in_cycle)
                if sleep_time > 0:
                    print(f"Cycle {telemetry_counter}: {steps_per_telemetry_cycle} steps in {elapsed_in_cycle:.3f}s, sleeping for {sleep_time:.3f}s")
                    time.sleep(sleep_time)
                else:
                    print(f"Cycle {telemetry_counter}: {steps_per_telemetry_cycle} steps in {elapsed_in_cycle:.3f}s (behind schedule)")
                
                # Reset cycle timer
                cycle_start_time = time.time()
        else:
            # For non-telemetry steps, just continue without delay
            pass

        # Collect data for debugging plots
        if ENABLE_PLOTTING:
            cdra_state.history['time'].append(cdra_state.time)
            cdra_state.history['moisture_content'].append(cdra_state.moisture_content)
            cdra_state.history['co2_content'].append(kg_per_kg_air_to_mmhg(cdra_state.co2_content))
            cdra_state.history['co2_removed'].append(cdra_state.co2_removed_total)
            cdra_state.history['air_flow_rate'].append(cdra_state.air_flow_rate)
            cdra_state.history['desiccant_heaters'].append((cdra_state.heater_on['desiccant_1'], cdra_state.heater_on['desiccant_3']))
            cdra_state.history['sorbent_heaters'].append((cdra_state.heater_on['sorbent_2'], cdra_state.heater_on['sorbent_4']))
            cdra_state.history['active_path'].append(cdra_state.valve_state['path_1_active'])
            cdra_state.history['desiccant_1_heater'].append(int(cdra_state.heater_on['desiccant_1']))
            cdra_state.history['desiccant_3_heater'].append(int(cdra_state.heater_on['desiccant_3']))
            cdra_state.history['sorbent_2_heater'].append(int(cdra_state.heater_on['sorbent_2']))
            cdra_state.history['sorbent_4_heater'].append(int(cdra_state.heater_on['sorbent_4']))
            
            # Collect saturation and adsorption efficiency data consistently
            for k in ['desiccant_1', 'desiccant_3', 'sorbent_2', 'sorbent_4']:
                cdra_state.history['saturation'][k].append(cdra_state.saturation[k])
                cdra_state.history['adsorption_eff'][k].append(cdra_state.adsorption_eff[k])
        else:
            pass


    # After simulation completes, show CDRA plots for debugging
    print(f"Simulation completed. Total telemetry posts: {telemetry_counter}")
    print("Showing CDRA debug plots...")
    plot_cdra_debug()
    print("Simulation finished.")

if __name__ == '__main__':
    main()



    

