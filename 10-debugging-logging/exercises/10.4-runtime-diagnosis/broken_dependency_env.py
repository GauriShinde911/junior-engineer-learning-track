"""
broken_dependency_env.py - Runtime Diagnosis: Dependency & Environment Conflicts

Simulates runtime failures caused by missing third-party dependencies, virtualenv
mismatches, or incompatible package versions.
"""

import sys
import importlib
from typing import Dict, Any, Optional


class DependencyError(Exception):
    """Raised when a required module or version is unavailable."""
    def __init__(self, message: str, error_type: str):
        super().__init__(message)
        self.error_type = error_type


def load_required_engine(module_name: str, min_version: Optional[str] = None) -> Any:
    """
    Imports a runtime engine module and optionally validates semantic versioning.
    Raises DependencyError with clear diagnostic context if missing or incompatible.
    """
    try:
        mod = importlib.import_module(module_name)
    except ModuleNotFoundError as e:
        raise DependencyError(
            f"Module '{module_name}' is not installed in interpreter '{sys.executable}'.",
            error_type="MISSING_MODULE"
        ) from e

    if min_version:
        mod_version = getattr(mod, "__version__", None)
        if mod_version is None:
            raise DependencyError(
                f"Module '{module_name}' has no '__version__' attribute to verify against {min_version}.",
                error_type="UNKNOWN_VERSION"
            )
        
        # Simple tuple-based numeric version comparison
        def parse_v(v_str: str):
            return tuple(int(x) for x in v_str.split(".") if x.isdigit())

        if parse_v(mod_version) < parse_v(min_version):
            raise DependencyError(
                f"Module '{module_name}' version {mod_version} is incompatible; requires >= {min_version}.",
                error_type="INCOMPATIBLE_VERSION"
            )

    return mod


def diagnose_python_environment(module_name: str) -> Dict[str, Any]:
    """
    Diagnoses whether missing dependency is due to inactive venv, wrong python interpreter,
    or missing package in requirements.
    """
    is_in_venv = sys.prefix != sys.base_prefix
    
    try:
        mod = importlib.import_module(module_name)
        return {
            "status": "INSTALLED",
            "location": getattr(mod, "__file__", "built-in"),
            "version": getattr(mod, "__version__", "unknown"),
            "python_executable": sys.executable,
            "in_virtualenv": is_in_venv,
            "remediation": "No action needed."
        }
    except ModuleNotFoundError:
        return {
            "status": "MISSING",
            "python_executable": sys.executable,
            "in_virtualenv": is_in_venv,
            "sys_path_sample": sys.path[:3],
            "root_cause": (
                "Virtual environment not activated" if not is_in_venv else "Package not installed in active venv"
            ),
            "remediation": (
                f"Run: pip install {module_name}" if is_in_venv else "Activate your virtual environment (source .venv/bin/activate) before running."
            )
        }


if __name__ == "__main__":
    print("Testing missing dependency diagnosis:")
    try:
        load_required_engine("non_existent_accelerator_pkg")
    except DependencyError as err:
        print("Caught expected dependency error:", err)
        print("Diagnostic summary:", diagnose_python_environment("non_existent_accelerator_pkg"))
