import os
import subprocess
import sys

INSTANCES_DIR = "instances"

def main() -> None:
    for nombre in os.listdir(INSTANCES_DIR):
        if not nombre.endswith('.txt'):
            continue
        ruta = os.path.join(INSTANCES_DIR, nombre)
        if not os.path.isfile(ruta):
            continue
        subprocess.run([sys.executable, "solver.py", ruta], check=True)

if __name__ == "__main__":
    main()