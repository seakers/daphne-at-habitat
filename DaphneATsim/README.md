# Integrated CDRA Simulation with Telemetry

This system integrates the CDRA (Carbon Dioxide Removal Assembly) simulation with real-time telemetry generation for space habitat monitoring.

## Overview

The system combines:
- **CDRA.py**: Advanced CO2 removal simulation with failure scenarios
- **simulation.py**: Main telemetry generation and HTTP posting with CDRA integration
- **simulation_config.py**: Centralized configuration management
- **jsonurl.py**: Utility for JSON file handling

## Features

- **Real-time simulation**: Configurable timing (real-time or fast simulation)
- **Dynamic CO2 telemetry**: ppCO2 values are dynamically calculated from CDRA simulation
- **Failure injection**: Configurable CDRA failure scenarios (filter saturation, valve stuck, heater failure, fan degradation)
- **Telemetry posting**: Automatic JSON generation and HTTP posting at configurable frequency
- **Debug plotting**: Matplotlib visualization of CDRA simulation results
- **Error handling**: Graceful fallback if CDRA simulation fails
- **Full compatibility**: Generates identical parameters to the referenced CDRA simulator

## Files

- `simulation.py` - Main simulation loop with CDRA integration and telemetry generation
- `CDRA.py` - CDRA simulation framework with failure scenarios
- `simulation_config.py` - Configuration parameters for simulation behavior
- `jsonurl.py` - JSON file handling utilities
- `test_integration.py` - Test script for CDRA integration
- `test_compatibility.py` - Compatibility test with referenced simulator
- `test_failures.py` - Test script for CDRA failure scenarios
- `jsonfile/sim_data.json` - Generated telemetry data

## Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify installation**:
   ```bash
   python -c "import numpy, matplotlib, requests; print('Dependencies installed successfully')"
   ```

## Configuration

Edit `simulation_config.py` to modify:

### **Timing Configuration:**
- **REAL_TIME_MODE**: Set to `True` for real-time simulation with delays, `False` for fast simulation
- **SIMULATION_SPEED**: Number of simulation steps per real second (default: 10)
- **TELEMETRY_FREQUENCY_HZ**: Telemetry posting frequency in Hz (default: 1.0 = every second)
- **TIME_STEPS**: Total number of simulation steps (default: 100000)
- **ENABLE_PLOTTING**: Whether to show matplotlib plots after simulation

### **CDRA Failure Scenarios:**
```python
CDRA_FAILURES = {
    'filter_saturation': False,        # Absorption bed saturation
    'filter_saturation_start': 0,      # When failure starts
    'filter_saturation_end': 1000,     # When failure ends
    
    'valve_stuck': True,               # Valve stuck in position
    'valve_stuck_start': 0,            # When failure starts
    'valve_stuck_end': 1000,           # When failure ends
    
    'heater_failure': [],              # List of failed heaters
    'fan_degraded': False,             # Reduced air flow
    'fan_degraded_start': 0,           # When degradation starts
    'fan_degraded_end': 1000,          # When degradation ends
    'degraded_flow_rate': 0.38         # Degraded flow rate (kg/s)
}
```

### **Telemetry Settings:**
- **JSON_FILE_PATH**: Path for generated telemetry data
- **TELEMETRY_URL**: HTTP endpoint for posting telemetry data

## Usage

### **Quick Start**

1. **Run the main simulation**:
   ```bash
   python simulation.py
   ```

2. **Test CDRA integration**:
   ```bash
   python test_integration.py
   ```

3. **Test compatibility** (verify identical parameters):
   ```bash
   python test_compatibility.py
   ```

4. **Test failure scenarios**:
   ```bash
   python test_failures.py
   ```

### **Configuration Examples**

**Real-time simulation with CDRA failures**:
```python
# In simulation_config.py
REAL_TIME_MODE = True
SIMULATION_SPEED = 10
TELEMETRY_FREQUENCY_HZ = 1.0
TIME_STEPS = 100000

CDRA_FAILURES = {
    'valve_stuck': True,
    'valve_stuck_start': 1000,
    'valve_stuck_end': 5000,
    'fan_degraded': True,
    'fan_degraded_start': 2000,
    'fan_degraded_end': 8000,
    'degraded_flow_rate': 0.5
}
```

**Fast simulation for testing**:
```python
# In simulation_config.py
REAL_TIME_MODE = False
TIME_STEPS = 1000
ENABLE_PLOTTING = True
```

**High-frequency telemetry**:
```python
# In simulation_config.py
TELEMETRY_FREQUENCY_HZ = 10.0  # Post telemetry 10 times per second
SIMULATION_SPEED = 100         # Generate 100 simulation steps per real second
```

## How It Works

### **Simulation Flow:**

1. **Initialization**: Creates CDRA state and initializes cabin parameters
2. **Per-step simulation**: 
   - Runs CDRA control and physics each step
   - Applies configured failure scenarios
   - Updates cabin CO2 concentration dynamically
3. **CO2 conversion**: Converts CDRA CO2 content (kg/kg) to ppCO2 (mmHg)
4. **Telemetry generation**: Creates structured JSON data with parameter status
5. **HTTP posting**: Posts telemetry to configured endpoint at specified frequency
6. **Timing control**: Maintains real-time synchronization or runs at maximum speed

### **CDRA Integration:**

The system integrates CDRA simulation by:
- **State management**: Maintains CDRA state throughout simulation
- **Failure injection**: Applies configurable failure scenarios
- **Dynamic CO2**: Updates ppCO2 values based on CDRA simulation results
- **Error handling**: Falls back to static values if CDRA simulation fails

### **Telemetry Structure:**

Generated telemetry includes:
- **Parameter data**: ppO2, ppCO2, humidity for L1 and L2 systems
- **Status information**: Caution/warning limits and current status
- **Simulation metadata**: Timestamps and simulation flags
- **Habitat status**: Master status and parameter groups

## Failure Scenarios

### **Supported Failure Types:**

- **Filter Saturation**: Absorption beds become fully saturated, reducing CO2 removal efficiency
- **Valve Stuck**: Valves get stuck in current position, preventing path switching
- **Heater Failure**: Specific heaters stop working, affecting regeneration cycles
- **Fan Degradation**: Reduced air flow rates, impacting overall system performance

### **Failure Testing:**

Use the included test script to verify failure scenarios:
```bash
python test_failures.py
```

## CO2 Conversion

The system uses exact unit conversion functions matching the referenced CDRA simulator:

**mmHg to kg/kg air:**
```python
co2_pa = co2_mmhg * 133.322
co2_mol_per_mol_air = co2_pa / (STANDARD_PRESSURE_MMHG * 133.322)
co2_kg_per_kg_air = co2_mol_per_mol_air * (MOLAR_MASS_CO2 / MOLAR_MASS_AIR)
```

**kg/kg air to mmHg:**
```python
co2_mol_per_mol_air = co2_kg_per_kg_air * (MOLAR_MASS_AIR / MOLAR_MASS_CO2)
co2_pa = co2_mol_per_mol_air * (STANDARD_PRESSURE_MMHG * 133.322)
co2_mmhg = co2_pa / 133.322
```

Where:
- `STANDARD_PRESSURE_MMHG = 760.0` mmHg
- `MOLAR_MASS_CO2 = 44.01` g/mol
- `MOLAR_MASS_AIR = 28.97` g/mol
- `133.322` Pa/mmHg conversion factor

## Output

- **Real-time telemetry**: JSON files generated at configurable frequency
- **HTTP posting**: Automatic posting to configured endpoint
- **Debug plots**: Matplotlib visualization after simulation completion (if enabled)
- **Console output**: Progress updates, timing information, and error messages

## Troubleshooting

### **Common Issues**

1. **Import errors**: Ensure all files are in the same directory and dependencies are installed
2. **CDRA simulation errors**: Check configuration parameters and failure scenario settings
3. **HTTP posting failures**: Verify endpoint URL and network connectivity
4. **Plotting issues**: Ensure matplotlib is installed and backend is configured

### **Debug Mode**

Enable debug output by modifying the simulation loop in `simulation.py`:
```python
# Add more verbose logging
if cdra_state.time % 10 == 0:  # Log every 10 steps instead of 100
    print(f"Step {cdra_state.time}: CO2 content = {cdra_state.co2_content:.6f}")
```

### **Performance Issues**

- **Slow simulation**: Set `REAL_TIME_MODE = False` for maximum speed
- **High memory usage**: Reduce `TIME_STEPS` or disable plotting
- **Network timeouts**: Increase timeout values in HTTP requests

## Dependencies

- **Python 3.7+**
- **numpy**: Numerical computations
- **matplotlib**: Plotting and visualization
- **requests**: HTTP communication
- **Built-in modules**: json, os, time, datetime

## File Structure

```
DaphneATsim/
├── simulation.py          # Main simulation script
├── CDRA.py               # CDRA simulation framework
├── simulation_config.py  # Configuration file
├── jsonurl.py           # JSON utilities
├── test_*.py            # Test scripts
├── jsonfile/            # Generated telemetry data
└── requirements.txt     # Python dependencies
```

## Future Enhancements

- Real-time plotting during simulation
- More sophisticated failure scenarios
- Additional environmental parameters
- Web-based configuration interface
- Historical data analysis tools
- Performance optimization for high-frequency simulations
