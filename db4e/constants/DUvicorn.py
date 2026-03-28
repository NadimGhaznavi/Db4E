# db4e/Constants/DUvicorn.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    Website: https://db4e.osoyalce.com/
#    License: GPL 3.0


from typing import Final


# Uvicorn constants
class DUvicorn:
    CLASS: Final[str] = "class"
    DEFAULT: Final[str] = "default"
    DISABLE_EXISTING_LOGGERS: Final[str] = "disable_existing_loggers"
    FILENAME: Final[str] = "filename"
    FMT: Final[str] = "fmt"
    FORMATTERS: Final[str] = "formatters"
    FORMATTER: Final[str] = "formatter"
    HANDLERS: Final[str] = "handlers"
    LOGGING_FILEHANDLER: Final[str] = "logging.FileHandler"
    USE_COLORS: Final[str] = "use_colors"
    UVICORN_LOGGING_DEFAULT_FORMATTER: Final[str] = "uvicorn.logging.DefaultFormatter"
