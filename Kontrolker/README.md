# Kontrolker
API de Orquestación de Contenedores Simplificada, que ofrece una capa de abstracción sobre Docker, permitiendo a los desarrolladores desplegar, gestionar y escalar contenedores en un pequeño clúster de máquinas con comandos simples, sin tener que escribir complejos archivos YAML.






Kontrolker API — Guía de instalación y ejecución
Requisitos previos

Asegúrate de tener instalado:
Python 3.10 o superior
Git
Docker Desktop

Crear y activar el entorno virtual

En Windows (PowerShell)
-
python -m venv venv
venv\Scripts\activate
-
Cuando esté activado, deberías ver algo como (venv) al inicio de tu línea de comandos.

Instalar dependencias
-
pip install -r requirements.txt
-

Crear archivo de entorno (.env)

Edita el .env (puedes hacerlo desde VS Code o un editor de texto):

ENV=dev
DB_URL=sqlite:///./kontrolker.db


Configurar el path del proyecto
FastAPI está dentro de la carpeta src/, así que asegúrate de incluirla en el path.
-
$env:PYTHONPATH = (Resolve-Path .\src).Path
-

Ejecutar la aplicación
Desde la raíz del proyecto:
-
uvicorn --app-dir src app.main:app --reload
-