import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QGridLayout, QLabel, QLineEdit, 
                               QPushButton, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QMessageBox, QInputDialog, QGroupBox, QAbstractItemView)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QCursor

# llama la base de datos creada en el otro documento
from database import FarmaciaDB
# llama los estilos creados en el otro documento
import styles

class FarmaciaComunalApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = FarmaciaDB()
        self.setWindowTitle("Sistema Farmacia Comunal")
        self.resize(1150, 700)
        
        # Aplicar QSS
        self.setStyleSheet(styles.get_stylesheet())

        # Credenciales trabajadores
        self.users = {
            "bodega": {
                "usuario": "juan", 
                "contraseña": "1234"
            },
            "entrega": {
                "usuario": "carlos", 
                "contraseña": "4567"
            }
        }
        
        # Widget principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.main_layout = QVBoxLayout(main_widget)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(25)

        self.create_widgets()
        self.actualizar_tabla()

    def login(self, tipo_acceso):
        # validador de usuario y contraseña usando QInputDialog
        user, ok1 = QInputDialog.getText(self, "Ingrese el Usuario", f"Usuario para {tipo_acceso}:")
        if not ok1:
            return False
            
        password, ok2 = QInputDialog.getText(self, "Ingrese la Contraseña", f"Contraseña para {tipo_acceso}:", QLineEdit.Password)
        if not ok2:
            return False
            
        credenciales = self.users.get(tipo_acceso)
        if user == credenciales["usuario"] and password == credenciales["contraseña"]:
            return True
        else:
            QMessageBox.critical(self, "Error al ingresar", "Usuario o contraseña incorrectos")
            return False

    def create_widgets(self):
        # SECCIÓN DE BODEGA
        grupo_ingreso = QGroupBox("Ingreso de medicamentos a la bodega")
        layout_ingreso = QGridLayout(grupo_ingreso)
        layout_ingreso.setContentsMargins(25, 35, 25, 25)
        layout_ingreso.setSpacing(15)

        layout_ingreso.addWidget(QLabel("Nombre:"), 0, 0)
        self.ent_nombre = QLineEdit()
        self.ent_nombre.setPlaceholderText("Ej. Paracetamol")
        layout_ingreso.addWidget(self.ent_nombre, 0, 1)

        layout_ingreso.addWidget(QLabel("Cantidad:"), 0, 2)
        self.ent_cantidad = QLineEdit()
        self.ent_cantidad.setPlaceholderText("0")
        layout_ingreso.addWidget(self.ent_cantidad, 0, 3)

        layout_ingreso.addWidget(QLabel("Vencimiento:"), 0, 4)
        self.ent_fecha = QLineEdit()
        self.ent_fecha.setPlaceholderText("YYYY-MM-DD")
        layout_ingreso.addWidget(self.ent_fecha, 0, 5)

        layout_ingreso.addWidget(QLabel("Laboratorio:"), 0, 6)
        self.ent_marca = QLineEdit()
        self.ent_marca.setPlaceholderText("Marca o Lab")
        layout_ingreso.addWidget(self.ent_marca, 0, 7)

        btn_guardar = QPushButton("Ingreso a Bodega")
        btn_guardar.setObjectName("btn_accion") # Para el estilo QSS
        btn_guardar.clicked.connect(self.guardar_datos)
        btn_guardar.setCursor(QCursor(Qt.PointingHandCursor))
        layout_ingreso.addWidget(btn_guardar, 0, 8)

        self.main_layout.addWidget(grupo_ingreso)

        # TABLA DE INVENTARIO
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Medicamento", "Unidades Disponibles", "Fecha de Vencimiento", "Laboratorio"])
        
        # Configuración de la tabla para aspecto SaaS
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents) # ID mas pequeño
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        
        self.main_layout.addWidget(self.table)

        # SECCIÓN DE ENTREGA
        grupo_entrega = QGroupBox("Gestión y Entrega al público")
        layout_entrega = QHBoxLayout(grupo_entrega)
        layout_entrega.setContentsMargins(25, 35, 25, 25)

        btn_entregar = QPushButton("Entrega de medicamentos")
        btn_entregar.clicked.connect(self.procesar_entrega)
        btn_entregar.setCursor(QCursor(Qt.PointingHandCursor))
        layout_entrega.addWidget(btn_entregar, alignment=Qt.AlignLeft)

        layout_entrega.addStretch() # Espaciador en el medio

        btn_alertas = QPushButton("Verificación de medicamentos")
        btn_alertas.setObjectName("btn_alerta") # Para el estilo QSS
        btn_alertas.clicked.connect(self.mostrar_alertas)
        btn_alertas.setCursor(QCursor(Qt.PointingHandCursor))
        layout_entrega.addWidget(btn_alertas, alignment=Qt.AlignRight)

        self.main_layout.addWidget(grupo_entrega)

    def guardar_datos(self):
        if not self.login("bodega"):
            return

        nombre = self.ent_nombre.text().strip()
        cantidad = self.ent_cantidad.text().strip()
        fecha = self.ent_fecha.text().strip()
        marca = self.ent_marca.text().strip()

        if nombre and cantidad:
            try:
                cant_int = int(cantidad)
                self.db.registrar_medicamento(nombre, cant_int, fecha, marca)
                QMessageBox.information(self, "Éxito", "Medicamento registrado en bodega")
                self.actualizar_tabla()
                # Limpiar campos
                self.ent_nombre.clear()
                self.ent_cantidad.clear()
                self.ent_fecha.clear()
                self.ent_marca.clear()
            except ValueError:
                QMessageBox.warning(self, "Error", "La cantidad debe ser un número entero.")
        else:
            QMessageBox.warning(self, "Campos incompletos", "Por favor llenar al menos nombre y cantidad.")

    def actualizar_tabla(self):
        self.table.setRowCount(0)
        datos = self.db.obtener_todo()
        
        for row_idx, fila in enumerate(datos):
            self.table.insertRow(row_idx)
            for col_idx, valor in enumerate(fila):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)

    def procesar_entrega(self):
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Error", "Por favor seleccione un medicamento de la lista")
            return
            
        row = selected_rows[0].row()
        item_id = int(self.table.item(row, 0).text())

        if not self.login("entrega"):
            return
            
        exito, nuevo_stock = self.db.entregar_medicamento(item_id, 1)
        
        if exito:
            QMessageBox.information(self, "Entrega", f"Medicamento entregado con éxito\nQuedan {nuevo_stock} unidades en inventario.")
            self.actualizar_tabla()
        else:
            QMessageBox.critical(self, "Error", "No hay unidades suficientes.")

    def mostrar_alertas(self):
        alertas = self.db.alertas_criticas()
        if not alertas:
            QMessageBox.information(self, "Reporte", "No hay medicamentos por vencer o agotarse.")
            return
        
        mensaje = "PRODUCTOS CON POCO STOCK O POR VENCER:\n\n"
        for a in alertas:
            mensaje += f"• Medicamento: {a[0]} | {a[1]} unidades | Vence: {a[2]}\n"
        QMessageBox.warning(self, "Alerta de Inventario", mensaje)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Opcional: configurar una fuente global más moderna si está disponible
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    ventana = FarmaciaComunalApp()
    ventana.show()
    sys.exit(app.exec())