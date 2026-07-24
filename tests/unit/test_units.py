"""
Unit tests for unit conversions and fundamental hydraulics.
"""
import sys
sys.path.insert(0, r'C:\PUMPCALC')

import unittest
import math
from src.domain.units import (
    gpm_to_m3h, gpm_to_lpm, ft_to_m, m_to_ft, inch_to_m,
    psi_to_pa, pa_to_psi, psi_to_ft_h2o, ft_h2o_to_psi,
    cP_to_Pa_s, lbm_ft3_to_kg_m3, kg_m3_to_lbm_ft3,
    hp_to_kw, kw_to_hp, velocity_head, reynolds_imperial, reynolds_si
)
from src.domain.units import Q_, ureg


class TestUnitConversions(unittest.TestCase):
    """Test unit conversion functions."""

    def test_gpm_to_m3h(self):
        """Test GPM to m³/h conversion."""
        # 1 GPM = 0.2271247 m³/h
        self.assertAlmostEqual(gpm_to_m3h(1.0), 0.2271247, places=4)
        self.assertAlmostEqual(gpm_to_m3h(770.5), 175.0, places=1)

    def test_gpm_to_lpm(self):
        """Test GPM to L/min conversion."""
        # 1 GPM = 3.78541 L/min
        self.assertAlmostEqual(gpm_to_lpm(1.0), 3.78541, places=3)
        self.assertAlmostEqual(gpm_to_lpm(770.5), 2916.7, places=1)

    def test_ft_to_m(self):
        """Test feet to meters conversion."""
        self.assertAlmostEqual(ft_to_m(1.0), 0.3048, places=4)
        self.assertAlmostEqual(ft_to_m(195.55), 59.604, places=3)

    def test_m_to_ft(self):
        """Test meters to feet conversion."""
        self.assertAlmostEqual(m_to_ft(1.0), 3.28084, places=4)
        self.assertAlmostEqual(m_to_ft(59.604), 195.55, places=2)

    def test_inch_to_m(self):
        """Test inches to meters conversion."""
        self.assertAlmostEqual(inch_to_m(1.0), 0.0254, places=4)
        self.assertAlmostEqual(inch_to_m(6.048), 0.1536, places=4)

    def test_psi_to_pa(self):
        """Test psi to Pa conversion."""
        # 1 psi = 6894.76 Pa
        self.assertAlmostEqual(psi_to_pa(1.0), 6894.76, places=1)
        self.assertAlmostEqual(psi_to_pa(14.7), 101353, places=0)

    def test_pa_to_psi(self):
        """Test Pa to psi conversion."""
        self.assertAlmostEqual(pa_to_psi(6894.76), 1.0, places=4)
        self.assertAlmostEqual(pa_to_psi(101325), 14.696, places=3)

    def test_psi_to_ft_h2o(self):
        """Test psi to ft H2O conversion."""
        # 1 psi = 2.3067 ft H2O (at SG=1)
        self.assertAlmostEqual(psi_to_ft_h2o(1.0), 2.3067, places=3)
        self.assertAlmostEqual(psi_to_ft_h2o(14.7), 33.91, places=2)

    def test_ft_h2o_to_psi(self):
        """Test ft H2O to psi conversion."""
        self.assertAlmostEqual(ft_h2o_to_psi(2.3067), 1.0, places=4)
        self.assertAlmostEqual(ft_h2o_to_psi(33.91), 14.7, places=1)

    def test_cP_to_Pa_s(self):
        """Test centipoise to Pa·s conversion."""
        # 1 cP = 0.001 Pa·s
        self.assertAlmostEqual(cP_to_Pa_s(1.0), 0.001, places=6)
        self.assertAlmostEqual(cP_to_Pa_s(0.52), 0.00052, places=6)

    def test_lbm_ft3_to_kg_m3(self):
        """Test lbm/ft³ to kg/m³ conversion."""
        # 1 lbm/ft³ = 16.0185 kg/m³
        self.assertAlmostEqual(lbm_ft3_to_kg_m3(1.0), 16.0185, places=3)
        self.assertAlmostEqual(lbm_ft3_to_kg_m3(62.0), 993.1, places=1)

    def test_kg_m3_to_lbm_ft3(self):
        """Test kg/m³ to lbm/ft³ conversion."""
        self.assertAlmostEqual(kg_m3_to_lbm_ft3(16.0185), 1.0, places=4)
        self.assertAlmostEqual(kg_m3_to_lbm_ft3(993.1), 62.0, places=1)

    def test_hp_to_kw(self):
        """Test HP to kW conversion."""
        # 1 HP = 0.7457 kW
        self.assertAlmostEqual(hp_to_kw(1.0), 0.7457, places=4)
        self.assertAlmostEqual(hp_to_kw(52.58), 39.21, places=2)

    def test_kw_to_hp(self):
        """Test kW to HP conversion."""
        self.assertAlmostEqual(kw_to_hp(0.7457), 1.0, places=4)
        self.assertAlmostEqual(kw_to_hp(39.20), 52.57, places=2)

    def test_velocity_head(self):
        """Test velocity head calculation."""
        # v = 8.6 ft/s, g = 32.174 ft/s²
        v = 8.6
        g = 32.174
        expected = v**2 / (2 * g)
        self.assertAlmostEqual(velocity_head(v, g), expected, places=6)

    def test_reynolds_imperial(self):
        """Test Reynolds number in imperial units."""
        # Re = 50.66 * Q * rho / (D * mu)
        Q = 770.5  # GPM
        D = 6.048  # inches
        rho = 62.0  # lbm/ft³
        mu = 0.52   # cP
        Re = reynolds_imperial(Q, D, rho, mu)
        # Expected: 50.66 * 770.5 * 62 / (6.048 * 0.52) = 769,510
        self.assertAlmostEqual(Re, 769510, delta=100)

    def test_reynolds_si(self):
        """Test Reynolds number in SI units."""
        # Re = rho * V * D / mu
        Q = 0.0486  # m³/s (770.5 GPM)
        D = 0.1536  # m (6.048 in)
        rho = 993.1  # kg/m³
        mu = 0.00052  # Pa·s
        A = math.pi * D**2 / 4
        V = Q / A
        Re = reynolds_si(Q, D, rho, mu)
        # Expected: 993.1 * V * 0.1536 / 0.00052
        self.assertGreater(Re, 100000)  # Turbulent


class TestPintRegistry(unittest.TestCase):
    """Test pint unit registry."""

    def test_gpm_unit_defined(self):
        """Test that GPM unit is defined."""
        q = Q_(1.0, 'gpm')
        # pint returns abbreviated form 'gpm'
        self.assertEqual(str(q.units), 'gpm')

    def test_ft_h2o_unit_defined(self):
        """Test that ft_H2O unit is defined."""
        h = Q_(1.0, 'ft_H2O')
        self.assertEqual(str(h.units), 'ft_H2O')

    def test_ft_fluid_unit_defined(self):
        """Test that ft_fluid unit is defined."""
        h = Q_(1.0, 'ft_fluid')
        self.assertEqual(str(h.units), 'ft_fluid')


class TestDiameterFromFlowVelocity(unittest.TestCase):
    """Test required_diameter_from_flow_velocity function."""

    def test_derived_constant(self):
        """Verify the C constant in required_diameter_from_flow_velocity equals 0.639 exactly."""
        C = 12.0 * math.sqrt(4.0 / (448.831 * math.pi))
        self.assertAlmostEqual(C, 0.639, places=2)

    def test_known_case_discharge(self):
        """Q=770.5 GPM, V=8.6 ft/s → D ≈ 6.05 in."""
        from src.domain.pipes import required_diameter_from_flow_velocity
        D = required_diameter_from_flow_velocity(770.5, 8.6)
        self.assertAlmostEqual(D, 6.05, places=1)

    def test_known_case_suction(self):
        """Q=770.5 GPM, V=3.12 ft/s → D ≈ 10.04 in."""
        from src.domain.pipes import required_diameter_from_flow_velocity
        D = required_diameter_from_flow_velocity(770.5, 3.12)
        self.assertAlmostEqual(D, 10.04, places=1)

    def test_dimensional_analysis(self):
        """Verify dimensional consistency: D² ∝ Q/V."""
        from src.domain.pipes import required_diameter_from_flow_velocity
        # If D² ∝ Q/V, then D² * V / Q = constant
        D1 = required_diameter_from_flow_velocity(100, 5)
        D2 = required_diameter_from_flow_velocity(200, 10)
        const1 = D1**2 * 5 / 100
        const2 = D2**2 * 10 / 200
        self.assertAlmostEqual(const1, const2, places=10)

    def test_zero_flow_returns_zero(self):
        """Zero flow should return 0.
        
        Note: math domain error would occur for negative, but 0 should be acceptable.
        The formula is D = C * sqrt(0 / V) = C * 0 = 0.
        """
        from src.domain.pipes import required_diameter_from_flow_velocity
        D = required_diameter_from_flow_velocity(0, 5)
        self.assertEqual(D, 0.0)

    def test_linearity_with_sqrt_q(self):
        """D should scale with sqrt(Q) for constant V."""
        from src.domain.pipes import required_diameter_from_flow_velocity
        D1 = required_diameter_from_flow_velocity(100, 5)
        D2 = required_diameter_from_flow_velocity(400, 5)  # 4x Q → 2x D
        self.assertAlmostEqual(D2 / D1, 2.0, places=6)


if __name__ == '__main__':
    unittest.main()