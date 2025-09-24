"""
db4e/Constants/DSelect.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from db4e.Constants.DLabel import DLabel


WEEKS_1 = 7 * 24
WEEKS_2 = 14 * 24
MONTHS_1 = 30 * 24
MONTHS_3 = 30 * 24 * 3
MONTHS_6 = 30 * 24 * 6

class DSelect:
    SELECT_LIST = [
        (DLabel.WEEK_1, WEEKS_1),
        (DLabel.WEEKS_2, WEEKS_2),
        (DLabel.MONTH_1, MONTHS_1),
        (DLabel.MONTHS_3, MONTHS_3),
        (DLabel.MONTHS_6, MONTHS_6),
        (DLabel.ALL_TIME, -1)    
    ]
    ONE_WEEK = WEEKS_1