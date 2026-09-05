"""Inicia la aplicacion y expone su ventana principal.

El trabajo de la interfaz esta en `ui.main_window`. Este archivo solo deja
un punto de entrada pequeno para ejecutar la aplicacion como modulo o comando.
"""

from .ui.main_window import FarmaciaComunalApp, run

__all__ = ["FarmaciaComunalApp", "run"]


if __name__ == "__main__":
    run()
