#!/usr/bin/env python3
"""
Test script to verify CDRA integration with simulation
"""

from CDRA import CDRAState, timestep, control, update_cabin_concentration
from simulation_config import *
import numpy as np

# Unit conversion functions - matching the referenced simulator exactly
def mmhg_to_kg_per_kg_air(co2_mmhg: float) -> float:
    """
    Convert CO2 partial pressure from mmHg to kg/kg air.
    Matches the referenced simulator implementation exactly.
    """
    co2_pa = co2_mmhg * 133.322
    co2_mol_per_mol_air = co2_pa / (STANDARD_PRESSURE_MMHG * 133.322)
    co2_kg_per_kg_air = co2_mol_per_mol_air * (MOLAR_MASS_CO2 / MOLAR_MASS_AIR)
    return co2_kg_per_kg_air

def kg_per_kg_air_to_mmhg(co2_kg_per_kg_air: float) -> float:
    """
    Convert CO2 concentration from kg/kg air to mmHg.
    Matches the referenced simulator implementation exactly.
    """
    co2_mol_per_mol_air = co2_kg_per_kg_air * (MOLAR_MASS_AIR / MOLAR_MASS_CO2)
    co2_pa = co2_mol_per_mol_air * (STANDARD_PRESSURE_MMHG * 133.322)
    co2_mmhg = co2_pa / 133.322
    return co2_mmhg

def test_cdra_integration():
    """Test the CDRA integration"""
    print("Testing CDRA integration...")
    
    # Initialize CDRA state
    cdra_state = CDRAState()
    
    # Convert initial CO2 from mmHg to kg/kg for CDRA simulation using proper conversion
    cdra_state.co2_content = mmhg_to_kg_per_kg_air(CO2_CONTENT_INIT)
    print(f"Initial CO2: {CO2_CONTENT_INIT} mmHg = {cdra_state.co2_content:.6f} kg/kg")
    
    # Test a few simulation steps
    for i in range(5):
        print(f"\nStep {i}:")
        print(f"  Time: {cdra_state.time}")
        print(f"  CO2 content: {cdra_state.co2_content:.6f}")
        print(f"  Air flow rate: {cdra_state.air_flow_rate}")
        
        # Apply control
        control(cdra_state)
        
        # Simulate one step
        co2_before = cdra_state.co2_content
        C_out, flow = timestep(cdra_state)
        update_cabin_concentration(cdra_state, C_out, flow)
        
        # Convert to mmHg for telemetry using proper conversion function
        ppco2_mmhg = kg_per_kg_air_to_mmhg(cdra_state.co2_content)
        
        print(f"  CO2 after: {cdra_state.co2_content:.6f}")
        print(f"  ppCO2 (mmHg): {ppco2_mmhg:.2f}")
        print(f"  Flow: {flow}")
        
        # Update time
        cdra_state.time += 1
    
    print("\nCDRA integration test completed successfully!")
    return True

if __name__ == "__main__":
    test_cdra_integration()
