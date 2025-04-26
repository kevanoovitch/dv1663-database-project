import subprocess
import sys
import importlib.util
from menu import Menu


def ensure_package(package):
    if importlib.util.find_spec(package) is None:
        print(f"[INFO] Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    else:
        print(f"[INFO] {package} is already installed.")


# Intance the object we will need
menu = Menu()

# Call functions (the real main)
menu.UseMainMenu()
