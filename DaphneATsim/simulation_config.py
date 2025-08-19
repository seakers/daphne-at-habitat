#!/usr/bin/env python3
"""
Configuration file for the integrated CDRA simulation

To test different failure scenarios, you can:
1. Modify the CDRA_FAILURES dictionary below
2. Or use one of the EXAMPLE_FAILURE_CONFIGS by copying it to CDRA_FAILURES
3. Or modify the failure parameters during simulation

Available failure types:
- filter_saturation: Absorption beds become fully saturated
- valve_stuck: Valves get stuck in current position
- heater_failure: Specific heaters stop working (list of component names)
- fan_degraded: Reduced air flow rates
"""

REAL_TIME_MODE = True  # Set to False to run as fast as possible (no delays, for testing)
SIMULATION_SPEED = 50  # How many simulation steps to generate per real second
TELEMETRY_FREQUENCY_HZ = 1.0  # How many telemetry posts per real second (e.g., 1.0 = every 1 second)
TIME_STEPS = 100000  # Total number of simulation steps
ENABLE_PLOTTING = False # Whether to show matplotlib plots after simulation

# Timing behavior:
# - If SIMULATION_SPEED = 10 and TELEMETRY_FREQUENCY_HZ = 1.0:
#   - Generate 10 simulation steps per real second
#   - Post telemetry once per second (after 10 steps)
#   - Sleep for remaining time to maintain real-world timing
# - Set REAL_TIME_MODE = False to run without delays (useful for testing)

# CDRA failure scenario configuration
CDRA_FAILURES = {
    'filter_saturation': False,
    'filter_saturation_start': 0,  # When filter saturation failure starts
    'filter_saturation_end': TIME_STEPS,    # When filter saturation failure ends
    
    'valve_stuck': True,
    'valve_stuck_start': 0,       # When valve stuck failure starts
    'valve_stuck_end': TIME_STEPS,         # When valve stuck failure ends
    
    'heater_failure': [],             # List of failed heaters (e.g., ['desiccant_1', 'sorbent_2'])
    
    'fan_degraded': False,
    'fan_degraded_start': 0,      # When fan degradation starts
    'fan_degraded_end': TIME_STEPS,        # When fan degradation ends
    'degraded_flow_rate': 0.38        # Degraded flow rate (kg/s)
}

# Telemetry settings
JSON_FILE_PATH = 'jsonfile/sim_data.json'
TELEMETRY_URL = 'http://localhost:8002/api/at/receiveHeraFeed'
# TELEMETRY_URL = 'https://daphne-at-lab.selva-research.com/api/at/receiveHeraFeed'


# Environmental parameters - matching the referenced simulator
CO2_CONTENT_INIT = 3  # mmHg, initial CO2 partial pressure

# Unit conversion constants - matching the referenced simulator exactly
STANDARD_PRESSURE_MMHG = 760.0
MOLAR_MASS_CO2 = 44.01  # g/mol
MOLAR_MASS_AIR = 28.97  # g/mol
# GAS_CONSTANT_R = 8.314  # J/(mol·K)
# STANDARD_TEMPERATURE_K = 298.15  # 25°C in Kelvin

# Legacy conversion factor (keeping for backward compatibility)
# CO2_TO_MMHG_FACTOR = STANDARD_PRESSURE_MMHG * MOLAR_MASS_CO2 / MOLAR_MASS_AIR

