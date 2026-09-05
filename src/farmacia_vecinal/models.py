"""Define los datos principales que usa la aplicacion.

Este modulo funciona como un contrato: indica que informacion tiene un
medicamento, una alerta y una sesion de usuario. Los objetos son inmutables
para evitar cambios accidentales mientras viajan entre las capas del sistema.

- El decorador @dataclass(frozen=True) hace que los objetos sean inmutables.
- El argumento slots=True hace que los objetos ocupen menos memoria y sean mas rapidos.
"""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class Medication:
    """Representa un medicamento y sus datos de inventario."""

    identifier: int | None
    name: str
    quantity: int
    expiration_date: date
    brand: str


@dataclass(frozen=True, slots=True)
class InventoryAlert:
    """Representa un medicamento que necesita atencion."""

    name: str
    quantity: int
    expiration_date: date
    brand: str


@dataclass(frozen=True, slots=True)
class UserSession:
    """Representa al usuario que inicio sesion y su rol."""

    username: str
    role: str
