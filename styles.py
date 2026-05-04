# Paleta de colores moderna (Dark SaaS Dashboard)
COLOR_FONDO = "#0B0F19"          # Fondo principal ultra oscuro (Slate 900 variation)
COLOR_SECUNDARIO = "#111827"     # Cajas, tarjetas y campos de texto (Gray 900)
COLOR_PRIMARIO = "#6366F1"       # Indigo 500
COLOR_ACCION = "#10B981"         # Emerald 500
COLOR_ALERTA = "#EF4444"         # Red 500
COLOR_TEXTO = "#F9FAFB"          # Texto principal (Gray 50)
COLOR_TEXTO_SECUNDARIO = "#9CA3AF" # Texto secundario o inactivo (Gray 400)
COLOR_BORDE = "#1F2937"          # Bordes sutiles (Gray 800)

# Colores de Hover y Selección
COLOR_HOVER_PRIMARIO = "#818CF8" # Indigo 400
COLOR_HOVER_ACCION = "#34D399"   # Emerald 400
COLOR_HOVER_ALERTA = "#F87171"   # Red 400
COLOR_SELECCION_FONDO = "#312E81" # Indigo 900 (Translucido)
COLOR_SCROLLBAR = "#374151"      # Gray 700

def get_stylesheet():
    return f"""
    QWidget {{
        background-color: {COLOR_FONDO};
        color: {COLOR_TEXTO};
        font-family: 'Segoe UI', 'Inter', sans-serif;
        font-size: 11pt;
    }}

    /* Etiquetas normales */
    QLabel {{
        color: {COLOR_TEXTO};
        font-weight: 500;
        background: transparent;
    }}

    /* Cajas de agrupación (SaaS Card Style) */
    QGroupBox {{
        background-color: {COLOR_SECUNDARIO};
        border: 1px solid {COLOR_BORDE};
        border-radius: 8px;
        margin-top: 24px;
        font-weight: bold;
        font-size: 12pt;
        color: {COLOR_TEXTO};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 10px;
        left: 20px;
        top: 2px;
    }}

    /* Entradas de texto */
    QLineEdit {{
        background-color: {COLOR_FONDO};
        border: 1px solid {COLOR_BORDE};
        border-radius: 6px;
        padding: 8px 12px;
        selection-background-color: {COLOR_PRIMARIO};
        color: {COLOR_TEXTO};
    }}
    QLineEdit:focus {{
        border: 1px solid {COLOR_PRIMARIO};
        background-color: {COLOR_SECUNDARIO};
    }}
    QLineEdit::placeholder {{
        color: {COLOR_TEXTO_SECUNDARIO};
    }}

    /* Botones */
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

    /* Botón de Acción Específica */
    QPushButton#btn_accion {{
        background-color: {COLOR_ACCION};
    }}
    QPushButton#btn_accion:hover {{
        background-color: {COLOR_HOVER_ACCION};
    }}

    /* Botón de Alerta Específica */
    QPushButton#btn_alerta {{
        background-color: {COLOR_ALERTA};
    }}
    QPushButton#btn_alerta:hover {{
        background-color: {COLOR_HOVER_ALERTA};
    }}

    /* Tabla (QTableWidget) */
    QTableWidget {{
        background-color: {COLOR_SECUNDARIO};
        border: 1px solid {COLOR_BORDE};
        border-radius: 8px;
        gridline-color: {COLOR_BORDE};
        selection-background-color: {COLOR_SELECCION_FONDO};
        selection-color: {COLOR_TEXTO};
        outline: none;
    }}
    QHeaderView::section {{
        background-color: {COLOR_FONDO};
        color: {COLOR_TEXTO_SECUNDARIO};
        padding: 12px;
        border: none;
        border-bottom: 1px solid {COLOR_BORDE};
        border-right: 1px solid {COLOR_BORDE};
        font-weight: bold;
        text-transform: uppercase;
        font-size: 10pt;
    }}
    QTableWidget::item {{
        padding: 8px;
        border-bottom: 1px solid {COLOR_BORDE};
    }}
    
    /* Scrollbars invisibles o esteticos para tablas */
    QScrollBar:vertical {{
        border: none;
        background: {COLOR_SECUNDARIO};
        width: 10px;
        margin: 0px 0px 0px 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {COLOR_SCROLLBAR};
        min-height: 20px;
        border-radius: 5px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    
    /* Dialogos */
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
    """