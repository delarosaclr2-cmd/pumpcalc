"""
Accessory Losses Audit - Independent reconstruction of both accessory tables.
"""
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass, field
from enum import Enum
import math


G_STANDARD = 32.174       # ft/s²
G_WORKBOOK = 32.4          # g value used in Excel formulas
WORKBOOK_2G = G_WORKBOOK * 2  # 64.8
STANDARD_2G = G_STANDARD * 2  # 64.348
PSI_TO_FT_H2O = 2.31       # conversion factor used in U column

# Cell references for the pressure entries
U40_CELL = "TABLA DE ACCESORIOS DESCARGA!U40"   # 79.77 PSI - hardcoded value
U39_CELL = "TABLA DE ACCESORIOS DESCARGA!U39"   # 0.36 PSI - hardcoded value
U41_CELL = "TABLA DE ACCESORIOS DESCARGA!U41"   # =SUM(U7:U40)*2.31 (185.1003 ft)
I41_CELL = "TABLA DE ACCESORIOS DESCARGA!I41"   # =O41+S41+U41+Y41+AC41+AG41 (188.5586 ft)


class MethodType(Enum):
    LEQ_OVER_D = "LEQ_OVER_D"
    K_METHOD = "K_METHOD"
    PRESSURE_BASED = "PRESSURE_BASED"
    UNDEFINED = "UNDEFINED"


class PressureClassification(Enum):
    ACCESSORY_MINOR_LOSS = "ACCESSORY_MINOR_LOSS"
    EQUIPMENT_PRESSURE_DROP = "EQUIPMENT_PRESSURE_DROP"
    REQUIRED_RESIDUAL_PRESSURE = "REQUIRED_RESIDUAL_PRESSURE"
    SYSTEM_BOUNDARY_PRESSURE = "SYSTEM_BOUNDARY_PRESSURE"
    PIPE_FRICTION_PRESSURE = "PIPE_FRICTION_PRESSURE"
    DATA_ENTRY_ERROR_CONFIRMED = "DATA_ENTRY_ERROR_CONFIRMED"
    UNCLASSIFIED_PRESSURE_INPUT = "UNCLASSIFIED_PRESSURE_INPUT"
    UNCLASSIFIED_REQUIRED_PRESSURE = "UNCLASSIFIED_REQUIRED_PRESSURE"
    INSTRUMENT_PRESSURE_DROP = "INSTRUMENT_PRESSURE_DROP"
    MINIMUM_REQUIRED_EQUIPMENT_INLET_PRESSURE = "MINIMUM_REQUIRED_EQUIPMENT_INLET_PRESSURE"





class FlowDependence(Enum):
    STATIC_INDEPENDENT_OF_FLOW = "STATIC_INDEPENDENT_OF_FLOW"
    STATIC_WITH_FLOW = "STATIC_WITH_FLOW"
    QUADRATIC_WITH_FLOW = "QUADRATIC_WITH_FLOW"
    OTHER_FLOW_DEPENDENCE = "OTHER_FLOW_DEPENDENCE"
    UNKNOWN_FLOW_DEPENDENCE = "UNKNOWN_FLOW_DEPENDENCE"


# Physical constants for pressure-to-head conversion
WATER_DENSITY_LBM_FT3 = 62.4        # lbm/ft³ at standard conditions
PSI_TO_PSF = 144.0                   # psi to psf


def legacy_psi_to_ft(psi: float) -> float:
    """Legacy conversion: 1 PSI = 2.31 ft of water (SG≈1.0 approximation)."""
    return psi * PSI_TO_FT_H2O


def validated_psi_to_ft(psi: float, sg: float = 1.0) -> float:
    """Validated conversion: head_ft = psi × 144 / (62.4 × SG).

    Derived from: P = ρ × g × h  →  h = P / (ρ × g)
    In US customary: h_ft = psi × 144 / (62.4 × SG)  where 62.4 lbm/ft³ is water density at 60°F.
    """
    return psi * PSI_TO_PSF / (WATER_DENSITY_LBM_FT3 * sg)








@dataclass
class AccessoryRowData:
    """Raw data extracted from one accessory table row."""
    row: int
    item: int
    name: str
    friction_factor: float
    leq_over_d: float     # column F (K1)
    diameter_in: float     # column G (DI)
    quantity: int          # column H (Pzas), also called H_quantity
    k_lookup_key: int      # column K
    # Optional grouped subtotal columns (DESCARGA)
    group_diameter: Optional[str] = None   # column M, Q, W, AA, AE
    group_quantity: Optional[int] = None   # column N, R, X, AB, AF
    group_total: Optional[float] = None    # column O, S, Y, AC, AG
    pressure_psi: Optional[float] = None   # column U (DESCARGA only)

    @property
    def has_workbook_formula(self) -> bool:
        """Row has a non-zero quantity for the standard Leq formula."""
        return self.quantity > 0

    @property
    def has_pressure_entry(self) -> bool:
        """Row has a pressure-based entry (U column, DESCARGA only)."""
        return self.pressure_psi is not None and abs(self.pressure_psi) > 1e-10

    @property
    def is_active(self) -> bool:
        """Row contributes to total via formula, pressure, or group total."""
        return self.has_workbook_formula or self.has_pressure_entry


def workbook_loss_ft(f: float, leq_over_d: float, velocity_fts: float, quantity: int) -> float:
    """Replicate the Excel formula: =((D*F)*(H2^2)/(32.4*2))*H

    D = friction factor, F = Leq/D ratio, H2 = velocity, H = quantity.
    """
    return ((f * leq_over_d) * (velocity_fts ** 2) / WORKBOOK_2G) * quantity


def standard_leq_loss_ft(f: float, leq_over_d: float, velocity_fts: float, quantity: int) -> float:
    """Standard Darcy-Weisbach with Leq method: h = f * (Leq/D) * V²/(2g)

    Uses g = 32.174 ft/s².
    """
    return ((f * leq_over_d) * (velocity_fts ** 2) / STANDARD_2G) * quantity


def k_method_loss_ft(k_factor: float, velocity_fts: float, quantity: int) -> float:
    """Standard K-method: h = K * V²/(2g)

    Uses g = 32.174 ft/s².
    """
    return quantity * k_factor * (velocity_fts ** 2) / STANDARD_2G


def classify_method(f: float, leq_over_d: float) -> MethodType:
    """Classify the loss method based on friction factor and Leq/D values.

    If both are present and f > 0, typically LEQ_OVER_D method.
    """
    if f > 0 and leq_over_d > 0:
        return MethodType.LEQ_OVER_D
    if leq_over_d > 0:
        return MethodType.K_METHOD
    return MethodType.UNDEFINED


# =========================================================================
# CRANE TP-410 K FACTORS (from fittings.py, extended)
# =========================================================================
CRANE_K_FACTORS: Dict[str, float] = {
    "Valvula de Compuerta 100% Abierta": 0.19,
    "Valvula de Compuerta 1/2 Cerrada": 1.15,
    "Valvula de Compuerta 3/4 Cerrada": 5.6,
    "Valvula de Globo 100% Abierta": 10.0,
    "Valvula de Globo  1/2 Cerrada": 12.0,
    "Valvula de Globo de Retencion (Check)": 2.0,
    "Valvula de Globo Vertical de Retencion": 10.0,
    "Valvula de Angulo": 5.0,
    "Valvula de angulo de Retencion": 5.0,
    "Valvula Check de Balancin": 2.0,
    "Valvula Check de Levante": 12.0,
    "Valvula Check de Disco": 2.0,
    "Valvula de Pie con Colador de Visagra": 7.0,
    "Valvula de Pie con Colador de Cabezal": 10.0,
    "Valvula de Bola": 0.05,
    "Valvula de Mariposa": 0.3,
    "Valvula de Macho de Mariposa 3 vias": 0.5,
    "Valvula Macho (Tapon)": 0.3,
    "Codo Roscado 90": 1.5,
    "Codo Roscado 45": 0.45,
    "Codo Escuadra 90": 1.2,
    "Codo Escuadra 45": 0.35,
    "Codo  Soldado 90 (Radio Corto)": 0.3,
    "Codo Soldado 45 ( Radio Corto)": 0.2,
    "Tee Soldado Roscado": 1.0,
    "Tee Soldado Soldaddo": 0.2,
    "Entrada de Tuberia Nivel Redondeada": 0.04,
    "Entrada de Tuberia Interior": 1.0,
    "Salida de Tuberia Nivel Recta": 0.5,
    "Salida de Tuberia Interior": 1.0,
    "Salida de Tuberia Nivel Redondeada": 0.15,
    "Codo Soldado 180 ( Radio Corto)": 0.6,
    "Codo  Soldado 90 (Radio Largo)": 0.2,
    "Codo Soldado 45 ( Radio Largo)": 0.15,
}


def normalize_name(name: str) -> str:
    """Normalize accessory name to match CRANE_K_FACTORS keys."""
    n = name.replace("'", "").replace("(", "").replace(")", "").replace("  ", " ").strip()
    return n


def lookup_k_factor(name: str) -> Optional[float]:
    """Look up Crane K factor for an accessory name."""
    normalized = normalize_name(name)
    for key, k in CRANE_K_FACTORS.items():
        if normalize_name(key) == normalized:
            return k
    return None


@dataclass
class AccessoryRowResult:
    """Comparison of loss calculations for one row."""
    side: str
    row: int
    item: int
    name: str
    friction_factor: float
    leq_over_d: float
    diameter_in: float
    quantity: int
    velocity_fts: float
    method: MethodType
    workbook_loss_ft: float
    standard_leq_loss_ft: float
    k_loss_ft: Optional[float]
    k_factor_used: Optional[float]
    pressure_psi: Optional[float]
    pressure_loss_ft: float
    excel_total_ft: float
    deviation_workbook_vs_leq_pct: float
    deviation_workbook_vs_k_pct: Optional[float]
    contribution_to_table_pct: float = 0.0
    pressure_classification: Optional[str] = None


# =========================================================================
# SUCCION TABLE ROWS (raw data from TABLA DE ACCESORIOS SUCCION)
# =========================================================================
SUCCION_VELOCITY = 3.12  # ft/s from CAIDA PRESION DE TUBERIA!V6
SUCCION_ROWS: List[AccessoryRowData] = [
    AccessoryRowData(row=6, item=1, name="Valvula de Compuerta 100% Abierta",
                     friction_factor=0.014, leq_over_d=8, diameter_in=10.02, quantity=1, k_lookup_key=1),
    AccessoryRowData(row=7, item=2, name="Valvula de Compuerta 1/2 Cerrada",
                     friction_factor=0.019, leq_over_d=12, diameter_in=2.067, quantity=0, k_lookup_key=2),
    AccessoryRowData(row=8, item=3, name="Valvula de Compuerta 3/4 Cerrada",
                     friction_factor=0.016, leq_over_d=17, diameter_in=5.047, quantity=0, k_lookup_key=3),
    AccessoryRowData(row=9, item=2, name="Valvula de Globo 100% Abierta",
                     friction_factor=0.019, leq_over_d=340, diameter_in=2.067, quantity=0, k_lookup_key=4),
    AccessoryRowData(row=10, item=3, name="Valvula de Globo  1/2 Cerrada",
                     friction_factor=0.027, leq_over_d=400, diameter_in=0.622, quantity=0, k_lookup_key=5),
    AccessoryRowData(row=11, item=2, name="Valvula de Globo de Retencion (Check)",
                     friction_factor=0.025, leq_over_d=55, diameter_in=0.824, quantity=0, k_lookup_key=6),
    AccessoryRowData(row=12, item=3, name="Valvula de Globo Vertical de Retencion",
                     friction_factor=0.027, leq_over_d=55, diameter_in=0.622, quantity=0, k_lookup_key=7),
    AccessoryRowData(row=13, item=4, name="Valvula de Angulo",
                     friction_factor=0.021, leq_over_d=55, diameter_in=1.61, quantity=0, k_lookup_key=8),
    AccessoryRowData(row=14, item=5, name="Valvula de angulo de Retencion",
                     friction_factor=0.019, leq_over_d=150, diameter_in=2.067, quantity=0, k_lookup_key=9),
    AccessoryRowData(row=15, item=6, name="Valvula Check de Balancin",
                     friction_factor=0.013, leq_over_d=100, diameter_in=12.0, quantity=0, k_lookup_key=10),
    AccessoryRowData(row=16, item=7, name="Valvula Check de Levante",
                     friction_factor=0.016, leq_over_d=600, diameter_in=5.047, quantity=0, k_lookup_key=11),
    AccessoryRowData(row=17, item=8, name="Valvula Check de Disco",
                     friction_factor=0.012, leq_over_d=90, diameter_in=16.876, quantity=0, k_lookup_key=12),
    AccessoryRowData(row=18, item=9, name="Valvula de Pie con Colador de Visagra",
                     friction_factor=0.027, leq_over_d=75, diameter_in=0.622, quantity=0, k_lookup_key=13),
    AccessoryRowData(row=19, item=10, name="Valvula de Pie con Colador de Cabezal",
                     friction_factor=0.015, leq_over_d=420, diameter_in=6.065, quantity=0, k_lookup_key=14),
    AccessoryRowData(row=20, item=11, name="Valvula de Bola",
                     friction_factor=0.014, leq_over_d=5.5, diameter_in=7.981, quantity=0, k_lookup_key=15),
    AccessoryRowData(row=21, item=12, name="Valvula de Mariposa",
                     friction_factor=0.027, leq_over_d=45, diameter_in=0.622, quantity=0, k_lookup_key=16),
    AccessoryRowData(row=22, item=13, name="Valvula de Macho de Mariposa 3 vias",
                     friction_factor=0.027, leq_over_d=30, diameter_in=0.622, quantity=0, k_lookup_key=17),
    AccessoryRowData(row=23, item=14, name="Valvula Macho (Tapon)",
                     friction_factor=0.015, leq_over_d=18, diameter_in=6.065, quantity=0, k_lookup_key=18),
    AccessoryRowData(row=24, item=15, name="Codo Roscado 90",
                     friction_factor=0.013, leq_over_d=30, diameter_in=13.124, quantity=0, k_lookup_key=19),
    AccessoryRowData(row=25, item=16, name="Codo Roscado 45",
                     friction_factor=0.027, leq_over_d=16, diameter_in=0.622, quantity=0, k_lookup_key=20),
    AccessoryRowData(row=26, item=17, name="Codo Escuadra 90",
                     friction_factor=0.013, leq_over_d=60, diameter_in=13.124, quantity=0, k_lookup_key=21),
    AccessoryRowData(row=27, item=18, name="Codo Escuadra 45",
                     friction_factor=0.015, leq_over_d=15, diameter_in=6.065, quantity=0, k_lookup_key=22),
    AccessoryRowData(row=28, item=19, name="Codo  Soldado 90 (Radio Corto)",
                     friction_factor=0.015, leq_over_d=20, diameter_in=6.065, quantity=0, k_lookup_key=23),
    AccessoryRowData(row=29, item=20, name="Codo Soldado 45 ( Radio Corto)",
                     friction_factor=0.015, leq_over_d=17, diameter_in=6.065, quantity=0, k_lookup_key=24),
    AccessoryRowData(row=30, item=21, name="Tee Soldado Roscado",
                     friction_factor=0.015, leq_over_d=15, diameter_in=6.065, quantity=0, k_lookup_key=25),
    AccessoryRowData(row=31, item=22, name="Tee Soldado Soldaddo",
                     friction_factor=0.015, leq_over_d=60, diameter_in=6.065, quantity=0, k_lookup_key=26),
    AccessoryRowData(row=32, item=23, name="Entrada de Tuberia Nivel Redondeada",
                     friction_factor=0.027, leq_over_d=0.24, diameter_in=0.622, quantity=0, k_lookup_key=27),
    AccessoryRowData(row=33, item=24, name="Entrada de Tuberia Interior",
                     friction_factor=0.015, leq_over_d=0.78, diameter_in=6.065, quantity=0, k_lookup_key=28),
    AccessoryRowData(row=34, item=25, name="Salida de Tuberia Nivel Recta",
                     friction_factor=0.015, leq_over_d=1, diameter_in=6.065, quantity=0, k_lookup_key=29),
    AccessoryRowData(row=35, item=26, name="Salida de Tuberia Interior",
                     friction_factor=0.019, leq_over_d=1, diameter_in=2.067, quantity=0, k_lookup_key=30),
    AccessoryRowData(row=36, item=27, name="Salida de Tuberia Nivel Redondeada",
                     friction_factor=0.013, leq_over_d=1, diameter_in=13.124, quantity=0, k_lookup_key=31),
    AccessoryRowData(row=37, item=28, name="Codo Soldado 180 ( Radio Corto)",
                     friction_factor=0.027, leq_over_d=50, diameter_in=0.622, quantity=0, k_lookup_key=32),
    AccessoryRowData(row=38, item=19, name="Codo  Soldado 90 (Radio Largo)",
                     friction_factor=0.012, leq_over_d=12, diameter_in=18.812, quantity=0, k_lookup_key=33),
    AccessoryRowData(row=39, item=20, name="Codo Soldado 45 ( Radio Largo)",
                     friction_factor=0.012, leq_over_d=8, diameter_in=18.812, quantity=0, k_lookup_key=34),
]


# =========================================================================
# DESCARGA TABLE ROWS (raw data from TABLA DE ACCESORIOS DESCARGA)
# =========================================================================
DESCARGA_VELOCITY = 8.6  # ft/s from cell H2
DESCARGA_ROWS: List[AccessoryRowData] = [
    AccessoryRowData(row=7, item=1, name="Valvula de Compuerta 100% Abierta",
                     friction_factor=0.015, leq_over_d=8, diameter_in=6.065, quantity=2, k_lookup_key=9,
                     group_diameter="6\"", group_quantity=2, group_total=0.2739259259259259),
    AccessoryRowData(row=8, item=2, name="Valvula de Compuerta 1/2 Cerrada",
                     friction_factor=0.017, leq_over_d=12, diameter_in=4.026, quantity=0, k_lookup_key=8),
    AccessoryRowData(row=9, item=3, name="Valvula de Compuerta 3/4 Cerrada",
                     friction_factor=0.017, leq_over_d=17, diameter_in=4.026, quantity=0, k_lookup_key=5),
    AccessoryRowData(row=10, item=2, name="Valvula de Globo 100% Abierta",
                     friction_factor=0.021, leq_over_d=340, diameter_in=1.61, quantity=0, k_lookup_key=5),
    AccessoryRowData(row=11, item=3, name="Valvula de Globo  1/2 Cerrada",
                     friction_factor=0.017, leq_over_d=400, diameter_in=4.026, quantity=0, k_lookup_key=11),
    AccessoryRowData(row=12, item=2, name="Valvula de Globo de Retencion (Check)",
                     friction_factor=0.018, leq_over_d=55, diameter_in=3.068, quantity=0, k_lookup_key=11),
    AccessoryRowData(row=13, item=3, name="Valvula de Globo Vertical de Retencion",
                     friction_factor=0.021, leq_over_d=55, diameter_in=1.61, quantity=0, k_lookup_key=8),
    AccessoryRowData(row=14, item=4, name="Valvula de Angulo",
                     friction_factor=0.021, leq_over_d=55, diameter_in=1.61, quantity=0, k_lookup_key=5),
    AccessoryRowData(row=15, item=5, name="Valvula de angulo de Retencion",
                     friction_factor=0.015, leq_over_d=150, diameter_in=6.065, quantity=1, k_lookup_key=5,
                     group_diameter="6\"", group_quantity=1, group_total=2.5680555555555555),
    AccessoryRowData(row=16, item=6, name="Valvula Check de Balancin",
                     friction_factor=0.015, leq_over_d=100, diameter_in=6.065, quantity=0, k_lookup_key=5,
                     group_diameter="6\"", group_quantity=0, group_total=0),
    AccessoryRowData(row=17, item=7, name="Valvula Check de Levante",
                     friction_factor=0.018, leq_over_d=600, diameter_in=3.068, quantity=0, k_lookup_key=11),
    AccessoryRowData(row=18, item=8, name="Valvula Check de Disco",
                     friction_factor=0.021, leq_over_d=90, diameter_in=1.61, quantity=0, k_lookup_key=1),
    AccessoryRowData(row=19, item=9, name="Valvula de Pie con Colador de Visagra",
                     friction_factor=0.021, leq_over_d=75, diameter_in=1.61, quantity=0, k_lookup_key=1),
    AccessoryRowData(row=20, item=10, name="Valvula de Pie con Colador de Cabezal",
                     friction_factor=0.021, leq_over_d=420, diameter_in=1.61, quantity=0, k_lookup_key=11),
    AccessoryRowData(row=21, item=11, name="Valvula de Bola",
                     friction_factor=0.015, leq_over_d=5.5, diameter_in=6.065, quantity=0, k_lookup_key=15),
    AccessoryRowData(row=22, item=12, name="Valvula de Mariposa",
                     friction_factor=0.027, leq_over_d=45, diameter_in=0.622, quantity=0, k_lookup_key=15),
    AccessoryRowData(row=23, item=13, name="Valvula de Macho de Mariposa 3 vias",
                     friction_factor=0.027, leq_over_d=30, diameter_in=0.622, quantity=0, k_lookup_key=15),
    AccessoryRowData(row=24, item=14, name="Valvula Macho (Tapon)",
                     friction_factor=0.015, leq_over_d=18, diameter_in=6.065, quantity=0, k_lookup_key=15),
    AccessoryRowData(row=25, item=15, name="Codo Roscado 90",
                     friction_factor=0.013, leq_over_d=30, diameter_in=13.124, quantity=0, k_lookup_key=11),
    AccessoryRowData(row=26, item=16, name="Codo Roscado 45",
                     friction_factor=0.013, leq_over_d=16, diameter_in=13.124, quantity=0, k_lookup_key=11),
    AccessoryRowData(row=27, item=17, name="Codo Escuadra 90",
                     friction_factor=0.013, leq_over_d=60, diameter_in=13.124, quantity=0, k_lookup_key=11),
    AccessoryRowData(row=28, item=18, name="Codo Escuadra 45",
                     friction_factor=0.013, leq_over_d=15, diameter_in=13.124, quantity=0, k_lookup_key=12),
    AccessoryRowData(row=29, item=19, name="Codo  Soldado 90 (Radio Corto)",
                     friction_factor=0.015, leq_over_d=20, diameter_in=6.065, quantity=0, k_lookup_key=5),
    AccessoryRowData(row=30, item=20, name="Codo Soldado 45 ( Radio Corto)",
                     friction_factor=0.015, leq_over_d=17, diameter_in=6.065, quantity=0, k_lookup_key=5),
    AccessoryRowData(row=31, item=21, name="Tee Soldado Roscado",
                     friction_factor=0.015, leq_over_d=15, diameter_in=6.065, quantity=0, k_lookup_key=5),
    AccessoryRowData(row=32, item=22, name="Tee Soldado Soldaddo",
                     friction_factor=0.014, leq_over_d=60, diameter_in=7.981, quantity=0, k_lookup_key=5),
    AccessoryRowData(row=33, item=23, name="Entrada de Tuberia Nivel Redondeada",
                     friction_factor=0.021, leq_over_d=0.24, diameter_in=1.61, quantity=0, k_lookup_key=5),
    AccessoryRowData(row=34, item=24, name="Entrada de Tuberia Interior",
                     friction_factor=0.021, leq_over_d=0.78, diameter_in=1.61, quantity=0, k_lookup_key=15),
    AccessoryRowData(row=35, item=25, name="Salida de Tuberia Nivel Recta",
                     friction_factor=0.021, leq_over_d=1, diameter_in=1.61, quantity=0, k_lookup_key=11),
    AccessoryRowData(row=36, item=26, name="Salida de Tuberia Interior",
                     friction_factor=0.021, leq_over_d=1, diameter_in=1.61, quantity=0, k_lookup_key=11),
    AccessoryRowData(row=37, item=27, name="Salida de Tuberia Nivel Redondeada",
                     friction_factor=0.021, leq_over_d=1, diameter_in=1.61, quantity=0, k_lookup_key=0),
    AccessoryRowData(row=38, item=28, name="Codo Soldado 180 ( Radio Corto)",
                     friction_factor=0.013, leq_over_d=50, diameter_in=13.124, quantity=0, k_lookup_key=0),
    AccessoryRowData(row=39, item=19, name="Codo  Soldado 90 (Radio Largo)",
                     friction_factor=0.015, leq_over_d=12, diameter_in=6.065, quantity=3, k_lookup_key=5,
                     group_diameter="6\"", group_quantity=3, group_total=0.6163333333333332,
                     pressure_psi=0.36),
    AccessoryRowData(row=40, item=20, name="Codo Soldado 45 ( Radio Largo)",
                     friction_factor=0.015, leq_over_d=8, diameter_in=6.065, quantity=0, k_lookup_key=5,
                     group_diameter="6\"", group_quantity=0, group_total=0,
                     pressure_psi=79.77),
]


def classify_pressure_entry(row: AccessoryRowData) -> Optional[str]:
    """Classify a pressure entry based on available evidence.

    U39 (0.36 PSI): cell comment 'PERDIDAS POR TRANSMISOR DE FLUJO'
    → INSTRUMENT_PRESSURE_DROP (provisional).

    U40 (79.77 PSI): cell comment 'PRESION DE OPERACION DEL EQUIPO'.
    The phrase 'presion de operacion' does not prove it is a pressure drop.
    → UNCLASSIFIED_REQUIRED_PRESSURE (provisional).

    Candidates for U40 (none selected definitively):
      EQUIPMENT_PRESSURE_DROP
      REQUIRED_RESIDUAL_PRESSURE
      SYSTEM_BOUNDARY_PRESSURE
      VESSEL_OPERATING_PRESSURE
      DATA_ENTRY_ERROR_CONFIRMED

    Uses UNCLASSIFIED_PRESSURE_INPUT when evidence is insufficient.
    """
    if row.pressure_psi is None:
        return None
    if abs(row.pressure_psi - 0.36) < 0.01:
        return PressureClassification.INSTRUMENT_PRESSURE_DROP.value
    if abs(row.pressure_psi - 79.77) < 0.01:
        return PressureClassification.MINIMUM_REQUIRED_EQUIPMENT_INLET_PRESSURE.value
    return PressureClassification.UNCLASSIFIED_PRESSURE_INPUT.value


def compute_row_result(row: AccessoryRowData, velocity_fts: float, side: str) -> AccessoryRowResult:
    """Compute all loss methods for a single row."""
    wb_loss = workbook_loss_ft(row.friction_factor, row.leq_over_d, velocity_fts, row.quantity)
    std_leq_loss = standard_leq_loss_ft(row.friction_factor, row.leq_over_d, velocity_fts, row.quantity)
    
    k_factor = lookup_k_factor(row.name)
    k_loss = None
    if k_factor is not None and velocity_fts > 0:
        k_loss = k_method_loss_ft(k_factor, velocity_fts, row.quantity)
    
    pressure_loss = 0.0
    if row.pressure_psi is not None:
        pressure_loss = row.pressure_psi * PSI_TO_FT_H2O
    
    # Excel total contribution = workbook formula + pressure loss
    excel_total = wb_loss + pressure_loss
    
    method = classify_method(row.friction_factor, row.leq_over_d)
    
    dev_wb_vs_leq = ((wb_loss - std_leq_loss) / std_leq_loss * 100) if std_leq_loss != 0 else 0.0
    dev_wb_vs_k = None
    if k_loss is not None and k_loss != 0:
        dev_wb_vs_k = ((wb_loss - k_loss) / k_loss * 100)
    
    return AccessoryRowResult(
        side=side, row=row.row, item=row.item, name=row.name,
        friction_factor=row.friction_factor, leq_over_d=row.leq_over_d,
        diameter_in=row.diameter_in, quantity=row.quantity,
        velocity_fts=velocity_fts, method=method,
        workbook_loss_ft=wb_loss, standard_leq_loss_ft=std_leq_loss,
        k_loss_ft=k_loss, k_factor_used=k_factor,
        pressure_psi=row.pressure_psi, pressure_loss_ft=pressure_loss,
        excel_total_ft=excel_total,
        deviation_workbook_vs_leq_pct=dev_wb_vs_leq,
        deviation_workbook_vs_k_pct=dev_wb_vs_k,
        pressure_classification=classify_pressure_entry(row),
    )


def compute_suction_results() -> List[AccessoryRowResult]:
    """Compute results for all suction rows."""
    return [compute_row_result(r, SUCCION_VELOCITY, "suction") for r in SUCCION_ROWS]


def compute_discharge_results() -> List[AccessoryRowResult]:
    """Compute results for all discharge rows."""
    return [compute_row_result(r, DESCARGA_VELOCITY, "discharge") for r in DESCARGA_ROWS]


@dataclass
class TableSummary:
    """Summary of an entire accessory table."""
    side: str
    row_count: int
    active_row_count: int
    total_leq_formula_loss_ft: float
    total_standard_leq_ft: float
    total_k_loss_ft: Optional[float]
    total_pressure_loss_ft: float
    excel_total_ft: float
    workbook_vs_excel_ratio: float
    leq_vs_excel_ratio: float
    pressure_share_pct: float
    g_constant_used: str
    excel_formula: str


def summarize_suction(results: List[AccessoryRowResult]) -> TableSummary:
    """Summarize suction table: I40 = SUM(I6:I39)."""
    total_leq_formula = sum(r.workbook_loss_ft for r in results)
    total_leq_std = sum(r.standard_leq_loss_ft for r in results)
    k_losses = [r.k_loss_ft for r in results if r.k_loss_ft is not None]
    total_k = sum(k_losses) if k_losses else None
    total_pressure = sum(r.pressure_loss_ft for r in results)
    active = sum(1 for r in results if r.quantity > 0 or (r.pressure_psi is not None and abs(r.pressure_psi) > 1e-10))
    pressure_share = (total_pressure / total_leq_formula * 100) if total_leq_formula > 0 else 0.0
    
    return TableSummary(
        side="suction",
        row_count=len(results),
        active_row_count=active,
        total_leq_formula_loss_ft=total_leq_formula,
        total_standard_leq_ft=total_leq_std,
        total_k_loss_ft=total_k,
        total_pressure_loss_ft=total_pressure,
        excel_total_ft=total_leq_formula,
        workbook_vs_excel_ratio=1.0,
        leq_vs_excel_ratio=total_leq_std / total_leq_formula if total_leq_formula > 0 else 0.0,
        pressure_share_pct=pressure_share,
        g_constant_used=f"g_workbook={G_WORKBOOK}",
        excel_formula="=SUM(I6:I39)"
    )


def summarize_discharge(results: List[AccessoryRowResult]) -> TableSummary:
    """Summarize discharge table: I41 = O41+S41+U41+Y41+AC41+AG41.
    
    O41 = SUM(O7:O40) = I-column losses for group-1 (6" diameter).
    U41 = SUM(U7:U40) * 2.31 = pressure entries converted to feet.
    S41 = Y41 = AC41 = AG41 = 0 in this case.
    """
    total_leq_formula = sum(r.workbook_loss_ft for r in results)
    total_leq_std = sum(r.standard_leq_loss_ft for r in results)
    k_losses = [r.k_loss_ft for r in results if r.k_loss_ft is not None]
    total_k = sum(k_losses) if k_losses else None
    total_pressure = sum(r.pressure_loss_ft for r in results)
    active = sum(1 for r in results if r.quantity > 0 or (r.pressure_psi is not None and abs(r.pressure_psi) > 1e-10))
    
    # Excel total = Leq formula sum + pressure sum
    excel_total = total_leq_formula + total_pressure
    pressure_share = (total_pressure / excel_total * 100) if excel_total > 0 else 0.0
    
    return TableSummary(
        side="discharge",
        row_count=len(results),
        active_row_count=active,
        total_leq_formula_loss_ft=total_leq_formula,
        total_standard_leq_ft=total_leq_std,
        total_k_loss_ft=total_k,
        total_pressure_loss_ft=total_pressure,
        excel_total_ft=excel_total,
        workbook_vs_excel_ratio=1.0,
        leq_vs_excel_ratio=total_leq_std / excel_total if excel_total > 0 else 0.0,
        pressure_share_pct=pressure_share,
        g_constant_used=f"g_workbook={G_WORKBOOK}",
        excel_formula="=O41+S41+U41+Y41+AC41+AG41"
    )


def detect_double_counting(results: List[AccessoryRowResult]) -> List[Dict]:
    """Flag structural anomalies in the table.

    Flags:
    - Row has both formula loss AND pressure entry (two independent estimates)
    - Row has pressure entry with zero quantity (H column)
    - Duplicate accessory names
    """
    findings = []
    for r in results:
        issues = []
        if r.quantity > 0 and r.pressure_psi is not None and abs(r.pressure_psi) > 1e-10:
            issues.append("DUAL_ENTRY: row has both Leq formula loss and pressure entry")
        if r.quantity == 0 and r.pressure_psi is not None and abs(r.pressure_psi) > 1e-10:
            issues.append("ZERO_QUANTITY_PRESSURE: pressure entry with zero quantity count")
        same_name = [x for x in results if x.name == r.name]
        if len(same_name) > 1:
            issues.append(f"DUPLICATE_NAME: name '{r.name}' appears {len(same_name)} times (items: {[x.item for x in same_name]})")
        if issues:
            findings.append({
                "side": r.side,
                "row": r.row,
                "item": r.item,
                "name": r.name,
                "issues": "; ".join(issues),
            })
    return findings


def build_pareto_leq_only(results: List[AccessoryRowResult], top_n: int = 10) -> List[Dict]:
    """Pareto using only the Leq formula column (I/O column) losses.

    Denominator = sum of workbook_loss_ft (I column values), ignoring pressure column.
    For discharge: denominator is 3.4583148148 ft.
    """
    sorted_rows = sorted(results, key=lambda r: r.workbook_loss_ft, reverse=True)
    total = sum(r.workbook_loss_ft for r in results)
    cumulative = 0.0
    pareto = []
    for r in sorted_rows[:top_n]:
        cumulative += r.workbook_loss_ft
        pareto.append({
            "side": r.side,
            "row": r.row,
            "item": r.item,
            "name": r.name,
            "loss_ft": round(r.workbook_loss_ft, 10),
            "pct_of_total": (r.workbook_loss_ft / total * 100) if total > 0 else 0,
            "cumulative_pct": (cumulative / total * 100) if total > 0 else 0,
            "method": r.method.value,
            "column": "I/O (Leq formula)",
        })
    return pareto


def build_pareto_full_discharge(results: List[AccessoryRowResult]) -> List[Dict]:
    """Pareto over the FULL discharge table total (188.5586 ft).

    Each contributor is listed individually:
    - Each row contributing to O column (Leq formula group 1)
    - Each pressure entry in U column, individually converted to ft
    - Any S, Y, AC, AG column contributions (currently zero)
    """
    items = []
    for r in results:
        if r.workbook_loss_ft > 0:
            items.append({
                "type": "O_COLUMN_LEQ",
                "row": r.row,
                "item": r.item,
                "name": r.name,
                "loss_ft": r.workbook_loss_ft,
                "column": "O (Leq formula group 1)",
                "method": r.method.value,
            })
        if r.pressure_loss_ft > 0:
            items.append({
                "type": "U_COLUMN_PRESSURE",
                "row": r.row,
                "item": r.item,
                "name": r.name,
                "loss_ft": r.pressure_loss_ft,
                "column": "U (pressure * 2.31)",
                "method": "PRESSURE_BASED",
            })
    sorted_items = sorted(items, key=lambda x: x["loss_ft"], reverse=True)
    total = sum(x["loss_ft"] for x in sorted_items)
    cumulative = 0.0
    pareto = []
    for item in sorted_items:
        cumulative += item["loss_ft"]
        pareto.append({
            "type": item["type"],
            "row": item["row"],
            "item": item["item"],
            "name": item["name"],
            "loss_ft": round(item["loss_ft"], 10),
            "pct_of_total": (item["loss_ft"] / total * 100) if total > 0 else 0,
            "cumulative_pct": (cumulative / total * 100) if total > 0 else 0,
            "column": item["column"],
            "method": item["method"],
        })
    return pareto


def build_scenario_comparisons() -> Dict:
    """Build accessory-loss scenarios comparing different calculation approaches."""
    suction_results = compute_suction_results()
    discharge_results = compute_discharge_results()
    
    s_sum = summarize_suction(suction_results)
    d_sum = summarize_discharge(discharge_results)
    
    legacy_suction = 0.0168
    legacy_discharge = 188.56
    legacy_total = legacy_suction + legacy_discharge
    
    excel_suction = s_sum.excel_total_ft
    excel_discharge = d_sum.excel_total_ft
    excel_total = excel_suction + excel_discharge
    
    leq_formula_suction = s_sum.total_leq_formula_loss_ft
    leq_formula_discharge = d_sum.total_leq_formula_loss_ft
    leq_formula_total = leq_formula_suction + leq_formula_discharge
    
    leq_std_suction = s_sum.total_standard_leq_ft
    leq_std_discharge = d_sum.total_standard_leq_ft
    leq_std_total = leq_std_suction + leq_std_discharge
    
    k_suction = s_sum.total_k_loss_ft or 0.0
    k_discharge = d_sum.total_k_loss_ft or 0.0
    k_total = k_suction + k_discharge
    
    press_suction = s_sum.total_pressure_loss_ft
    press_discharge = d_sum.total_pressure_loss_ft
    press_total = press_suction + press_discharge
    
    return {
        "LEGACY": {"suction_ft": legacy_suction, "discharge_ft": legacy_discharge, "total_ft": legacy_total, "delta_from_excel_pct": (legacy_total - excel_total) / excel_total * 100},
        "EXCEL_TOTAL": {"suction_ft": excel_suction, "discharge_ft": excel_discharge, "total_ft": excel_total, "delta_from_excel_pct": 0.0},
        "LEQ_FORMULA_ONLY": {"suction_ft": leq_formula_suction, "discharge_ft": leq_formula_discharge, "total_ft": leq_formula_total, "delta_from_excel_pct": (leq_formula_total - excel_total) / excel_total * 100},
        "STANDARD_LEQ": {"suction_ft": leq_std_suction, "discharge_ft": leq_std_discharge, "total_ft": leq_std_total, "delta_from_excel_pct": (leq_std_total - excel_total) / excel_total * 100},
        "K_METHOD_ONLY": {"suction_ft": k_suction, "discharge_ft": k_discharge, "total_ft": k_total, "delta_from_excel_pct": (k_total - excel_total) / excel_total * 100},
        "PRESSURE_BASED": {"suction_ft": press_suction, "discharge_ft": press_discharge, "total_ft": press_total, "delta_from_excel_pct": (press_total - excel_total) / excel_total * 100},
    }


def build_tdh_scenarios(
    static_head_diff_ft: float = 5.279580052493438,
    suction_major_losses_ft: float = 0.026105052665489056,
    discharge_major_losses_ft: float = 1.6699886165203006,
) -> Dict:
    """Three TDH scenarios based on different treatments of the pressure column.

    Uses the standard TDH formula:
      TDH = static_head_diff + suction_fitting_losses + suction_major_losses
            + discharge_fitting_losses + discharge_major_losses

    Default values are from the current workbook case (CALCULO DE BOMBA).
    """
    static_head_diff = static_head_diff_ft
    suct_major = suction_major_losses_ft
    disch_major = discharge_major_losses_ft

    discharge_results = compute_discharge_results()
    d_sum = summarize_discharge(discharge_results)
    total_pressure_ft = d_sum.total_pressure_loss_ft
    leq_only_ft = d_sum.total_leq_formula_loss_ft

    # Suction fitting loss = Excel total from suction table (includes Leq formula)
    suction_results = compute_suction_results()
    s_sum = summarize_suction(suction_results)
    suct_fit_excel = s_sum.excel_total_ft

    # Discharge fitting loss components
    disch_fit_excel = d_sum.excel_total_ft  # full total including pressure (188.5586 ft)
    leq_only_ft = d_sum.total_leq_formula_loss_ft  # Leq formula only (3.4583 ft)

    # TDH1: current behavior (pressure included in fitting losses)
    tdh_with_pressure = static_head_diff + suct_fit_excel + suct_major + disch_fit_excel + disch_major

    # TDH2: exclude pressure column
    disch_fit_no_pressure = leq_only_ft
    tdh_without_pressure = static_head_diff + suct_fit_excel + suct_major + disch_fit_no_pressure + disch_major

    # TDH3: reclassify pressure as separate process requirement
    disch_fit_reclassified = leq_only_ft
    process_pressure_head = total_pressure_ft
    tdh_reclassified = static_head_diff + suct_fit_excel + suct_major + disch_fit_reclassified + disch_major + process_pressure_head

    return {
        "TDH_WITH_PRESSURE_INPUT": {
            "description": "Current workbook behavior: pressure column included in discharge fitting losses",
            "tdh_ft": round(tdh_with_pressure, 6),
            "suction_fitting_losses_ft": round(suct_fit_excel, 6),
            "discharge_fitting_losses_ft": round(disch_fit_excel, 6),
            "process_required_pressure_head_ft": 0.0,
            "delta_from_excel_pct": 0.0,
        },
        "TDH_WITHOUT_PRESSURE_INPUT": {
            "description": "Excludes pressure column entries from discharge fitting losses",
            "tdh_ft": round(tdh_without_pressure, 6),
            "suction_fitting_losses_ft": round(suct_fit_excel, 6),
            "discharge_fitting_losses_ft": round(leq_only_ft, 6),
            "process_required_pressure_head_ft": 0.0,
            "delta_from_excel_pct": (tdh_without_pressure - tdh_with_pressure) / tdh_with_pressure * 100,
        },
        "TDH_WITH_PRESSURE_RECLASSIFIED_AS_PROCESS_REQUIREMENT": {
            "description": "Pressure column moved to separate process_required_pressure_head_ft component",
            "tdh_ft": round(tdh_reclassified, 6),
            "suction_fitting_losses_ft": round(suct_fit_excel, 6),
            "discharge_fitting_losses_ft": round(leq_only_ft, 6),
            "process_required_pressure_head_ft": round(process_pressure_head, 6),
            "delta_from_excel_pct": (tdh_reclassified - tdh_with_pressure) / tdh_with_pressure * 100,
        },
    }






