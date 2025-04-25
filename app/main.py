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


ensure_package("rich")

# Now you can use it!
from rich.console import Console

console = Console()
console.print("[bold green]Hello, Rich world![/bold green]")

# Intance the object we will need
menu = Menu()

# Call functions (the real main)
menu.UseMainMenu()
