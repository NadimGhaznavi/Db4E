# db4e/Constants/DStatus.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0


from typing import Final


# Status
class DStatus:
    COMPLETE: Final[str] = "complete"
    ERROR: Final[str] = "error"
    GOOD: Final[str] = "good"
    PENDING: Final[str] = "pending"
    PROCESSING: Final[str] = "processing"
    UNKNOWN: Final[str] = "unknown"
    WARN: Final[str] = "warn"
