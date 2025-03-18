Este directorio contiene archivos para configurar MLflow, como el servicio systemd:
- mlflow_serv.service

Pasos:

1. Ajusta las IP y credenciales en ../paths.env
2. Ajusta en mlflow_serv.service:
   - EnvironmentFile= (debe apuntar a la ruta real)
   - WorkingDirectory= (ruta real de tu proyecto)
3. Copiar mlflow_serv.service a /etc/systemd/system/:
   sudo cp mlflow_serv.service /etc/systemd/system/mlflow_serv.service

4. sudo systemctl daemon-reload
5. sudo systemctl enable mlflow_serv.service
6. sudo systemctl start mlflow_serv.service
7. sudo systemctl status mlflow_serv.service
