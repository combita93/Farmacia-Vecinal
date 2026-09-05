"""Aplica las reglas de negocio de la farmacia.

`InventoryService` valida y coordina las operaciones del inventario.
`AuthService` comprueba las credenciales y el rol de cada usuario. Esta capa
no conoce ventanas ni botones, por eso puede probarse sin iniciar Qt.
"""

import logging
from datetime import date

from .database import FarmaciaDB
from .models import InventoryAlert, Medication, UserSession

BODEGA_ROLE = "bodega"
DELIVERY_ROLE = "entrega"
LOGGER = logging.getLogger(__name__)


class ValidationError(ValueError):
    """Indica que los datos recibidos no son validos."""


class AuthenticationError(ValueError):
    """Indica que el usuario o el rol no son validos."""


class MedicationNotFoundError(LookupError):
    """Indica que el medicamento solicitado no existe."""


class InsufficientStockError(ValueError):
    """Indica que no hay unidades suficientes para una entrega."""


class InventoryService:
    """Valida y ejecuta las operaciones del inventario."""

    def __init__(self, database: FarmaciaDB) -> None:
        """Recibe el repositorio que usara para las operaciones."""
        self.database = database

    def list_medications(self) -> list[Medication]:
        """Devuelve el inventario completo."""
        return self.database.list_medications()

    def find_medication(self, medication_id: int) -> Medication | None:
        """Busca un medicamento sin lanzar error si no existe."""
        return self.database.find_medication(medication_id)

    def register(self, medication: Medication) -> Medication:
        """Valida y registra un medicamento en el inventario."""
        self._validate_name(medication.name)
        self._validate_positive_quantity(medication.quantity)
        registered_medication = self.database.add_medication(medication)
        LOGGER.info(
            "Medicamento registrado: nombre=%s, cantidad=%s",
            registered_medication.name,
            medication.quantity,
        )
        return registered_medication

    def deliver(self, medication_id: int, quantity: int) -> Medication:
        """Entrega unidades y devuelve el medicamento con su stock restante."""
        self._validate_positive_quantity(quantity)
        medication = self._find_or_raise(medication_id)
        if quantity > medication.quantity:
            raise InsufficientStockError(
                f"Stock disponible: {medication.quantity}"
            )
        delivered = self.database.decrease_stock(medication_id, quantity)
        if delivered is None:
            raise InsufficientStockError("El stock cambio antes de completar la entrega")
        LOGGER.info(
            "Medicamento entregado: id=%s, cantidad=%s, restante=%s",
            medication_id,
            quantity,
            delivered.quantity,
        )
        return delivered

    def update(self, medication: Medication) -> Medication:
        """Valida y guarda los nuevos datos de un medicamento."""
        self._validate_name(medication.name)
        if medication.quantity < 0:
            raise ValidationError("La cantidad no puede ser negativa")
        if medication.identifier is None or not self.database.update_medication(medication):
            raise MedicationNotFoundError("El medicamento no existe")
        LOGGER.info("Medicamento actualizado: id=%s", medication.identifier)
        return self._find_or_raise(medication.identifier)

    def delete(self, medication_id: int) -> None:
        """Elimina un medicamento o lanza error si no existe."""
        if not self.database.delete_medication(medication_id):
            raise MedicationNotFoundError("El medicamento no existe")
        LOGGER.info("Medicamento eliminado: id=%s", medication_id)

    def alerts(self, reference_date: date | None = None) -> list[InventoryAlert]:
        """Devuelve alertas tomando como referencia la fecha indicada."""
        return self.database.list_alerts(reference_date or date.today())

    @staticmethod
    def _validate_name(name: str) -> None:
        """Comprueba que el nombre no este vacio."""
        if not name.strip():
            raise ValidationError("El nombre del medicamento es obligatorio")

    @staticmethod
    def _validate_positive_quantity(quantity: int) -> None:
        """Comprueba que una cantidad sea mayor que cero."""
        if quantity <= 0:
            raise ValidationError("La cantidad debe ser positiva")

    def _find_or_raise(self, medication_id: int) -> Medication:
        """Busca un medicamento y lanza error si no existe."""
        medication = self.database.find_medication(medication_id)
        if medication is None:
            raise MedicationNotFoundError("El medicamento no existe")
        return medication


class AuthService:
    """Comprueba credenciales y crea sesiones de usuario."""

    def __init__(self, database: FarmaciaDB) -> None:
        """Recibe el repositorio que contiene los usuarios."""
        self.database = database

    def authenticate(
        self, username: str, password: str, required_role: str
    ) -> UserSession:
        """Valida credenciales y devuelve una sesion con el rol solicitado."""
        normalized_username = username.strip()
        if not normalized_username or not password:
            raise AuthenticationError("El usuario y la contrasena son obligatorios")
        role = self.database.find_user_role(normalized_username, password)
        if role != required_role:
            LOGGER.warning(
                "Autenticacion rechazada: usuario=%s, rol=%s",
                normalized_username,
                required_role,
            )
            raise AuthenticationError("Credenciales o rol incorrectos")
        LOGGER.info("Usuario autenticado: usuario=%s, rol=%s", normalized_username, role)
        return UserSession(normalized_username, role)
