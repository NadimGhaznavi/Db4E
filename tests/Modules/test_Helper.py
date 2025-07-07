"""
tests/Modules/test_Helper.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0
"""

from db4e.Modules.Helper import result_row

def test_result_row():
    label = "Deployment"
    status = "good"
    message = "Everything went smoothly"

    expected = {
        "Deployment": {
            "status": "good",
            "msg": "Everything went smoothly"
        }
    }

    assert result_row(label, status, message) == expected