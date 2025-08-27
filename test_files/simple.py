def calculate_factorial(n):
    """Calculate factorial of a number"""
    if n < 0:
        return None
    elif n == 0:
        return 1
    else:
        result = 1
        for i in range(1, n + 1):
            result *= i
        return result

# Bug: Missing edge case handling for large numbers
print(calculate_factorial(5))