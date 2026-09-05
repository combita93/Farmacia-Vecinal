"""Construye la ventana y conecta las acciones de Qt con los servicios.

La ventana recoge datos del usuario, llama a la capa de servicios y muestra
el resultado. No contiene consultas SQL ni reglas de inventario.
"""

from __future__ import annotations

import sys
from datetime import date

from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QCursor, QFont
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QDateEdit,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..database import DatabaseError, FarmaciaDB
from ..models import InventoryAlert, Medication, UserSession
from ..services import (
    AuthService,
    AuthenticationError,
    BODEGA_ROLE,
    DELIVERY_ROLE,
    InsufficientStockError,
    InventoryService,
    MedicationNotFoundError,
    ValidationError,
)
from . import styles

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 750
TABLE_COLUMNS = [
    "ID",
    "Medicamento",
    "Unidades Disponibles",
    "Fecha de Vencimiento",
    "Laboratorio",
]


class FarmaciaComunalApp(QMainWindow):
    """Ventana principal para gestionar medicamentos y sesiones."""

    def __init__(
        self,
        database: FarmaciaDB | None = None,
        inventory_service: InventoryService | None = None,
        auth_service: AuthService | None = None,
    ) -> None:
        """Crea la ventana y recibe sus dependencias por inyeccion."""
        super().__init__()
        self.database = database or FarmaciaDB()
        self.inventory_service = inventory_service or InventoryService(self.database)
        self.auth_service = auth_service or AuthService(self.database)
        self.current_session: UserSession | None = None

        self.setWindowTitle("Sistema Farmacia Comunal")
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setStyleSheet(styles.get_stylesheet())
        self._build_interface()
        self.refresh_inventory()
        self._refresh_session_status()

    def _build_interface(self) -> None:
        """Construye las secciones principales de la ventana."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(30, 20, 30, 30)
        self.main_layout.setSpacing(20)
        self._build_header()
        self._build_login_section()
        self._build_registration_section()
        self._build_inventory_table()
        self._build_management_section()

    def _build_header(self) -> None:
        """Crea el titulo, el estado de sesion y el cierre de sesion."""
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        title_column = QVBoxLayout()
        title_column.setSpacing(2)
        title = QLabel("Farmacia Comunal")
        title.setObjectName("lbl_titulo")
        subtitle = QLabel("Sistema de gestion de inventario y entrega de medicamentos")
        subtitle.setObjectName("lbl_subtitulo")
        title_column.addWidget(title)
        title_column.addWidget(subtitle)
        layout.addLayout(title_column)
        layout.addStretch()

        self.session_label = QLabel("Sin sesion activa")
        self.session_label.setObjectName("lbl_sesion")
        self.session_label.setProperty("estado", "inactiva")
        layout.addWidget(self.session_label)

        self.logout_button = self._button("Cerrar Sesion", "btn_logout")
        self.logout_button.clicked.connect(self.logout)
        self.logout_button.setEnabled(False)
        layout.addWidget(self.logout_button)
        self.main_layout.addWidget(header)

    def _build_login_section(self) -> None:
        """Crea los botones de acceso para cada rol."""
        group = QGroupBox("Inicio de Sesion")
        layout = QHBoxLayout(group)
        layout.setContentsMargins(30, 10, 30, 20)
        layout.setSpacing(20)
        layout.addWidget(self._login_button("Ingreso: Almacenamiento Bodega", BODEGA_ROLE))
        layout.addStretch()
        layout.addWidget(self._login_button("Ingreso: Entrega Medicamentos", DELIVERY_ROLE))
        self.main_layout.addWidget(group)

    def _build_registration_section(self) -> None:
        """Crea el formulario para registrar medicamentos."""
        group = QGroupBox("Ingreso de medicamentos a la bodega")
        layout = QGridLayout(group)
        layout.setContentsMargins(25, 35, 25, 25)
        layout.setSpacing(15)

        layout.addWidget(QLabel("Nombre:"), 0, 0)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ej. Paracetamol")
        layout.addWidget(self.name_input, 0, 1)

        layout.addWidget(QLabel("Cantidad:"), 0, 2)
        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("0")
        layout.addWidget(self.quantity_input, 0, 3)

        layout.addWidget(QLabel("Vencimiento:"), 0, 4)
        self.expiration_input = QDateEdit(QDate.currentDate())
        self.expiration_input.setDisplayFormat("yyyy-MM-dd")
        self.expiration_input.setCalendarPopup(True)
        layout.addWidget(self.expiration_input, 0, 5)

        layout.addWidget(QLabel("Laboratorio:"), 0, 6)
        self.brand_input = QLineEdit()
        self.brand_input.setPlaceholderText("Marca o Lab")
        layout.addWidget(self.brand_input, 0, 7)

        save_button = self._button("Ingreso a Bodega", "btn_accion")
        save_button.clicked.connect(self.save_medication)
        layout.addWidget(save_button, 0, 8)
        self.main_layout.addWidget(group)

    def _build_inventory_table(self) -> None:
        """Crea y configura la tabla del inventario."""
        self.table = QTableWidget()
        self.table.setColumnCount(len(TABLE_COLUMNS))
        self.table.setHorizontalHeaderLabels(TABLE_COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.main_layout.addWidget(self.table)

    def _build_management_section(self) -> None:
        """Crea los botones de entrega, edicion, eliminacion y alertas."""
        group = QGroupBox("Gestion de Inventario")
        layout = QHBoxLayout(group)
        layout.setContentsMargins(25, 35, 25, 25)
        layout.setSpacing(15)

        deliver_button = self._button("Entrega de medicamentos")
        deliver_button.clicked.connect(self.deliver_medication)
        layout.addWidget(deliver_button)

        edit_button = self._button("Editar medicamento", "btn_secundario")
        edit_button.clicked.connect(self.edit_medication)
        layout.addWidget(edit_button)

        delete_button = self._button("Eliminar medicamento", "btn_peligro")
        delete_button.clicked.connect(self.delete_medication)
        layout.addWidget(delete_button)
        layout.addStretch()

        alerts_button = self._button("Verificacion de medicamentos", "btn_alerta")
        alerts_button.clicked.connect(self.show_alerts)
        layout.addWidget(alerts_button)
        self.main_layout.addWidget(group)

    def _login_button(self, label: str, role: str) -> QPushButton:
        """Crea un boton que inicia sesion con un rol especifico."""
        button = self._button(label, "btn_login")
        button.clicked.connect(lambda: self.login(role))
        return button

    @staticmethod
    def _button(label: str, object_name: str | None = None) -> QPushButton:
        """Crea un boton Qt y aplica su estilo visual opcional."""
        button = QPushButton(label)
        if object_name:
            button.setObjectName(object_name)
        button.setCursor(QCursor(Qt.PointingHandCursor))
        return button

    def login(self, required_role: str) -> bool:
        """Solicita credenciales, autentica al usuario y actualiza la sesion."""
        username, accepted = QInputDialog.getText(
            self, "Inicio de Sesion", f"Usuario para {required_role}:"
        )
        if not accepted:
            return False
        password, accepted = QInputDialog.getText(
            self,
            "Inicio de Sesion",
            f"Contrasena para {required_role}:",
            QLineEdit.Password,
        )
        if not accepted:
            return False
        try:
            self.current_session = self.auth_service.authenticate(
                username, password, required_role
            )
        except AuthenticationError as error:
            self.current_session = None
            self._refresh_session_status()
            self._show_error("Error al ingresar", str(error))
            return False
        self._refresh_session_status()
        self._show_info(
            "Bienvenido", f"Sesion iniciada como {required_role.capitalize()}."
        )
        return True

    def logout(self) -> None:
        """Finaliza la sesion actual y actualiza la interfaz."""
        self.current_session = None
        self._refresh_session_status()
        self._show_info("Sesion cerrada", "Ha cerrado sesion exitosamente.")

    def _refresh_session_status(self) -> None:
        """Actualiza el texto y el estado visual de la sesion."""
        if self.current_session:
            text = (
                f"Sesion: {self.current_session.role.capitalize()} "
                f"({self.current_session.username})"
            )
            state = "activa"
        else:
            text = "Sin sesion activa"
            state = "inactiva"
        self.session_label.setText(text)
        self.session_label.setProperty("estado", state)
        self.logout_button.setEnabled(self.current_session is not None)
        self.session_label.style().unpolish(self.session_label)
        self.session_label.style().polish(self.session_label)

    def save_medication(self) -> None:
        """Lee el formulario y registra un medicamento para bodega."""
        if not self._require_role(BODEGA_ROLE, "registrar medicamentos"):
            return
        try:
            medication = Medication(
                identifier=None,
                name=self.name_input.text().strip().title(),
                quantity=int(self.quantity_input.text().strip()),
                expiration_date=self._selected_date(),
                brand=self.brand_input.text().strip().title() or "Desconocido",
            )
            self.inventory_service.register(medication)
        except (ValueError, ValidationError, DatabaseError) as error:
            self._show_error("Datos invalidos", str(error))
            return
        self._show_info("Exito", "Medicamento registrado en bodega")
        self._clear_registration_form()
        self.refresh_inventory()

    def refresh_inventory(self) -> None:
        """Recarga la tabla con los medicamentos almacenados."""
        medications = self.inventory_service.list_medications()
        self.table.setRowCount(0)
        for row_index, medication in enumerate(medications):
            self.table.insertRow(row_index)
            values = (
                medication.identifier,
                medication.name,
                medication.quantity,
                medication.expiration_date.isoformat(),
                medication.brand,
            )
            for column_index, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_index, column_index, item)

    def deliver_medication(self) -> None:
        """Solicita unidades y procesa una entrega al usuario."""
        if not self._require_role(DELIVERY_ROLE, "entregar medicamentos"):
            return
        medication = self._selected_medication()
        if medication is None:
            return
        quantity, accepted = QInputDialog.getInt(
            self,
            "Entrega de Medicamento",
            f"Medicamento: {medication.name}\n"
            f"Stock disponible: {medication.quantity} unidades\n\n"
            "Cuantas unidades desea entregar?",
            minValue=1,
            maxValue=max(medication.quantity, 1),
            value=1,
        )
        if not accepted:
            return
        try:
            remaining = self.inventory_service.deliver(medication.identifier, quantity)
        except (InsufficientStockError, MedicationNotFoundError, DatabaseError) as error:
            self._show_error("Error de inventario", str(error))
            self.refresh_inventory()
            return
        self._show_info(
            "Entrega exitosa",
            f"Se entregaron {quantity} unidades de {medication.name}.\n"
            f"Quedan {remaining.quantity} unidades en inventario.",
        )
        self.refresh_inventory()

    def edit_medication(self) -> None:
        """Solicita nuevos datos y actualiza el medicamento seleccionado."""
        if not self._require_role(BODEGA_ROLE, "editar medicamentos"):
            return
        medication = self._selected_medication()
        if medication is None:
            return
        name, accepted = QInputDialog.getText(
            self, "Editar Medicamento", "Nombre:", text=medication.name
        )
        if not accepted or not name.strip():
            return
        quantity, accepted = QInputDialog.getInt(
            self,
            "Editar Medicamento",
            "Cantidad:",
            value=medication.quantity,
            minValue=0,
        )
        if not accepted:
            return
        expiration_text, accepted = QInputDialog.getText(
            self,
            "Editar Medicamento",
            "Fecha de vencimiento (YYYY-MM-DD):",
            text=medication.expiration_date.isoformat(),
        )
        if not accepted:
            return
        try:
            expiration_date = date.fromisoformat(expiration_text.strip())
        except ValueError:
            self._show_error("Fecha invalida", "Use el formato YYYY-MM-DD.")
            return
        brand, accepted = QInputDialog.getText(
            self, "Editar Medicamento", "Laboratorio:", text=medication.brand
        )
        if not accepted:
            return
        updated = Medication(
            medication.identifier,
            name.strip().title(),
            quantity,
            expiration_date,
            brand.strip().title() or "Desconocido",
        )
        try:
            self.inventory_service.update(updated)
        except (ValidationError, MedicationNotFoundError, DatabaseError) as error:
            self._show_error("No se pudo actualizar", str(error))
            return
        self._show_info("Exito", "Medicamento actualizado correctamente.")
        self.refresh_inventory()

    def delete_medication(self) -> None:
        """Confirma y elimina el medicamento seleccionado."""
        if not self._require_role(BODEGA_ROLE, "eliminar medicamentos"):
            return
        medication = self._selected_medication()
        if medication is None:
            return
        response = QMessageBox.question(
            self,
            "Confirmar Eliminacion",
            f"Esta seguro de eliminar '{medication.name}' del inventario?\n\n"
            "Esta accion no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if response != QMessageBox.Yes:
            return
        try:
            self.inventory_service.delete(medication.identifier)
        except (MedicationNotFoundError, DatabaseError) as error:
            self._show_error("No se pudo eliminar", str(error))
            return
        self._show_info("Eliminado", f"'{medication.name}' fue eliminado del inventario.")
        self.refresh_inventory()

    def show_alerts(self) -> None:
        """Muestra medicamentos con stock bajo o vencimiento cercano."""
        try:
            alerts = self.inventory_service.alerts()
        except DatabaseError as error:
            self._show_error("Error de base de datos", str(error))
            return
        if not alerts:
            self._show_info("Reporte", "No hay medicamentos por vencer o agotarse.")
            return
        message = "PRODUCTOS CON POCO STOCK O POR VENCER:\n\n"
        message += "\n".join(_format_alert(alert) for alert in alerts)
        QMessageBox.warning(self, "Alerta de Inventario", message)

    def _selected_medication(self) -> Medication | None:
        """Devuelve el medicamento seleccionado en la tabla."""
        selected_items = self.table.selectedItems()
        if not selected_items:
            self._show_error("Seleccion requerida", "Seleccione un medicamento de la lista.")
            return None
        try:
            medication_id = int(self.table.item(selected_items[0].row(), 0).text())
        except (AttributeError, ValueError):
            self._show_error("Error", "No se pudo identificar el medicamento seleccionado.")
            return None
        try:
            medication = self.inventory_service.find_medication(medication_id)
        except DatabaseError as error:
            self._show_error("Error de base de datos", str(error))
            return None
        if medication is None:
            self._show_error("Error", "El medicamento seleccionado ya no existe.")
            self.refresh_inventory()
        return medication

    def _require_role(self, role: str, action: str) -> bool:
        """Comprueba que la sesion actual tenga permiso para una accion."""
        if self.current_session and self.current_session.role == role:
            return True
        self._show_error("Acceso denegado", f"Debe iniciar sesion para {action}.")
        return False

    def _selected_date(self) -> date:
        """Convierte la fecha del formulario en un objeto `date`."""
        value = self.expiration_input.date().toString("yyyy-MM-dd")
        return date.fromisoformat(value)

    def _clear_registration_form(self) -> None:
        """Limpia los campos del formulario de registro."""
        self.name_input.clear()
        self.quantity_input.clear()
        self.brand_input.clear()
        self.expiration_input.setDate(QDate.currentDate())

    def _show_info(self, title: str, message: str) -> None:
        """Muestra un mensaje informativo al usuario."""
        QMessageBox.information(self, title, message)

    def _show_error(self, title: str, message: str) -> None:
        """Muestra un mensaje de error al usuario."""
        QMessageBox.critical(self, title, message)

    def closeEvent(self, event) -> None:
        """Cierra la base de datos antes de cerrar la ventana."""
        self.database.close()
        event.accept()


def _format_alert(alert: InventoryAlert) -> str:
    """Convierte una alerta en una linea legible para el dialogo."""
    return (
        f"{alert.name} | {alert.quantity} unidades | "
        f"Vence: {alert.expiration_date.isoformat()} | {alert.brand}"
    )


def run() -> None:
    """Crea la aplicacion Qt y ejecuta su ciclo de eventos."""
    application = QApplication(sys.argv)
    application.setFont(QFont("Segoe UI", 10))
    window = FarmaciaComunalApp()
    window.show()
    sys.exit(application.exec())
