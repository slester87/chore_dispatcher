#!/usr/bin/env python3
"""
Factorial Calculator
Implements both recursive and iterative approaches to calculate factorial.
"""

def validate_input(n):
    """Validate input for factorial calculation."""
    if not isinstance(n, int):
        raise TypeError("Input must be an integer")
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    return True

def factorial_recursive(n):
    """Calculate factorial using recursive approach."""
    validate_input(n)
    if n == 0 or n == 1:
        return 1
    return n * factorial_recursive(n - 1)

def factorial_iterative(n):
    """Calculate factorial using iterative approach."""
    validate_input(n)
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def main():
    """Main function with user interface."""
    print("Factorial Calculator")
    print("===================")
    
    try:
        num = int(input("Enter a non-negative integer: "))
        
        recursive_result = factorial_recursive(num)
        iterative_result = factorial_iterative(num)
        
        print(f"\nResults for {num}!:")
        print(f"Recursive approach: {recursive_result}")
        print(f"Iterative approach: {iterative_result}")
        
        if recursive_result == iterative_result:
            print("✓ Both methods agree!")
        else:
            print("✗ Methods disagree - check implementation")
            
    except ValueError as e:
        print(f"Error: {e}")
    except TypeError as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\nGoodbye!")

if __name__ == "__main__":
    main()
