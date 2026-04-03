# db4e/Constants/DSystemD.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0


from typing import Final


class DSystemD:
    ACTIVE: Final[str] = "active"
    DISABLE: Final[str] = "disable"
    ENABLE: Final[str] = "enable"
    ENABLED: Final[str] = "enabled"
    INACTIVE: Final[str] = "inactive"
    PID: Final[str] = "pid"
    RAW_STDOUT: Final[str] = "raw_stdout"
    RAW_STDERR: Final[str] = "raw_stderr"
    REPLACE: Final[str] = "replace"
    SERVICE_SUFFIX: Final[str] = ".service"
    START: Final[str] = "start"
    STATUS: Final[str] = "status"
    STOP: Final[str] = "stop"
