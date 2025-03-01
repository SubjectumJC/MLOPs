FROM python:3.9

WORKDIR /app

# Instalar uv y dependencias del proyecto
RUN pip install uv
COPY pyproject.toml pyproject.toml
RUN uv sync && uv add jupyterlab

CMD ["uv", "run", "--with", "jupyter", "jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--allow-root", "--NotebookApp.token=''"]
