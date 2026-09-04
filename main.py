# controlar la salida de la aplicación (sys.exit).
import sys
# Se usa para validar que las fechas tengan formato YYYY-MM-DD.
from datetime import datetime
# Importa los widgets de PySide6.QtWidgets necesarios para la interfaz:
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QGridLayout, QLabel, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QInputDialog, QGroupBox, 
    QAbstractItemView, QFrame, QDateEdit
    )

from PySide6.QtCore import Qt, QDate

# QFont: permite configurar la fuente tipográfica de la aplicación.
# QCursor: permite cambiar el cursor del mouse (mano al pasar sobre botones).
from PySide6.QtGui import QFont, QCursor

# Esta clase maneja toda la lógica de acceso a la base de datos SQLite.
from database import FarmaciaDB

# Importa el módulo styles (archivo styles.py).
import styles
# =============================================================================
# FarmaciaComunalApp: Ventana principal de la aplicación. Hereda de QMainWindow.
#              Contiene toda la interfaz gráfica y la lógica de eventos.

class FarmaciaComunalApp(QMainWindow):
# =============================================================================

    # __init__ (Constructor): Se ejecuta automáticamente al crear la ventana principal.
    # Configura la ventana, conecta la base de datos, aplica
    #estilos y crea todos los widgets de la interfaz.
    def __init__(self):
        # Llama al constructor de la clase padre (QMainWindow).
        # Esto inicializa la ventana base de Qt.
        super().__init__()

        # Crea una instancia de FarmaciaDB (abre la conexión a SQLite).
        # Esta instancia se usa en toda la aplicación para operar con la BD.
        self.db = FarmaciaDB()

        # título de la ventana principal.
        self.setWindowTitle("Sistema Farmacia Comunal")

        # Define el tamaño inicial de la ventana
        self.resize(1200, 750)

        # Aplica la hoja de estilos QSS a toda la aplicación
        self.setStyleSheet(styles.get_stylesheet())

        # Variable de estado global para el rol actual de la sesión.
        # Puede ser "bodega", "entrega" o None (sin sesión) (none es ninguno)
        self.current_role = None

        # Variable que guarda el nombre de usuario que inició sesión.
        # Ejemplo: "juan" o "carlos".
        self.current_user = None

        # Crea el widget principal que contendrá toda la interfaz.
        main_widget = QWidget()

        # Establece main_widget como el widget central de la ventana principal.
        # QMainWindow requiere un widget central obligatoriamente.
        self.setCentralWidget(main_widget)

        # Crea un layout vertical para el widget principal.
        # QVBoxLayout apila los elementos de arriba hacia abajo.
        self.main_layout = QVBoxLayout(main_widget)

        # Define los márgenes internos del layout: (izq, arriba, der, abajo).
        self.main_layout.setContentsMargins(30, 20, 30, 30)

        # Define el espaciado entre los widgets del layout 
        self.main_layout.setSpacing(20)

        # Llama al método create_header que crea la cabecera de la app
        # (título, indicador de sesión y botón de cerrar sesión).
        self.create_header()

        # Llama al método create_widgets que crea todas las secciones
        # de la interfaz (login, ingreso, tabla, gestión).
        self.create_widgets()

        # Llama al método actualizar_tabla para cargar los datos
        # del inventario desde la base de datos a la tabla visual.
        self.actualizar_tabla()

        # Llama al método actualizar_estado_sesion para mostrar
        # el estado inicial de la sesión (sin sesión activa).
        self.actualizar_estado_sesion()

    # =========================================================================

    # create_header: Crea la cabecera de la aplicación con:
    # Título y subtítulo a la izquierda.
    # Indicador de sesión activa.
    # Botón de cerrar sesión.
  
    def create_header(self):
        # Crea un widget contenedor para la cabecera.
        header_widget = QWidget()

        # Crea un layout horizontal para la cabecera.
        # Los elementos se colocarán de izquierda a derecha.
        header_layout = QHBoxLayout(header_widget)

        # Sin márgenes internos en la cabecera.
        header_layout.setContentsMargins(0, 0, 0, 0)

        # Espaciado entre los elementos de la cabecera.
        header_layout.setSpacing(15)

        # Crea un layout vertical para la columna del título.
        # El título y subtítulo se apilan verticalmente.
        col_titulo = QVBoxLayout()

        # Espaciado el título y el subtítulo.
        col_titulo.setSpacing(2)

        # Crea la etiqueta del título principal de la aplicación.
        lbl_titulo = QLabel("Farmacia Comunal")

        # Asigna el objectName "lbl_titulo" para que el estilo QSS
        # QLabel#lbl_titulo aplique el formato grande y en negrita.
        lbl_titulo.setObjectName("lbl_titulo")

        # Agrega el título al layout vertical de la columna.
        col_titulo.addWidget(lbl_titulo)

        # Crea la etiqueta del subtítulo descriptivo.
        lbl_subtitulo = QLabel("Sistema de gestión de inventario y entrega de medicamentos")

        # Asigna el objectName "lbl_subtitulo" para el estilo QSS
        # QLabel#lbl_subtitulo (texto más pequeño y gris).
        lbl_subtitulo.setObjectName("lbl_subtitulo")

        # Agrega el subtítulo al layout vertical de la columna.
        col_titulo.addWidget(lbl_subtitulo)

        # Agrega la columna del título al layout horizontal de la cabecera.
        header_layout.addLayout(col_titulo)

        # Agrega un espaciador flexible que empuja los elementos
        # siguientes hacia la derecha de la cabecera.
        header_layout.addStretch()

        # Crea la etiqueta que muestra el estado de la sesión.
        # Inicialmente muestra "Sin sesión activa".
        self.lbl_sesion = QLabel("Sin sesión activa")

        # Asigna el objectName "lbl_sesion" para el estilo QSS
        self.lbl_sesion.setObjectName("lbl_sesion")

        # Establece la propiedad "estado" a "inactiva".
        # El estilo QSS usa esta propiedad para cambiar colores:
        # "activa": verde (sesión iniciada).
        # "inactiva": gris (sin sesión).
        self.lbl_sesion.setProperty("estado", "inactiva")

        # Agrega el indicador de sesión al layout horizontal.
        header_layout.addWidget(self.lbl_sesion)

        # Crea el botón de cerrar sesión.
        self.btn_logout = QPushButton("Cerrar Sesión")

        # Asigna el objectName "btn_logout" para el estilo QSS
        self.btn_logout.setObjectName("btn_logout")

        # Cambia el cursor a una mano cuando el mouse pasa sobre el botón.
        # Qt.PointingHandCursor es el cursor de "mano señalando".
        self.btn_logout.setCursor(QCursor(Qt.PointingHandCursor))

        # Cuando el usuario haga clic, se ejecutará self.logout().
        self.btn_logout.clicked.connect(self.logout)

        # Deshabilita el botón inicialmente (no hay sesión que cerrar).
        # setEnabled(False) hace que el botón se vea gris y no responda.
        self.btn_logout.setEnabled(False)

        # Agrega el botón de logout al layout horizontal.
        header_layout.addWidget(self.btn_logout)

        # Agrega el widget de la cabecera al layout principal de la ventana.
        self.main_layout.addWidget(header_widget)

    # =========================================================================

    def login(self, tipo_acceso):
        # Paso 1: Pedir el nombre de usuario al usuario.
        # QInputDialog.getText muestra un diálogo con un campo de texto.
        # Retorna una tupla (texto_ingresado, ok):
        # texto_ingresado: lo que escribió el usuario.
        # ok: True si presionó OK, False si canceló.
        user, ok1 = QInputDialog.getText(self, "Inicio de Sesión", f"Usuario para {tipo_acceso}:")

        # Si el usuario canceló 
        # se aborta el login retornando False.
        if not ok1 or not user.strip():
            return False

        # Pedir la contraseña.
        # QLineEdit.Password hace que los caracteres se muestren como puntos (•••).
        password, ok2 = QInputDialog.getText(self, "Inicio de Sesión", f"Contraseña para {tipo_acceso}:", QLineEdit.Password)

        # Si el usuario canceló o dejó la contraseña vacía, se aborta.
        if not ok2 or not password:
            return False

        # Validar credenciales contra la base de datos.
        # self.db.validar_credenciales retorna el rol si las credenciales
        # son correctas, o None si son incorrectas.
        # .strip() elimina espacios en blanco al inicio y final del usuario.
        rol = self.db.validar_credenciales(user.strip(), password)

        # Verifica que el rol obtenido coincida con el rol solicitado.
        if rol == tipo_acceso:
            # Guarda el rol actual en la variable de estado.
            self.current_role = tipo_acceso

            # Guarda el nombre de usuario actual.
            self.current_user = user.strip()

            # Actualiza el indicador visual de sesión 
            self.actualizar_estado_sesion()

            # Muestra un mensaje de bienvenida.
            # .capitalize() convierte "bodega" en "Bodega".
            QMessageBox.information(self, "Bienvenido", f"Sesión iniciada como {tipo_acceso.capitalize()}.")

            # Retorna True indicando login exitoso.
            return True
        else:
            # Si las credenciales son incorrectas, muestra un error.
            QMessageBox.critical(self, "Error al ingresar", f"Usuario o contraseña incorrectos para {tipo_acceso}.")

            # Limpia el estado de sesión por seguridad.
            self.current_role = None
            self.current_user = None

            # Actualiza el indicador visual de sesión.
            self.actualizar_estado_sesion()

            # Retorna False indicando login fallido.
            return False

    # ========================================================================
    # logout: Cierra la sesión actual y resetea el estado de acceso.
    #              Se ejecuta al hacer clic en el botón "Cerrar Sesión".
    
    def logout(self):
        # Limpia el rol actual (ninguna sesión activa).
        self.current_role = None

        # Limpia el nombre de usuario actual.
        self.current_user = None

        # Actualiza el indicador visual de sesión.
        self.actualizar_estado_sesion()

        # Muestra un mensaje informativo de sesión cerrada.
        QMessageBox.information(self, "Sesión Cerrada", "Ha cerrado sesión exitosamente.")

    # ========================================================================
    #  actualizar_estado_sesion: Actualiza el indicador visual de sesión y el estado
    #  del botón de cerrar sesión según la sesión actual.
   
    def actualizar_estado_sesion(self):
        # Si hay una sesión activa (current_role no es None)...
        if self.current_role:
            # Actualiza el texto del label mostrando el rol y usuario.
            # Ejemplo: "Sesión: Bodega (juan)".
            self.lbl_sesion.setText(f"Sesión: {self.current_role.capitalize()} ({self.current_user})")

            # Cambia la propiedad "estado" a "activa".
            # El estilo QSS la mostrará en verde.
            self.lbl_sesion.setProperty("estado", "activa")

            # Habilita el botón de cerrar sesión.
            self.btn_logout.setEnabled(True)
        else:
            # Si NO hay sesión activa...
            # Muestra el texto de "sin sesión".
            self.lbl_sesion.setText("Sin sesión activa")

            # Cambia la propiedad "estado" a "inactiva".
            # El estilo QSS la mostrará en gris.
            self.lbl_sesion.setProperty("estado", "inactiva")

            # Deshabilita el botón de cerrar sesión.
            self.btn_logout.setEnabled(False)

        self.lbl_sesion.style().unpolish(self.lbl_sesion)
        self.lbl_sesion.style().polish(self.lbl_sesion)

    # =========================================================================

    #create_widgets: Crea todas las secciones de la interfaz:
    #  Sección de login (botones de acceso por rol).
    #  Sección de ingreso de medicamentos (formulario).
    #  Tabla de inventario.
    #  Sección de gestión (entregar, editar, eliminar, alertas).

    def create_widgets(self):

        # Crea una caja de grupo con título "Inicio de Sesión".
        # QGroupBox agrupa visualmente los widgets con un título flotante.
        grupo_login = QGroupBox("Inicio de Sesión")

        # Crea un layout horizontal dentro de la caja de grupo.
        layout_login = QHBoxLayout(grupo_login)

        # Márgenes internos
        layout_login.setContentsMargins(30, 10, 30, 20)

        # Espaciado  entre los elementos del layout.
        layout_login.setSpacing(20)

        # Crea el botón de login para el rol "bodega".
        btn_login_bodega = QPushButton("Ingreso: Almacenamiento Bodega")

        # Asigna el objectName "btn_login" para el estilo QSS
        btn_login_bodega.setObjectName("btn_login")

        # Conecta el clic del botón al método login con el argumento "bodega".
        # Se usa lambda para pasar el argumento sin ejecutarlo inmediatamente.
        btn_login_bodega.clicked.connect(lambda: self.login("bodega"))

        # Cambia el cursor a mano al pasar sobre el botón.
        btn_login_bodega.setCursor(QCursor(Qt.PointingHandCursor))

        # Crea el botón de login para el rol "entrega".
        btn_login_entrega = QPushButton("Ingreso: Entrega Medicamentos")

        # Asigna el objectName "btn_login" para el mismo estilo QSS.
        btn_login_entrega.setObjectName("btn_login")

        # Conecta el clic al método login con el argumento "entrega".
        btn_login_entrega.clicked.connect(lambda: self.login("entrega"))

        # Cambia el cursor a mano al pasar sobre el botón.
        btn_login_entrega.setCursor(QCursor(Qt.PointingHandCursor))

        # Agrega el botón de bodega al layout (izquierda).
        layout_login.addWidget(btn_login_bodega)

        # Agrega un espaciador flexible en el medio.
        # Esto separa los dos botones y los empuja a los extremos.
        layout_login.addStretch()

        # Agrega el botón de entrega al layout (derecha).
        layout_login.addWidget(btn_login_entrega)

        # Agrega la caja de login al layout principal de la ventana.
        self.main_layout.addWidget(grupo_login)

        # =====================================================================
        #  Ingreso de medicamentos (Formulario de bodega)
       
        # Crea una caja de grupo para el formulario de ingreso.
        grupo_ingreso = QGroupBox("Ingreso de medicamentos a la bodega")

        # Crea un layout de cuadrícula (filas y columnas) para el formulario.
        layout_ingreso = QGridLayout(grupo_ingreso)

        # Márgenes internos:
        layout_ingreso.setContentsMargins(25, 35, 25, 25)

        # Espaciado de 15px entre los elementos de la cuadrícula.
        layout_ingreso.setSpacing(15)

        # Agrega la etiqueta "Nombre:" en la fila 0, columna 0.
        layout_ingreso.addWidget(QLabel("Nombre:"), 0, 0)

        # Crea el campo de texto para el nombre del medicamento.
        self.ent_nombre = QLineEdit()

        # Establece un texto de ejemplo (placeholder) en el campo.
        self.ent_nombre.setPlaceholderText("Ej. Paracetamol")

        # Agrega el campo de nombre en la fila 0, columna 1.
        layout_ingreso.addWidget(self.ent_nombre, 0, 1)

        # Agrega la etiqueta "Cantidad:" en la fila 0, columna 2.
        layout_ingreso.addWidget(QLabel("Cantidad:"), 0, 2)

        # Crea el campo de texto para la cantidad de unidades.
        self.ent_cantidad = QLineEdit()

        # Placeholder "0" como ejemplo de cantidad.
        self.ent_cantidad.setPlaceholderText("0")

        # Agrega el campo de cantidad en la fila 0, columna 3.
        layout_ingreso.addWidget(self.ent_cantidad, 0, 3)

        # Agrega la etiqueta "Vencimiento:" en la fila 0, columna 4.
        layout_ingreso.addWidget(QLabel("Vencimiento:"), 0, 4)

        # Crea el campo para seleccionar la fecha de vencimiento.
        self.ent_fecha = QDateEdit()

        # Define el formato de la fecha.
        self.ent_fecha.setDisplayFormat("yyyy-MM-dd")

        # Permite seleccionar la fecha mediante un calendario.
        self.ent_fecha.setCalendarPopup(True)

        # Define la fecha actual como fecha inicial.
        self.ent_fecha.setDate(QDate.currentDate())

        # Agrega el campo de fecha en la fila 0, columna 5.
        layout_ingreso.addWidget(self.ent_fecha, 0, 5)

        # Agrega la etiqueta "Laboratorio:" en la fila 0, columna 6.
        layout_ingreso.addWidget(QLabel("Laboratorio:"), 0, 6)

        # Crea el campo de texto para la marca o laboratorio.
        self.ent_marca = QLineEdit()

        # Placeholder "Marca o Lab" como ejemplo.
        self.ent_marca.setPlaceholderText("Marca o Lab")

        # Agrega el campo de laboratorio en la fila 0, columna 7.
        layout_ingreso.addWidget(self.ent_marca, 0, 7)

        # Crea el botón para guardar el medicamento en bodega.
        btn_guardar = QPushButton("Ingreso a Bodega")

        # Asigna el objectName "btn_accion" para el estilo QSS
        btn_guardar.setObjectName("btn_accion")

        # Conecta el clic del botón al método guardar_datos.
        btn_guardar.clicked.connect(self.guardar_datos)

        # Cambia el cursor a mano al pasar sobre el botón.
        btn_guardar.setCursor(QCursor(Qt.PointingHandCursor))

        # Agrega el botón de guardar en la fila 0, columna 8.
        layout_ingreso.addWidget(btn_guardar, 0, 8)

        # Agrega la caja de ingreso al layout principal.
        self.main_layout.addWidget(grupo_ingreso)

        # =====================================================================
        # TABLA DE INVENTARIO
       

        # Crea la tabla de inventario (QTableWidget).
        self.table = QTableWidget()

        # Define el número de columnas de la tabla (5 columnas).
        self.table.setColumnCount(5)

        # Define los encabezados de las columnas.
        self.table.setHorizontalHeaderLabels(["ID", "Medicamento", "Unidades Disponibles", "Fecha de Vencimiento", "Laboratorio"])

        # Configuración de la tabla para aspecto SaaS (moderno):

        # Hace que todas las columnas se estiren para llenar el ancho disponible.
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # La columna 0 (ID) se ajusta al contenido (más pequeña).
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)

        # Deshabilita la edición de celdas por el usuario.
        # NoEditTriggers: el usuario no puede modificar los datos de la tabla.
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Define que la selección sea por filas completas.
        # SelectRows: al hacer clic se selecciona toda la fila.
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Define que solo se pueda seleccionar una fila a la vez.
        # SingleSelection: no permite selección múltiple.
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)

        # Oculta el encabezado vertical (los números de fila a la izquierda).
        self.table.verticalHeader().setVisible(False)

        # Desactiva las líneas de la cuadrícula (aspecto más limpio).
        self.table.setShowGrid(False)

        # Activa los colores alternos en las filas (zebra striping).
        # Las filas pares e impares tendrán colores ligeramente diferentes.
        self.table.setAlternatingRowColors(True)

        # Agrega la tabla al layout principal de la ventana.
        self.main_layout.addWidget(self.table)

        # =====================================================================
        # GESTIÓN DE INVENTARIO

        # Crea una caja de grupo para las acciones de gestión.
        grupo_gestion = QGroupBox("Gestión de Inventario")

        # Crea un layout horizontal para los botones de gestión.
        layout_gestion = QHBoxLayout(grupo_gestion)

        # Márgenes internos: 
        layout_gestion.setContentsMargins(25, 35, 25, 25)

        # Espaciado entre los botones.
        layout_gestion.setSpacing(15)

        # Crea el botón de entrega de medicamentos.
        btn_entregar = QPushButton(" Entrega de medicamentos")

        # Conecta el clic al método procesar_entrega.
        btn_entregar.clicked.connect(self.procesar_entrega)

        # Cambia el cursor a mano al pasar sobre el botón.
        btn_entregar.setCursor(QCursor(Qt.PointingHandCursor))

        # Agrega el botón de entrega al layout.
        layout_gestion.addWidget(btn_entregar)

        # Crea el botón de edición de medicamentos.
        btn_editar = QPushButton("Editar medicamento")

        # Asigna el objectName "btn_secundario" para el estilo QSS
        # QPushButton#btn_secundario (borde gris, estilo outline).
        btn_editar.setObjectName("btn_secundario")

        # Conecta el clic al método editar_medicamento.
        btn_editar.clicked.connect(self.editar_medicamento)

        # Cambia el cursor a mano al pasar sobre el botón.
        btn_editar.setCursor(QCursor(Qt.PointingHandCursor))

        # Agrega el botón de editar al layout.
        layout_gestion.addWidget(btn_editar)

        # Crea el botón de eliminación de medicamentos.
        btn_eliminar = QPushButton("Eliminar medicamento")

        # Asigna el objectName "btn_peligro" para el estilo QSS
        # QPushButton#btn_peligro (borde rojo, estilo outline).
        btn_eliminar.setObjectName("btn_peligro")

        # Conecta el clic al método eliminar_medicamento.
        btn_eliminar.clicked.connect(self.eliminar_medicamento)

        # Cambia el cursor a mano al pasar sobre el botón.
        btn_eliminar.setCursor(QCursor(Qt.PointingHandCursor))

        # Agrega el botón de eliminar al layout.
        layout_gestion.addWidget(btn_eliminar)

        # Agrega un espaciador flexible.
        # Esto empuja el botón de alertas hacia la derecha.
        layout_gestion.addStretch()

        # Crea el botón de verificación de medicamentos.
        btn_alertas = QPushButton("Verificación de medicamentos")

        # Asigna el objectName "btn_alerta" para el estilo QSS
        # QPushButton#btn_alerta (fondo rojo).
        btn_alertas.setObjectName("btn_alerta")

        # Conecta el clic al método mostrar_alertas.
        btn_alertas.clicked.connect(self.mostrar_alertas)

        # Cambia el cursor a mano al pasar sobre el botón.
        btn_alertas.setCursor(QCursor(Qt.PointingHandCursor))

        # Agrega el botón de alertas al layout (derecha).
        layout_gestion.addWidget(btn_alertas)

        # Agrega la caja de gestión al layout principal.
        self.main_layout.addWidget(grupo_gestion)

    # =========================================================================

    # validar_fecha: Valida que una cadena de texto tenga formato de fecha
    # válido: YYYY-MM-DD (ejemplo: 2026-12-31).
   
    def validar_fecha(self, fecha_str):
        # Bloque try/except para capturar el error de formato.
        try:
            # Intenta convertir la cadena a un objeto datetime.
            # strptime = "string parse time" (analizar tiempo desde string).
            # "%Y-%m-%d" es el formato: año-4 dígitos, mes-2, día-2.
            # Si el formato no coincide, lanza ValueError.
            datetime.strptime(fecha_str, "%Y-%m-%d")

            # Si llegó aquí, la fecha es válida. Retorna True.
            return True
        except ValueError:
            # Si hubo un error de formato, la fecha es inválida.
            # Retorna False.
            return False

    # =========================================================================
    # SECCIÓN: ACCIONES (Lógica de negocio de la interfaz)
    
    # guardar_datos: Guarda un medicamento en la base de datos.
    # Solo el rol "bodega" puede ejecutar esta acción.
    # Valida que los campos estén completos y correctos.
  
    def guardar_datos(self):
        # CONTROL DE ACCESO: Verifica que el rol actual sea "bodega".
        # Si no lo es, muestra una advertencia y aborta la operación.
        if self.current_role != "bodega":
            # Muestra un mensaje de advertencia.
            QMessageBox.warning(self, "Acceso Denegado",
                                "Para realizar este ingreso, debe iniciar sesión en bodega.")
            # Sale del método sin hacer nada más.
            return

        # Obtiene el texto de cada campo del formulario.
        # .strip() elimina espacios en blanco al inicio y final.
        # .title() convierte la primera letra de cada palabra a mayúscula para evitar medicamentos duplicados.
        nombre = self.ent_nombre.text().strip().title()
        cantidad = self.ent_cantidad.text().strip()
        fecha = self.ent_fecha.date().toString("yyyy-MM-dd")
        marca = self.ent_marca.text().strip().title()

        # Verifica que nombre y cantidad no estén vacíos.
        # Si falta alguno, muestra advertencia y aborta.
        if not nombre or not cantidad:
            QMessageBox.warning(self, "Campos incompletos", "Por favor llenar al menos nombre y cantidad.")
            return
#=============================================================================
        # VALIDACIÓN DE CANTIDAD:
        # Bloque try/except para convertir la cantidad a entero.
        try:
            # Intenta convertir el texto de cantidad a número entero.
            cant_int = int(cantidad)

            # Verifica que la cantidad sea positiva (mayor que 0).
            if cant_int <= 0:
                # Si es 0 o negativa, muestra error y aborta.
                QMessageBox.warning(self, "Error", "La cantidad debe ser un número positivo.")
                return
        except ValueError:
            # Si la conversión falló (no es un número), muestra error.
            QMessageBox.warning(self, "Error", "La cantidad debe ser un número entero.")
            return
#=============================================================================
        # VALIDACIÓN DE FECHA:
        # Si el usuario proporcionó una fecha, verifica su formato.
        # La condición "if fecha" es True solo si el campo no está vacío.
        if fecha and not self.validar_fecha(fecha):
            # Si la fecha no tiene formato válido, muestra error y aborta.
            QMessageBox.warning(self, "Error de Fecha",
                                "La fecha debe tener formato YYYY-MM-DD.\nEjemplo: 2026-12-31")
            return

        # Si NO se proporcionó fecha, se usa una fecha lejana por defecto.
        # "2099-12-31" es una fecha muy futura que nunca generará alertas.
        if not fecha:
            fecha = "2099-12-31"

        # Llamada a la base de datos:
        # Registra el medicamento en la BD.
        # Si el medicamento ya existe por nombre, suma la cantidad al stock.
        self.db.registrar_medicamento(nombre, cant_int, fecha, marca)

        # Muestra un mensaje de éxito.
        QMessageBox.information(self, "Éxito", "Medicamento registrado en bodega")

        # Recarga la tabla para mostrar los datos actualizados.
        self.actualizar_tabla()

        # LIMPIAR CAMPOS:
        # Vacía todos los campos del formulario para el siguiente ingreso.
        self.ent_nombre.clear()
        self.ent_cantidad.clear()
        self.ent_fecha.clear()
        self.ent_marca.clear()

    # ========================================================================
  
    # actualizar_tabla: Recarga la tabla de inventario con los datos actuales
    # de la base de datos.
    
    def actualizar_tabla(self):
        # Elimina todas las filas actuales de la tabla.
        # setRowCount(0) deja la tabla vacía.
        self.table.setRowCount(0)

        # Obtiene todos los medicamentos de la base de datos.
        # obtener_todo() retorna una lista de tuplas:
        # (id, nombre, cantidad, fecha_vencimiento, marca).
        datos = self.db.obtener_todo()

        # Itera sobre cada fila de datos.
        # enumerate() retorna (índice, elemento) para cada fila.
        for row_idx, fila in enumerate(datos):
            # Inserta una fila nueva en la tabla en la posición row_idx.
            self.table.insertRow(row_idx)

            # Itera sobre cada valor de la fila (cada columna).
            # enumerate() retorna (índice_columna, valor).
            for col_idx, valor in enumerate(fila):
                # Crea un item de tabla con el valor convertido a texto.
                item = QTableWidgetItem(str(valor))

                # Centra el texto de la celda horizontal y verticalmente.
                # Qt.AlignCenter combina AlignHCenter y AlignVCenter.
                item.setTextAlignment(Qt.AlignCenter)

                # Coloca el item en la tabla en (fila, columna).
                self.table.setItem(row_idx, col_idx, item)

# ========================================================================
    
    # obtener_fila_seleccionada: Obtiene el ID del medicamento seleccionado en la tabla.
    # Si no hay selección o el ID no es válido, muestra error.
    
    def obtener_fila_seleccionada(self):
        # Obtiene la lista de items seleccionados en la tabla.
        # selectedItems() retorna los QTableWidgetItem seleccionados.
        selected_items = self.table.selectedItems()

        # Si no hay items seleccionados (lista vacía)...
        if not selected_items:
            # Muestra una advertencia pidiendo seleccionar un medicamento.
            QMessageBox.warning(self, "Error", "Por favor seleccione un medicamento de la lista")
            # Retorna None indicando que no hay selección.
            return None

        # Obtiene el número de fila del primer item seleccionado.
        # .row() retorna el índice de fila (0, 1, 2, ...).
        row = selected_items[0].row()

        # Bloque try/except para manejar errores de conversión.
        try:
            # Obtiene el texto de la celda en la columna 0 (ID).
            # self.table.item(row, 0) obtiene el item de la fila y columna 0.
            # .text() obtiene el texto del item.
            # int() convierte el texto a número entero.
            item_id = int(self.table.item(row, 0).text())

            # Retorna el ID del medicamento.
            return item_id
        except (ValueError, AttributeError):
            # ValueError: si el texto no es un número válido.
            # AttributeError: si el item es None (celda vacía).
            # Muestra un error crítico.
            QMessageBox.critical(self, "Error", "No se pudo identificar el medicamento seleccionado.")
            # Retorna None indicando error.
            return None

    # ========================================================================
    # Dprocesar_entrega: Procesa la entrega de medicamentos al público.
    #  Solo el rol "entrega" puede ejecutar esta acción.
    #  Pide la cantidad a entregar y actualiza el stock.
    # ========================================================================

    def procesar_entrega(self):
        # CONTROL DE ACCESO: Verifica que el rol actual sea "entrega".
        if self.current_role != "entrega":
            # Muestra advertencia si no tiene permisos.
            QMessageBox.warning(self, "Acceso Denegado",
                                "Para realizar esta acción, debe iniciar sesión en entrega medicamentos.")
            # Aborta la operación.
            return

        # Obtiene el ID del medicamento seleccionado.
        # Si es None, el método ya mostró el error correspondiente.
        item_id = self.obtener_fila_seleccionada()
        if item_id is None:
            return

        # Obtiene los datos completos del medicamento desde la BD.
        # Esto es para mostrar información en el diálogo de entrega.
        medicamento = self.db.obtener_medicamento_por_id(item_id)

        # Si el medicamento ya no existe (fue eliminado)...
        if medicamento is None:
            # Muestra un error crítico.
            QMessageBox.critical(self, "Error", "El medicamento seleccionado ya no existe en el inventario.")
            # Recarga la tabla para quitar el registro fantasma.
            self.actualizar_tabla()
            # Aborta la operación.
            return

        # Extrae el nombre del medicamento (posición 1 de la tupla).
        # La tupla es: (id, nombre, cantidad, fecha, marca).
        nombre_med = medicamento[1]

        # Extrae el stock actual (posición 2 de la tupla).
        stock_actual = medicamento[2]

        # Pide al usuario la cantidad a entregar.
      
        cantidad, ok = QInputDialog.getInt(
            self, "Entrega de Medicamento",
            f"Medicamento: {nombre_med}\nStock disponible: {stock_actual} unidades\n\n¿Cuántas unidades desea entregar?",
            minValue=1, maxValue=max(stock_actual, 1), value=1
        )

        # Si el usuario canceló el diálogo, aborta la operación.
        if not ok:
            return

        # LLAMADA A LA BASE DE DATOS:
       
        exito, nuevo_stock = self.db.entregar_medicamento(item_id, cantidad)

        # Si la entrega fue exitosa...
        if exito:
            # Muestra un mensaje de éxito con los detalles.
            QMessageBox.information(self, "Entrega Exitosa",
                                    f"Se entregaron {cantidad} unidades de {nombre_med}.\nQuedan {nuevo_stock} unidades en inventario.")
            # Recarga la tabla para reflejar el nuevo stock.
            self.actualizar_tabla()
        else:
            # Si no hay stock suficiente, muestra un error.
            QMessageBox.critical(self, "Error de Inventario",
                                f"No hay unidades suficientes para realizar la entrega.\nStock actual: {stock_actual}")

    # =========================================================================
    # editar_medicamento: Edita los datos de un medicamento seleccionado.
    #              Solo el rol "bodega" puede ejecutar esta acción.
    #              Usa diálogos para pedir los nuevos valores.

    def editar_medicamento(self):
        # CONTROL DE ACCESO: Verifica que el rol actual sea "bodega".
        if self.current_role != "bodega":
            # Muestra advertencia si no tiene permisos.
            QMessageBox.warning(self, "Acceso Denegado",
                                "Para editar un medicamento, debe iniciar sesión en bodega.")
            # Aborta la operación.
            return

        # Obtiene el ID del medicamento seleccionado.
        item_id = self.obtener_fila_seleccionada()
        if item_id is None:
            return

        # Obtiene los datos actuales del medicamento desde la BD.
        medicamento = self.db.obtener_medicamento_por_id(item_id)

        # Si el medicamento ya no existe...
        if medicamento is None:
            # Muestra error y recarga la tabla.
            QMessageBox.critical(self, "Error", "El medicamento seleccionado ya no existe en el inventario.")
            self.actualizar_tabla()
            return

        # Nombre:
        # Muestra un diálogo con el nombre actual precargado (text=medicamento[1]).
        nombre, ok1 = QInputDialog.getText(self, "Editar Medicamento", "Nombre:", text=medicamento[1])

        # Si canceló o dejó vacío, aborta.
        if not ok1 or not nombre.strip():
            return

        # Cantidad:
        # Muestra un diálogo numérico con la cantidad actual precargada.
        # minValue=0 permite que la cantidad sea 0.
        cantidad, ok2 = QInputDialog.getInt(self, "Editar Medicamento", "Cantidad:",
                                            value=medicamento[2], minValue=0)

        # Si canceló, aborta.
        if not ok2:
            return

        # Fecha de vencimiento:
        # Muestra un diálogo con la fecha actual precargada.
        fecha, ok3 = QInputDialog.getText(self, "Editar Medicamento", "Fecha de vencimiento (YYYY-MM-DD):",
                                          text=medicamento[3])

        # Si canceló, aborta.
        if not ok3:
            return

        # Valida que la fecha tenga formato correcto.
        if not self.validar_fecha(fecha):
            # Si es inválida, muestra error y aborta.
            QMessageBox.warning(self, "Error de Fecha",
                                "La fecha debe tener formato YYYY-MM-DD.\nEjemplo: 2026-12-31")
            return

        # Laboratorio/Marca:
        # Muestra un diálogo con la marca actual precargada.
        marca, ok4 = QInputDialog.getText(self, "Editar Medicamento", "Laboratorio:", text=medicamento[4])

        # Si canceló, aborta.
        if not ok4:
            return

        # GUARDAR CAMBIOS:
        # Llama al método de la BD para actualizar el medicamento.
        # Retorna True si fue exitoso, False si hubo error.
        exito = self.db.editar_medicamento(item_id, nombre.strip(), cantidad, fecha, marca.strip())

        # Si la edición fue exitosa...
        if exito:
            # Muestra mensaje de éxito.
            QMessageBox.information(self, "Éxito", "Medicamento actualizado correctamente.")
            # Recarga la tabla con los datos actualizados.
            self.actualizar_tabla()
        else:
            # Si hubo error, muestra mensaje crítico.
            QMessageBox.critical(self, "Error", "No se pudo actualizar el medicamento.")

    # =========================================================================
    # eliminar_medicamento: Elimina un medicamento del inventario.
    # Solo el rol "bodega" puede ejecutar esta acción.
    # Pide confirmación antes de eliminar.
  
    def eliminar_medicamento(self):
        # CONTROL DE ACCESO: Verifica que el rol actual sea "bodega".
        if self.current_role != "bodega":
            # Muestra advertencia si no tiene permisos.
            QMessageBox.warning(self, "Acceso Denegado",
                                "Para eliminar un medicamento, debe iniciar sesión en bodega.")
            # Aborta la operación.
            return

        # Obtiene el ID del medicamento seleccionado.
        item_id = self.obtener_fila_seleccionada()
        if item_id is None:
            return

        # Obtiene los datos del medicamento para mostrar su nombre.
        medicamento = self.db.obtener_medicamento_por_id(item_id)

        # Si el medicamento ya no existe...
        if medicamento is None:
            # Muestra error y recarga la tabla.
            QMessageBox.critical(self, "Error", "El medicamento seleccionado ya no existe en el inventario.")
            self.actualizar_tabla()
            return

        # Extrae el nombre del medicamento para la confirmación.
        nombre_med = medicamento[1]

        # Muestra un diálogo de pregunta con botones Sí/No.
        # QMessageBox.question retorna el botón que el usuario presionó.
        # Parámetros:
        # Título: "Confirmar Eliminación".
        # Mensaje: pregunta si está seguro.
        # Botones: Yes | No (Sí o No).
        # Botón por defecto: No (más seguro).
        respuesta = QMessageBox.question(
            self, "Confirmar Eliminación",
            f"¿Está seguro de eliminar '{nombre_med}' del inventario?\n\nEsta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        # Si el usuario confirmó con "Sí"...
        if respuesta == QMessageBox.Yes:
            # Llama al método de la BD para eliminar el medicamento.
            exito = self.db.eliminar_medicamento(item_id)

            # Si la eliminación fue exitosa...
            if exito:
                # Muestra mensaje de éxito.
                QMessageBox.information(self, "Eliminado", f"'{nombre_med}' fue eliminado del inventario.")
                # Recarga la tabla sin el medicamento eliminado.
                self.actualizar_tabla()
            else:
                # Si hubo error, muestra mensaje crítico.
                QMessageBox.critical(self, "Error", "No se pudo eliminar el medicamento.")

    # =========================================================================
    # mostrar_alertas: Muestra las alertas de inventario (stock bajo o
    #              vencimiento próximo). Cualquier usuario puede verlas.
 
    def mostrar_alertas(self):
        # Bloque try/except para manejar errores de base de datos.
        try:
            # Obtiene las alertas críticas de la BD.
            # alertas_criticas() retorna medicamentos con stock <= 5
            # o que vencen en menos de 30 días.
            alertas = self.db.alertas_criticas()
        except Exception as e:
            # Si hay un error de BD, muestra mensaje crítico.
            QMessageBox.critical(self, "Error de Base de Datos", f"No se pudieron obtener las alertas críticas: {e}")
            # Aborta la operación.
            return

        # Si no hay alertas (lista vacía)...
        if not alertas:
            # Muestra un mensaje informativo de que todo está bien.
            QMessageBox.information(self, "Reporte", "No hay medicamentos por vencer o agotarse.")
            # Sale del método.
            return

        # Construye el mensaje de alertas.
        # El encabezado indica que hay productos con problemas.
        mensaje = "PRODUCTOS CON POCO STOCK O POR VENCER:\n\n"

        # Itera sobre cada alerta de la lista.
        for a in alertas:
            # Cada alerta es una tupla: (nombre, cantidad, fecha, marca).
            # a[0] = nombre del medicamento.
            # a[1] = unidades disponibles.
            # a[2] = fecha de vencimiento.
            # a[3] = laboratorio/marca.
            # Agrega una línea al mensaje con los datos de la alerta.
            mensaje += f"• {a[0]} | {a[1]} unidades | Vence: {a[2]} | {a[3]}\n"

        # Muestra el mensaje de alerta en un cuadro de advertencia.
        QMessageBox.warning(self, "Alerta de Inventario", mensaje)

    # =========================================================================
    # SECCIÓN: CIERRE DE APLICACIÓN
    # =========================================================================

    # -------------------------------------------------------------------------
  
    # closeEvent: Evento que se ejecuta automáticamente cuando el usuario
    # cierra la ventana principal. Se usa para liberar
    # recursos (cerrar la conexión a la base de datos).
    # 
    def closeEvent(self, event):
        # Cierra la conexión a la base de datos SQLite.
        # Esto libera el archivo farmacia.db y evita corrupción de datos.
        self.db.close()

        # Acepta el evento de cierre.
        # event.accept() permite que la ventana se cierre normalmente.
        # Si se usara event.ignore(), la ventana no se cerraría.
        event.accept()

# =============================================================================
# PUNTO DE ENTRADA DE LA APLICACIÓN


# Verifica si este archivo se está ejecutando directamente (no importado).
#( __name__ es "__main__" ) solo cuando se ejecuta: python main.py
if __name__ == "__main__":
    # Crea la aplicación Qt.
    # QApplication es obligatoria en toda aplicación PySide6.
    # sys.argv pasa los argumentos de línea de comandos a Qt.
    app = QApplication(sys.argv)

    # Configura una fuente global más moderna.
    # QFont("Segoe UI", 10)
    font = QFont("Segoe UI", 10)

    # Aplica la fuente a toda la aplicación.
    app.setFont(font)

    # Crea la ventana principal de la aplicación.
    ventana = FarmaciaComunalApp()

    # Muestra la ventana en pantalla.
    # Sin .show(), la ventana existe pero no es visible.
    ventana.show()

    # Inicia el bucle de eventos de la aplicación.
    # app.exec() mantiene la aplicación corriendo hasta que se cierre.
    # sys.exit() asegura que el programa termine con el código de salida correcto.
    sys.exit(app.exec())