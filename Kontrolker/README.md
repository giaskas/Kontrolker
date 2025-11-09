# Kontrolker
API de Orquestación de Contenedores Simplificada, que ofrece una capa de abstracción sobre Docker, permitiendo a los desarrolladores desplegar, gestionar y escalar contenedores en un pequeño clúster de máquinas con comandos simples, sin tener que escribir complejos archivos YAML.






📦 Requisitos previos

Antes de iniciar, asegúrate de tener instalado:


 Python 3.10 o superior
 Git
 Docker Desktop (opcional, solo si quieres correrlo en contenedor)


1️⃣ Clonar el repositorio

git clone https://github.com/TU_USUARIO/kontrolker.git
cd kontrolker

2️⃣ Crear y activar el entorno virtual
 
python -m venv venv
venv\Scripts\activate


Cuando esté activo, verás (venv) al inicio de tu línea de comandos.

3️⃣ Instalar dependencias
 
pip install -r requirements.txt

⚙️4️⃣ Configurar el entorno (.env)
Copia el archivo de ejemplo y renómbralo:


copy .env.example .env

Abre el archivo .env y verifica que contenga lo siguiente:

ENV=dev
DB_URL=sqlite:///./kontrolker.db


5️⃣ Configurar el path del proyecto
FastAPI está dentro de la carpeta src/, así que se necesita agregarla al PYTHONPATH:


$env:PYTHONPATH = (Resolve-Path .\src).Path

▶️ 6️⃣ Ejecutar la aplicación

Desde la raíz del proyecto:

uvicorn --app-dir src app.main:app --reload


La API estará disponible en:

🌐 http://127.0.0.1:8000

📘 Swagger Docs: http://127.0.0.1:8000/docs

🧪 7️⃣ Probar el endpoint de salud

Ejecuta este comando en la terminal:

curl http://127.0.0.1:8000/health


Debe responder:

{"status": "ok"}

🐋 8️⃣ (Opcional) Ejecutar con Docker

Si tienes Docker instalado y prefieres levantarlo con un solo comando:

docker compose up --build


Esto:

Construirá la imagen con el Dockerfile.

Levantará la API en http://127.0.0.1:8000.

🗂️ 9️⃣ Estructura general del proyecto
src/app/
├── core/         → Configuración y logs
├── db/           → Conexión a la base de datos
├── models/       → Modelos SQLModel
├── schemas/      → Validaciones Pydantic
├── routers/      → Endpoints (Projects, Services, etc.)
├── services/     → Lógica de negocio
├── engines/      → Integraciones externas (Docker)
├── tests/        → Pruebas automatizadas
└── main.py       → Punto de entrada de la app

🧾 🔟 Comandos útiles
Acción	Comando
🔹 Formatear código	ruff check . --fix
🔹 Ejecutar pruebas	pytest -q
🔹 Regenerar requirements.txt	pip freeze > requirements.txt
🔹 Salir del entorno virtual	deactivate
💡 Notas finales

No subas tu archivo .env al repositorio, solo el .env.example.

Si Uvicorn no detecta el módulo app, asegúrate de usar:

uvicorn --app-dir src app.main:app --reload


Puedes editar los valores de DB_URL y ENV según tu entorno.
uvicorn --app-dir src app.main:app --reload
si
-

#es una prueba de Malvaez