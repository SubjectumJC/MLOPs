import subprocess, os, sys, pathlib
print(">> Ejecutando entrenamiento local")
script_path = pathlib.Path(__file__).parent / "train_local" / "train.py"
subprocess.check_call([sys.executable, "-u", str(script_path)])
