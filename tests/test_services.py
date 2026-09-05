import tempfile
import unittest
from datetime import date
from pathlib import Path

from farmacia_vecinal.database import FarmaciaDB
from farmacia_vecinal.models import Medication
from farmacia_vecinal.services import (
    AuthService,
    AuthenticationError,
    InsufficientStockError,
    InventoryService,
    ValidationError,
)


class InventoryServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.database_path = Path(tempfile.mktemp(suffix=".db"))
        self.database = FarmaciaDB(self.database_path)
        self.inventory = InventoryService(self.database)

    def tearDown(self) -> None:
        self.database.close()
        self.database_path.unlink(missing_ok=True)

    def test_register_and_deliver_updates_stock(self) -> None:
        medication = self.inventory.register(
            Medication(None, "Paracetamol", 10, date(2099, 12, 31), "Demo")
        )

        remaining = self.inventory.deliver(medication.identifier, 4)

        self.assertEqual(remaining.quantity, 6)

    def test_delivery_cannot_exceed_stock(self) -> None:
        medication = self.inventory.register(
            Medication(None, "Ibuprofeno", 2, date(2099, 12, 31), "Demo")
        )

        with self.assertRaises(InsufficientStockError):
            self.inventory.deliver(medication.identifier, 3)

    def test_register_rejects_non_positive_quantity(self) -> None:
        with self.assertRaises(ValidationError):
            self.inventory.register(
                Medication(None, "Aspirina", 0, date(2099, 12, 31), "Demo")
            )

    def test_authentication_requires_expected_role(self) -> None:
        authentication = AuthService(self.database)

        session = authentication.authenticate("juan", "1234", "bodega")

        self.assertEqual(session.role, "bodega")
        with self.assertRaises(AuthenticationError):
            authentication.authenticate("juan", "1234", "entrega")


if __name__ == "__main__":
    unittest.main()
