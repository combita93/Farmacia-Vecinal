# Arquitectura

## Capas actuales

El proyecto conserva una arquitectura pequena y adecuada para una aplicacion local:

- `models.py`: objetos inmutables `Medication`, `InventoryAlert` y `UserSession`.
- `database.py`: repositorio SQLAlchemy ORM, modelos de persistencia y consultas.
- `services.py`: autenticacion, validaciones y casos de uso de inventario.
- `ui/main_window.py`: widgets Qt, dialogos y presentacion de resultados.
- `main.py`: punto de entrada y API publica compatible.
- `ui/styles.py`: constantes de color y hoja de estilos QSS.

La interfaz no contiene reglas de stock ni consultas de base de datos. Las dependencias se inyectan en
`FarmaciaComunalApp`, por lo que los servicios pueden probarse sin iniciar Qt.

El paquete vive en `src/farmacia_vecinal` para que las importaciones sean estables tanto desde `uv run farmacia-vecinal` como desde `uv run python -m farmacia_vecinal`.

## Flujo de inicio

1. `farmacia_vecinal.main:run` crea `QApplication`.
2. `FarmaciaComunalApp` crea `FarmaciaDB`.
3. `FarmaciaDB` crea `database/`, abre `database/farmacia.db` y asegura las tablas.
4. La ventana carga el inventario y comienza el bucle de eventos Qt.
5. `closeEvent` cierra la conexion SQLite.

## Persistencia

SQLite crea las tablas `inventario` y `usuarios` si no existen. La ruta por defecto siempre es `database/farmacia.db`; la carpeta se crea automaticamente. La ruta se calcula desde la ubicacion del paquete, no desde el directorio actual del proceso. Esto evita que se creen varias bases de datos al lanzar el programa desde rutas distintas.

`FarmaciaDB` acepta opcionalmente `database_path`, lo que permite usar una base temporal en pruebas sin modificar la base local.

Las operaciones de inventario pasan por `InventoryService`. Este servicio rechaza
cantidades invalidas, controla roles en autenticacion y transforma los fallos de
persistencia en errores explicitos. `FarmaciaDB` usa SQLAlchemy para trabajar con
objetos Python en lugar de sentencias SQL escritas manualmente.

## Roles

- `bodega`: alta, edicion y eliminacion de medicamentos.
- `entrega`: descuento de unidades mediante la accion de entrega.
- cualquier sesion: consulta del inventario y de las alertas.

## Decisiones y limites

Se mantiene SQLite como motor local y SQLAlchemy como ORM. La autenticacion actual usa SHA-256 con el usuario como parte del valor hash; para un despliegue real debe migrarse a un algoritmo especifico para contrasenas, como Argon2 o bcrypt, y retirar las credenciales de demostracion del codigo.
