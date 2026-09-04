# PALETA DE COLORES PRINCIPAL

# Color de fondo principal de toda la aplicación.
COLOR_FONDO = "#0B0F19"         
# Color secundario usado para tarjetas, cajas de grupo y campos de texto.
COLOR_SECUNDARIO = "#111827"     
# Color primario de la aplicación 
COLOR_PRIMARIO = "#6366F1"       
# Se usa para el botón de "Ingreso a Bodega" (acciones positivas/éxito).
COLOR_ACCION = "#10B981"      
# Se usa para botones de alerta, errores y advertencias.
COLOR_ALERTA = "#EF4444"     
# Color de texto principal.
COLOR_TEXTO = "#F9FAFB"         

# Color de texto secundario o inactivo.
COLOR_TEXTO_SECUNDARIO = "#9CA3AF" 
# bordes, se usa para bordes de cajas, tablas y separadores.
COLOR_BORDE = "#1F2937"          
#==========================================================================
# COLORES DE HOVER Y SELECCIÓN

# Se aplica cuando el mouse pasa sobre botones primarios.
COLOR_HOVER_PRIMARIO = "#818CF8" 
# Se aplica cuando el mouse pasa sobre botones de acción.
COLOR_HOVER_ACCION = "#34D399"   
# Se aplica cuando el mouse pasa sobre botones de alerta.
COLOR_HOVER_ALERTA = "#F87171" 
# Color de fondo para filas seleccionadas en la tabla 
COLOR_SELECCION_FONDO = "#312E81" 
# Color de las barras de scroll 
COLOR_SCROLLBAR = "#374151"      
#==========================================================================
# COLORES ADICIONALES PARA BADGES Y ESTADOS

# Verde oscuro para indicar que el inventario está bien.
COLOR_BADGE_OK = "#065F46"      
# Naranja oscuro para indicar que el stock está por agotarse.
COLOR_BADGE_WARN = "#92400E"     
# Rojo oscuro para indicar stock crítico o vencimiento próximo
COLOR_BADGE_CRIT = "#7F1D1D" 
# Verde muy claro que contrasta bien sobre los fondos oscuros de badges.
COLOR_BADGE_TEXTO = "#D1FAE5"   
# Color de fondo para el encabezado de la tabla 
COLOR_HEADER_GRADIENTE = "#1E293B" # Slate 800


# =============================================================================
# get_stylesheet: Retorna la hoja de estilos QSS completa como un string.
#Se usa f-string para insertar los valores de los colores
#definidos arriba dentro del texto QSS.
#Las llaves dobles {{ }} son necesarias porque en un f-string
#las llaves simples se interpretan como expresiones Python.

def get_stylesheet():
    return f"""
 

   
    QWidget {{
        background-color: {COLOR_FONDO};
        color: {COLOR_TEXTO};
        font-family: 'Segoe UI', 'Inter', sans-serif;
        font-size: 11pt;
    }}

    QMainWindow {{
        background-color: {COLOR_FONDO};
    }}

    QLabel {{
        color: {COLOR_TEXTO};
        font-weight: 500;
        background: transparent;
    }}

    QLabel#lbl_titulo {{
        font-size: 20pt;
        font-weight: bold;
        color: {COLOR_TEXTO};
        padding: 5px 0px;
    }}

    QLabel#lbl_subtitulo {{
        font-size: 10pt;
        color: {COLOR_TEXTO_SECUNDARIO};
        font-weight: normal;
    }}

    QLabel#lbl_sesion {{
        background-color: {COLOR_SECUNDARIO};
        border: 1px solid {COLOR_BORDE};
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: bold;
        font-size: 10pt;
    }}

    QLabel#lbl_sesion[estado="activa"] {{
        color: {COLOR_ACCION};
        border-color: {COLOR_ACCION};
    }}

    QLabel#lbl_sesion[estado="inactiva"] {{
        color: {COLOR_TEXTO_SECUNDARIO};
        border-color: {COLOR_BORDE};
    }}

    QGroupBox {{
        background-color: {COLOR_SECUNDARIO};
        border: 1px solid {COLOR_BORDE};
        border-radius: 10px;
        margin-top: 28px;
        font-weight: bold;
        font-size: 12pt;
        color: {COLOR_TEXTO};
        padding-top: 10px;
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 12px;
        left: 20px;
        top: 4px;
        color: {COLOR_PRIMARIO};
        font-size: 11pt;
        letter-spacing: 0.5px;
    }}

    QLineEdit {{
        background-color: {COLOR_FONDO};
        border: 1px solid {COLOR_BORDE};
        border-radius: 6px;
        padding: 8px 12px;
        selection-background-color: {COLOR_PRIMARIO};
        color: {COLOR_TEXTO};
        min-height: 20px;
    }}

    QLineEdit:focus {{
        border: 1px solid {COLOR_PRIMARIO};
        background-color: {COLOR_SECUNDARIO};
    }}

    QLineEdit::placeholder {{
        color: {COLOR_TEXTO_SECUNDARIO};
    }}

    QPushButton {{
        background-color: {COLOR_PRIMARIO};
        color: white;
        border: none;
        border-radius: 6px;
        padding: 10px 18px;
        font-weight: bold;
        font-size: 11pt;
    }}

    QPushButton:hover {{
        background-color: {COLOR_HOVER_PRIMARIO};
    }}

    QPushButton:pressed {{
        background-color: {COLOR_PRIMARIO};
    }}

    QPushButton:disabled {{
        background-color: {COLOR_BORDE};
        color: {COLOR_TEXTO_SECUNDARIO};
    }}
       - padding: 12px vertical y 24px horizontal (botón más grande). */
    QPushButton#btn_login {{
        background-color: transparent;
        border: 2px solid {COLOR_PRIMARIO};
        color: {COLOR_PRIMARIO};
        border-radius: 8px;
        padding: 12px 24px;
        font-size: 11pt;
    }}

    QPushButton#btn_login:hover {{
        background-color: {COLOR_PRIMARIO};
        color: white;
    }}

    QPushButton#btn_accion {{
        background-color: {COLOR_ACCION};
    }}

    QPushButton#btn_accion:hover {{
        background-color: {COLOR_HOVER_ACCION};
    }}

    QPushButton#btn_alerta {{
        background-color: {COLOR_ALERTA};
    }}

    QPushButton#btn_alerta:hover {{
        background-color: {COLOR_HOVER_ALERTA};
    }}

    QPushButton#btn_logout {{
        background-color: transparent;
        border: 1px solid {COLOR_ALERTA};
        color: {COLOR_ALERTA};
        border-radius: 6px;
        padding: 8px 16px;
        font-size: 10pt;
    }}

    QPushButton#btn_logout:hover {{
        background-color: {COLOR_ALERTA};
        color: white;
    }}

    QPushButton#btn_secundario {{
        background-color: transparent;
        border: 1px solid {COLOR_BORDE};
        color: {COLOR_TEXTO_SECUNDARIO};
        border-radius: 6px;
        padding: 8px 16px;
        font-size: 10pt;
    }}

    QPushButton#btn_secundario:hover {{
        border-color: {COLOR_PRIMARIO};
        color: {COLOR_PRIMARIO};
    }}
    QPushButton#btn_peligro {{
        background-color: transparent;
        border: 1px solid {COLOR_ALERTA};
        color: {COLOR_ALERTA};
        border-radius: 6px;
        padding: 8px 16px;
        font-size: 10pt;
    }}

    QPushButton#btn_peligro:hover {{
        background-color: {COLOR_ALERTA};
        color: white;
    }}

    QTableWidget {{
        background-color: {COLOR_SECUNDARIO};
        border: 1px solid {COLOR_BORDE};
        border-radius: 10px;
        gridline-color: {COLOR_BORDE};
        selection-background-color: {COLOR_SELECCION_FONDO};
        selection-color: {COLOR_TEXTO};
        outline: none;
        alternate-background-color: {COLOR_FONDO};
    }}
    QTableWidget::item {{
        padding: 10px 8px;
        border-bottom: 1px solid {COLOR_BORDE};
    }}

    QTableWidget::item:selected {{
        background-color: {COLOR_SELECCION_FONDO};
        color: {COLOR_TEXTO};
    }}

    QTableWidget::item:hover {{
        background-color: #1E293B;
    }}

    QHeaderView::section {{
        background-color: {COLOR_HEADER_GRADIENTE};
        color: {COLOR_TEXTO_SECUNDARIO};
        padding: 12px 8px;
        border: none;
        border-bottom: 2px solid {COLOR_PRIMARIO};
        border-right: 1px solid {COLOR_BORDE};
        font-weight: bold;
        text-transform: uppercase;
        font-size: 9pt;
        letter-spacing: 1px;
    }}

    QScrollBar:vertical {{
        border: none;
        background: {COLOR_SECUNDARIO};
        width: 10px;
        margin: 0px;
    }}

    QScrollBar::handle:vertical {{
        background: {COLOR_SCROLLBAR};
        min-height: 20px;
        border-radius: 5px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: {COLOR_PRIMARIO};
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    QScrollBar:horizontal {{
        border: none;
        background: {COLOR_SECUNDARIO};
        height: 10px;
        margin: 0px;
    }}

    QScrollBar::handle:horizontal {{
        background: {COLOR_SCROLLBAR};
        min-width: 20px;
        border-radius: 5px;
    }}

    QScrollBar::handle:horizontal:hover {{
        background: {COLOR_PRIMARIO};
    }}

    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}

    QDialog {{
        background-color: {COLOR_SECUNDARIO};
    }}

    QMessageBox {{
        background-color: {COLOR_SECUNDARIO};
    }}

    QMessageBox QLabel {{
        background: transparent;
        font-size: 11pt;
        color: {COLOR_TEXTO};
    }}
    
    QMessageBox QPushButton {{
        min-width: 80px;
    }}

    QInputDialog {{
        background-color: {COLOR_SECUNDARIO};
    }}

    QInputDialog QLabel {{
        background: transparent;
        color: {COLOR_TEXTO};
        font-size: 11pt;
    }}
    QInputDialog QLineEdit {{
        background-color: {COLOR_FONDO};
        border: 1px solid {COLOR_BORDE};
        border-radius: 6px;
        padding: 8px 12px;
        color: {COLOR_TEXTO};
        min-width: 250px;
    }}

    QInputDialog QLineEdit:focus {{
        border: 1px solid {COLOR_PRIMARIO};
    }}

    QInputDialog QPushButton {{
        background-color: {COLOR_PRIMARIO};
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: bold;
    }}
    QInputDialog QPushButton:hover {{
        background-color: {COLOR_HOVER_PRIMARIO};
    }}

    QDialogButtonBox QPushButton {{
        background-color: {COLOR_PRIMARIO};
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 20px;
        font-weight: bold;
        min-width: 80px;
    }}

    QDialogButtonBox QPushButton:hover {{
        background-color: {COLOR_HOVER_PRIMARIO};
    }}

    QToolTip {{
        background-color: {COLOR_SECUNDARIO};
        color: {COLOR_TEXTO};
        border: 1px solid {COLOR_PRIMARIO};
        border-radius: 4px;
        padding: 6px 10px;
        font-size: 10pt;
    }}
    """