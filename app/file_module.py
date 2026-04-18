from pathlib import Path
from datetime import datetime
import os


def save_text(content: str, prefix: str = "network_result") -> str:
    # Ruta de Descargas del usuario
    downloads_path = Path.home() / "Downloads"

    # Crear carpeta si no existe (por seguridad)
    downloads_path.mkdir(parents=True, exist_ok=True)

    # Nombre con fecha y hora
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = downloads_path / f"{prefix}_{timestamp}.txt"

    # Guardar archivo
    file_path.write_text(content, encoding="utf-8")

    return str(file_path)