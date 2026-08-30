"""Cloud-safe entrypoint for the Evidence Gap Navigator research module."""

from pathlib import Path
import runpy


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MODULE_APP = (
    REPOSITORY_ROOT
    / "T3 - Dashboards, Interfaces & Open Infrastructure"
    / "T3-R3 - Evidence Gap Navigator"
    / "R3a-evidence-gap-navigator"
    / "app.py"
)

runpy.run_path(str(MODULE_APP), run_name="__main__")
