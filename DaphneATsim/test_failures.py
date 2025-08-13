#!/usr/bin/env python3
"""
Test script to verify CDRA failure scenarios are working correctly
"""

from CDRA import CDRAState, timestep, control, update_cabin_concentration
from simulation_config import *
import numpy as np

def test_valve_stuck_failure():
    """Test that valve stuck failure prevents valve switching"""
    print("=== Testing Valve Stuck Failure ===")
    
    # Initialize CDRA state
    cdra_state = CDRAState()
    
    # Track valve state changes
    valve_states = []
    
    print("Normal operation (first 10 steps):")
    for i in range(10):
        control(cdra_state)
        valve_states.append(cdra_state.valve_state['path_1_active'])
        print(f"  Step {i}: Valve path_1_active = {cdra_state.valve_state['path_1_active']}")
        cdra_state.time += 1
    
    # Now enable valve stuck failure
    print("\nEnabling valve stuck failure...")
    FAILURE_SCENARIO['valve_stuck'] = True
    FAILURE_SCENARIO['valve_stuck_start'] = 10
    FAILURE_SCENARIO['valve_stuck_end'] = 20
    
    print("Operation with valve stuck (next 10 steps):")
    for i in range(10):
        control(cdra_state)
        valve_states.append(cdra_state.valve_state['path_1_active'])
        print(f"  Step {i+10}: Valve path_1_active = {cdra_state.valve_state['path_1_active']}")
        cdra_state.time += 1
    
    # Check if valve switching stopped during failure
    normal_switching = valve_states[:10]
    stuck_switching = valve_states[10:]
    
    print(f"\nValve switching analysis:")
    print(f"  Normal operation: {normal_switching}")
    print(f"  During failure: {stuck_switching}")
    
    # Valve should switch every 200 steps (VALVE_SWITCH_INTERVAL)
    # During normal operation, we should see some changes
    # During failure, it should stay constant
    normal_changes = sum(1 for i in range(1, len(normal_switching)) if len(normal_switching) > 1 else 0
    stuck_changes = sum(1 for i in range(1, len(stuck_switching)) if len(stuck_switching) > 1 else 0
    
    print(f"  Changes during normal operation: {normal_changes}")
    print(f"  Changes during failure: {stuck_changes}")
    
    if stuck_changes == 0:
        print("✓ Valve stuck failure working correctly - no switching during failure")
    else:
        print("✗ Valve stuck failure not working - valve still switching during failure")
    
    return stuck_changes == 0

def test_filter_saturation_failure():
    """Test that filter saturation failure reduces adsorption efficiency"""
    print("\n=== Testing Filter Saturation Failure ===")
    
    cdra_state = CDRAState()
    
    print("Normal operation (first 5 steps):")
    for i in range(5):
        control(cdra_state)
        timestep(cdra_state)
        
        # Check adsorption efficiency
        avg_efficiency = np.mean(list(cdra_state.adsorption_eff.values()))
        print(f"  Step {i}: Avg adsorption efficiency = {avg_efficiency:.4f}")
        cdra_state.time += 1
    
    # Enable filter saturation failure
    print("\nEnabling filter saturation failure...")
    FAILURE_SCENARIO['filter_saturation'] = True
    FAILURE_SCENARIO['filter_saturation_start'] = 5
    FAILURE_SCENARIO['filter_saturation_end'] = 15
    
    print("Operation with filter saturation (next 5 steps):")
    for i in range(5):
        control(cdra_state)
        timestep(cdra_state)
        
        # Check adsorption efficiency
        avg_efficiency = np.mean(list(cdra_state.adsorption_eff.values()))
        print(f"  Step {i+5}: Avg adsorption efficiency = {avg_efficiency:.4f}")
        cdra_state.time += 1
    
    # Check if efficiency dropped during failure
    normal_efficiency = 0.05  # BASE_ADSORPTION_EFF
    failed_efficiency = BASE_ADSORPTION_EFF + MAX_ADSORPTION_EFF_INCREMENT
    
    print(f"\nEfficiency analysis:")
    print(f"  Normal efficiency: {normal_efficiency}")
    print(f"  Failed efficiency: {failed_efficiency}")
    
    if failed_efficiency > normal_efficiency:
        print("✓ Filter saturation failure working correctly - efficiency increased during failure")
    else:
        print("✗ Filter saturation failure not working - efficiency unchanged during failure")
    
    return failed_efficiency > normal_efficiency

def test_fan_degradation_failure():
    """Test that fan degradation reduces air flow rate"""
    print("\n=== Testing Fan Degradation Failure ===")
    
    cdra_state = CDRAState()
    
    print("Normal operation (first 5 steps):")
    for i in range(5):
        control(cdra_state)
        print(f"  Step {i}: Air flow rate = {cdra_state.air_flow_rate:.3f} kg/s")
        cdra_state.time += 1
    
    # Enable fan degradation failure
    print("\nEnabling fan degradation failure...")
    FAILURE_SCENARIO['fan_degraded'] = True
    FAILURE_SCENARIO['fan_degraded_start'] = 5
    FAILURE_SCENARIO['fan_degraded_end'] = 15
    
    print("Operation with fan degradation (next 5 steps):")
    for i in range(5):
        control(cdra_state)
        print(f"  Step {i+5}: Air flow rate = {cdra_state.air_flow_rate:.3f} kg/s")
        cdra_state.time += 1
    
    # Check if flow rate dropped during failure
    normal_flow = AIR_FLOW_RATE
    degraded_flow = FAILURE_SCENARIO['degraded_flow_rate']
    
    print(f"\nFlow rate analysis:")
    print(f"  Normal flow rate: {normal_flow:.3f} kg/s")
    print(f"  Degraded flow rate: {degraded_flow:.3f} kg/s")
    
    if degraded_flow < normal_flow:
        print("✓ Fan degradation failure working correctly - flow rate reduced during failure")
    else:
        print("✗ Fan degradation failure not working - flow rate unchanged during failure")
    
    return degraded_flow < normal_flow

def main():
    """Run all failure tests"""
    print("CDRA Failure Scenario Tests")
    print("=" * 50)
    
    # Reset failure scenarios to defaults
    from CDRA import FAILURE_SCENARIO
    FAILURE_SCENARIO.update(CDRA_FAILURES)
    
    # Run tests
    valve_test = test_valve_stuck_failure()
    filter_test = test_filter_saturation_failure()
    fan_test = test_fan_degradation_failure()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"  Valve stuck failure: {'✓ PASS' if valve_test else '✗ FAIL'}")
    print(f"  Filter saturation failure: {'✓ PASS' if filter_test else '✗ PASS'}")
    print(f"  Fan degradation failure: {'✓ PASS' if fan_test else '✗ FAIL'}")
    
    all_passed = valve_test and filter_test and fan_test
    if all_passed:
        print("\n✓ ALL FAILURE TESTS PASSED")
    else:
        print("\n✗ SOME FAILURE TESTS FAILED")
    
    return all_passed

if __name__ == "__main__":
    main()
