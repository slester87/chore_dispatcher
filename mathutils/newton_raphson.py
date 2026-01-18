#!/usr/bin/env python3
"""
Newton-Raphson Root Finding Algorithm
Implements the Newton-Raphson method for finding roots of equations.
"""

import math

class NewtonRaphsonSolver:
    """Newton-Raphson method for finding roots of equations."""
    
    def __init__(self, tolerance=1e-10, max_iterations=100):
        """
        Initialize the Newton-Raphson solver.
        
        Args:
            tolerance: Convergence tolerance (default: 1e-10)
            max_iterations: Maximum number of iterations (default: 100)
        """
        self.tolerance = tolerance
        self.max_iterations = max_iterations
        self.iterations = 0
        self.convergence_history = []
    
    def find_root(self, func, derivative, initial_guess):
        """
        Find root using Newton-Raphson method.
        
        Args:
            func: Function f(x) to find root of
            derivative: Derivative f'(x) of the function
            initial_guess: Initial guess for the root
            
        Returns:
            tuple: (root, converged, iterations)
        """
        self._validate_inputs(func, derivative, initial_guess)
        
        x = float(initial_guess)
        self.iterations = 0
        self.convergence_history = [x]
        
        for i in range(self.max_iterations):
            self.iterations = i + 1
            
            # Evaluate function and derivative
            fx = func(x)
            fpx = derivative(x)
            
            # Check for division by zero
            if abs(fpx) < 1e-15:
                raise ValueError(f"Derivative is zero at x={x}. Cannot continue.")
            
            # Newton-Raphson iteration
            x_new = x - fx / fpx
            self.convergence_history.append(x_new)
            
            # Check convergence
            if self._check_convergence(x, x_new, fx):
                return x_new, True, self.iterations
            
            x = x_new
        
        # Did not converge
        return x, False, self.iterations
    
    def _check_convergence(self, x_old, x_new, func_value):
        """Check if the algorithm has converged."""
        # Check function value convergence
        if abs(func_value) < self.tolerance:
            return True
        
        # Check step size convergence
        if abs(x_new - x_old) < self.tolerance:
            return True
        
        return False
    
    def _validate_inputs(self, func, derivative, initial_guess):
        """Validate input parameters."""
        if not callable(func):
            raise TypeError("Function must be callable")
        if not callable(derivative):
            raise TypeError("Derivative must be callable")
        
        try:
            float(initial_guess)
        except (TypeError, ValueError):
            raise TypeError("Initial guess must be a number")
        
        # Test function calls
        try:
            func(float(initial_guess))
            derivative(float(initial_guess))
        except Exception as e:
            raise ValueError(f"Error evaluating function at initial guess: {e}")

# Example functions for testing
def polynomial_example():
    """Example: Find root of x^2 - 2 = 0 (should find sqrt(2))"""
    def f(x):
        return x**2 - 2
    
    def df(x):
        return 2*x
    
    solver = NewtonRaphsonSolver()
    root, converged, iterations = solver.find_root(f, df, 1.0)
    
    print(f"Finding root of x^2 - 2 = 0")
    print(f"Root: {root:.10f}")
    print(f"Converged: {converged}")
    print(f"Iterations: {iterations}")
    print(f"Verification: f({root}) = {f(root):.2e}")
    print(f"Expected: sqrt(2) = {math.sqrt(2):.10f}")
    return root, converged, iterations

def transcendental_example():
    """Example: Find root of cos(x) - x = 0"""
    def f(x):
        return math.cos(x) - x
    
    def df(x):
        return -math.sin(x) - 1
    
    solver = NewtonRaphsonSolver()
    root, converged, iterations = solver.find_root(f, df, 0.5)
    
    print(f"\nFinding root of cos(x) - x = 0")
    print(f"Root: {root:.10f}")
    print(f"Converged: {converged}")
    print(f"Iterations: {iterations}")
    print(f"Verification: f({root}) = {f(root):.2e}")
    return root, converged, iterations

def main():
    """Demonstrate Newton-Raphson method with examples."""
    print("Newton-Raphson Root Finding Algorithm")
    print("=" * 40)
    
    try:
        # Example 1: Polynomial
        polynomial_example()
        
        # Example 2: Transcendental
        transcendental_example()
        
        # Example 3: Custom function
        print(f"\nFinding root of x^3 - x - 1 = 0")
        def f(x):
            return x**3 - x - 1
        
        def df(x):
            return 3*x**2 - 1
        
        solver = NewtonRaphsonSolver(tolerance=1e-12)
        root, converged, iterations = solver.find_root(f, df, 1.5)
        
        print(f"Root: {root:.10f}")
        print(f"Converged: {converged}")
        print(f"Iterations: {iterations}")
        print(f"Verification: f({root}) = {f(root):.2e}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
