# db4e/Constants/DUvicorn.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    Website: https://db4e.osoyalce.com/
#    License: GPL 3.0


from db4e.util.ConstGroup import ConstGroup


# Uvicorn constants
class DUvicorn(ConstGroup):
    CLASS: str = "class"
    DEFAULT: str = "default"
    DISABLE_EXISTING_LOGGERS: str = "disable_existing_loggers"
    FILENAME: str = "filename"
    FMT: str = "fmt"
    FORMATTERS: str = "formatters"
    FORMATTER: str = "formatter"
    HANDLERS: str = "handlers"
    LOGGING_FILEHANDLER: str = "logging.FileHandler"
    USE_COLORS: str = "use_colors"
    UVICORN_LOGGING_DEFAULT_FORMATTER: str = "uvicorn.logging.DefaultFormatter"
