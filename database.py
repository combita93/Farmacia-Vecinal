import sqlite3
from datetime import datetime, timedelta

class FarmaciaDB:
    def __init__(self):
        self.conn = sqlite3.connect("farmacia.db")
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                fecha_vencimiento DATE NOT NULL
            )
        ''')
        self.conn.commit()

    def registrar_medicamento(self, nombre, cantidad, fecha_vencimiento):
        self.cursor.execute("INSERT INTO inventario (nombre, cantidad, fecha_vencimiento) VALUES (?, ?, ?)",
                            (nombre, cantidad, fecha_vencimiento))
        self.conn.commit()

    def obtener_todo(self):
        self.cursor.execute("SELECT * FROM inventario")
        return self.cursor.fetchall()

    def entregar_medicamento(self, id_med, cantidad_pedida):
        self.cursor.execute("SELECT cantidad FROM inventario WHERE id = ?", (id_med,))
        stock_actual = self.cursor.fetchone()[0]
        
        if stock_actual >= cantidad_pedida:
            nuevo_stock = stock_actual - cantidad_pedida
            self.cursor.execute("UPDATE inventario SET cantidad = ? WHERE id = ?", (nuevo_stock, id_med))
            self.conn.commit()
            return True, nuevo_stock
        return False, stock_actual

    def alertas_criticas(self):
        # Alerta si quedan menos de 5 unidades o vencen en menos de 30 días
        fecha_limite = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        self.cursor.execute("SELECT nombre, cantidad, fecha_vencimiento FROM inventario WHERE cantidad <= 5 OR fecha_vencimiento <= ?", (fecha_limite,))
        return self.cursor.fetchall()