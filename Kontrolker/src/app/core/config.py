# src/app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AnyUrl
from typing import Optional

class Settings(BaseSettings):
    # ---- Configuración de tu app (tipado + defaults) ----
    ENV: str = Field(default="dev")
    DB_URL: str = Field(default="sqlite:///./kontrolker.db")
    API_PORT: int = Field(default=8000)
    DEBUG: bool = Field(default=True)

    # (Ejemplo de campo opcional)
    DOCKER_HOST: Optional[str] = None

    # ---- De dónde leer las variables (.env) ----
    model_config = SettingsConfigDict(
        env_file=".env",           # lee automáticamente tu .env en la raíz
        env_file_encoding="utf-8", # por si hay acentos
        case_sensitive=False       # variables no sensibles a mayúsculas
    )

# Instancia global para importar en el resto de la app
settings = Settings()
