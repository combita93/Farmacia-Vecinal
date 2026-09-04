# Esto permite almacenar las contraseñas de forma segura
import hashlib
# trabajar con bases de datos de forma local
import sqlite3
#datetime: se usa para obtener la fecha y hora actual del sistema
#timedelta: se usa para calcular diferencias de tiempo
from datetime import datetime, timedelta

#======================================================================
class FarmaciaDB:

 #__init__ (Constructor)
 #Se ejecuta automáticamente al crear un objeto FarmaciaDB.
 #bre la conexión a la base de datos, crea el cursor y
 #asegura que las tablas necesarias existan '''

    def __init__(self):
        # Establece la conexión con el archivo de base de datos SQLite.
        # Si el archivo no existe, SQLite lo crea automáticamente.
        self.conn = sqlite3.connect("farmacia.db")

        # Crea un cursor. El cursor es el objeto que se usa para ejecutar
        # sentencias SQL y recorrer los resultados obtenidos.
        self.cursor = self.conn.cursor()

        # Llama al método create_table para asegurar que las tablas
        # 'inventario' y 'usuarios' existan en la base de datos.
        self.create_table()

#======================================================================
    #  create_table: crea las tablas 'inventario' y 'usuarios' si no existen.
    #              También maneja la migración de la columna 'marca' para
    #              bases de datos antiguas que no la tenían.
    def create_table(self):
      
        # CREATE TABLE IF NOT EXISTS: solo crea la tabla si no existe ya.
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                fecha_vencimiento DATE NOT NULL,
                marca TEXT NOT NULL DEFAULT 'Desconocido'
            )
        ''')

        # Intenta seleccionar la columna 'marca' de la tabla inventario.
        try:
            self.cursor.execute("SELECT marca FROM inventario LIMIT 1")
        except sqlite3.OperationalError:
            # Si la columna 'marca' no existe (base de datos antigua),
            # se ejecuta ALTER TABLE para agregarla con un valor por defecto.
            self.cursor.execute("ALTER TABLE inventario ADD COLUMN marca TEXT NOT NULL DEFAULT 'Desconocido'")

        # Crea la tabla 'usuarios' si no existe.
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rol TEXT UNIQUE NOT NULL,
                usuario TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        ''')

        # lista de usuarios inaciales
        # El hash se genera con hashlib.sha256 usando el formato "usuario:contraseña".
        usuarios_iniciales = [
            # Usuario de bodega: juan con contraseña 1234
            ("bodega", "juan", hashlib.sha256("juan:1234".encode()).hexdigest()),
            # Usuario de entrega: carlos con contraseña 4567
            ("entrega", "carlos", hashlib.sha256("carlos:4567".encode()).hexdigest())
        ]

        # Bloque try/except para insertar los usuarios iniciales.
        try:
            # Itera sobre cada tupla de usuarios iniciales.
            for rol, usuario, hash_pass in usuarios_iniciales:
                # Inserta el usuario en la tabla.
                # ON CONFLICT(usuario) DO NOTHING: si el usuario ya existe,
                # (evita duplicados gracias a la restricción UNIQUE).
                self.cursor.execute(
                    "INSERT INTO usuarios (rol, usuario, password_hash) VALUES (?, ?, ?) ON CONFLICT(usuario) DO NOTHING",
                    (rol, usuario, hash_pass)
                )
        except Exception as e:
            # Si ocurre cualquier error al inicializar usuarios, lo imprime en consola
            print(f"Error al inicializar usuarios: {e}")

        # Guarda todos los cambios pendientes en la base de datos.
        # Sin commit, los cambios no se persisten en el archivo db
        self.conn.commit()

#======================================================================
    # registrar_medicamento:Registra un medicamento nuevo en el inventario.
    # si el medicamento ya existe por nombre, suma la cantidad
    # al stock existente en lugar de crear un duplicado.
    
    def registrar_medicamento(self, nombre, cantidad, fecha_vencimiento, marca):
        # Crea un cursor nuevo para esta operación específica.
        cursor = self.conn.cursor()

        # manejar errores de base de datos.

        try:
            # Busca por el nombre
            cursor.execute("SELECT id, cantidad FROM inventario WHERE nombre = ?", (nombre,))
            resultado = cursor.fetchone()

            # Si el medicamento ya existe (resultado no es None)...
            if resultado:
                # Desempaqueta el ID y el stock actual de la tupla resultado.
                id_existente, stock_actual = resultado
                # Calcula el nuevo stock sumando la cantidad ingresada.
                nuevo_stock = stock_actual + cantidad
                # Actualiza la cantidad del medicamento existente.
                cursor.execute("UPDATE inventario SET cantidad = ? WHERE id = ?", (nuevo_stock, id_existente))
                # Confirma el cambio en la base de datos.
                self.conn.commit()
                # Imprime un mensaje informativo en consola.
                print(f"Stock actualizado para {nombre}. Nuevo total: {nuevo_stock}")
            else:
                # Si el medicamento NO existe, inserta un nuevo registro.
                # Los signos ? son placeholders que se reemplazan con los valores
                # (nombre, cantidad, fecha_vencimiento, marca).
                cursor.execute(
                    "INSERT INTO inventario (nombre, cantidad, fecha_vencimiento, marca) VALUES (?, ?, ?, ?)",
                    (nombre, cantidad, fecha_vencimiento, marca)
                )
                # Confirma el cambio en la base de datos.
                self.conn.commit()
                # Imprime un mensaje informativo en consola.
                print(f"Nuevo medicamento {nombre} registrado con éxito.")

        except Exception as e:
            # Si ocurre cualquier error, lo imprime en consola.
            print(f"Error al registrar medicamento: {e}")

#======================================================================
    # obtener_todo: Obtiene todos los registros del inventario.
    #              Los resultados se ordenan alfabéticamente por nombre.
    # retorna: Lista de tuplas cada una con (id, nombre, cantidad, fecha, marca).

    def obtener_todo(self):
        # Ejecuta una consulta SELECT para obtener todas las columnas
        # de la tabla inventario ordenadas por nombre de forma ascendente
        self.cursor.execute("SELECT * FROM inventario ORDER BY nombre ASC")
        # fetchall() retorna una lista con todas las filas del resultado.
        return self.cursor.fetchall()

#======================================================================

    def obtener_medicamento_por_id(self, id_med):
        # Ejecuta una consulta SELECT filtrando por el ID proporcionado.
        self.cursor.execute("SELECT * FROM inventario WHERE id = ?", (id_med,))
        # fetchone() retorna la primera fila o None si no hay coincidencias (None es ninguno)
        return self.cursor.fetchone()

#======================================================================
    # entregar_medicamento: Entrega una cantidad de medicamento al público.
    #              Verifica que haya stock suficiente antes de descontar.
   
    def entregar_medicamento(self, id_med, cantidad_pedida):
        # Consulta la cantidad actual de stock del medicamento.
        self.cursor.execute("SELECT cantidad FROM inventario WHERE id = ?", (id_med,))
        # Obtiene la primera fila del resultado.
        resultado = self.cursor.fetchone()

        # Si el resultado es None, significa que el ID no existe en la tabla (None es ninguno)
        if resultado is None:
        # Retorna (False, 0) indicando que la entrega falló.
            return False, 0

        # Extrae el stock actual resultante (posición 0).
        stock_actual = resultado[0]

        # Verifica si hay suficiente stock para la cantidad pedida.
        if stock_actual >= cantidad_pedida:
            # Calcula el nuevo stock restando la cantidad entregada.
            nuevo_stock = stock_actual - cantidad_pedida
            # Actualiza la cantidad en la base de datos.
            self.cursor.execute("UPDATE inventario SET cantidad = ? WHERE id = ?", (nuevo_stock, id_med))
            # Confirma el cambio.
            self.conn.commit()
            # Retorna éxito y el nuevo stock.
            return True, nuevo_stock

        # Si no hay stock suficiente, retorna (False, stock_actual).
        return False, stock_actual

#======================================================================
    # editar_medicamento: Actualiza todos los datos de un medicamento existente.

    def editar_medicamento(self, id_med, nombre, cantidad, fecha_vencimiento, marca):
        # try/except para manejar errores de base de datos.
        try:
            # Ejecuta una sentencia UPDATE que modifica todas las columnas
            # del medicamento identificado por su ID.
            self.cursor.execute(
                "UPDATE inventario SET nombre = ?, cantidad = ?, fecha_vencimiento = ?, marca = ? WHERE id = ?",
                (nombre, cantidad, fecha_vencimiento, marca, id_med)
            )
            # Confirma el cambio en la base de datos.
            self.conn.commit()
            # Retorna True indicando que la operación fue exitosa.
            return True
        except Exception as e:
            # Si ocurre un error, lo imprime en consola.
            print(f"Error al editar medicamento: {e}")
            # Retorna False indicando que la operación falló.
            return False

#======================================================================
    # eliminar_medicamento: Elimina un medicamento del inventario por su ID.
    
    def eliminar_medicamento(self, id_med):
        # Bloque try/except para manejar errores de base de datos.
        try:
            # Ejecuta una sentencia DELETE que elimina el registro
            # del medicamento identificado por su ID.
            self.cursor.execute("DELETE FROM inventario WHERE id = ?", (id_med,))
            # Confirma el cambio en la base de datos.
            self.conn.commit()
            # Retorna True indicando que la operación fue exitosa.
            return True
        except Exception as e:
            # Si ocurre un error, lo imprime en consola.
            print(f"Error al eliminar medicamento: {e}")
            # Retorna False indicando que la operación falló.
            return False

#======================================================================
    # alertas_criticas: Busca medicamentos que necesitan atención:
    # Stock menor o igual a 5 unidades (poco inventario).
    # Fecha de vencimiento dentro de los próximos 30 días.
    # Los resultados se ordenan por urgencia (fecha más próxima
    #  primero y menor stock primero).
   
    def alertas_criticas(self):
        # Calcula la fecha límite: hoy + 30 días.
        # datetime.now() obtiene la fecha/hora actual.
        # timedelta(days=30) representa un intervalo de 30 días.
        # strftime('%Y-%m-%d') formatea la fecha como "YYYY-MM-DD".
        fecha_limite = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')

        # Ejecuta la consulta SQL:
    
        self.cursor.execute(
            """SELECT nombre, cantidad, fecha_vencimiento, marca 
               FROM inventario 
               WHERE cantidad <= 5 OR fecha_vencimiento <= ? 
               ORDER BY fecha_vencimiento ASC, cantidad ASC""",
            (fecha_limite,)
        )
        # Retorna todas las filas que cumplen la condición.
        return self.cursor.fetchall()

 #======================================================================    
    # validar_credenciales: Valida las credenciales de un usuario contra la tabla
    #              'usuarios' de la base de datos.

    def validar_credenciales(self, usuario, password):
        # Genera el hash SHA-256 de la contraseña usando el mismo formato
        # que se uso al crear los usuarios: "usuario:contraseña".
        # .encode() convierte el string a bytes (requerido por hashlib).
        # .hexdigest() convierte el hash a una cadena hexadecimal legible.
        password_hash = hashlib.sha256(f"{usuario}:{password}".encode()).hexdigest()

        # Crea un cursor nuevo para esta consulta.
        cursor = self.conn.cursor()

        # Ejecuta la consulta SQL que busca un usuario con el nombre
        # y el hash de contraseña proporcionados.
        cursor.execute(
            "SELECT rol FROM usuarios WHERE usuario = ? AND password_hash = ?",
            (usuario, password_hash)
        )
        # Obtiene la primera fila del resultado (o None si no hay coincidencia) (none es ninguno)
        resultado = cursor.fetchone()

        # Si se encontró un resultado (credenciales correctas)...
        if resultado:
            # Retorna el rol del usuario (posición 0 de la tupla).
            return resultado[0]

        # Si no se encontró resultado, retorna None (credenciales incorrectas).
        return None

    def close(self):
        # Verifica si la conexión existe antes de cerrarla.
        if self.conn:
            # Cierra la conexión a la base de datos SQLite.
            self.conn.close()