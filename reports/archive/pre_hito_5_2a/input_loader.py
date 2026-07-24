"""
Input loader module - Load and validate input data.
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, validator
from src.domain.fluids import Fluid
from src.domain.pipes import Pipe
from src.domain.units import Q_, ureg


class FluidInput(BaseModel):
    """Fluid properties input model."""
    name: str = "Water"
    density_lbm_ft3: float = Field(gt=0, description="Mass density in lbm/ft³")
    specific_gravity: float = Field(gt=0, le=5, description="Specific gravity")
    viscosity_cP: float = Field(gt=0, description="Dynamic viscosity in cP")
    temperature_F: float = Field(description="Temperature in °F")
    vapor_pressure_psi: float = Field(ge=0, description="Vapor pressure in psia")
    
    @validator('specific_gravity')
    def check_sg_consistency(cls, v, values):
        if 'density_lbm_ft3' in values:
            expected_sg = values['density_lbm_ft3'] / 62.4
            if abs(v - expected_sg) > 0.05:
                raise ValueError(f"SG {v} inconsistent with density {values['density_lbm_ft3']} lbm/ft³")
        return v
    
    def to_fluid(self) -> Fluid:
        return Fluid.from_imperial(
            name=self.name,
            rho_lbm_ft3=self.density_lbm_ft3,
            mu_cP=self.viscosity_cP,
            temp_F=self.temperature_F,
            vp_psia=self.vapor_pressure_psi,
            sg=self.specific_gravity
        )


class PipeInput(BaseModel):
    """Pipe input model."""
    side: str  # "suction" or "discharge"
    nominal_diameter_in: float = Field(gt=0)
    schedule: str = "STD"
    inner_diameter_in: float = Field(gt=0)
    length_ft: float = Field(ge=0)
    roughness_ft: float = Field(ge=0)
    material: str = "Steel"


class VesselInput(BaseModel):
    """Suction vessel input model."""
    pressure_psi: float = 0.0
    pressure_type: str = "gauge"  # "absolute", "gauge", "vacuum"
    liquid_surface_elev_ft: float = 0.0
    min_level_elev_ft: Optional[float] = None


class PumpInput(BaseModel):
    """Pump input model."""
    rated_flow_gpm: float = Field(gt=0)
    design_flow_gpm: float = Field(gt=0)
    tdh_ft: float = Field(gt=0)
    efficiency: float = Field(gt=0, le=1)
    rpm: int = Field(gt=0)
    motor_efficiency: Optional[float] = None


class WorkbookInputs(BaseModel):
    """Complete workbook inputs."""
    fluid: FluidInput
    suction_pipe: PipeInput
    discharge_pipe: PipeInput
    vessel: VesselInput
    pump: PumpInput
    atmospheric_pressure_psi: float = 14.7
    static_suction_head_ft: float = 0.0
    static_discharge_head_ft: float = 0.0
    suction_fitting_losses_ft: float = 0.0
    suction_pipe_losses_ft: float = 0.0
    discharge_fitting_losses_ft: float = 0.0
    discharge_pipe_losses_ft: float = 0.0
    
    class Config:
        arbitrary_types_allowed = True


def create_workbook_inputs() -> WorkbookInputs:
    """Create inputs from workbook current case."""
    return WorkbookInputs(
        fluid=FluidInput(
            name="Agua Blanca",
            density_lbm_ft3=62.0,
            specific_gravity=0.995,
            viscosity_cP=0.52,
            temperature_F=95.0,
            vapor_pressure_psi=0.8
        ),
        suction_pipe=PipeInput(
            side="suction",
            nominal_diameter_in=10.0,
            inner_diameter_in=10.02,
            length_ft=6.96,
            roughness_ft=0.00012,
            material="Acero Inox SS"
        ),
        discharge_pipe=PipeInput(
            side="discharge",
            nominal_diameter_in=6.0,
            inner_diameter_in=6.065,
            length_ft=36.0,
            roughness_ft=0.00012,
            material="Acero Inox SS"
        ),
        vessel=VesselInput(
            pressure_psi=0.0,
            pressure_type="gauge",
            liquid_surface_elev_ft=1.64,
            min_level_elev_ft=1.64
        ),
        pump=PumpInput(
            rated_flow_gpm=770.5,
            design_flow_gpm=770.5,
            tdh_ft=195.55,
            efficiency=0.72,
            rpm=3600,
            motor_efficiency=None
        ),
        atmospheric_pressure_psi=14.7,
        static_suction_head_ft=1.64,
        static_discharge_head_ft=6.92,
        suction_fitting_losses_ft=0.0168,
        suction_pipe_losses_ft=0.0261,
        discharge_fitting_losses_ft=188.56,
        discharge_pipe_losses_ft=1.67
    )


if __name__ == '__main__':
    inputs = create_workbook_inputs()
    print("Workbook Inputs Created:")
    print(f"  Fluid: {inputs.fluid.name}")
    print(f"  Density: {inputs.fluid.density_lbm_ft3} lbm/ft³")
    print(f"  SG: {inputs.fluid.specific_gravity}")
    print(f"  Viscosity: {inputs.fluid.viscosity_cP} cP")
    print(f"  Temp: {inputs.fluid.temperature_F} °F")
    print(f"  Vapor P: {inputs.fluid.vapor_pressure_psi} psia")
    print(f"  Suction pipe: {inputs.suction_pipe.nominal_diameter_in} in, L={inputs.suction_pipe.length_ft} ft")
    print(f"  Discharge pipe: {inputs.discharge_pipe.nominal_diameter_in} in, L={inputs.discharge_pipe.length_ft} ft")
    print(f"  Pump: Q={inputs.pump.rated_flow_gpm} GPM, H={inputs.pump.tdh_ft} ft, η={inputs.pump.efficiency*100:.0f}%")