# Integrated CDRA Simulation with Telemetry

This system integrates the CDRA (Carbon Dioxide Removal Assembly) simulation with real-time telemetry generation for space habitat monitoring.

## Overview

The system combines:
- **CDRA.py**: Advanced CO2 removal simulation with failure scenarios
- **simulation.py**: Main telemetry generation and HTTP posting
- **simulation_config.py**: Centralized configuration management

## Features

- **Real-time simulation**: Configurable timing (real-time or fast simulation)
- **Dynamic CO2 telemetry**: ppCO2 values are dynamically calculated from CDRA simulation
- **Failure injection**: Configurable CDRA failure scenarios
- **Telemetry posting**: Automatic JSON generation and HTTP posting every second
- **Debug plotting**: Matplotlib visualization of CDRA simulation results
- **Error handling**: Graceful fallback if CDRA simulation fails
- **Full compatibility**: Generates identical parameters to the referenced CDRA simulator

## Files

- `simulation.py` - Main simulation loop with CDRA integration
- `CDRA.py` - CDRA simulation framework
- `simulation_config.py` - Configuration parameters
- `test_integration.py` - Test script for CDRA integration
- `test_compatibility.py` - Compatibility test with referenced simulator
- `test_failures.py` - Test script for CDRA failure scenarios
- `jsonfile/sim_data.json` - Generated telemetry data

## Configuration

Edit `simulation_config.py` to modify:

- **Timing**: Real-time mode, simulation speed, total steps
- **CDRA failures**: Filter saturation, fan degradation timing
- **Telemetry**: JSON file path, HTTP endpoint URL
- **Debug**: Plotting options, output intervals

## Usage

### Quick Start

1. **Test integration**:
   ```bash
   python test_integration.py
   ```

2. **Test compatibility** (verify identical parameters):
   ```bash
   python test_compatibility.py
   ```

3. **Test failure scenarios**:
   ```bash
   python test_failures.py
   ```

4. **Run full simulation**:
   ```bash
   python simulation.py
   ```

5. **Run fast simulation** (no real-time delays):
   ```bash
   # Edit simulation_config.py: REAL_TIME_MODE = False
   python simulation.py
   ```

### Configuration Examples

**Real-time simulation with CDRA failures**:
```python
REAL_TIME_MODE = True
SIMULATION_SPEED = 1.0
CDRA_FAILURES = {
    'fan_degraded': True,
    'fan_degraded_start': 1000,
    'fan_degraded_end': 5000,
    'degraded_flow_rate': 0.5
}
```

**Test specific failure scenarios**:
```python
# Use predefined example configurations
from simulation_config import EXAMPLE_FAILURE_CONFIGS

# Test valve stuck failure
CDRA_FAILURES.update(EXAMPLE_FAILURE_CONFIGS['valve_stuck_test'])

# Test multi-failure scenario
CDRA_FAILURES.update(EXAMPLE_FAILURE_CONFIGS['multi_failure_test'])
```

**Fast simulation for testing**:
```python
REAL_TIME_MODE = False
TIME_STEPS = 1000
ENABLE_PLOTTING = True
```

## CDRA Integration Details

The system integrates CDRA simulation by:

1. **Initialization**: Creates CDRA state at startup
2. **Per-step simulation**: Runs CDRA control and physics each second
3. **CO2 conversion**: Converts CDRA CO2 content (kg/kg) to ppCO2 (mmHg)
4. **Telemetry update**: Updates JSON data with dynamic CO2 values
5. **Error handling**: Falls back to static values if CDRA fails

## Failure Scenarios

The system supports comprehensive CDRA failure scenarios:

### **Supported Failure Types:**
- **Filter Saturation**: Absorption beds become fully saturated, reducing CO2 removal efficiency
- **Valve Stuck**: Valves get stuck in current position, preventing path switching
- **Heater Failure**: Specific heaters stop working, affecting regeneration cycles
- **Fan Degradation**: Reduced air flow rates, impacting overall system performance

### **Failure Configuration:**
```python
CDRA_FAILURES = {
    'filter_saturation': True,
    'filter_saturation_start': 1000,  # When failure starts
    'filter_saturation_end': 2000,    # When failure ends
    
    'valve_stuck': True,
    'valve_stuck_start': 1000,
    'valve_stuck_end': 3000,
    
    'heater_failure': ['desiccant_1', 'sorbent_2'],  # List of failed components
    
    'fan_degraded': True,
    'fan_degraded_start': 1000,
    'fan_degraded_end': 5000,
    'degraded_flow_rate': 0.5  # Reduced flow rate
}
```

### **Testing Failures:**
Use the included test script to verify failure scenarios:
```bash
python test_failures.py
```

## CO2 Conversion

The system uses the exact same unit conversion functions as the referenced CDRA simulator:

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

- **Real-time telemetry**: JSON files generated every second
- **HTTP posting**: Automatic posting to configured endpoint
- **Debug plots**: Matplotlib visualization after simulation completion
- **Console output**: Progress updates and error messages

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure all files are in the same directory
2. **CDRA simulation errors**: Check configuration parameters
3. **HTTP posting failures**: Verify endpoint URL and network connectivity
4. **Plotting issues**: Ensure matplotlib is installed and backend is configured

### Debug Mode

Enable debug output by modifying the simulation loop:
```python
# Add more verbose logging
if counter[0] % 10 == 0:  # Log every 10 steps instead of 100
    print(f"Step {counter[0]}: CO2 content = {cdra_state.co2_content:.6f}")
```

## Dependencies

- Python 3.7+
- numpy
- matplotlib
- requests
- json (built-in)
- os (built-in)
- time (built-in)
- datetime (built-in)

## Future Enhancements

- Real-time plotting during simulation
- More sophisticated failure scenarios
- Additional environmental parameters
- Web-based configuration interface
- Historical data analysis tools
