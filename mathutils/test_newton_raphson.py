#!/usr/bin/env python3
"""
Test suite for Newton-Raphson root finding algorithm
"""

import unittest
import math
from .newton_raphson import NewtonRaphsonSolver

class TestNewtonRaphsonSolver(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.solver = NewtonRaphsonSolver()
    
    def test_initialization(self):
        """Test solver initialization with default and custom parameters."""
        # Default parameters
        solver1 = NewtonRaphsonSolver()
        self.assertEqual(solver1.tolerance, 1e-10)
        self.assertEqual(solver1.max_iterations, 100)
        
        # Custom parameters
        solver2 = NewtonRaphsonSolver(tolerance=1e-6, max_iterations=50)
        self.assertEqual(solver2.tolerance, 1e-6)
        self.assertEqual(solver2.max_iterations, 50)
    
    def test_polynomial_root(self):
        """Test finding root of x^2 - 2 = 0 (should find sqrt(2))."""
        def f(x):
            return x**2 - 2
        
        def df(x):
            return 2*x
        
        root, converged, iterations = self.solver.find_root(f, df, 1.0)
        
        self.assertTrue(converged)
        self.assertAlmostEqual(root, math.sqrt(2), places=9)
        self.assertLess(iterations, 10)
        self.assertAlmostEqual(f(root), 0, places=10)
    
    def test_transcendental_root(self):
        """Test finding root of cos(x) - x = 0."""
        def f(x):
            return math.cos(x) - x
        
        def df(x):
            return -math.sin(x) - 1
        
        root, converged, iterations = self.solver.find_root(f, df, 0.5)
        
        self.assertTrue(converged)
        self.assertAlmostEqual(f(root), 0, places=9)
        self.assertLess(iterations, 20)
    
    def test_cubic_root(self):
        """Test finding root of x^3 - x - 1 = 0."""
        def f(x):
            return x**3 - x - 1
        
        def df(x):
            return 3*x**2 - 1
        
        root, converged, iterations = self.solver.find_root(f, df, 1.5)
        
        self.assertTrue(converged)
        self.assertAlmostEqual(f(root), 0, places=9)
        self.assertLess(iterations, 15)
    
    def test_linear_function(self):
        """Test finding root of linear function 2x - 4 = 0."""
        def f(x):
            return 2*x - 4
        
        def df(x):
            return 2
        
        root, converged, iterations = self.solver.find_root(f, df, 0.0)
        
        self.assertTrue(converged)
        self.assertAlmostEqual(root, 2.0, places=10)
        self.assertLessEqual(iterations, 2)  # Should converge quickly
    
    def test_division_by_zero(self):
        """Test handling of division by zero (derivative = 0)."""
        def f(x):
            return x**2 - 1
        
        def df(x):
            return 0  # Always zero derivative
        
        with self.assertRaises(ValueError) as context:
            self.solver.find_root(f, df, 1.0)
        
        self.assertIn("Derivative is zero", str(context.exception))
    
    def test_non_convergence(self):
        """Test behavior when algorithm doesn't converge."""
        def f(x):
            return x**3 + 1  # Oscillating behavior with certain initial guesses
        
        def df(x):
            return 3*x**2
        
        solver = NewtonRaphsonSolver(max_iterations=5)
        root, converged, iterations = solver.find_root(f, df, 0.1)
        
        self.assertFalse(converged)
        self.assertEqual(iterations, 5)
    
    def test_input_validation(self):
        """Test input validation for invalid parameters."""
        def f(x):
            return x**2 - 1
        
        def df(x):
            return 2*x
        
        # Non-callable function
        with self.assertRaises(TypeError):
            self.solver.find_root("not_a_function", df, 1.0)
        
        # Non-callable derivative
        with self.assertRaises(TypeError):
            self.solver.find_root(f, "not_a_function", 1.0)
        
        # Invalid initial guess
        with self.assertRaises(TypeError):
            self.solver.find_root(f, df, "not_a_number")
    
    def test_convergence_history(self):
        """Test that convergence history is recorded."""
        def f(x):
            return x**2 - 4
        
        def df(x):
            return 2*x
        
        root, converged, iterations = self.solver.find_root(f, df, 1.0)
        
        self.assertTrue(converged)
        self.assertEqual(len(self.solver.convergence_history), iterations + 1)
        self.assertEqual(self.solver.convergence_history[0], 1.0)
        self.assertAlmostEqual(self.solver.convergence_history[-1], root, places=10)
    
    def test_tolerance_settings(self):
        """Test different tolerance settings."""
        def f(x):
            return x**2 - 2
        
        def df(x):
            return 2*x
        
        # Loose tolerance
        solver_loose = NewtonRaphsonSolver(tolerance=1e-3)
        root1, converged1, iterations1 = solver_loose.find_root(f, df, 1.0)
        
        # Tight tolerance
        solver_tight = NewtonRaphsonSolver(tolerance=1e-12)
        root2, converged2, iterations2 = solver_tight.find_root(f, df, 1.0)
        
        self.assertTrue(converged1)
        self.assertTrue(converged2)
        self.assertLess(iterations1, iterations2)  # Loose tolerance should converge faster
        self.assertAlmostEqual(root1, math.sqrt(2), places=3)
        self.assertAlmostEqual(root2, math.sqrt(2), places=11)
    
    def test_multiple_roots(self):
        """Test finding different roots of x^3 - x = 0 (roots: -1, 0, 1)."""
        def f(x):
            return x**3 - x
        
        def df(x):
            return 3*x**2 - 1
        
        # Find root near 1
        root1, converged1, _ = self.solver.find_root(f, df, 0.8)
        self.assertTrue(converged1)
        self.assertAlmostEqual(root1, 1.0, places=9)
        
        # Find root near -1
        root2, converged2, _ = self.solver.find_root(f, df, -0.8)
        self.assertTrue(converged2)
        self.assertAlmostEqual(root2, -1.0, places=9)

if __name__ == "__main__":
    unittest.main()
