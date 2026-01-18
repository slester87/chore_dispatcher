#!/usr/bin/env python3
"""
Test suite for factorial calculator
"""

import unittest
from factorial_calculator import factorial_recursive, factorial_iterative, validate_input

class TestFactorialCalculator(unittest.TestCase):
    
    def test_validate_input_valid(self):
        """Test validation with valid inputs."""
        self.assertTrue(validate_input(0))
        self.assertTrue(validate_input(5))
        self.assertTrue(validate_input(10))
    
    def test_validate_input_negative(self):
        """Test validation rejects negative numbers."""
        with self.assertRaises(ValueError):
            validate_input(-1)
        with self.assertRaises(ValueError):
            validate_input(-10)
    
    def test_validate_input_non_integer(self):
        """Test validation rejects non-integers."""
        with self.assertRaises(TypeError):
            validate_input(3.14)
        with self.assertRaises(TypeError):
            validate_input("5")
    
    def test_factorial_base_cases(self):
        """Test factorial base cases (0! and 1!)."""
        self.assertEqual(factorial_recursive(0), 1)
        self.assertEqual(factorial_iterative(0), 1)
        self.assertEqual(factorial_recursive(1), 1)
        self.assertEqual(factorial_iterative(1), 1)
    
    def test_factorial_small_numbers(self):
        """Test factorial for small numbers."""
        test_cases = [
            (2, 2),
            (3, 6),
            (4, 24),
            (5, 120)
        ]
        
        for n, expected in test_cases:
            with self.subTest(n=n):
                self.assertEqual(factorial_recursive(n), expected)
                self.assertEqual(factorial_iterative(n), expected)
    
    def test_factorial_larger_numbers(self):
        """Test factorial for larger numbers."""
        test_cases = [
            (6, 720),
            (7, 5040),
            (10, 3628800)
        ]
        
        for n, expected in test_cases:
            with self.subTest(n=n):
                self.assertEqual(factorial_recursive(n), expected)
                self.assertEqual(factorial_iterative(n), expected)
    
    def test_methods_agree(self):
        """Test that both methods produce identical results."""
        for n in range(0, 15):
            with self.subTest(n=n):
                recursive_result = factorial_recursive(n)
                iterative_result = factorial_iterative(n)
                self.assertEqual(recursive_result, iterative_result)
    
    def test_factorial_negative_numbers(self):
        """Test that negative numbers raise ValueError."""
        with self.assertRaises(ValueError):
            factorial_recursive(-1)
        with self.assertRaises(ValueError):
            factorial_iterative(-1)

if __name__ == "__main__":
    unittest.main()
