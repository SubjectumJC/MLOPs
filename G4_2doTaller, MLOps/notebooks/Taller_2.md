# Taller Desarrollo en Contenedores

Deben integrar **uv** en el Proyecto con **Docker Compose**.
Anteriormente, configuramos un entorno de desarrollo para Machine Learning utilizando Docker Compose y Jupyter Lab. Ahora, integraremos uv en este entorno para gestionar las dependencias de manera más eficiente.

Cree un ambiente de desarrollo usando Docker compose, este ambiente debe tener una instancia de JupyterLab instalada mediante UV. En este ambiente entrene nuevos modelos. Los nuevos modelos deben ser consumidos por una API desplegada en el mismo docker compose, sin embargo, los modelos entrenados deben ser compartidos por los dos servicios. Es decir, cuando un nuevo modelo es guardado en el notebook, la API puede consumirlo para realizar inferencia.

![Taller Desarrollo en Contenedores](Desarrollo_en_contenedores.png)