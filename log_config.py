import os
import sys
import logging
from datetime import datetime
from pathlib import Path
import arcpy

def setup_logger(
    name="wegennetwerk",
    log_level_console=logging.INFO,
    log_level_file=logging.DEBUG
):
    # Map van dit script
    script_dir = Path(__file__).resolve().parent

    # Datum en uur in bestandsnaam
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = script_dir / f"{name}_{timestamp}.log"

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    logger.propagate = False  # voorkomt dubbele logs via root logger

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(log_level_console)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File
    fh = logging.FileHandler(log_file, mode="a", encoding="utf-8")
    fh.setLevel(log_level_file)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Alleen ArcPy handler toevoegen als je in ArcGIS draait
    if "arcgispro-py3" in sys.executable.lower() and os.environ.get("AGP_PYTHON_TOOL", "") == "1":
        class ArcpyHandler(logging.Handler):
            def emit(self, record):
                msg = self.format(record)
                if record.levelno >= logging.ERROR:
                    arcpy.AddError(msg)
                elif record.levelno >= logging.WARNING:
                    arcpy.AddWarning(msg)
                else:
                    arcpy.AddMessage(msg)
        logger.addHandler(ArcpyHandler())

    return logger

# 🔹 Maak de logger éénmalig aan
logger = setup_logger()
