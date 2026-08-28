"""
Ground truth for the GPP evaluation scorecard.
Each sample lists the REAL issues that exist in that file, written by hand.
This is what GPP's output gets checked against.
"""

GROUND_TRUTH = {
    "sample1.py": [
        "combined import (os, sys) on one line",
        "missing space after comma in import",
        "CalculateTotal should be snake_case (calculate_total)",
        "missing spaces around = in Total=0",
        "missing spaces around + in Total+i",
        "Total variable should be lowercase",
        "missing docstring",
    ],
    "sample2.py": [
        "missing spaces around = in message=",
        "class person should be PascalCase (Person)",
        "missing space after comma in __init__(self,age)",
        "missing spaces around = in self.age=age",
        "missing docstrings",
    ],
    "sample3.py": [
        # intentionally empty - this file is clean
    ],
    "sample_student.py": [
    "combined import (os, sys) on one line",
    "missing space after comma in import",
    "CalculateTotal should be snake_case (calculate_total)",
    "missing spaces around = in Total=0",
    "missing spaces around + in Total+i",
    "Total variable should be lowercase",
    "missing docstring for calculate_total",
    "class shopping_cart should be PascalCase (ShoppingCart)",
    "missing space after comma in __init__(self,name)",
    "missing spaces around = in self.name=name",
    "self.x is a vague/unclear attribute name (should be self.items)",
    "missing space after comma in add(self,item)",
    "extra spaces inside parentheses in add( self,item )",
    "missing docstrings for class and methods",
    "extra spaces inside parentheses in print( CalculateTotal(c.x) )",
],
}