from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QHeaderView,
    QGroupBox, QAbstractItemView, QDateEdit
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QCursor

class InterfazFarmacia(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema Farmacia Comunal")
        self.resize(1200, 750)

        # Configuración del contenedor principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.main_layout = QVBoxLayout(main_widget)
        self.main_layout.setContentsMargins(30, 20, 30, 30)
        self.main_layout.setSpacing(20)

        # Construcción de todas las partes de la interfaz
        self.crear_cabecera()
        self.crear_seccion_login()
        self.crear_formulario_ingreso()
        self.crear_tabla_inventario()
        self.crear_seccion_gestion()

    def crear_cabecera(self):
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        col_titulo = QVBoxLayout()
        lbl_titulo = QLabel("Farmacia Comunal")
        lbl_titulo.setObjectName("lbl_titulo")
        lbl_subtitulo = QLabel("Sistema de gestión de inventario y entrega de medicamentos")
        lbl_subtitulo.setObjectName("lbl_subtitulo")
        
        col_titulo.addWidget(lbl_titulo)
        col_titulo.addWidget(lbl_subtitulo)
        header_layout.addLayout(col_titulo)
        header_layout.addStretch()

        self.lbl_sesion = QLabel("Sin sesión activa")
        self.lbl_sesion.setObjectName("lbl_sesion")
        self.lbl_sesion.setProperty("estado", "inactiva")
        header_layout.addWidget(self.lbl_sesion)

        self.btn_logout = QPushButton("Cerrar Sesión")
        self.btn_logout.setObjectName("btn_logout")
        self.btn_logout.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_logout.setEnabled(False)
        header_layout.addWidget(self.btn_logout)

        self.main_layout.addWidget(header_widget)

    def crear_seccion_login(self):
        grupo_login = QGroupBox("Inicio de Sesión")
        layout_login = QHBoxLayout(grupo_login)
        layout_login.setContentsMargins(30, 10, 30, 20)

        self.btn_login_bodega = QPushButton("Ingreso: Almacenamiento Bodega")
        self.btn_login_bodega.setObjectName("btn_login")
        self.btn_login_bodega.setCursor(QCursor(Qt.PointingHandCursor))

        self.btn_nuevo_usuario = QPushButton("Crear Usuario")
        self.btn_nuevo_usuario.setObjectName("btn_secundario")
        self.btn_nuevo_usuario.setCursor(QCursor(Qt.PointingHandCursor))

        self.btn_login_entrega = QPushButton("Ingreso: Entrega Medicamentos")
        self.btn_login_entrega.setObjectName("btn_login")
        self.btn_login_entrega.setCursor(QCursor(Qt.PointingHandCursor))

        layout_login.addWidget(self.btn_login_bodega)
        layout_login.addStretch()
        layout_login.addWidget(self.btn_nuevo_usuario)
        layout_login.addStretch()
        layout_login.addWidget(self.btn_login_entrega)

        self.main_layout.addWidget(grupo_login)

    def crear_formulario_ingreso(self):
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
        self.ent_fecha = QDateEdit()
        self.ent_fecha.setCalendarPopup(True)
        self.ent_fecha.setDisplayFormat("yyyy-MM-dd")
        self.ent_fecha.setDate(QDate.currentDate())
        layout_ingreso.addWidget(self.ent_fecha, 0, 5)

        layout_ingreso.addWidget(QLabel("Laboratorio:"), 0, 6)
        self.ent_marca = QLineEdit()
        self.ent_marca.setPlaceholderText("Marca o Lab")
        layout_ingreso.addWidget(self.ent_marca, 0, 7)

        self.btn_guardar = QPushButton("Ingreso a Bodega")
        self.btn_guardar.setObjectName("btn_accion")
        self.btn_guardar.setCursor(QCursor(Qt.PointingHandCursor))
        layout_ingreso.addWidget(self.btn_guardar, 0, 8)

        self.main_layout.addWidget(grupo_ingreso)

    def crear_tabla_inventario(self):
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Medicamento", "Unidades Disponibles", "Fecha de Vencimiento", "Laboratorio"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)

        self.main_layout.addWidget(self.table)

    def crear_seccion_gestion(self):
        grupo_gestion = QGroupBox("Gestión de Inventario")
        layout_gestion = QHBoxLayout(grupo_gestion)
        layout_gestion.setContentsMargins(25, 35, 25, 25)

        self.btn_entregar = QPushButton(" Entrega de medicamentos")
        self.btn_entregar.setCursor(QCursor(Qt.PointingHandCursor))
        layout_gestion.addWidget(self.btn_entregar)

        self.btn_editar = QPushButton("Editar medicamento")
        self.btn_editar.setObjectName("btn_secundario")
        self.btn_editar.setCursor(QCursor(Qt.PointingHandCursor))
        layout_gestion.addWidget(self.btn_editar)

        self.btn_eliminar = QPushButton("Eliminar medicamento")
        self.btn_eliminar.setObjectName("btn_peligro")
        self.btn_eliminar.setCursor(QCursor(Qt.PointingHandCursor))
        layout_gestion.addWidget(self.btn_eliminar)

        self.btn_excel = QPushButton("Exportar Excel")
        self.btn_excel.setObjectName("btn_accion")
        self.btn_excel.setCursor(QCursor(Qt.PointingHandCursor))
        layout_gestion.addWidget(self.btn_excel)

        layout_gestion.addStretch()

        self.btn_alertas = QPushButton("Verificación de medicamentos")
        self.btn_alertas.setObjectName("btn_alerta")
        self.btn_alertas.setCursor(QCursor(Qt.PointingHandCursor))
        layout_gestion.addWidget(self.btn_alertas)

        self.main_layout.addWidget(grupo_gestion)