"""Persistencia del sistema usando SQLAlchemy sobre SQLite.

Este modulo contiene el repositorio y los modelos de persistencia. Los
servicios trabajan con modelos del dominio y no necesitan conocer SQLAlchemy.
"""

from __future__ import annotations

import hashlib
from datetime import date, timedelta
from pathlib import Path

from sqlalchemy import Date, Engine, Integer, String, create_engine, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from .models import InventoryAlert, Medication

DATABASE_DIRECTORY = Path(__file__).resolve().parents[2] / "database"
DEFAULT_DATABASE_PATH = DATABASE_DIRECTORY / "farmacia.db"
DEFAULT_BRAND = "Desconocido"
LOW_STOCK_LIMIT = 5
EXPIRATION_ALERT_DAYS = 30

INITIAL_USERS = (
    ("bodega", "juan", "1234"),
    ("entrega", "carlos", "4567"),
)


class DatabaseError(RuntimeError):
    """Indica que una operacion de persistencia no pudo completarse."""


class Base(DeclarativeBase):
    """Clase base de los modelos administrados por SQLAlchemy."""


class MedicationRecord(Base):
    """Representa la tabla de inventario."""

    __tablename__ = "inventario"

    identifier: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    name: Mapped[str] = mapped_column("nombre", String, nullable=False)
    quantity: Mapped[int] = mapped_column("cantidad", Integer, nullable=False)
    expiration_date: Mapped[date] = mapped_column(
        "fecha_vencimiento", Date, nullable=False
    )
    brand: Mapped[str] = mapped_column(
        "marca", String, nullable=False, default=DEFAULT_BRAND
    )


class UserRecord(Base):
    """Representa la tabla de usuarios."""

    __tablename__ = "usuarios"

    identifier: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    role: Mapped[str] = mapped_column("rol", String, unique=True, nullable=False)
    username: Mapped[str] = mapped_column("usuario", String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column("password_hash", String, nullable=False)


class FarmaciaDB:
    """Repositorio de inventario y usuarios basado en SQLAlchemy ORM."""

    def __init__(
        self,
        database_path: Path | str = DEFAULT_DATABASE_PATH,
        session_factory: sessionmaker[Session] | None = None,
    ) -> None:
        """Crea el motor y prepara las tablas de la base indicada."""
        self.engine = _create_engine(database_path)
        self.session_factory = session_factory or sessionmaker(
            bind=self.engine, expire_on_commit=False
        )
        self._create_schema()

    def _create_schema(self) -> None:
        """Crea las tablas y los usuarios iniciales si no existen."""
        try:
            Base.metadata.create_all(self.engine)
            with self.session_factory.begin() as session:
                self._seed_users(session)
        except SQLAlchemyError as error:
            raise DatabaseError("No se pudo inicializar la base de datos") from error

    @staticmethod
    def _seed_users(session: Session) -> None:
        """Agrega usuarios de demostracion que aun no existan."""
        existing_users = set(session.scalars(select(UserRecord.username)))
        for role, username, password in INITIAL_USERS:
            if username not in existing_users:
                session.add(
                    UserRecord(
                        role=role,
                        username=username,
                        password_hash=_hash_password(username, password),
                    )
                )

    def list_medications(self) -> list[Medication]:
        """Devuelve todos los medicamentos ordenados por nombre."""
        try:
            with self.session_factory() as session:
                records = session.scalars(
                    select(MedicationRecord).order_by(MedicationRecord.name)
                ).all()
                return [_to_medication(record) for record in records]
        except SQLAlchemyError as error:
            raise DatabaseError("No se pudo consultar el inventario") from error

    def find_medication(self, medication_id: int) -> Medication | None:
        """Busca un medicamento por ID y devuelve `None` si no existe."""
        try:
            with self.session_factory() as session:
                record = session.get(MedicationRecord, medication_id)
                return _to_medication(record) if record else None
        except SQLAlchemyError as error:
            raise DatabaseError("No se pudo consultar el medicamento") from error

    def add_medication(self, medication: Medication) -> Medication:
        """Agrega un medicamento o suma unidades a uno existente."""
        try:
            with self.session_factory.begin() as session:
                record = session.scalar(
                    select(MedicationRecord).where(
                        MedicationRecord.name == medication.name
                    )
                )
                if record:
                    record.quantity += medication.quantity
                else:
                    record = MedicationRecord(
                        name=medication.name,
                        quantity=medication.quantity,
                        expiration_date=medication.expiration_date,
                        brand=medication.brand,
                    )
                    session.add(record)
                    session.flush()
                return _to_medication(record)
        except SQLAlchemyError as error:
            raise DatabaseError("No se pudo registrar el medicamento") from error

    def update_medication(self, medication: Medication) -> bool:
        """Actualiza un medicamento y devuelve si el ID existia."""
        if medication.identifier is None:
            return False
        try:
            with self.session_factory.begin() as session:
                record = session.get(MedicationRecord, medication.identifier)
                if record is None:
                    return False
                record.name = medication.name
                record.quantity = medication.quantity
                record.expiration_date = medication.expiration_date
                record.brand = medication.brand
                return True
        except SQLAlchemyError as error:
            raise DatabaseError("No se pudo actualizar el medicamento") from error

    def delete_medication(self, medication_id: int) -> bool:
        """Elimina un medicamento y devuelve si fue encontrado."""
        try:
            with self.session_factory.begin() as session:
                record = session.get(MedicationRecord, medication_id)
                if record is None:
                    return False
                session.delete(record)
                return True
        except SQLAlchemyError as error:
            raise DatabaseError("No se pudo eliminar el medicamento") from error

    def decrease_stock(self, medication_id: int, quantity: int) -> Medication | None:
        """Descuenta unidades si existe el medicamento y hay stock suficiente."""
        try:
            with self.session_factory.begin() as session:
                record = session.get(MedicationRecord, medication_id)
                if record is None or record.quantity < quantity:
                    return None
                record.quantity -= quantity
                session.flush()
                return _to_medication(record)
        except SQLAlchemyError as error:
            raise DatabaseError("No se pudo entregar el medicamento") from error

    def list_alerts(self, reference_date: date) -> list[InventoryAlert]:
        """Devuelve medicamentos con poco stock o vencimiento cercano."""
        expiration_limit = reference_date + timedelta(days=EXPIRATION_ALERT_DAYS)
        try:
            with self.session_factory() as session:
                records = session.scalars(
                    select(MedicationRecord)
                    .where(
                        (MedicationRecord.quantity <= LOW_STOCK_LIMIT)
                        | (MedicationRecord.expiration_date <= expiration_limit)
                    )
                    .order_by(
                        MedicationRecord.expiration_date,
                        MedicationRecord.quantity,
                    )
                ).all()
                return [_to_alert(record) for record in records]
        except SQLAlchemyError as error:
            raise DatabaseError("No se pudieron consultar las alertas") from error

    def find_user_role(self, username: str, password: str) -> str | None:
        """Busca el rol de un usuario con credenciales validas."""
        try:
            with self.session_factory() as session:
                user = session.scalar(
                    select(UserRecord).where(
                        UserRecord.username == username,
                        UserRecord.password_hash == _hash_password(username, password),
                    )
                )
                return user.role if user else None
        except SQLAlchemyError as error:
            raise DatabaseError("No se pudo validar el usuario") from error

    def close(self) -> None:
        """Libera el motor y sus conexiones."""
        self.engine.dispose()


def _create_engine(database_path: Path | str) -> Engine:
    """Crea un motor SQLite para la ruta recibida."""
    resolved_path = Path(database_path).resolve()
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{resolved_path}")


def _hash_password(username: str, password: str) -> str:
    """Genera el hash usado para comparar una contrasena."""
    return hashlib.sha256(f"{username}:{password}".encode()).hexdigest()


def _to_medication(record: MedicationRecord) -> Medication:
    """Convierte un registro ORM en un modelo del dominio."""
    return Medication(
        identifier=record.identifier,
        name=record.name,
        quantity=record.quantity,
        expiration_date=record.expiration_date,
        brand=record.brand,
    )


def _to_alert(record: MedicationRecord) -> InventoryAlert:
    """Convierte un registro ORM en una alerta del dominio."""
    return InventoryAlert(
        name=record.name,
        quantity=record.quantity,
        expiration_date=record.expiration_date,
        brand=record.brand,
    )
