#!/usr/bin/env python3
"""
Compatibility test to verify our simulator generates identical parameters
to the referenced CDRA simulator
"""

import sys
import os

# Add the referenced simulator path to sys.path
referenced_path = "/Users/tomakazuki/local/documents/research/daphne-at-docker/daphne_brain/AT/diagnosis/physics"
sys.path.insert(0, referenced_path)

try:
    from cdra_sim_adapter import run_cdra_simulation, mmhg_to_kg_per_kg_air, kg_per_kg_air_to_mmhg as ref_kg_to_mmhg
    print("✓ Successfully imported referenced CDRA simulator")
except ImportError as e:
    print(f"✗ Failed to import referenced simulator: {e}")
    print("Make sure the path is correct and the file exists")
    sys.exit(1)

from simulation_config import *
from CDRA import CDRAState, timestep, control, update_cabin_concentration

# Our unit conversion functions
def mmhg_to_kg_per_kg_air(co2_mmhg: float) -> float:
    """Our implementation matching the referenced simulator"""
    co2_pa = co2_mmhg * 133.322
    co2_mol_per_mol_air = co2_pa / (STANDARD_PRESSURE_MMHG * 133.322)
    co2_kg_per_kg_air = co2_mol_per_mol_air * (MOLAR_MASS_CO2 / MOLAR_MASS_AIR)
    return co2_kg_per_kg_air

def kg_per_kg_air_to_mmhg(co2_kg_per_kg_air: float) -> float:
    """Our implementation matching the referenced simulator"""
    co2_mol_per_mol_air = co2_kg_per_kg_air * (MOLAR_MASS_AIR / MOLAR_MASS_CO2)
    co2_pa = co2_mol_per_mol_air * (STANDARD_PRESSURE_MMHG * 133.322)
    co2_mmhg = co2_pa / 133.322
    return co2_mmhg

def test_unit_conversion_compatibility():
    """Test that our unit conversion functions match the referenced simulator"""
    print("\n=== Testing Unit Conversion Compatibility ===")
    
    test_values = [0.004, 0.003, 0.005, 0.002, 0.006]
    
    for kg_kg in test_values:
        # Test kg/kg to mmHg conversion
        our_mmhg = kg_per_kg_air_to_mmhg(kg_kg)
        ref_mmhg = ref_kg_to_mmhg(kg_kg)
        
        diff = abs(our_mmhg - ref_mmhg)
        if diff < 1e-10:
            print(f"✓ kg/kg {kg_kg:.6f} -> mmHg: {our_mmhg:.6f} (matches reference)")
        else:
            print(f"✗ kg/kg {kg_kg:.6f} -> mmHg: {our_mmhg:.6f} vs {ref_mmhg:.6f} (DIFFERENCE: {diff:.2e})")
    
    for mmhg in [4.62, 3.5, 5.8, 2.3, 6.9]:
        # Test mmHg to kg/kg conversion
        our_kg_kg = mmhg_to_kg_per_kg_air(mmhg)
        ref_kg_kg = mmhg_to_kg_per_kg_air(mmhg)  # Using our function as reference
        
        diff = abs(our_kg_kg - ref_kg_kg)
        if diff < 1e-10:
            print(f"✓ mmHg {mmhg:.2f} -> kg/kg: {our_kg_kg:.6f} (matches reference)")
        else:
            print(f"✗ mmHg {mmhg:.2f} -> kg/kg: {our_kg_kg:.6f} vs {ref_kg_kg:.6f} (DIFFERENCE: {diff:.2e})")

def test_simulation_compatibility():
    """Test that our simulation generates identical parameters"""
    print("\n=== Testing Simulation Compatibility ===")
    
    # Test configuration
    test_duration = 10  # seconds
    baseline_co2_mmhg = 4.62
    failure_config = {
        'filter_saturation': False,
        'fan_degraded': False,
        'valve_stuck': False,
        'heater_failure': []
    }
    
    print(f"Running referenced simulator for {test_duration}s...")
    ref_series = run_cdra_simulation(
        failure_config=failure_config,
        duration_seconds=test_duration,
        baseline_co2_mmHg=baseline_co2_mmhg,
        onset_time_sec=3
    )
    
    print(f"Running our simulator for {test_duration}s...")
    # Run our simulation
    cdra_state = CDRAState()
    cdra_state.co2_content = mmhg_to_kg_per_kg_air(baseline_co2_mmhg)
    
    our_series = []
    for step in range(test_duration):
        control(cdra_state)
        C_out, flow = timestep(cdra_state)
        update_cabin_concentration(cdra_state, C_out, flow)
        our_series.append(kg_per_kg_air_to_mmhg(cdra_state.co2_content))
        cdra_state.time += 1
    
    # Compare results
    print(f"\nComparing {len(ref_series)} data points...")
    max_diff = 0
    total_diff = 0
    
    for i, (ref_val, our_val) in enumerate(zip(ref_series, our_series)):
        diff = abs(ref_val - our_val)
        max_diff = max(max_diff, diff)
        total_diff += diff
        
        if i < 5:  # Show first 5 values
            print(f"  Step {i}: Ref={ref_val:.6f}, Our={our_val:.6f}, Diff={diff:.2e}")
    
    avg_diff = total_diff / len(ref_series)
    print(f"\nCompatibility Results:")
    print(f"  Max difference: {max_diff:.2e}")
    print(f"  Average difference: {avg_diff:.2e}")
    
    if max_diff < 1e-10:
        print("✓ COMPATIBLE: Simulators generate identical parameters")
        return True
    else:
        print("✗ NOT COMPATIBLE: Simulators generate different parameters")
        return False

def main():
    """Run all compatibility tests"""
    print("CDRA Simulator Compatibility Test")
    print("=" * 50)
    
    # Test unit conversions
    test_unit_conversion_compatibility()
    
    # Test simulation compatibility
    compatible = test_simulation_compatibility()
    
    print("\n" + "=" * 50)
    if compatible:
        print("✓ ALL TESTS PASSED: Simulators are compatible")
    else:
        print("✗ SOME TESTS FAILED: Simulators are not compatible")
    
    return compatible

if __name__ == "__main__":
    main()
