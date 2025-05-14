import subprocess, os, sys
print(">> Ejecutando worker de entrenamiento")
subprocess.check_call(["python", "-u", "/data/train_local/train.py"])

