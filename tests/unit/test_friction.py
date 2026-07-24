"""
Unit tests for friction factor calculations.
"""
import sys
sys.path.insert(0, r'C:\PUMPCALC')

import unittest
import math
from src.domain.friction import (
    colebrook_white, swamee_jain, haaland,
    get_friction_factor, get_all_methods, FrictionResult
)


class TestColebrookWhite(unittest.TestCase):
    """Test Colebrook-White equation solver."""

    def test_laminar_flow(self):
        """Test laminar flow (Re < 2300)."""
        result = colebrook_white(1000, 0.001)
        self.assertEqual(result.flow_regime, "laminar")
        self.assertEqual(result.method, "laminar")
        self.assertAlmostEqual(result.friction_factor, 64.0/1000, places=6)

    def test_known_laminar(self):
        """Test known laminar case: Re=1000, f=0.064."""
        result = colebrook_white(1000, 0.001)
        self.assertAlmostEqual(result.friction_factor, 0.064, places=6)

    def test_smooth_pipe_turbulent(self):
        """Test smooth pipe turbulent: Re=1e5, eps/D=0."""
        # For smooth pipe, Blasius: f = 0.316/Re^0.25 = 0.0178
        result = colebrook_white(100000, 0.0)
        self.assertAlmostEqual(result.friction_factor, 0.0178, places=3)

    def test_rough_pipe_turbulent(self):
        """Test rough pipe turbulent: Re=1e6, eps/D=0.01."""
        # From Moody chart: f ≈ 0.038
        result = colebrook_white(1000000, 0.01)
        self.assertAlmostEqual(result.friction_factor, 0.038, places=2)

    def test_residual_check(self):
        """Test that residual is near zero for converged solution."""
        Re = 768553
        eps_D = 0.000238
        result = colebrook_white(Re, eps_D)

        f = result.friction_factor
        lhs = 1.0 / math.sqrt(f)
        rhs = -2.0 * math.log10(eps_D/3.7 + 2.51/(Re * math.sqrt(f)))
        residual = abs(lhs - rhs)

        # Residual should be very small (Colebrook converged)
        self.assertLess(residual, 1e-6, f"Residual {residual} too large")

    def test_convergence(self):
        """Test that solver converges within iterations."""
        Re = 462915
        eps_D = 0.000144
        result = colebrook_white(Re, eps_D)
        self.assertTrue(result.converged)
        self.assertLess(result.iterations, 100)


class TestSwameeJain(unittest.TestCase):
    """Test Swamee-Jain explicit approximation."""

    def test_turbulent(self):
        """Test turbulent flow."""
        result = swamee_jain(100000, 0.001)
        self.assertEqual(result.flow_regime, "turbulent")
        self.assertEqual(result.method, "swamee-jain")

    def test_transitional(self):
        """Test transitional flow (2300 < Re < 4000)."""
        result = swamee_jain(3000, 0.001)
        self.assertEqual(result.flow_regime, "transitional")

    def test_laminar(self):
        """Test laminar flow."""
        result = swamee_jain(1000, 0.001)
        self.assertEqual(result.flow_regime, "laminar")
        self.assertEqual(result.method, "laminar")
        self.assertAlmostEqual(result.friction_factor, 64.0/1000, places=6)

    def test_smooth_pipe(self):
        """Test smooth pipe."""
        result = swamee_jain(100000, 0.0)
        self.assertAlmostEqual(result.friction_factor, 0.0178, places=3)


class TestHaaland(unittest.TestCase):
    """Test Haaland explicit approximation."""

    def test_turbulent(self):
        """Test turbulent flow."""
        result = haaland(100000, 0.001)
        self.assertEqual(result.flow_regime, "turbulent")
        self.assertEqual(result.method, "haaland")

    def test_smooth_pipe(self):
        """Test smooth pipe."""
        result = haaland(100000, 0.0)
        self.assertAlmostEqual(result.friction_factor, 0.0178, places=3)


class TestFrictionFactorComparison(unittest.TestCase):
    """Test comparison of all methods."""

    def test_current_case_suction(self):
        """Test suction line: Re=462,915, eps/D=0.000144."""
        results = get_all_methods(462915, 0.000144)

        f_laminar = results['laminar'].friction_factor
        f_colebrook = results['colebrook'].friction_factor
        f_swamee = results['swamee-jain'].friction_factor
        f_haaland = results['haaland'].friction_factor

        # Laminar should be 64/Re = 0.000138
        self.assertAlmostEqual(f_laminar, 64.0/462915, places=6)

        # Turbulent methods should be close
        self.assertAlmostEqual(f_colebrook, 0.0150, places=3)

        # Turbulent methods should be close to each other (allow 3 places for approximations)
        self.assertAlmostEqual(f_swamee, f_colebrook, places=3)
        self.assertAlmostEqual(f_haaland, f_colebrook, places=3)

    def test_current_case_discharge(self):
        """Test discharge line: Re=768,553, eps/D=0.000238."""
        results = get_all_methods(768553, 0.000238)

        f_colebrook = results['colebrook'].friction_factor
        f_swamee = results['swamee-jain'].friction_factor
        f_haaland = results['haaland'].friction_factor

        self.assertAlmostEqual(f_colebrook, 0.0153, places=3)

        # Different explicit methods have small differences - allow 3 places
        self.assertAlmostEqual(f_swamee, f_colebrook, places=3)
        self.assertAlmostEqual(f_haaland, f_colebrook, places=3)

    def test_rough_pipe_all_methods(self):
        """Test all methods for rough pipe at Re=1e6, eps/D=0.01."""
        results = get_all_methods(1000000, 0.01)

        f_colebrook = results['colebrook'].friction_factor
        f_swamee = results['swamee-jain'].friction_factor
        f_haaland = results['haaland'].friction_factor

        # Should all be around 0.038
        self.assertAlmostEqual(f_colebrook, 0.038, places=2)
        # Different explicit methods are approximations - allow 3 places
        self.assertAlmostEqual(f_swamee, f_colebrook, places=3)
        self.assertAlmostEqual(f_haaland, f_colebrook, places=3)

    def test_smooth_pipe_all_methods(self):
        """Test all methods for smooth pipe at Re=1e5."""
        results = get_all_methods(100000, 0.0)

        f_colebrook = results['colebrook'].friction_factor
        f_swamee = results['swamee-jain'].friction_factor
        f_haaland = results['haaland'].friction_factor

        # Should all match Blasius ~0.0178
        self.assertAlmostEqual(f_colebrook, 0.0178, places=3)
        # Different explicit methods have small differences - allow 3 places
        self.assertAlmostEqual(f_swamee, f_colebrook, places=3)
        self.assertAlmostEqual(f_haaland, f_colebrook, places=3)


class TestResidualVerification(unittest.TestCase):
    """Test that Colebrook solutions satisfy the equation."""

    def test_residual_check(self):
        """Test that residual is near zero for converged solution."""
        Re = 768553
        eps_D = 0.000238
        result = colebrook_white(Re, eps_D)

        f = result.friction_factor
        lhs = 1.0 / math.sqrt(f)
        rhs = -2.0 * math.log10(eps_D/3.7 + 2.51/(Re * math.sqrt(f)))
        residual = abs(lhs - rhs)

        # Residual should be very small (Colebrook converged)
        self.assertLess(residual, 1e-6, f"Residual {residual} too large")

    def test_residual_current_suction(self):
        """Test residual for current suction case."""
        Re = 462915
        eps_D = 0.000144
        result = colebrook_white(Re, eps_D)

        f = result.friction_factor
        lhs = 1.0 / math.sqrt(f)
        rhs = -2.0 * math.log10(eps_D/3.7 + 2.51/(Re * math.sqrt(f)))
        residual = abs(lhs - rhs)

        self.assertLess(residual, 1e-6)

    def test_residual_range(self):
        """Test residual across range of Re and eps/D."""
        test_cases = [
            (4000, 0.001),
            (10000, 0.0001),
            (100000, 0.0001),
            (1000000, 0.0001),
            (10000000, 0.001),
            (100000000, 0.01),
        ]

        for Re, eps_D in test_cases:
            result = colebrook_white(Re, eps_D)
            f = result.friction_factor
            lhs = 1.0 / math.sqrt(f)
            rhs = -2.0 * math.log10(eps_D/3.7 + 2.51/(Re * math.sqrt(f)))
            residual = abs(lhs - rhs)
            self.assertLess(residual, 1e-6, 
                f"Residual {residual} too large for Re={Re}, eps/D={eps_D}")


if __name__ == '__main__':
    unittest.main()